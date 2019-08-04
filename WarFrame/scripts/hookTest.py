"""
Python Hook

By AutumnSun
"""
import PyHook3 as pyhook
from collections import defaultdict
import pythoncom
import win32con as C
import win32api

import config


class KeyEvent(object):
    """KeyEvent
    """

    def __init__(self, ctrlDown, shiftDown, event):
        self.ctrl = ctrlDown
        self.shift = shiftDown
        self.alt = event.Alt
        self.event = event


class MyHookManager(object):
    """KeyBoardManager
    """

    def __init__(self):
        self.keyState = {}
        self.keyHooks = {
            'down': defaultdict(list),
            'press': defaultdict(list),
            'up': defaultdict(list),
            'mouse': defaultdict(list),
        }

        self.hook = pyhook.HookManager()
        self.hook.KeyAll = self.checkKeyEvent
        self.hook.MouseAll = self.checkMouseEvent

    def onKey(self, key, actions, funcs):
        if not isinstance(actions, (tuple, list, set)):
            actions = [actions]
        if not isinstance(funcs, (tuple, list, set)):
            funcs = [funcs]

        for action in actions:
            for func in funcs:
                self.keyHooks[action][key].append(func)

    def waitKeys(self):
        self.hook.HookKeyboard()
        if self.keyHooks["mouse"]:
            print("Hook mouse")
            self.hook.HookMouse()
        pythoncom.PumpMessages()

    def exit(self):
        win32api.PostQuitMessage()

    def metaKeys(self):
        metaKeys = []
        for name, codes in config.META_KEYS:
            state = False
            for code in codes:
                state = state or self.keyState.get(code)
            if state:
                metaKeys += [name]
        return metaKeys

    def checkKeyEvent(self, event):
        """按键被按下时触发

        判断并执行down/press/up动作
        """
        if event.KeyID in config.EXIT_KEYIDS:
            self.exit()
        lastState = self.keyState.get(event.KeyID)
        curState = event.Message == 256
        self.keyState[event.KeyID] = curState

        if not curState:
            action = "up"
        elif not lastState:
            action = "down"
        else:
            action = "press"
        event.action = action
        event.FullName = "+".join(self.metaKeys() + [event.Key])
        return self.checkEvent(event)

    def checkEvent(self, event):
        if event.FullName in self.keyHooks[event.action]:
            for func in self.keyHooks[event.action][event.FullName]:
                if isinstance(func, dict):
                    args = func.get("args", [])
                    kwargs = func.get("kwargs", {})
                    func = func["func"]
                    ret = func(event, *args, **kwargs)
                else:
                    ret = func(event)
                if not ret:
                    return False

        for func in self.keyHooks[event.action]["*"]:
            ret = func(event)
            if not ret:
                return False
        return True

    def checkMouseEvent(self, event):
        """按键被按下时触发

        判断并执行down/press/up动作
        """
        if config.MOUSE_STOP and event.Position[0] <= 0 and event.Position[1] <= 0:
            self.exit()

        words = event.MessageName.split(" ")
        print(words)
        if words[-1] == "up":
            event.action = "up"
            words.pop()
        elif words[-1] == "down":
            event.action = "down"
            words.pop()
        else:
            event.action = "mouse"
        event.Key = "".join([w.capitalize() for w in words])
        event.KeyID = config.MOUSE_KEY_ID.get(event.Key, -1)

        event.FullName = "+".join(self.metaKeys() + [event.Key])
        return self.checkEvent(event)


def show(event):
    print()
    for key in dir(event):
        if key.startswith("__"):
            continue
        val = getattr(event, key)
        if callable(val):
            continue
        print(f"{key}={val}")
    print()
    return True


def hold(event):
    print("Hold:", event.Key)
    return False


def send_keys(event, *keys):
    show(event)
    print("Send", keys)
    for k in keys:
        win32api.keybd_event(k, 0, 0, 0)
    return False

def send_keys_up(event, *keys):
    show(event)
    print("Send", keys)
    for k in keys:
        win32api.keybd_event(k, 0, C.KEYEVENTF_KEYUP, 0)
    return False


if __name__ == "__main__":
    manager = MyHookManager()
    # manager.on("Capital", show)
    # manager.on("Ctrl+A", show)
    manager.onKey("Alt+Tab", ["down", "up"], show)
    manager.onKey("Alt+Tab", ["down", "press", "up"], hold)
    manager.onKey("Win+Ctrl+Right", ["down", "press", "up"], show)
    manager.onKey("Alt+Tab", ["press"], hold)
    manager.onKey("Ctrl+1", ["down", "press"],
                  {"func": send_keys, "args": [C.VK_NUMPAD0]})
    manager.onKey("P", ["down", "press"],
                  {"func": send_keys, "args": [27]})
    manager.onKey("P", ["up"],
                  {"func": send_keys_up, "args": [27]})
    # manager.onKey("A", ["down", "press"], show)
    manager.onKey("*", ["down", "press", "up"], show)

    manager.waitKeys()
