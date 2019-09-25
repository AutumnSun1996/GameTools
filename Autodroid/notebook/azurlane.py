from .common import *
from azurlane.map_anchor import *

from azurlane.fight_event import EventFight as AzurLane

const["section"] = "azurlane"


def check_map_anchor(anchor):
    s = const["s"]
    if isinstance(anchor, str):
        anchor = s.data["Anchors"][anchor]
    if 'ImageData' not in anchor:
        load_image(anchor, s.section)
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
    const["s"] = AzurLane(name)
    const["s"].make_screen_shot()
    reset_log()
    return const["s"]


def get_grid_center(self, offx, offy):
    """返回格子中心点坐标列表，包括棋盘坐标和屏幕坐标"""
    warped = cv.warpPerspective(self.screen, trans_matrix, target_size)
    filtered_map = cv.filter2D(warped, 0, filter_kernel)
    _, poses = self.search_resource("Corner", image=filtered_map)
    if len(poses) < 3:
        raise RuntimeError("Less than 4 anchors found. ")

    poses = np.array(poses)
    poses += self.resources["Corner"]["Offset"]
    diff = (poses % 100)
    dx = np.argmax(np.bincount(diff[:, 0]))
    dy = np.argmax(np.bincount(diff[:, 1]))

    res = dx+100*offx, dy+100*offy
    res = (np.array(list(res), dtype="float") + 50).reshape(1, -1, 2)

    pos_in_screen = cv.perspectiveTransform(res, inv_trans).reshape(-1, 2).astype("int")
    print(pos_in_screen)
    return pos_in_screen[0]


def crop_in_map(center, offset, size):
    s = const["s"]
    x, y = center
    wh = np.array(list(reversed(s.screen.shape[:2])))
    coef = 0.0005907301142274507
    r = coef * y + 1
    lt = np.asarray(offset) * r + [x, y]
    rb = lt + np.asarray(size) * r
    if lt.min() < 0:
        return None
    if np.any(rb > wh):
        return None
    print("lt/rb", lt, rb)
    part = cv_crop(s.screen, (*lt.astype("int"), *rb.astype("int")))
    return part, lt, rb

'''
Example:
save_enemy((3, 2), """
    CropOffset: [-40, -100]
    CropSize: [80, 110]
    Image: Enemy/E2.png
    Offset: [-30, -90]
    Size: [60, 90]
    Type: Dynamic
""")
'''
def save_enemy(pos, info):
    s = const["s"]
    if isinstance(info, str):
        info = yaml.load(info)
    offset = info["CropOffset"]
    size = info["CropSize"]

    diff_s = []
    results = []
    x, y = get_grid_center(s, *pos)
    part = crop_in_map((x, y), info["CropOffset"], info["CropSize"])
#     part = cv.resize(part, tuple(size))
    show(part[0])
    part = crop_in_map((x, y), info["Offset"], info["Size"])
    show(part[0])

    path = "%s/resources/%s" % (const["section"], info["Image"])
    cv_save(path, part[0])
    logger.info("%s Saved.", os.path.realpath(path))
