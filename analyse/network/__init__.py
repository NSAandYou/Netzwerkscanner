class Device:
    def __init__(self, mac_addr):
        self._mac_addr: str = mac_addr.lower()
        self.pkg_recv: int = 0
        self.pkg_send: int = 0

    def get_mac_addr(self) -> str:
        return self._mac_addr

    def increase_pkg_recv(self):
        self.pkg_recv += 1

    def increase_pkg_send(self):
        self.pkg_send += 1

    def get_pkg_processed(self) -> int:
        return self.pkg_send + self.pkg_recv

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

        if dst_addr in self.devices:
            self.devices.get(dst_addr).increase_pkg_recv()
        else:
            self.devices[dst_addr] = Device(dst_addr)
            self.devices.get(dst_addr).increase_pkg_recv()

        if src_addr in self.devices:
            self.devices.get(src_addr).increase_pkg_send()
        else:
            self.devices[src_addr] = Device(src_addr)
            self.devices.get(src_addr).increase_pkg_send()

    def tostring(self):
        return ('MAC-Address          Send  Recv  Sum\n' +
                '\n'.join(device.tostring() for device in self.devices.values()))
