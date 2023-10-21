import tkinter as tk


class Window:

    def __init__(self, callback_closed):
        self.root = tk.Tk()
        self.root.title('Projektseminar')
        self.output = tk.Text()
        self.setup_layout()
        ##self.root.protocol("WM_DELETE_WINDOW", callback_closed)

    def setup_layout(self):
        self.output = tk.Text(
            self.root,
            height=12,
            width=40
        )
        self.output.pack(expand=True)
        self.output.config(state='disabled')

    def print(self, string):
        print(string)
        ##self.output.insert(tk.END, string)

    def open(self):
        self.root.mainloop()

    def close(self):
        self.root.destroy()