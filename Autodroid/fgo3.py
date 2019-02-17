from fgo_fast import FGOSimple

if __name__ == "__main__":
    FGOSimple.section = "FGO3"
    fgo = FGOSimple("FGO3")
    count = 0
    while 1:
        fgo.check_scene()
        print(fgo.current_scene_name)
        if fgo.current_scene_name == "获得物品":
            count += 1
            print(fgo.current_scene_name, count)
            if count >= 50:
                fgo.manual()
                break