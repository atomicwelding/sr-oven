""" Server responsible for communicating with clients and make the right calls
    to oven's methods.
"""

from flask import Flask, request
from jsonschema import ValidationError, validate

from oven.oven import Oven

app = Flask(__name__)
oven = Oven()

def successful_post() -> tuple: 
    return "works", 200
def unsuccessful_rqt(msg = "") -> tuple:
    return "bad request : " + msg, 400

################ ROUTER ################
@app.route('/', methods=["GET", "POST"])
def index() -> tuple:
    if(request.method == "GET"):
        return oven.config, 200
    elif(request.method == "POST"):
        try:
            validate(instance=request.json, schema=oven.schema)
            oven.config = request.json
            return successful_post()
        except ValidationError as err:
            return unsuccessful_rqt(str(err))
    else:
        unsuccessful_rqt("only get or post methods are allowed")

@app.route('/power', methods=["GET", "POST"])
def power(val = None):
    if(request.method == "GET"):
        return str(oven.config_get_power())
    elif(request.method == "POST" 
        and isinstance(request.json["power"],float)):
        oven.config_set_power(request.json["power"], float)
    else:
        return unsuccessful_rqt()


@app.route('/days/<string:day>', methods=["GET", "POST"])
def days(day = None):
    if(day is None):
        return unsuccessful_rqt()
    if(request.method == "GET"):
        return str(oven.config_get_day(day)), 200
    elif(request.method == "POST" 
        and isinstance(request.json[day], bool)):
        oven.config_set_day(day, request.json[day])
        return successful_post()
    else:
        return unsuccessful_rqt()

@app.route('/hours/<string:hour>', methods=["GET", "POST"])
def hours(hour = None):
    if(hour is None):
        return unsuccessful_rqt()
    
    if(request.method == "GET"):
        return str(oven.config_get_hour(hour)), 200
    elif(request.method == "POST"
        and isinstance(request.json[hour], str)):
        oven.config_set_hour(hour, request.json[hour])
        return successful_post()
    else:
        return unsuccessful_rqt()

@app.errorhandler(404)
def page_not_found(error):
   return "This page doesn't exist.", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8488)