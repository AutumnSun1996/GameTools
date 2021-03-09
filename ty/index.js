"use strict";

const fs = require('fs');
const path = require('path');
const { parseMidi } = require('midi-file');
const { midiTrackToCommands, rebuildCommands, commandStats } = require('./js/midiparser.js');
const { commandsToText, commandsToNotes, textToCommands } = require('./js/mmlparser.js');

console.debug = function () { };

function midiToMML(data) {
    let parsed = parseMidi(data);
    let result = [];
    let stats = [];
    console.log("基本信息", parsed.header);
    for (let track of parsed.tracks) {
        let cmds = midiTrackToCommands(track);
        stats.push(commandStats(cmds));
        alignCommands(cmds, parsed.header.ticksPerBeat / 16);
        cmds = rebuildCommands(cmds, parsed.header.ticksPerBeat || 480);
        stats.push(commandStats(cmds));
        let text = commandsToText(cmds);
        result.push(text);
    }
    console.log(stats);
    let mml = result.join("\n#NewTrack\n")
    mml = mml.replace(/\n+/g, "\n").replace(/^\n+/, "");
    return mml;
}

function convertMidiFile(midiPath) {
    console.log("处理", midiPath);
    let file = path.parse(midiPath);
    let newPath = path.join(file.dir, file.name + ".mml");
    if (fs.existsSync(newPath)) {
        console.log("已存在, 跳过");
        return;
    }
    let input = fs.readFileSync(midiPath);
    let result = `#Title ${file.name}\n` + midiToMML(input);
    console.log("已写入到", newPath);
    fs.writeFileSync(newPath, result);
}

function addTick(cmds, delDelta = true) {
    // 为每个事件添加绝对时间
    let tick = 0;
    for (let cmd of cmds) {
        tick += cmd.deltaTime;
        cmd.tick = tick;
        if (delDelta) {
            delete cmd.deltaTime;
        }
    }
}

function addDeltaTick(cmds, sort = true) {
    // 为每个事件添加绝对时间
    if (cmds.length === 0) {
        return;
    }
    if (sort) {
        cmds.sort((a, b) => { return a.tick - b.tick });
    }
    cmds[0].deltaTime = 0;
    for (let i = 0; i < cmds.length - 1; ++i) {
        cmds[i + 1].deltaTime = cmds[i + 1].tick - cmds[i].tick;
    }
}

function alignCommands(cmds, grid = 30) {
    console.log("alignCommands", grid);
    for (let cmd of cmds) {
        for (let key of ['timestamp']) {
            if (cmd[key] % grid) {
                let origin = cmd[key];
                cmd[key] = Math.round(cmd[key] / grid) * grid;
                console.log("align", origin, cmd[key]);
            }
        }
    }
}

function mergeTracks(tracks, align = false) {
    let mergedTrack = [];
    for (let t of tracks) {
        addTick(t);
        mergedTrack.push(...t);
    }
    if (align) {
        alignCommands(mergedTrack, align);
    }
    addDeltaTick(mergedTrack);
    return mergedTrack;
}

function midiToSingleMML(data) {
    let parsed = parseMidi(data);
    let ts = parsed.tracks;
    let cmds = [];
    console.log("基本信息", parsed.header);
    let track = mergeTracks([ts[3]], parsed.header.ticksPerBeat / 4)
    console.log(track);
    cmds = midiTrackToCommands(track);
    cmds = rebuildCommands(cmds, parsed.header.ticksPerBeat || 480);
    let mml = commandsToText(cmds);
    mml = mml.replace(/\n+/g, "\n").replace(/^\n+/, "");
    return mml;
}

function main() {
    let data = fs.readFileSync("midi/There is a reason.mid");

    let parsed = parseMidi(data);
    let result = [];
    let stats = [];
    console.log("基本信息", parsed.header);
    for (let track of parsed.tracks) {
        let cmds = midiTrackToCommands(track);
        stats.push(commandStats(cmds));
        console.log(cmds.slice(cmds.length - 5));
        alignCommands(cmds, parsed.header.ticksPerBeat / 16);
        console.log(cmds.slice(cmds.length - 5));
        cmds = rebuildCommands(cmds, parsed.header.ticksPerBeat || 480);
        stats.push(commandStats(cmds));
        let text = commandsToText(cmds);
        result.push(text);
    }
    console.log(stats);
    return;
    let mml = result.join("\n#NewTrack\n")
    mml = mml.replace(/\n+/g, "\n").replace(/^\n+/, "");

    console.log(mml);
}


// const baseDir = "E:\\Documents\\Documents\\MuseScore3\\乐谱";
const baseDir = "midi";

for (let name of fs.readdirSync(baseDir)) {
    if (!/.mid/.test(name)) {
        continue;
    }
    console.log(name);
    convertMidiFile(path.join(baseDir, name));
}

// main();

// function mergeCommands(commands) {
//     let ticksPerBeat = 480;
//     let state = { timestamp: 0, tempo: 120 };
//     let prevNoteNum = null, prevDuration = 0;
//     let notes = [];
//     for (let cmd of commands) {
//         cmd.timestamp = state.timestamp;
//         if (cmd.type === "rest") {
//             let duration = 240 / cmd.divide;
//             state.timestamp += duration;
//         } else if (cmd.type === "note") {
//             let evt = { noteNum: cmd.noteNum, timestamp: state.timestamp, vel: state.vel };
//             evt.duration = ticksPerBeat / cmd.divide;
//             if (cmd.dots) {
//                 evt.duration = evt.duration * Math.pow(1.5, cmd.dots);
//             }
//             if (prevNoteNum !== null) {
//                 if (prevNoteNum !== evt.noteNum) {
//                     throw SyntaxError(`相连的音符必须相同: ${prevNoteNum} ${evt.noteNum}`);
//                 }
//                 evt.duration = evt.duration + prevDuration;
//             }
//             if (cmd.is_prefix) { // '&'
//                 prevNoteNum = evt.noteNum;
//                 prevDuration = evt.duration;
//             } else {
//                 prevNoteNum = null;
//                 prevDuration = null;
//                 if (!cmd.is_chord) { // 和弦不增加当前时间戳
//                     state.timestamp += evt.duration;
//                 }
//             }
//         } else if (cmd.type === "newtrack") {
//             state = { timestamp: 0, tempo: 120 };
//         } else if (cmd.type === "tempo") {
//             state.tempo = cmd.value;
//         }
//     }
//     return commands;
// }

// let text = fs.readFileSync("midi/新闻联播-片头.mml").toString();
// let commands = textToCommands(text);

// // console.log(commands);
// getCommandsTicks(commands);
// commands.sort((a, b)=>{return a.timestamp - b.timestamp});
// // console.log(commands);

// let cmds = rebuildCommands(commands);
// console.log(commandsToText(cmds));

// console.log(mml.commandsToText([{ type: "note", noteNum: 76, divide: 4 }]))

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
