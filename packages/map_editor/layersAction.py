from typing import Any
from pathlib import Path
from dt_maps import MapLayer
from mapStorage import MapStorage
from classes.basic.command import Command
from layers import TileLayerHandler, WatchtowersLayerHandler
from classes.basic.chain import AbstractHandler
from classes.MapDescription import MapDescription
from classes.Commands.GetLayerCommand import GetLayerCommand

LAYERS = [
    WatchtowersLayerHandler
]


class LayersAction:
    """This class uses commands for different actions"""
    _chain_map: AbstractHandler = None

    def __init__(self):
        self._chain_map = TileLayerHandler()
        _ = self._chain_map
        for layer in LAYERS:
            _ = _.set_next(layer)

    def _exec(self, cmd: Command) -> Any:
        return self._chain_map.handle(command=cmd)

    def get_tiles(self) -> MapLayer:
        return self._exec(GetLayerCommand("tiles"))


if __name__ == '__main__':
    MapStorage(MapDescription(Path("./maps/tm1"), "map_1"))
    layers_api = LayersAction()
    tiles: MapLayer = layers_api.get_tiles()
    print(type(tiles))
    print(tiles)
    layers_api.get_tiles()["map_1/tile_0_0"].j = 1
    tiles: MapLayer = layers_api.get_tiles()
    print(type(tiles))
    print(tiles)
