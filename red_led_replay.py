#!/usr/bin/env python3

import time
import usb.core
import usb.util

VENDOR_ID  = 0x331A
PRODUCT_ID = 0x501C

# ------------------------------------------------------------------
# captured packets
# ------------------------------------------------------------------

PACKETS = [
    # init (temporarily disables LED lighting. it automatically comes back after a second or two without additional packets needed to be sent.)
    #"04ab0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",

    # random/session blob from capture (changes everytime i change it in the original proprietary software on windows)
    #"555528e9ee36c58fbdc27c9e34aff6aae55fe233a06d3dd7db86d0c5577afa750192af971725c1498b665e8cac80dbf903e5afb07be2c392c678e9b0fb67a902",

    # (ESSENTIAL) status / handshake packets
    "04020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",

    "04190000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",

    "04130000000000001200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",

    # LED payload blocks
    "01ff00000000000000100c000000aa55020000ff0000000001100c000000aa55030000ff0000000001100c000000aa55040000ff0000000001100c000000aa55",

    "050000ff0000000001100c000000aa55060000ff0000000000100c000000aa55075affff0000000000100c000000aa55080000ff0000000000100c000000aa55",

    "090000ff0000000001100c000000aa550a0000ff0000000001100c030000aa550b0000ff0000000001100c000000aa550c0000ff0000000001100c000000aa55",

    "0d0000ff0000000001100c000000aa550e0000ff0000000001100c000000aa550f0000ff0000000001100c000000aa55100000ff0000000001100c000000aa55",

    "110000ff0000000001100c000000aa55120000ff0000000001100c000000aa55130000ff0000000001100c000000aa558000000000000000001000000000aa55",

    # padding
    "00" * 64,
    "00" * 64,
    "00" * 64,

    # brightness/mask blocks
    "80000000" * 16,
    "80000000" * 16,
    "80000000" * 16,
    "80000000" * 16,
    "80000000" * 16,
    "80000000" * 16,
    "80000000" * 16,
    "80000000" * 16,
    "80000000" * 16,

    # final LED block
    "01ff00000000000000100c000000aa55"
    + ("00" * 48),

    # finalize? (not needed for the LEDs to change colour)
    
#"04020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",

    #"04f00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
]


# ------------------------------------------------------------------
# usb helpers
# ------------------------------------------------------------------

def find_hid_keyboard_interface(dev):
    cfg = dev.get_active_configuration()

    for intf in cfg:
        print(
            f"Interface {intf.bInterfaceNumber}, alt {intf.bAlternateSetting}, "
            f"class 0x{intf.bInterfaceClass:02x}, "
            f"subclass 0x{intf.bInterfaceSubClass:02x}, "
            f"protocol 0x{intf.bInterfaceProtocol:02x}"
        )

    # Pick the keyboard HID interface: class 3, subclass 1, protocol 1
    for intf in cfg:
        if (
            intf.bInterfaceClass == 0x03 and
            intf.bInterfaceSubClass == 0x01 and
            intf.bInterfaceProtocol == 0x01
        ):
            return intf.bInterfaceNumber

    raise RuntimeError("keyboard HID interface not found")

def get_report(dev, intf):
    return dev.ctrl_transfer(0xA1, 0x01, 0x0300, intf, 64, timeout=1000)

def send_packet(dev, intf, payload_hex):
    payload = bytes.fromhex(payload_hex)
    dev.ctrl_transfer(0x21, 0x09, 0x0300, intf, payload, timeout=1000)
    resp = get_report(dev, intf)
    print(resp.tobytes().hex())

def main():
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        raise SystemExit("device not found")

    intf = find_hid_keyboard_interface(dev)

    detached = False
    try:
        if dev.is_kernel_driver_active(intf):
            dev.detach_kernel_driver(intf)
            detached = True
    except (NotImplementedError, usb.core.USBError):
        pass

    usb.util.claim_interface(dev, intf)

    try:
        for i, pkt in enumerate(PACKETS):
            print(f"[{i+1}/{len(PACKETS)}]")
            send_packet(dev, intf, pkt)
            time.sleep(0.015)
    finally:
        usb.util.release_interface(dev, intf)
        if detached:
            try:
                dev.attach_kernel_driver(intf)
            except Exception:
                pass

if __name__ == "__main__":
    main()
