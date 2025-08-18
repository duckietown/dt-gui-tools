from dt_maps import MapLayer
from classes.basic.command import Command
from utils.constants import TILES


class MoveTileCommand(Command):
    _new_position: tuple = (0, 0)
    _tile_name: str

    def __init__(self, tile_name: str, new_position: tuple) -> None:
        self._tile_name = tile_name
        self._new_position = new_position

    def execute(self, layer: MapLayer, layer_name: str, *args,
                **kwargs) -> None:
        if layer_name == TILES:
            # No longer persist i/j; indices are implied by tile name
            pass
