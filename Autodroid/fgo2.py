# 石头号-弓阶

from fgo_fast import FGOSimple

FGOSimple.section = "FGO2"


if __name__ == "__main__":
    fgo = FGOSimple("C尼禄")
    # fgo = FGOSimple("石头号-弓阶")
    count = 0
    while 1:
        fgo.check_scene()
        print(fgo.current_scene_name)
        if fgo.current_scene_name == "获得物品":
            count += 1
            print(fgo.current_scene_name, count)
            if count >= 1:
                fgo.manual()
                break