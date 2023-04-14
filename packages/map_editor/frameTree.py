from classes.frame_tree import FrameTree
from utils.singletonMeta import SingletonMeta


class FrameTreeStorage(metaclass=SingletonMeta):
    """Only this class contains object Map from dt_maps """
    tree: FrameTree = None

    def __init__(self) -> None:
        self.tree = FrameTree()


if __name__ == '__main__':
    t = FrameTreeStorage()
    print(t.tree)
