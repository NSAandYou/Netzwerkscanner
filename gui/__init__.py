import queue
import tkinter as tk


class MainWindow(tk.Tk):

    def __init__(self, worker):
        super().__init__()
        self.title('Projektseminar')

        self.worker = worker
        self.event_queue = queue.Queue(maxsize=100)
        self.passive_output = None
        self.window_structure = Structure(self)
        self.passive_power_button = None

        self.setup_layout()

    def setup_layout(self):
        # prepares window layout

        self.passive_output = tk.Text(
            self,
            height=24,
            width=80
        )
        self.passive_output.pack(expand=True)
        self.passive_output.config(state='disabled')

        self.passive_power_button = tk.Button(text="Start passive Scan", command=self.passive_power_button_pressed)
        self.passive_power_button.pack()

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
                self.passive_output.config(state='normal')
                self.passive_output.insert(tk.END, data)
                self.passive_output.config(state='disabled')
                self.passive_output.see(tk.END)
            elif key == "PRINT_OUTPUT_STRUCTURE":
                self.window_structure.set(data)

    def passive_print(self, string):
        # prints to passive_output

        self.event_queue.put(("PRINT_OUTPUT_PASSIVE", string))
        self.after(0, self.refresh)

    def structure_print(self, string):
        # prints to passive_output

        self.event_queue.put(("PRINT_OUTPUT_STRUCTURE", string))
        self.after(0, self.refresh)

    def open(self):
        # opens window

        self.mainloop()

    def close(self):
        # closes window

        self.destroy()


class Structure(tk.Toplevel):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.title('Network Structure')

        self.passive_structure = tk.Text(
            self,
            height=24,
            width=60
        )
        self.passive_structure.pack(expand=True)
        self.passive_structure.config(state='disabled')

    def set(self, string):
        self.passive_structure.config(state='normal')
        self.passive_structure.delete(1.0, tk.END)
        self.passive_structure.insert(1.0, string)
        self.passive_structure.config(state='disabled')
        self.passive_structure.see(tk.END)
