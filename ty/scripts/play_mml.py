import sys
import os
from mmlparser import MMLParser
import rtmidi
import time


def update_vel(all_events):
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


def play(mml, start_at):
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
    update_vel(all_events)

    with midi:
        start = time.perf_counter() - start_at
        for ts, evt, channel, note, vel in all_events:
            if ts < start_at:
                continue
            wait = ts - time.perf_counter() + start
            if wait > 0:
                time.sleep(wait)
            if note == 0:
                continue
            print(
                "{:6.3f} evt 0x{:02x} chl {} note {} vel {}".format(
                    ts, evt, channel, note, vel
                )
            )
            if channel >= 9:
                channel += 1
            if channel >= 16:
                channel = channel % 16
            midi.send_message([evt + channel, note, vel])
    del midi


data = """
0 r
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
i 8
j 9
A 1   N - - -
B 2   N -
C 4   N
D 8   下划线*1
E 16  下划线*2
F 32  下划线*3
"""
reps = dict([line.split()[:2] for line in data.strip().splitlines()])


def convert(text):
    text = "".join([reps.get(c, c) for c in text])
    return text


def main(name, start_at=0):
    print("Play", name, "from", start_at)
    if not os.path.exists(name):
        return
    with open(name, "r", -1, "UTF8") as f:
        data = f.read()
        need_convert = data.startswith("%!NUMFORMAT")
    tracks = []
    track = []
    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue
        if not line.startswith("%"):
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
    play(tracks, start_at)


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
        if not data.startswith("%!NUMFORMAT"):
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
        if len(sys.argv) > 2:
            start_at = float(sys.argv[2])
        else:
            start_at = 0
        main(name, start_at)
    else:
        convert_all()
