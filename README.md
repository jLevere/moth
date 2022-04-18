# moth
Updates discord message if someone is in the club office.  Uses raspi to check light status in room.


Uses adafruit blinka circuitpython package to interact with raspberrypi gpio.

`sudo pip install Adafruit-Blinka` to install gpio package

`sudo pip install requests` for webhook interactions.

## conf

```
{
    "webhook": "",                  <- add valid webhook to the channel you want the notifications in.
    "bot": {                        <- these are the values that are used to create the first message which is not updated.
        "username": "moth",
        "avatar_url": "https://i.imgur.com/GZetIAl.png"
    },
    "pin": 3,                       <- the gpio pin the capacitor is on.
    "blackpoint": 5,                <- if you already know the blackpoint, else use wizard.
    "cycles": 10,                   <- samples taken per test. 10 is a good number.
    "sleep" : 3                     <- time to wait between each message update.
}
```


Moth must be run as root to interact with gpio.  Make sure your file permissions are safe and sane. 755 is not a bad choice.


## systemd

To run as a service with systemd add the service file to /etc/systemd/system

run `sudo systemctl daemon-reload` to load the unit file

then `sudo systemctl start moth.service` to start the service

you can add add moth.service to start on boot with `systemctl enable moth.status`  but it really isn't designed for that.