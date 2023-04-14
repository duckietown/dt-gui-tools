from dt_maps import MapLayer
from classes.basic.command import Command


class ChangeIDCommand(Command):
    _new_id: int or str
    _name: str

    def __init__(self, layer_name: str, name: str, new_id: int or str) -> None:
        self._name = name
        self._new_id = new_id
        self._layer_name = layer_name

    def execute(self, layer: MapLayer, layer_name: str, *args,
                **kwargs) -> None:
        if layer_name == self._layer_name:
            layer[self._name].id = self._new_id
