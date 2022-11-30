import networkx as nx
import numpy as np

from Router import Router
from Wire import Wire
from Packet import Packet


class Network:
    def __init__(self, router_num=25, buffer_size=10):
        # initialize networkx backend
        self.network = self.init_network(router_num)

        # initialize network variables

        # all the routers and wires
        self.routers = []
        self.wires = []

        # the routers that can generate new packets
        self.customer_routers = []
        self.customer_buffer_size = buffer_size

        # total amount of packets
        self.packets = []

        self.congestion_count = 0

        self.all_router_data = np.array(self.network.nodes.data())
        self.all_connections = np.array(self.network.edges())

        # build network
        self.build_network()

    def shortest_path_step(self):
        # loop through all packets, hop on each timestep
        for packet in self.packets:
            # packet step if not complete
            if not packet.complete():
                # if the next hop routers buffer is full, packet stays on wire and retry
                # next iteration of loop
                # simulated CONGESTION!!
                # todo: add negative reward and keep track of congestion rate
                if packet.on_wire():
                    self.congestion_count += packet.push_to_router()
                else:
                    packet.push_to_wire()
            else:
                # print and remove packet on arrival
                print(packet)
                self.packets.remove(packet)

    def generate_packets(self, amount=1):
        if not amount > self.customer_buffer_size:
            for router in self.customer_routers:
                src = self.routers[router.id]
                for _ in range(amount):
                    dst = np.random.choice(self.customer_routers)
                    # dst cannot be the same src
                    # you cannot send packets to yourself
                    while src is dst:
                        dst = np.random.choice(self.customer_routers)
                    else:
                        p = Packet(src, dst, self.network)
                        self.routers[src.id].insert_packet(p)
                        self.packets.append(p)
        else:
            raise Exception(
                f"cannot generate more packets than buffer size: {self.customer_buffer_size}")

    # low level initialization details

    def init_network(self, n):
        graph = nx.random_internet_as_graph(n)
        nx.set_node_attributes(graph, {})
        return graph

    def build_network(self):
        self.build_routers(self.customer_buffer_size)
        self.build_wires()
        self.connect_routers()

    def connect_routers(self):
        for router in self.routers:
            router.build_connections(self.wires)
            router.build_actions()

    def build_routers(self, buffer_size):
        # extract data from nodes and edges and map
        for node in self.all_router_data:
            id = node[0]
            kind = node[1]['type']
            r = Router(id=id, kind=kind, network=self.network,
                       buffer_size=buffer_size)
            self.routers.append(r)

            if kind == 'C' or kind == 'CP':
                self.customer_routers.append(r)

    def build_wires(self):
        for connection in self.all_connections:
            router_id_1 = connection[0]
            router_id_2 = connection[1]
            wire = Wire(self.routers[router_id_1], self.routers[router_id_2])
            self.wires.append(wire)
