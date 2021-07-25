
function insertCommand(cmds, cmd) {
    let i = cmds.length;
    for (;i > 0 && cmds[i - 1].tick > cmd.tick; --i) {}
    console.log(i)
    cmds.splice(i, 0, cmd);
    console.log(cmds);
}

let a = [];
insertCommand(a, { tick: 0, id: 0 });
insertCommand(a, { tick: 0, id: 1 });
insertCommand(a, { tick: 0, id: 2 });
insertCommand(a, { tick: 3, id: 3 });
insertCommand(a, { tick: 1, id: 4 });
