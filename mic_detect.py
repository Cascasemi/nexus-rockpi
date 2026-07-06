"""
USB Microphone Detector
=======================
Run this on your laptop (Windows/Linux/Mac) to find the exact
name of your USB microphone.

Copy the name shown in the output and paste it into:
  raspberry_pi/realtime_detector.py  →  USB_MIC_NAME = "..."

The Pi script will then match that name automatically whenever
the same USB microphone is plugged in.

Usage:
  python detect_mic.py
"""

import sounddevice as sd


def main():
    devices = sd.query_devices()

    print()
    print("=" * 60)
    print("  ALL AUDIO DEVICES DETECTED")
    print("=" * 60)
    print(f"  {'IDX':<5} {'TYPE':<8} {'CHANNELS':<10} NAME")
    print("-" * 60)

    usb_mics = []

    for idx, dev in enumerate(devices):
        has_input  = dev["max_input_channels"] > 0
        has_output = dev["max_output_channels"] > 0

        if has_input and has_output:
            dev_type = "IN/OUT"
        elif has_input:
            dev_type = "INPUT"
        elif has_output:
            dev_type = "OUTPUT"
        else:
            dev_type = "?"

        channels = (
            f"in:{dev['max_input_channels']}"
            f" out:{dev['max_output_channels']}"
        )
        name = dev["name"]
        marker = ""

        # Flag likely USB microphones — "audio" alone is too broad (catches built-in HD Audio)
        name_lower = name.lower()
        skip_keywords = ("microsoft sound mapper", "primary sound", "high definition audio")
        is_builtin = any(s in name_lower for s in skip_keywords)
        if has_input and not is_builtin and any(k in name_lower for k in ("usb", "pnp", "microphone (usb", "microphone (2-")):
            marker = "  <-- USB MIC"
            usb_mics.append((idx, name))

        print(f"  [{idx:<3}] {dev_type:<8} {channels:<12} {name}{marker}")

    print("=" * 60)

    # Summary
    print()
    if usb_mics:
        print("  USB MICROPHONE(S) FOUND:")
        print()
        for idx, name in usb_mics:
            print(f"    Device index : {idx}")
            print(f"    Device name  : {name}")
            print()
            print("  Copy this name into raspberry_pi/realtime_detector.py:")
            print()
            print(f'    USB_MIC_NAME = "{name}"')
            print()
    else:
        print("  No USB microphone detected.")
        print("  Make sure it is plugged in and try again.")
        print()
        print("  If you know which device it is, copy its name from")
        print("  the list above and set it manually:")
        print('    USB_MIC_NAME = "<paste name here>"')
        print()

    # Quick recording test
    if usb_mics:
        idx, name = usb_mics[0]
        print("-" * 60)
        print(f"  Quick test: recording 2 seconds from [{idx}] {name}")
        print("  Speak into the microphone now...")
        print()

        try:
            import numpy as np
            recording = sd.rec(
                int(2 * 44100),
                samplerate=44100,
                channels=1,
                dtype="float32",
                device=idx,
            )
            sd.wait()
            rms = float((recording ** 2).mean() ** 0.5)

            if rms > 0.001:
                print(f"  Audio captured — RMS level: {rms:.5f}  (mic is working)")
            else:
                print(f"  Very low signal (RMS: {rms:.5f}) — check mic volume/mute")
        except Exception as exc:
            print(f"  Recording test failed: {exc}")

    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
