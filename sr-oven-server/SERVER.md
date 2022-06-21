# sr-oven-server

This intends to be a minimalistic and daemonic http server manipulating the strontium oven. It listens on local network and can be controlled using HTTP protocol. See the API.

## API

API's code is somewhat well auto-documented and it might be interesting to check the routes by yourself. Still, here's a short hint on the corresponding API (note that values prefixed by a semicolon are mandatory using `POST` requests):

- `/`: get the whole config file
- `/days/<day>/:<val>` :
    - `GET` returns "true" or "false" for `<day>`, depending on what has been scheduled
    - `POST` decides to turn on or off the oven at the given `<day>`
      - `<day>`: "monday", "tuesday", ...
      - `<val>`: "true", "false" 
- `/hours/<hour>/:<val>` :
  - `GET` returns the hour corresponding to start or stop, depending of which `<hour>` is asked
  - `POST` set starting or stoping hour
    - `<hour>`: "start", "stop"
    - `<val>`: hour to be set (*e.g.* `00:32:01`)
- `/temperature/:<val>` :
  - `GET` get oven's current temperature 
  - `POST` set a new temperature for the oven
    - `<val>`: float number, representing the desired temperature for oven in celsius degree (*e.g.* `503.5`)
- `/status/:<val>` :
  - `GET` returns "true" if the oven is turned on, "false" if not
  - `POST` turns on or off the oven, manually
    - `<val>`: "true", "false"

## Adding functionalities, creating a client

Pretty easy : all you have to do is adding routes in `server.py` and implement corresponding methods in `oven.py`. If you need to store more datas or so, just add them in `config.json`.

To create a client, it is strongly encouraged to keep tracks of datas by requesting `/`, storing them in RAM as json. 

## Dependencies 

- `daemonize`
- `jsonschema`
- `flask`
- `pyvisa`
