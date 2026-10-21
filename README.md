[English](README.md) | [עברית](README.he.md)

# MITM Lab Toolkit

A small set of Python / Scapy scripts that build a man-in-the-middle position on a local network and demonstrate three classic LAN attacks at the packet level: ARP poisoning, DNS spoofing, and TCP RST injection. Built as a hands-on lab for understanding how these techniques actually work, rather than relying on a ready-made tool.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Scapy](https://img.shields.io/badge/built%20with-Scapy-green)
![Purpose](https://img.shields.io/badge/purpose-educational-orange)

> **Authorized use only.** These scripts are for learning and for testing on networks and devices you own or have explicit written permission to test. Using them against systems you do not own is illegal in most places. You are responsible for how you use this code.

## Contents

- [How it fits together](#how-it-fits-together)
- [Requirements](#requirements)
- [Finding your interface index](#finding-your-interface-index)
- [Scripts](#scripts)
  - [arp_spoofer.py](#arp_spooferpy)
  - [DNS_POISION.py](#dns_poisionpy)
  - [RST_PKTS.py](#rst_pktspy)
  - [mac_fixer.py](#mac_fixerpy)
- [Disclaimer](#disclaimer)

## How it fits together

The scripts are meant to run together. First you put yourself in the middle with ARP poisoning, then you run the DNS and RST scripts on top of that position.

```mermaid
flowchart LR
    VIC["Victim device"] <-->|traffic| ATT["My PC<br/>(attacker / MITM)"]
    ATT <-->|traffic| GW["Router / Internet"]
```

All of the victim's traffic is forced through your computer, which sits between the victim and the router. From that position the three scripts run: ARP poisoning creates the position, then DNS spoofing and TCP RST act on the traffic passing through.

Typical order:

1. `arp_spoofer.py` to get traffic flowing through your machine.
2. `DNS_POISION.py` and/or `RST_PKTS.py` on top of that.

## Requirements

- Python 3.10+
- [Scapy](https://scapy.net/)
- On Windows: [Npcap](https://npcap.com/) installed
- Administrator / root privileges (the scripts send and sniff raw packets)

```bash
pip install scapy
```

## Finding your interface index

Every script takes `--iface` as a Scapy interface **index** (a number). To list the interfaces and their index numbers:

```bash
python -c "from scapy.all import show_interfaces; show_interfaces()"
```

Take the number from the index column for the interface you want to use.

## Scripts

### arp_spoofer.py

Puts your machine between the victim and the gateway. It sends forged ARP replies that tell the victim "the router is at my MAC" and tell the router "the victim is at my MAC", so traffic in both directions passes through you. Your own MAC is read automatically from the chosen interface.

<details>
<summary>Arguments and example</summary>

| Flag | Meaning |
|------|---------|
| `--victim-ip` | IP of the target host |
| `--victim-mac` | MAC of the target host |
| `--router-ip` | Gateway IP |
| `--router-mac` | Gateway MAC |
| `--iface` | Interface index (see above) |

```bash
python arp_spoofer.py \
  --victim-ip 192.168.1.50 \
  --victim-mac AA:BB:CC:DD:EE:FF \
  --router-ip 192.168.1.1 \
  --router-mac 11:22:33:44:55:66 \
  --iface 15
```

Runs in a loop, refreshing the poisoned entries until you stop it with Ctrl+C.
</details>

### DNS_POISION.py

Needs an active MITM position (run `arp_spoofer.py` first). It watches the victim's DNS queries, and when it sees a query for the domain you chose going to one of the legitimate resolvers, it sends back a forged A record that points the domain to an IP you control.

<details>
<summary>Arguments and example</summary>

| Flag | Meaning |
|------|---------|
| `--victim-ip` | IP of the target host |
| `--iface` | Interface index |
| `--conf-domain` | The domain to hijack (for example `example.com.`) |
| `--dns-ip` | One or more legitimate DNS server IPs to watch for |
| `--fake-server` | The IP the forged DNS answer returns (the server impersonating the real one) |

```bash
python DNS_POISION.py \
  --victim-ip 192.168.1.50 \
  --iface 15 \
  --conf-domain example.com. \
  --dns-ip 192.168.1.1 8.8.8.8 \
  --fake-server 192.168.1.80
```

`--dns-ip` accepts several values separated by spaces.
</details>

### RST_PKTS.py

Watches TCP traffic from the victim to a list of target IPs and injects TCP RST packets to tear those connections down. Useful in the lab for forcing the victim to drop existing sessions so a fresh connection (and a fresh DNS lookup) happens.

<details>
<summary>Arguments and example</summary>

| Flag | Meaning |
|------|---------|
| `--victim-ip` | IP of the target host |
| `--iface` | Interface index |
| `--target-ips` | One or more IPs whose connections should be reset |

```bash
python RST_PKTS.py \
  --victim-ip 192.168.1.50 \
  --iface 15 \
  --target-ips 93.184.216.34 1.2.3.4
```

`--target-ips` accepts several values separated by spaces.
</details>

### mac_fixer.py

A small helper. Takes a MAC address in almost any format (dashes, dots, no separators, upper or lower case) and prints it back in the standard colon format that Scapy expects.

<details>
<summary>Usage</summary>

```bash
python mac_fixer.py AA-BB-CC-DD-EE-FF
# -> aa:bb:cc:dd:ee:ff
```

If you run it with no argument it will ask you to type the address.
</details>

## Disclaimer

This project is for education and for authorized testing only. Run it in a lab you control, or against systems you have explicit written permission to test. Attacking networks or devices without authorization is illegal in most jurisdictions. The author is not responsible for any misuse or damage caused by this code.
