import threading

import nmap

import smart_classifier
import webbrowser

CVE_SEARCH_LIST = ("https://nvd.nist.gov/vuln/search/results?form_type=Advanced&results_type=overview&isCpeNameSearch"
                   "=true&seach_type=all&query=")


class Device:
    def __init__(self, mac_addr):
        self._mac_addr: str = mac_addr.lower()
        self.ip_addr: str = "UNKNOWN"
        self.pkt_send: int = 0
        self.os_cpe_active: str = "SCAN MISSING"
        self.os_cpe_list_passive: [] = []

    def get_mac_addr(self) -> str:
        return self._mac_addr

    def set_ip(self, ip: str):
        if self.ip_addr != ip:
            if self.ip_addr != "UNKNOWN":
                print(f"WARNING: Device({self._mac_addr}) now sends with ip {ip} instead of {self.ip_addr}(old): Could "
                      "be ARP problem")
            self.ip_addr = str(ip)

    def increase_pkt_send(self):
        self.pkt_send += 1

    def scan(self):
        # noinspection PyBroadException
        try:
            nm = nmap.PortScanner()
            print(f"INFO: Start Scan for {self.ip_addr}({self._mac_addr})")
            scan = nm.scan(self.ip_addr, arguments='-O')
            ip = list(scan['scan'].keys())[0]
            self.os_cpe_active = "UNKNOWN"
            if len((scan['scan'][ip]['osmatch'])) > 0:
                if 'cpe' in scan['scan'][ip]['osmatch'][0]['osclass'][0]:
                    self.os_cpe_active = scan['scan'][ip]['osmatch'][0]['osclass'][0]['cpe'][0]
            print(f"INFO: Stop Scan for {self.ip_addr}({self._mac_addr})")
        except nmap.nmap.PortScannerError:
            self.os_cpe_active = "NO ROOT PRIV"
        except:
            self.os_cpe_active = "ERROR"

    def scan_on_thread(self):
        if self.os_cpe_active != "SCANNING" and self.ip_addr != "UNKNOWN" and self._mac_addr != "ff:ff:ff:ff:ff:ff":
            self.os_cpe_active = "SCANNING"
            threading.Thread(target=self.scan).start()

    def view_cve(self):
        if "cpe" in self.get_os_cpe_active():
            webbrowser.open(CVE_SEARCH_LIST + self.get_os_cpe_active())
        else:
            webbrowser.open(CVE_SEARCH_LIST + self.get_os_cpe_passive())

    def get_os_cpe_active(self):
        return self.os_cpe_active

    def get_os_cpe_passive(self):
        return max(self.os_cpe_list_passive, key=self.os_cpe_list_passive.count)

    def get_os_cpe_passive_confidence(self):
        confidence = self.os_cpe_list_passive.count(self.get_os_cpe_passive()) / len(self.os_cpe_list_passive)
        if confidence < 0.5 and self.os_cpe_active == "SCAN MISSING":
            self.scan_on_thread()
        return confidence

    def smart_analyse(self, pkt):
        self.os_cpe_list_passive.append(smart_classifier.predict(pkt))
        if len(self.os_cpe_list_passive) > 20:
            self.os_cpe_list_passive.pop(0)


class Structure:
    def __init__(self):
        self.devices = {}

    def analyse_pkt(self, pkt):
        if hasattr(pkt, 'eth'):
            if hasattr(pkt.eth, 'dst') and hasattr(pkt.eth, 'src'):
                if pkt.eth.src not in self.devices:
                    self.devices[pkt.eth.src] = Device(pkt.eth.src)
                device: Device = self.devices.get(pkt.eth.src)
                device.increase_pkt_send()
                device.smart_analyse(pkt)
        if hasattr(pkt, 'arp'):
            if pkt.arp.opcode == '1':
                self.get_device_by_mac(pkt.arp.src.hw_mac).set_ip(pkt.arp.src.proto_ipv4)
            elif pkt.arp.opcode == '2':
                self.get_device_by_mac(pkt.arp.src.hw_mac).set_ip(pkt.arp.src.proto_ipv4)
                self.get_device_by_mac(pkt.arp.dst.hw_mac).set_ip(pkt.arp.dst.proto_ipv4)

    def get_device_by_mac(self, mac_addr: str) -> Device:
        return self.devices.get(mac_addr)
