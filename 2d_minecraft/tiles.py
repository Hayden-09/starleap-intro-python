from enum import Enum


class TileType(Enum):
    AIR = (False, (0,0,0,0))
    GRASS = (True, (86, 125, 70))
    DIRT = (True, (155, 118, 83))
    STONE = (True, (120, 120, 120))

    def __init__(self, is_solid, color):
        self.is_solid = is_solid
        self.color = color
