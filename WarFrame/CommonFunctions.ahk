GetStatus(a, b){

}

ShowTip(text, dt:=500, x:=0, y:=0){
    ToolTip, %text%, %x%, %y%
    if(dt > 0){
        SetTimer, ClearTip, %dt%
    }
}

ClearTip:
SetTimer, ClearTip, off
ToolTip, 
Return

TRand(mean){
    Return mean
}

TRandSleep(mean){
    Sleep, mean
}
RandSleep(a, b){
    mean := (a + b) / 2
    Sleep, mean
}