"use strict";

class Scanner {
    constructor(source) {
        this.source = source;
        this.index = 0;
    }

    hasNext() {
        return this.index < this.source.length;
    }

    peek() {
        return this.source.charAt(this.index) || "";
    }

    next() {
        return this.source.charAt(this.index++) || "";
    }

    forward() {
        while (this.hasNext() && this.match(/\s/)) {
            ++this.index;
        }
    }

    expect(matcher) {
        if (!this.match(matcher)) {
            this.throwUnexpectedToken();
        }
        this.index += 1;
    }

    scan(matcher) {
        const target = this.source.substr(this.index);

        let result = matcher.exec(target);

        if (result) {
            this.index += result[0].length;
        }

        return result;
    }

    throwUnexpectedToken() {
        const identifier = this.peek() || "ILLEGAL";
        throw new SyntaxError(`Unexpected token: ${identifier}`);
    }

    part(offset = 0, size = 10) {
        return this.source.substr(this.index + offset, size);
    }
}

const NOTE_MAP = { "C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11 };

function initState() {
    return {
        tempo: 120,
        divide: 4,
        vel: 90,
        octave: 4,
        timestamp: 0,
    };
}

function parse(source) {
    let scanner = new Scanner(source);
    let result = [];
    let prevNoteNum = null, prevDuration = 0;
    let state = initState();
    while (scanner.hasNext()) {
        let m = null;
        // Note
        m = scanner.scan(/^([A-GPR])([\-\+#]?)(\d*)(\.*)(\*\d+)?(\[[12]\])?(:?)(&?)/i);
        if (m) {
            let note = m[1].toUpperCase(), noteNum = null, evt = {};
            if (note === "P" || note === "R") {
                evt = { type: "rest", timestamp: state.timestamp };
                noteNum = "r";
            } else {
                noteNum = NOTE_MAP[note] + 12 * state.octave;
                if (m[2]) { // acc
                    if (m[2] === "-") {
                        note = note + "b";
                        --noteNum;
                    } else {
                        note = note + "#";
                        ++noteNum;
                    }
                }
                evt = { type: "note", note: `${note}${state.octave}`, noteNum: noteNum, timestamp: state.timestamp, vel: state.vel };
            }
            let divide = state.divide;
            if (m[3]) {
                divide = parseInt(m[3]);
            }
            evt.duration = 240 / state.tempo / divide;
            if (m[4]) {
                evt.duration = evt.duration * Math.pow(1.5, m[4].length);
            }
            if (prevNoteNum !== null) {
                if (prevNoteNum !== noteNum) {
                    throw SyntaxError(`相连的音符必须相同: ${prevNoteNum} ${noteNum} @${scanner.index} ${scanner.part(-5, 0)}`)
                }
                evt.duration = evt.duration + prevDuration;
            }
            if (m[8]) { // '&'
                prevNoteNum = noteNum;
                prevDuration = evt.duration;
                console.log("pre note", evt);
            } else {
                prevNoteNum = null;
                prevDuration = null;
                if (!m[7]) { // 带':'标记的为和弦, 不增加当前时间戳
                    state.timestamp += evt.duration;
                }
                result.push(evt);
            }
            continue;
        }
        if (scanner.scan(/^>/)) {
            ++state.octave;
            result.push({ type: 'octave', value: state.octave });
            continue;
        }
        if (scanner.scan(/^</)) {
            --state.octave;
            result.push({ type: 'octave', value: state.octave });
            continue;
        }
        m = scanner.scan(/^O(\d+)/i)
        if (m) {
            state.octave = parseInt(m[1]);
            result.push({ type: 'octave', value: state.octave });
            continue;
        }
        m = scanner.scan(/^L(\d+)/i)
        if (m) {
            state.divide = parseInt(m[1]);
            result.push({ type: 'divide', value: state.divide });
            continue;
        }
        m = scanner.scan(/^V(\d+)/i);
        if (m) {
            state.vel = parseInt(m[1]);
            result.push({ type: 'vel', value: state.vel });
            continue;
        }
        m = scanner.scan(/^T(\d+)/i);
        if (m) {
            console.log("set tempo", m);
            state.tempo = parseInt(m[1]);
            result.push({ type: 'tempo', value: state.vel });
            continue;
        }
        m = scanner.scan(/^#\s*NewTrack\n/);
        if (m) {
            result.push({ type: 'comment', value: m[0] });
            state = initState();
            continue;
        }
        m = scanner.scan(/^#.+\n/);
        if (m) {
            result.push({ type: 'comment', value: m[0] });
            continue;
        }
        m = scanner.scan(/^[|\s]+/);
        if (m) {
            result.push({ type: 'ignore', value: m[0] });
            continue;
        }
        console.log(result);
        throw SyntaxError(`无法解析: ${scanner.index} ${scanner.part()}`);
    }
    return result;
}
