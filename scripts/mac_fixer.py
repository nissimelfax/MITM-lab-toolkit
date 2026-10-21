import re
import sys


def normalize_mac(mac_input):
    clean_mac = re.sub(r'[^0-9a-fA-F]', '', mac_input).lower()

    if len(clean_mac) != 12:
        raise ValueError("MAC address is not legal")
    formatted_mac = ':'.join(clean_mac[i:i + 2] for i in range(0, 12, 2))
    return formatted_mac

if __name__ == "__main__":
    #address can be given in argument or input by user
    if len(sys.argv) > 1:
        raw_mac = sys.argv[1]
    else:
        raw_mac = input("Enter MAC address: ")

    try:
        fixed_mac = normalize_mac(raw_mac)
        print(fixed_mac)
    except ValueError as e:
        print(f"Error: {e}")