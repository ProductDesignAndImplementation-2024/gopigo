#!/usr/bin/env python



from __future__ import print_function

from __future__ import division

# the above lines are meant for Python3 compatibility.

# they force the use of Python3 functionality for print(), 

# the integer division and input()

# mind your parentheses!

import asyncio

import threading

import queue

import easygopigo3 as easy

import time

from di_sensors import line_follower

from di_sensors.easy_line_follower import EasyLineFollower

import requests

SERVER_URL = "http://10.0.0.2:5000"

GoPiGo3_number = 1

sensor_readings = None

threshold = 0.1

gpg = easy.EasyGoPiGo3()

gpg.set_speed(300)

q = queue.Queue()

followline = True

package_picked_up = False

route_received = False

try:

    my_linefollower = gpg.init_line_follower()
    #linefollower_real = line_follower.LineFollowerRed(bus='RPI_1SW')
    linefollower_easy = EasyLineFollower()


    time.sleep(0.1)

except:

  print('Line Follower not responding')

  time.sleep(0.2)

  exit()

try:

  #front_distance_sensor = gpg.init_distance_sensor(port="AD2")
  package_detector  = gpg.init_distance_sensor(port="AD1")

  time.sleep(0.1)

except:

  print('Distance sensor not responding')

  time.sleep(0.2)

  exit()

# start


def linefollowercontroller():
    print("Linefollower controller enabled")
    while True:
        lineposition = q.get()
        if followline == True:

            if lineposition == 'center':

                gpg.forward()

            if lineposition == 'left':

                gpg.left()

            if lineposition == 'right':

                gpg.right()
    #await asyncio.sleep(0.1)


def request_route():
    try:
        response = requests.get(f"{SERVER_URL}/request-route",) # timeout=30)
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

def package_detection():
    global package_picked_up
    if package_detector.read_mm() < 30 and not package_picked_up:
        print("Package picked up")
        package_picked_up = True
    elif package_detector.read_mm() > 30 and package_picked_up:
        print("Package is unloaded")
        package_picked_up = False

def send_message_to_server(message):
    try:
        response = requests.post(f"{SERVER_URL}/send-message", json={"message": message})
        if response.status_code == 200:
            json_data = response.json()
            print(f"Message sent: {json_data['message']}")
        else:
            print(f"Error: Received status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Exception occurred: {e}")
    
def send_command_to_server(command):
    try:
        response = requests.post(f"{SERVER_URL}/send-command", json={"command": command})
        if response.status_code == 200:
            print(f"Command sent: {command}")
        else:
            print(f"Error: Received status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Exception occurred: {e}")

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

gpg.stop()


