# newtab
This is a tool that runs on `localhost` that can display where you should be.

# Installation
## Download
Either
1. Download ZIP and decompress; or
2.
```sh
git clone https://github.com/hanwenzhu/newtab.git
cd newtab
```

## Install Prerequisites
- Python 3.6+
- Run the following line:
```sh
python3 -m pip install -r requirements.txt
```

# Basic Usage
Run
```sh
python3 run.py
```
and go to [`http://localhost:5050`](http://localhost:5050) in the browser.

The `app` is located at `newtab:app`. Specify port using `python3 run.py <port>`.

# Customization
## WiFi login
WiFi login credentials and URL can be customized in `instance/wifi-user.json`.

## Timetable
The timetable can be customized in `instance/clock-user.json`. Set `rotation` to `false` and put timetables starting from Monday into `timetable` to use a fixed schedule.
