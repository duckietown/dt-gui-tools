from PyQt5.QtWidgets import QLabel
from typing import Dict, Any

ACCURACY = 4


class DebugLine(QLabel):

    def __init__(self, text: str = ""):
        super().__init__()
        self.text = text
        self.set_text(self.text)

    def set_text(self, text: str):
        self.text = text
        self.setText(self.text)
        self.show()

    def set_mouse_pos(self, event: Dict[str, Any]) -> None:
        self.setText(f"Cursor position: x={event['pos'][0]}, "
                     f"y={event['pos'][1]}, "
                     f"x'={event['map_pose'][0]:.{ACCURACY}f}, "
                     f"y'={event['map_pose'][1]:.{ACCURACY}f}")
