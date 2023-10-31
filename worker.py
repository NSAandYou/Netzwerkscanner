import threading

import pyshark

from analyse import PassiveAnalyser
from analyse.network import Structure
from gui import MainWindow


class Worker:
    def __init__(self, network_interface):
        self.window = MainWindow(self)

        self.network_interface = network_interface
        self.network_structure = Structure()

        self.passive_scanner = pyshark.LiveCapture(interface=network_interface) ##TODO UnknownInterfaceException
        self.passive_analyser = PassiveAnalyser(self.network_structure, self.window.passive_print, self.window.structure_print)
        self.passive_working_state = False

    def start(self):
        # Starts the GUI, Background processes and program in general

        self.run_gui()
        self.stop()

    def run_gui(self):
        # Opens GUI

        self.window.open()

    def stop(self):
        # stops background processes and program

        self.stop_passive()

    def start_passive(self):
        # starts passive scan in new thread

        self.passive_working_state = True
        threading.Thread(target=self.passive_worker).start()

    def stop_passive(self):
        # stops passive scan thread (sets flag so shutdown takes time)

        self.passive_working_state = False

    def passive_worker(self):
        # function for passive scan loop

        for packet in self.passive_scanner.sniff_continuously():
            if not self.passive_working_state:
                break
            self.passive_analyser.analyse_package(packet)
