import tkinter as tk
from tkinter import ttk

class App():
    def __init__(self) -> None:

        # states
        self._T = 0.0
        self._isOn = False

        # calendar

        # tkinter related
        self._root = tk.Tk()
        self._root.title("Sr-oven")
        self._root.geometry("600x400")

        self._root.columnconfigure(index=0, weight=1)
        self._root.columnconfigure(index=1, weight=3)

        grid_w, grid_h = self._root.grid_size()

        # temperature monitoring
        self.frame_monitor = ttk.LabelFrame(self._root, text="Monitor", width=380, height=100)
        self.frame_monitor.grid(column=0, row=0, columnspan=2)

        # field to input new temperature for the oven
        self.lbl_new_temp = ttk.Label(self._root, text="Temperature:")
        self.lbl_new_temp.grid(column=0, row=1)

        self.entry_new_temp = ttk.Entry(self._root, width=30)
        self.entry_new_temp.grid(column=1, row=1, sticky=tk.W, )

        self.btn_set_new_temp = ttk.Button(self._root, text="Set")
        self.btn_set_new_temp.grid(column=1, row=1, padx=20)

        # bottom right buttons
        self.btn_se_frame = ttk.Frame(self._root)
        self.btn_se_frame.grid(column=grid_h, row=grid_w, sticky=tk.SE)

        self.btn_start = ttk.Button(self.btn_se_frame, text="Start")
        self.btn_start.pack(side=tk.LEFT)

        self.btn_stop = ttk.Button(self.btn_se_frame, text="Stop")
        self.btn_stop.pack(side=tk.LEFT)

        self.btn_schedule = ttk.Button(self.btn_se_frame, text="Schedule")
        self.btn_schedule.pack(side=tk.LEFT)
    

    # accessors
    @property
    def T(self):
        return self._T
    @T.setter
    def T(self, t):
        self._T = t

    @property
    def isOn(self):
        return self._isOn
    @isOn.setter
    def isOn(self, b):
        self._isOn = b

    # methods
    def run(self) -> None:
        self._root.mainloop() 



if __name__ == "__main__":
    app = App()
    app.run()

