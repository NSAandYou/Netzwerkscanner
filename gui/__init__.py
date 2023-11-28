import queue
import tkinter as tk

from gui.network_structure import NetworkStructure
from gui.passive_output import PassiveOutput


class MainWindow(tk.Tk):

    def __init__(self, worker):
        super().__init__()
        self.title('Projektseminar')

        self.worker = worker
        self.event_queue: queue.Queue = queue.Queue(maxsize=100)
        self.passive_output = None
        self.window_network_structure = None
        self.window_passive_output = None

        self.status_text = None
        self.passive_power_button = None
        self.open_window_network_structure_button = None
        self.open_window_passive_output_button = None

        self.setup_layout()

    def setup_layout(self):
        # prepares window layout

        self.status_text = tk.Text(
            self,
            height=18,
            width=40
        )
        self.status_text.pack(expand=True)
        self.status_text.config(state='disabled')
        self.start_loops(1000)

        self.passive_power_button: tk.Button = tk.Button(text="Start passive Scan",
                                                         command=self.passive_power_button_pressed)
        self.passive_power_button.pack()

        self.open_window_network_structure_button: tk.Button = tk.Button(text="Network Structure",
                                                                         command=self.open_window_network_structure)
        self.open_window_network_structure_button.pack()

        self.open_window_passive_output_button: tk.Button = tk.Button(text="Passive Scan Output",
                                                                      command=self.open_window_passive_output)
        self.open_window_passive_output_button.pack()

    def passive_power_button_pressed(self):
        # action when passive scan button is pressed

        if self.worker.passive_working_state:
            self.worker.stop_passive()
            self.passive_power_button.config(text="Start passive Scan")
        else:
            self.worker.start_passive()
            self.passive_power_button.config(text="Stop passive Scan")

    def refresh(self):
        """
        Refreshes window/goes throw event_queue

        Call only with root.after!
        """

        while self.event_queue.qsize() > 0:
            key, data = self.event_queue.get()
            if key == "PRINT_OUTPUT_PASSIVE":
                self.window_passive_output.insert(data)
            elif key == "PRINT_OUTPUT_STRUCTURE":
                self.window_network_structure.set(data)

    def passive_print(self, string):
        # prints to passive_output
        if self.window_passive_output is not None and self.window_passive_output.winfo_exists():
            self.event_queue.put(("PRINT_OUTPUT_PASSIVE", string))
            self.after(0, self.refresh)

    def structure_print(self, string):
        # prints to passive_output
        if self.window_network_structure is not None and self.window_network_structure.winfo_exists():
            self.event_queue.put(("PRINT_OUTPUT_STRUCTURE", string))
            self.after(0, self.refresh)

    def refresh_status_text(self):
        text: str = ''
        if self.worker.passive_working_state:
            text += 'Passive Output: Active'
        else:
            text += 'Passive Output: Inactive'

        self.status_text.config(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(
            1.0,
            text
        )
        self.status_text.config(state='disabled')

    def loop_refresh_status_text(self):
        self.refresh_status_text()
        self.after(1000, self.loop_refresh_status_text)

    def start_loops(self, time):
        self.after(time, self.loop_refresh_status_text)

    def open(self):
        # opens window

        self.mainloop()

    def open_window_passive_output(self):
        if self.window_passive_output is not None and self.window_passive_output.winfo_exists():
            self.window_passive_output.lift()
        else:
            self.window_passive_output = PassiveOutput(self)

    def open_window_network_structure(self):
        if self.window_network_structure is not None and self.window_network_structure.winfo_exists():
            self.window_network_structure.lift()
        else:
            self.window_network_structure = NetworkStructure(self)

    def close(self):
        # closes window

        self.destroy()
