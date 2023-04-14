class Buffer:
    _objects: dict = None

    def save_buffer(self, buffer: dict) -> None:
        self._objects = buffer

    def get_buffer(self) -> dict:
        return self._objects
