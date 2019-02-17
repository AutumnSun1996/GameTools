from fgo.fast import FGOSimple

import logging
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    FGOSimple.section = "FGO2"
    # fgo = FGOSimple("C尼禄")
    # fgo = FGOSimple("R金时")
    # fgo = FGOSimple("石头号-弓阶")
    # fgo = FGOSimple("小号剧情推进")
    fgo = FGOSimple("小号赝作速刷")
    count = 0
    while 1:
        fgo.check_scene()
        if fgo.current_scene_name == "获得物品":
            count += 1
            logger.warning("Scene %s Count %d", fgo.current_scene_name, count)
            if count >= 50:
                # fgo.manual()
                break
