from fgo_fast import FGOSimple

import logging
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    FGOSimple.section = "FGO3"
    # fgo = FGOSimple("XY赝作速刷-枪本")
    fgo = FGOSimple("XY赝作速刷-终本")
    
    count = 0
    try:
        while 1:
            fgo.check_scene()
            if fgo.current_scene_name == "获得物品":
                count += 1
                logger.warning("Scene %s Count %d", fgo.current_scene_name, count)
                if count >= 1:
                    # fgo.manual()
                    fgo.error("已完成%d" % count)
                    break
    except KeyboardInterrupt:
        logger.warning("(OnExit) Scene %s Count %d", fgo.current_scene_name, count)
