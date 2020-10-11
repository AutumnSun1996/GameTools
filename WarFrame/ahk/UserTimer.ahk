#SingleInstance force
SetTitleMatchMode, 3

Role := 1
Role := 400

RoleName(){
    global Role
    If (Role = 1)
    {
        Return "Nekros"
    }
    If (Role = 2)
    {
        Return "Nova"
    }
    Return "Whip-" . Role
}

Step := 20

UpdateByNow := False
TimeOut := [30, 20]
If (Role < 3)
{
    RoleTimeOut := TimeOut[Role] * 1000
}
Else
{
    RoleTimeOut := 60 * 1000
}

#include CommonFunctions.ahk

; #IfWinActive WARFRAME

onNormal:
; ShowTip("onNormal", 500)
If (Role < 3)
{
    RandSleep(1000, 3000)
    Return
}
Send, {w Down}
Send, ^e
TRandSleep(Role, Role * 0.15)
Return


onTimeOut:
; ShowTip("onTimeOut", 500)
If (Role > 2)
{
    Send, {w Up}
    TRandSleep(200, 100)
    Send, {Shift Down}
    TRandSleep(200, 100)
; Send, {a Down}
; TRandSleep(200, 100)
    Hold("s", 2000)
    TRandSleep(200, 100)
; Send, {a Up}
; TRandSleep(200, 100)
    Send, {Shift Up}
    TRandSleep(200, 100)
    Send, {w Down}
    Return
}
If (Role = 2)
{
    Send, 4
    TRandSleep(1000, 100)
}
Send, {Shift Down}
TRandSleep(200, 100)
Hold("s", 1600)
TRandSleep(200, 100)
Hold("w", 1800)
TRandSleep(200, 100)
Send, {Shift Up}
Return


Hold(key, dt){
    ; ShowTip("Hold:" . key . "-" . dt)
    Send, {%key% Down}
    dt1 := TRandSleep(dt, dt*0.15)
    Send, {%key% Up}
    Return dt1
}


#MaxThreadsPerHotkey 3
#x::
#MaxThreadsPerHotkey 1
If KeepRunning
{
    KeepRunning := false
    ShowTip("Stopping", 0)
    return
}
KeepRunning := true
StartTime := A_TickCount - RoleTimeOut
If (Role > 2)
{
    Send, {w Down}
    ; StartTime := A_TickCount
}
ShowTip("Start As " . RoleName(), 500)
Loop
{
    Passed := A_TickCount - StartTime
    ShowTip("Check-" . Role . "-" . Passed . "-" . RoleTimeOut . "-" . (Passed > RoleTimeOut), 0)
    If (Passed > RoleTimeOut)
    {
        ; ShowTip("onTimeOut-" . UpdateByNow, 500)
        gosub onTimeOut
        If UpdateByNow
        {
            StartTime := A_TickCount
        }
        Else
        {
            StartTime := StartTime + RoleTimeOut
        }
    }
    Else
    {
        ; ShowTip("onNormal-" . StartTime . "-" . A_TickCount . "-" . UpdateByNow, 500)
        gosub onNormal
    }
}
Until not KeepRunning
If (Role > 2)
{
    Send, {w Up}
}
ShowTip("Stopped", 500)
Return


#If %KeepRunning%

+8::
NumpadMult::Step := Step * 2
/::
NumpadDiv::Step := Step // 2
PgUp::
NumpadAdd::Role := Role + Step
PgDn::
NumpadSub::Role := Role - Step
Numpad0::Step := 20

Right::
Role := Role * 3
ShowTip("Pause for " . Role, Role)
Send, {w Down}
Role := Role // 3
Return
