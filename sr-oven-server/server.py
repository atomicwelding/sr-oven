""" Server responsible for communicating with clients and make the right calls
    to oven's methods.
"""

from flask import Flask, request 
from oven.oven import Oven

app = Flask(__name__)
oven = Oven()

################ ROUTER ################
@app.route('/', methods=["GET", "POST"])
def index():
    return oven.config

@app.route('/status/')
@app.route('/status/<string:val>', methods=["POST"])
def status(val = None):
    if(request.method == "POST" and (val is not "true" or val is not "false")):
        oven.config_set_status(val == "true")
    elif(request.method == "GET"):
        return str(oven.config_get_status())
    else: 
        return "error"

@app.route('/temperature/')
@app.route('/temperature/<float:val>', methods=["POST"])
def temperature(val = None):
    if(request.method == "POST" and val is not None):
        oven.config_set_temperature(val)
    elif(request.method == "GET"):
        return str(oven.config_get_temperature())
    else: 
        return "error"

@app.route('/days/<string:day>')
@app.route('/days/<string:day>/<string:val>', methods=["POST"])
def days(day = None, val = None):
    if(day is None):
        return "error"
    if(request.method == "GET"):
        return str(oven.config_get_day(day))
    if(request.method == "POST" and val is not None):
        if(val == "true"):
            oven.config_set_day(day, True)
        elif(val == "false"):
            oven.config_set_day(day, False)
        else:
            return "error"

@app.route('/hours/<string:hour>')
@app.route('/hours/<string:hour>/<string:val>', methods=["POST"])
def hours(hour = None, val = None):
    if(hour is None):
        return "error"
    
    if(request.method == "GET"):
        return str(oven.config_get_hour(hour))
    
    if(request.method == "POST" and val is not None):
        oven.config_set_hour(hour, val)

@app.errorhandler(404)
def page_not_found(error):
   return "This page doesn't exist.", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8488)