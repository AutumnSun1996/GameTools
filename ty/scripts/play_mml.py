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


data = """
0 p
1 c
2 d
3 e
4 f
5 g
6 a
7 b
a 0
b 1
c 2
d 3
e 4
f 5
g 6
h 7
A 1   N - - -
B 2   N -
C 4   N
D 8   下划线*1
E 16  下划线*2
F 32  下划线*3
"""
reps = dict([line.split()[:2] for line in data.strip().splitlines()])


def convert(text):
    text = ''.join([reps.get(c, c) for c in text])
    return text


def main(name):
    print("Play", name)
    if not os.path.exists(name):
        return
    with open(name, "r", -1, "UTF8") as f:
        data = f.read()
        need_convert = data.startswith("#!NUMFORMAT")
    tracks = []
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
            tracks.append("".join(track))
            track = []
    if track:
        mml = "".join(track)
        tracks.append(mml)

    if need_convert:
        tracks = [convert(t) for t in tracks]
    play(tracks)


def convert_file(data):
    converted = []
    for line in data.splitlines()[1:]:  # 删除首行
        if not line.startswith("#"):
            line = convert(line)
        converted.append(line)
    return "\n".join(converted)


def convert_all():
    for name in os.listdir("mml"):
        if not name.endswith(".N.mml"):
            continue

        with open(os.path.join("mml", name), "r", -1, "UTF8") as f:
            data = f.read()
        if not data.startswith("#!NUMFORMAT"):
            continue
        new_data = convert_file(data)
        new_path = os.path.join("mml", name[:-6] + ".mml")
        print("Convert", name, new_path)
        print(new_data)

        with open(new_path, "w", -1, "UTF8") as f:
            f.write(new_data)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
        main(name)
    else:
        convert_all()
