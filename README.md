# Adafruit-DHT22 sensor remote monitor
This repo contains two sets of scripts for the purpose of monitoring the adafruit DHT22 sensor connected to a raspberry 
pi. For testing purposes a dummy driver was also created.


## Repo index:
### Dummy driver
#### Script(s):
 - `ada_dht.py` to test scripts without the actual sensor present (`6` lines of code)


### TCP socket client/Server
#### Overview
Client's first request was a solution to monitor the sensor readings remotely. As using a web server was not possible
the logical solution was to use TCP sockets to relay the data across a network (or internet). 
#### Script(s):
 - `client.py` to run on the raspberry pi (`32` lines of code)
 - `server.py` to run on a remote machine (`90` lines of code)

 
### Telegram bot
#### Overview
Client's next request was to receive data to 'their app', but as no such app existed i suggested Telegram as an app. The
script requires an API key (token) in order to work. for information on how to register your bot and obtain your token,
please follow the tutorial [here](https://core.telegram.org/bots#6-botfather).
#### Script(s):
 - `telegram-bot.py` (`197` lines of code)
