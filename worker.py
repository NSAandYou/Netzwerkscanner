import multiprocessing
import threading

import pyshark

from analyse import PassiveAnalyser
from gui import Window


class Worker:
    def __init__(self, network_interface):
        self.window = Window(self)

        self.network_interface = network_interface
        self.passive_scanner = pyshark.LiveCapture(interface=network_interface)
        self.passive_analyser = PassiveAnalyser(self.window.print)
        self.passive_working_state = False

    def start(self):
        ##self.start_passive()
        self.run_gui()
        self.stop()

    def run_gui(self):
        self.window.open()

    def stop(self):
        self.stop_passive()

    def start_passive(self):
        self.passive_working_state = True
        threading.Thread(target=self.passive_worker).start()

    def stop_passive(self):
        self.passive_working_state = False

    def passive_worker(self):
        for packet in self.passive_scanner.sniff_continuously():
            if not self.passive_working_state:
                break
            self.passive_analyser.analyse_package(packet)
