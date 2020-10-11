If (A_ScriptName = "MultiTimer.ahk"){
    Run, Warframe.ahk
    ExitApp
}

#SingleInstance force
SetTitleMatchMode, 3
#include CommonFunctions.ahk


RoleInit:
TipX:=0
TipY:=80
; Test Nova Walk Boom Trinity Whip TrinityJump
Role := Nova()
Step := 20
Return

Test(){
    tmp := {}
    tmp.Name := "Test"
    tmp.Loop := 20
    tmp.Levels := [{"Name": "send4", "Label": "send", "TimeOut": 1500, "ActNow":1 , "Args":[0, "4", 1000]}]
    return tmp
}
Nova(){
    tmp := {}
    tmp.Name := "Nova"
    tmp.Loop := 1000
    tmp.Levels := [{"Name": "send4", "Label": "send", "TimeOut": 19000, "ActNow":1 , "UpdateByNow":1, "Args":[0, "4", 1000]}
        ,{"Label": "moveSW", "TimeOut": 30000, "ActNow": 1}]
    return tmp
}
Walk(){
    tmp := {}
    tmp.Name := "Walk"
    tmp.Loop := 3000
    tmp.Levels := [{"Label": "moveSW", "TimeOut": 30000, "ActNow": 1}]
    return tmp
}
Trinity(){
    tmp := {}
    tmp.Name := "Trinity"
    tmp.Loop := 500
    tmp.Levels := [{"Label": "moveSW", "TimeOut": 30000, "ActNow": 1}
        ,{"Name": "send2", "Label": "send", "TimeOut": 1000, "ActNow":1 , "Args":[0, "2", 0]}]
    return tmp
}
TrinityJump(){
    tmp := {}
    tmp.Name := "TrinityJump"
    tmp.Loop := 1
    tmp.Levels := [{"Name": "send3", "Label": "send", "TimeOut": 1000, "ActNow":1 , "Args":[0, "3", 2000]}
        ,{"Label": "Castanas", "TimeOut": 1, "ActNow": 1, "UpdateByNow": 1, "FixedTimeOut":1}]
    return tmp
}
Whip(DT:=400){
    tmp := {}
    tmp.Name := "Whip" . DT
    tmp.DT := DT
    tmp.Loop := 1
    tmp.is_whip := 1
    tmp.Levels := [{"Label": "moveSW", "TimeOut": 60000}
        ,{"Name": "w Down", "Label": "send", "TimeOut": 5000, "ActNow":1 , "Args":[0, "{w Down}", 0]}
        ,{"Name": "slide", "Label": "send", "TimeOut": 1, "ActNow":1 , "UpdateByNow": 1, "Args":[0, "^e", DT]}]
    return tmp
}

; ShowTip("Init:" . Role . "-" . Role.Name . "-" . Role.Loop . "-" . Role.Levels[1].Name, 500, TipX, TipY)

ShowWaitStatus:
text := Role.Name . "`n"

for idx, lvl in Role.Levels
{
    Left := (TimeOut[idx] - A_TickCount + StartTime[idx])
    Left := (Left > 0) ? Left : 0
    Name := lvl.Name ? lvl.Name : lvl.Label
    text := text . Left . "ms For " . Name "`n"
}
ShowTip(text, 0)
Return

#IfWinActive WARFRAME
send:
TRandSleep(Args[1])
Send, % Args[2]
TRandSleep(Args[3])
Return

Castanas:
Send, {Space}
TRandSleep(300)
Send, {LButton}{MButton}
TRandSleep(100)
Send, {Space}
TRandSleep(300)
Send, {LButton}{MButton}
TRandSleep(1000)
Return

Boom13:  
TRandSleep(500)
Send, {LControl Down}
TRandSleep(270)
Send, {1 Down}
TRandSleep(200)
Send, {LControl Up}
TRandSleep(20)
Send, {1 Up}
TRandSleep(200)
Send, {Space Down}
TRandSleep(50)
Send, {Space Up}
TRandSleep(80)
Send, {RButton Down}
TRandSleep(500)
Send, {e Down}
TRandSleep(400)
Send, {RButton Up}
TRandSleep(400)
SendInput, {e Up}{3 Down}
TRandSleep(100)
Send, {3 Up}
TRandSleep(2000)
Send, {3 Down}
TRandSleep(100)
Send, {3 Up}
Return

