from dataclasses import dataclass
from pathlib import Path


@dataclass
class MapDescription:
    """Describe map name and folder of map"""
    folder: Path
    map_name: str
