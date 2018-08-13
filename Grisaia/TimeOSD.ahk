#SingleInstance force


Init:
BackGroundColor = 666666  ; Can be any RGB color (it will be made transparent below).
TextColor = 66CCFF
Gui +LastFound +AlwaysOnTop +Disabled -Caption +ToolWindow  ; +ToolWindow avoids a taskbar button and an alt-tab menu item.
Gui, Color, %BackGroundColor%
Gui, Font, s14  ; Set a large font size (32-point).
Gui, Add, Text, vMyText c%TextColor% R2 w600 ; set size of the window.
WinSet, ExStyle, +0x20 ; 0x20 = WS_EX_CLICKTHROUGH
WinSet, AlwaysOnTop, on
; WinSet, Transparent, 150
; Make all pixels of CustomColor transparent and make the text itself translucent:
WinSet, TransColor, %BackGroundColor% 200
Gui, Show, x2450 y20 NoActivate,  ; NoActivate avoids deactivating the currently active window.
; Gui, Show, x0 y45
SetTimer, ShowTime, 500
SetTimer, IdelCheck, 10000
Return

ShowTime:
WinGetActiveStats, Title, Width, Height, WinX, WinY
; Height := Height + 80 ; 任务栏高度
IsFull := (Width >= A_ScreenWidth and Height >= A_ScreenHeight and WinX <= 0 and WinY <= 0) ; Or 1
; ToolTip, %IsFull%: %Width%x%Height% in %A_ScreenWidth%x%A_ScreenHeight% at %WinX%x%WinY%, 5, 5
If (IsFull) {
    Text := Format("{}`n{}", FillString(TimeStr(), 19), FillString(PowerStr(), 20))
    GuiControl,, MyText, %Text% 
    ; ToolTip, %Text%, 2400, 24
} Else {
    GuiControl,, MyText, 
    ; ToolTip,
}
Return

IdelCheck:
If (not WinActive("ahk_class CoreSystem2")){
    ; ShowTip("Not In Game", 500, 5, 5)
    Return
}
If (A_TimeIdlePhysical > 30 * 60 * 1000){
    ; ToolTip, A_TimeIdlePhysical=%A_TimeIdlePhysical%
    Send, {Space 2}
} Else If (A_TimeIdle > 1 * 60 * 1000){
    ; ShowTip("Moving: " A_TimeIdle, 500, 5, 5)
    MouseGetPos, MouseX, MouseY
    MouseMove, 3000, 500
    MouseMove, 3000, 1000
    MouseMove, MouseX, MouseY
}
Return

