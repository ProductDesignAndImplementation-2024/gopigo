import easygopigo3 as easy
from di_sensors.easy_line_follower import EasyLineFollower
import requests
import time


gpg = easy.EasyGoPiGo3()
my_linefollower = EasyLineFollower()

gpg.set_speed(100)


SERVER_URL = "http://10.0.0.2:5000"

route = []

gpg.open_eyes()
time.sleep(1)
gpg.close_eyes()
time.sleep(1)


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

def send_command_to_gopigo(command):
    if command == 'forward':
        gpg.forward()
        #print("Moving forward")
    elif command == 'left':
        gpg.left()
        #print("Turning left")
    elif command == 'right':
        gpg.right()
        #print("Turning right")
    elif command == 'stop':
        gpg.stop()
        #print("Stopped")

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

def main():
    last_command = None
    
    route = request_route()
    print(route)
    
    while True:
        
        command = get_command_from_server()

        if command and command != last_command:
            print(f"Executing command: {command}")
            send_command_to_gopigo(command)
            last_command = command

        time.sleep(1)

if __name__ == "__main__":
    main()
