from scapy.all import sniff, Raw

def packet_callback(packet):
    if packet.haslayer(Raw):
        print("[INTERCEPTED] Raw Data:", packet[Raw].load)

sniff(iface="enp0s3", filter="tcp port 3001 3002 3003", prn=packet_callback, store=0)
