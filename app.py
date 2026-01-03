import streamlit as st
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ============================
# PAGE CONFIG
# ============================
st.set_page_config(
    page_title="Option Wheel Dashboard",
    layout="wide"
)

# ============================
# DARK THEME CSS
# ============================
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.metric-card {
    background: #161a23;
    padding: 14px;
    border-radius: 14px;
    text-align: center;
}
.metric-title {
    font-size: 11px;
    color: #9aa4b2;
}
.metric-value {
    font-size: 22px;
    font-weight: 600;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🌀 Option Wheel Performance Dashboard")

# ============================
# INPUT
# ============================
raw_text = st.text_area(
    "Paste Backtest Output",
    height=240
)

# ============================
# PARSERS
# ============================
def parse_trades(text):
    rows = []
    pattern = re.compile(
        r"\d+\s+(\d{4}-\d{2}-\d{2})\s+(PE|CE)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+(True|False)"
    )
    for m in pattern.finditer(text):
        rows.append({
            "Expiry": m.group(1),
            "Type": m.group(2),
            "Strike": int(m.group(3)),
            "Premium": float(m.group(4)),
            "Profit": float(m.group(5)),
            "ITM": m.group(6) == "True"
        })
    return pd.DataFrame(rows)

def parse_summary(text):
    fields = {
        "Option Profit": r"OPTION PROFIT:\s*([\d.]+)",
        "Final Profit": r"FINAL PROFIT \(Incl\. MTM\):\s*([\d.]+)",
        "Total Return %": r"TOTAL RETURN %:\s*([\d.]+)"
    }
    out = {}
    for k, p in fields.items():
        m = re.search(p, text)
        if m:
            out[k] = float(m.group(1))
    return out

# ============================
# MAIN
# ============================
if raw_text.strip():

    trades = parse_trades(raw_text)
    summary = parse_summary(raw_text)

    if trades.empty:
        st.error("No trades detected.")
        st.stop()

    trades["Expiry"] = pd.to_datetime(trades["Expiry"])
    trades = trades.sort_values("Expiry")

    trades["CumPnL"] = trades["Profit"].cumsum()
    trades["Month"] = trades["Expiry"].dt.to_period("M").astype(str)

    monthly = trades.groupby("Month")["Profit"].sum().reset_index()
    avg_monthly = monthly["Profit"].mean()

    # ============================
    # TOP METRICS
    # ============================
    c1, c2, c3, c4, c5 = st.columns(5)

    def card(col, title, value):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    card(c1, "Total Trades", len(trades))
    card(c2, "Option Profit", f"₹{summary.get('Option Profit', trades['Profit'].sum()):,.0f}")
    card(c3, "Final Profit", f"₹{summary.get('Final Profit', 0):,.0f}")
    card(c4, "Total Return", f"{summary.get('Total Return %', 0):.2f}%")
    card(c5, "Avg Monthly PnL", f"₹{avg_monthly:,.0f}")

    # ============================
    # CHARTS ROW
    # ============================
    left, right = st.columns([2.2, 1])

    # -------- EQUITY CURVE --------
    with left:
        st.markdown("**📈 Equity Curve**")

        fig, ax = plt.subplots(figsize=(6.5, 3))

        ax.plot(trades["Expiry"], trades["CumPnL"], color="#2dd4bf", linewidth=2)
        ax.fill_between(trades["Expiry"], trades["CumPnL"], alpha=0.15, color="#2dd4bf")

        ax.set_facecolor("#0e1117")
        fig.patch.set_facecolor("#0e1117")

        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        ax.tick_params(colors="white", labelsize=8)
        ax.spines[:].set_color("#444")
        ax.set_ylabel("PnL", color="white", fontsize=8)

        st.pyplot(fig, use_container_width=True)

    # -------- MONTHLY PNL --------
    with right:
        st.markdown("**📊 Monthly PnL**")

        fig, ax = plt.subplots(figsize=(4, 3))

        colors = ["#22c55e" if x >= 0 else "#ef4444" for x in monthly["Profit"]]

        ax.bar(
            monthly["Month"],
            monthly["Profit"],
            color=colors,
            width=0.65
        )

        # Dynamic Y scaling (visual padding)
        ymax = monthly["Profit"].max()
        ymin = monthly["Profit"].min()
        pad = (ymax - ymin) * 0.25
        ax.set_ylim(ymin - pad, ymax + pad)

        ax.set_facecolor("#0e1117")
        fig.patch.set_facecolor("#0e1117")

        ax.tick_params(axis="x", rotation=90, colors="white", labelsize=7)
        ax.tick_params(axis="y", colors="white", labelsize=7)
        ax.spines[:].set_color("#444")

        st.pyplot(fig, use_container_width=True)

    # ============================
    # TRADE LOG
    # ============================
    with st.expander("📋 View Full Trade Log"):
        st.dataframe(trades, use_container_width=True)
