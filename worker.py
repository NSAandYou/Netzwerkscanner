import tkinter as tk

import pyshark

import smart_classifier
from structure import *


class Worker(tk.Tk):
    REFRESH_LOOP_TIME = 1000

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

        self.displayed_devices = []

        self.start_refresh_loop(Worker.REFRESH_LOOP_TIME)

    def refresh(self):
        """
        Refreshes window/goes throw event_queue

        Call only with root.after!
        """

        for index, device in enumerate(list(self.network_structure.devices.values())):
            index += 1
            if index >= len(self.displayed_devices):
                self.add_displayed_device(device)

            if self.displayed_devices[index][2]['text'] != device.ip_addr:
                self.displayed_devices[index][2].config(text=device.ip_addr)
            if self.displayed_devices[index][3]['text'] != device.pkt_send:
                self.displayed_devices[index][3].config(text=device.pkt_send)
            if self.displayed_devices[index][4]['text'] != device.get_os_cpe_passive():
                self.displayed_devices[index][4].config(text=device.get_os_cpe_passive())
            if self.displayed_devices[index][5]['text'] != f"{int(device.get_os_cpe_passive_accuracy()*100)}%":
                self.displayed_devices[index][5].config(text=f"{int(device.get_os_cpe_passive_accuracy()*100)}%")
            if self.displayed_devices[index][7]['text'] != device.get_os_cpe_active():
                self.displayed_devices[index][7].config(text=device.get_os_cpe_active())

        self.after(Worker.REFRESH_LOOP_TIME, self.refresh)

    def start_refresh_loop(self, time):
        self.after(time, self.refresh)

    def add_displayed_device(self, device):
        row = len(self.displayed_devices)

        display_device = [
            row,
            tk.Label(self, text=device.get_mac_addr()),
            tk.Label(self, text=device.ip_addr),
            tk.Label(self, text=device.pkt_send),
            tk.Label(self, text=device.get_os_cpe_passive),
            tk.Label(self, text=device.get_os_cpe_passive_accuracy()),
            tk.Button(self, text="Scan", command=device.scan_on_thread),
            tk.Label(self, text=device.get_os_cpe_active()),
        ]

        display_device[1].grid(row=row, column=0)
        display_device[2].grid(row=row, column=1)
        display_device[3].grid(row=row, column=2)
        display_device[4].grid(row=row, column=3)
        display_device[5].grid(row=row, column=4)
        display_device[6].grid(row=row, column=5)
        display_device[7].grid(row=row, column=6)

        self.displayed_devices.append(display_device)

    def open(self):
        # opens window

        display_device = [
            0,
            tk.Label(self, text='MAC-Address'),
            tk.Label(self, text='IP-Address'),
            tk.Label(self, text='Packets'),
            tk.Label(self, text='OS CPE Passive'),
            tk.Label(self, text='Sicherheit'),
            tk.Label(self, text='Scan device'),
            tk.Label(self, text='OS CPE Active'),
        ]

        display_device[1].grid(row=0, column=0)
        display_device[2].grid(row=0, column=1)
        display_device[3].grid(row=0, column=2)
        display_device[4].grid(row=0, column=3)
        display_device[5].grid(row=0, column=4)
        display_device[6].grid(row=0, column=5)
        display_device[7].grid(row=0, column=6)

        self.displayed_devices.append(display_device)

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
