#SingleInstance force
SetTitleMatchMode, 3
gosub, CheckGameStatus
SetTimer, CheckGameStatus, 200
#include MultiTimer.ahk

#If
^p::GetStatus(true, -1)

^l::
Send, qsy19960105
Sleep, 500
Send, {Enter}
Return

CheckGameStatus:
If (not WinActive("Warframe")){
    UpdateGameStatus("Not Active")
    Return
}

MouseGetPos, X, Y
ImageSearch, OutputVarX, OutputVarY, X-5, Y+8, X+27, Y+40, *20 Cursor.bmp
If (ErrorLevel = 0){
    UpdateGameStatus("Using Cursor")
    Return
}

BloodBar := ColorMatches(1895, 92, 0x2827B7) or ColorMatches(1895, 92, 0x505050)
If (BloodBar){
    UpdateGameStatus("In Mission")
    Return
}

UpdateGameStatus("In Game")
Return

ColorMatches(X, Y, Color, Variant:=10){
    global GameStatus
    PixelSearch, tmpX, tmpY, X, Y, X, Y, Color, Variant
    Result := !ErrorLevel
    ; PixelGetColor, OutputVar, X, Y
    ; ShowTip(GameStatus "; ColorMatches: " X "x" Y ": " OutputVar  " with " Color " : " Result)
    Return Result
}
UpdateGameStatus(Status){
    global GameStatus, LastStatusChange, StatusMeets
    if (LastStatusChange = Status){
        StatusMeets := StatusMeets + 1
        If (GameStatus != Status){
            SetTimer, CheckGameStatus, 200
        }
    } Else {
        StatusMeets := 0
        LastStatusChange := Status
    }
    If (GameStatus != Status and StatusMeets > 2){
        text = Update GameStatus From: "%GameStatus%" To "%Status%"
        ShowTip(text, 2000)
        GameStatus := Status
        SetTimer, CheckGameStatus, 1000
    }
}

#IfWinActive Warframe
PrintScreen::
ShowTip("ScreenShot")
RunWait, pythonw screenAnalyse.py fromAHK, .\scripts
Return

^t::
MouseGetPos, X, Y
ImageSearch, OutputVarX, OutputVarY, X-5, Y+8, X+27, Y+40, *20 Cursor.bmp
ShowTip("ScreenShot" . ErrorLevel)
Return

*XButton1::
If (KeepUpOn) {
    FileAppend, %A_Now% End`n, board.log
    gosub, ClearTip
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
    ShowTip("KeepGoing")
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
Send, {Space}
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

#If (UseSkillLimit) and (GameStatus = "In Mission")
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

#If (not UseSkillLimit) and (GameStatus = "In Mission")
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


#If (GameStatus = "In Mission") or (GameStatus = "In Game")
NumpadDot::MButton

*^g::
; G系破解
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
; 滑砍
Loop, 10
{
    Send, {LCtrl Down}
    TRandSleep(80)
    Send, {LCtrl Up}
    TRandSleep(110)
}
Return

*XButton2::MButton

*WheelUp::
; 跳跃动作
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
    ShiftIsDown := GetKeyState("Shift")
    If(ShiftIsDown){
        Send, {ShiftUp}
        Sleep, 10
        Send, {Shift}
        Sleep, 10
        Send, {ShiftDown}
    }Else{
        Send, {Shift}
    }
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

