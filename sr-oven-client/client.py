import json, sys, math
import requests as re
import threading as thread

import tkinter as tk
from tkinter import ttk

from influxdb_client import InfluxDBClient 

def set_interval_as_daemon(interval: float, callback: any) -> thread.Thread:
    """ Mimics "setInterval" in javascript.
    It calls the callback each X secs, X being defined by the interval parameter.
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
        self.t2 = None
        self.haserror = False

        self.oven_config = {}
        self.days = {}
        self.monitor_val = {}

        self.start_hour = None
        self.stop_hour = None

        self.url = None
        self.client_db = None 
        self.query_api = None

    def monitor_update_frame(self) -> None:
        self.query_influx_monitoring()
        self.monitor_update_estimated()
    
    
    def monitor_update_estimated(self) -> None:
        """ We use polynomial curve fitting to estimate parameters.
        """

        I = self.monitor_val['current']['estimated'].get()
        if(I == '' or I == '0.0'):
            self.monitor_val['power']['estimated'].set(0.0)
            self.monitor_val['pressure']['estimated'].set(0.0)
            self.monitor_val['temperature']['estimated'].set(0.0)
            return
        
        I2 = float(I)**2
        Pest = (-0.24302921*(I2)**3) + (1.4810746*(I2)**2) +\
            (2.43942776*I2) + (-0.08978468)
        
        Test2 = -595.47122786*Pest**2 + 37601.10325344*Pest + 611.80015273
        Test = math.sqrt(Test2)

        pest_log10 = (-0.00996306 * Pest**3) + (0.14799649*Pest**2) + \
              (  -0.26653075 * Pest) -8.89107361
        pest = 10**pest_log10


        self.monitor_val['power']['estimated'].set("{:.2f}".format(Pest))
        self.monitor_val['temperature']['estimated'].set("{:.2f}".format(Test))
        self.monitor_val['pressure']['estimated'].set("{:.2e}".format(pest))



        

            
    
    def monitor_frame(self) -> None:
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
        frame_monitor.columnconfigure(index=4, weight=1)

        # labels
        ttk.Label(frame_monitor, text="Power (W)").grid(column=1, row=0, padx=10)
        ttk.Label(frame_monitor, text="Current (A)").grid(column=2, row=0, padx=10)
        ttk.Label(frame_monitor, text="Temperature (°C)").grid(column=3, row=0, padx=10)
        ttk.Label(frame_monitor, text="Pressure (mbar)").grid(column=4, row=0, padx=10)

        ttk.Label(frame_monitor, text="Estimated: ").grid(column=0, row=1, pady=5)
        ttk.Label(frame_monitor, text="Measured: ").grid(column=0, row=2, pady=5)

        self.init_monitor()

        ttk.Label(frame_monitor,
            textvariable=self.monitor_val["power"]["estimated"]).grid(column=1, row=1)
        ttk.Entry(frame_monitor,
            textvariable=self.monitor_val["current"]["estimated"], width=6, justify='center').grid(column=2, row=1)
        ttk.Label(frame_monitor,
            textvariable=self.monitor_val["temperature"]["estimated"]).grid(column=3, row=1)
        ttk.Label(frame_monitor,
            textvariable=self.monitor_val["pressure"]["estimated"]).grid(column=4, row=1)
        
        ttk.Label(frame_monitor,
            textvariable=self.monitor_val["power"]["sensor"]).grid(column=1, row=2)
        ttk.Label(frame_monitor,
            textvariable=self.monitor_val["current"]["sensor"]).grid(column=2, row=2)
        ttk.Label(frame_monitor,
            textvariable=self.monitor_val["temperature"]["sensor"]).grid(column=3, row=2)
        ttk.Label(frame_monitor,
            textvariable=self.monitor_val["pressure"]["sensor"]).grid(column=4, row=2)
    
    def error_window(self, err) -> None:
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

    def schedule_window(self) -> None:
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

        # corresponding labels
        # we don't use built-in checkbutton labels because they can't be aligned correctly
        # instead use new labels
        for i,d in enumerate(self.days):
            self.days[d]['ref_checkbox'] = tk.Checkbutton(days_frame, variable=self.days[d]['var'])
            self.days[d]['ref_checkbox'].grid(column=0, row=i)
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
        btn_scheduler_frame = ttk.Frame(right_frame)
        btn_scheduler_frame.grid(column=0, row=1, sticky=tk.SE, pady=60)

        btn_scheduler_frame.columnconfigure(index=0, weight=1)
        
        btn_save = ttk.Button(btn_scheduler_frame, text="Save", command=self.set_schedule)
        btn_save.grid(column=0, row=0)
    
    def main_window(self) -> None:
        """ Aims to handle the main window
        """
        # set up the main window
        self._root.title("Sr-oven")
        self._root.geometry("530x135")
        self._root.resizable(False, False)

        # call the monitor handling method.
        self.monitor_frame()


        control_frame = ttk.Frame(self._root)
        control_frame.grid(column=0, row=1, columnspan=2)

        control_frame.columnconfigure(index=0, weight=1)
        control_frame.columnconfigure(index=0, weight=2)
        
        # current command
        left_control_frame = ttk.Frame(control_frame)
        left_control_frame.grid(column=0, row=0, padx=18)

        left_control_frame.columnconfigure(index=0, weight=1)
        left_control_frame.columnconfigure(index=1, weight=1)
        left_control_frame.columnconfigure(index=2, weight=1)

        lbl_new_curr = ttk.Label(left_control_frame, text="Current (A): ")
        lbl_new_curr.grid(column=0, row=0)

        entry_new_curr = ttk.Entry(left_control_frame, width=6)
        entry_new_curr.grid(column=1, row=0, padx=2, ipady=4)

        btn_set_new_curr = ttk.Button(left_control_frame, text="Set", width=10, 
                            command= lambda: self.set_current(float(entry_new_curr.get())))
        btn_set_new_curr.grid(column=2, row=0)

        entry_new_curr.insert(0, self.get_current())

        # start/stop/schedule buttons
        right_control_frame = ttk.Frame(control_frame)
        right_control_frame.grid(column=1, row=0)

        right_control_frame.columnconfigure(index=0, weight=1)
        right_control_frame.columnconfigure(index=1, weight=1)
        right_control_frame.columnconfigure(index=2, weight=1)

        btn_start = ttk.Button(right_control_frame, text="Start", command=self.start_oven)
        btn_start.grid(column=0, row=0, padx=2)

        btn_stop = ttk.Button(right_control_frame, text="Stop", command=self.stop_oven)
        btn_stop.grid(column=1, row=0, padx=2)

        btn_schedule = ttk.Button(right_control_frame, text="Schedule", command=self.schedule_window)
        btn_schedule.grid(column=2, row=0, padx=2)



    # config and init 
    def start_oven(self) -> None:
        self.oven_config["status"] = True
        re.post(self.url+"status/start")
    def stop_oven(self) -> None:
        self.oven_config["status"] = False
        re.post(self.url+"status/stop")

    def get_current(self) -> float:
        return self.oven_config["current"]
    def set_current(self, temp: float) -> None:
        self.oven_config["current"] = temp
        self.oven_config["modified"] = True


    def set_schedule(self) -> None:
        self.oven_config["hours"]["start"] = self.start_hour.get()
        self.oven_config["hours"]["stop"] = self.stop_hour.get()
        self.oven_config["modified"] = True
        
        for d in self.days:
            self.oven_config["days"][d.lower()] = self.days[d]['var'].get()

    def send_oven_config(self):
        """ This method is in charge to send the new values to the oven server
        """
        try:
            if(self.oven_config['modified']):
                re.post(self.url, json=self.oven_config)
            self.oven_config['modified'] = False
        except Exception as err:
            self.error_window(err)

    def init_hours(self) -> None:
        """ Similar to init_days, this method retrieves the hours defined in the
        oven config file
        """
        self.start_hour = tk.StringVar()
        self.start_hour.set(self.oven_config["hours"]["start"])

        self.stop_hour = tk.StringVar()
        self.stop_hour.set(self.oven_config["hours"]["stop"])
    
    def init_monitor(self) -> None:
        self.monitor_val = {
            "power": {
                "estimated":tk.StringVar(),
                "sensor":tk.StringVar()
            },

            "current": {
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

        self.monitor_val["power"]["estimated"].set(value="-")
        self.monitor_val["power"]["sensor"].set(value="-")
        self.monitor_val["current"]["estimated"].set(value="0.0")
        self.monitor_val["current"]["sensor"].set(value="-")
        self.monitor_val["temperature"]["estimated"].set(value="-")
        self.monitor_val["temperature"]["sensor"].set(value="-")
        self.monitor_val["pressure"]["estimated"].set(value="-")
        self.monitor_val["pressure"]["sensor"].set(value="-")
        

    def init_days(self) -> None:
        """ Tkinter needs special variables to handle checkboxes' values.
        Here, we're setting the states of each checkbox, ticking it when it is set
        on True in the oven config file.
        """
        self.days2 = {"Monday":tk.BooleanVar(),
        "Tuesday":tk.BooleanVar(),
        "Wednesday":tk.BooleanVar(),
        "Thursday":tk.BooleanVar(),
        "Friday":tk.BooleanVar(),
        "Saturday":tk.BooleanVar(),
        "Sunday":tk.BooleanVar()}

        self.days = {
            "Monday": {
                "var": tk.BooleanVar(),
                "ref_checkbox": None
            },

            "Tuesday": {
                "var": tk.BooleanVar(),
                "ref_checkbox": None
            },

            "Wednesday": {
                "var": tk.BooleanVar(),
                "ref_checkbox": None
            },

            "Thursday": {
                "var": tk.BooleanVar(),
                "ref_checkbox": None
            },

            "Friday": {
                "var": tk.BooleanVar(),
                "ref_checkbox": None
            },

            "Saturday": {
                "var": tk.BooleanVar(),
                "ref_checkbox": None
            },

            "Sunday": {
                "var": tk.BooleanVar(),
                "ref_checkbox": None
            }
        }

        # directly set the tk variables of corresponding days on true or false
        for d in self.days:
            self.days[d]['var'].set(self.oven_config["days"][d.lower()])
    

    
    def query_influx_monitoring(self) -> None:
        """ Queries InfluxDB to get measured values which will be displayed in the monitor
        """
        q_pow = 'from(bucket: "lab") \
                |> range(start: -5m, stop: now())\
                |> filter(fn: (r) => r["_measurement"] == "oven")\
                |> filter(fn: (r) => r["_field"] == "power")\
                |> last()'
        r_pow = self.query_api.query(q_pow)[0].records[0].values['_value']

        q_press = 'from(bucket: "lab")\
                |> range(start: -5m, stop: now())\
                |> filter(fn: (r) => r["_measurement"] == "vacuum")\
                |> filter(fn: (r) => r["_field"] == "pressure_mbar")\
                |> filter(fn: (r) => r["probe"] == "collimPfeiffer")\
                |> last()'
        r_press = self.query_api.query(q_press)[0].records[0].values['_value']

        q_resist = 'from(bucket: "lab") \
                |> range(start: -5m, stop: now()) \
                |> filter(fn: (r) => r["_measurement"] == "oven") \
                |> filter(fn: (r) => r["_field"] == "resist") \
                |> last()'
        r_resist = self.query_api.query(q_resist)[0].records[0].values['_value']
        
        # use a fitting curve to convert oven power supp. resist. to temperature
        # see labbook for more informations
        r_temp = 25.0 +( -1.7*0.0036 + math.sqrt( math.pow(1.7*0.0036, 2.0) - 4.0 * (-0.0000016)*\
        (1.7-float(r_resist)))) / (-2.0*0.0000016)

        q_curr = 'from(bucket: "lab") \
                |> range(start: -5m, stop: now()) \
                |> filter(fn: (r) => r["_measurement"] == "oven") \
                |> filter(fn: (r) => r["_field"] == "current") \
                |> last()'
        r_curr = self.query_api.query(q_curr)[0].records[0].values['_value']

        # update monitor labels with retrieved values from sensors
        self.monitor_val['power']['sensor'].set("{:.2f}".format(r_pow))
        self.monitor_val['pressure']['sensor'].set("{:.2e}".format(r_press))
        self.monitor_val['current']['sensor'].set("{:.2f}".format(r_curr))
        self.monitor_val['temperature']['sensor'].set("{:.2f}".format(r_temp))

    
    def on_closing(self) -> None:
        """ This method is called when the client is terminating
        """
        # join all the threads here to ensure they exit too
        self.t.join()
        self.t2.join()
        
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

            with open("./client_config.json") as client_config_file:
                client_config = json.load(client_config_file)
                self.url = f"http://{client_config['host']}:{client_config['port']}/"
                self.client_db = InfluxDBClient(url=f"http://{client_config['influx_host']}:{client_config['influx_port']}/", 
                        token=client_config['influx_token'], 
                        org="Strontium")
            self.query_api = self.client_db.query_api()
            # init connection by retrieving the config file of the oven
            self.oven_config = json.loads(re.get(self.url).text)
            # send oven_config every 3 seconds 
            self.t = set_interval_as_daemon(interval=3.0,
                        callback=self.send_oven_config)
            # update monitor measured values every 0.1s
            self.t2 = set_interval_as_daemon(interval=0.1,
                        callback=self.monitor_update_frame)
        except Exception as err:
            self.error_window(err)
        
        # on closing the main window
        self._root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # main window config
        self.main_window()
        self._root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()

