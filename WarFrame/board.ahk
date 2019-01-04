#SingleInstance force
SetTitleMatchMode, 3

*-::
ToolTip, Reload
Sleep, 200
Reload
Return

*XButton1::
If (KeepUpOn) {
    FileAppend, %A_Now% End`n, board.log
    ToolTip,
    SetTimer, PressSpace, Off
    SetTimer, ADToggle, Off
    If (PressA) {
        Send, {a Up}
    } Else {
        Send, {d Up}
    }
    Send, {w Up}
    Sleep, 50
    Send, {ShiftUp}
    KeepUpOn = 
} Else {
    FileAppend, %A_Now% Start`n, board.log
    ToolTip, KeepGoing, 10, 20
    Send, {w Down}
    Sleep, 100
    Send, {ShiftDown}
    SetTimer, PressSpace, 90
    PressA = 1
    Send, {a Down}
    SetTimer, ADToggle, 700
    KeepUpOn = 1
}
Return


PressSpace:
Random, RandValue, 0, 30
Sleep, %RandValue%
Send, {WheelDown}
Return

ADToggle:
Random, RandValue, 0, 30
Sleep, %RandValue%
If (PressA){
    PressA = 
    Send, {a Up}
    Random, RandValue, 40, 90
    Sleep, %RandValue%
    Send, {d Down}
} Else {
    PressA = 1
    Send, {d Up}
    Random, RandValue, 40, 90
    Sleep, %RandValue%
    Send, {a Down}
}
Return