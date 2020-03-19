#SingleInstance force
SetTitleMatchMode, 3

#IfWinActive Warframe
^r::
ToolTip, Reload
Sleep, 200
Reload
Return

NumpadSub::
Wait := 400
WaitHalf := Wait / 2
; 确认
Send, {Enter}
Sleep, %Wait%
MouseMove, 400, 600, 5
Sleep, %Wait%
; 选择mod
Click
Sleep, %Wait%
; 数量4
Send, {BackSpace}
Sleep, %Wait%
Send, 4
Sleep, %Wait%
Send, {Enter}
Sleep, %Wait%
; 选择融合
MouseMove, 710, 350, 5
Sleep, %Wait%
Click
Sleep, %Wait%
Send, {Enter}
Return