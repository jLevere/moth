#!/usr/bin/env python3
import time
import requests
import random
import json
import logging
import math
import sys
import signal

import RPi.GPIO as GPIO


""" simple program to update discord message with the lights status in club office.
"""

with open('conf.json') as f:
    conf = json.load(f)


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


############################## pin interactions ###########################


def simulate_pin_test(pin, cycles):
    return math.floor(random.randrange(0, 20))


def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)
    
def test_print_callback(pin):
    """print something on callback

    Args:
        pin (_type_): _description_
    """
    print(GPIO.input(pin))

def test_light_status(pin: int) -> None:
    """prints light status to stdout

    Args:
        pin (int): _description_
    """
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(pin, GPIO.FALLING, callback=test_print_callback, bouncetime=100)

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
    
    
    
def graph_light(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN)
    
    
    print("graphing sensor output")
    for i in range(100):
        
        if GPIO.input(pin):
            print("-", end='')
        else:
            print("_", end='')
        
        time.sleep(0.5)
    print("finished")
        


def main(quiet, sim=False):
    with open('conf.json') as f:
        conf = json.load(f)

    pin = conf['pin']
    blackpoint = conf['blackpoint']

    if quiet:
        # pass used for clarity
        pass
    else:
        choice = input("Press enter to start or type more for more options: ")
        if choice == 'more':
            choice = input("(t) for light_test, (s) for simulation mode, (g) for graph: ")
            choice = choice.lower()[:1]

            if choice == 't':
                test_light_status(pin)
            elif choice == 's':
                blackpoint = conf['blackpoint']
                sim = True
            elif choice == 'g':
                graph_light(pin)
            else:
                print('invalid option, exiting')
                raise SystemExit


    webhook = Webhook()

    print(f"starting with blackpoint: {blackpoint}")

    light_is_on = False
    while True:

        if sim:
            light = (simulate_pin_test(pin, conf['cycles']) < blackpoint)

        if light_is_on == light:
            webhook.notify(f'someone is in the office: {light}')

        light_is_on = light

        time.sleep(conf['sleep'])

if __name__ == '__main__':
    main(len(sys.argv) > 1 and sys.argv[1] == 'quiet', sim=False)
        