Energize:
TRandSleep(1000)
Send, {LShift Down}
TRandSleep(200)
Send, {s Down}
TRandSleep(800)
Send, {s Up}
TRandSleep(300)
Send, {LShift Up}
TRandSleep(100)
Send, 5
TRandSleep(300)
Send, v
TRandSleep(300)
MouseGetPos, x, y
If (y < 1000){
    MouseMove, x, 1200
} Else {
    MouseMove, x, y+10
}
TRandSleep(300)
MouseMove, 0, -6, , R
TRandSleep(300)
Send, {Space}
TRandSleep(300)
Send, 5
TRandSleep(1000)
MouseMove, 0, 10, , R
TRandSleep(300)
MouseMove, 0, -1, , R
Return

moveSW:
TS := Args?Args:2000
Send, {w Up}
TRandSleep(200)
Send, {LShift Down}
TRandSleep(200)
Send, {s Down}
TRandSleep(TS)
Send, {s Up}
TRandSleep(500)
Send, {w Down}
If not Role.is_whip
{
    TRandSleep(TS * 1.1)
    Send, {w Up}
    TRandSleep(500)
}
Send, {LShift Up}
TRandSleep(200)
Return

moveASW:
TS := Args?Args:2000
Send, {w Up}
TRandSleep(200)
Send, {s Down}
TRandSleep(200)
Send, {a Down}
TRandSleep(200)
Send, {LShift Down}
TRandSleep(TS)
Send, {s Up}
TRandSleep(200)
Send, {a Up}
TRandSleep(500)
Send, {w Down}
If not Role.is_whip
{
    TRandSleep(TS * 1.1)
    Send, {w Up}
    TRandSleep(500)
}
Send, {LShift Up}
TRandSleep(200)
Return

#If KeepRunning Or WinActive("WARFRAME")
#MaxThreadsPerHotkey 3
#x::
#MaxThreadsPerHotkey 1
If KeepRunning
{
    KeepRunning := false
    ShowTip("Stopping", 0, TipX, TipY)
    Return
}
KeepRunning := true

If not Role
{
    gosub RoleInit
}
StartTime := {}
TimeOut := {}
for idx, lvl in Role.Levels
{
    StartTime[idx] := A_TickCount
    If lvl.FixedTimeOut
    {
        TimeOut[idx] := lvl.TimeOut
    }
    Else
    {
        TimeOut[idx] := FLoor(TRand(lvl.TimeOut))  ; Random TimeOut
    }
    If (lvl.ActNow)
    {
        StartTime[idx] := A_TickCount - TimeOut[idx]
    }
    ; ShowTip("SetTime: " . lvl.Name . "-" . StartTime[idx], 1000, TipX, TipY)
}

If (Role.is_whip)
{
    Send, {w Down}
}
ShowTip("Start As " . Role.Name, 500, TipX, TipY)
Loop
{
    gosub ShowWaitStatus
    for idx, lvl in Role.Levels     ; Check Each Level, lower Levels will wait for higher Levels.
    {
        Passed := A_TickCount - StartTime[idx]
        If (Passed > TimeOut[idx])
        {
            ; ShowTip("Check-" . Role.Name . "-" . lvl.Name . ":" . lvl.Args . "/" . (Passed > TimeOut[idx]) . "/" . Passed . "/" . TimeOut[idx], 0, TipX, TipY)
            Label := lvl.Label
            Args := lvl.Args
            gosub %Label%
            If lvl.FixedTimeOut
            {
                TimeOut[idx] := lvl.TimeOut
            }
            Else
            {
                TimeOut[idx] := FLoor(TRand(lvl.TimeOut))  ; Random TimeOut
            }
            If lvl.UpdateByNow
            {
                StartTime[idx] := A_TickCount
            }
            Else
            {
                While (StartTime[idx] + lvl.TimeOut < A_TickCount){
                    StartTime[idx] := StartTime[idx] + lvl.TimeOut
                }
                
            }
        }
        Else
        {
            TRandSleep(Role.Loop)
        }
        If not KeepRunning
        {
            Break
        }
    }
}
Until not KeepRunning
If (Role.is_whip)
{
    Send, {w Up}
}
ShowTip("Stopped", 500, TipX, TipY)
Return

#If (Role.is_whip and KeepRunning)
+8::
NumpadMult::Step := Step * 2
/::
NumpadDiv::Step := Step // 2
PgUp::
NumpadAdd::Role := Whip(Role.DT + Step)
PgDn::
NumpadSub::Role := Whip(Role.DT - Step)
0::
Numpad0::Step := 20

Right::
Role := Whip(Role.DT * 3)
ShowTip("Pause for " . Role.DT, Role.DT, TipX, TipY)
Send, {w Down}
Role := Whip(Role.DT // 3)
Return
