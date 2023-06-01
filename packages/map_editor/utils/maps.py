import os
import shutil
from pathlib import Path
from classes.MapDescription import MapDescription
from mapStorage import MapStorage
from dt_maps import Map, MapLayer
from typing import Dict, Any
from dt_maps.Map import REGISTER


def copy_dir_with_map(path_from: str, path_to: str) -> None:
    if not os.path.exists(path_to):
        shutil.copytree(path_from, path_to)


def default_map_storage(map_dir: str) -> MapStorage:
    return MapStorage(MapDescription(Path(map_dir), "map_1"))


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


def change_map_name(dm: Map, new_name: str) -> None:
    dm._name = new_name


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


def convert_layer_name_to_class_name(layer_name: str) -> str:
    layer_name_list = layer_name.split("_")
    class_name = ""
    for name in layer_name_list:
        name = list(name)
        name[0] = name[0].upper()
        name = "".join(name)
        class_name += name
    return class_name


if __name__ == '__main__':
    m = default_map_storage()
    print(m.map.name)
