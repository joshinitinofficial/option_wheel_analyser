import os
import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec

# ============================
# DATABASE BACKTEST REPORTS
# ============================
DATABASE_DIR = "database"

# Ensure folder exists (safe for Streamlit Cloud)
if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)

# Read all txt files from database folder
report_files = sorted([
    f for f in os.listdir(DATABASE_DIR)
    if f.lower().endswith(".txt")
])

# Dropdown options
BACKTEST_REPORTS = ["-- Paste Manually --"] + report_files

# ============================
# PAGE CONFIG
# ============================
st.set_page_config(page_title="Option Wheel Dashboard", layout="wide")

# ============================
# CSS
# ============================
st.markdown("""
<style>
body { background-color: #0e1117; }

.info-card {
    background: #111827;
    padding: 10px 14px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 6px;
}

.card-title {
    font-size: 10px;
    color: #9aa4b2;
}

.card-value {
    font-size: 17px;
    font-weight: 600;
    color: white;
}

.v-gap { margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("Option Wheel Performance Dashboard")

# ============================
# REPORT SELECTION DROPDOWN
# ============================
selected_report = st.selectbox(
    "Select Backtest Report",
    options=BACKTEST_REPORTS
)

# ============================
# SESSION STATE INIT
# ============================
if "raw_text" not in st.session_state:
    st.session_state.raw_text = ""

# ============================
# AUTO-FILL TEXT AREA
# ============================
if selected_report != "-- Paste Manually --":
    file_path = os.path.join(DATABASE_DIR, selected_report)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            st.session_state.raw_text = f.read()
    except Exception as e:
        st.error(f"Error reading file: {e}")


# ============================
# TEXT INPUT AREA
# ============================
raw_text = st.text_area(
    "Backtest Output",
    height=220,
    value=st.session_state.raw_text
)


# ============================
# HELPERS
# ============================
def parse_trades(text):
    rows = []
    pattern = re.compile(
        r"\d+\s+(\d{4}-\d{2}-\d{2})\s+(PE|CE)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+(True|False)"
    )
    for m in pattern.finditer(text):
        rows.append({
            "Expiry": m.group(1),
            "Profit": float(m.group(5))
        })
    return pd.DataFrame(rows)

def val(text, pattern):
    m = re.search(pattern, text)
    return m.group(1).strip() if m else None

def card(col, title, value):
    col.markdown(f"""
    <div class="info-card">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================
# MAIN
# ============================
if raw_text.strip():

    trades = parse_trades(raw_text)
    if trades.empty:
        st.error("No trades detected.")
        st.stop()

    # -------- Strategy Info --------
    scrip = val(raw_text, r"Scrip\s*:\s*(\w+)")
    pe_otm = val(raw_text, r"PE OTM %\s*:\s*([\d.]+)")
    ce_otm = val(raw_text, r"CE OTM %\s*:\s*([\d.]+)")
    lot_size = val(raw_text, r"Lot Size\s*:\s*(\d+)")
    period = val(raw_text, r"Backtest Period\s*:\s*(.+)")

    # -------- Summary --------
    realised_profit = float(val(raw_text, r"REALIZED PROFIT:\s*([\d.]+)") or 0)
    bond_profit = float(val(raw_text, r"BOND PROFIT:\s*([\d.]+)") or 0)
    equity_months = val(raw_text, r"EQUITY MONTHS:\s*(\d+)")
    stock_mtm = float(val(raw_text, r"CURRENT STOCK MTM:\s*([\d.]+)") or 0)
    total_capital = float(val(raw_text, r"TOTAL CAPITAL:\s*(\d+)") or 0)
    final_profit = float(val(raw_text, r"FINAL PROFIT .*:\s*([\d.]+)") or 0)
    total_return = float(val(raw_text, r"TOTAL RETURN %:\s*([\d.]+)") or 0)
    total_months = int(val(raw_text, r"TOTAL MONTHS:\s*(\d+)") or 1)

    avg_monthly_profit = final_profit / total_months
    avg_monthly_profit_pct = (avg_monthly_profit / total_capital * 100) if total_capital else 0
    drawdown_text = f"Same as {scrip} – {pe_otm}%"

    # -------- Data prep --------
    trades["Expiry"] = pd.to_datetime(trades["Expiry"])
    trades = trades.sort_values("Expiry")
    trades["CumPnL"] = trades["Profit"].cumsum()
    trades["Month"] = trades["Expiry"].dt.to_period("M").astype(str)
    monthly = trades.groupby("Month")["Profit"].sum().reset_index()

    # ============================
    # STRATEGY DETAILS
    # ============================
    st.markdown("### Strategy Details")
    a1, a2, a3, a4, a5 = st.columns(5)
    card(a1, "Scrip", scrip)
    card(a2, "PE OTM %", f"{pe_otm}%")
    card(a3, "CE OTM %", f"{ce_otm}%")
    card(a4, "Lot Size", lot_size)
    card(a5, "Backtest Period", period)

    # ============================
    # PERFORMANCE SUMMARY
    # ============================
    st.markdown("### Performance Summary")

    r1 = st.columns(5)
    card(r1[0], "Realised Profit", f"₹{realised_profit:,.0f}")
    card(r1[1], "Bond Profit", f"₹{bond_profit:,.0f}")
    card(r1[2], "Equity Holding Months", equity_months)
    card(r1[3], "Current Stock MTM", f"₹{stock_mtm:,.0f}")
    card(r1[4], "Total Return", f"{total_return:.2f}%")

    st.markdown('<div class="v-gap"></div>', unsafe_allow_html=True)

    r2 = st.columns(5)
    card(r2[0], "Total Capital", f"₹{total_capital:,.0f}")
    card(r2[1], "Final Profit", f"₹{final_profit:,.0f}")
    card(r2[2], "Avg Monthly Profit", f"₹{avg_monthly_profit:,.0f}")
    card(r2[3], "Avg Monthly Profit %", f"{avg_monthly_profit_pct:.2f}%")
    card(r2[4], "Drawdown", drawdown_text)

    # ============================
    # ONE FIGURE – TWO CHARTS
    # ============================
    fig = plt.figure(figsize=(14, 4))
    gs = GridSpec(1, 2, width_ratios=[2.2, 1])

    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    # Equity Curve
    ax1.plot(trades["Expiry"], trades["CumPnL"], color="#2dd4bf", linewidth=2)
    ax1.fill_between(trades["Expiry"], trades["CumPnL"], alpha=0.15, color="#2dd4bf")
    ax1.text(0.5, 0.96, "Equity Curve", transform=ax1.transAxes,
             ha="center", va="top", fontsize=9, color="#cbd5e1")
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax1.tick_params(colors="white", labelsize=8)

    # Monthly PnL (Year-wise X-axis)
    monthly["Year"] = pd.to_datetime(monthly["Month"]).dt.year
    yearly = monthly.groupby("Year")["Profit"].sum().reset_index()

    colors = ["#22c55e" if x >= 0 else "#ef4444" for x in yearly["Profit"]]

    ax2.bar(yearly["Year"].astype(str), yearly["Profit"], color=colors, width=0.6)
    
    ax2.text(
        0.5, 0.96, "Monthly PnL",
        transform=ax2.transAxes,
        ha="center", va="top",
        fontsize=9, color="#cbd5e1"
    )

    pad = (yearly["Profit"].max() - yearly["Profit"].min()) * 0.25
    ax2.set_ylim(yearly["Profit"].min() - pad, yearly["Profit"].max() + pad)

    ax2.tick_params(axis="x", labelsize=8, colors="white")
    ax2.tick_params(axis="y", labelsize=7, colors="white")


    for ax in [ax1, ax2]:
        ax.set_facecolor("#0e1117")
        ax.spines[:].set_color("#444")

    fig.patch.set_facecolor("#0e1117")
    fig.subplots_adjust(left=0.04, right=0.99, top=0.92, bottom=0.2, wspace=0.15)

    st.pyplot(fig, use_container_width=True)

    with st.expander("View Full Trade Log"):
        st.dataframe(trades, use_container_width=True)
