from typing import List, TypeVar, Generic
import networkx as nx

T = TypeVar('T')

EMPTY = []


class Tree(Generic[T]):

    def __init__(self):
        self.G = nx.DiGraph()

    def add(self, successor: T, predecessor: T) -> None:
        self.G.add_edge(predecessor, successor)

    def exist(self, element: T) -> bool:
        try:
            self.G[element]
        except KeyError as e:
            return False
        return True

    def remove_node(self, element: T) -> None:
        self.G.remove_node(element)

    def successors(self, element: T) -> List[T]:
        try:
            return list(self.G.successors(element))
        except TypeError:
            return EMPTY

    def predecessors(self, element: T) -> List[T]:
        try:
            return list(self.G.predecessors(element))
        except TypeError:
            return EMPTY

    def clear(self) -> None:
        self.G.clear()
