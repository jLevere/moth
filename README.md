# moth
Updates discord message if someone is in the club office.  Uses raspi to check light status in room.


Uses adafruit blinka circuitpython package to interact with raspberrypi gpio.

`sudo pip install Adafruit-Blinka`  to install package

## Setup

First run the `print_light_values` function to find what the normal and dark values are.  Set the darkpoint value in `main` with this.

Next set the gpio pin in the `main` function.  On raspberrypi gpio are designated as board.D`{pin_number}`  

Then generate a discord webhook and load it into the `make_inital_message` function.  

Next go to discord and get the message_id of the inital message and load it and the webhook into the `notify` function.  This will allow moth to update the message inplace without resending it.




Moth must be run as root to interact with gpio.  Make sure your file permissions are safe and sane.
