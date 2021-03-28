# Adafruit-DHT22 sensor remote monitor
This repo contains two sets of scripts for the purpose of monitoring an [Adafruit DHT22](https://www.adafruit.com/product/385)
sensor connected to a raspberry pi. For testing purposes a dummy driver was also created.


## Software requirements:
 - Python3
 - git
 - pip3


## Setup:
On a command line, clone the repo using the following command:
```shell script
git clone https://github.com/lord-aceldama/Azouagh-Adafruit-DHT22-remote-monitor
``` 

Once the repo is downloaded, change into the new directory. 
```shell script
cd Azouagh-Adafruit-DHT22-remote-monitor
``` 

Once the repo is downloaded, you may wish to create a virtual environment for the script to run in. If you do not wish 
to create a virtual environment, skip this step, otherwise run:
```shell script
python3 -m venv venv
. venv/bin/activate
``` 

You can now install the necessary pips by running:
```shell script
pip3 install -r requirements.txt
```


## Repo index:
### Dummy driver
#### Script(s):
 - `ada_dht.py` to test scripts without the actual sensor present (`6` lines of code)


### TCP socket client/Server
#### Overview
Client's first request was a solution to monitor the sensor readings remotely. As using a web server was not possible
the logical solution was to use TCP sockets to relay the data across a network (or internet). 
#### Script(s):
 - `client.py` to run on the raspberry pi (`31` lines of code)
 - `server.py` to run on a remote machine (`89` lines of code)
#### Usage:
```shell script
usage: client.py [-h] [-p PORT] host

positional arguments:
  host                  The remote hostname/ip to connect to.

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  The remote port to connect to. (default: 60606)
```

```shell script
usage: server.py [-h] [-p PORT]

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  The port to listen on. (default: '60606')
```

 
### Telegram bot
#### Overview
Client's next request was to receive data to 'their app', but as no such app existed i suggested Telegram as an app. The
script requires an API key (token) in order to work. for information on how to register your bot and obtain your token,
please follow the tutorial [here](https://core.telegram.org/bots#6-botfather).
#### Script(s):
 - `telegram-bot.py` (`197` lines of code)
