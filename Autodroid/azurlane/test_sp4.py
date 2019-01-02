from fight_sp4 import SP4Control
if __name__ == "__main__":
    sp4 = SP4Control()
    sp4.update_current_scene()
    # print(sp4.current_scene)
    sp4.mood_detect()
    # print(sp4.select_ships())

    # print(sp4.retire())
