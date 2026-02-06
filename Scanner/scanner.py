#!/usr/bin/env python3

import scapy.all as scapy
from optparse import OptionParser
from mac_vendor_lookup import MacLookup
from Database.DB_Data import add_unapproved
from mailalarm import send_unapproved_mail


def is_randomized_mac(mac: str) -> bool:
    # Locally administered MAC (U/L bit = 1)
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

    def get_vendor(self, mac: str) -> str:
        if is_randomized_mac(mac):
            return "Random"

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
            })
        return results

    def display_result(self, results):
        print("_" * 80)
        print("IP\t\t\tMAC Address\t\tVendor")
        print("-" * 80)
        for r in results:
            print(f"{r['IP']}\t\t{r['MAC']}\t{r['VENDOR']}")
        print("-" * 80)

    def send_to_db(self, results):
        for r in results:
            add_unapproved(
                mac_address=r["MAC"],
                ip_address=r["IP"],
                vendor=r["VENDOR"],
            )
        send_unapproved_mail()

def run_scan(target: str) -> None:
    scanner = NetworkScanner(target)
    res = scanner.scan_arp()
    scanner.display_result(res)
    scanner.send_to_db(res)

def main(argv=None):
    parser = OptionParser()
    parser.add_option("-t", "--target", dest="target")
    (options, _) = parser.parse_args(args=argv)

    if not options.target:
        parser.error("Specify target IP range")

    run_scan(options.target)


if __name__ == "__main__":
    main()
