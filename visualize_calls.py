import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from parse_sip import parse_sip
from parse_rtp import parse_rtp

PCAP_FILE = "SIP-Call-Flow-Over-TCP.pcap"

def plot_sip_call_flow(sip_df):
    """Draws a SIP call flow diagram with arrows between Source and Destination"""
    fig, ax = plt.subplots(figsize=(12, 4))

    # Map each unique participant to a vertical position
    participants = list(pd.unique(sip_df[["Source", "Destination"]].values.ravel()))
    participant_map = {p: i for i, p in enumerate(participants)}
    
    for i, row in sip_df.iterrows():
        src_y = participant_map[row["Source"]]
        dst_y = participant_map[row["Destination"]]
        ax.annotate(
            row["Method"],
            xy=(row["Time"], dst_y),
            xytext=(row["Time"], src_y),
            arrowprops=dict(arrowstyle="->", color="blue", lw=1.5),
            fontsize=9,
            ha="center"
        )

    # Set Y-axis labels and style
    ax.set_yticks(list(participant_map.values()))
    ax.set_yticklabels(list(participant_map.keys()))
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Participants")
    ax.set_title("SIP Call Flow Diagram")
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    return fig

def main():
    st.set_page_config(page_title="VoIP Call Tracing Dashboard", layout="wide")
    st.title("📞 VoIP Call Tracing Dashboard")

    # Parse SIP and RTP
    sip_df = parse_sip(PCAP_FILE)
    rtp_df = parse_rtp(PCAP_FILE)

    # ---------------- SIP Analysis ----------------
    st.header("📡 SIP Analysis")

    if not sip_df.empty:
        st.subheader("📋 SIP Messages")
        st.dataframe(sip_df, use_container_width=True)

        st.subheader("📊 Call Summary")
        call_summary = sip_df.groupby(["Source", "Destination"])["Method"].apply(list)
        st.write(call_summary)

        st.subheader("📈 SIP Call Flow Diagram")
        fig = plot_sip_call_flow(sip_df)
        st.pyplot(fig)
    else:
        st.warning("No SIP packets found in the capture.")

    # ---------------- RTP Analysis ----------------
    st.header("🎧 RTP Analysis")
    st.subheader("🎶 RTP Packet Details")
    if not rtp_df.empty:
        st.dataframe(rtp_df, use_container_width=True)

        st.subheader("📊 RTP Sequence Flow")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(rtp_df["Time"], rtp_df["Sequence"], marker=".", linestyle="-", color="green")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("RTP Sequence Number")
        ax.set_title("RTP Packet Sequence Progression")
        ax.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig)

        st.subheader("📉 RTP Jitter Over Time")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(rtp_df["Time"], rtp_df["Jitter"], color="red", marker="o")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Jitter (s)")
        ax.set_title("Inter-packet Jitter")
        ax.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig)

        st.subheader("❌ RTP Packet Loss")
        loss_count = rtp_df["Loss"].dropna().sum()
        st.metric("Total Packet Loss", f"{int(loss_count)} packets")
    else:
        st.warning("No RTP packets found in the capture.")

if __name__ == "__main__":
    main()
