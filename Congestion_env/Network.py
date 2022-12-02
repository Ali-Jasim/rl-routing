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
        self.all_actions = []
        self.buffer_sizes = []
        self.src_dst = []

        # reward for each step
        self.total_reward = 0

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
        reward = 0
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
                    packet.choose_action_shortest()
                    packet.push_to_wire()

                reward += packet.reward
            else:
                # print and remove packet on arrival
                # print(packet)
                self.packets.remove(packet)

        self.update_buffer_sizes()
        self.total_reward += reward
        return reward

    def generate_packets(self, amount=1):
        if not amount > self.customer_buffer_size:
            for router in self.customer_routers:
                src = self.routers[router.id]
                rng = np.random.randint(amount)
                for _ in range(rng):
                    dst = np.random.choice(self.customer_routers)
                    # dst cannot be the same src
                    # you cannot send packets to yourself
                    while src is dst:
                        dst = np.random.choice(self.customer_routers)
                    else:
                        p = Packet(src, dst, self.network)
                        self.routers[src.id].insert_packet(p)
                        self.packets.append(p)
            # update paths
            self.update_src_dst()
        else:
            raise Exception(
                f"cannot generate more packets than buffer size: {self.customer_buffer_size}")

    def update_packet_hop(self, packet, dst):
        for p in self.packets:
            if p == packet:
                p.update_next_hop(dst)

    def update_buffer_sizes(self):
        self.buffer_sizes = []
        for router in self.routers:
            self.buffer_sizes.append(
                [router.id, len(router.buffer), router.buffer_size])

    def update_src_dst(self):
        for packet in self.packets:
            self.src_dst.append([packet.src_id, packet.dst_id])

    # low level initialization details

    def init_network(self, n):
        G = nx.random_internet_as_graph(n)
        # for visualization we can set a layout for nodes
        pos = nx.spring_layout(G)
        nx.set_node_attributes(G, pos, "pos")
        #nx.set_node_attributes(G, {})
        # for visualization
        self.pos = nx.get_node_attributes(G, "pos")

        return G

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

        self.all_actions = [i for i in range(len(self.routers))]

    def build_wires(self):
        for connection in self.all_connections:
            router_id_1 = connection[0]
            router_id_2 = connection[1]
            wire = Wire(self.routers[router_id_1], self.routers[router_id_2])
            self.wires.append(wire)
