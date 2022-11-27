import matplotlib.pyplot as plt
import networkx as nx
from env import NetworkEnv
envq = NetworkEnv(
    graph=nx.generators.geometric.random_geometric_graph(50, 0.2))
envq.create_packets(n=10)
envq.render()
plt.show()
