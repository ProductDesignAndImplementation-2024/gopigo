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

    route = []
    global route_received

    routeindex = 0
    gpg.close_eyes()
    while True:

        while not route_received:
            
            package_detection()
            global package_picked_up
            if package_picked_up:
                print("Requesting route...")
                time.sleep(3)
                route = request_route()
                while len(route) == 0:
                    print("No route received, requesting again...")
                    route = request_route()
                print(route)
                route_received = True
            else:
                gpg.stop()
                continue
        
        linevalues = linefollower_easy.read()
        lineposition = linefollower_easy.read_position()
        q.put(lineposition)
        #t1.run()
        #t2.run()
        #print(linevalues)
        #print(lineposition)
        if (linevalues[0] < threshold and linevalues[1] < threshold and linevalues[2] < threshold and linevalues[3] < threshold and linevalues[4] < threshold
        or linevalues[0] < threshold and linevalues[1] < threshold and linevalues[2]< threshold
        or linevalues[2] < threshold and linevalues[3] < threshold and linevalues[4] < threshold):

            counter += 1
            global followline
            followline = False
            gpg.open_eyes()

        while counter > 0:
                    
            #gpg.drive_cm(7)
            print(route[routeindex])
            print(routeindex)
            
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
            else:
                gpg.stop()
                gpg.close_eyes()
                exit()
            counter = 0
            followline = True
            gpg.close_eyes()
        #await asyncio.sleep(0)


asyncio.run(main())