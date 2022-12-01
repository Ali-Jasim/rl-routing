class Wire:
    def __init__(self, router1, router2):
        # connection between two routers
        self.router1 = router1
        self.router2 = router2
        # need a tuple to jump on graph
        self.jump = (router1.id, router2.id)
        # list of packets on wire
        # acting as input buffer
        self.packets = []

    def __eq__(self, other):
        if not isinstance(self, type(other)):
            return False

        return (self.router1 is other.router1) and (self.router2 is other.router2)

    def __repr__(self):
        return f"{self.router1.id},{self.router2.id}\n"

    def find_packet(self, packet):
        for p in self.packets:
            if p is packet:
                return packet

        return None

    def is_active(self):
        return len(self.packets) != 0

    def insert_packet(self, packet):
        self.packets.append(packet)

    def remove_packet(self, packet, dst):
        p = self.find_packet(packet)

        if dst == self.router1.id:
            return self.hop(p, self.router1)
        elif dst == self.router2.id:
            return self.hop(p, self.router2)

    def hop(self, packet, dst):
        # if we successfully hopped to router, remove packet
        if packet and dst.insert_packet(packet):
            self.packets.remove(packet)
            return dst

        # operation failure, dst router congested
        return None
