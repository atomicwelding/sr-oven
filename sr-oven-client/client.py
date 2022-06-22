import json, sys
import requests as re
import threading as thread

import tkinter as tk
from tkinter import ttk

def set_interval_as_daemon(interval: float, callback: any) -> thread.Thread:
    """ Mimics "setInterval" in javascript.
    It calls the callback each X secs, X being defined by interval parameter.
    Returns a thread.
    """
    def cb_wrapper():
        set_interval_as_daemon(interval, callback)
        callback()
    t = thread.Timer(interval, cb_wrapper)
    t.daemon = True
    t.start()
    return t

class App():
    def __init__(self) -> None:
        self._root = None
        self.t = None
        self.haserror = False

        self.oven_config = {}
        self.days = {}
        self.monitor_val = {}

        self.start_hour = None
        self.stop_hour = None

        self.url = None
        with open("./client_config.json") as client_config_file:
            client_config = json.load(client_config_file)
            self.url = f"http://{client_config['host']}:{client_config['port']}/"

    
    def error(self, err) -> None:
        """ This method need to be called whenever you have an error and want
        to display it to the user.
        """
        if(self.haserror):
            return
        else:
            self.haserror = True

        window_error = tk.Toplevel(self._root)
        window_error.title("An error has occured")

        lbl_error = tk.Label(window_error, text="Error: {}".format(err))
        lbl_error.pack()

        btn_quit = ttk.Button(window_error, text="Quit SrOven", command=self.on_closing)
        btn_quit.pack()

    def schedule(self) -> None:
        """ This method is responsible for handling the schedule window
        """

        self.init_hours()
        self.init_days()

        # init a new window
        window_schedule = tk.Toplevel(self._root)
        window_schedule.title("Scheduler")
        window_schedule.geometry("380x190")

        window_schedule.columnconfigure(index=0, weight=1)
        window_schedule.columnconfigure(index=1, weight=1)

        # set up frame, grid and utils for days in schedule window
        days_frame = tk.LabelFrame(window_schedule, text="Days", width=180, height=300)
        days_frame.grid(column=0, row=0, sticky=tk.N)

        days_frame.columnconfigure(index=0, weight=1)
        days_frame.columnconfigure(index=1, weight=2)

        # Monday
        tk.Checkbutton(days_frame, variable=self.days["Monday"]).grid(column=0, row=0)
        
        # Tuesday
        tk.Checkbutton(days_frame, variable=self.days["Tuesday"]).grid(column=0, row=1)

        # Wednesday
        tk.Checkbutton(days_frame, variable=self.days["Wednesday"]).grid(column=0, row=2)

        # Thursday
        tk.Checkbutton(days_frame,variable=self.days["Thursday"]).grid(column=0, row=3)

        # Friday
        tk.Checkbutton(days_frame, variable=self.days["Friday"]).grid(column=0, row=4)

        # Saturday
        tk.Checkbutton(days_frame, variable=self.days["Saturday"]).grid(column=0, row=5)

        # Sunday
        tk.Checkbutton(days_frame, variable=self.days["Sunday"]).grid(column=0, row=6)

        # corresponding labels
        # we don't use built-in checkbutton labels because they can't be aligned correctly
        # instead use new labels
        for i in range(7):            
            tk.Label(days_frame, text=list(self.days.keys())[i]).grid(column=1, row=i, sticky=tk.W)

        # right frame is composed of 2 items : a label frame for hours and a save button
        right_frame = tk.Frame(window_schedule)
        right_frame.grid(column=1, row=0, sticky=tk.N)
        
        # build a grid for this frame
        right_frame.columnconfigure(index=0, weight=1)

        # hours label frame
        hours_frame = tk.LabelFrame(right_frame, text="Hours", width=180, height=200, pady=10)
        hours_frame.grid(column=0, row=0, sticky=tk.NE)
        
        hours_frame.columnconfigure(index=0, weight=1)
        hours_frame.columnconfigure(index=1, weight=1)

        lbl_start = ttk.Label(hours_frame, text="Start:")
        lbl_start.grid(column=0, row=0)

        entry_start = ttk.Entry(hours_frame, textvariable=self.start_hour)
        entry_start.grid(column=1, row=0)

        lbl_stop = ttk.Label(hours_frame, text="Stop:")
        lbl_stop.grid(column=0, row=1)

        entry_stop = ttk.Entry(hours_frame, textvariable=self.stop_hour)
        entry_stop.grid(column=1, row=1)

        # save button
        btn_save = ttk.Button(right_frame, text="Save", command=self.set_schedule)
        btn_save.grid(column=0, row=1, sticky=tk.SE, pady=60)
    

    def monitor(self) -> None:
        """ Method to display a minimal monitoring interface.
        """
        # insert monitoring in the main window
        frame_monitor = ttk.LabelFrame(self._root, text="Monitor", width=800, height=100)
        frame_monitor.grid(column=0, row=0, columnspan=2)

        # create a grid inside the frame
        frame_monitor.columnconfigure(index=0, weight=1)
        frame_monitor.columnconfigure(index=1, weight=1)
        frame_monitor.columnconfigure(index=2, weight=1)
        frame_monitor.columnconfigure(index=3, weight=1)

        # labels
        ttk.Label(frame_monitor, text="Power (W)").grid(column=1, row=0, padx=10)
        ttk.Label(frame_monitor, text="Temperature (°C)").grid(column=2, row=0, padx=10)
        ttk.Label(frame_monitor, text="Pressure (?)").grid(column=3, row=0, padx=10)

        ttk.Label(frame_monitor, text="Estimated: ").grid(column=0, row=1, pady=5)
        ttk.Label(frame_monitor, text="Sensors: ").grid(column=0, row=2, pady=5)

        self.monitor_val = {
            "power": {
                "estimated":tk.StringVar(),
                "sensor":tk.StringVar()
            },

            "temperature": {
                "estimated":tk.StringVar(),
                "sensor":tk.StringVar()
            },

            "pressure": {
                "estimated":tk.StringVar(),
                "sensor":tk.StringVar()
            }
        }

        self.monitor_val["power"]["estimated"].set(value="0.0")
        self.monitor_val["power"]["sensor"].set(value="0.0")
        self.monitor_val["temperature"]["estimated"].set(value="0.0")
        self.monitor_val["temperature"]["sensor"].set(value="0.0")
        self.monitor_val["pressure"]["estimated"].set(value="0.0")
        self.monitor_val["pressure"]["sensor"].set(value="0.0")

        ttk.Label(frame_monitor,
            textvariable=self.monitor_val["power"]["estimated"]).grid(column=1, row=1)
        ttk.Label(frame_monitor,
            textvariable=self.monitor_val["temperature"]["estimated"]).grid(column=2, row=1)
        ttk.Label(frame_monitor,
            textvariable=self.monitor_val["pressure"]["estimated"]).grid(column=3, row=1)
        
        ttk.Label(frame_monitor,
            textvariable=self.monitor_val["power"]["sensor"]).grid(column=1, row=2)
        ttk.Label(frame_monitor,
            textvariable=self.monitor_val["temperature"]["sensor"]).grid(column=2, row=2)
        ttk.Label(frame_monitor,
            textvariable=self.monitor_val["pressure"]["sensor"]).grid(column=3, row=2)





    def gui(self) -> None:
        """ Aims to handle the main window
        """

        # set up the main window
        self._root.title("Sr-oven")
        self._root.geometry("600x200")
        self._root.resizable(True, False)

        # create a grid to position items
        self._root.columnconfigure(index=0, weight=1)
        self._root.columnconfigure(index=1, weight=3)

        # retrieve grid width & height
        grid_w, grid_h = self._root.grid_size()

        # call the monitor handling method.
        self.monitor()

        # field to input new power to power supply
        lbl_new_temp = ttk.Label(self._root, text="Power:")
        lbl_new_temp.grid(column=0, row=1)

        frame_temp = ttk.Frame(self._root)
        frame_temp.grid(column=1, row=1, sticky=tk.W, pady=5)

        entry_new_temp = ttk.Entry(frame_temp, width=30)
        entry_new_temp.pack(side=tk.LEFT, padx=5)

        entry_new_temp.insert(0, self.get_power())

        btn_set_new_temp = ttk.Button(frame_temp, text="Set P",
                            command= lambda: self.set_power(float(entry_new_temp.get())))
        btn_set_new_temp.pack(side=tk.LEFT)

        # bottom right buttons
        # create a frame to contain them, and add new buttons to this frame
        btn_se_frame = ttk.Frame(self._root)
        btn_se_frame.grid(column=1, row=grid_w, sticky=tk.SE, pady=30)

        btn_start = ttk.Button(btn_se_frame, text="Start", command=self.start_oven)
        btn_start.pack(side=tk.LEFT, padx=3)

        btn_stop = ttk.Button(btn_se_frame, text="Stop", command=self.stop_oven)
        btn_stop.pack(side=tk.LEFT, padx=5)

        btn_schedule = ttk.Button(btn_se_frame, text="Schedule", command=self.schedule)
        btn_schedule.pack(side=tk.LEFT, padx=5)
    
    def start_oven(self) -> None:
        self.oven_config["status"] = True
    def stop_oven(self) -> None:
        self.oven_config["status"] = False

    def get_power(self) -> float:
        return self.oven_config["power"]
    def set_power(self, temp: float) -> None:
        self.oven_config["power"] = temp

    def init_hours(self) -> None:
        """ Similar to init_days, this method retrieves the hours defined in the
        oven config file
        """
        self.start_hour = tk.StringVar()
        self.start_hour.set(self.oven_config["hours"]["start"])

        self.stop_hour = tk.StringVar()
        self.stop_hour.set(self.oven_config["hours"]["stop"])
        

    def init_days(self) -> None:
        """ Tkinter needs special variables to handle checkboxes' values.
        Here, we're setting the states of each checkbox, ticking it when it is set
        on True in the oven config file.
        """
        self.days = {"Monday":tk.BooleanVar(),
        "Tuesday":tk.BooleanVar(),
        "Wednesday":tk.BooleanVar(),
        "Thursday":tk.BooleanVar(),
        "Friday":tk.BooleanVar(),
        "Saturday":tk.BooleanVar(),
        "Sunday":tk.BooleanVar()} 

        # directly set the tk variables of corresponding days on true or false
        for d in self.days:
            self.days[d].set(self.oven_config["days"][d.lower()])
    
    def set_schedule(self) -> None:
        self.oven_config["hours"]["start"] = self.start_hour.get()
        self.oven_config["hours"]["stop"] = self.stop_hour.get()
        
        for d in self.days:
            self.oven_config["days"][d.lower()] = self.days[d].get()

    def send_oven_config(self):
        try:
            re.post(self.url, json=self.oven_config)
        except Exception as err:
            self.error(err)

    
    def on_closing(self) -> None:
        """ This method is called when the client is terminating
        """
        # join all the threads here to ensure they exit too
        self.t.join()
        
        # destroy tk context and window
        self._root.destroy()

        # exit the program
        sys.exit()

    
    def run(self) -> None:
        """ It's the main method here. 
        """
        # top level instance of Tk (main window)
        self._root = tk.Tk()
        try:
            # init connection by retrieving the config file of the oven
            self.oven_config = json.loads(re.get(self.url).text)
            # send oven_config every 3 seconds 
            self.t = set_interval_as_daemon(interval=3.0,
                        callback=self.send_oven_config)
        except Exception as err:
            self.error(err)
        
        # on closing the main window
        self._root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # main window config
        self.gui()
        self._root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()

