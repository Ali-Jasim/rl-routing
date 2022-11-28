import networkx as nx
import random
from collections import defaultdict, OrderedDict
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import cv2

from packet import Packet

FREE = "blue"
OCCUPIED = "red"
JUST_COMPLETE = "lawngreen"


class NetworkEnv():
    def __init__(self, fig=None, graph=None):
        self.nodes = len(graph.nodes)
        self.graph = graph
        self.packets = OrderedDict()
        self.just_completed = []
        self.completed_packets = 0
        self.occupied = {}
        self.occupied_nodes = {}
        self.collisions = 0

        self.fig = fig
        if self.fig is None:
            self.fig = Figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.fig)

        nx.set_node_attributes(self.graph, {})

    def generate_packet(self):

        sender = random.choice(range(self.nodes))
        while (sender in self.occupied):
            sender = random.choice(range(self.nodes))
        else:

            to = random.choice(range(self.nodes))
            path = nx.shortest_path(self.graph, sender, to)
            return Packet(sender, to, path=path)

    def create_packets(self, n=10):
        for _ in range(n):
            p = self.generate_packet()
            if p is None:
                continue
            self.packets[p.id] = p

    def create_packet_avoid(self):
        if not self.all_occupied():
            self.create_packets(n=10)

    # keep track of occupied nodes
    def update_occupied(self):

        #
        for packet in self.packets.values():
            if isinstance(packet.current, tuple):
                f, t = packet.current
                self.occupied[(f, t)] = True
                self.occupied[(t, f)] = True
            else:
                self.occupied[packet.current] = True

        return self.occupied

    def update_occupied_nodes(self):
        self.occupied_nodes = [True if index in self.occupied else False
                               for index in range(self.nodes)]

    def all_occupied(self):

        for node in self.occupied_nodes:
            if not node:
                return False
        return True

    def render(self, mode="rgb"):
        if mode == "rgb":
            pos = nx.get_node_attributes(self.graph, 'pos')
            occupied = {}
            for packet in self.packets.values():
                if isinstance(packet.current, tuple):
                    f, t = packet.current
                    occupied[(f, t)] = True
                    occupied[(t, f)] = True
                else:
                    occupied[packet.current] = True

            node_color = [
                OCCUPIED if index in occupied else FREE
                for index in range(self.nodes)
            ]
            for nid in self.just_completed:
                node_color[nid] = JUST_COMPLETE

            edge_color = [OCCUPIED if (u, v) in occupied else FREE for (
                u, v) in self.graph.edges()]
            edge_weight = [3 for (u, v) in self.graph.edges()]

            options = {
                "node_color": node_color,
                "edge_color": edge_color,
                "width": edge_weight,
            }
            ax = self.fig.gca()
            nx.draw(self.graph, pos, ax=ax, **options)
            self.canvas.draw()
            # convert to opencv image for display
            img = np.fromstring(self.canvas.tostring_rgb(), dtype=np.uint8,
                                sep='')
            img = img.reshape(self.canvas.get_width_height()[::-1] + (3,))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            return img
        raise f"Mode {mode} not supported."

    def done(self):
        return len(self.packets.keys()) == 0

    def step(self, inputs):
        wires = defaultdict(lambda: defaultdict(lambda: False))
        just_completed = []

        reward = 0
        for packet in self.packets.values():
            if isinstance(packet.current, tuple):
                f, t = packet.current
                wires[f][t] = True

        for packet_key in list(self.packets.keys()):
            if packet_key not in self.packets:
                continue
            packet = self.packets[packet_key]
            continue_check = False

            # check if on wire
            if packet.on_wire():
                packet.continue_on_wire(self.graph)
                continue_check = True

            if packet.done():
                just_completed.append(packet.to)
                del self.packets[packet.id]
                reward += 1
                continue_check = True

            if continue_check:
                continue

            cur = packet.current
            to = packet.to
            n = inputs[cur][to]

            # detect collision
            if to in self.occupied:
                # reward -= 1
                self.collisions += 1

            if n == -1:
                continue
            if not self.graph.has_edge(cur, n):
                # refuse to route invalid paths
                continue
            if wires[cur][n]:
                continue

            wires[cur][n] = True

            packet.hop(n, self.graph)
            self.update_occupied()
            self.update_occupied_nodes()

        self.just_completed = just_completed
        self.completed_packets += reward

        info = {}

        return self.create_observation(), reward, self.done(), info

    def reset(self, initial_packets=1):
        self.packets = OrderedDict()
        self.create_packets(initial_packets)
        return self.create_observation()

    def create_observation(self):
        # create one hot adjacency matrix
        adj_matrix = np.array(nx.adjacency_matrix(self.graph).todense())
        wires = np.zeros((self.nodes, self.nodes))
        packets = np.zeros((self.nodes, self.nodes))
        routes = defaultdict(dict)

        packets_vals = self.packets.values()
        for i, packet in enumerate(packets_vals):
            val = (i+1)/len(packets_vals)
            if isinstance(packet.current, tuple):
                f, t = packet.current
                wires[f][t] = 1.0
                continue
            elif packet.done():
                continue
            else:
                routes[packet.current][packet.to] = packet.find_next_hop()
                packets[packet.current][packet.to] = val

        return (adj_matrix, wires, packets, routes)
