#!/usr/bin/env python


from __future__ import print_function

from __future__ import division

# the above lines are meant for Python3 compatibility.

# they force the use of Python3 functionality for print(), 

# the integer division and input()

# mind your parentheses!


import easygopigo3 as easy

import time

from di_sensors import line_follower

from di_sensors.easy_line_follower import EasyLineFollower

sensor_readings = None

threshold = 0.1

gpg = easy.EasyGoPiGo3()

gpg.set_speed(200)


try:

    my_linefollower = gpg.init_line_follower()
    #linefollower_real = line_follower.LineFollowerRed(bus='RPI_1SW')
    linefollower_easy = EasyLineFollower()


    time.sleep(0.1)

except:

  print('Line Follower not responding')

  time.sleep(0.2)

  exit()
'''
try:

  my_distance_sensor = gpg.init_distance_sensor(port="AD2")

  time.sleep(0.1)

except:

  print('Distance sensor not responding')

  time.sleep(0.2)

  exit()


my_linefollower.read_position()

my_linefollower.read_position()

my_distance_sensor.read_mm()
'''


# start

'''
while True:

   

  #print(my_distance_sensor.read_mm())

  #print(my_linefollower.read_position())

  #print(linefollower_real.read_sensors())




gpg.forward()

#while not my_linefollower.read_position() == "black":
'''
counter = 0
route = ["r","l","l","l","f","l","l","r","s"]
routeindex = 0
gpg.close_eyes()

while True:

    #print(my_linefollower.read_position())

    #print("Distance Sensor Reading (mm): " + str(my_distance_sensor.read_mm()))
    linevalues = linefollower_easy.read()

    if (linevalues[0] < threshold and linevalues[1] < threshold and linevalues[2] < threshold and linevalues[3] < threshold and linevalues[4] < threshold
    or linevalues[0] < threshold and linevalues[1] < threshold and linevalues[2]< threshold
    or linevalues[2] < threshold and linevalues[3] < threshold and linevalues[4] < threshold):

        counter += 1

    while counter > 1:
        
        #gpg.drive_cm(7)
        print(route[routeindex])
        print(routeindex)
        
        if route[routeindex] == "r":
            gpg.orbit(90,5.3)
            #gpg.right()
            routeindex += 1
                #continue
        elif route[routeindex] == "f":
            gpg.forward()
            routeindex += 1
            #continue
        elif route[routeindex] == "l":
            gpg.orbit(-90,5.3)
            #gpg.left()
            routeindex += 1
                #continue
        else:
            gpg.stop()
            gpg.open_eyes()
            exit()
        counter = 0
        '''
        gpg.stop()

        gpg.open_eyes()

        time.sleep(1)

        gpg.close_eyes()

        time.sleep(1)

        #gpg.forward()
        '''

    if my_linefollower.read_position() == 'center':

        gpg.forward()

    if my_linefollower.read_position() == 'left':

        gpg.left()

    if my_linefollower.read_position() == 'right':

        gpg.right()



gpg.stop()

