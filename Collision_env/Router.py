

class Router:
    def __init__(self, id, connections, graph):
        # node on graph
        self.id = id
        self.network = graph
        # edges where this is the src
        # list of wires
        self.connections = connections
        self.actions = len(connections)
        self.buffer = []  # stack
        self.buffer_size = 1  # change this to hold more packets

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

    def remove_packet(self, dst):
        # if there is a connection to the destination
        # and the buffer is not empty
        # move packet to wire
        wire = self.has_connection(dst)
        if wire and self.buffer:
            packet = self.buffer[0]
            self.buffer = self.buffer[-1]
            packet.hop(dst, self.network)
