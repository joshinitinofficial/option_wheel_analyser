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
""",
    
    "NIFTY OWS with 5% OTM from Jan24 to Dec25": """
🌀 OPTION WHEEL BACKTEST RESULT
Scrip              : NIFTY
PE OTM %           : 5.00 %
CE OTM %           : 5.00 %
Lot Size           : 65
Backtest Period    : 2024-01-25 → 2025-12-30
Bond Return (Ann.) : 6.00 %

        Expiry Type  Strike  Premium    Profit    ITM
0   2024-01-25   PE   20700    57.10   3711.50  False
1   2024-02-29   PE   20300    48.60   3159.00  False
2   2024-03-28   PE   20900    43.00   2795.00  False
3   2024-04-25   PE   21200    31.35   2037.75  False
4   2024-05-30   PE   21400    47.00   3055.00  False
5   2024-06-27   PE   21400   178.00  11570.00  False
6   2024-07-25   PE   22900    70.80   4602.00  False
7   2024-08-29   PE   23200    59.40   3861.00  False
8   2024-09-26   PE   23900    46.35   3012.75  False
9   2024-10-31   PE   24900    57.95   3766.75   True
10  2024-11-28   CE   26100    15.75   1023.75  False
11  2024-12-26   CE   26100     8.60    559.00  False
12  2025-01-30   CE   26100     8.20    533.00  False
13  2025-02-27   CE   26100     9.90    643.50  False
14  2025-05-29   CE   26100    27.70   1800.50  False
15  2025-06-26   CE   26100    62.15   4039.75  False
16  2025-07-31   CE   26100   165.30  10744.50  False
17  2025-08-28   CE   26100    18.35   1192.75  False
18  2025-09-30   CE   26100    15.45   1004.25  False
19  2025-10-28   CE   26100    13.15    854.75  False
20  2025-11-25   CE   26100   318.65  20712.25  False
21  2025-12-30   CE   26100   314.05  20413.25  False

💰 REALIZED PROFIT: 105092.0
🏦 BOND PROFIT: 60547.5
📦 EQUITY MONTHS: 15
📆 TOTAL MONTHS: 24
💼 TOTAL CAPITAL: 1345500
📊 CURRENT STOCK MTM: 67723.5
📍 CURRENT SPOT PRICE: 25941.9
✅ FINAL PROFIT (Incl. MTM): 233363.0
📈 TOTAL RETURN %: 17.34
""",
    
  "NIFTY OWS with 5% OTM from Jan24 to Dec25": """
    🌀 OPTION WHEEL BACKTEST RESULT
Scrip              : NIFTY
PE OTM %           : 1.00 %
CE OTM %           : 1.00 %
Lot Size           : 65
Backtest Period    : 2019-02-28 → 2025-12-30
Bond Return (Ann.) : 6.00 %

        Expiry Type  Strike  Premium    Profit    ITM
