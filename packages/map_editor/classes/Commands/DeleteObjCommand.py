from dt_maps import Map, MapLayer
from classes.basic.command import Command
from utils.maps import delete_obj


class DeleteObjCommand(Command):
    _layer_name: str
    _object_name: str

    def __init__(self, layer_name: str, object_name: str):
        self._layer_name = layer_name
        self._object_name = object_name

    def execute(self, dm: Map, layer: MapLayer, layer_name: str, *args,
                **kwargs) -> None:
        if layer_name == self._layer_name:
            delete_obj(layer, self._object_name)
