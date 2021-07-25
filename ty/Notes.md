MidiShow 直接提取midi文件

打开需提取的midi文件页面

添加Hook:

```js
const original = JZZ.MIDI.SMF.prototype.load;
JZZ.MIDI.SMF.prototype.load = function (){
    var args = Array.prototype.slice.call(arguments, 0);
    var obj = this;
    console.log("JZZ.MIDI.SMF.prototype.load called");
    console.log(btoa(arguments[0]));
    return original.apply(obj,args);
};
```
点击播放按钮，文件内容将以Base64格式输出到控制台。

debugger 方案(原始方案)

搜索js中的`new JZZ.MIDI.SMF`, 设置断点。

点击播放按钮，此时将会在断点处暂停。

传入该构造器的内容`a(e[0].substr(28, 28), n) + a(t[0], n) + a(e[0].substr(0, 28), n)`即为解密后的midi文件数据。

可以通过函数 `btoa` 以 base64 格式输出到控制台。
```js
btoa(a(e[0].substr(28, 28), n) + a(t[0], n) + a(e[0].substr(0, 28), n));
```



通过mml尽量还原midi效果:

1. 转换:
    Midi Track -> 音符开始时间+持续时间
    音符开始时间+持续时间 -> 音符并发&
    音符 -> MML文本


Notes

Groups

```
--__--__--
__--__--__
```

track0
track1
track2

track0.last_group
