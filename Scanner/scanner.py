#!/usr/bin/env python3

import scapy.all as scapy
from optparse import OptionParser
from mac_vendor_lookup import MacLookup
from Database.DB_Data import add_unapproved

def is_randomized_mac(mac):
    first_byte = int(mac.split(":")[0], 16)
    return bool(first_byte & 0b00000010)

class NetworkScanner:
    def __init__(self, target):
        self.target = target
        self.lookup = MacLookup()
        try:
            self.lookup.load_vendors()
        except Exception:
            self.lookup.update_vendors()

    def get_vendor(self, mac):
        try:
            return self.lookup.lookup(mac)
        except Exception:
            return "Unknown"

    def scan_arp(self):
        arp = scapy.ARP(pdst=self.target)
        ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        answered = scapy.srp(ether / arp, timeout=1, verbose=False)[0]

        results = []
        for _, r in answered:
            mac = r.hwsrc
            results.append({
                "IP": r.psrc,
                "MAC": mac,
                "VENDOR": self.get_vendor(mac),
                "RANDOMIZED": is_randomized_mac(mac)
            })
        return results

    def display_result(self, results):
        print("_" * 100)
        print("IP\t\t\tMAC Address\t\tVendor\t\tRandomized")
        print("-" * 100)
        for r in results:
            print(f"{r['IP']}\t\t{r['MAC']}\t{r['VENDOR']}\t{r['RANDOMIZED']}")
        print("-" * 100)

    def send_to_db(self, results):
        for r in results:
            add_unapproved(
                r["IP"],
                r["MAC"],
                r["VENDOR"],
                r["RANDOMIZED"]
            )

def main():
    parser = OptionParser()
    parser.add_option("-t", "--target", dest="target")
    (options, _) = parser.parse_args()

    if not options.target:
        parser.error("Specify target IP range")

    scanner = NetworkScanner(options.target)
    res = scanner.scan_arp()
    scanner.display_result(res)
    scanner.send_to_db(res)

if __name__ == "__main__":
    main()
