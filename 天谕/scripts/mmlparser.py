"MML (Music Macro Language) parser and player for Python"
import re
import time
from heapq import heappush, heappop


class MMLParser:
    """This class provides generator-based parser and mixer to produce musical
    events from single or multiple MML strings.  Currently, supported MML
    commands are: A-G, MS, MN, ML, L, V, O, T, N, <, >, P, and R.
    """

    NOTE_MAP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

    OCTAVE_PATTERN = r"(<|>)"
    NOTE_PATTERN = r"(([A-GPR])(\+|#|-)?(\d*)(\.?))"
    LNOTV_PATTERN = r"([LNOTV]\d+)"
    M_PATTERN = r"(M(F|B|N|L|S))"

    MUSIC_RE = re.compile(
        "|".join([OCTAVE_PATTERN, NOTE_PATTERN, LNOTV_PATTERN, M_PATTERN])
    )

    DEFAULT_DIVIDE = 4
    DEFAULT_OCTAVE = 4
    DEFAULT_MODE = "n"
    DEFAULT_TEMPO = 72
    DEFAULT_VEL = 90

    EVT_NOTE_ON = 0
    EVT_NOTE_OFF = 1
    EVT_NEXT_NOTE = 2

    def __init__(self, num_channels, callback):
        """Create a parser with the specified number of channels.  The given
        callback function will be used to receive note-on/off event
        information."""
        self.num_channels = num_channels
        self.octave = [self.DEFAULT_OCTAVE] * num_channels
        self.divide = [self.DEFAULT_DIVIDE] * num_channels
        self.mode = [self.DEFAULT_MODE] * num_channels
        self.vel = [self.DEFAULT_VEL] * num_channels
        self.tempo = self.DEFAULT_TEMPO
        self.callback = callback

    def parse(self, channel, seq):
        """Parse a single MML string, seq, using states from the channel"""
        # music = re.sub(r"\s+|\|","",music.upper())
        seq = seq.upper().replace(" ", "").replace("|", "").replace("\n", "")
        pos = 0
        prev_note_num = None
        prev_length = None
        while pos < len(seq):
            m = self.MUSIC_RE.match(seq[pos:])
            if m:
                piece = m.group(0)
                pos += len(piece)
            else:
                raise Exception(
                    "Invalid music expression at position {} ({})".format(
                        pos, seq[pos:]
                    )
                )

            if m.group(2):  # note
                note = m.group(3)
                if note not in "PR":
                    num = self.NOTE_MAP[note] + 12 * self.octave[channel]
                    acc = m.group(4)
                    if acc:
                        if acc in "+#":
                            num += 1
                        elif acc == "-":
                            num -= 1
                else:
                    num = 0
                if m.group(5):
                    divide = int(m.group(5))
                else:
                    divide = self.divide[channel]
                length = 60 * 4 / self.tempo / divide
                if m.group(6):  # dot
                    length *= 1.5
                if prev_note_num is not None:  # tied to the previous note
                    if prev_note_num != num:
                        raise Exception("Tied notes cannot be different")
                    length += prev_length
                # check for possible following note tie
                if seq[pos : pos + 1] == "&":
                    prev_note_num = num
                    prev_length = length
                    pos += 1
                else:
                    prev_note_num = None
                    prev_length = None
                    yield num, length
            elif piece[0] in "<":  # octave down
                self.octave[channel] -= 1
            elif piece[0] in ">":  # octave up
                self.octave[channel] += 1
            elif piece[0] == "L":  # default length
                self.divide[channel] = int(piece[1:])
            elif piece[0] == "N":  # note number
                yield int(piece[1:]), 60 * 4 / self.tempo / self.divide
            elif piece[0] == "O":  # default octave
                self.octave[channel] = int(piece[1:])
            elif piece[0] == "V":  # velocity
                self.vel[channel] = int(piece[1:])
            elif piece[0] == "T":  # tempo
                self.tempo = int(piece[1:])
            elif piece in ("MF", "MB"):
                pass
            elif piece == "MN":
                self.mode[channel] = "n"
            elif piece == "ML":
                self.mode[channel] = "l"
            elif piece == "MS":
                self.mode[channel] = "s"

    def get_hold_duration(self, channel, duration):
        """Compute the note-on interval for the given duration and current
        mode of playing (e.g., staccato, legato)"""
        if self.mode[channel] == "s":  # staccato
            hold = min(0.1, duration)
        elif self.mode[channel] == "l":  # legato
            hold = duration
        else:  # normal
            hold = duration - min(0.1, duration / 4)
        return hold

    def mix(self, *seqs):
        """Mix multiple MML strings and generate series of time-ordered events"""
        channels = {}
        ts = 0
        evq = []  # (ts,eventtype,stream#,note)
        for i, seq in enumerate(seqs):
            channels[i] = self.parse(i, seq)
            heappush(evq, (0, self.EVT_NEXT_NOTE, i, None))
        while evq:
            ts, etype, i, note = heappop(evq)
            yield ts, etype, i, note
            if etype == self.EVT_NEXT_NOTE:
                try:
                    note, duration = next(channels[i])
                    hold = self.get_hold_duration(i, duration)
                    heappush(evq, (ts, self.EVT_NOTE_ON, i, note))
                    heappush(evq, (ts + hold, self.EVT_NOTE_OFF, i, note))
                    heappush(evq, (ts + duration, self.EVT_NEXT_NOTE, i, None))
                except StopIteration:
                    pass

    def play(self, *seqs):
        """Parse the sequence(s) and send note-on/off events, along with
        channel number and velocity, to the registered callback function.
        Delays are performed with the blocking time.sleep() function."""
        if len(seqs) > self.num_channels:
            raise Exception("Insufficient channels")
        start = time.perf_counter()
        for ts, etype, i, note in self.mix(*seqs):
            now = time.perf_counter() - start
            wait = ts - now
            if wait > 0:
                time.sleep(wait)

            if etype == self.EVT_NOTE_ON and note > 0:
                self.callback(i, "on", note, self.vel[i])
            elif etype == self.EVT_NOTE_OFF:
                self.callback(i, "off", note, 0)

    async def aplay(self, *seqs):
        """Parse the sequence(s) and send note-on/off events, along with
        channel number and velocity, to the registered callback function.
        Delays are performed with the non-blocking asyncio.sleep()
        function."""
        if len(seqs) > self.num_channels:
            raise Exception("Insufficient channels")
        import asyncio

        start = time.perf_counter()
        for ts, etype, i, note in self.mix(*seqs):
            now = time.perf_counter() - start
            wait = ts - now
            if wait > 0:
                await asyncio.sleep(wait)
            now = ts
            if etype == self.EVT_NOTE_ON and note > 0:
                self.callback(i, "on", note, self.vel[i])
            elif etype == self.EVT_NOTE_OFF:
                self.callback(i, "off", note, 0)
