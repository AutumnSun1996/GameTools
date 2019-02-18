from fgo_fast import FGOSimple

if __name__ == "__main__":
    FGOSimple.section = "FGO3"
    fgo = FGOSimple("XY赝作速刷-枪本")
    count = 0
    while 1:
        fgo.check_scene()
        print(fgo.current_scene_name)
        if fgo.current_scene_name == "获得物品":
            count += 1
            print(fgo.current_scene_name, count)
            if count >= 20:
                fgo.manual()
                break
