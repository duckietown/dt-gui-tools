from pathlib import Path
from typing import Any, Dict
from utils.constants import TILE_SIZE
from mapStorage import MapStorage
from classes.layers import BasicLayerHandler
from classes.MapDescription import MapDescription
from classes.Commands.GetLayerCommand import GetLayerCommand
from dt_maps.types.watchtowers import WatchtowerType
from dt_maps.types.tiles import TileType
from dt_maps.types.traffic_signs import TrafficSignType
from dt_maps.types.citizens import CitizenType
from dt_maps.types.vehicles import VehicleType, ColorType


class TilesLayerHandler(BasicLayerHandler):
    def __init__(self, **kwargs) -> None:
        kwargs["default_conf"] = {'i': 0, 'j': 0, 'type': 'floor'}
        super(TilesLayerHandler, self).__init__(**kwargs)

    def check_config(self, config: Dict[str, Any]) -> bool:
        return super().check_config(config) and config.get("type") \
               in [t.value for t in TileType]

    def fields_with_types(self) -> list:
        return ["type"]


class WatchtowersLayerHandler(BasicLayerHandler):
    def __init__(self, **kwargs) -> None:
        kwargs["default_conf"] = {'configuration': 'WT18', 'id': ""}
        super(WatchtowersLayerHandler, self).__init__(**kwargs)

    def check_config(self, config: Dict[str, Any]) -> bool:
        return super().check_config(config) and config.get("configuration") \
               in [t.value for t in WatchtowerType]

    def fields_with_types(self) -> list:
        return ["configuration"]


class FramesLayerHandler(BasicLayerHandler):
    def __init__(self, **kwargs) -> None:
        kwargs["default_conf"] = {
            'pose': {'x': 1.0, 'y': 1.0, 'z': 0.0, 'yaw': 0.0, 'roll': 0.0,
                     'pitch': 0.0}, 'relative_to': ""}
        super(FramesLayerHandler, self).__init__(**kwargs)


class TileMapsLayerHandler(BasicLayerHandler):
    def __init__(self, **kwargs) -> None:
        kwargs["default_conf"] = {TILE_SIZE: {'x': 0.585, 'y': 0.585}}
        super(TileMapsLayerHandler, self).__init__(**kwargs)


class TrafficSignsLayerHandler(BasicLayerHandler):
    def __init__(self, **kwargs) -> None:
        kwargs["default_conf"] = {"type": "stop", "id": 1, "family": "36h11"}
        super(TrafficSignsLayerHandler, self).__init__(**kwargs)

    def check_config(self, config: Dict[str, Any]) -> bool:
        return super().check_config(config) and \
               config.get("type") in [t.value for t in TrafficSignType]

    def fields_with_types(self) -> list:
        return ["type"]


class GroundTagsLayerHandler(BasicLayerHandler):
    def __init__(self, **kwargs) -> None:
        kwargs["default_conf"] = {"size": 0.15, "id": 0, "family": "36h11"}
        super(GroundTagsLayerHandler, self).__init__(**kwargs)


class CitizensLayerHandler(BasicLayerHandler):
    def __init__(self, **kwargs) -> None:
        kwargs["default_conf"] = {"color": "yellow"}
        super(CitizensLayerHandler, self).__init__(**kwargs)

    def check_config(self, config: Dict[str, Any]) -> bool:
        return super().check_config(config) and \
               config.get("color") in [t.value for t in CitizenType]

    def fields_with_types(self) -> list:
        return ["color"]


class VehiclesLayerHandler(BasicLayerHandler):
    def __init__(self, **kwargs) -> None:
        kwargs["default_conf"] = {"color": "blue", "configuration": "DB18",
                                  "id": ""}
        super(VehiclesLayerHandler, self).__init__(**kwargs)

    def check_config(self, config: Dict[str, Any]) -> bool:
        return super().check_config(config) and \
               config.get("configuration") in [t.value for t in VehicleType] and \
               config.get("color") in [t.value for t in ColorType]

    def fields_with_types(self) -> list:
        return ["configuration", "color"]


if __name__ == '__main__':
    MapStorage(MapDescription(Path("./maps/tm1"), "map_1"))
    tile_layer = TilesLayerHandler()
    watchtower_layer = WatchtowersLayerHandler()
    tile_layer.set_next(watchtower_layer)
    layer = tile_layer

    # while layer:
    print(layer.handle(GetLayerCommand("watchtowers")))
