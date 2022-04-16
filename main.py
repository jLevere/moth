#!/usr/bin/env python3
import time
import requests
import random
import json
import logging
import board
import math
from digitalio import DigitalInOut, Direction


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
    )

""" simple program to update discord message with the lights status in club office.

    uses raspberrypi 3.3v with photoresistor to alter the charge time of capacitor.  when cap is full it raises gpio to high.
    I used a 0.1uf for low light conditions found in office.
"""



class Webhook():
    """ Turns a discord message into a status notification.
    Sends a message then contenually edits the same message with new content.
    """

    def __init__(self):
        with open('conf.json', encoding='utf-8') as f:
            self.conf = json.load(f)

    def _update_conf(self):
        """ loads the current conf into file
        """
        with open('conf.json', 'w', encoding='utf-8') as f:
            json.dump(self.conf, f, indent=4, ensure_ascii=False)

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
        except requests.exceptions.RequestException as e:
            logging.error(f'webhook post errored with: {e}')
       
        if response and response.status_code in [200, 204]:
            msg = json.loads((response.content).decode('utf-8'))
            self.conf['message_id'] = msg['id']
            self._update_conf()
            return msg
        else:
            logging.error(f'Error sending webhook: {response.status_code} {response.content}')
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
            resp = requests.patch(url, data=data)
            logging.info(f'Webhook updated {resp.status_code} {resp.content}')
        except requests.exceptions.RequestException as e:
            logging.error(f'Error sending webhook: {e} \n make sure your message_id is valid.')


    def notify(self, content):
        """ if a message is already sent then update it, else send a new one
        """
        if 'message_id' in self.conf:
            self._edit(content)
        else:
            self._send(content)


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


def main():

    with open('conf.json') as f:
        conf = json.load(f)

    choice = input("Test(t) to test or enter to start: ")
    if choice.lower()[:1] == 't':
        print_light_values(conf['pin'])

    choice = input("Yes(Y) to configure blackpoint with wizard, else No(N) to use blackpoint from conf [Y/N]: ")
    
    if choice.lower()[:1] == 'y':
        blackpoint = configure_blackpoint(conf['pin'], conf['cycles'])
    else:
        blackpoint = conf['blackpoint']

    webhook = Webhook()

    print(f"starting with blackpoint: {blackpoint}")

    while True:
        light = (test_pin(conf['pin'], 10) < blackpoint)
        webhook.notify(f'someone is in the office: {light}')

        time.sleep(conf['sleep'])

if __name__ == '__main__':
    main()