import multiprocessing
import queue
import threading
import time
import tkinter as tk


class Window:

    def __init__(self, worker):
        self.worker = worker

        self.root = tk.Tk()
        self.root.title('Projektseminar')
        self.passive_output = tk.Text()
        self.passive_power_button = tk.Button()

        self.setup_layout()
        self.event_queue = queue.Queue(maxsize=100)
        ##self.root.protocol("WM_DELETE_WINDOW", callback_closed)

    def setup_layout(self):
        self.passive_output = tk.Text(
            self.root,
            height=24,
            width=80
        )
        self.passive_output.pack(expand=True)
        self.passive_output.config(state='disabled')

        self.passive_power_button = tk.Button(text="Start passive Scan", command=self.passive_power_button_pressed)
        self.passive_power_button.pack()

    def passive_power_button_pressed(self):
        if self.worker.passive_working_state:
            self.worker.stop_passive()
            self.passive_power_button.config(text="Start passive Scan")
        else:
            self.worker.start_passive()
            self.passive_power_button.config(text="Stop passive Scan")

    def refresh(self):
        while self.event_queue.qsize() > 0:
            key, data = self.event_queue.get()
            if key == "PRINT_OUTPUT_PASSIVE_DEBUG":
                self.passive_output.config(state='normal')
                self.passive_output.insert(tk.END, data)
                self.passive_output.config(state='disabled')
                self.passive_output.see(tk.END)

    def print(self, string):
        self.event_queue.put(("PRINT_OUTPUT_PASSIVE_DEBUG", string))
        self.root.after(0, self.refresh)

    def open(self):
        self.root.mainloop()

    def close(self):
        self.root.destroy()
