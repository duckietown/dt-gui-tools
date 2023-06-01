from dt_maps import MapLayer
from classes.basic.command import Command
from utils.constants import FRAMES


class RotateCommand(Command):
    _new_angle: float = 0.0
    _frame_name: str

    def __init__(self, frame_name: str, new_angle: float) -> None:
        self._frame_name = frame_name
        self._new_angle = new_angle

    def execute(self, layer: MapLayer, layer_name: str, *args,
                **kwargs) -> None:
        if layer_name == FRAMES:
            layer[self._frame_name].pose.yaw = float(self._new_angle)
