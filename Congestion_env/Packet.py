import uuid
import networkx as nx
from Wire import Wire
from Router import Router


class Packet:
    def __init__(self, src, dst, graph, path=[]):
        self.id = str(uuid.uuid4())
        self.curr = src
        self.next_hop = None
        self.src = src
        self.dst = dst
        self.path = path
        self.graph = graph

    # add an equal method to find
    def __eq__(self, other):
        if not isinstance(self, other):
            return False

        return self.id is other.id

    def __repr__(self):
        return f"id: {self.id},\n src: {self.curr}, dst: {self.dst}, curr: {self.curr}"

    def on_wire(self):
        return isinstance(self.curr, Wire)

    def on_router(self):
        return isinstance(self.curr, Router)

    def push_to_wire(self, wire, dst):
        if isinstance(self.curr, Router):
            self.curr = wire
            self.next_hop = dst

    def push_to_router(self, router):
        if isinstance(self.curr, Wire):
            self.curr = router
            self.update_path()
            self.next_hop = self.find_next_hop()

    def find_next_hop(self):
        # we are at destination
        if len(self.path) < 2:
            return -1
        # shortest path
        return self.path[1]

    def complete(self):
        return self.curr is self.dst

    def update_path(self):
        self.path = nx.shortest_path(self.graph, self.curr, self.dst)
