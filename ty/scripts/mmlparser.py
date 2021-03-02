"""
MML (Music Macro Language) parser and player for Python
"""

import re
import logging

logger = logging.getLogger(__name__)


DEFAULT_OCTAVE = 4
DEFAULT_DIVIDE = 4
DEFAULT_MODE = "n"
DEFAULT_TEMPO = 120
DEFAULT_VOLUME = 90
NOTE_MAP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


class MMLParser:
    """This class provides generator-based parser and mixer to produce musical
    events from single MML strings.
    supported MML commands: A-G, MS, MN, ML, L, V, O, T, N, <, >, P, and R.
    support note decorators: :, &, #, +, -
    ignores note decorators: *{num}, [{num}],
    """

    PATTERNS = {
        "OCTAVE": re.compile(r"(<|>)"),
        "NOTE": re.compile(r"([A-GPR])([\-\+#]?)(\d*)(\.*)(\*\d+)?(\[[12]\])?([:&]?)"),
        "CCMD": re.compile(r"([LNOTV]\d+)"),
        "M": re.compile(r"(M[FBNLS])"),
    }

    def __init__(self):
        """Create parser"""
        self.octave = DEFAULT_OCTAVE
        self.divide = DEFAULT_DIVIDE
        self.mode = DEFAULT_MODE
        self.volume = DEFAULT_VOLUME
        self.tempo = DEFAULT_TEMPO

    def handle_note(self, m, mml, pos, ts):
        logger.debug("handle_note %s %s", m, ts)
        note = m.group(1)
        if note in "PR":
            note_num = 0
        else:
            note_num = NOTE_MAP[note] + 12 * self.octave + 12
            acc = m.group(2)
            if acc:
                if acc in "+#":
                    note_num += 1
                elif acc == "-":
                    note_num -= 1
        # divide
        divide = int(m.group(3) or self.divide)
        duration = 60 * 4 / self.tempo / divide
        for _ in m.group(4):  # dot
            duration *= 1.5
        if m.group(7) == ":":  # 和弦, 不增加当前时刻
            add_ts = False
        else:
            add_ts = True
        return pos, add_ts, note_num, duration

    def parse(self, mml, channel_id=0):
        """Parse a single MML string, seq, using states from the channel"""
        # music = re.sub(r"\s+|\|","",music.upper())
        
        lines = []
        for line in mml.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            lines.append(line)
        mml = "\n".join(lines)
        for char in " |\r\n":
            mml = mml.replace(char, "")
        mml = mml.upper()

        notes = []
        pos = 0
        ts = 0
        prev_note_num = None
        prev_duration = 0
        while pos < len(mml):
            logger.debug("Check %s, %s", pos, mml[pos : pos + 10])
            for typ, p in self.PATTERNS.items():
                m = p.match(mml[pos:])
                if m is not None:
                    break
            if m is None:
                raise ValueError(
                    "Invalid music expression at position {} ({})".format(
                        pos, mml[pos : pos + 10]
                    )
                )
            piece = m.group(0)
            pos += len(piece)
            if typ == "NOTE":  # note
                pos, add_ts, note_num, duration = self.handle_note(m, mml, pos, ts)
                if prev_note_num is not None:
                    if prev_note_num != note_num:
                        raise ValueError("Tied notes cannot be different")
                    duration += prev_duration

                # check for possible following note tie
                if m.group(7) == "&":
                    prev_note_num = note_num
                    prev_duration = duration
                else:
                    prev_note_num = None
                    prev_duration = 0

                    hold = self.get_hold_duration(duration)
                    notes.append([ts, 0x90, channel_id, note_num, self.volume])
                    notes.append([ts + hold, 0x80, channel_id, note_num, 0])
                    if add_ts:
                        ts += duration

            elif piece[0] == "<":  # octave down
                self.octave -= 1
            elif piece[0] == ">":  # octave up
                self.octave += 1
            elif piece[0] == "L":  # default length
                self.divide = int(piece[1:])
            elif piece[0] == "N":  # note number
                duration = 60 * 4 / self.tempo / self.divide
                hold = self.get_hold_duration(duration)
                note_num = int(piece[1:])
                notes.append([ts, 0x90, channel_id, note_num, self.volume])
                notes.append([ts + hold, 0x80, channel_id, note_num, 0])
                ts += duration
            elif piece[0] == "O":  # default octave
                self.octave = int(piece[1:])
            elif piece[0] == "V":  # volume
                self.volume = int(piece[1:])
            elif piece[0] == "T":  # tempo
                self.tempo = int(piece[1:])
            elif piece == "MN":
                self.mode = "n"
            elif piece == "ML":
                self.mode = "l"
            elif piece == "MS":
                self.mode = "s"
        return notes

    def get_hold_duration(self, duration):
        """Compute the note-on interval for the given duration and current
        mode of playing (e.g., staccato, legato)"""
        if self.mode == "s":  # staccato
            hold = min(0.1, duration)
        elif self.mode == "l":  # legato
            hold = duration
        else:  # normal
            hold = duration - min(0.1, duration / 4)
        return hold


