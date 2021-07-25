#SingleInstance, Force
SendMode Play
SetWorkingDir, %A_ScriptDir%

SetTimer, PressKeys, 200

PressKeys:
    If(Active){
        Send, 1
    }
Return

*^t::
    If(Active){
        Active := 0
    } Else {
        Active := 1
    }
    ToolTip, Active=%Active%, 5, 5
Return