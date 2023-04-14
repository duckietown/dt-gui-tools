from dt_maps import MapLayer
from classes.basic.command import Command


class DeepCopyLayerCommand(Command):
    _layer_name: str

    def __init__(self, layer_name: str):
        self._layer_name = layer_name

    def execute(self, layer: MapLayer, layer_name: str, *args,
                **kwargs) -> None:
        if layer_name == self._layer_name:
            get_deepcopy = kwargs["get_deepcopy"]
            return get_deepcopy(layer)
