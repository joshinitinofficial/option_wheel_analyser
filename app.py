import streamlit as st
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ============================
# PAGE CONFIG
# ============================
st.set_page_config(page_title="Option Wheel Dashboard", layout="wide")

# ============================
# DARK THEME CSS
# ============================
st.markdown("""
<style>
body { background-color: #0e1117; }

.info-card {
    background: #111827;
    padding: 10px 14px;
    border-radius: 10px;
    text-align: center;
}

.metric-card {
    background: #161a23;
    padding: 14px;
    border-radius: 14px;
    text-align: center;
}

.card-title {
    font-size: 11px;
    color: #9aa4b2;
}

.card-value {
    font-size: 20px;
    font-weight: 600;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🌀 Option Wheel Performance Dashboard")

# ============================
# INPUT
# ============================
raw_text = st.text_area("Paste Backtest Output", height=240)

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

def parse_value(text, pattern):
    m = re.search(pattern, text)
    return m.group(1).strip() if m else None

# ============================
# MAIN
# ============================
if raw_text.strip():

    trades = parse_trades(raw_text)
    if trades.empty:
        st.error("No trades detected.")
        st.stop()

    # ---- Strategy Info ----
    scrip = parse_value(raw_text, r"Scrip\s*:\s*(\w+)")
    pe_otm = parse_value(raw_text, r"PE OTM %\s*:\s*([\d.]+ %)")
    ce_otm = parse_value(raw_text, r"CE OTM %\s*:\s*([\d.]+ %)")
    lot_size = parse_value(raw_text, r"Lot Size\s*:\s*(\d+)")
    period = parse_value(raw_text, r"Backtest Period\s*:\s*(.+)")

    # ---- Summary ----
    realised_profit = float(parse_value(raw_text, r"OPTION PROFIT:\s*([\d.]+)") or trades["Profit"].sum())
    bond_profit = float(parse_value(raw_text, r"BOND PROFIT:\s*([\d.]+)") or 0)
    equity_months = parse_value(raw_text, r"EQUITY MONTHS:\s*(\d+)")
    stock_mtm = float(parse_value(raw_text, r"CURRENT STOCK MTM:\s*([\d.]+)") or 0)
    final_profit = float(parse_value(raw_text, r"FINAL PROFIT .*:\s*([\d.]+)") or 0)
    total_return = float(parse_value(raw_text, r"TOTAL RETURN %:\s*([\d.]+)") or 0)

    # ---- Data prep ----
    trades["Expiry"] = pd.to_datetime(trades["Expiry"])
    trades = trades.sort_values("Expiry")
    trades["CumPnL"] = trades["Profit"].cumsum()
    trades["Month"] = trades["Expiry"].dt.to_period("M").astype(str)

    monthly = trades.groupby("Month")["Profit"].sum().reset_index()
    avg_monthly = monthly["Profit"].mean()

    # ============================
    # STRATEGY INFO ROW
    # ============================
    st.markdown("### 📌 Strategy Details")
    i1, i2, i3, i4, i5 = st.columns(5)

    def info(col, title, value):
        col.markdown(f"""
        <div class="info-card">
            <div class="card-title">{title}</div>
            <div class="card-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    info(i1, "Scrip", scrip)
    info(i2, "PE OTM %", pe_otm)
    info(i3, "CE OTM %", ce_otm)
    info(i4, "Lot Size", lot_size)
    info(i5, "Backtest Period", period)

    # ============================
    # PERFORMANCE METRICS
    # ============================
    st.markdown("### 📊 Performance Summary")
    m1, m2, m3, m4, m5 = st.columns(5)

    info(m1, "Realised Profit", f"₹{realised_profit:,.0f}")
    info(m2, "Bond Profit", f"₹{bond_profit:,.0f}")
    info(m3, "Equity Holding Months", equity_months)
    info(m4, "Current Stock MTM", f"₹{stock_mtm:,.0f}")
    info(m5, "Total Return", f"{total_return:.2f}%")

    # ============================
    # CHARTS
    # ============================
    left, right = st.columns([2.2, 1])

    with left:
        st.markdown("**📈 Equity Curve**")
        fig, ax = plt.subplots(figsize=(6.5, 3))
        ax.plot(trades["Expiry"], trades["CumPnL"], color="#2dd4bf", linewidth=2)
        ax.fill_between(trades["Expiry"], trades["CumPnL"], alpha=0.15, color="#2dd4bf")
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.tick_params(colors="white", labelsize=8)
        ax.set_facecolor("#0e1117")
        fig.patch.set_facecolor("#0e1117")
        ax.spines[:].set_color("#444")
        st.pyplot(fig, use_container_width=True)

    with right:
        st.markdown("**📊 Monthly PnL**")
        fig, ax = plt.subplots(figsize=(4, 3))
        colors = ["#22c55e" if x >= 0 else "#ef4444" for x in monthly["Profit"]]
        ax.bar(monthly["Month"], monthly["Profit"], color=colors, width=0.65)
        pad = (monthly["Profit"].max() - monthly["Profit"].min()) * 0.25
        ax.set_ylim(monthly["Profit"].min() - pad, monthly["Profit"].max() + pad)
        ax.tick_params(axis="x", rotation=90, labelsize=7, colors="white")
        ax.tick_params(axis="y", labelsize=7, colors="white")
        ax.set_facecolor("#0e1117")
        fig.patch.set_facecolor("#0e1117")
        ax.spines[:].set_color("#444")
        st.pyplot(fig, use_container_width=True)

    # ============================
    # TRADE LOG
    # ============================
    with st.expander("📋 View Full Trade Log"):
        st.dataframe(trades, use_container_width=True)
