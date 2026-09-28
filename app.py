import streamlit as st
import pandas as pd
import json
import os
import yfinance as yf
from datetime import datetime
import pytz
from engine import scan_syariah_market

st.set_page_config(
    page_title="ApexHub • Executive Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PIN Rahasia Admin (Ganti angka ini sesuai keinginan Anda)
ADMIN_PIN = "8899"

DB_FILE = os.path.expanduser("portfolio_tracker.json")
BOT_FILE = os.path.expanduser("bot_state.json")

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

# Styling UI Modern
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    .stApp { background-color: #0d121d !important; color: #e2e8f0 !important; }
    section[data-testid="stSidebar"] { background-color: #111726 !important; border-right: 1px solid #1e293b !important; }
    .brand-box { display: flex; align-items: center; gap: 12px; padding: 6px 0 16px 0; margin-bottom: 12px; border-bottom: 1px solid #1e293b; }
    .brand-logo { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: white; border-radius: 12px; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.15rem; }
    .brand-title { font-size: 1.25rem; font-weight: 800; color: #f8fafc; line-height: 1.1; }
    .brand-subtitle { font-size: 0.68rem; color: #64748b; font-weight: 600; letter-spacing: 0.8px; }
    .greeting-banner { background: linear-gradient(135deg, #141c2e 0%, #101624 100%); border: 1px solid #1e293b; border-radius: 20px; padding: 22px 26px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; }
    .greeting-title { font-size: 1.7rem; font-weight: 800; color: #f8fafc; margin: 0; }
    .clean-card { background-color: #141c2e; border: 1px solid #1f2c42; border-radius: 18px; padding: 18px; margin-bottom: 14px; }
    .badge-soft-green { background: rgba(16, 185, 129, 0.15); color: #34d399; font-size: 0.72rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; }
    .badge-soft-slate { background: rgba(148, 163, 184, 0.12); color: #94a3b8; font-size: 0.72rem; font-weight: 600; padding: 4px 10px; border-radius: 20px; }
    div[data-testid="stMetric"] { background: #141c2e !important; border: 1px solid #1f2c42 !important; border-radius: 16px !important; padding: 14px 18px !important; }
    div[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.75rem !important; font-weight: 600; }
    div[data-testid="stMetricValue"] { color: #f8fafc !important; font-family: 'JetBrains Mono', monospace !important; font-size: 1.4rem !important; }
</style>
""", unsafe_allow_html=True)

wib = pytz.timezone("Asia/Jakarta")
now_wib = datetime.now(wib)
time_str = now_wib.strftime("%H:%M WIB")
date_str = now_wib.strftime("%d %B %Y")

# Inisialisasi Session State Login
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

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

    # Otentikasi Akses
    st.caption("MODE AKSES")
    if not st.session_state.is_admin:
        pin_input = st.text_input("Masukan PIN Admin:", type="password", placeholder="Viewer Mode (Read-Only)")
        if pin_input == ADMIN_PIN:
            st.session_state.is_admin = True
            st.rerun()
        st.info("🔒 Anda sedang dalam mode **Viewer (Hanya Lihat)**.")
    else:
        st.success("🔓 Mode: **Owner / Administrator**")
        if st.button("Kunci Aplikasi (Sign Out)", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()

    st.write("")
    st.caption("UTAMA")
    menu_nav = st.radio(
        "Menu:",
        ["📊 01 Radar Saham ISSI", "🤖 02 Bot Asisten (Auto)", "💼 03 Portofolio Riil"],
        label_visibility="collapsed"
    )

    # Pintasan Akun Pribadi hanya tampil jika login sebagai Admin
    if st.session_state.is_admin:
        st.write("")
        st.caption("AKSES PRIBADI (ADMIN ONLY)")
        st.link_button("💻 DataAnnotation.tech", "https://app.dataannotation.tech", use_container_width=True)
        st.link_button("🎨 Adobe Stock Contributor", "https://contributor.stock.adobe.com", use_container_width=True)
        st.link_button("🎓 Coursera Dashboard", "https://www.coursera.org", use_container_width=True)
        st.link_button("✉️ Gmail Workspace", "https://mail.google.com", use_container_width=True)

@st.cache_data(ttl=600)
def get_market_data():
    return scan_syariah_market()

# ==================== GREETING BANNER ====================
user_name = "Juhdan" if st.session_state.is_admin else "Guest"
st.markdown(f"""
<div class="greeting-banner">
    <div>
        <h1 class="greeting-title">Good morning, {user_name}</h1>
        <p style="color:#94a3b8; font-size:0.85rem; margin:4px 0 0 0;">{'ApexHub Cockpit siap untuk kontrol penuh.' if st.session_state.is_admin else 'Mode peninjau publik: sinyal pasar aktif & analitik terverifikasi.'}</p>
    </div>
    <div style="background:#0b111e; border:1px solid #243247; color:#94a3b8; font-size:0.8rem; padding:6px 14px; border-radius:20px;">
        📅 {date_str} • <b>{time_str}</b>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== MENU 1: RADAR SAHAM ====================
if "01 Radar Saham" in menu_nav:
    with st.spinner("Memindai konstituen saham syariah BEI..."):
        top_stocks, total_scanned = get_market_data()

    buy_count = sum(1 for s in top_stocks if "BUY" in s["status"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Saham Dipindai", f"{total_scanned} Emiten")
    m2.metric("Sinyal Pullback", f"{buy_count} Saham")
    m3.metric("Rasio Risiko", "1 : 2 (ATR)")
    m4.metric("Setup", "Support EMA-20")

    st.write("")
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
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <span style="font-size:1.35rem; font-weight:800; color:#f8fafc;">{s['code']}</span>
                        {badge_html}
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                        <span style="color:#94a3b8;">Harga: <b style="color:#f8fafc;">Rp {int(s['price']):,}</b></span>
                        <span style="color:{c_color}; font-weight:700;">{s['change']:+.2f}%</span>
                    </div>
                    <div style="background:#0c121d; border:1px solid #1a2538; padding:12px; border-radius:12px; font-size:0.82rem; display:grid; grid-template-columns: 1fr 1fr; gap:6px;">
                        <div>🎯 <b>Target TP:</b> <span style="color:#34d399;">Rp {s['tp']:,}</span></div>
                        <div>🛡️ <b>Batas SL:</b> <span style="color:#f87171;">Rp {s['sl']:,}</span></div>
                        <div style="grid-column: span 2; margin-top:4px;">📍 <b>Area Antre:</b> <b style="color:#38bdf8;">{s['entry']}</b></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.line_chart(s["sparkline"], height=80)

    with tab_table:
        table_rows = []
        for s in top_stocks:
            table_rows.append({
                "Emiten": s["code"],
                "Harga": f"Rp {int(s['price']):,}",
                "Perubahan": f"{s['change']:+.2f}%",
                "Keputusan": s["status"],
                "Area Beli": s["entry"],
                "Target TP": f"Rp {s['tp']:,}",
                "Batas SL": f"Rp {s['sl']:,}"
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

# ==================== MENU 2: BOT TRADING ====================
elif "02 Bot Asisten" in menu_nav:
    default_bot = {"cash": 10000000.0, "initial_cash": 10000000.0, "positions": [], "history": []}
    bot_data = load_json(BOT_FILE, default_bot)

    # Konfigurasi hanya bisa diakses oleh Admin
    if st.session_state.is_admin:
        with st.expander("⚙️ Kontrol Modal Bot (Admin Only)", expanded=False):
            c_b1, c_b2 = st.columns([3, 1])
            with c_b1:
                modal_bot = st.number_input("Atur Modal Bot (Rp):", min_value=1000000, value=int(bot_data.get("initial_cash", 10000000)), step=1000000)
            with c_b2:
                st.write("")
                st.write("")
                if st.button("Reset Modal", use_container_width=True):
                    bot_data = {"cash": float(modal_bot), "initial_cash": float(modal_bot), "positions": [], "history": []}
                    save_json(BOT_FILE, bot_data)
                    st.rerun()

    equity_val = sum([p["lots"] * 100 * p.get("current_price", p["buy_price"]) for p in bot_data["positions"]])
    total_val = bot_data["cash"] + equity_val
    overall_pnl = total_val - bot_data["initial_cash"]
    overall_pct = (overall_pnl / bot_data["initial_cash"]) * 100

    bm1, bm2, bm3, bm4 = st.columns(4)
    bm1.metric("💵 Kas Bot", f"Rp {int(bot_data['cash']):,}")
    bm2.metric("📊 Portofolio", f"Rp {int(equity_val):,}")
    bm3.metric("💼 Total Aset", f"Rp {int(total_val):,}")
    bm4.metric("📈 Pertumbuhan", f"Rp {int(overall_pnl):,}", f"{overall_pct:+.2f}%")

    st.write("")
    st.write("##### 🎯 Posisi Saham Berjalan (Read-Only Monitor)")
    if bot_data["positions"]:
        p_rows = []
        for p in bot_data["positions"]:
            c_p = p.get("current_price", p["buy_price"])
            val = p["lots"] * 100 * c_p
            pnl_pos = val - p["total_cost"]
            pct_pos = (pnl_pos / p["total_cost"]) * 100
            p_rows.append({
                "Emiten": p["code"],
                "Lot": f"{p['lots']} Lot",
                "Harga Beli": f"Rp {int(p['buy_price']):,}",
                "Harga Terkini": f"Rp {int(c_p):,}",
                "Target TP": f"Rp {p['tp']:,}",
                "Batas SL": f"Rp {p['sl']:,}",
                "Floating (%)": f"{pct_pos:+.2f}%"
            })
        st.dataframe(pd.DataFrame(p_rows), use_container_width=True, hide_index=True)
    else:
        st.info("💡 Bot sedang memantau sinyal baru.")

    st.write("##### 📜 Buku Jurnal Transaksi Bot")
    if bot_data["history"]:
        clean_hist = [{k: v for k, v in h.items() if not k.startswith("_")} for h in reversed(bot_data["history"])]
        st.dataframe(pd.DataFrame(clean_hist), use_container_width=True, hide_index=True)

# ==================== MENU 3: PORTOFOLIO MANUAL ====================
elif "03 Portofolio Riil" in menu_nav:
    port_data = load_json(DB_FILE, {"open_trades": [], "history": []})

    if not st.session_state.is_admin:
        st.warning("🔒 Halaman ini diproteksi. Masukkan PIN Admin di sidebar untuk menambah atau menutup posisi transaksi.")
    else:
        st.write("##### 📝 Input Transaksi Akun Sekuritas")
        c_in1, c_in2, c_in3, c_in4 = st.columns([2, 2, 2, 1.5])
        with c_in1:
            inp_emiten = st.text_input("Kode Saham:").upper().strip()
        with c_in2:
            inp_lot = st.number_input("Jumlah Lot:", min_value=1, value=10, step=1)
        with c_in3:
            inp_harga = st.number_input("Harga Beli (Rp):", min_value=50, value=2500, step=10)
        with c_in4:
            st.write("")
            st.write("")
            if st.button("Catat Beli", use_container_width=True):
                if inp_emiten:
                    total_cost = inp_lot * 100 * inp_harga
                    port_data["open_trades"].append({
                        "ticker": f"{inp_emiten}.JK",
                        "code": inp_emiten,
                        "lots": inp_lot,
                        "buy_price": inp_harga,
                        "total_cost": total_cost,
                        "date": datetime.now().strftime("%d/%m/%Y")
                    })
                    save_json(DB_FILE, port_data)
                    st.success("Tersimpan!")
                    st.rerun()

    st.write("---")
    st.write("##### 🎯 Rekam Portofolio Terbuka")
    if port_data["open_trades"]:
        for idx, pos in enumerate(port_data["open_trades"]):
            try:
                curr_p = float(yf.Ticker(pos["ticker"]).fast_info.last_price)
            except Exception:
                curr_p = pos["buy_price"]

            curr_val = pos["lots"] * 100 * curr_p
            pnl = curr_val - pos["total_cost"]
            pct = (pnl / pos["total_cost"]) * 100

            c_pos1, c_pos2, c_pos3 = st.columns([3, 3, 2])
            with c_pos1:
                st.markdown(f"**{pos['code']}** ({pos['lots']} Lot)")
                st.caption(f"Beli: Rp {int(pos['buy_price']):,} | Terkini: Rp {int(curr_p):,}")
            with c_pos2:
                pnl_color = "#34d399" if pnl >= 0 else "#f87171"
                st.markdown(f"<span style='color:{pnl_color}; font-weight:700;'>Rp {int(pnl):,} ({pct:+.2f}%)</span>", unsafe_allow_html=True)
            with c_pos3:
                # Tombol Tutup Posisi HANYA BISA DIKLIK OLEH ADMIN
                if st.session_state.is_admin:
                    if st.button("Tutup / Jual", key=f"close_{idx}"):
                        port_data["history"].append({
                            "Tanggal": datetime.now().strftime("%d/%m/%Y"),
                            "Emiten": pos["code"],
                            "Lot": pos["lots"],
                            "Harga Beli": f"Rp {int(pos['buy_price']):,}",
                            "Harga Jual": f"Rp {int(curr_p):,}",
                            "Laba/Rugi": f"Rp {int(pnl):,}",
                            "Hasil (%)": f"{pct:+.2f}%",
                            "_is_win": pnl > 0
                        })
                        port_data["open_trades"].pop(idx)
                        save_json(DB_FILE, port_data)
                        st.rerun()
                else:
                    st.caption("🔒 View Only")
            st.divider()
    else:
        st.info("Belum ada posisi transaksi aktif.")