async def main():
    linevalues = [1,1,1,1,1]
    lineposition = ""

    #t1 = threading.Thread(target=crossingdetection, args=[linevalues])
    t2 = threading.Thread(target=linefollowercontroller)
    #t1.start()
    t2.start()
    counter = 0
    #route = ["r","l","l","l","f","l","l","r","r","r","r","f","r","r","f","r","f","r","s"]
    attemptnum = 0
    route = []
    command = None
    start_command = "start" + str(GoPiGo3_number)
    global route_received
    global followline
    grdclr = False
    yieldturn = False
    active = False
    routeindex = int(0)
    gpg.close_eyes()
    while True:
        while not active:
            command = get_command_from_server()
            """
            if command == "stop":
                print("Stopping GoPiGo3")
                gpg.stop()
            """
            if command == start_command:
                #time.sleep(1)
                send_message_to_server("Starting GoPiGo" + str(GoPiGo3_number))
                gpg.open_eyes()
                time.sleep(0.2)
                gpg.close_eyes()
                time.sleep(0.2)
                gpg.open_eyes()
                time.sleep(0.2)
                gpg.close_eyes()
                time.sleep(0.2)
                gpg.open_eyes()
                time.sleep(0.2)
                gpg.close_eyes()
                active = True
                followline = True
                break
                
            gpg.open_eyes()
            time.sleep(1)
            gpg.close_eyes()
            time.sleep(1)

    
    
        while active:
            linevalues = linefollower_easy.read()
            if (linevalues[0] < threshold and linevalues[1] < threshold and linevalues[2] < threshold and linevalues[3] < threshold and linevalues[4] < threshold):
            
                if grdclr:
                    gpg.stop()
                    followline = False
                    package_detection()
                    if package_picked_up:
                        print ("waiting for package removal...")
                        send_message_to_server("GoPiGo" + str(GoPiGo3_number) + " is waiting for package removal")
                        time.sleep(0.5)
                        continue
                    else:
                        print("package removed !")
                        send_message_to_server("GoPiGo" + str(GoPiGo3_number) + " package removed")
                        followline = True
                        yieldturn = True
                        grdclr = False
                        gpg.forward()
                        time.sleep(0.4)
                        continue
                        
                
                        
                if not route_received:
                    gpg.stop()
                    followline = False
                    package_detection()

                    if attemptnum > 0:
                        followline = False
                        gpg.stop()
                        while len(route) == 0:
                            print("No route received, requesting again...")
                            route = request_route()
                        print(route)
                        send_message_to_server("GoPiGo" + str(GoPiGo3_number) + " received route " + str(route))
                        attemptnum = 0
                        route_received = True
                        followline = True
                        gpg.forward()
                        time.sleep(0.4)
                        linevalues = linefollower_easy.read()
                        continue

                    if package_picked_up:
                        #print("Requesting route...")
                        send_message_to_server("GoPiGo" + str(GoPiGo3_number) + " picked up package and is requesting route")
                        #time.sleep(3)
                        followline = True
                        #route = request_route()
                        attemptnum += 1
                        time.sleep(1)
                        gpg.forward()
                        time.sleep(0.4)
                        
                    
                    if not package_picked_up:
                        print("waiting for package...")
                        send_message_to_server("GoPiGo" + str(GoPiGo3_number) + " is waiting for package")
                        #continue
                        
                


                        
            if yieldturn:
                    print("going inactive...")
                    active = False
                    yieldturn = False
                    gpg.forward()
                    #time.sleep(0.4)
                    for x in range(90):
                        time.sleep(0.001667)
                        lineposition = linefollower_easy.read_position()
                        q.put(lineposition)
                    gpg.stop()
                    followline = False
                    break        
                    

            if route_received:
                
                if (linevalues[0] < threshold and linevalues[1] < threshold and linevalues[2] < threshold and linevalues[3] < threshold and linevalues[4] < threshold
                or linevalues[0] < threshold and linevalues[1] < threshold and linevalues[2]< threshold
                or linevalues[2] < threshold and linevalues[3] < threshold and linevalues[4] < threshold):

                    counter += 1
                    
                    followline = False
                    gpg.open_eyes()

                    
                while counter > 0:
                            
                    #gpg.drive_cm(7)
                    print(routeindex)
                    print(route[routeindex])

                    
                    if route[routeindex] == "r":
                        gpg.drive_cm(7)
                        gpg.orbit(90)
                        #gpg.right()
                        routeindex += 1
                            #continue
                    elif route[routeindex] == "f":
                        gpg.forward()
                        time.sleep(0.2)
                        routeindex += 1
                        #continue
                    elif route[routeindex] == "l":
                        gpg.drive_cm(7)
                        gpg.orbit(-90)
                        #gpg.left()
                        routeindex += 1
                            #continue
                    if len(route) == routeindex:
                        #gpg.stop()
                        gpg.close_eyes()
                        routeindex = 0
                        route = []
                        route_received = False
                        grdclr = True
                        followline = True
                        send_command_to_server("start" + str(GoPiGo3_number +1)) # Send start command to next GoPiGo3
                        time.sleep(0.3)
                        send_message_to_server("Sending start command to GoPiGo" + str(GoPiGo3_number + 1))
                        #exit()
                    counter = 0
                    followline = True
                    gpg.close_eyes()
                    
                #await asyncio.sleep(0)
            '''
                if routeindex == 0:
                    route = []
                    route_received = False
                    grdclr = True
                    send_command_to_server("start" + str(GoPiGo3_number +1)) # Send start command to next GoPiGo3
                    time.sleep(3)
                    send_message_to_server("Sending start command to GoPiGo" + str(GoPiGo3_number + 1))
            
            '''     
            lineposition = linefollower_easy.read_position()
            q.put(lineposition)
            #t1.run()
            #t2.run()
            #print(linevalues)
            #print(lineposition)
            


asyncio.run(main())