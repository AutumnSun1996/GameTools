# from azurlane.fight_simple import SimpleFight as AzurLane
from azurlane.operation import Operation as AzurLane


if __name__ == "__main__":
    m = AzurLane("演习")
    while True:
        m.check_scene()
