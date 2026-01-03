import streamlit as st
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt

st.set_page_config(page_title="Option Wheel Report Analyser", layout="wide")

st.title("📊 Option Wheel Backtest Report Analyser")
st.caption("Paste Option Wheel backtest output → Get full analytics")

# =====================================================
# INPUT
# =====================================================
raw_text = st.text_area(
    "Paste Backtest Output Here",
    height=400
)

# =====================================================
# PARSE TRADE TABLE
# =====================================================
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

# =====================================================
# PARSE SUMMARY (ROBUST)
# =====================================================
def parse_summary(text):
    fields = {
        "Option Profit": r"OPTION PROFIT:\s*([\d.]+)",
        "Bond Profit": r"BOND PROFIT:\s*([\d.]+)",
        "Equity Months": r"EQUITY MONTHS:\s*(\d+)",
        "Total Months": r"TOTAL MONTHS:\s*(\d+)",
        "Total Capital": r"TOTAL CAPITAL:\s*(\d+)",
        "Current Stock MTM": r"CURRENT STOCK MTM:\s*([\d.]+)",
        "Spot Price": r"CURRENT SPOT PRICE:\s*([\d.]+)",
        "Final Profit": r"FINAL PROFIT \(Incl\. MTM\):\s*([\d.]+)",
        "Total Return %": r"TOTAL RETURN %:\s*([\d.]+)"
    }

    summary = {}
    for k, p in fields.items():
        m = re.search(p, text)
        if m:
            summary[k] = float(m.group(1))

    return summary

# =====================================================
# MAIN LOGIC
# =====================================================
if raw_text.strip():

    trades = parse_trades(raw_text)
    summary = parse_summary(raw_text)

    if trades.empty:
        st.error("❌ No trades detected. Please paste full backtest output.")
        st.stop()

    # -------------------------
    # DATA PREP
    # -------------------------
    trades["Expiry"] = pd.to_datetime(trades["Expiry"])
    trades = trades.sort_values("Expiry")

    trades["Cumulative PnL"] = trades["Profit"].cumsum()
    trades["Month"] = trades["Expiry"].dt.to_period("M").astype(str)

    monthly = trades.groupby("Month")["Profit"].sum().reset_index()
    avg_monthly = monthly["Profit"].mean()

    cum = trades["Cumulative PnL"]
    peak = cum.cummax()
    drawdown = cum - peak

    # =====================================================
    # METRICS
    # =====================================================
    st.subheader("📌 Key Metrics")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Trades", len(trades))
    c2.metric("Option Profit", f"₹{summary.get('Option Profit', trades['Profit'].sum()):,.0f}")
    c3.metric("Avg Monthly PnL", f"₹{avg_monthly:,.0f}")
    c4.metric("ITM %", f"{trades['ITM'].mean()*100:.1f}%")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Bond Profit", f"₹{summary.get('Bond Profit', 0):,.0f}")
    c6.metric("Stock MTM", f"₹{summary.get('Current Stock MTM', 0):,.0f}")
    c7.metric("Final Profit", f"₹{summary.get('Final Profit', 0):,.0f}")
    c8.metric("Total Return %", f"{summary.get('Total Return %', 0):.2f}%")

    # =====================================================
    # EQUITY CURVE
    # =====================================================
    st.subheader("📈 Option Strategy Equity Curve")

    fig, ax = plt.subplots()
    ax.plot(trades["Expiry"], trades["Cumulative PnL"], linewidth=2)
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Option PnL")
    ax.grid(True)
    st.pyplot(fig)

    # =====================================================
    # DRAWDOWN
    # =====================================================
    st.subheader("📉 Drawdown")

    fig, ax = plt.subplots()
    ax.fill_between(trades["Expiry"], drawdown, color="red", alpha=0.35)
    ax.set_ylabel("Drawdown")
    ax.grid(True)
    st.pyplot(fig)

    # =====================================================
    # MONTHLY RETURNS
    # =====================================================
    st.subheader("📊 Monthly Returns")

    st.dataframe(monthly, use_container_width=True)

    fig, ax = plt.subplots()
    ax.bar(monthly["Month"], monthly["Profit"])
    ax.set_xticklabels(monthly["Month"], rotation=90)
    ax.set_ylabel("Monthly PnL")
    ax.grid(True)
    st.pyplot(fig)

    # =====================================================
    # TRADE LOG
    # =====================================================
    st.subheader("📋 Full Trade Log")
    st.dataframe(trades, use_container_width=True)

    # =====================================================
    # SUMMARY JSON
    # =====================================================
    st.subheader("🧾 Parsed Summary")
    st.json(summary)