TimeStr(){
    Text := A_Hour ":" A_Min ":" A_Sec
    Return Text
}
PowerStr(){
    global LastCheck, PowerStatus
    If (LastCheck and A_TickCount - LastCheck < 10000) {
        Return PowerStatus
    }
    LastCheck := A_TickCount
    VarSetCapacity(SystemPowerStatus, 12, 0)
    res := DllCall("GetSystemPowerStatus", Ptr, &SystemPowerStatus)
    ; https://docs.microsoft.com/zh-cn/windows/desktop/api/winbase/ns-winbase-_system_power_status
    ACLine := NumGet(SystemPowerStatus, 0, "Char")
    ; Flag := NumGet(SystemPowerStatus, 1, "UChar")
    Percent := NumGet(SystemPowerStatus, 2, "UChar")
    ; SysFlag := NumGet(SystemPowerStatus, 3, "UChar")
    LifeTime := NumGet(SystemPowerStatus, 4, "Int")
    ; LifeFullTime := NumGet(SystemPowerStatus, 8, "Int")
    If (ACLine){
        PowerStatus := Format("充电中({}%)", Percent)
    } Else {
        PowerStatus := Format("{}({}%)", Time2Str(LifeTime), Percent)
    }
    Return PowerStatus
}
Time2Str(secs){
    If (secs <= 0){
        Return ""
    }
    min := Mod(secs // 60, 60)
    hour := secs // 3600
    If (hour > 0){
        Text :=  Format("剩余{}小时{}分", hour, min)
    } Else {
        Text :=  Format("剩余{}分", min)
    }
    Return Text
}
FillString(Text, Size, With:=" "){
    Need := Size - StrWidth(Text)
    If (Need > 0){
        Text := Format("{:" Need "}{}", "", Text)
    }
    Return Text
}
StrWidth(Text){
    width := 0
    Loop, Parse, Text
    {
        If (Ord(A_LoopField) < 0x7F) {
            width := width + 1
        } Else {
            width := width + 2
        }
    }
    Return width
}

^r::
If (WinExist("ahk_class CoreSystem2")){
    WinActivate, ahk_class CoreSystem2
} Else {
    ToolTip, Opening...
    Run, "D:\Games\EN-The Fruit of Grisaia.lnk"
    WinWait, ahk_class CoreSystem2, , 5
    ToolTip, 
    SwitchIME()
    Loop, 5
    {
        Sleep, 1000
        Click, 400, 400
    }
    Sleep, 4000
    LoadSave()
}
Return

; 0x04090409 英语(美国) 美式键盘
SwitchIME(dwLayout:=0x04090409){
    HKL:=DllCall("LoadKeyboardLayout", Str, dwLayout, UInt, 1)
    ControlGetFocus,ctl,A
    SendMessage,0x50,0,HKL,%ctl%,A
}


LoadSave(){
    WinActivate, ahk_class CoreSystem2
    Sleep, 500
    
    ; Continue
    MouseMove, 1341, 1224
    Sleep, 100
    Send, {Enter}
    Sleep, 1500
    
    ; Auto Saves
    MouseMove, 2562, 268
    Sleep, 100
    Send, {Enter}
    Sleep, 1000
    
    ; 180, 370 To ~, 1550
    ; 1560, 370 To ~, 1550
    PixelSearch, PosX, PosY, 180, 370, 180, 1550, 0xD2783D, 50, Fast
    If (ErrorLevel){
        PixelSearch, PosX, PosY, 1560, 370, 1560, 1550, 0xD2783D, 50, Fast
    }
    MouseMove, PosX, PosY
    Sleep, 100
    Send, {Enter}
    
    MouseMove, 3000, 1000
}

#If WinActive("ahk_class CoreSystem2")
Right::WheelDown
LCtrl::ShowTip("Force Skip Disabled")

; NumLk:None /:Esc *:QuickSave -:QuickLoad
; 7:Auto+ 8:Auto- 9:None +:BackLog
; .......................
; ....................... Enter:Next
; 0:ToggleGUI ............


NumpadDiv::Esc
NumpadMult::F1  ; QuickSave
NumpadSub::F2   ; QuickLoad
Numpad0::Space  ; Toggle UI

NumpadAdd::WheelUp
NumPadEnter::WheelDown

MButton::F4     ; Auto Speed +
Numpad7::F4     ; Auto Speed +
Numpad8::F5     ; Auto Speed -
Numpad9::F3

Numpad6::PgUp
Numpad3::PgDn

~RButton & WheelUp::Volume_Up
~RButton & WheelDown::Volume_Down

LButton::
MouseGetPos, PosX, PosY
If (PosY < 150) {
    Send, {WheelUp}
} Else If (PosY > 1770){
    Send, {WheelDown}
} Else {
    Click
}
Return

p::GetStatus(-1)

GetStatus(ShowNow:=500){
	MouseGetPos, x, y
	WinGetClass, Class, A
	WinGetActiveStats, Title, Width, Height, WinX, WinY
	PixelGetColor, Color, x, y, Slow 
    res := WinActive("ahk_class CoreSystem2")
	ReturnText = %res%: Class=%Class% Title=%Title% Pos=%x% %y% in %Width%x%Height% Color=%Color%
	If (ShowNow != 0){
		ShowTip(ReturnText, ShowNow)
	}
	Return ReturnText
}

ShowTip(Tip, Time:=1000, X:="", Y:=""){
    global ToolTipNow
    If (ToolTipNow = Tip) {
        gosub, ClearTip
        Return
    }
	ToolTip, %A_ScriptName%:`n%Tip%, %X%, %Y%
    ToolTipNow := Tip
	If (Time > 0) {
        SetTimer, ClearTip, %Time%
	}
}


ClearTip:
SetTimer, ClearTip, off
ToolTip, 
ToolTipNow := ""
Return