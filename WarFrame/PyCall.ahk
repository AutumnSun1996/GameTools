; test.ahk
#SingleInstance force

cmdReturn(command){
    ; WshShell 对象: http://msdn.microsoft.com/en-us/library/aew9yb99
    shell := ComObjCreate("WScript.Shell")
    ; 通过 cmd.exe 执行单条命令
    exec := shell.Exec(ComSpec " /C " command)
    ; 读取并返回命令的输出
    return exec.StdOut.ReadAll()
}

^=::
ToolTip, %A_Now%.%A_MSec%
dt = %A_Now%.%A_MSec%
RunWait,python.exe MineHelper.py test %dt%,D:\Documents\GameRoutes\WarFrame\scripts,Hide
Sleep, 500
ToolTip,
Return

#IfWinActive Warframe
=::
ToolTip, Start, 5,5
Click, down
RunWait,python.exe MineHelper.py mine %A_Now%.%A_MSec%,D:\Documents\GameRoutes\WarFrame\scripts,Hide
ToolTip, End.
Click, up
Sleep, 500
ToolTip, 
Return

-::
ToolTip, Start.
RunWait,python.exe MineHelper.py shot %A_Now%.%A_MSec%,D:\Documents\GameRoutes\WarFrame\scripts,Hide
ToolTip, End.
Sleep, 500
ToolTip, 
Return
