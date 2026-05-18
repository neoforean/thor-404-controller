#!/usr/bin/env python3

import argparse
import time
import usb.core
import usb.util

VENDOR_ID  = 0x331A
PRODUCT_ID = 0x501C


def apply_rgb(template_hex: str, rgb_hex: str) -> str:
    rgb_hex = rgb_hex.lower().strip()
    if len(rgb_hex) != 6 or any(c not in "0123456789abcdef" for c in rgb_hex):
        raise ValueError("RGB must be 6 hex chars, e.g. ff0000 or 0000ff")
    # Replace bytes 1..3 after the leading report byte 0x01
    return template_hex[:2] + rgb_hex + template_hex[8:]


def find_hid_keyboard_interface(dev):
    cfg = dev.get_active_configuration()

    for intf in cfg:
        print(
            f"Interface {intf.bInterfaceNumber}, alt {intf.bAlternateSetting}, "
            f"class 0x{intf.bInterfaceClass:02x}, "
            f"subclass 0x{intf.bInterfaceSubClass:02x}, "
            f"protocol 0x{intf.bInterfaceProtocol:02x}"
        )

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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rgb",
        default="ff0000",
        help="RGB color as 6 hex chars, e.g. ff0000, 0000ff, 00ff00",
    )
    args = parser.parse_args()

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
        packets = [
            "04020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "04190000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "04130000000000001200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",

            "01ff00000000000000100c000000aa55020000ff0000000001100c000000aa55030000ff0000000001100c000000aa55040000ff0000000001100c000000aa55",
            "050000ff0000000001100c000000aa55060000ff0000000000100c000000aa55075affff0000000000100c000000aa55080000ff0000000000100c000000aa55",
            "090000ff0000000001100c000000aa550a0000ff0000000001100c030000aa550b0000ff0000000001100c000000aa550c0000ff0000000001100c000000aa55",
            "0d0000ff0000000001100c000000aa550e0000ff0000000001100c000000aa550f0000ff0000000001100c000000aa55100000ff0000000001100c000000aa55",
            "110000ff0000000001100c000000aa55120000ff0000000001100c000000aa55130000ff0000000001100c000000aa558000000000000000001000000000aa55",

            "00" * 64,
            "00" * 64,
            "00" * 64,

            "80000000" * 16,
            "80000000" * 16,
            "80000000" * 16,
            "80000000" * 16,
            "80000000" * 16,
            "80000000" * 16,
            "80000000" * 16,
            "80000000" * 16,
            "80000000" * 16,

            "01ff00000000000000100c000000aa55" + ("00" * 48),
        ]

        packets[3] = apply_rgb(packets[3], args.rgb)
        packets[-1] = apply_rgb(packets[-1], args.rgb)

        for i, pkt in enumerate(packets, 1):
            print(f"[{i}/{len(packets)}]")
            send_packet(dev, intf, pkt)
            time.sleep(0.015)

    finally:
        usb.util.release_interface(dev, intf)
        if detached:
            try:
                dev.attach_kernel_driver(intf)
            except Exception as e:
                print(f"failed to reattach kernel driver: {e}")


if __name__ == "__main__":
    main()
