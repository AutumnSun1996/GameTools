from fgo.fast import FGOSimple

import logging
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # fgo = FGOSimple("刷材料")
    # fgo = FGOSimple("主号换人礼装速刷")
    # fgo = FGOSimple("主号赝作速刷")
    fgo = FGOSimple("主号赝作-终本-慢速")
    # fgo = FGOSimple("主号赝作速刷-术本")
    # fgo = FGOSimple("主号赝作速刷-杀本")

    count = 0
    try:
        while 1:
            fgo.check_scene()
            if fgo.current_scene_name == "获得物品":
                count += 1
                logger.warning("Scene %s Count %d", fgo.current_scene_name, count)
                if count >= 0:
                    # fgo.manual()
                    fgo.error("已完成%d" % count)
                    break
            # input("Pause...")
    except KeyboardInterrupt:
        logger.warning("(OnExit) Scene %s Count %d", fgo.current_scene_name, count)
