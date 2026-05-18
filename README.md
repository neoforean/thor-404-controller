this is a repo in which i experiment with changing my genesis thor 404 tkl keyboard's led lighting through python

---

im using nobara linux but this should be straightforward for any linux distro

### dependencies
1. get pyusb<br>
installed it with sudo because pyusb wouldn't shut up about permissions:
```
sudo python3 -m pip install pyusb
```

### usage
format: `sudo python3 thor.py --rgb RRGGBB` (no hashtag)<br>
example:
```
sudo python3 thor.py --rgb 7700e0
```
> it will hopefully output `[21/21]`

### notes

> [!note]
> ### AI disclaimer
> the python script was made in a big part with AI. however, i did use virtualbox with USB passthrough and went into wireshark, captured, and examined the packets being sent. i did confirm which exact packets were essential, and i did confirm that the script works on my keyboard.

> [!tip]
> the keyboard (at least my model) likes shifting the LEDs towards blue, so to achieve a purple, the input colour has to be closer to pink
