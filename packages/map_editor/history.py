from typing import Optional

MAX_BUFFER_LENGTH = 100


class Memento:
    _state = None

    def __init__(self, state) -> None:
        self._state = state

    def get_state(self):
        return self._state


class EditorHistory:
    buffer: [Memento] = []
    current_state_index: int = -1

    def delete(self, start_index: int) -> None:
        """
        Delete objects from current_state_index to max_length.
        If buffer is full, delete old states.
        """
        del self.buffer[start_index:]

    def clear_history(self) -> None:
        self.delete(0)

    def push(self, m: Memento) -> None:
        """
        Add new state to the end of buffer.
        """
        if self.current_state_index + 1 == MAX_BUFFER_LENGTH:
            if len(self.buffer) > 0:
                self.buffer.pop(0)
            self.current_state_index -= 1

        if self.current_state_index + 1 < MAX_BUFFER_LENGTH:
            self.buffer.append(m)
            self.current_state_index = len(self.buffer) - 1

    def undo(self) -> Optional[Memento]:
        """
        Return state from history at index current_state_index - 1.
        """
        if self.current_state_index - 1 >= 0:
            self.current_state_index -= 1
            return self.buffer[self.current_state_index]
        elif self.current_state_index == 0:
            return self.buffer[0]
        else:
            return None

    def shift_undo(self) -> Optional[Memento]:
        """
        Return state from history at index current_state_index + 1.
        """
        if self.current_state_index == len(self.buffer) - 1:
            return self.buffer[self.current_state_index]
        elif self.current_state_index + 1 < len(self.buffer):
            self.current_state_index += 1
            return self.buffer[self.current_state_index]
        else:
            return None
