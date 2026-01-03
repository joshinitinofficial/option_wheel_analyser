import streamlit as st
import pandas as pd
import numpy as np
import pytesseract
import cv2
import re
from PIL import Image
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Option Wheel Report Analyser", layout="wide")

st.title("📊 Option Wheel Backtest Report Analyser")
st.caption("Upload screenshot → Get full analytics")

# -----------------------------
# OCR FUNCTION
# -----------------------------
def extract_text_from_image(image):
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)[1]
    text = pytesseract.image_to_string(img)
    return text

# -----------------------------
# PARSE TRADE TABLE
# -----------------------------
def parse_trades(text):
    rows = []
    pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2})\s+(PE|CE)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+(True|False)"
    )

    for match in pattern.finditer(text):
        rows.append({
            "Expiry": match.group(1),
            "Type": match.group(2),
            "Strike": int(match.group(3)),
            "Premium": float(match.group(4)),
            "Profit": float(match.group(5)),
            "ITM": match.group(6) == "True"
        })

    return pd.DataFrame(rows)

# -----------------------------
# PARSE SUMMARY
# -----------------------------
def parse_summary(text):
    summary = {}

    patterns = {
        "option_profit": r"OPTION PROFIT:\s*([\d.]+)",
        "bond_profit": r"BOND PROFIT:\s*([\d.]+)",
        "total_return": r"TOTAL RETURN %:\s*([\d.]+)",
        "months": r"EQUITY MONTHS:\s*(\d+)",
        "capital": r"TOTAL CAPITAL:\s*(\d+)"
    }

    for k, p in patterns.items():
        m = re.search(p, text)
        if m:
            summary[k] = float(m.group(1))

    return summary

# -----------------------------
# FILE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader("Upload Backtest Screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Report", use_column_width=True)

    with st.spinner("Extracting & analysing report..."):
        text = extract_text_from_image(image)

        trades = parse_trades(text)
        summary = parse_summary(text)

    if trades.empty:
        st.error("Could not extract trade data. Please upload a clearer image.")
        st.stop()

    # -----------------------------
    # DATA PREP
    # -----------------------------
    trades["Expiry"] = pd.to_datetime(trades["Expiry"])
    trades = trades.sort_values("Expiry")

    trades["Cumulative PnL"] = trades["Profit"].cumsum()

    trades["Month"] = trades["Expiry"].dt.to_period("M").astype(str)
    monthly = trades.groupby("Month")["Profit"].sum().reset_index()

    avg_monthly_return = monthly["Profit"].mean()

    # Drawdown
    cum = trades["Cumulative PnL"]
    peak = cum.cummax()
    drawdown = cum - peak

    # -----------------------------
    # METRICS
    # -----------------------------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Trades", len(trades))
    c2.metric("Total PnL", f"₹{trades['Profit'].sum():,.0f}")
    c3.metric("Avg Monthly PnL", f"₹{avg_monthly_return:,.0f}")
    c4.metric("ITM Rate", f"{trades['ITM'].mean()*100:.1f}%")

    # -----------------------------
    # EQUITY CURVE
    # -----------------------------
    st.subheader("📈 Equity Curve")

    fig, ax = plt.subplots()
    ax.plot(trades["Expiry"], trades["Cumulative PnL"])
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative PnL")
    ax.grid(True)
    st.pyplot(fig)

    # -----------------------------
    # DRAWDOWN
    # -----------------------------
    st.subheader("📉 Drawdown")

    fig, ax = plt.subplots()
    ax.fill_between(trades["Expiry"], drawdown, color="red", alpha=0.4)
    ax.set_ylabel("Drawdown")
    ax.grid(True)
    st.pyplot(fig)

    # -----------------------------
    # MONTHLY RETURNS
    # -----------------------------
    st.subheader("📊 Monthly Returns")
    st.dataframe(monthly, use_container_width=True)

    fig, ax = plt.subplots()
    ax.bar(monthly["Month"], monthly["Profit"])
    ax.set_xticklabels(monthly["Month"], rotation=90)
    ax.set_ylabel("Monthly PnL")
    st.pyplot(fig)

    # -----------------------------
    # TRADE LOG
    # -----------------------------
    st.subheader("📋 Full Trade Log")
    st.dataframe(trades, use_container_width=True)

    # -----------------------------
    # SUMMARY
    # -----------------------------
    if summary:
        st.subheader("🧾 Extracted Summary")
        st.json(summary)

