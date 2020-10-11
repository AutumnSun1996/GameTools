#SingleInstance force
SetTimer, CheckGameStatus, 1000

#include CommonFunctions.ahk

CheckGameStatus:
If (not WinActive("Warframe")){
    UpdateGameStatus("Not Active")
    Return
}

MouseGetPos, X, Y
CursorColor := ColorMatches(X, Y, 0xF3F3F3)
If (CursorColor){
    UpdateGameStatus("Using Cursor")
    Return
}

BloodBar := ColorMatches(1895, 92, 0x2827B7, 5) or ColorMatches(1895, 92, 0x505050, 5)
If (BloodBar){
    UpdateGameStatus("In Mission" BloodBar EnergyStar)
    Return
}

UpdateGameStatus("In Game")
Return

ColorMatches(X, Y, Color, Variant:=10){
    global GameStatus
    PixelSearch, tmpX, tmpY, X, Y, X, Y, Color, Variant
    Result := !ErrorLevel
    PixelGetColor, OutputVar, X, Y
    ShowTip(GameStatus "; ColorMatches: " X "x" Y ": " OutputVar  " with " Color " : " Result)
    Return Result
}
UpdateGameStatus(Status){
    global GameStatus, LastStatusChange, StatusMeets
    if (LastStatusChange = Status){
        StatusMeets := StatusMeets + 1
    } Else {
        StatusMeets := 0
        LastStatusChange := Status
    }
    If (GameStatus != Status and StatusMeets > 1){
        text = Update GameStatus From: "%GameStatus%" To "%Status%"
        ; ShowTip(text, 1000)
        GameStatus := Status
    }
}