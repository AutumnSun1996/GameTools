#SingleInstance force
SetTitleMatchMode, 3
#include MultiTimer.ahk

#If
^p::GetStatus(true, -1)

^l::Send, qsy19960105{Enter}

#If (UseSkillLimit) and WinActive("Warframe")
^Enter::
ShowTip("技能限制 Off")
UseSkillLimit := false
Return

4::
Requied := 10100
If (not LastClick) {
    LastClick := 0
}
Waiting := Requied - A_TickCount + LastClick
If (Waiting < 0)
{
    Send, 4
    LastClick := A_TickCount
    gosub, ClearTip
    Return
}
ShowTip("技能限制中" Waiting, -1)
Return

#If (not UseSkillLimit) and WinActive("Warframe")
^Enter::
ShowTip("技能限制 On")
UseSkillLimit := true
Return

#IfWinActive Warframe
^+v::Send, % UStr(Clipboard)

UStr(Text){
    UnicodeText := ""
    InCommand := False
    Loop, Parse, Text, 
    {
        Char := A_LoopField
        If (InCommand){
            If (Char = "}"){
                InCommand := False
            }
            UnicodeText := UnicodeText . Char
        } Else {
            If (Char = "{"){
                InCommand := True
                UnicodeText := UnicodeText . Char
            } Else {
                UnicodeText := UnicodeText . Format("{{}U+{:04X}{}}", Ord(Char))
            }
        }
    }
    Return UnicodeText
}

NumpadDot::MButton

*^g::
SetBatchLines, -1
Sleep, 300
SendInput, {LCtrl Down}
Sleep, 200
Wait := [400, 120, 500, 120, 490, 130, 400, 110]
ddt := 0

SendInput, x
for idx, dt in Wait
{
    ; ToolTip, %idx%-%dt%-%ddt%
    ; ddt := dt - TRandSleep(dt - ddt, 10)
    Sleep, dt
    SendInput, {Space}
}
SetBatchLines, 10ms
ToolTip,
Sleep, 2000
SendInput, {LCtrl Up}
Return

^h::
Loop, 10
{
    Send, {LCtrl Down}
    TRandSleep(80)
    Send, {LCtrl Up}
    TRandSleep(110)
}
Return

*WheelUp::
If (!LastWheelUp){
    ShowTip("Bullet Jump")
    Send, ^{Space}
    LastWheelUp := 1
    SetTimer, ClearWheelUp, 800
} Else If (LastWheelUp = 1) {
    ShowTip("Second Jump")
    Send, {Space}
    LastWheelUp := 2
    SetTimer, ClearWheelUp, 800
} Else If (LastWheelUp = 2){
    ShowTip("Shift")
    Send, {Shift}
    LastWheelUp := 0
}
Return

ClearWheelUp:
SetTimer, ClearWheelUp, Off
LastWheelUp := ""
ToolTip, 
Return

*WheelDown::
; Send, {MButton}
; ToolTip, Slide
Send, ^e
Return

Hold(key, dt){
    ; ShowTip("Hold:" . key . "-" . dt)
    Start := A_TickCount
    Send, {%key% Down}
    TRandSleep(dt)
    Send, {%key% Up}
    Elapsed := A_TickCount - Start
    Return Elapsed
}

SendStroke(key, CtrlFirst)  {
    Send,{LControl Down}
    RandSleep(5, 60)
    Send,{%key% Down}
    Used := RandSleep(50, 200)
    Random,rand,0,100
    if (CtrlFirst > rand)
    {
        Send,{LControl Up}
        Used := Used + RandSleep(5, 100)
        Send,{%key% Up}
    }
    else
    {
        Send,{%key% Up}
        Used := Used + RandSleep(5, 100)
        Send, {LControl Up}
    }
    Return Used
}