0   2019-02-28   PE   10700   138.65   9012.25  False
1   2019-03-28   PE   10700   142.45   9259.25  False
2   2019-04-25   PE   11500   121.60   7904.00  False
3   2019-05-30   PE   11500   239.90  15593.50  False
4   2019-06-27   PE   11800   117.70   7650.50  False
5   2019-07-25   PE   11700   106.55   6925.75   True
6   2019-08-29   CE   11800    15.30    994.50  False
7   2019-09-26   CE   11800     7.05    458.25  False
8   2019-10-31   CE   11800   133.15  15154.75   True
9   2019-11-28   PE   11800   154.00  10010.00  False
10  2019-12-26   PE   12000   102.60   6669.00  False
11  2020-01-30   PE   12000    97.45   6334.25  False
12  2020-02-27   PE   11900   154.50  10042.50   True
13  2020-03-26   CE   12000    66.00   4290.00  False
14  2020-04-30   CE   12000    12.50    812.50  False
15  2020-05-28   CE   12000     3.50    227.50  False
16  2020-06-25   CE   12000     2.30    149.50  False
17  2020-08-27   CE   12000    26.35   1712.75  False
18  2020-09-24   CE   12000    53.20   3458.00  False
19  2020-10-29   CE   12000    20.00   1300.00  False
20  2020-11-26   CE   12000   150.50  16282.50   True
21  2020-12-31   PE   12900   215.85  14030.25  False
22  2021-01-28   PE   13800   225.10  14631.50  False
23  2021-02-25   PE   13700   300.45  19529.25  False
24  2021-03-25   PE   14900   243.70  15840.50   True
25  2021-04-29   CE   15000   148.65   9662.25  False
26  2021-05-27   CE   15000   326.90  27748.50   True
27  2021-06-24   PE   15200   201.70  13110.50  False
28  2021-07-29   PE   15600   186.30  12109.50  False
29  2021-08-26   PE   15600   130.65   8492.25  False
30  2021-09-30   PE   16500   163.00  10595.00  False
31  2021-10-28   PE   17400   235.00  15275.00  False
32  2021-11-25   PE   17700   238.10  15476.50   True
33  2021-12-30   CE   17900   152.25   9896.25  False
34  2022-01-27   CE   17900    68.20   4433.00  False
35  2022-02-24   CE   17900   123.10   8001.50  False
36  2022-05-26   CE   17900   100.75   6548.75  False
37  2022-06-30   CE   17900    12.45    809.25  False
38  2022-07-28   CE   17900     4.40    286.00  False
39  2022-08-25   CE   17900    23.80   1547.00  False
40  2022-09-29   CE   17900   210.25  13666.25  False
41  2022-10-27   CE   17900    51.15   3324.75  False
42  2022-11-24   CE   17900   252.35  29402.75   True
43  2022-12-29   PE   18300   148.70   9665.50   True
44  2023-02-23   CE   18500    91.65   5957.25  False
45  2023-03-29   CE   18500    22.20   1443.00  False
46  2023-04-27   CE   18500     7.35    477.75  False
47  2023-05-25   CE   18500    31.45   2044.25  False
48  2023-06-28   CE   18500   191.25  25431.25   True
49  2023-07-27   PE   18800   113.95   7406.75  False
50  2023-08-31   PE   19500   131.95   8576.75   True
51  2023-09-28   CE   19700    96.00   6240.00  False
52  2023-10-26   CE   19700   225.25  14641.25  False
53  2023-11-30   CE   19700    38.00  15470.00   True
54  2023-12-28   PE   19900   118.50   7702.50  False
55  2024-01-25   PE   21600   206.95  13451.75   True
56  2024-02-29   CE   21800   219.70  27280.50   True
57  2024-03-28   PE   21800   196.65  12782.25  False
58  2024-04-25   PE   22100   167.25  10871.25  False
59  2024-05-30   PE   22300   194.45  12639.25  False
60  2024-06-27   PE   22300   418.15  27179.75  False
61  2024-07-25   PE   23800   234.90  15268.50  False
62  2024-08-29   PE   24200   262.75  17078.75  False
63  2024-09-26   PE   24900   197.45  12834.25  False
64  2024-10-31   PE   25900   208.40  13546.00   True
65  2024-11-28   CE   26200    13.65    887.25  False
66  2024-12-26   CE   26200     7.50    487.50  False
67  2025-01-30   CE   26200     8.05    523.25  False
68  2025-02-27   CE   26200     7.80    507.00  False
69  2025-06-26   CE   26200    50.40   3276.00  False
70  2025-07-31   CE   26200   136.30   8859.50  False
71  2025-08-28   CE   26200    14.50    942.50  False
72  2025-09-30   CE   26200    13.15    854.75  False
73  2025-10-28   CE   26200    10.10    656.50  False
74  2025-11-25   CE   26200   268.95  17481.75  False
75  2025-12-30   CE   26200   267.30  17374.50  False

💰 REALIZED PROFIT: 802389.25
🏦 BOND PROFIT: 93892.5
📦 EQUITY MONTHS: 56
📆 TOTAL MONTHS: 83
💼 TOTAL CAPITAL: 695500
📊 CURRENT STOCK MTM: 2723.5
📍 CURRENT SPOT PRICE: 25941.9
✅ FINAL PROFIT (Incl. MTM): 805112.75
📈 TOTAL RETURN %: 115.76
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
