class Router:
    def __init__(self, id, kind, network, buffer_size):
        # node on graph
        self.id = id
        self.network = network
        # avoiding using type, better name?
        self.kind = kind

        # edges connected to this node
        # list of wires connected to routers
        self.connections = []

        self.actions = []

        # depending on type, set buffer size
        if kind == 'T':
            self.buffer_size = 100  # change this to hold more packets
        elif kind == 'M':
            self.buffer_size = 25  # change this to hold more packets
        elif kind == 'C' or kind == 'CP':
            self.buffer_size = buffer_size

        self.buffer = []  # Queue

    def __eq__(self, other):
        if not isinstance(self, other):
            return False

        return self.id == other.id

    def __repr__(self):
        return f"id: {self.id}, type: {self.kind}\n connections: {self.connections}\n"

    # for visualization we need to know
    # if the router is full, active, and inactive
    # full = red; active = yellow; inactive = grey
    def is_full(self):
        return len(self.buffer) >= self.buffer_size

    def is_active(self):
        return len(self.buffer) != 0

    # can only add and find connections
    def has_connection(self, dst):
        for connection in self.connections:
            node1, node2 = connection.jump
            if dst == node1 or dst == node2:
                return connection

        return None

    def build_connections(self, wires):
        for wire in wires:
            if self is wire.router1 or self is wire.router2:
                self.connections.append(wire)

    def build_actions(self):
        for connection in self.connections:
            r1, r2 = connection.jump
            if r1 != self.id:
                self.actions.append(r1)
            elif r2 != self.id:
                self.actions.append(r2)

    # no need for queue, just find and remove
    # todo: if this is the packet dst router, call network to remove packet from transmission

    def insert_packet(self, packet):
        if self is packet.dst:
            return True

        if not self.is_full():
            # enqueue packet
            self.buffer.append(packet)
            return True

        return False

    # push to wire
    def remove_packet(self, packet, dst):
        # if there is a connection to the destination
        # and the buffer is not empty
        # and the packet exists
        # move packet to wire
        wire = self.has_connection(dst)
        packet_index = self.find_packet(packet)
        if wire and self.buffer and packet_index != -1:
            # dequeue packet
            self.buffer.remove(packet)
            wire.insert_packet(packet)
            return wire

    def find_packet(self, packet):
        for index, p in enumerate(self.buffer):
            if p is packet:
                return index
        return -1

    # cant generate packets here, must generate from network and insert to routers
    # centralized controller controls packet path
