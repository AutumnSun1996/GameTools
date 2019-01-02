"""
碧蓝航线演习

"""

from map_anchor import FightMap


class Operation(FightMap):
    """
    碧蓝航线演习

    """
    def __init__(self):
        super().__init__()

    def reload(self):
        self

if __name__ == "__main__":
    op = Operation()
    op.check_scene()
