"""
音符 "cdefgab"
时值 数字

"o" + Number: 改变音高到 Number
MML@t54l1rrrr.r4l16rv15baf+a8af+a8af+af+e8.baf+a8af+a8an61baa8.ef+>c+c+8c+c-c+8c+c-c+e8c+8c+c+c+c+8c+e8ec+e8ec-32c+32eec+c-c+c+ec+eec+c-c+c+ec+ef+ec+ec+c+c+8e8c+8.eec+c-c+c+ec+eec+c-c+c+ec+ef+ec+ec+c+c+8&c+32c+c+8c+c-c+8c+c-c+e8c+8c+c+c+c+8c+e8ec+e8ec-32c+32eec+c-c+c+ec+eec+c-c+c+ec+ef+ec+ec+c+c+8e8c+8.eec+c-c+c+ec+eec+c-c+c+ec+ef+ec+ec+c+c+8&c+32ffdcdcdfdc4&cffdcdcdfccdfgfdfddcc4&cn58cn58c8.n58c8d8f8d8.ffdcdcdfdc4&cffdcdcdfccdfgfdfddcc8&c32d8&d32c.c8

Music Macro Language:
CDEFGAB	音符。后面跟随着“#”或是“+”作为升记号，-作为降记号。后面跟随着数字或点表示音符时值，如“A+2.”表示升A附点二分音符。
R	休止符。与音符表示法相同，后面跟随的数字或点表示音符长度。
O	指定八度。后面跟随着数字来指定乐器演奏哪个八度。
>、<	控制乐谱高八度或低八度。使用“>”表示乐谱之后为高八度，用“<”表示乐谱之后为低八度。
L	指定音符时值。使用此方式指定如果“A”～“G”或是“R”之后没有接数字的话代表的音符时值为何。常见的预设值为四分音符。如“L4CCCC”表示四个C的四分音符。
V	指定音量大小。后面跟随的数字可指定之后演奏乐器的音量大小。
T	指定乐器的速度。例如“T120”表示以120BPM来演奏

MML输入:

添加音符:

1234567: 添加CDEFGAB音符

0: 添加休止符

+: 升半音
-: 降半音

修改音阶: o+数字

时值: 小键盘数字
2: 1
1: 2
1/2: 3
1/4: 4
1/8: 5
1/16: 6
1/32: 7
1/64: 8
1/128: 9

.: 添加附点

调整时值: 
小键盘*: 翻倍
小键盘/: 减半

"""
