"""
Python Hook

By AutumnSun

"""

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
        self.event = event


class KeyBoardManager(object):
    """KeyBoardManager
    """
    def __init__(self, *args, **kwargs):
        self.ctrlDown = False
        self.shiftDown = False
        self.lastKey = None
        self.keyHooks = {'down': {}, 'press': {}, 'up': {}}

        self.hook = pyhook.HookManager()
        self.hook.KeyDown = self.KeyDown
        self.hook.KeyUp = self.KeyUp
        self.hook.HookKeyboard()

    def on(self, key, down=None, press=None, up=None):
        if down:
            self.keyHooks['down'][key] = down
        if press:
            self.keyHooks['press'][key] = press
        if up:
            self.keyHooks['up'][key] = up

    def waitKeys(self):
        pythoncom.PumpMessages()

    def exit(self):
        win32api.PostQuitMessage()

    def show(self, event):
        for key in event.__dict__:
            print(key, getattr(event, key))
        print()
        return
        print(event.Window)
        print(event.WindowName)
        if event.Key in {'Lshift', 'Rshift', 'Lcontrol', 'Rcontrol', 'Lmenu',
                         'Rmenu'}:
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

        if event.KeyID in self.keyHooks['press']:
            return self.keyHooks['press'][event.KeyID](event)

        print("Press")
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
    manager.waitKeys()
    # print(help(key))
    screen = bitmap.capture_screen()
    screen.save('screen.png')
