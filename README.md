# moth
Updates discord message if someone is in the club office.  Uses raspi to check light status in room.


Uses adafruit blinka circuitpython package to interact with raspberrypi gpio.

`sudo pip install Adafruit-Blinka`  to install package
`sudo pip install requests` as well to get the requests http package to interact with webhooks

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


increase the logging level to help with troubleshooting.