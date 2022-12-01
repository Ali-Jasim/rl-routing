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

        # if packet completes path, flag successful completion
        self.completed = False

        # depending on type, set buffer size
        if kind == 'T':
            # change this to hold more packets
            self.buffer_size = int(buffer_size*10)
        elif kind == 'M':
            # change this to hold more packets
            self.buffer_size = int(buffer_size*2.5)
        elif kind == 'C' or kind == 'CP':
            self.buffer_size = buffer_size

        self.buffer = []  # Queue

    def __eq__(self, other):
        if not isinstance(self, type(other)):
            return False

        return self.id == other.id

    def __repr__(self):
        return f"id: {self.id}, type: {self.kind}\n connections: {self.connections}\n"

    # for visualization we need to know
    # if the router is full, active, and inactive
    # full = red; active = yellow; inactive = grey
    # if we recieved packets destined on this step, flag completed true
    def is_full(self):
        return len(self.buffer) > self.buffer_size

    def is_active(self):
        return len(self.buffer) != 0

    def is_completed(self):
        return self.completed

    def reset_completed(self):
        self.completed = False

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

    # packet control operations
    def insert_packet(self, packet):
        # if this is the dst router, accept regardless of buffer size
        if self is packet.dst:
            self.completed = True
            return True
        elif not self.is_full():
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

            # wire.insert_packet(packet)
            return wire

    def find_packet(self, packet):
        for index, p in enumerate(self.buffer):
            if p is packet:
                return index
        return -1

    # cant generate packets here, must generate from network and insert to routers
    # centralized controller controls packet path
