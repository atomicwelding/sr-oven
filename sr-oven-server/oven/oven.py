import json
from jsonschema import validate

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

                "temperature": {
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

            "required":["status", "temperature", "hours", "days"]
        }

        with open('./oven/config.json') as config_file:
            self._config = json.load(config_file)
        
        validate(instance=self._config, schema=self.schema)


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
    def config_get_status(self) -> bool:
        return self._config["status"]
    def config_set_status(self, val: bool):
        # Use this method to turn on or off the oven manually.
        self._config["status"] = val
        self.config_save()
    
    def config_get_temperature(self) -> float:
        return self._config["temperature"]
    def config_set_temperature(self, val: float) -> None:
        # Use this method to set temperature, in celsius degree
        self._config["temperature"] = val
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

    def config_save(self) -> None:
        # Call this method whenever you're modifying 
        # self._config to save the changes into config.json
        validate(instance=self._config, schema=self.schema)
        with open('./oven/config.json', 'w+') as config_file:
            config_file.write(json.dumps(self._config))

