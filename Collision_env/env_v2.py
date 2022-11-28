# create an environment using networkx simulating a network.
# required : packets that hop from router to router (node to node)
# idea : simulate centralized traffic controller
import networkx as nx
import numpy as np
import cv2
from Packet import Packet
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

FREE = "blue"
OCCUPIED = "red"
JUST_COMPLETE = "lawngreen"


class NetworkEnv():
    def __init__(self, fig=None, graph=None):
        self.nodes = len(graph.nodes)
        self.graph = graph
        # changed to list
        self.packets = []
        self.packets_on_wire = []
        self.complete = []
        self.complete_packets = 0
        # keep a list of occupied nodes
        # wires can hold multiple packets, but nodes can only hold one packet at a time
        self.occupied = [False for i in range(self.nodes)]

        nx.set_node_attributes(self.graph, {})

        # for visualization
        self.fig = fig

        if self.fig is None:
            self.fig = Figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.fig)

    def create_packets(self, n=10):
        for i in range(n):

            # if all routers are occupied, stop generating packets
            if self.all_occupied():
                break

            packet = self.generate_packet()

            if packet is None:
                continue

            self.packets.append(packet)

    def generate_packet(self):
        pass

    # cannot generate new packets when all occupied
    def all_occupied(self):
        for node in self.nodes:
            if not self.occupied[node]:
                return False
        return True

    def update_occupied(self):

        for packet in self.packets:
            # if packets current is tuple, we are on wire
            if not isinstance(packet.curr, tuple):
                self.occupied[packet.curr] = True

    # on successful packet move, update the packets location
    def update_packet_list(self, packet):
        #find and update
        for i in range(len(self.packets)):
            if self.packets[i] == packet:
                self.packets[i] = packet

    def delete_packet(self, packet):
        #find and delete
        for i in range(len(self.packets)):
            if self.packets[i] == packet:
                del self.packets[i]

    def render(self):
        pos = nx.get_node_attributes(self.graph, 'pos')

        # create list of packets
        has_packet = []
        for packet in self.packets:
            if isinstance(packet.curr, tuple):
                src, dst = packet.curr
                has_packet[(src, dst)] = True
                has_packet[(dst, src)] = True
            else:
                has_packet[packet.curr] = True

        # from original environment
        node_color = [OCCUPIED if index in has_packet else FREE
                      for index in range(self.nodes)]

        for packet in self.complete:
            node_color[packet] = JUST_COMPLETE

        edge_color = [OCCUPIED if (u, v) in has_packet else FREE
                      for (u, v) in self.graph.edges()]

        edge_weight = [3 for (u, v) in self.graph.edges()]

        options = {
            "node_color": node_color,
            "edge_color": edge_color,
            "width": edge_weight
        }

        ax = self.fig.gca()

        # draw and convert to opencv
        # use cv2.imshow(img) to display the img
        nx.draw(self.graph, pos, ax=ax, **options)
        self.canvas.draw()
        # convert to opencv image for display
        img = np.fromstring(self.canvas.tostring_rgb(), dtype=np.uint8,
                            sep='')
        img = img.reshape(self.canvas.get_width_height()[::-1] + (3,))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img

    def done(self):
        return len(self.packets.keys()) == 0

    def step(self, inputs):
        just_completed = []

        reward = 0

        moving_packets = self.packets.copy()

        # we will update this and set it
        new_packet_list = []

        while moving_packets:

            # remove packet from front of list and process movement
            # if the packets destination is a router and its occupied
            #   then append packet to end of list and give negative reward
            packet = moving_packets[0]
            moving_packets = moving_packets[1:]

            # if packet is not in the network packet list, ignore it
            if packet not in self.packets:
                continue

            # if a router contains a node, its occupied, packet waits on wire
            # append to back of list
            if packet.on_wire():
                # if the next hop is occupied
                if not self.occupied[packet.find_next_hop()]:
                    packet.continue_on_wire()
                    # if we reach dest, append to completed list for render
                    if packet.done():
                        just_completed.append(packet.dst)
                        self.complete += 1
                        reward += 1
                        self.delete_packet(packet)
                else:
                    # give negative reward and move to back of list
                    reward -= 1
                    moving_packets.append(packet)
            else:  # we are entering a wire no collision checks
                src = packet.curr
                dst = packet.dst

                wire = inputs[src][dst]

                if wire == -1 and not self.graph.has_edge(src, wire):
                    # invalid path, cant move packet
                    # packet loss?
                    continue

                packet.hop(wire, self.graph)
                new_packet_list.append(packet)

            self.update_occupied_routers()
            self.complete = just_completed

            info = []

        return self.create_observation(), reward, self.done(), info

    def reset(self, n=1):
        self.packets = []
        self.create_packets(n)
        return self.create_observation()

    def create_observation(self):
        # create adjancey matrix
        adj = np.array(nx.adjacency_matrix(self.graph).todense())

        # wire state, includes amount of packets on wire
        wires = np.array([[] for wire in self.graph.edges()])

        # occupied routers
        routers = np.array([[node, self.occupied[node]]
                           for node in self.nodes])

        # current amount of packets
        packets = np.array(len(self.packets))

        # construct routes
        routes = np.array([[packet.curr, packet.find_next_hop()]
                          for packet in self.packets])

        return (adj, wires, packets, routers, routes)
