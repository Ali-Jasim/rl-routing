import networkx as nx
import numpy as np

# we need better abstractions, just packet is not enough
from Router import Router
from Wire import Wire
from Packet import Packet

# generate random internet graph that will represent our network
network = nx.random_internet_as_graph(n=25)
nx.set_node_attributes(network, {})

all_nodes_data = np.array(network.nodes.data())

all_connections = np.array(network.edges())

# create router for each node
# create a wire for each connection
# then build the network

# all the routers and wires
routers = []
wires = []

# the routers that can generate new packets
customer_routers = []
customer_buffer_size = 10

# total amount of packets
packets = []

# extract data from nodes and edges and map
for node in all_nodes_data:
    id = node[0]
    kind = node[1]['type']
    r = Router(id=id, connections=[], kind=kind, graph=network)
    routers.append(r)

    if kind == 'C' or kind == 'CP':
        customer_routers.append(r)

for connection in all_connections:
    router_id_1 = connection[0]
    router_id_2 = connection[1]
    wire = Wire(routers[router_id_1], routers[router_id_2])
    wires.append(wire)

# building the network
for router in routers:
    router.build_connections(wires)
    router.build_actions()


def generate_packets(amount=1):

    if amount > customer_buffer_size:
        raise Exception(
            f"cannot generate more packets than buffer size: {customer_buffer_size}")
    else:
        for router in customer_routers:
            src = routers[router.id]
            for _ in range(amount):
                dst = np.random.choice(customer_routers)
                # dst cannot be the same src
                # you cannot send packets to yourself
                while src is dst:
                    dst = np.random.choice(customer_routers)
                else:
                    p = Packet(src, dst, network)
                    routers[src.id].insert_packet(p)
                    packets.append(p)


generate_packets(9)

# shortest path implemented
for packet in packets:
    while not packet.complete():
        packet.push_to_wire()
        packet.push_to_router()
        print(packet)
