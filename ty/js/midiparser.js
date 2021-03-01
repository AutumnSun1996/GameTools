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
const MAX_UNIT = 128;
const UNITS = [];
for (let i = MAX_UNIT; i >= 1; i = i / 2) {
    UNITS.push(i);
}

function getDivide(n) {
    let left = n;
    let res = [];
    let prev = null;
    for (let i = 0; i < UNITS.length;) {
        let u = UNITS[i];
        if (left >= u) {
            if (prev && prev.duration === u * 2) {
                prev.dot = true;
                prev = null;
            } else {
                prev = { duration: u, divide: MAX_UNIT / u };
                res.push(prev);
            }
            left -= u;
        } else {
            ++i;
        }
    }
    return res;
}

function midiTrackToCommands(track, posOffset = 0) {
    let state = initState();
    let commands = [];
    let ignoreCount = { total: 0 };
    for (let i = 0; i < track.length; ++i) {
        let evt = track[i];
        let chl = state.channels[evt.channel];
        let pos = posOffset + i;
        state.time += evt.deltaTime;
        console.debug("handle", pos, evt);

        function handleNoteOff(e) {
            let key = e.noteNumber.toString();
            let note = chl.notes[key];
            if (!note) {
                console.warn("无对应的按下事件", e);
                return;
            }
            note.hold = state.time - note.timestamp;
            commands.push(note);
            delete chl.notes[key];
        }
        switch (evt.type) {
            case "noteOn":
                let key = evt.noteNumber.toString();
                if (evt.velocity === 0) {
                    handleNoteOff(evt);
                } else {
                    if (chl.notes[key]) {
                        console.warn("重复的按下事件", evt, chl.notes[key], state.time);
                    }
                    chl.notes[key] = {
                        type: "note",
                        noteNum: evt.noteNumber,
                        timestamp: state.time,
                        vel: evt.velocity,
                        pos,
                    }
                }
                break;
            case "noteOff":
                handleNoteOff(evt);
                break;
            case "trackName":
            case "instrumentName":
                commands.push({
                    type: "text", text: `\n#${evt.type} ${evt.text}\n`,
                    timestamp: state.time,
                    pos,
                });
                break;
            case "setTempo":
                commands.push({
                    type: "tempo",
                    value: Math.round(60000000 / evt.microsecondsPerBeat),
                    pos,
                });
                break;
            case "controller":
            case "endOfTrack":
            default:
                if (!ignoreCount[evt.type]) {
                    ignoreCount[evt.type] = 0;
                }
                ++ignoreCount[evt.type];
                ++ignoreCount['total'];
                console.debug("ignore event", state.time, evt,);
        }
    }
    commands.sort((a, b) => { return a.pos - b.pos });
    if (ignoreCount.total > 0) {
        console.log("已忽略:", ignoreCount);
    }
    return commands;
}


/**
 * 
 * @param {Array} cmds 
 * [
 *   { type: "rest", ticks: 0 },
 *   {      
 *     type: "note",
 *     noteNum: 48,
 *     timestamp: 120,
 *     hold: 120
 *   }
 * ]
 * @param {*} ticksPerBeat 
 * @param {*} quantize 
 */
function rebuildCommands(cmds, ticksPerBeat = 480) {
    let commands = [];
    let group = { time: 0, notes: [] };
    let minDuration = ticksPerBeat / (MAX_UNIT / 4);

    function getNoteDuration(note, wantedDuration) {
        let duration = note.durationTicks;
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

    function pushNote(note, force = false) {
        console.debug("pushNote", note);
        if (note.duration < minDuration) {
            if (note.duration > minDuration / 2 || force) {
                console.warn("延长过短的音符", note, minDuration);
                note.duration = minDuration;
            } else {
                console.warn("忽略过短的音符", note, minDuration);
                return false;
            }
        }
        let divides = getDivide(note.duration * (MAX_UNIT / 4) / ticksPerBeat);
        if (divides.length === 0) {
            console.log("push", note, ticksPerBeat, divides);
        }
        divides[divides.length - 1].end = true;

        // 检查是否需要更新 vel
        if (note.type === "note" && note.velocity !== commandState.vel) {
            commands.push({ type: 'vel', value: evt.velocity, ticks: note.ticks });
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
        return true;
    }
    function pushGroup(wantedDuration) {
        // 音符开始时间改变
        // 找到结束时间等于新的时间的音符, 或者添加对应的rest
        let mainNote = { duration: 0, ticks: group.time };
        // 最后一次调用, wantedDuration将为null
        if (wantedDuration === null) {
            if (group.notes.length === 0) {
                // 最后一次调用且无数据, 直接返回
                return;
            }
            mainNote = group.notes[0];
        }
        for (let n of group.notes) {
            n.duration = getNoteDuration(n, wantedDuration);
            // 当前音符更符合需求, 设置当前音符为主音符
            if (wantedDuration && wantedDuration >= n.duration && n.duration > mainNote.duration) {
                mainNote = n;
            }
        }

        // console.log("pushGroup", mainNote, group);
        mainNote.is_chord = false;
        // 添加和弦音符
        for (let note of group.notes) {
            if (note.is_chord) {
                pushNote(note);
            }
        }
        let forcePush = true;
        // 添加主音符
        if (mainNote.duration > 0) {
            if (pushNote(mainNote)) {
                forcePush = false;
            }
        } else {
            console.warn("和弦无主音符", group, wantedDuration);
        }
        // 补充休止符
        if (wantedDuration && mainNote.duration < wantedDuration) {
            pushNote({ type: 'rest', duration: wantedDuration - mainNote.duration, ticks: mainNote.ticks }, forcePush);
        }
    }
    for (let cmd of cmds) {
        if (cmd.type !== "note") {
            commands.push(cmd);
            continue;
        }
        let n = {
            midi: cmd.noteNum,
            ticks: cmd.timestamp,
            durationTicks: cmd.hold,
            is_chord: true,
        }
        if (!n.durationTicks) {
            console.warn("音符时长有问题", cmd, n);
        }
        if (n.durationTicks === 0) {
            console.warn("音符时长为0", cmd);
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
    let state = { total: 0, min: 127, max: 0, };
    for (let cmd of commands) {
        if (cmd.type !== "note") {
            continue;
        }
        ++state.total;
        state.min = Math.min(cmd.noteNum, state.min);
        state.max = Math.max(cmd.noteNum, state.max);
    }
    if (state.total === 0) {
        return { total: 0 };
    }
    state.minNote = numToNote(state.min);
    state.maxNote = numToNote(state.max);
    return state;
}

if (module) {
    module.exports = {
        commandStats,
        rebuildCommands,
        midiTrackToCommands,
    }
}