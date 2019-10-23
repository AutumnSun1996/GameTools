"""
Python Hook

By AutumnSun

"""

from collections import defaultdict

from autopy import bitmap
import PyHook3 as pyhook
import pythoncom
import win32api


class KeyEvent(object):
    """KeyEvent
    """
    def __init__(self, ctrlDown, shiftDown, event):
        self.ctrl = ctrlDown
        self.shift = shiftDown
        self.alt = event.Alt
>>>>>>> a8c89b51872dc8d0349a8741b09e31eb0eb0aa3f
        self.event = event


class KeyBoardManager(object):
    """KeyBoardManager
    """
    mouseKeys = {"LButton", "RButton", "MButton", "WheelDown", "WheelUp"}
    def __init__(self, *args, **kwargs):
        self.ctrlDown = False
        self.shiftDown = False
        self.lastKey = None
        self.keyHooks = defaultdict(dict)
        self.mouseHooks = defaultdict(dict)

        self.hook = PyHook3.HookManager()
        self.hook.KeyDown = self.KeyDown
        self.hook.KeyUp = self.KeyUp
        self.hook.MouseAllButtonsDown = self.KeyDown
        self.hook.MouseAllButtonsUp = self.KeyUp

    def on(self, key, down=None, up=None):
        if down is None and up is None:
            raise ValueError("Must set at least one of down/up")
        if key in self.mouseKeys:
            hooks = self.mouseHooks
        else:
            hooks = self.keyHooks
        if down:
            hooks['down'][key] = down
        if up:
            hooks['up'][key] = up

    def waitKeys(self):
        # 为监控Ctrl、Shift，必须调用HookKeyboard
        self.hook.HookKeyboard()
        # 鼠标Hook可根据需要调用
        if self.mouseHooks:
            self.hook.HookMouse()
        pythoncom.PumpMessages()

    def exit(self, *args):
        win32api.PostQuitMessage()

    def show(self, event):
        print(event.Key)
        for key in event.__dict__:
            print(key, getattr(event, key))
        print()
        return
        print(event.Window)
        print(event.WindowName)
        if event.Key in {'Lshift', 'Rshift', 'Lcontrol', 'Rcontrol', 'Lmenu', 'Rmenu'}:
            print(event.Key, event.KeyID, event.ScanCode)
            print()
            return
        text = ''
        if self.ctrlDown:
            text += 'Ctrl+'
        if self.shiftDown:
            text += 'Shift+'
        if event.Alt:
            text += 'Alt+'
        print(text + event.Key, event.KeyID, event.ScanCode)
        print()

    def KeyDown(self, event):
        if event.Key in {'Lshift', 'Rshift'}:
            self.shiftDown = event.Key
        elif event.Key in {'Lcontrol', 'Rcontrol'}:
            self.ctrlDown = event.Key

        if event.KeyID in self.keyHooks['down']:
            return self.keyHooks['down'][event.KeyID](event)
        elif event.Key in self.keyHooks['down']:
            return self.keyHooks['down'][event.Key](event)

        print("Down")
        self.show(event)
        if event.Key == 'Return':
            self.exit()
        return True

    def KeyUp(self, event):
        if event.Key in {'Lshift', 'Rshift'}:
            self.shiftDown = False
        elif event.Key in {'Lcontrol', 'Rcontrol'}:
            self.ctrlDown = False
        print("Release")
        self.show(event)
        return True

if __name__ == "__main__":
    manager = KeyBoardManager()
    manager.on("Capslock", print)
    manager.on("Escape", manager.exit)
    manager.on("Escape", manager.show)

    manager.on("Capslock", print)
    manager.waitKeys()
    # print(help(key))
    # screen = bitmap.capture_screen()
    # screen.save('screen.png')
