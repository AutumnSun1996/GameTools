from fgo.fgo_simple import FGOSimple


if __name__ == "__main__":
    f = FGOSimple("每日任务")
    while True:
        f.check_scene()