class MMLSimplifier:
    """MML 简化

    删除多余的时长标注
    在连续5个音符中有超过3个时长相同时, 修改默认时长
    保留所有的其他内容
    """

    PATTERN = re.compile(r"(?i)([A-GPR][\-\+#]?)(\d*)(\.*)|([OL])(\d+)|(<|>)")

    def __init__(self):
        """Create simplifier"""
        self.octave = DEFAULT_OCTAVE
        self.divide = DEFAULT_DIVIDE

    def parse(self, mml):
        """Parse a single MML string, seq, using states from the channel"""
        # music = re.sub(r"\s+|\|","",music.upper())
        marks = []
        pos = 0
        while pos < len(mml):
            logger.debug("Check %s, %s", pos, mml[pos : pos + 10])
            m = self.PATTERN.search(mml[pos:])
            if m is None:
                marks.append(["#", mml[pos:]])
                return marks
            l, r = m.span()
            if l > 0:
                marks.append(["#", mml[pos : pos + l]])
            # piece = m.group(0).upper()
            note, divide, dots, cmd, cmd_arg, octave = m.groups()
            if octave:
                if octave == "<":
                    self.octave -= 1
                else:
                    self.octave += 1
            elif cmd:
                cmd = cmd.upper()
                if cmd == "O":  # octave
                    self.octave = int(cmd_arg)
                elif cmd == "L":
                    self.divide = int(cmd_arg)
            else:  # note
                note = note.upper()
                if divide:
                    divide = int(divide)
                else:
                    divide = self.divide
                marks.append(["N", note, self.octave, divide, dots])
            # update pos
            pos += r
        return marks

    def build_text(self, marks, sep=""):
        """获取简化后的曲谱"""
        self.octave = DEFAULT_OCTAVE
        self.divide = DEFAULT_DIVIDE

        for idx, mark in enumerate(marks):
            if mark[0] == "#":
                yield mark[1]
                yield sep
                continue
            _, note, octave, divide, dots = mark

            if divide != self.divide:
                # 后续5个音符的
                n = same_count = 0
                for m in marks[idx:]:
                    if m[0] != "N":
                        continue
                    n += 1
                    if m[3] == divide:
                        same_count += 1
                    if n > 4:
                        break
                if same_count > 2:
                    self.divide = divide
                    yield "L%d" % divide
                    yield sep

            delta = octave - self.octave
            if delta == 0:
                pass
            elif delta == -1:
                yield "<"
            elif delta == -2:
                yield "<<"
            elif delta == 1:
                yield ">"
            elif delta == 2:
                yield ">>"
            else:
                yield "O%d" % octave
            self.octave = octave

            yield note
            if divide != self.divide:
                yield str(divide)
            yield dots
            yield sep


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    parser = MMLSimplifier()
    data = open("mml/献给爱丽丝.mml").read()
    marks = parser.parse(data)
    res = [item for item in parser.build_text(marks)]
    print("RESULT")
    res = "".join(res)
    # check is same
    
    origin_notes = MMLParser().parse(data)
    new_notes = MMLParser().parse(res)
    print(res)
    print("from", len(data), "to", len(res))
    print(origin_notes == new_notes)
