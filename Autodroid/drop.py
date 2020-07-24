from azurlane.common_fight import CommonMap
from simulator.win32_tools import rand_click
import time
import sys

s = CommonMap("Games")
start_time = time.time()
last = {}


def check():
    global last
    name = "HandleMark"
    t = time.time()
    s.make_screen_shot()
    found, pos = s.search_resource(name)
    if not found:
        last = {}
        #         print("Wait...")
        time.sleep(0.1)
        return
    x = pos[0]
    if last:
        speed = (x - last["x"]) / (t - last["t"])
    #         print("Speed", speed)

    last["t"] = t
    last["x"] = x

    if 682 < x < 698:
        #         print("CLICK AT", x)
        rand_click(s.hwnd, (300, 300, 400, 400))
        time.sleep(0.2)
        return True


#     print("Skip AT", x)

n = int(sys.argv[1])
clicked = 0
while clicked < n:
    did = check()
    if did:
        clicked += 1
        print(time.time() - start_time, "Clicked", clicked, n)
