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
        if fgo.current_scene_name in {"10连抽", "关卡选择"}:
            count += 1
            print(fgo.current_scene_name, count)
        elif fgo.current_scene_name == "结束":
            fgo.notice("已完成%d次抽取。等待手动操作" % count)
            print("Total:", count)
            input("Pause...")
    print("Total:", count)
