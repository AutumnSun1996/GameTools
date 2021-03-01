
function midiTrackToMidiCommands(cmds) {
    // 将 noteOn 与 noteOff 进行合并
    addTick(cmds, true);

    let channels = [];
    for (let i = 0; i < 16; ++i) {
        channels.push({});
    }
    let res = [];
    for (let cmd of cmds) {
        switch (cmd.type) {
            case "noteOn":
                if (channels[cmd.channel][cmd.noteNumber]) {
                    console.warn("重复的noteOn", channels[cmd.channel][cmd.noteNumber], cmd);
                } else {
                    channels[cmd.channel][cmd.noteNumber] = cmd;
                    res.push(cmd);
                }
                break;
            case "noteOff":
                let onCmd = channels[cmd.channel][cmd.noteNumber];
                if (onCmd) {
                    onCmd.durationTicks = cmd.tick - onCmd.tick;
                    delete channels[cmd.channel][cmd.noteNumber];
                } else {
                    console.warn("无效的noteOff", channels[cmd.channel][cmd.noteNumber], cmd);
                }
                break;
            default:
                res.push(cmd);
        }
    }

    let validRes = [];
    for (let cmd of cmds) {
        if (cmd.type === "note" && !cmd.durationTicks) {
            console.log("未结束的note", cmd);
        } else {
            validRes.push(cmd);
        }
    }
    return validRes;
}

function insertCommand(cmds, cmd) {
    let i = cmds.length;
    for (; i > 0 && cmds[i - 1].tick > cmd.tick; --i) { }
    console.log(i)
    cmds.splice(i, 0, cmd);
}


function midiCommandsToMidiTrack(cmds) {
    // 将 note 分离成 noteOn 与 noteOff
    let res = [];
    for (let cmd of cmds) {
        if (cmd.type === "note") {
            insertCommand(res, {
                type: "noteOn",
                noteNumber: cmd.noteNumber,
                channel: cmd.channel || 0,
                tick: cmd.tick,
            });
            insertCommand(res, {
                type: "noteOff",
                noteNumber: cmd.noteNumber,
                channel: cmd.channel || 0,
                tick: cmd.tick + cmd.durationTicks,
            });
        } else {
            insertCommand(res, cmd);
        }
    }
    return res;
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
    for (let i = 0; i < cmds.length - 1; ++i) {
        cmds[i + 1].deltaTime = cmds[i + 1].tick - cmds[i].tick;
    }
}

function midiTrackToMidiCommands(track, posOffset = 0) {
    let midiCommands = [];

}
/*
{
    // Common
    type: 'tempo',

    // Midi
    microsecondsPerBeat: 50000,

    // MML
    value: 120,
}
{
    // Common
    type: 'note',
    noteNumber: 48,

    // Midi
    durationTicks: 120,
    tick: 0,

    // Midi Play
    note: 'C4',
    time: 0,
    duration: 0.2,

    // MML
    divide: 4,
    dot: 0,
    is_chord: true,
}
{
    // MML Only
    type: 'rest',
    divide: 4,
    dot: 0
}
*/

