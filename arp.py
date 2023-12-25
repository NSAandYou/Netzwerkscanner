import scapy.all as scapy


def request_mac_by_ip(ip: str):
    answered, unanswered = scapy.srp(scapy.Ether(dst='ff:ff:ff:ff:ff:ff') / scapy.ARP(pdst=ip), timeout=1)
    for i in answered:
        return i[1].hwsrc
    return None

def scan_ip_range(ip: str, network_mask: int):
    returnValue = {'ip': [], 'mac': []}
    if network_mask == 24:
        network_ip = ".".join(ip.split(".")[0:3])
        for i in range(100, 110):
            scan_ip = f"{network_ip}.{str(i)}"
            print(scan_ip)
            scan_result = request_mac_by_ip(scan_ip)
            if scan_result is not None:
                print("Ergebnis", scan_ip, scan_result)
                returnValue['ip'].append(scan_ip)
                returnValue['mac'].append(scan_result)
    return returnValue

def process_arp_pkt():
    pass