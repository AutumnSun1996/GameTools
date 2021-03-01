"use strict";

const fs = require('fs');
const path = require('path');
console.debug = function () { };


const { parseMidi } = require('midi-file');
const { midiTrackToCommands, rebuildCommands, commandStats } = require('./midiparser.js');
var mml = require('./js/mmlparser.js');
// Read MIDI file into a buffer
// var input = fs.readFileSync('midi/This game.txt');

// var input = fs.readFileSync('E:\\Documents\\Documents\\MuseScore3\\乐谱\\There is a reason-t1.mid');
// input = atob(input);
// console.log(input.slice(0, 4).toString());
// input = Buffer.from(input.toString(), "base64");
// console.log(input.slice(0, 4).toString());

// Parse it into an intermediate representation
// This will take any array-like object.  It just needs to support .length, .slice, and the [] indexed element getter.
// Buffers do that, so do native JS arrays, typed arrays, etc.
function midiFileToText(midiPath) {
    console.log("处理", midiPath);
    let file = path.parse(midiPath);
    let newPath = path.join(file.dir, file.name + ".mml");
    if (fs.existsSync(newPath)) {
        console.log("已存在, 跳过");
        return;
    }
    let input = fs.readFileSync(midiPath);
    let parsed = parseMidi(input);
    let result = [];
    console.log("基本信息", parsed.header);
    for (let track of parsed.tracks) {
        let cmds = midiTrackToCommands(track);
        cmds = rebuildCommands(cmds, parsed.header.ticksPerBeat);
        console.log(commandStats(cmds));
        let text = mml.commandsToText(cmds);
        result.push(text);
    }
    result = result.join("\n#NewTrack\n")
    result = `#Title ${file.name}\n` + result.replace(/\n+/g, "\n");
    console.log("已写入到", newPath);
    fs.writeFileSync(newPath, result);
}

for (let name of fs.readdirSync("midi")) {
    if (!/.mid/.test(name)) {
        continue;
    }
    console.log(name);
    midiFileToText("midi/" + name);
}

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
