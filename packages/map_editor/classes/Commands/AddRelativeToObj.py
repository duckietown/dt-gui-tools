from dt_maps import Map, MapLayer
from classes.basic.command import Command
from typing import Dict, Any


class AddRelativeToObj(Command):
    _layer_name: str
    _object_name: str

    def __init__(self, layer_name: str, object_name: str):
        self._layer_name = layer_name
        self._object_name = object_name

    def execute(self, dm: Map, layer: MapLayer, layer_name: str, new_config: Dict[str, Any], *args, **kwargs) -> None:
        if layer_name == self._layer_name:
            dm.get_layer("frames")[self._object_name]['relative_to'] = dm.name
