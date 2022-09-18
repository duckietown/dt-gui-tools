import os
from pathlib import Path

from dt_maps.types.tile_maps import TileSize
from dt_maps.types.tiles import Tile
from dt_maps.types.traffic_signs import TrafficSign
from dt_maps.types.vehicles import Vehicle
from dt_maps.types.citizens import Citizen
from dt_maps.types.ground_tags import GroundTag
from classes.MapDescription import MapDescription
from mapStorage import MapStorage
from dt_maps import Map, MapLayer
from dt_maps.types.frames import Frame
from dt_maps.types.watchtowers import Watchtower
from typing import Dict, Any
from utils.constants import FRAMES, WATCHTOWERS, TILES, TILE_MAPS, VEHICLES, \
    CITIZENS, TRAFFIC_SIGNS, GROUND_TAGS

REGISTER = {
    FRAMES: Frame,
    TILES: Tile,
    TILE_MAPS: TileSize,
    WATCHTOWERS: Watchtower,
    VEHICLES: Vehicle,
    CITIZENS: Citizen,
    TRAFFIC_SIGNS: TrafficSign,
    GROUND_TAGS: GroundTag
}


def default_map_storage() -> MapStorage:
    return MapStorage(MapDescription(Path("./maps/tm1"), "map_1"))


def create_layer(dm: Map, layer_name: str, layer: Dict[str, Any]) -> None:
    layer = MapLayer(dm, layer_name, layer)
    dm._layers.__dict__[layer_name] = layer
    register = lambda l, t: dm.layers.get(l).register_entity_helper(
        t) if dm.layers.has(l) else 0
    register(layer_name, REGISTER[layer_name])


def set_obj(layer: MapLayer, obj_name: str, default_conf: dict) -> None:
    layer[obj_name] = default_conf


def delete_obj(layer: MapLayer, obj_name: str) -> None:
    layer.__delitem__(obj_name)


def change_map_directory(dm: Map, new_dir: str) -> None:
    dm._path = new_dir
    dm._assets_dir = os.path.join(dm._path, "assets")


def get_map_height(tiles: Dict[str, Any]) -> int:
    return get_map_size(tiles, "j")
    

def get_map_width(tiles: Dict[str, Any]) -> int:
    return get_map_size(tiles, "i")


def get_map_size(tiles: Dict[str, Any], side: str) -> int:
    elems = []
    for tile_name in tiles:
        elems.append(tiles[tile_name][side])
    if len(elems) > 0:
        return max(elems) + 1
    else:
        return 0


if __name__ == '__main__':
    m = default_map_storage()
    print(m.map.name)
