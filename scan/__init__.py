import pyshark


class Capture:
    def __init__(self, network_interface, callback_function):
        self.live_capture = pyshark.LiveCapture(interface=network_interface)
        self.live_capture.apply_on_packets(callback_function)
