from datetime import datetime, timedelta
import json, threading as thread, atexit, pyvisa
from jsonschema import validate

MAX_CURRENT = 1.4

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

class Oven():
    """ Main class to handle the oven. Works with a config.json file. We check the config.json is 
    properly formed using jsonschema. Raises an error when config.json is corrupted.

    All connections between the power supply and sr-oven-server are handled in this class.
    There's a router in server.py that calls methods of oven object.
    """
    def __init__(self) -> None:

        self.schema = {
            "type":"object",
            "properties": {
                "status": {
                    "type":"boolean"
                },

                "modified": {
                    "type":"boolean"
                },

                "current": {
                    "type":"number"
                },

                "days" : {
                    "type":"object",
                    "properties":{
                        "monday": {
                            "type":"boolean"
                        },

                        "tuesday": {
                            "type":"boolean"
                        },

                        "wednesday": {
                            "type":"boolean"
                        },

                        "thursday": {
                            "type":"boolean"
                        },

                        "friday": {
                            "type":"boolean"
                        },

                        "saturday": {
                            "type":"boolean"
                        },

                        "sunday": {
                            "type":"boolean"
                        }
                    }
                },

                "hours": {
                    "type":"object",
                    "properties": {
                        "start": {
                            "type":"string",
                        },

                        "stop": {
                            "type":"string"
                        }
                    }
                }
            }, 

            "required":["status", "modified", "current", "hours", "days"]
        }

        with open('/usr/local/bin/oven/config.json') as config_file:
            self._config = json.load(config_file)
        
        validate(instance=self._config, schema=self.schema)

        self.t = set_interval_as_daemon(1, self.handle_daemon)
        atexit.register(self.__del__)

    def __del__(self) -> None:
        # join threads here to ensure they stop too
        self.t.join()

    def handle_daemon(self) -> None: 
        """ Function to handle the oven, runs as a thread
        """
    
        # call this to check wether you should start or stop the oven
        self.should_be_on()
        
        # guard clause
        if(self.config_get_modified() == False):
            return
        
        # connect to the oven visa interface
        oven_PSU = pyvisa.ResourceManager().open_resource('ASRL/dev/serial/by-id/usb-TDK-LAMBDA_Z+_Serial_Port_641A075-0001-if00::INSTR')
        oven_PSU.write("INST:NSEL 01")

        # protect against too high current
        # might be good to put it in a config file or as an argument when launching the server
        # take care to not write it in config.json since it can be modified from client
        if(self._config['current'] <= MAX_CURRENT):
            oven_PSU.write(f"CURR {self._config['current']}")

        # close the connection
        self.config_set_modified(False)
        oven_PSU.close()
            
    def start(self) -> None:
        """ Default parameters at start
        """

        self.config_set_current(1.4)
        self.config_set_status(True)

        # ensure the oven wakes up
        oven_PSU = pyvisa.ResourceManager().open_resource('ASRL/dev/serial/by-id/usb-TDK-LAMBDA_Z+_Serial_Port_641A075-0001-if00::INSTR')
        oven_PSU.write("INST:NSEL 01")
        oven_PSU.write("OUTP 1")
        oven_PSU.write("VOLT 6") 
        oven_PSU.write("CURR 1.4")
        oven_PSU.close()

    def stop(self) -> None:
        """ Default parameters at stop
        """

        self.config_set_current(0.8)
        self.config_set_status(False)

        # ensure the oven shutdowns
        oven_PSU = pyvisa.ResourceManager().open_resource('ASRL/dev/serial/by-id/usb-TDK-LAMBDA_Z+_Serial_Port_641A075-0001-if00::INSTR')
        oven_PSU.write("INST:NSEL 01")
        oven_PSU.write("OUTP 1")
        oven_PSU.write("VOLT 4")
        oven_PSU.write("CURR 0.8")
        oven_PSU.close()

    def should_be_on(self) -> bool :
        """ Checks the schedule and returns true iff the oven should be on at those hours
            We allow +- 2 minutes around the desired hours to try to start or stop the oven.
        """
        
        start = [int(x) for x in self._config['hours']['start'].split(':')]
        starth = datetime.today().replace(hour=start[0], minute=start[1] , second=start[2])

        starting_hour_interval = {
            'after' : starth - timedelta(minutes=1),
            'before': starth + timedelta(minutes=1),
            
        }

        stop = [int(x) for x in  self._config['hours']['stop'].split(':')]
        stoph = datetime.today().replace(hour=stop[0], minute=stop[1] , second=stop[2])
        stopping_hour_interval = {
            'after' : stoph - timedelta(minutes=1),
            'before' : stoph + timedelta(minutes=1)
        }
        
        now = datetime.today()
        if(starting_hour_interval['after'] <= now and now <= starting_hour_interval['before']):
            self.start()
        elif(stopping_hour_interval['after'] <= now and now <= stopping_hour_interval['before']):
            self.stop()


    # accessors
    @property
    def config(self) -> dict:
        return self._config
    @config.setter
    def config(self, c) -> None:
        validate(instance=c, schema=self.schema)
        self._config = c
        self.config_save()

    # methods for configuration file
    # I initially would use accessors to get&set every values of _config 
    # but kept this very "c-ish" style for every entries in _config, since
    # accessors cannot have parameters
    def config_get_status(self) -> bool:
        return self._config["status"]
    def config_set_status(self, val: bool):
        # Use this method to turn on or off the oven manually.
        self._config["status"] = val
        self.config_save()
    
    def config_get_current(self) -> float:
        return self._config["current"]
    def config_set_current(self, val: float) -> None:
        # Use this method to set current, in A
        self._config["current"] = val
        self.config_save()

    def config_get_day(self, day: str) -> bool:
        return self._config["days"][day]
    def config_set_day(self, day: str, val: bool) -> None:
        # Use this method to enable or disable launching the oven at a certain day
        self._config["days"][day] = val
        self.config_save()

    def config_get_hour(self, key: str) -> str:
        return self._config["hours"][key]
    def config_set_hour(self, key: str, val: str) -> None:
        # Use this method to set starting and ending hour.
        self._config["hours"][key] = val
        self.config_save()

    def config_get_modified(self) -> bool:
        return self._config["modified"]
    def config_set_modified(self, val: bool) -> None:
        self._config["modified"] = val

    def config_save(self) -> None:
        # Call this method whenever you're modifying 
        # self._config to save the changes into config.json
        validate(instance=self._config, schema=self.schema)
        with open('./oven/config.json', 'w+') as config_file:
            config_file.write(json.dumps(self._config))

        self.config_set_modified(True)

