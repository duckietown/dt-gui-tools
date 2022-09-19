from dt_maps import Map, MapLayer
from classes.basic.command import Command
from utils.maps import set_obj
from typing import Dict, Any


class ChangeObjCommand(Command):
    _layer_name: str
    _object_name: str
    _new_config: Dict[str, Any]

    def __init__(self, layer_name: str, object_name: str,
                 new_config: Dict[str, Any]):
        self._layer_name = layer_name
        self._object_name = object_name
        self._new_config = new_config

    def execute(self, dm: Map, layer: MapLayer, layer_name: str, *args,
                **kwargs) -> None:
        if layer_name == self._layer_name:
            set_obj(layer, self._object_name, self._new_config)
