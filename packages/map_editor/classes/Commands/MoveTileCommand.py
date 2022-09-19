from dt_maps import Map, MapLayer
from classes.basic.command import Command
from utils.constants import TILES


class MoveTileCommand(Command):
    _new_position: tuple = (0, 0)
    _tile_name: str

    def __init__(self, tile_name: str, new_position: tuple):
        self._tile_name = tile_name
        self._new_position = new_position

    def execute(self, dm: Map, layer: MapLayer, layer_name: str, *args,
                **kwargs) -> None:
        if layer_name == TILES:
            layer[self._tile_name].i = self._new_position[0]
            layer[self._tile_name].j = self._new_position[1]
