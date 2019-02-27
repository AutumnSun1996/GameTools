import sys
from fgo_fast import FGOSimple

if __name__ == "__main__":
    if len(sys.argv) > 1:
        section = sys.argv[1]
    else:
        section = "FGO2"

    FGOSimple.section = section
    fgo = FGOSimple("10连抽")
    count = 0
    while True:
        fgo.check_scene()
        if fgo.current_scene_name in {"重置奖品"}:
            count += 1
            print(fgo.current_scene_name, count)
        elif fgo.current_scene_name == "结束" and not fgo.scene_changed:
            fgo.notice("抽取结束(已重置%d次), 等待手动操作" % count)
            print("Total:", count)
            input("Pause...")
        elif fgo.current_scene_name == "礼物盒已满":
            fgo.notice("礼物盒已满(已重置%d次), 等待手动操作" % count)
            break
    print("Total:", count)
