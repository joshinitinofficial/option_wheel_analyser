import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec

# ============================
# HARDCODED BACKTEST REPORTS
# ============================
BACKTEST_REPORTS = {
    "-- Paste Manually --": "",
    
    "NIFTY OWS with 1% OTM from Jan24 to Dec25": """
🌀 OPTION WHEEL BACKTEST RESULT
Scrip              : NIFTY
PE OTM %           : 1.00 %
CE OTM %           : 1.00 %
Lot Size           : 65
Backtest Period    : 2024-01-25 → 2025-12-30
Bond Return (Ann.) : 6.00 %

        Expiry Type  Strike  Premium    Profit    ITM
0   2024-01-25   PE   21600   206.95  13451.75   True
1   2024-02-29   CE   21800   219.70  27280.50   True
2   2024-03-28   PE   21800   196.65  12782.25  False
3   2024-04-25   PE   22100   167.25  10871.25  False
4   2024-05-30   PE   22300   194.45  12639.25  False
5   2024-06-27   PE   22300   418.15  27179.75  False
6   2024-07-25   PE   23800   234.90  15268.50  False
7   2024-08-29   PE   24200   262.75  17078.75  False
8   2024-09-26   PE   24900   197.45  12834.25  False
9   2024-10-31   PE   25900   208.40  13546.00   True
10  2024-11-28   CE   26200    13.65    887.25  False
11  2024-12-26   CE   26200     7.50    487.50  False
12  2025-01-30   CE   26200     8.05    523.25  False
13  2025-02-27   CE   26200     7.80    507.00  False
14  2025-06-26   CE   26200    50.40   3276.00  False
15  2025-07-31   CE   26200   136.30   8859.50  False
16  2025-08-28   CE   26200    14.50    942.50  False
17  2025-09-30   CE   26200    13.15    854.75  False
18  2025-10-28   CE   26200    10.10    656.50  False
19  2025-11-25   CE   26200   268.95  17481.75  False
20  2025-12-30   CE   26200   267.30  17374.50  False

💰 REALIZED PROFIT: 214782.75
🏦 BOND PROFIT: 49140.0
📦 EQUITY MONTHS: 17
📆 TOTAL MONTHS: 24
💼 TOTAL CAPITAL: 1404000
📊 CURRENT STOCK MTM: 2723.5
📍 CURRENT SPOT PRICE: 25941.9
✅ FINAL PROFIT (Incl. MTM): 266646.25
📈 TOTAL RETURN %: 18.99
""",

    "NIFTY OWS with 2% OTM from Jan24 to Dec25": """
🌀 OPTION WHEEL BACKTEST RESULT
Scrip              : NIFTY
PE OTM %           : 2.00 %
CE OTM %           : 2.00 %
Lot Size           : 65
Backtest Period    : 2024-01-25 → 2025-12-30
Bond Return (Ann.) : 6.00 %

        Expiry Type  Strike  Premium    Profit    ITM
0   2024-01-25   PE   21300   134.30   8729.50  False
1   2024-02-29   PE   20900   138.00   8970.00  False
2   2024-03-28   PE   21600   142.40   9256.00  False
3   2024-04-25   PE   21800    99.00   6435.00  False
4   2024-05-30   PE   22100   142.15   9239.75  False
5   2024-06-27   PE   22100   347.80  22607.00  False
6   2024-07-25   PE   23600   178.00  11570.00  False
7   2024-08-29   PE   23900   172.40  11206.00  False
8   2024-09-26   PE   24600   126.00   8190.00  False
9   2024-10-31   PE   25700   159.00  10335.00   True
10  2024-11-28   CE   26200    13.65    887.25  False
11  2024-12-26   CE   26200     7.50    487.50  False
12  2025-01-30   CE   26200     8.05    523.25  False
13  2025-02-27   CE   26200     7.80    507.00  False
14  2025-06-26   CE   26200    50.40   3276.00  False
15  2025-07-31   CE   26200   136.30   8859.50  False
16  2025-08-28   CE   26200    14.50    942.50  False
17  2025-09-30   CE   26200    13.15    854.75  False
18  2025-10-28   CE   26200    10.10    656.50  False
19  2025-11-25   CE   26200   268.95  17481.75  False
20  2025-12-30   CE   26200   267.30  17374.50  False

💰 REALIZED PROFIT: 158388.75
🏦 BOND PROFIT: 62302.5
📦 EQUITY MONTHS: 15
📆 TOTAL MONTHS: 24
💼 TOTAL CAPITAL: 1384500
📊 CURRENT STOCK MTM: 15723.5
📍 CURRENT SPOT PRICE: 25941.9
✅ FINAL PROFIT (Incl. MTM): 236414.75
📈 TOTAL RETURN %: 17.08
"""
}


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
    options=list(BACKTEST_REPORTS.keys())
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
    st.session_state.raw_text = BACKTEST_REPORTS[selected_report]

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

    # Monthly PnL
    colors = ["#22c55e" if x >= 0 else "#ef4444" for x in monthly["Profit"]]
    ax2.bar(monthly["Month"], monthly["Profit"], color=colors, width=0.65)
    ax2.text(0.5, 0.96, "Monthly PnL", transform=ax2.transAxes,
             ha="center", va="top", fontsize=9, color="#cbd5e1")
    pad = (monthly["Profit"].max() - monthly["Profit"].min()) * 0.25
    ax2.set_ylim(monthly["Profit"].min() - pad, monthly["Profit"].max() + pad)
    ax2.tick_params(axis="x", rotation=90, labelsize=7, colors="white")
    ax2.tick_params(axis="y", labelsize=7, colors="white")

    for ax in [ax1, ax2]:
        ax.set_facecolor("#0e1117")
        ax.spines[:].set_color("#444")

    fig.patch.set_facecolor("#0e1117")
    fig.subplots_adjust(left=0.04, right=0.99, top=0.92, bottom=0.2, wspace=0.15)

    st.pyplot(fig, use_container_width=True)

    with st.expander("View Full Trade Log"):
        st.dataframe(trades, use_container_width=True)
