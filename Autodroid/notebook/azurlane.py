from .common import *

from azurlane.common_fight import FightMap

const["section"] = "azurlane"


def check_map_anchor(anchor):
    s = const["s"]
    if isinstance(anchor, str):
        anchor = s.data["Anchors"][anchor]
    diff, pos = get_match(s.screen, anchor['ImageData'])
    print(diff, pos)
    x, y = pos
    w, h = anchor["Size"]
    dx, dy = anchor["Offset"]
    draw = s.screen.copy()
    for node_name in s.g.nodes:
        nx, ny = s.get_map_pos(anchor["OnMap"], (x+dx, y+dy), node_name)
        cv.circle(draw, (nx, ny), 3, (0, 0, 0), -1)
    cv.rectangle(draw, (x, y), (x+w, y+h), (255, 255, 255), 2)
    cv.circle(draw, (x+dx, y+dy), 5, (255, 255, 255), -1)
    show(draw)


def init_map(name):
    const["s"] = FightMap(name)
    const["s"].make_screen_shot()
    return const["s"]
