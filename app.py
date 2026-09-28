import streamlit as st
import pandas as pd
import json
import os
import yfinance as yf
from datetime import datetime
import pytz
from engine import scan_syariah_market

# Konfigurasi Halaman Standar ApexHub
st.set_page_config(
    page_title="ApexHub • Executive Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = os.path.expanduser("~/saham-syariah-app/portfolio_tracker.json")
BOT_FILE = os.path.expanduser("~/saham-syariah-app/bot_state.json")

def load_json(path, default):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f, indent=4)
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# --- MODERN SOFT-SAAS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }
    
    .stApp {
        background-color: #0d121d !important;
        color: #e2e8f0 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #111726 !important;
        border-right: 1px solid #1e293b !important;
    }
    
    .brand-box {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 6px 0 16px 0;
        margin-bottom: 12px;
        border-bottom: 1px solid #1e293b;
    }
    .brand-logo {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        color: white;
        border-radius: 12px;
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.15rem;
        box-shadow: 0 4px 14px rgba(234, 88, 12, 0.35);
    }
    .brand-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.3px;
        line-height: 1.1;
    }
    .brand-subtitle {
        font-size: 0.68rem;
        color: #64748b;
        font-weight: 600;
        letter-spacing: 0.8px;
    }

    .greeting-banner {
        background: linear-gradient(135deg, #141c2e 0%, #101624 100%);
        border: 1px solid #1e293b;
        border-radius: 20px;
        padding: 24px 28px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 14px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    .greeting-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .greeting-sub {
        font-size: 0.88rem;
        color: #94a3b8;
        margin: 6px 0 0 0;
    }
    .period-pill {
        background-color: #0b111e;
        border: 1px solid #243247;
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 8px 16px;
        border-radius: 30px;
    }

    .clean-card {
        background-color: #141c2e;
        border: 1px solid #1f2c42;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .clean-card:hover {
        border-color: #334b6e;
    }

    .badge-soft-green {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .badge-soft-slate {
        background: rgba(148, 163, 184, 0.12);
        color: #94a3b8;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }

    div[data-testid="stMetric"] {
        background: #141c2e !important;
        border: 1px solid #1f2c42 !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12) !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        font-size: 1.55rem !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #1f2c42 !important;
        border-radius: 14px !important;
        overflow: hidden;
    }

    .stButton>button {
        background: linear-gradient(180deg, #1e293b 0%, #172033 100%) !important;
        color: #f1f5f9 !important;
        border: 1px solid #2b3952 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
    }
    .stButton>button:hover {
        border-color: #f97316 !important;
        color: #f97316 !important;
    }
    .stLinkButton>a {
        background-color: #141c2e !important;
        color: #cbd5e1 !important;
        border: 1px solid #243247 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s;
    }
    .stLinkButton>a:hover {
        background-color: #1c273e !important;
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
    }
    div[data-baseweb="select"] > div, .stNumberInput input, .stTextInput input {
        background-color: #0f1624 !important;
        border: 1px solid #233147 !important;
        color: #f8fafc !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

wib = pytz.timezone("Asia/Jakarta")
now_wib = datetime.now(wib)
time_str = now_wib.strftime("%H:%M WIB")
date_str = now_wib.strftime("%d %B %Y")

# ==================== SIDEBAR KIRI ====================
with st.sidebar:
    st.markdown("""
    <div class="brand-box">
        <div class="brand-logo">▲</div>
        <div>
            <div class="brand-title">ApexHub</div>
            <div class="brand-subtitle">EXECUTIVE COMMAND</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("UTAMA")
    menu_nav = st.radio(
        "Menu:",
        ["📊 01 Dashboard & Radar", "🤖 02 Bot Asisten (Auto)", "💼 03 Portofolio Riil", "🚀 04 Side Hustle & Learn"],
        label_visibility="collapsed"
    )

    st.write("")
    st.caption("AKSES CEPAT (SIDE HUSTLE)")
    st.link_button("💻 DataAnnotation.tech", "https://app.dataannotation.tech", use_container_width=True)
    st.link_button("🎨 Adobe Stock Contributor", "https://contributor.stock.adobe.com", use_container_width=True)
    st.link_button("🎓 Coursera Dashboard", "https://www.coursera.org", use_container_width=True)
    st.link_button("✉️ Gmail Workspace", "https://mail.google.com", use_container_width=True)

    st.write("")
    st.caption("CORE ENGINE")
    st.markdown("""
    <div style="background:#0c121d; border:1px solid #1a2538; padding:12px 14px; border-radius:12px; font-size:0.75rem;">
        <span style="color:#64748b;">Strategi Pasar:</span><br>
        <b style="color:#34d399;">Pullback at Support (EMA-20)</b><br><br>
        <span style="color:#64748b;">Target Risiko-Imbalan:</span><br>
        <b style="color:#f97316;">Dinamis 1 : 2 (ATR-Based)</b>
    </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=600)
def get_market_data():
    return scan_syariah_market()

# ==================== HERO GREETING BANNER ====================
st.markdown(f"""
<div class="greeting-banner">
    <div>
        <h1 class="greeting-title">Good morning, Juhdan</h1>
        <p class="greeting-sub">ApexHub siap memantau pasar saham syariah, mendeteksi peluang pullback, dan mengawal alur kerja harian Anda.</p>
    </div>
    <div class="period-pill">
        📅 {date_str} • <b>{time_str}</b>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== MENU 1: DASHBOARD & RADAR SAHAM ====================
if "01 Dashboard" in menu_nav:
    with st.spinner("ApexHub sedang memindai seluruh konstituen pasar saham syariah BEI..."):
        top_stocks, total_scanned = get_market_data()

    buy_count = sum(1 for s in top_stocks if "BUY" in s["status"])

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Total Saham Dipindai", f"{total_scanned} Emiten")
    with col_m2:
        st.metric("Sinyal Pullback Valid", f"{buy_count} Saham", f"{buy_count} setup")
    with col_m3:
        st.metric("Risk-Reward Model", "1 : 2 Asymmetric", "ATR Dinamis")
    with col_m4:
        st.metric("Fase Eksekusi", "Uptrend Pullback", "EMA-20 Support")

    st.write("")

    with st.expander("⚙️ Konfigurasi Tampilan Modul", expanded=False):
        c_p1, c_p2, c_p3 = st.columns(3)
        show_sparkline = c_p1.checkbox("Tampilkan Sparkline Tren 14 Hari", value=True)
        show_tech = c_p2.checkbox("Tampilkan Detail Indikator (RSI & ATR)", value=True)
        show_calc = c_p3.checkbox("Tampilkan Kalkulator Eksekusi Lot", value=True)

    tab_card, tab_table = st.tabs(["📱 Mode Kartu Fokus", "📊 Mode Tabel Komprehensif"])

    with tab_card:
        col_kiri, col_kanan = st.columns(2)
        for idx, s in enumerate(top_stocks):
            target_col = col_kiri if idx % 2 == 0 else col_kanan
            is_buy = "BUY" in s["status"]
            badge_html = '<span class="badge-soft-green">BUY (PULLBACK)</span>' if is_buy else '<span class="badge-soft-slate">MONITOR</span>'
            c_color = "#34d399" if s["change"] >= 0 else "#f87171"

            with target_col:
                st.markdown(f"""
                <div class="clean-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div>
                            <span style="font-size:1.4rem; font-weight:800; color:#f8fafc; letter-spacing:-0.5px;">{s['code']}</span>
                            <span style="font-size:0.8rem; color:#64748b; margin-left:8px;">BEI SYARIAH</span>
                        </div>
                        {badge_html}
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:14px;">
                        <span style="color:#94a3b8; font-size:0.9rem;">Harga Terkini: <b style="color:#f8fafc; font-size:1.15rem;">Rp {int(s['price']):,}</b></span>
                        <span style="color:{c_color}; font-weight:700; font-size:1rem;">{s['change']:+.2f}%</span>
                    </div>
                    <div style="background:#0c121d; border:1px solid #1a2538; padding:14px; border-radius:12px; font-size:0.83rem; display:grid; grid-template-columns: 1fr 1fr; gap:8px;">
                        <div>🎯 <b>Target TP ({s['tp_pct']}):</b><br><span style="color:#34d399; font-weight:700;">Rp {s['tp']:,}</span></div>
                        <div>🛡️ <b>Batas SL ({s['sl_pct']}):</b><br><span style="color:#f87171; font-weight:700;">Rp {s['sl']:,}</span></div>
                        <div style="grid-column: span 2; margin-top:4px;">📍 <b>Area Antrean Beli:</b> <b style="color:#38bdf8;">{s['entry']}</b></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if show_sparkline:
                    st.line_chart(s["sparkline"], height=85)
                if show_tech:
                    st.caption(f"Status: RSI {s['rsi']} • ATR Rp {s['atr']} • {s['trend']}")
                    st.write("")

    with tab_table:
        table_rows = []
        for s in top_stocks:
            table_rows.append({
                "Emiten": s["code"],
                "Harga": f"Rp {int(s['price']):,}",
                "Perubahan": f"{s['change']:+.2f}%",
                "Keputusan": s["status"],
                "Area Antre Beli": s["entry"],
                "Target TP (ATR)": f"Rp {s['tp']:,} ({s['tp_pct']})",
                "Batas SL (ATR)": f"Rp {s['sl']:,} ({s['sl_pct']})",
                "Teknikal": f"RSI {s['rsi']} | ATR Rp {s['atr']}"
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    if show_calc:
        st.write("---")
        st.write("##### 🧮 Kalkulator Lot Sebelum Eksekusi di Sekuritas")
        stock_options = [s["code"] for s in top_stocks]
        c_calc1, c_calc2 = st.columns([1, 1])

        with c_calc1:
            pil_saham = st.selectbox("Pilih Saham Rekomendasi:", options=stock_options)
            modal_user = st.number_input("Modal Siap Pakai (Rp):", min_value=500000, value=5000000, step=500000)

        s_obj = next((item for item in top_stocks if item["code"] == pil_saham), top_stocks[0])
        p_val = s_obj["price"]
        l_price = p_val * 100
        qty_lot = int(modal_user // l_price) if l_price > 0 else 0
        spent_modal = qty_lot * l_price
        sisa_dana = modal_user - spent_modal

        with c_calc2:
            st.markdown(f"""
            <div class="clean-card" style="margin-top:10px;">
                <b style="color:#f97316;">SIMULASI ORDER ({pil_saham}):</b><br><br>
                • Pasang di Sekuritas: <span style="color:#34d399; font-weight:800; font-size:1.3rem;">{qty_lot} LOT</span> ({qty_lot * 100:,} Lembar)<br>
                • Total Biaya: <b>Rp {int(spent_modal):,}</b> (Sisa Kas: Rp {int(sisa_dana):,})<br>
                • Target Untung ({s_obj['tp_pct']}): <span style="color:#34d399; font-weight:700;">Rp {s_obj['tp']:,}</span><br>
                • Batas Risiko ({s_obj['sl_pct']}): <span style="color:#f87171; font-weight:700;">Rp {s_obj['sl']:,}</span>
            </div>
            """, unsafe_allow_html=True)

# ==================== MENU 2: BOT ASISTEN TRADING ====================
elif "02 Bot Asisten" in menu_nav:
    default_bot = {"cash": 10000000.0, "initial_cash": 10000000.0, "positions": [], "history": []}
    bot_data = load_json(BOT_FILE, default_bot)

    with st.expander("⚙️ Konfigurasi Modal & Reset Bot", expanded=False):
        c_b1, c_b2 = st.columns([3, 1])
        with c_b1:
            modal_bot = st.number_input("Atur Modal Bot (Rp):", min_value=1000000, value=int(bot_data.get("initial_cash", 10000000)), step=1000000)
        with c_b2:
            st.write("")
            st.write("")
            if st.button("Terapkan / Reset Modal", use_container_width=True):
                bot_data = {"cash": float(modal_bot), "initial_cash": float(modal_bot), "positions": [], "history": []}
                save_json(BOT_FILE, bot_data)
                st.rerun()

    with st.spinner("ApexHub Bot sedang mengevaluasi pasar dan posisi aktif..."):
        top_stocks, _ = get_market_data()

        retained_positions = []
        for pos in bot_data["positions"]:
            try:
                curr_price = float(yf.Ticker(pos["ticker"]).fast_info.last_price)
            except Exception:
                curr_price = pos["buy_price"]

            if curr_price >= (pos["buy_price"] + (pos["tp"] - pos["buy_price"]) * 0.5) and pos["sl"] < pos["buy_price"]:
                pos["sl"] = pos["buy_price"]

            hit_tp = curr_price >= pos["tp"]
            hit_sl = curr_price <= pos["sl"]

            if hit_tp or hit_sl:
                revenue = pos["lots"] * 100 * curr_price
                pnl = revenue - pos["total_cost"]
                pct = (pnl / pos["total_cost"]) * 100
                bot_data["cash"] += revenue

                reason = "TAKE PROFIT (TARGET ATR)" if hit_tp else ("TRAILING BEP" if curr_price >= pos["buy_price"] else "STOP LOSS")
                bot_data["history"].append({
                    "Waktu": datetime.now().strftime("%d/%m %H:%M"),
                    "Aksi": f"JUAL ({reason})",
                    "Emiten": pos["code"],
                    "Lot": pos["lots"],
                    "Harga Jual": f"Rp {int(curr_price):,}",
                    "Laba/Rugi": f"Rp {int(pnl):,}",
                    "Hasil (%)": f"{pct:+.2f}%"
                })
            else:
                pos["current_price"] = curr_price
                retained_positions.append(pos)

        bot_data["positions"] = retained_positions

        best_signals = [s for s in top_stocks if "BUY" in s["status"]]
        active_codes = [p["code"] for p in bot_data["positions"]]

        if len(bot_data["positions"]) < 3 and bot_data["cash"] >= 1500000:
            for sig in best_signals:
                if sig["code"] in active_codes:
                    continue

                c_price = sig["price"]
                budget = min(bot_data["cash"] * 0.45, 3000000)
                lot_size = int(budget // (c_price * 100))

                if lot_size >= 1:
                    total_spent = lot_size * 100 * c_price
                    bot_data["cash"] -= total_spent

                    bot_data["positions"].append({
                        "ticker": sig["ticker"],
                        "code": sig["code"],
                        "buy_price": c_price,
                        "current_price": c_price,
                        "lots": lot_size,
                        "total_cost": total_spent,
                        "tp": sig["tp"],
                        "sl": sig["sl"],
                        "entry_date": datetime.now().strftime("%d/%m %H:%M")
                    })

                    bot_data["history"].append({
                        "Waktu": datetime.now().strftime("%d/%m %H:%M"),
                        "Aksi": "BELI (PULLBACK SETUP)",
                        "Emiten": sig["code"],
                        "Lot": lot_size,
                        "Harga Jual": f"Rp {int(c_price):,}",
                        "Laba/Rugi": "-",
                        "Hasil (%)": "POSISI TERBUKA"
                    })
                    break

        save_json(BOT_FILE, bot_data)

    equity_val = sum([p["lots"] * 100 * p.get("current_price", p["buy_price"]) for p in bot_data["positions"]])
    total_val = bot_data["cash"] + equity_val
    overall_pnl = total_val - bot_data["initial_cash"]
    overall_pct = (overall_pnl / bot_data["initial_cash"]) * 100

    bm1, bm2, bm3, bm4 = st.columns(4)
    bm1.metric("💵 Kas Bot Tersedia", f"Rp {int(bot_data['cash']):,}")
    bm2.metric("📊 Nilai Saham Dipegang", f"Rp {int(equity_val):,}")
    bm3.metric("💼 Total Aset Portofolio", f"Rp {int(total_val):,}")
    bm4.metric("📈 Pertumbuhan Aset", f"Rp {int(overall_pnl):,}", f"{overall_pct:+.2f}%")

    st.write("")
    st.write("##### 🎯 Posisi Saham yang Dikelola Bot (Active Trades)")
    if bot_data["positions"]:
        p_rows = []
        for p in bot_data["positions"]:
            c_p = p.get("current_price", p["buy_price"])
            val = p["lots"] * 100 * c_p
            pnl_pos = val - p["total_cost"]
            pct_pos = (pnl_pos / p["total_cost"]) * 100
            p_rows.append({
                "Emiten": p["code"],
                "Volume": f"{p['lots']} Lot",
                "Harga Beli": f"Rp {int(p['buy_price']):,}",
                "Harga Terkini": f"Rp {int(c_p):,}",
                "Target TP (ATR)": f"Rp {p['tp']:,}",
                "Batas SL (ATR)": f"Rp {p['sl']:,}",
                "Floating P/L": f"Rp {int(pnl_pos):,}",
                "Floating (%)": f"{pct_pos:+.2f}%"
            })
        st.dataframe(pd.DataFrame(p_rows), use_container_width=True, hide_index=True)
    else:
        st.info("💡 Bot sedang menunggu sinyal setup pullback valid berikutnya untuk mengambil posisi.")

    st.write("##### 📜 Buku Jurnal Transaksi Bot")
    if bot_data["history"]:
        clean_bot_hist = [{k: v for k, v in h.items() if not k.startswith("_")} for h in reversed(bot_data["history"])]
        st.dataframe(pd.DataFrame(clean_bot_hist), use_container_width=True, hide_index=True)
    else:
        st.caption("Belum ada riwayat transaksi bot.")

# ==================== MENU 3: PORTOFOLIO MANUAL RIIL ====================
elif "03 Portofolio" in menu_nav:
    port_data = load_json(DB_FILE, {"open_trades": [], "history": []})

    st.write("##### 📝 Input Transaksi Akun Sekuritas")
    c_in1, c_in2, c_in3, c_in4 = st.columns([2, 2, 2, 1.5])
    with c_in1:
        inp_emiten = st.text_input("Kode Saham (contoh: BRIS):").upper().strip()
    with c_in2:
        inp_lot = st.number_input("Jumlah Lot:", min_value=1, value=10, step=1)
    with c_in3:
        inp_harga = st.number_input("Harga Beli (Rp):", min_value=50, value=2500, step=10)
    with c_in4:
        st.write("")
        st.write("")
        if st.button("Catat Posisi Beli", use_container_width=True):
            if inp_emiten:
                ticker_full = f"{inp_emiten}.JK"
                total_cost = inp_lot * 100 * inp_harga
                port_data["open_trades"].append({
                    "ticker": ticker_full,
                    "code": inp_emiten,
                    "lots": inp_lot,
                    "buy_price": inp_harga,
                    "total_cost": total_cost,
                    "date": datetime.now().strftime("%d/%m/%Y")
                })
                save_json(DB_FILE, port_data)
                st.success(f">> Posisi {inp_emiten} berhasil disimpan!")
                st.rerun()

    st.write("---")
    st.write("##### 🎯 Posisi Saham Berjalan (Live Floating P/L)")

    if port_data["open_trades"]:
        for idx, pos in enumerate(port_data["open_trades"]):
            try:
                curr_p = float(yf.Ticker(pos["ticker"]).fast_info.last_price)
            except Exception:
                curr_p = pos["buy_price"]

            curr_val = pos["lots"] * 100 * curr_p
            pnl = curr_val - pos["total_cost"]
            pct = (pnl / pos["total_cost"]) * 100

            c_pos1, c_pos2, c_pos3, c_pos4 = st.columns([2, 3, 2, 1])
            with c_pos1:
                st.markdown(f"**{pos['code']}** ({pos['lots']} Lot)")
                st.caption(f"Beli: Rp {int(pos['buy_price']):,} | Terkini: Rp {int(curr_p):,}")
            with c_pos2:
                pnl_color = "#34d399" if pnl >= 0 else "#f87171"
                st.markdown(f"<span style='color:{pnl_color}; font-weight:700;'>Rp {int(pnl):,} ({pct:+.2f}%)</span>", unsafe_allow_html=True)
                st.caption(f"Nilai Posisi: Rp {int(curr_val):,}")
            with c_pos3:
                tp_ref = int(pos["buy_price"] * 1.05)
                sl_ref = int(pos["buy_price"] * 0.975)
                st.caption(f"Target Acuan: TP Rp {tp_ref:,} | SL Rp {sl_ref:,}")
            with c_pos4:
                if st.button("Tutup / Jual", key=f"close_{idx}"):
                    port_data["history"].append({
                        "Tanggal": datetime.now().strftime("%d/%m/%Y"),
                        "Emiten": pos["code"],
                        "Lot": pos["lots"],
                        "Harga Beli": f"Rp {int(pos['buy_price']):,}",
                        "Harga Jual": f"Rp {int(curr_p):,}",
                        "Laba/Rugi (Rp)": f"Rp {int(pnl):,}",
                        "Hasil (%)": f"{pct:+.2f}%",
                        "_is_win": pnl > 0
                    })
                    port_data["open_trades"].pop(idx)
                    save_json(DB_FILE, port_data)
                    st.rerun()
            st.divider()
    else:
        st.info("💡 Belum ada posisi aktif yang dicatat. Silakan masukkan posisi di formulir atas.")

    st.write("##### 📜 Rekam Jejak Portofolio & Win Rate")
    if port_data["history"]:
        total_closed = len(port_data["history"])
        wins = sum(1 for h in port_data["history"] if h.get("_is_win", False))
        win_rate = (wins / total_closed * 100) if total_closed > 0 else 0

        c_w1, c_w2 = st.columns(2)
        c_w1.metric("Total Transaksi Selesai", f"{total_closed} Kali")
        c_w2.metric("Win Rate Portofolio", f"{win_rate:.1f}%")

        clean_history = [{k: v for k, v in item.items() if not k.startswith("_")} for item in reversed(port_data["history"])]
        st.dataframe(pd.DataFrame(clean_history), use_container_width=True, hide_index=True)
    else:
        st.caption("Belum ada riwayat transaksi yang tersimpan.")

# ==================== MENU 4: SIDE HUSTLE & LEARNING HUB ====================
elif "04 Side Hustle" in menu_nav:
    st.write("##### 🚀 Side Hustle & Learning Portals")
    st.caption("Platform terpadu untuk produktivitas harian dan pembelajaran Anda:")

    c_h1, c_h2 = st.columns(2)
    with c_h1:
        st.markdown("""
        <div class="clean-card">
            <h4 style="margin:0 0 8px 0; color:#38bdf8;">💻 DataAnnotation.tech</h4>
            <p style="color:#94a3b8; font-size:0.85rem;">Portal pengerjaan task AI training, evaluasi dataset, dan analisis instruksi.</p>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("Buka DataAnnotation Portal ↗", "https://app.dataannotation.tech", use_container_width=True)

        st.write("")
        st.markdown("""
        <div class="clean-card">
            <h4 style="margin:0 0 8px 0; color:#a78bfa;">🎓 Coursera Learning</h4>
            <p style="color:#94a3b8; font-size:0.85rem;">Ruang peningkatan skill profesional, sertifikasi, dan pembelajaran mandiri.</p>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("Buka Coursera Dashboard ↗", "https://www.coursera.org", use_container_width=True)

    with c_h2:
        st.markdown("""
        <div class="clean-card">
            <h4 style="margin:0 0 8px 0; color:#f97316;">🎨 Adobe Stock Contributor</h4>
            <p style="color:#94a3b8; font-size:0.85rem;">Dashboard kontributor aset kreatif, evaluasi portofolio, dan statistik unduhan.</p>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("Buka Adobe Stock Contributor ↗", "https://contributor.stock.adobe.com", use_container_width=True)

        st.write("")
        st.markdown("""
        <div class="clean-card">
            <h4 style="margin:0 0 8px 0; color:#34d399;">✉️ Google Workspace (Gmail)</h4>
            <p style="color:#94a3b8; font-size:0.85rem;">Akses cepat kotak masuk email untuk koordinasi kerjaan dan notifikasi penting.</p>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("Buka Kotak Masuk Gmail ↗", "https://mail.google.com", use_container_width=True)
