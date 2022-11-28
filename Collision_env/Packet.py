import uuid
import networkx as nx
import Wire
import Router


class Packet:
    def __init__(self, src, dst, graph, path=[]):
        self.id = str(uuid.uuid4())
        self.curr = src
        self.src = src
        self.dst = dst
        self.path = path
        self.graph = graph

    # add an equal method to find
    def __eq__(self, other):
        if not isinstance(self, other):
            return False

        return self.id == other.id

    def on_wire(self):
        # if packet is on an edge it will be a tuple
        # require it to be false and dest of wire needs to be free for packet to hop
        return isinstance(self.curr, Wire)

    def find_next_hop(self):
        # we are at destination
        if len(self.path) < 2:
            return -1
        # shortest path
        return self.path[1]

    # todo: find all connected neighbors and send selection of paths

    def hop(self, target, graph):
        # hop to next router
        if isinstance(self.curr, Wire):
            # we are on wire hop to router
            self.curr = self.curr.remove_packet()
        if isinstance(self.curr, Router):
            self.curr = self.curr.remove_packet(target)

        # self.curr = (self.curr, target)
        # for now just find shortest path
        self.path = nx.shortest_path(graph, target, self.dst)

    def update_path(self, target):
        self.path - nx.shortest_path()

    def continue_on_wire(self, occupied):
        src, dst = self.current
        self.current = dst
        # stay on wire if dst is occupied

    def done(self):
        return self.curr == self.dst
