; CommonFunctions.ahk
#SingleInstance force

Init:
If (A_ScriptName = "CommonFunctions.ahk"){
    ShowTip("Exit:" . A_ScriptName)
    ExitApp
    Return
}
BackGroundColor = 666666  ; Can be any RGB color (it will be made transparent below).
TextColor = 66CCFF
Gui +LastFound +AlwaysOnTop +Disabled -Caption +ToolWindow  ; +ToolWindow avoids a taskbar button and an alt-tab menu item.
Gui, Color, %BackGroundColor%
Gui, Font, s14  ; Set a large font size (32-point).
Gui, Add, Text, vMyText c%TextColor% R10 W%A_ScreenWidth% ; XX & YY serve to auto-size the window.
WinSet, ExStyle, +0x20 ; 0x20 = WS_EX_CLICKTHROUGH
; WinSet, Transparent, 150
; Make all pixels of CustomColor transparent and make the text itself translucent:
WinSet, TransColor, %BackGroundColor% 200
Gui, Show, x0 y45 NoActivate,  ; NoActivate avoids deactivating the currently active window.
; Gui, Show, x0 y45
ShowTip("Inited")
Return

^q::
ShowTip("Exit:" . A_ScriptName)
ExitApp
Return

GetStatus(ShowNow:=true, Time:=500)
{
	MouseGetPos, x, y
	WinGetClass, Class, A
	WinGetActiveStats, Title, Width, Height, WinX, WinY
	PixelGetColor, Color, x, y, Slow 
	ReturnText = Class=%Class% Title=%Title% Pos=%x% %y% in %Width%x%Height% Color=%Color%
	If (Time != 0)
	{
		ShowTip(ReturnText, Time)
	}
	Return ReturnText
}

ShowTip(Tip, Time:=1000, X:="", Y:="")
{
    global ToolTipNow
    If (ToolTipNow = Tip)
    {
        GuiControl,, MyText, 
        ToolTipNow := ""
        Return
    }
	GuiControl,, MyText, %A_ScriptName%:`n%Tip%
	IfGreater, Time, 0
	{
        SetTimer, ClearTip, %Time%
	}
    Else
    {
        ToolTipNow := Tip
    }
}

ClearTip:
SetTimer, ClearTip, off
GuiControl,, MyText, 
ToolTipNow := ""
Return

ShowToolTip(Tip, Time:=1000, X:="", Y:="")
{
    global ToolTipNow
    If (ToolTipNow = Tip)
    {
        ToolTip,
        ToolTipNow := ""
        Return
    }
	ToolTip, %Tip%, X, Y
	IfGreater, Time, 0
	{
		Sleep, Time
		ToolTip,
	}
    Else
    {
        ToolTipNow := Tip
    }
}

RandSleep(TMin:=100, TMax:=200)
{
    Random, dt, TMin, TMax
    Sleep, dt
    Return dt
}

TRand(Mean, Range:=-1, Smooth:=5)
{
    Result := 0
    If (Range < 0)
    {
        Range := Mean * 0.1
    }
    TMin := (Mean - Range) / Smooth
    TMax := (Mean + Range) / Smooth
    Loop,  %Smooth% 
    {
        Random, dt, TMin, TMax
        Result := Result + dt
    }
    Return Result
}

TRandSleep(Mean, Range:=-1, Smooth:=5)
{
    dt := TRand(Mean, Range, Smooth)
    ; ToolTip % "TRandSleep-" . Mean . "-" . Range . "-" . Smooth . "-" . dt
    Sleep, dt
    Return dt
}
; 0x04090409 英语(美国) 美式键盘
; 0x08040804 中文(中国) 简体中文-美式键盘
SwitchIME(dwLayout:=0x04090409){
    HKL:=DllCall("LoadKeyboardLayout", Str, dwLayout, UInt, 1)
    ControlGetFocus,ctl,A
    SendMessage,0x50,0,HKL,%ctl%,A
}
