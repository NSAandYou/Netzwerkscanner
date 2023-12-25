import threading

import nmap


class Device:
    def __init__(self, mac_addr):
        self._mac_addr: str = mac_addr.lower()
        self.ip_addr: str = "UNKNOWN"
        self.pkg_recv: int = 0
        self.pkg_send: int = 0
        self.os_cpe: str = "SCAN MISSING"

    def get_mac_addr(self) -> str:
        return self._mac_addr

    def set_check_ip(self, ip: str):
        if self.ip_addr != ip:
            if self.ip_addr != "UNKNOWN":
                pass
                ##print(f"WARNING: Device({self._mac_addr}) now sends with ip {ip} instead of {self.ip_addr}(old): Could "
                ##      "be ARP problem")   TODO
            self.ip_addr = str(ip)

    def increase_pkg_recv(self):
        self.pkg_recv += 1

    def increase_pkg_send(self):
        self.pkg_send += 1

    def get_pkg_processed(self) -> int:
        return self.pkg_send + self.pkg_recv

    def scan(self):
        nm = nmap.PortScanner()
        if self.ip_addr != "UNKNOWN" and self._mac_addr != "ff:ff:ff:ff:ff:ff":
            print(f"INFO: Start Scan for {self.ip_addr}({self._mac_addr})")
            scan = nm.scan(self.ip_addr, arguments='-O')
            ip = list(scan['scan'].keys())[0]
            self.os_cpe = "UNKNOWN"
            if len((scan['scan'][ip]['osmatch'])) > 0:
                if 'cpe' in scan['scan'][ip]['osmatch'][0]['osclass'][0]:
                    self.os_cpe = scan['scan'][ip]['osmatch'][0]['osclass'][0]['cpe'][0]
            print(f"INFO: Stop Scan for {self.ip_addr}({self._mac_addr})")

    def scan_on_thread(self):
        threading.Thread(target=self.scan).start()

    def get_os_cpe(self):
        return self.os_cpe

    def tostring(self):
        return '{0:<20} {1:<5} {2:<5} {3}'.format(self.get_mac_addr(), self.pkg_send, self.pkg_recv,
                                                  self.get_pkg_processed())


class Structure:
    def __init__(self):
        self.devices = {}

    def analyse_pkg(self, pkg):
        if hasattr(pkg, 'eth'):
            if hasattr(pkg.eth, 'dst') and hasattr(pkg.eth, 'src'):
                dst_addr = pkg.eth.dst
                src_addr = pkg.eth.src
            else:
                return
        elif hasattr(pkg, 'wlan'):
            if hasattr(pkg.wlan, 'da') and hasattr(pkg.wlan, 'sa'):
                dst_addr = pkg.wlan.da
                src_addr = pkg.wlan.sa
            else:
                return
        else:
            return

        new_devices = []

        if hasattr(pkg, 'wlan') or hasattr(pkg, 'eth'):
            if dst_addr in self.devices:
                self.devices.get(dst_addr).increase_pkg_recv()
            else:
                self.devices[dst_addr] = Device(dst_addr)
                self.devices.get(dst_addr).increase_pkg_recv()
                new_devices.append(dst_addr)

            if src_addr in self.devices:
                self.devices.get(src_addr).increase_pkg_send()
            else:
                self.devices[src_addr] = Device(src_addr)
                self.devices.get(src_addr).increase_pkg_send()
                new_devices.append(src_addr)

        if hasattr(pkg, 'arp'):
            if pkg.arp.opcode == '1':
                self.devices.get(pkg.arp.src_hw_mac).set_check_ip(pkg.arp.src_proto_ipv4)
            elif pkg.arp.opcode == '2':
                self.devices.get(pkg.arp.src_hw_mac).set_check_ip(pkg.arp.src_proto_ipv4)
                self.devices.get(pkg.arp.dst_hw_mac).set_check_ip(pkg.arp.dst_proto_ipv4)
            else:
                return
        if hasattr(pkg, 'ip'):
            self.devices.get(dst_addr).set_check_ip(pkg.ip.addr)

        for device in new_devices:
            self.devices.get(device).scan_on_thread()

    def get_device_by_mac(self, mac_addr: str) -> Device:
        return self.devices.get(mac_addr)