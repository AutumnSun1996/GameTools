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

function midiTrackToNotes(track) {
    let state = initState();
    let notes = [];
    let extraCommands = [];

    for (let evt of track) {
        state.time += evt.deltaTime;
        let chl = state.channels[evt.channel]
        function handleNoteOff(evt) {
            let key = evt.noteNum.toString();
            let note = chl.notes[key];
            if (!note) {
                console.warn("无对应的按下事件", evt, state);
            }
            note.hold = state.time - note.timestamp;
            notes.push(note);
            delete chl.notes[key];
        }
        switch (evt.type) {
            case "noteOn":
                let key = evt.noteNum.toString();
                if (evt.velocity === 0) {
                    handleNoteOff(evt);
                } else {
                    if (chl.notes[key]) {
                        console.warn("重复的按下事件", evt, state);
                    }
                    chl.notes[key] = {
                        noteNum: evt.noteNum,
                        timestamp: state.time,
                        vel: evt.velocity,
                    }
                }
                break;
            case "noteOff":
                handleNoteOff(evt);
                break;
            case "trackName":
                extraCommands.push({
                    type: "text", text: `#TrackName ${evt.text}\n`,
                    timestamp: state.time,
                });
            default:
            // console.debug("ignore event", state.time, evt,);
        }
    }
    notes.sort((a, b) => { a.timestamp - b.timestamp });
    return { notes, extraCommands };
}

function notesToCommands(notes, ticksPerBeat = 480, quantize = 16) {
    let commands = [];
    let group = { time: 0, notes: [] };
    let rescaler = Math.round(ticksPerBeat / quantize);
    let minDuration = ticksPerBeat / 16;

    function getNoteDuration(note, wantedDuration) {
        let duration = parseInt(Math.ceil(note.durationTicks / rescaler) * rescaler);
        if (!wantedDuration) {
            return duration;
        }
        let thresh = Math.max(minDuration, note.durationTicks / 6);
        let delta = wantedDuration - duration;
        if (delta > 0 && delta < thresh) {
            console.debug("延长音符", note.durationTicks, duration, wantedDuration, note);
            return wantedDuration;
        }
        return duration;
    }

    function pushNote(note) {
        if (note.duration < minDuration) {
            console.warn("note.duration is small", note);
            return;
        }
        let divides = getDivide(note.duration * 16 / ticksPerBeat);
        if (divides.length === 0) {
            console.log("push", note, note.duration * 16 / ticksPerBeat, divides);
        }
        divides[divides.length - 1].end = true;

        // 检查是否需要更新 vel
        if (note.type === "note" && note.velocity !== commandState.vel) {
            commands.push({ type: 'vel', note: evt.velocity, ticks: note.ticks });
        }
        for (let d of divides) {
            let evt;
            if (note.type === "rest") {
                evt = { type: "rest", ticks: note.ticks }
            } else {
                evt = {
                    type: "note",
                    noteNum: note.midi,
                    ticks: note.ticks
                }
            }
            evt.divide = d.divide;
            if (d.dot) {
                evt.dots = 1;
            }
            if (!d.end) {
                evt.is_prefix = true;
            }
            if (d.end && note.is_chord) {
                evt.is_chord = true;
            }
            commands.push(evt);
        }
    }
    function pushGroup(wantedDuration) {
        // 音符开始时间改变
        // 找到结束时间等于新的时间的音符, 或者添加对应的rest
        let mainNote = { duration: 0, ticks: group.time };
        // 最后一次调用, wantedDuration将为null
        if (wantedDuration === null) {
            mainNote = group.notes[0];
        }
        for (let n of group.notes) {
            n.duration = getNoteDuration(n, wantedDuration);
            // 当前音符更符合需求, 设置当前音符为主音符
            if (wantedDuration && wantedDuration >= n.duration && n.duration > mainNote.duration) {
                mainNote = n;
            }
        }

        mainNote.is_chord = false;
        // console.log("pushGroup", mainNote, notes);
        // 添加和弦音符
        for (let note of group.notes) {
            if (note.is_chord) {
                pushNote(note);
            }
        }
        // 添加主音符
        if (mainNote.duration > 0) {
            pushNote(mainNote);
        }
        // 补充休止符
        if (wantedDuration && mainNote.duration < wantedDuration) {
            pushNote({ type: 'rest', duration: wantedDuration - mainNote.duration, ticks: mainNote.ticks });
        }
    }
    for (let note of notes) {
        let n = {
            midi: note.midi,
            ticks: note.ticks,
            durationTicks: note.durationTicks,
            is_chord: true,
        }
        // if (n.duration % 1) {
        //     console.warn("非整数时值", n.duration, note);
        // }
        if (note.durationTicks === 0) {
            console.warn("音符时长为0", note);
            continue;
        }
        if (n.ticks === group.time) {
            group.notes.push(n);
            continue;
        }
        pushGroup(n.ticks - group.time);
        group = { time: n.ticks, notes: [n] };
    }
    // push last group
    pushGroup(null);
    return commands;
}
function commandStats(commands) {
    let state = { max: 0, min: 127 };
    for (let cmd of commands) {
        if (cmd.type !== "note") {
            continue;
        }
        state.max = Math.max(cmd.noteNum, state.max);
        state.min = Math.min(cmd.noteNum, state.min);
    }
    state.maxNote = numToNote(state.max);
    state.minNote = numToNote(state.min);
    return state;
}
// // console.log(getDivide(1920*16/480))
// // process.exit();

