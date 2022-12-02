import uuid
import networkx as nx
from Wire import Wire
from Router import Router


class Packet:
    def __init__(self, src, dst, graph, path=[]):
        self.id = str(uuid.uuid4())
        self.src_id = src.id
        self.dst_id = dst.id
        self.curr = src
        self.curr_router = src  # we need to know src router for each hop on wire
        self.next_router = None  # updated on path update
        self.src = src
        self.dst = dst
        self.graph = graph  # change this to network on vscode
        self.reward = 0
        #self.path = self.update_path()

# possibly return possible actions in current router
# possible actions = where we can hop

    # add an equal method to find
    def __eq__(self, other):
        if not isinstance(self, type(other)):
            return False

        return self.id == other.id

    def __repr__(self):
        return f"id: {self.id},\n curr: {self.curr_router}, dst: {self.dst}"

    def on_wire(self):
        return isinstance(self.curr, Wire)

    def on_router(self):
        return isinstance(self.curr, Router)

    def get_actions(self):
        if isinstance(self.curr, Router):
            return self.curr.actions

    def choose_action(self, action):
        self.next_router = action

    def validate_action(self):
        if self.next_router in self.curr.actions:
            self.reward += -1
            return True

        self.reward += -2
        self.next_router = None
        # as per paper, -2 for invalid actions
        return False

    # this is the input buffer for the next router

    def push_to_wire(self):
        if isinstance(self.curr, Router):
            if self.validate_action():
                self.curr = self.curr.remove_packet(self, self.next_router)

    def push_to_router(self):
        if isinstance(self.curr, Wire):
            router = self.curr.remove_packet(self, self.next_router)
            if router:
                self.curr_router = router
                self.curr = router
                self.next_router = None
                # self.update_path()
                return 0
            else:
                # big negative reward for congestion
                self.reward += -5
                return 1
            # otherwise we stay on wire

    def complete(self):
        return self.curr is self.dst

    def update_next_hop(self, dst):
        self.next_router = dst

    # build a more sophisticated path finding function, for now, shortest path
    def choose_action_shortest(self):
        self.path = nx.shortest_path(
            self.graph, self.curr_router.id, self.dst.id)
        if len(self.path) >= 2:
            self.next_router = self.path[1]
