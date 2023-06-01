from typing import Dict, Any
from dt_maps import MapLayer
from classes.basic.command import Command


class GetDefaultLayerConf(Command):
    _layer_name: str = None

    def __init__(self, layer_name) -> None:
        self._layer_name = layer_name

    def execute(self, layer: MapLayer,
                layer_name: str,
                default_conf: dict,
                *args, **kwargs) -> Dict[str, Any]:
        if layer_name == self._layer_name:
            return default_conf
