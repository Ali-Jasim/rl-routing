class Wire:
    def __init__(self, router1, router2):
        # connection between two routers
        self.router1 = router1
        self.router2 = router2
        # list of packets on wire
        # acting as input buffer
        self.packets = []

    def __eq__(self, other):
        if not isinstance(self, other):
            return False

        return (self.router1 == other.router1) and (self.router2 == other.router2)

    def __repr__(self):
        return f"{self.router1.id},{self.router2.id}\n"

    def find_packet(self, packet):
        for p in self.packets:
            if p is packet:
                return p

        return None

    # Queue behaviour
    def insert_packet(self, packet):
        self.packets.append(packet)

    def remove_packet(self, packet, dst):
        p = self.find_packet(packet)

        if dst is self.router1:
            self.hop(p, self.router1)
        elif dst is self.router2:
            self.hop(p, self.router2)

    def hop(self, packet, dst):
        # if we successfully hopped to router, remove packet
        if packet and dst.insert_packet(packet):
            packet.push_to_router(dst)
            self.packets.remove(packet)
            return self.dst

        # operation failure, dst router congested
        return -1
