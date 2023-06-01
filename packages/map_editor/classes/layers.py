import logging
from abc import ABC
from dt_maps import MapLayer
from dt_maps.types.commons import EntityHelper
from classes.basic.chain import AbstractHandler
from classes.basic.command import Command
from dt_maps.Map import REGISTER
from mapStorage import MapStorage
from utils.constants import LAYER_NAME
from utils.maps import create_layer
from typing import Dict, Any, Optional
from copy import deepcopy, copy


class AbstractLayer(ABC):
    _data: MapLayer = None
    _layer_handler: EntityHelper = None
    _layer_name: str = ""
    _default_conf: Dict[str, Any] = {}

    def __init__(self, **kwargs) -> None:
        self.dm = MapStorage().map
        self._layer_name = kwargs[LAYER_NAME]
        self._default_conf = kwargs["default_conf"]
        try:
            self._data = self.dm.layers[self._layer_name]
        except KeyError:
            logging.error(f"Empty layer {self._layer_name}")
            create_layer(self.dm, self._layer_name, {})
            self._data = self.dm.layers[self._layer_name]
        self._layer_handler = REGISTER[self._layer_name]

    def check_config(self, config: Dict[str, Any]) -> bool:
        for field in config:
            try:
                map_layer_type = self._layer_handler._get_property_types(self._layer_handler, field)
            except TypeError:
                map_layer_type = self._layer_handler._get_property_types(
                    field)
            if not isinstance(config[field], map_layer_type):
                return False
        return True

    def set_layer_handler(self, handler: EntityHelper) -> None:
        self._layer_handler = handler

    def get_layer_deepcopy(self, layer: MapLayer) -> Optional[Dict[str, Any]]:
        if not len(layer):
            return {}
        new_layer = {}
        for name, item in layer.items():
            new_item = {}
            for item_filed in self._default_conf:
                new_item[item_filed] = deepcopy(layer[name][item_filed])
                if item_filed in self.fields_with_types():
                    new_item[item_filed] = new_item[item_filed].value
            new_layer[name] = new_item
        return new_layer

    def fields_with_types(self) -> list:
        return []


class BasicLayerHandler(AbstractHandler, AbstractLayer):
    def __init__(self, **kwargs) -> None:
        super(BasicLayerHandler, self).__init__(**kwargs)

    def handle(self, command: Command) -> Any:
        response = command.execute(self._data, self._layer_name,
                                   deepcopy(self._default_conf),
                                   check_config=self.check_config,
                                   get_deepcopy=self.get_layer_deepcopy)
        if response:
            return response
        return super().handle(command)


class DynamicLayer(EntityHelper):
    _fields: Dict[str, Any] = {}
    _layer_name: str = ""

    def __init__(self, **kwargs) -> None:
        super(DynamicLayer, self).__init__(kwargs["map"], kwargs[LAYER_NAME])
        self._layer_name = kwargs[LAYER_NAME]
        for field_name, field_val in kwargs["conf"].items():
            self._fields[field_name] = field_val
            setattr(self, field_name, field_val)

    def _get_property_values(self, name: str) -> str:
        return self._fields[name]

    def _get_property_types(self, name: str) -> Any:
        return type(self._fields[name])

    def _get_layer_name(self) -> str:
        return self._layer_name
