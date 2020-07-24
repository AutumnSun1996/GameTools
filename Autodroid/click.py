import sys
import time

from simulator.win32_tools import rand_click, get_window_hwnd
from simulator.image_tools import get_all_match
from config_loader import config


def main(section, rows):
    window_title = config.get(section, "WindowTitle")
    hwnd = get_window_hwnd(window_title)

    if not hwnd:
        print("No Such Window")
        return

    x0, y0 = 100, 200
    dx, dy = int(800 / 6), int(430 / 3)
    w, h = 80, 80
    for i in range(7):
        for j in range(rows):
            x, y = (x0 + dx * i, y0 + dy * j)
            rand_click(hwnd, (x, y, x + w, y + h))
            time.sleep(0.3)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        section = sys.argv[1]
    else:
        section = "FGO"

    rows = ""
    while True:
        if rows:
            rows = int(rows)
        else:
            rows = 3
        main(section, rows)
        rows = input("Pause...")
