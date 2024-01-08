import tkinter as tk

import pyshark

import smart_classifier
from structure import *


class Worker(tk.Tk):
    REFRESH_LOOP_TIME = 5000

    def __init__(self, network_interface, clf_file_path):
        super().__init__()
        self.title('Projektseminar')

        self.network_interface = network_interface
        self.network_structure = Structure()

        smart_classifier.__init__(clf_file_path)

        self.passive_scanner = pyshark.LiveCapture(interface=network_interface, include_raw=True, use_json=True)
        self.passive_thread_working_state = False

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)

        self.start_refresh_loop(Worker.REFRESH_LOOP_TIME)

    def refresh(self):
        """
        Refreshes window/goes throw event_queue

        Call only with root.after!
        """

        for child in self.winfo_children():
            child.destroy()

        tk.Label(self, text='MAC-Address').grid(row=0, column=0)
        tk.Label(self, text='IP-Address').grid(row=0, column=1)
        tk.Label(self, text='Packets').grid(row=0, column=2)
        tk.Label(self, text='OS CPE Passive').grid(row=0, column=3)
        tk.Label(self, text='Sicherheit').grid(row=0, column=4)
        tk.Label(self, text='Scan device').grid(row=0, column=5)
        tk.Label(self, text='OS CPE Active').grid(row=0, column=6)

        row = 1
        for device in self.network_structure.devices.values():
            tk.Label(self, text=device.get_mac_addr()).grid(row=row, column=0)
            tk.Label(self, text=device.ip_addr).grid(row=row, column=1)
            tk.Label(self, text=device.pkt_send).grid(row=row, column=2)
            tk.Label(self, text=device.get_os_cpe_passive()).grid(row=row, column=3)
            tk.Label(self, text=f"{int(device.get_os_cpe_passive_accuracy()*100)}%").grid(row=row, column=4)
            tk.Button(self, text="Scan", command=device.scan_on_thread).grid(row=row, column=5)
            tk.Label(self, text=device.get_os_cpe_active()).grid(row=row, column=6)
            row += 1

        self.after(Worker.REFRESH_LOOP_TIME, self.refresh)

    def start_refresh_loop(self, time):
        self.after(time, self.refresh)

    def open(self):
        # opens window

        self.mainloop()

    def close(self):
        # closes window

        self.destroy()

    def start(self):
        # Starts the GUI, Background processes and program in general

        self.start_passive_thread()
        self.open()
        self.stop()

    def stop(self):
        # stops background processes and program

        self.stop_passive_thread()

    def start_passive_thread(self):
        # starts passive scan in new thread

        self.passive_thread_working_state = True
        threading.Thread(target=self.passive_worker).start()

    def stop_passive_thread(self):
        # stops passive scan thread (sets flag so shutdown takes time)

        self.passive_thread_working_state = False

    def passive_worker(self):
        # function for passive scan loop

        for pkt in self.passive_scanner.sniff_continuously():
            if not self.passive_thread_working_state:
                break
            self.network_structure.analyse_pkt(pkt)
