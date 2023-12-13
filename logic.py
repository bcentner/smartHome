import threading
import requests
from datetime import datetime

def get_weather(format: str):
    match format:
        case "temp":
            format = "t_2m:F"
        case "wind":
            format = "wind_speed_10m:ms"
        case "precip":
            format = "precip_24h:mm"
        case "sunrise":
            format = "sunrise:sql"
        case "sunset":
            format = "sunset:sql"
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
        cmd = input(f"Hi. What would you like to do? ").lower()
        match cmd:
            case "lights":
                color = input("What color? ").lower()
                # TODO: do color api stuff
            case "weather":
                choice = input("Temp, wind, precip, sunrise, or sunset?").lower()
                get_weather(format=choice)

            case _:
                print("Sorry, I don't currently recognize that command")
