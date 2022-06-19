import json, threading as thread
import requests as re

import tkinter as tk
from tkinter import ttk

HOST = "localhost"
PORT = 8488
URL = f"http://{HOST}:{PORT}/"

class App():
    def __init__(self) -> None:
        self._root = tk.Tk()

        # init connection by retrieving the config file of the oven
        try:
            self.oven_config = json.loads(re.get(URL).text)
        except re.exceptions.RequestException as err:
            self.error(err)
            
        # main window
        self.gui()
        

    # gui methods
    def error(self, err) -> None:
        window_error = tk.Toplevel(self._root)
        window_error.title("An error has occured")

        lbl_error = tk.Label(window_error, text="Error: {}".format(err))
        lbl_error.pack()

        btn_quit = ttk.Button(window_error, text="Quit SrOven", command=self._root.destroy)
        btn_quit.pack()

    def schedule(self) -> None:
        # init a new window
        window_schedule = tk.Toplevel(self._root)
        window_schedule.title("Scheduler")
        window_schedule.geometry("380x190")

        window_schedule.columnconfigure(index=0, weight=1)
        window_schedule.columnconfigure(index=1, weight=1)

        # days' dedicated frame
        days_frame = tk.LabelFrame(window_schedule, text="Days", width=180, height=300)
        days_frame.grid(column=0, row=0, sticky=tk.N)

        days_frame.columnconfigure(index=0, weight=1)
        days_frame.columnconfigure(index=1, weight=2)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # days' checkboxes
        for i in range(7):
            tk.Checkbutton(days_frame, command=lambda: print("to implement")).grid(column=0, row=i)
            tk.Label(days_frame, text=days[i]).grid(column=1, row=i, sticky=tk.W)

        right_frame = tk.Frame(window_schedule)
        right_frame.grid(column=1, row=0, sticky=tk.N)
        
        right_frame.columnconfigure(index=0, weight=1)

        # hours' dedicated frame
        hours_frame = tk.LabelFrame(right_frame, text="Hours", width=180, height=200, pady=10)
        hours_frame.grid(column=0, row=0, sticky=tk.NE)
        
        hours_frame.columnconfigure(index=0, weight=1)
        hours_frame.columnconfigure(index=1, weight=1)

        lbl_start = ttk.Label(hours_frame, text="Start:")
        lbl_start.grid(column=0, row=0)

        entry_start = ttk.Entry(hours_frame)
        entry_start.grid(column=1, row=0)

        lbl_stop = ttk.Label(hours_frame, text="Stop:")
        lbl_stop.grid(column=0, row=1)

        entry_stop = ttk.Entry(hours_frame)
        entry_stop.grid(column=1, row=1)

        # save button
        btn_save = ttk.Button(right_frame, text="Save")
        btn_save.grid(column=0, row=1, sticky=tk.SE, pady=60)
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

        btn_start = ttk.Button(btn_se_frame, text="Start", command=self.start_oven)
        btn_start.pack(side=tk.LEFT, padx=3)

        btn_stop = ttk.Button(btn_se_frame, text="Stop", command=self.stop_oven)
        btn_stop.pack(side=tk.LEFT, padx=5)

        btn_schedule = ttk.Button(btn_se_frame, text="Schedule", command=self.schedule)
        btn_schedule.pack(side=tk.LEFT, padx=5)
    
    # other methods
    def start_oven(self) -> None:
        re.post(URL+'status/true')
    def stop_oven(self) -> None:
        re.post(URL+'status/false')

    def run(self) -> None:
        self._root.mainloop()



if __name__ == "__main__":
    app = App()
    app.run()

