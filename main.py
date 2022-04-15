#!/usr/bin/env python3
import time
import requests
import board
import math
from digitalio import DigitalInOut, Direction



""" simple program to update discord message with the lights status in club office.

    uses raspberrypi 3.3v with photoresistor to alter the charge time of capacitor.  when cap is full it raises gpio to high.
    I used a 0.1uf for low light conditions found in office.
"""


######## utilities #############

def make_inital_message():
    """ use this to make a message to use
    """
    data = {
        "username" : "Moth",
        "avatar_url" : "https://imgur.com/GZetIAl",
        "content" : "wiggly?"
    }
    webhook = ""
    r = requests.get(webhook, data=data)
    print(r)


def print_light_values(pin):
    """ prints light value ever second for debugging and setting darkpoint
    """
    while True:
        time.sleep(1)
        print(test_pin(pin, 10))



####### main logic ################

def test_pin(pin, cycles):
    """ returns double relivite to the light intensity.
    higher numbers are higher light intensity.
    """
    with DigitalInOut(pin) as rc:
        for i in range(cycles):
            rc.direction = Direction.OUTPUT
            rc.value = False

            start_time = time.time()
            rc.direction = Direction.INPUT

            avg = 0
            while rc.value is False:
                final = time.time() - start_time

            avg = avg + math.floor(final * 100000)

            # this helps with acuracy
            time.sleep(0.1)


        return avg / cycles if time != 0 else 0



def notify(status):
    ''' updates webhook message with status of the lights
    '''
    data = {  
    "content": f"someone is in the office: {status}",
    }

    webhook_url = ""

    # message to change
    message_id = 964561421276966912
    webhook = f"{webhook_url}/messages/{message_id}"


    with requests.patch(webhook, data=data) as r:
        print(f'discord response: {r.status_code} lights status: {status}')



def main():

    # the value at which it is considered dark
    darkpoint = 3
    # cycles to run when getting light value.  more is more acurate but takes more time.
    test_cycles = 10
    # which gpio to use
    pin = board.D4

    while True:

        # returns true when the light value is greater than darkpoint.
        # in otherwords, returns true when light is on.
        notify(test_pin(pin, test_cycles) < darkpoint)

        # sleep for a few min. 300 = 2.5min, etc
        time.sleep(300)


    
if __name__ == '__main__':
    main()
