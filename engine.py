import yfinance as yf
import pandas as pd
import numpy as np

# Semesta Konstituen Saham Syariah ISSI Lintas Sektor
ISSI_UNIVERSE = [
    "AALI.JK", "ABMM.JK", "ACES.JK", "ADCP.JK", "ADHI.JK", "ADMR.JK", "ADRO.JK", "AGII.JK", "AKRA.JK", "AMRT.JK",
    "ANTM.JK", "APLN.JK", "ASII.JK", "ASRI.JK", "ASSA.JK", "AUTO.JK", "AVIA.JK", "BIRD.JK", "BKSL.JK", "BREN.JK",
    "BRIS.JK", "BRMS.JK", "BRPT.JK", "BSDE.JK", "BSSR.JK", "BTPS.JK", "BUMI.JK", "CLEO.JK", "CPIN.JK", "CTRA.JK",
    "DART.JK", "DEWA.JK", "DGIK.JK", "DMAS.JK", "DRMA.JK", "DSNG.JK", "ELSA.JK", "EMTK.JK", "ENRG.JK", "ERAA.JK",
    "ESSA.JK", "EXCL.JK", "GIAA.JK", "GJTL.JK", "GOTO.JK", "HEAL.JK", "HRUM.JK", "ICBP.JK", "INCO.JK", "INDF.JK",
    "INKP.JK", "INTP.JK", "ISAT.JK", "ITMG.JK", "JPFA.JK", "JRPT.JK", "KAEF.JK", "KIJA.JK", "KLBF.JK", "KPIG.JK",
    "KRAS.JK", "LPPF.JK", "MAPI.JK", "MAPA.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK", "MIKA.JK", "MNCN.JK", "MPMX.JK",
    "MTDL.JK", "MYOR.JK", "PANI.JK", "PANR.JK", "PBSA.JK", "PGAS.JK", "PPRO.JK", "PRDA.JK", "PTBA.JK", "PTPP.JK",
    "PWON.JK", "RAJA.JK", "RALS.JK", "ROTI.JK", "SCMA.JK", "SILO.JK", "SIMP.JK", "SMDR.JK", "SMGR.JK", "SMRA.JK",
    "SMSM.JK", "SRTG.JK", "SSIA.JK", "SSMS.JK", "TAPG.JK", "TINS.JK", "TKIM.JK", "TLKM.JK", "TOWR.JK", "TPIA.JK",
    "UNTR.JK", "UNVR.JK", "WIKA.JK", "WOOD.JK", "WSKT.JK"
]

def calculate_atr(df, period=14):
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def scan_syariah_market():
    tickers_str = " ".join(ISSI_UNIVERSE)
    data = yf.download(tickers_str, period="4mo", interval="1d", group_by="ticker", progress=False, threads=True)
    
    results = []
    
    for ticker in ISSI_UNIVERSE:
        clean_code = ticker.replace(".JK", "")
        try:
            df = data[ticker].dropna() if ticker in data else None
            if df is None or len(df) < 40:
                continue

            c_price = float(df["Close"].iloc[-1])
            prev_price = float(df["Close"].iloc[-2])
            change_pct = ((c_price - prev_price) / prev_price) * 100

            vol_now = float(df["Volume"].iloc[-1])
            vma20 = float(df["Volume"].tail(20).mean())

            # Filter Likuiditas Minimal
            if vol_now < 100000:
                continue

            # Indikator Tren Jangka Menengah & Pendek
            ema20 = float(df["Close"].ewm(span=20).mean().iloc[-1])
            sma50 = float(df["Close"].tail(50).mean()) if len(df) >= 50 else ema20 * 0.98

            # Indikator RSI
            diff = df["Close"].diff()
            gain = diff.clip(lower=0).tail(14).mean()
            loss = -diff.clip(upper=0).tail(14).mean()
            rs = gain / loss if loss != 0 else 1
            rsi = float(100 - (100 / (1 + rs)))

            # Indikator ATR 14
            atr_series = calculate_atr(df)
            atr_val = float(atr_series.iloc[-1]) if not np.isnan(atr_series.iloc[-1]) else (c_price * 0.02)

            # --- SISTEM SKORING PULLBACK STRATEGY (0 - 100) ---
            score = 0
            
            # 1. Tren Dasar Harus Bullish (Maks 35 Poin)
            is_uptrend = (c_price > sma50) and (ema20 > sma50)
            if is_uptrend:
                score += 35

            # 2. Posisi Pullback Dekat Support EMA-20 (Maks 30 Poin)
            # Mengukur jarak harga terkini ke EMA-20
            pct_from_ema20 = ((c_price - ema20) / ema20) * 100
            if -1.0 <= pct_from_ema20 <= 2.0:
                score += 30  # Sangat ideal di lantai pantulan
            elif 2.0 < pct_from_ema20 <= 4.0:
                score += 15  # Mulai menjauh dari support

            # 3. RSI Fase Dingin / Santai (Maks 20 Poin)
            if 45 <= rsi <= 56:
                score += 20  # Sweet-spot pullback (belum jenuh beli)
            elif 40 <= rsi <= 62:
                score += 10

            # 4. Volume Koreksi Rendah / Sehat (Maks 15 Poin)
            # Saat pullback, volume idealnya rendah atau mulai stabil
            if vol_now <= (vma20 * 1.1):
                score += 15
            elif vol_now <= (vma20 * 1.4):
                score += 5

            # --- TARGET DINAMIS FLEKSIBEL (ATR-BASED RRR 1:2) ---
            # Stop Loss: 1.5x ATR | Take Profit: 3.0x ATR
            sl_distance = max(int(atr_val * 1.5), int(c_price * 0.015))
            tp_distance = int(sl_distance * 2)

            tp_price = int(c_price + tp_distance)
            sl_price = int(c_price - sl_distance)
            tp_pct = ((tp_price - c_price) / c_price) * 100
            sl_pct = ((c_price - sl_price) / c_price) * 100

            # Penentuan Keputusan & Antrean Masuk
            if score >= 80:
                status = "BUY (PULLBACK SUPPORT)"
                entry_low = int(min(c_price, ema20))
                entry_high = int(c_price)
                entry_str = f"Rp {entry_low:,} - {entry_high:,}"
                decision_badge = "STRONG BUY"
            else:
                status = "WAIT / MONITOR"
                entry_str = f"Tunggu di Rp {int(ema20):,}"
                decision_badge = "MONITOR"

            sparkline_prices = df["Close"].tail(14).tolist()

            results.append({
                "code": clean_code,
                "ticker": ticker,
                "price": c_price,
                "change": change_pct,
                "score": score,
                "status": status,
                "badge": decision_badge,
                "entry": entry_str,
                "tp": tp_price,
                "sl": sl_price,
                "tp_pct": f"+{tp_pct:.1f}%",
                "sl_pct": f"-{sl_pct:.1f}%",
                "atr": int(atr_val),
                "rsi": int(rsi),
                "trend": "PULLBACK UPTREND" if is_uptrend else "NETRAL",
                "sparkline": sparkline_prices
            })
        except Exception:
            continue

    # Urutkan berdasarkan skor tertinggi
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:10], len(results)
