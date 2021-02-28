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

const NOTE_MAP = {
    "C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11,
    "1": 0, "2": 2, "3": 4, "4": 5, "5": 7, "6": 9, "7": 11,
};
const NOTE_MAP_INV = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
const CMD_PREFIX = { vel: "V", tempo: "T" };

function initState() {
    return {
        tempo: 120,
        divide: 4,
        vel: 90,
        octave: 4,
        timestamp: 0,
        offset: 0,
    };
}

function numToNote(num) {
    let octave = parseInt(num / 12);
    let note = NOTE_MAP_INV[num - octave * 12];
    return `${note}${octave}`;
}

function numTextToCommands(text) {
    const DIVIDE_MAP = { "%": 4, "%%": 2, "%%%%": 1, "_": 8, "__": 16, "___": 32, "A": 1, "B": 2, "C": 4, "D": 8, "E": 16, "F": 32 };
    let scanner = new Scanner(text);
    let commands = [];
    let state = initState();
    while (scanner.hasNext()) {
        let m = null;
        // Note
        m = scanner.scan(/^([0-7])([-+]?)(%+|_+|[ABCDEF])?(\.*)(\*\d+)?(\[[12]\])?(:?)(&?)/);
        console.log(m);
        if (m) {
            let note = m[1].toUpperCase(), noteNum = null, evt = {};
            if (note === "0") {
                evt = { type: "rest" };
                noteNum = "r";
            } else {
                noteNum = NOTE_MAP[note] + 12 * state.octave + state.offset;
                if (m[2]) { // acc
                    if (m[2] === "-") {
                        --noteNum;
                    } else {
                        ++noteNum;
                    }
                }
                evt = { type: "note", noteNum: noteNum };
                evt.note = numToNote(noteNum);
            }

            if (m[3]) {
                evt.divide = DIVIDE_MAP[m[3]];
            } else {
                evt.divide = state.divide;
            }
            if (m[4]) {
                evt.dots = m[4].length;
            }
            if (m[5] || m[6]) {
                evt.extra = m[5] + m[6];
            }
            if (m[7]) {
                evt.is_chord = true;
            }
            if (m[8]) {
                evt.is_prefix = true;
            }
            commands.push(evt)
            continue;
        }
        if (scanner.scan(/^>/)) {
            ++state.octave;
            continue;
        }
        if (scanner.scan(/^</)) {
            --state.octave;
            continue;
        }
        m = scanner.scan(/^=([1-7])=([A-G])([#b]?)(\d*)/);
        if (m) {
            let offset = NOTE_MAP[m[2]] - NOTE_MAP[m[1]];
            if (m[3]) { // acc
                if (m[3] === "-") {
                    --offset;
                } else {
                    ++offset;
                }
            }
            if (m[4]) {
                offset = offset + (parseInt(m[4]) - 4) * 12;
            }
            state.offset = offset;
            console.log(`选调${m[1]}=${m[2]}${m[3]}`, m, state);
            continue;
        }
        m = scanner.scan(/^O(\d+)/i)
        if (m) {
            state.octave = parseInt(m[1]);
            continue;
        }
        m = scanner.scan(/^L(\d+)/i)
        if (m) {
            state.divide = parseInt(m[1]);
            continue;
        }
        m = scanner.scan(/^V(\d+)/i);
        if (m) {
            state.vel = parseInt(m[1]);
            commands.push({ type: 'vel', value: state.vel });
            continue;
        }
        m = scanner.scan(/^T(\d+)/i);
        if (m) {
            console.log("set tempo", m);
            state.tempo = parseInt(m[1]);
            commands.push({ type: 'tempo', value: state.tempo });
            continue;
        }
        m = scanner.scan(/^#\s*NewTrack\n/);
        if (m) {
            state = initState();
            commands.push({ type: 'newtrack', text: m[0] });
            continue;
        }
        m = scanner.scan(/^#.*(\n|$)/);
        if (m) {
            commands.push({ type: 'text', text: m[0] });
            continue;
        }
        m = scanner.scan(/^[|\s]/);
        if (m) {
            commands.push({ type: 'text', text: m[0] });
            continue;
        }
        console.log(commands);
        throw SyntaxError(`无法解析: ${scanner.index} ${scanner.part()}`);
    }
    return commands;
}

function textToCommands(text) {
    let scanner = new Scanner(text);
    let commands = [];
    let state = initState();
    while (scanner.hasNext()) {
        let m = null;
        // Note
        m = scanner.scan(/^(N\d+|[A-GPR])([\-\+#]?)(\d*)(\.*)(\*\d+)?(\[[12]\])?(:?)(&?)/i);
        if (m) {
            let note = m[1].toUpperCase(), noteNum = null, evt = {};
            if (note === "P" || note === "R") {
                evt = { type: "rest" };
                noteNum = "r";
            } else if (note[0] === "N") {
                noteNum = parseInt(note.substr(1));
                evt = { type: "note", noteNum: noteNum };
                evt.note = numToNote(noteNum);
            } else {
                noteNum = NOTE_MAP[note] + 12 * state.octave;
                if (m[2]) { // acc
                    if (m[2] === "-") {
                        --noteNum;
                    } else {
                        ++noteNum;
                    }
                }
                evt = { type: "note", noteNum: noteNum };
                evt.note = numToNote(noteNum);
            }

            if (m[3]) {
                evt.divide = parseInt(m[3]);
            } else {
                evt.divide = state.divide;
            }
            if (m[4]) {
                evt.dots = m[4].length;
            }
            if (m[5] || m[6]) {
                evt.extra = m[5] + m[6];
            }
            if (m[7]) {
                evt.is_chord = true;
            }
            if (m[8]) {
                evt.is_prefix = true;
            }
            commands.push(evt)
            continue;
        }
        if (scanner.scan(/^>/)) {
            ++state.octave;
            continue;
        }
        if (scanner.scan(/^</)) {
            --state.octave;
            continue;
        }
        m = scanner.scan(/^O(\d+)/i)
        if (m) {
            state.octave = parseInt(m[1]);
            continue;
        }
        m = scanner.scan(/^L(\d+)/i)
        if (m) {
            state.divide = parseInt(m[1]);
            continue;
        }
        m = scanner.scan(/^V(\d+)/i);
        if (m) {
            state.vel = parseInt(m[1]);
            commands.push({ type: 'vel', value: state.vel });
            continue;
        }
        m = scanner.scan(/^T(\d+)/i);
        if (m) {
            console.log("set tempo", m);
            state.tempo = parseInt(m[1]);
            commands.push({ type: 'tempo', value: state.tempo });
            continue;
        }
        m = scanner.scan(/^#\s*NewTrack\n/);
        if (m) {
            state = initState();
            commands.push({ type: 'newtrack', text: m[0] });
            continue;
        }
        m = scanner.scan(/^#.+(\n|$)/);
        if (m) {
            commands.push({ type: 'text', text: m[0] });
            continue;
        }
        m = scanner.scan(/^[|\s]/);
        if (m) {
            commands.push({ type: 'text', text: m[0] });
            continue;
        }
        console.log(commands);
        throw SyntaxError(`无法解析: ${scanner.index} ${scanner.part()}`);
    }
    return commands;
}
/**
 * 
 * @param {Array} commands 指令列表
 * @returns 
 * [{
 *   noteNum: 48,
 *   timestamp: 10.52,
 *   vel: 90,
 *   duration: 0.5,
 *   hold: 0.4,
 * }]
 */
function commandsToNotes(commands) {
    let notes = [];
    let state = initState();
    let prevNoteNum = null, prevDuration = 0;
    for (let cmd of commands) {
        if (cmd.type === "rest") {
            let duration = 240 / state.tempo / cmd.divide;
            state.timestamp += duration;
        } else if (cmd.type === "note") {
            let evt = { noteNum: cmd.noteNum, timestamp: state.timestamp, vel: state.vel };
            evt.duration = 240 / state.tempo / cmd.divide;
            if (cmd.dots) {
                evt.duration = evt.duration * Math.pow(1.5, cmd.dots);
            }
            if (prevNoteNum !== null) {
                if (prevNoteNum !== evt.noteNum) {
                    console.log(cmd);
                    console.log(evt);
                    throw SyntaxError(`相连的音符必须相同: ${prevNoteNum} ${evt.noteNum}`);
                }
                evt.duration = evt.duration + prevDuration;
            }
            if (cmd.is_prefix) { // '&'
                prevNoteNum = evt.noteNum;
                prevDuration = evt.duration;
                console.log("pre note", evt);
            } else {
                prevNoteNum = null;
                prevDuration = null;
                if (!cmd.is_chord) { // 和弦不增加当前时间戳
                    state.timestamp += evt.duration;
                }
                evt.hold = evt.duration - Math.min(0.1, evt.duration / 4);
                notes.push(evt);
            }
        } else if (cmd.type === "newtrack") {
            state = initState();
        } else if (cmd.type === "vel") {
            state.vel = cmd.value;
        } else if (cmd.type === "tempo") {
            state.tempo = cmd.value;
        }
    }
    return notes;
}

function serchForDivide(commands, divide, limit = 5) {
    let found = 0, total = 0;
    for (let cmd of commands) {
        if (cmd.type === "note") {
            ++total;
            if (total > limit) {
                break;
            }
            if (cmd.divide == divide) {
                ++found;
            }
        }
    }
    return found;
}

function commandsToText(commands) {
    let text = [];
    let state = initState();
    for (let i = 0; i < commands.length; ++i) {
        let cmd = commands[i];
        switch (cmd.type) {
            case "rest":
            case "note":
                // divide preset
                if (state.divide != cmd.divide) {
                    if (serchForDivide(commands.slice(i), cmd.divide, 5) > 2) {
                        state.divide = cmd.divide;
                        text.push(`L${cmd.divide}`);
                    }
                }
                // note / rest
                if (cmd.type === "note") {
                    // octave
                    let octave = parseInt(cmd.noteNum / 12);
                    let noteOffset = cmd.noteNum - octave * 12;
                    switch (octave - state.octave) {
                        case 0:
                            break
                        case 1:
                            text.push(">");
                            break;
                        case 2:
                            text.push(">>");
                            break;
                        case -1:
                            text.push("<");
                            break;
                        case -2:
                            text.push("<<");
                            break;
                        default:
                            text.push(`O${octave}`);
                    }
                    state.octave = octave;
                    text.push(NOTE_MAP_INV[noteOffset]);
                } else {
                    text.push("R");
                }
                // divide
                if (state.divide != cmd.divide) {
                    text.push(cmd.divide.toString());
                }
                // dots
                if (cmd.dots) {
                    for (let i = 0; i < cmd.dots; ++i) {
                        text.push(".");
                    }
                }
                // extra
                if (cmd.extra) {
                    text.push(cmd.extra);
                }
                if (cmd.is_chord) { // 和弦不增加当前时间戳
                    text.push(":");
                }
                if (cmd.is_prefix) { // 连接音符
                    text.push("&");
                }
                break;
            case "newtrack":
                state = initState();
            case "text":
                text.push(cmd.text);
                break;
            case "vel":
            case "tempo":
                state[cmd.type] = cmd.value;
                text.push(`${CMD_PREFIX[cmd.type]}${cmd.value}`);
                break;
        }
    }
    return text.join("");
}

function textToNotes(text) {
    return commandsToNotes(textToCommands(text));
}

function simplify(text) {
    return commandsToText(textToCommands(text));
}

if (module) {
    module.exports = {
        commandsToText,
        textToCommands,
        numToNote,
    }
}
