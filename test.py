from jsonschema import validate
schema = {
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

j = {"bloo":"bli"}

validate(instance=j, schema=schema)