import sys
import os
from mmlparser import MMLParser
import rtmidi
import time


def update_volume(all_events):
    min_vol = 0xFFFF
    max_vol = 0
    for note in all_events:
        if note[1] == 0x90:
            vol = note[4]
            min_vol = min(min_vol, vol)
            max_vol = max(max_vol, vol)
    ratio = 90 / max_vol
    print("update volume", ratio)
    if ratio < 1.5:
        return
    ratio = int(round(ratio))
    for note in all_events:
        note[4] = note[4] * ratio


def play(mml):
    midi = rtmidi.MidiOut()
    available_ports = midi.get_ports()

    if available_ports:
        midi.open_port(0)
    else:
        midi.open_virtual_port("My virtual output")

    
    all_events = []
    for idx, track in enumerate(mml):
        events = MMLParser().parse(track, idx)
        all_events.extend(events)
    all_events.sort()
    update_volume(all_events)

    with midi:
        start = time.perf_counter()
        for ts, evt, channel, note, volume in all_events:
            wait = ts - time.perf_counter() + start
            if wait > 0:
                time.sleep(wait)
            print(
                "{:6.3f} evt 0x{:02x} chl {} note {} volume {}".format(
                    ts, evt, channel, note, volume
                )
            )
            midi.send_message([evt + channel, note, volume])
    del midi


def main(name):
    print("Play", name)
    if not os.path.exists(name):
        return
    with open(name, "r", -1, "UTF8") as f:
        data = f.read()
    mml = []
    track = []
    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue
        if not line.startswith("#"):
            track.append(line)
            continue
        if "NewTrack" not in line:
            continue
        if track:
            mml.append("".join(track))
            track = []
    if track:
        mml.append("".join(track))
    play(mml)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "mml/卡农.mml"
    main(name)
