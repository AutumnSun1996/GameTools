import sys
import os
from mmlparser import MMLParser
import rtmidi



def play(mml):
    midi = rtmidi.MidiOut()
    available_ports = midi.get_ports()

    if available_ports:
        midi.open_port(0)
    else:
        midi.open_virtual_port("My virtual output")

    def callback(channel, evt, note, vel):
        if evt == "on":
            if midi:
                midi.send_message([0x90 + channel, note, vel])
            print("CH{}: plays note {} with vel={}".format(channel, note, vel))
        elif evt == "off":
            if midi:
                midi.send_message([0x80 + channel, note, 0])
            print("CH{}: stops note {}".format(channel, note))

    parser = MMLParser(len(mml), callback)
    with midi:
        parser.play(*mml)
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
        track = []
    play(mml)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "mml/卡农.mml"
    main(name)
