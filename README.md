# Genesis Thor 404 TKL RGB Controller for Linux
Control RGB lighting on the Genesis Thor 404 TKL keyboard under Linux.

Supports per-key "custom" mode, custom colour, presets, brightness adjustment & speed control.

> <img alt="The main window's GUI" width="643" height="442" alt="image" src="https://github.com/user-attachments/assets/a2aa4736-8163-4083-8f8a-1185aa3984d2" />

Custom mode:
> <img alt="The per-key lighting editor window GUI for the 'Custom' preset" width="1249" height="489" alt="image" src="https://github.com/user-attachments/assets/66305902-1c92-4a38-81a7-20f138edd5fc" />

---

### dependencies
1. get pyusb and pyqt6<br>
installed it with sudo because pyusb wouldn't shut up about permissions:
```
sudo python3 -m pip install pyqt6 pyusb
```

### usage
1. download `thor_keymap.json` and `thorgui.py`

2. put them in the same folder

3. use the gui
```
sudo python3 thorgui.py
```

---

it also accepts arguments (press apply in gui to apply)
```
sudo python3 thorgui.py --effect static --rgb 0000ff
```


```
sudo python3 thorgui.py --effect rainbow --multicolor --direction down
```

---

list available presets
```
sudo python3 thorgui.py --list
```

### technical
the main packet's offsets:
| Offset | Meaning           |
| ------ | ----------------- |
| 0x00   | effect ID         |
| 0x01   | red               |
| 0x02   | green             |
| 0x03   | blue              |
| 0x08   | multicolor toggle |
| 0x09   | brightness        |
| 0x0A   | speed             |
| 0x0B   | direction         |
| 0x0E   | 0xAA              |
| 0x0F   | 0x55              |

> **example `120000ff00000000011002010000aa55`**
> | Field      | Value            |
> | ---------- | ---------------- |
> | effect     | `0x12` = wave    |
> | RGB        | `0000ff` = blue  |
> | multicolor | `0x01` = enabled |
> | brightness | `0x10` = 16      |
> | speed      | `0x02` = 2       |
> | direction  | `0x01` = right   |

### notes

> [!note]
> ### AI disclaimer
> the python script was made in a big part with AI. USB packets were captured and verified using VirtualBox with USB passthrough, Wireshark and tshark. This software sends only the essential packets. Tested and working on a real Thor 404 TKL keyboard.

> [!tip]
> ### Resources
> previous research (offsets, notes, etc.) can be found in the [Resources](https://github.com/rrivvi/thor-404-linux-rgb-script/tree/resources) branch 
