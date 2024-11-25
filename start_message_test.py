import easygopigo3 as easy
from di_sensors.easy_line_follower import EasyLineFollower
import requests
import time


gpg = easy.EasyGoPiGo3()
my_linefollower = EasyLineFollower()

gpg.set_speed(100)

GoPiGo3_number = 1

SERVER_URL = "http://10.0.0.2:5000"

route = []

gpg.close_eyes()


def request_route():
    try:
        response = requests.get(f"{SERVER_URL}/request-route", timeout=30)
        if response.status_code == 200:
            json_data = response.json()
            route = json_data['route']
            return route
        else:
            print(f"Error: Received status code {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Exception occurred: {e}")
        return []


def get_command_from_server():
    try:
        response = requests.get(f"{SERVER_URL}/get-command")
        if response.status_code == 200:
            data = response.json()
            if 'command' in data:
                return data['command']
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching command: {e}")
        return None

def send_command_to_server(command):
    try:
        response = requests.post(f"{SERVER_URL}/send-command", json={"command": command})
        if response.status_code == 200:
            print(f"Command sent: {command}")
        else:
            print(f"Error: Received status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Exception occurred: {e}")

def main():
    
    command = None
    start = False
    start_command = "start" + str(GoPiGo3_number)
    while not start:
        
        command = get_command_from_server()
        """
        if command == "stop":
            print("Stopping GoPiGo3")
            gpg.stop()
        """
        if command == start_command:
            print("Starting GoPiGo3" + str(GoPiGo3_number))
            gpg.open_eyes()
            time.sleep(1)
            gpg.close_eyes()
            time.sleep(1)
            start = True
            send_command_to_server("start" + str(GoPiGo3_number +1)) # Send start command to next GoPiGo3

        time.sleep(5)


if __name__ == "__main__":
    main()
