# sr-oven-server

This intends to be a minimalistic and daemonic http server manipulating the strontium oven. It listens on local network and can be controlled using HTTP protocol. See the API. 

## API

API's code is somewhat well auto-documented and it might be interesting to check the routes by yourself. Still, here's a short hint on the corresponding endpoints.

- `/`:
  - `GET` returns the whole config file
  - `POST` replaces the config file
- `/days/:<day>/` :
    - `GET` returns "true" or "false" for `:<day>`, depending on what has been scheduled
    - `POST` decides to turn on or off the oven at a given day, *e.g* `{"monday":true}` would make the oven start on monday.
- `/hours/<hour>/:<val>` :
  - `GET` returns the hour corresponding to start or stop, depending of which `<hour>` is asked
  - `POST` set starting or stoping hour, *e.g* `{"start":"16:00:21"}` 
- `/temperature/:<val>` :
  - `GET` get oven's current value
  - `POST` set a new current value for the oven, *e.g* `{"current":1.26}`
- `/status/:<val>` :
  - `GET` returns "true" if the oven is turned on, "false" if not
  - `POST` turns on or off the oven, manually (query the url directly, we do not use json here)
    - `<val>`:
      - `start` : starts the oven
      - `stop` : stop the oven

## Adding functionalities, creating a client

Pretty easy : all you have to do is adding routes in `server.py` and implement corresponding methods in `oven.py`. If you need to store more datas or so, just add them in `config.json`. Update the schema too.

To create a client, it is strongly encouraged to keep tracks of datas by requesting `/`, storing them in RAM as json. 

## Dependencies 

- `jsonschema`
- `flask`
- `pyvisa`

## Install 

? 
