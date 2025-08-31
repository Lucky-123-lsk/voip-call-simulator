import asyncio
import pyshark
import pandas as pd

# 🔹 Fix for Windows event loop issue
if not asyncio.get_event_loop().is_running():
    asyncio.set_event_loop(asyncio.new_event_loop())

def parse_rtp(pcap_file):
    cap = pyshark.FileCapture(pcap_file, display_filter="rtp")
    rtp_data = []
    last_time = None
    last_seq = None

    for pkt in cap:
        try:
            time = float(pkt.sniff_timestamp)
            seq = int(pkt.rtp.seq)
            src = pkt.ip.src
            dst = pkt.ip.dst
            ssrc = pkt.rtp.ssrc
            ts = pkt.rtp.timestamp
            ptype = pkt.rtp.payload_type

            # Calculate jitter (variation in inter-packet arrival)
            jitter = None
            if last_time is not None:
                jitter = abs((time - last_time))
            last_time = time

            # Detect packet loss
            loss = None
            if last_seq is not None:
                expected = last_seq + 1
                if seq != expected:
                    loss = seq - expected
            last_seq = seq

            rtp_data.append({
                "Time": time,
                "Source": src,
                "Destination": dst,
                "SSRC": ssrc,
                "Sequence": seq,
                "Timestamp": ts,
                "PayloadType": ptype,
                "Jitter": jitter,
                "Loss": loss
            })

        except AttributeError:
            continue

    return pd.DataFrame(rtp_data)
