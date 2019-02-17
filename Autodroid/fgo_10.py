from fgo_fast import FGOSimple

if __name__ == "__main__":
    FGOSimple.section = "FGO2"
    fgo = FGOSimple("10连抽")
    count = 0
    while True:
        fgo.check_scene()
        if fgo.current_scene_name in {"10连抽", "关卡选择"}:
            count += 1
            print(fgo.current_scene_name, count)
        elif fgo.current_scene_name == "结束":
            print("Total:", count)
            input("Pause...")
    print("Total:", count)