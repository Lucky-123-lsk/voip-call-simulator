import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="VoIP Call Tracing Dashboard", page_icon="📞", layout="wide")

st.title("📞 VoIP Call Tracing Dashboard")

# Load pre-parsed CSV
try:
    df = pd.read_csv("sip_calls.csv")
except FileNotFoundError:
    st.error("❌ sip_calls.csv not found. Please run parse_voip.py first.")
    st.stop()

# Show SIP message table
st.subheader("📋 SIP Messages")
st.dataframe(df)

# Call Summary
st.subheader("📊 Call Summary")
call_summary = df.groupby("Call_ID")["Method"].apply(list)
st.write(call_summary)

# Visualization: Call Flow
st.subheader("📈 SIP Call Flow Diagram")
participants = list(pd.concat([df["Source"], df["Destination"]]).unique())
y_positions = {p: i for i, p in enumerate(participants)}

fig, ax = plt.subplots(figsize=(12,6))
for _, row in df.iterrows():
    ax.plot([row["Time"], row["Time"]],
            [y_positions[row["Source"]], y_positions[row["Destination"]]],
            marker="o")
    ax.text(row["Time"],
            (y_positions[row["Source"]] + y_positions[row["Destination"]]) / 2,
            row["Method"], fontsize=8)

ax.set_yticks(range(len(participants)))
ax.set_yticklabels(participants)
ax.set_title("VoIP SIP Call Flow")
ax.set_xlabel("Time")
ax.set_ylabel("Participants")

st.pyplot(fig)