var fs = require('fs')
const { Midi } = require('@tonejs/midi')

var mml = require('./js/mmlparser.js');
// Read MIDI file into a buffer
// var input = fs.readFileSync('midi/This game.txt');
var input = fs.readFileSync('midi/妄想税.txt');
// var input = fs.readFileSync('E:\\Documents\\Documents\\MuseScore3\\乐谱\\There is a reason-t1.mid');
// input = atob(input);
// console.log(input.slice(0, 4).toString());
input = Buffer.from(input.toString(), "base64");
// console.log(input.slice(0, 4).toString());

// Parse it into an intermediate representation
// This will take any array-like object.  It just needs to support .length, .slice, and the [] indexed element getter.
// Buffers do that, so do native JS arrays, typed arrays, etc.
const parsed = new Midi(input);
let tempos = []
for (let tempo of parsed.header.tempos) {
    tempos.push({ type: "tempo", value: Math.round(tempo.bpm), ticks: tempo.ticks });
}
console.log(tempos);
let result = [];
for (let track of parsed.tracks) {
    console.log(track.notes[0]);
    let cmds = notesToCommands(track.notes);
    console.log(commandStats(cmds));
    // console.log(cmds);
    cmds.unshift(...tempos);
    cmds.sort((a, b) => { a.ticks - b.ticks });
    // console.log(cmds.slice(0, 10));
    let text = mml.commandsToText(cmds);
    console.log(text.substr(0, 10));
    result.push(text);
}
fs.writeFileSync("out.mml", result.join("\n#NewTrack\n"))
// console.log(mml.commandsToText([{ type: "note", noteNum: 76, divide: 4 }]))
173动物管理局招贤纳士.加入本会,月月奖金,天天美女,大块吃肉,大碗喝酒,名额有限

// let notes = [
//     {
//         "duration": 0.21175411249999998,
//         "durationTicks": 227,
//         "midi": 61,
//         "name": "C#4",
//         "ticks": 240,
//         "time": 0.223881,
//         "velocity": 0.5905511811023622
//     },
//     {
//         "duration": 0.21175411249999998,
//         "durationTicks": 227,
//         "midi": 68,
//         "name": "G#4",
//         "ticks": 480,
//         "time": 0.447762,
//         "velocity": 0.5905511811023622
//     },
//     {
//         "duration": 0.21175411249999998,
//         "durationTicks": 227,
//         "midi": 76,
//         "name": "E5",
//         "ticks": 720,
//         "time": 0.671643,
//         "velocity": 0.5905511811023622
//     },
//     {
//         "duration": 0.21175411249999998,
//         "durationTicks": 227,
//         "midi": 73,
//         "name": "C#5",
//         "ticks": 960,
//         "time": 0.895524,
//         "velocity": 0.5905511811023622
//     },
//     {
//         "duration": 0.6371280125000001,
//         "durationTicks": 683,
//         "midi": 76,
//         "name": "E5",
//         "ticks": 1200,
//         "time": 1.119405,
//         "velocity": 0.5905511811023622
//     },];
// let cmds = notesToCommands(notes);
// console.log(cmds);
// cmds.sort((a, b) => { a.ticks - b.ticks });
// // console.log(cmds.slice(0, 10));
// let text = mml.commandsToText(cmds);
// console.log(text);
