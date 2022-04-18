#!/usr/bin/env python3
import time
import requests
import random
import json
import logging
import board
import math
import sys
from digitalio import DigitalInOut, Direction
from adafruit_blinka.microcontroller.bcm283x.pin import Pin


""" simple program to update discord message with the lights status in club office.

    uses raspberrypi 3.3v with photoresistor to alter the charge time of capacitor.  when cap is full it raises gpio to high.
    I used a 0.1uf for low light conditions found in office.
"""


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename='moth.log',
    filemode='w'
    )



class Webhook():
    """ Turns a discord message into a status notification.
    Sends a message then contenually edits the same message with new content.
    """

    def __init__(self):
        with open('conf.json', encoding='utf-8') as f:
            self.conf = json.load(f)
        self.errors = 0
        self.allowed_errors = 100

    def _update_conf(self):
        """ loads the current conf into file
        """
        with open('conf.json', 'w', encoding='utf-8') as f:
            json.dump(self.conf, f, indent=4, ensure_ascii=False)

    def _good_response(self, response):
        """ check the response code on response.  also kill if error counter is too high.
        """
        if self.errors > self.allowed_errors:
            logging.error(f"more than {self.allowed_errors} http errors have occured, killing to prevent ip banning by discord")
            raise SystemExit

        if response.status_code in [200, 204]:
            logging.info(f'Webhook updated {response.status_code} {response.content}')
            return True
        elif response.status_code == 404:
            logging.error(f"Discord 404, couldnt find webhook serverside.  Make sure your webhook is set up correctly and message_id is correct.  \n{response.content}")
            self.errors = self.errors + 1
            return False 
        elif response.status_code == 403:
            logging.error(f"Discord perms denied 403, make sure you webhook is set up correctly and message_id is correct {response.content}")
            self.errors = self.errors + 1
            return False
        else:
            logging.error(f'Error sending webhook: {response.status_code} {response.content}')
            self.errors = self.errors + 1
            return False


    def _send(self, content=None):
        """ sends a webhook and saves its message id for further use.
        """

        content = "wiggle" if not content else content
        data = {
            'username' : self.conf['bot']['username'],
            'avatar_url': self.conf['bot']['avatar_url'],
            'content' : content
        }

        try:
            response = requests.post(
                self.conf['webhook'],
                data=data,
                params={"wait": True}
            )

            if self._good_response(response):
                msg = json.loads((response.content).decode('utf-8'))
                self.conf['message_id'] = msg['id']
                self._update_conf()
                return msg                

        except requests.exceptions.RequestException as e:
            logging.error(f'webhook post errored with: {e}')
            return None



    def _edit(self, content):
        """ edits the message of the id stored in conf
        """
        data = {
            "content" : content
        }

        id = self.conf['message_id']
        webhook = self.conf['webhook']
        url = f'{webhook}/messages/{id}'

        try:
            response = requests.patch(url, data=data)

            self._good_response(response)

        except requests.exceptions.RequestException as e:
            logging.error(f'Error sending webhook: {e}')


    def notify(self, content):
        """ if a message is already sent then update it, else send a new one
        """
        if 'message_id' in self.conf:
            self._edit(content)
        else:
            self._send(content)

def simulate_pin_test(pin, cycles):
    return math.floor(random.randrange(0, 20))


def test_pin(pin: int, cycles: int):
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
            final = 0
            while rc.value is False:
                final = time.time() - start_time

            avg = avg + math.floor(final * 100000)

            # this helps with acuracy
            time.sleep(0.1)

        avg = avg / cycles if time != 0 else 0
        logging.info(f"light value: {avg}")
        return avg


def print_light_values(pin):
    """ prints light value ever second for debugging and setting darkpoint
    """
    while True:
        time.sleep(1)
        print(test_pin(pin, 10))


def configure_blackpoint(pin, cycles):
    print("configuing light levels...")
    input("turn the lights off and press enter")
    dark = test_pin(pin, cycles)
    print(f"dark is set to: {dark}")

    input("now turn the lights on and press enter")
    light = test_pin(pin, cycles)
    print(f"light is set to: {light}")

    if dark == 0:
        print("dark is registering as value 0, which isn't right.  please check your hardware")
        raise SystemExit
    
    avg = (light + dark) / 2

    print(f'the darkpoint is set to: {avg}')

    return avg


def main(quiet, sim=False):
    with open('conf.json') as f:
        conf = json.load(f)

    pin = Pin(conf['pin'])
    blackpoint = conf['blackpoint']

    if quiet:
        # pass used for clarity
        pass
    else:
        choice = input("Press enter to start or type more for more options: ")
        if choice == 'more':
            choice = input("(t) for light_test, (w) for config wizard, (s) for simulation mode: ")
            choice = choice.lower()[:1]

            if choice == 't':
                print_light_values(pin)
            elif choice == 'w':
                blackpoint = configure_blackpoint(pin, conf['cycles'])
            elif choice == 's':
                blackpoint = conf['blackpoint']
                sim = True
            else:
                print('invalid option, exiting')
                raise SystemExit


    webhook = Webhook()

    print(f"starting with blackpoint: {blackpoint}")

    light_is_on = False
    while True:

        if sim:
            light = (simulate_pin_test(pin, conf['cycles']) < blackpoint)
        else:
            light = (test_pin(pin, int(conf['cycles'])) < blackpoint)


        if light_is_on == light:
            webhook.notify(f'someone is in the office: {light}')

        light_is_on = light

        time.sleep(conf['sleep'])

if __name__ == '__main__':
    main(len(sys.argv) > 1 and sys.argv[1] == 'quiet', sim=False)
        