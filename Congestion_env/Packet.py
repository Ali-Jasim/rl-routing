import uuid
import networkx as nx
from Wire import Wire
from Router import Router


class Packet:
    def __init__(self, src, dst, graph, path=[]):
        self.id = str(uuid.uuid4())
        self.curr = src
        self.curr_router = src  # we need to know src router for each hop on wire
        self.next_router = None  # updated on path update
        self.src = src
        self.dst = dst
        self.graph = graph  # change this to network on vscode
        self.path = self.update_path()

# possibly return possible actions in current router
# possible actions = where we can hop

    # add an equal method to find
    def __eq__(self, other):
        if not isinstance(self, other):
            return False

        return self.id == other.id

    def __repr__(self):
        return f"id: {self.id},\n curr: {self.curr_router}, dst: {self.dst}"

    def on_wire(self):
        return isinstance(self.curr, Wire)

    def on_router(self):
        return isinstance(self.curr, Router)

    # this is the input buffer for the next router
    def push_to_wire(self):
        if isinstance(self.curr, Router):
            self.curr = self.curr.remove_packet(self, self.next_router)

    def push_to_router(self):
        if isinstance(self.curr, Wire):
            router = self.curr.remove_packet(self, self.next_router)
            if router:
                self.curr_router = router
                self.curr = router
                self.update_path()
            # otherwise we stay on wire

    def complete(self):
        return self.curr is self.dst

    # build a more sophisticated path finding function, for now, shortest path
    def update_path(self):
        self.path = nx.shortest_path(
            self.graph, self.curr_router.id, self.dst.id)
        if len(self.path) >= 2:
            self.next_router = self.path[1]
