import tkinter as tk
from tkinter import ttk

class App():
    def __init__(self) -> None:

        # states
        self._T = 0.0
        self._isOn = False

        # tkinter init
        self._root = tk.Tk()
        self.gui()
        

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

    # gui methods
    def schedule(self) -> None:
        window_schedule = tk.Toplevel(self._root)
        window_schedule.title("Scheduler")
        window_schedule.geometry("200x600")

        days_frame = tk.LabelFrame(window_schedule, text="Days", width=180, height=300)
        days_frame.pack()

        hours_frame = tk.LabelFrame(window_schedule, text="Hours", width=180, height=200, pady=10)
        hours_frame.pack()


    def gui(self) -> None:
        self._root.title("Sr-oven")
        self._root.geometry("600x200")
        self._root.resizable(True, False)

        self._root.columnconfigure(index=0, weight=1)
        self._root.columnconfigure(index=1, weight=3)

        grid_w, grid_h = self._root.grid_size()

        # temperature monitoring
        frame_monitor = ttk.LabelFrame(self._root, text="Monitor", width=580, height=100)
        frame_monitor.grid(column=0, row=0, columnspan=2)

        # field to input new temperature for the oven
        lbl_new_temp = ttk.Label(self._root, text="Temperature:")
        lbl_new_temp.grid(column=0, row=1)

        frame_temp = ttk.Frame(self._root)
        frame_temp.grid(column=1, row=1, sticky=tk.W, pady=5)

        entry_new_temp = ttk.Entry(frame_temp, width=30)
        entry_new_temp.pack(side=tk.LEFT, padx=5)

        btn_set_new_temp = ttk.Button(frame_temp, text="Set T°")
        btn_set_new_temp.pack(side=tk.LEFT)

        # bottom right buttons
        btn_se_frame = ttk.Frame(self._root)
        btn_se_frame.grid(column=1, row=grid_w, sticky=tk.SE, pady=30)

        btn_start = ttk.Button(btn_se_frame, text="Start")
        btn_start.pack(side=tk.LEFT, padx=3)

        btn_stop = ttk.Button(btn_se_frame, text="Stop")
        btn_stop.pack(side=tk.LEFT, padx=5)

        btn_schedule = ttk.Button(btn_se_frame, text="Schedule", command=self.schedule)
        btn_schedule.pack(side=tk.LEFT, padx=5)
    
    # other methods
    def run(self) -> None:
        self._root.mainloop()



if __name__ == "__main__":
    app = App()
    app.run()

