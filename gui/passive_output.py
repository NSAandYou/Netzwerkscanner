import tkinter as tk


class PassiveOutput(tk.Toplevel):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.toplevel = main_window
        self.title('Passive Scan Output')

        self.passive_output: tk.Text = tk.Text(
            self,
            height=24,
            width=80
        )
        self.passive_output.pack(expand=True)
        self.passive_output.config(state='disabled')

    def insert(self, string):
        self.passive_output.config(state='normal')
        self.passive_output.insert(tk.END, string)
        self.passive_output.config(state='disabled')
        self.passive_output.see(tk.END)
