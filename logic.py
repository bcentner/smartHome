import threading
import requests
from datetime import datetime
import time

def get_weather(format: str):
    if format == "temp":
        format = "t_2m:F"
    elif format== "wind":
        format = "wind_speed_10m:ms"
    elif format == "precip":
        format = "precip_24h:mm"
    elif format == "sunrise":
        format = "sunrise:sql"
    elif format == "sunset":
        format = "sunset:sql"
    else:
        print("Sorry, I don't know that command")
        return
    cur_time = datetime.utcnow()
    formatted_datetime = cur_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    url = f"https://api.meteomatics.com/{formatted_datetime}/{format}/41.8781,87.6298/html"
    resp = requests.get(url=url)

    if resp.status_code == 200:
        print(resp)
    else:
        print("Error " + resp.status_code)

class Users:
    def __init__(self, name: str) -> None:
        self._statuses = [] # name in list -> logged in

    def log_in(self, name: str):
        self._statuses.append(name)
        thread = threading.Thread(target=self.get_input)
        thread.start()

    def log_out(self, name: str):
        idx = self._statuses.index(name)
        self._statuses.pop(idx)

    def get_input(self):
        while True:
            cmd = input(f"Hi. What would you like to do? ").lower()
            if cmd == "lights":
                color = input("What color? ").lower()
                # TODO: do color api stuff
            elif cmd == "weather":
                choice = input("Temp, wind, precip, sunrise, or sunset?").lower()
                get_weather(format=choice)
            else:
                print("Sorry, I don't currently recognize that command")
            time.sleep(1)
