from dt_maps import Map, MapLayer
from classes.basic.command import Command
from utils.constants import FRAMES, RELATIVE_TO


class AddRelativeToObj(Command):
    _object_name: str
    _relative_to: str

    def __init__(self, object_name: str, relative_to: str):
        self._object_name = object_name
        self._relative_to = relative_to

    def execute(self, dm: Map, layer: MapLayer, layer_name: str, *args,
                **kwargs) -> None:
        if layer_name == FRAMES:
            layer[self._object_name][RELATIVE_TO] = self._relative_to
