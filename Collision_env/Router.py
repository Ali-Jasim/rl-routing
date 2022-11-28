

class Router:
    def __init__(self, id, connections, kind, graph):
        # node on graph
        self.id = id
        self.network = graph
        self.kind = kind

        # edges where this is the src
        # list of wires connected to routers
        self.connections = connections

        # how many actions are possible in router
        self.actions = len(connections)

        # depending on type, set buffer size
        if kind == 'T':
            self.buffer_size = 100  # change this to hold more packets
        elif kind == 'M':
            self.buffer_size = 25  # change this to hold more packets
        elif kind == 'C' or kind == 'CP':
            self.buffer_size = 10

        self.buffer = []  # stack

    def __eq__(self, other):
        if not isinstance(self, other):
            return False

        return self.id == other.id

    def is_full(self):
        return len(self.buffer) >= self.buffer_size

    def has_connection(self, dst):
        for connection in self.connections:
            if connection == dst:
                return connection

        return None

    # stack behaviour
    # todo: if this is the packet dst router, call network to remove packet from transmission
    def insert_packet(self, packet):
        if self.is_full():
            self.buffer.append(packet)
            return True

        return False

    # push to wire
    def remove_packet(self, dst):
        # if there is a connection to the destination
        # and the buffer is not empty
        # move packet to wire
        wire = self.has_connection(dst)
        if wire and self.buffer:
            packet = self.buffer[0]
            self.buffer = self.buffer[-1]
            packet.push_to_wire(wire, dst)
