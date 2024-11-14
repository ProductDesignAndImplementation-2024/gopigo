from __future__ import print_function

from __future__ import division

# the above lines are meant for Python3 compatibility.

# they force the use of Python3 functionality for print(), 

# the integer division and input()

# mind your parentheses!



import easygopigo3 as easy

import time

from di_sensors import line_follower



sensor_readings = None



gpg = easy.EasyGoPiGo3()


try:

  #front_distance_sensor = gpg.init_distance_sensor(port="AD2")
  package_detector  = gpg.init_distance_sensor(port="AD1")

  time.sleep(0.1)

except:

  print('Distance sensor not responding')

  time.sleep(0.2)

  exit()




package_picked_up = False


while True:

    #print("Package detector distance (mm): "+ str(package_detector.read_mm()))
    
    
    if package_detector.read_mm() < 30 and not package_picked_up:
        print("Package picked up")
        package_picked_up = True
        # Request route from server
        # route = request_route()
    elif package_detector.read_mm() > 30 and package_picked_up:
        print("Package is unloaded")
        package_picked_up = False
    