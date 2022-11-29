import networkx as nx
import numpy as np
from router import Router
from wire import Wire
from packet import Packet

G = nx.random_internet_as_graph(n=25)
nx.set_node_attributes(G, {})

all_nodes_data = np.array(G.nodes.data())

all_connections = np.array(G.edges())

# create router for each node
# create a wire for each connection
# then build the network
routers = []
wires = []

# building the network
# extract data from nodes and edges and map
for node in all_nodes_data:
    id = node[0]
    kind = node[1]['type']
    routers.append(Router(id=id, connections=None, kind=kind, graph=G))

for connection in all_connections:
    router_id_1 = connection[0]
    router_id_2 = connection[1]
    wire = Wire(routers[router_id_1], routers[router_id_2])
    wires.append(wire)

for router in routers:
    router.add_connections(wires)

print(routers)

# todo: generate packets
# possible idea: CP (Content providers) produce more traffic
