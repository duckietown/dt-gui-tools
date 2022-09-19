from dt_maps import Map, MapLayer
from classes.basic.command import Command
from utils.constants import TILE_MAPS, TILE_SIZE


class SetTileSizeCommand(Command):
    _new_size: tuple = (0.0, 0.0)
    _tile_map_name: str

    def __init__(self, tile_map_name: str, new_size: tuple):
        self._tile_map_name = tile_map_name
        self._new_size = new_size

    def execute(self, dm: Map, layer: MapLayer, layer_name: str, *args,
                **kwargs) -> None:
        if layer_name == TILE_MAPS:
            layer[self._tile_map_name][TILE_SIZE]['x'] = self._new_size[0]
            layer[self._tile_map_name][TILE_SIZE]['y'] = self._new_size[1]
