"use strict";

function initState() {
    let channels = [];
    for (let i = 0; i < 16; ++i) {
        channels.push({ notes: {} });
    }
    return {
        time: 0,
        channels: channels,
    }
}
function numToNote(num) {
    let octave = parseInt(num / 12);
    let note = NOTE_MAP_INV[num - octave * 12];
    return `${note}${octave}`;
}
const NOTE_MAP_INV = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

function reduction(m, n) {
    let start = Math.min(m, n);
    for (var i = start; i >= 2; i--) {
        if (m % i == 0 && n % i == 0) {
            m = m / i;
            n = n / i;
            break;
        }
    }
    return { m, n };
}

function getDivide(n) {
    const units = [64, 32, 16, 8, 4, 2, 1];
    let left = n;
    let res = [];
    let prev = null;
    for (let i = 0; i < units.length;) {
        let u = units[i];
        if (left >= u) {
            if (prev && prev.duration === u * 2) {
                prev.dot = true;
                prev = null;
            } else {
                prev = { duration: u, divide: 64 / u };
                res.push(prev);
            }
            left -= u;
        } else {
            ++i;
        }
    }
    return res;
}

function midiTrackToCommands(track, ticksPerBeat) {
    let state = initState();
    let commandState = { time: 0 };
    let commands = [];
    let allDivide = {};
    // 记录当前的和弦
    let lastCoords = [];

    function pushNote(note) {
        let divides = getDivide(note.duration * 16 / ticksPerBeat);
        divides[divides.length - 1].end = true;

        // 检查是否需要更新 vel
        if (note.type === "note" && note.vel !== commandState.vel) {
            commands.push({ type: 'vel', note: evt.vel });
        }
        for (let d of divides) {
            let evt;
            if (note.type === "rest") {
                evt = { type: "rest" }
            } else {
                evt = {
                    type: "note",
                    noteNum: note.noteNum
                }
            }
            evt.divide = d.divide;
            if (d.dot) {
                evt.dots = 1;
            }
            if (!d.end) {
                evt.is_prefix = true;
            } else {
                if (note.is_chord) {
                    evt.is_chord = true;
                }
            }
            commands.push(evt);
        }
    }
    function pushCoords(wantedDuration) {
        // 音符开始时间改变
        // 找到结束时间等于新的时间的音符, 或者添加对应的rest
        let mainNote = null;
        let resorted = [];
        for (let n of lastCoords) {
            // 未找到主要音符且当前音符符合需求, 设置当前音符为主音符
            if (!mainNote && wantedDuration === n.duration) {
                n.is_chord = false;
                mainNote = n;
            } else {
                n.is_chord = true;
                resorted.push(n);
            }
        }
        // 无对应时间的音符, 添加休止符
        if (!mainNote) {
            mainNote = { type: "rest", duration: wantedDuration };
        }
        // 主音符放在最后
        resorted.push(mainNote);
        for (let note of resorted) {
            pushNote(note);
        }
    }
    function updateCoords(note) {
        let wantedDuration = note.time - commandState.time;
        if (wantedDuration === 0) {
            // 音符开始时间未变化, 放入当前和弦
            lastCoords.push(note);
            return;
        }
        pushCoords(wantedDuration);
        // 更新和弦和时间信息
        lastCoords = [note];
        commandState.time = note.time;
    }
    for (let evt of track) {
        state.time += evt.deltaTime;
        let chl = state.channels[evt.channel]
        function handleNoteOff(evt) {
            let key = evt.noteNumber.toString();
            let note = chl.notes[key];
            if (!note) {
                console.warn("无对应的按下事件", evt, state);
            }
            note.duration = state.time - note.time;
            updateCoords(note);
            delete chl.notes[key];
        }
        switch (evt.type) {
            case "noteOn":
                let key = evt.noteNumber.toString();
                if (evt.velocity === 0) {
                    handleNoteOff(evt);
                } else {
                    if (chl.notes[key]) {
                        console.warn("重复的按下事件", evt, state);
                    }
                    chl.notes[key] = {
                        time: state.time,
                        noteNum: evt.noteNumber,
                        vel: evt.velocity,
                    }
                }
                break;
            case "noteOff":
                handleNoteOff(evt);
                break;
            case "trackName":
                commands.push({ type: "text", text: `#TrackName ${evt.text}\n` });
            default:
            // console.debug("ignore event", state.time, evt,);
        }
    }
    if (lastCoords.length > 0) {
        pushCoords(lastCoords[0].duration);
    }
    console.log(allDivide);
    return commands;
}

var fs = require('fs')
var parseMidi = require('midi-file').parseMidi
var mml = require('./js/mmlparser.js');
// Read MIDI file into a buffer
var input = fs.readFileSync('midi/This Game.mid')

// Parse it into an intermediate representation
// This will take any array-like object.  It just needs to support .length, .slice, and the [] indexed element getter.
// Buffers do that, so do native JS arrays, typed arrays, etc.
var parsed = parseMidi(input)
// console.log(parsed.header.ticksPerBeat);
let commands = midiTrackToCommands(parsed.tracks[1], parsed.header.ticksPerBeat);
console.log(commands);
// console.log(getDivide(64 + 32))
console.log(mml.commandsToText(commands));
console.log(numToNote(48));
