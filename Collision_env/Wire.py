
class Wire:
    def __init__(self, src, dst):
        # connection between two routers
        self.src = src
        self.dst = dst
        # list of packets on wire
        self.packets = []

    def __eq__(self, other):
        if not isinstance(self, other):
            return False

        return (self.src == other.src) and (self.dst == other.dst)

    def find_packet(self, packet):
        for p in self.packets:
            if p == packet:
                return p

        return None

    # stack behaviour
    def insert_packet(self, packet):
        self.packets.append(packet)

    def remove_packet(self, packet):
        p = self.find_packet(packet)

        # if we successfully hopped to router, remove packet
        if self.dst.insert_packet(p) and p:
            self.packets.remove(p)
            return self.dst

        # operation failure, dst router congested
        return -1
