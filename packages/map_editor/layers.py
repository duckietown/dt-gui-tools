from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
from utils.constants import TILES, TILE_SIZE, TILE_MAPS, WATCHTOWERS, \
    FRAMES, TRAFFIC_SIGNS, GROUND_TAGS, VEHICLES, CITIZENS
from mapStorage import MapStorage
from classes.layers import AbstractLayer
from classes.basic.command import Command
from classes.basic.chain import AbstractHandler
from classes.MapDescription import MapDescription
from classes.Commands.GetLayerCommand import GetLayerCommand
from dt_maps.types.watchtowers import WatchtowerType
from dt_maps.types.tiles import TileType
from dt_maps.types.traffic_signs import TrafficSignType
from dt_maps.types.citizens import CitizenType
from dt_maps.types.vehicles import VehicleType, ColorType


class TileLayerHandler(AbstractHandler, AbstractLayer):
    def __init__(self, *kwargs) -> None:
        super(TileLayerHandler, self).__init__(*kwargs)

    def handle(self, command: Command) -> Any:
        response = command.execute(self.dm, self.data, self.layer_name(),
                                   self.default_conf(),
                                   check_config=self.check_config)
        if response:
            return response
        return super().handle(command)

    def layer_name(self) -> str:
        return TILES

    def default_conf(self) -> Dict[str, Any]:
        return {'i': 0, 'j': 0, 'type': 'floor'}

    def check_config(self, config: Dict[str, Any]) -> bool:
        return super().check_config(config) and config.get("type") \
               in [t.value for t in TileType]


class WatchtowersLayerHandler(AbstractHandler, AbstractLayer):
    def __init__(self, *kwargs) -> None:
        super(WatchtowersLayerHandler, self).__init__(*kwargs)

    def handle(self, command: Command) -> Any:
        response = command.execute(self.dm, self.data, self.layer_name(),
                                   self.default_conf(),
                                   check_config=self.check_config)
        if response:
            return response
        return super().handle(command)

    def layer_name(self) -> str:
        return WATCHTOWERS

    def default_conf(self) -> Dict[str, str]:
        return {'configuration': 'WT18', 'id': ""}

    def check_config(self, config: Dict[str, Any]) -> bool:
        return super().check_config(config) and config.get("configuration") \
               in [t.value for t in WatchtowerType]


class FramesLayerHandler(AbstractHandler, AbstractLayer):
    def __init__(self, *kwargs) -> None:
        super(FramesLayerHandler, self).__init__(*kwargs)

    def handle(self, command: Command) -> Any:
        response = command.execute(self.dm, self.data, self.layer_name(),
                                   self.default_conf(),
                                   check_config=self.check_config)
        if response:
            return response
        return super().handle(command)

    def layer_name(self) -> str:
        return FRAMES

    def default_conf(self) -> Dict[str, Any]:
        return {'pose': {'x': 1.0, 'y': 1.0, 'z': 0.0, 'yaw': 0.0, 'roll': 0.0,
                         'pitch': 0.0}, 'relative_to': ""}


class TileMapsLayerHandler(AbstractHandler, AbstractLayer):
    def __init__(self, *kwargs) -> None:
        super(TileMapsLayerHandler, self).__init__(*kwargs)

    def handle(self, command: Command) -> Any:
        response = command.execute(self.dm, self.data, self.layer_name(),
                                   self.default_conf())
        if response:
            return response
        return super().handle(command)

    def layer_name(self) -> str:
        return TILE_MAPS

    def default_conf(self) -> Dict[str, Any]:
        return {TILE_SIZE: {'x': 0.585, 'y': 0.585}}


class TrafficSignsHandler(AbstractHandler, AbstractLayer):
    def __init__(self, *kwargs) -> None:
        super(TrafficSignsHandler, self).__init__(*kwargs)

    def handle(self, command: Command) -> Any:
        response = command.execute(self.dm, self.data, self.layer_name(),
                                   self.default_conf(),
                                   check_config=self.check_config)
        if response:
            return response
        return super().handle(command)

    def layer_name(self) -> str:
        return TRAFFIC_SIGNS

    def default_conf(self) -> Dict[str, Any]:
        return {"type": "stop", "id": 0, "family": "36h11"}

    def check_config(self, config: Dict[str, Any]) -> bool:
        return super().check_config(config) and \
               config.get("type") in [t.value for t in TrafficSignType]


class GroundTagsHandler(AbstractHandler, AbstractLayer):
    def __init__(self, *kwargs) -> None:
        super(GroundTagsHandler, self).__init__(*kwargs)

    def handle(self, command: Command) -> Any:
        response = command.execute(self.dm, self.data, self.layer_name(),
                                   self.default_conf(),
                                   check_config=self.check_config)
        if response:
            return response
        return super().handle(command)

    def layer_name(self) -> str:
        return GROUND_TAGS

    def default_conf(self) -> Dict[str, Any]:
        return {"size": 0.15, "id": 0, "family": "36h11"}


class CitizensHandler(AbstractHandler, AbstractLayer):
    def __init__(self, *kwargs) -> None:
        super(CitizensHandler, self).__init__(*kwargs)

    def handle(self, command: Command) -> Any:
        response = command.execute(self.dm, self.data, self.layer_name(),
                                   self.default_conf(),
                                   check_config=self.check_config)
        if response:
            return response
        return super().handle(command)

    def layer_name(self) -> str:
        return CITIZENS

    def default_conf(self) -> Dict[str, Any]:
        return {"color": "yellow"}

    def check_config(self, config: Dict[str, Any]) -> bool:
        return super().check_config(config) and \
               config.get("color") in [t.value for t in CitizenType]


class VehiclesHandler(AbstractHandler, AbstractLayer):
    def __init__(self, *kwargs) -> None:
        super(VehiclesHandler, self).__init__(*kwargs)

    def handle(self, command: Command) -> Any:
        response = command.execute(self.dm, self.data, self.layer_name(),
                                   self.default_conf(),
                                   check_config=self.check_config)
        if response:
            return response
        return super().handle(command)

    def layer_name(self) -> str:
        return VEHICLES

    def default_conf(self) -> Dict[str, Any]:
        return {"color": "blue", "configuration": "DB18", "id": ""}

    def check_config(self, config: Dict[str, Any]) -> bool:
        return super().check_config(config) and \
               config.get("configuration") in [t.value for t in VehicleType] and \
               config.get("color") in [t.value for t in ColorType]


if __name__ == '__main__':
    MapStorage(MapDescription(Path("./maps/tm1"), "map_1"))
    tile_layer = TileLayerHandler()
    watchtower_layer = WatchtowersLayerHandler()
    tile_layer.set_next(watchtower_layer)
    layer = tile_layer

    # while layer:
    print(layer.handle(GetLayerCommand("watchtowers")))
