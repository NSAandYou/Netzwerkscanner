import tkinter as tk


class NetworkStructure(tk.Toplevel):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.toplevel = main_window
        self.title('Network Structure')

        self.passive_structure = tk.Text(
            self,
            height=24,
            width=60
        )
        self.passive_structure.insert(1.0, main_window.worker.network_structure.tostring())
        self.passive_structure.pack(expand=True)
        self.passive_structure.config(state='disabled')

    def set(self, string):
        self.passive_structure.config(state='normal')
        self.passive_structure.delete(1.0, tk.END)
        self.passive_structure.insert(1.0, string)
        self.passive_structure.config(state='disabled')
