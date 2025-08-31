import asyncio
import pyshark
import pandas as pd

# 🔹 Fix for Windows event loop issue
if not asyncio.get_event_loop().is_running():
    asyncio.set_event_loop(asyncio.new_event_loop())

def parse_sip(pcap_file):
    cap = pyshark.FileCapture(pcap_file, display_filter="sip")
    sip_data = []
    for pkt in cap:
        try:
            sip_data.append({
                "Time": float(pkt.sniff_timestamp),
                "Source": pkt.ip.src,
                "Destination": pkt.ip.dst,
                "Method": pkt.sip.Method if hasattr(pkt.sip, "Method") else "",
                "Status": pkt.sip.Status_Code if hasattr(pkt.sip, "Status_Code") else ""
            })
        except AttributeError:
            continue
    return pd.DataFrame(sip_data)
