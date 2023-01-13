# environment libraries
from Network import Network
import networkx as nx
import numpy as np
from DDQN import Agent


# visualization libraries
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import cv2


class env:
    def __init__(self, num_routers=25, customer_buffer_size=10):
        # initialize network environment
        self.network = Network(num_routers, customer_buffer_size)
        self.num_routers = num_routers
        self.customer_buffer_size = customer_buffer_size

        # visualization
        self.fig = Figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.fig)

    def render(self, mode='opencv'):
        # two modes, matplotlib and opencv

        # matplotlib for jupyter notebook environment
        # opencv for python environment
        # always return matrix representing image of network graph

        # for routers in network
        ACTIVE_ROUTER = 'yellow'
        INACTIVE_ROUTER = 'grey'
        FULL = 'red'
        COMPLETED = 'lawngreen'

        # for wires in network
        ACTIVE_WIRE = 'green'
        INACTIVE_WIRE = 'blue'

        node_color = []
        for router in self.network.routers:
            if router.is_full():
                node_color.append(FULL)
            elif router.is_completed():
                node_color.append(COMPLETED)
                router.reset_completed()
            elif router.is_active():
                node_color.append(ACTIVE_ROUTER)
            else:
                node_color.append(INACTIVE_ROUTER)

        edge_color = []
        for wire in self.network.wires:
            if wire.is_active():
                edge_color.append(ACTIVE_WIRE)
            else:
                edge_color.append(INACTIVE_WIRE)

        edge_weight = [2 for _ in range(len(self.network.wires))]

        options = {
            "node_color": node_color,
            "edge_color": edge_color,
            "width": edge_weight,
        }
        # generate image and return
        ax = self.fig.gca()
        nx.draw(self.network.network, pos=self.network.pos, ax=ax, **options)
        self.canvas.draw()

        if mode == 'opencv':
            # convert to opencv image for display
            img = np.fromstring(self.canvas.tostring_rgb(), dtype=np.uint8,
                                sep='')
            img = img.reshape(self.canvas.get_width_height()[::-1] + (3,))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif mode == 'matplotlib':
            # convert to matplotlib img
            s, (width, height) = self.canvas.print_to_buffer()
            img = np.fromstring(s, np.uint8).reshape((height, width, 4))

        return img

    def reset(self):
        self.network.packets = []

        for router in self.network.routers:
            router.clear_buffer()

        for wire in self.network.wires:
            wire.clear_buffer()

        self.network.generate_packets(self.customer_buffer_size - 1)
        self.network.congestion_count = 0

        return self.create_observation()

    # action here will be a list of packets and next hop

    def step(self, custom=False, packet=None):
        # our agent takes a step
        if custom:
            reward, done, packet = self.network.step(packet)
        else:
            # just take shortest path
            reward = self.network.shortest_path_step()

        return self.create_observation(), reward, done, packet

    def done(self):
        return len(self.network.packets) == 0

    # return list of all actions, buffer sizes, src id, dst id
    # return state of network, and anything related to the packets

    def create_observation(self):

        Router_states = np.array(self.network.buffer_sizes, dtype=np.float32)

        # convert to tensor
        return Router_states

    # attempt #1, choose action for every packet on every timestep
    def get_actions(self):
        all_packets = []

        for packet in self.network.packets:
            # if packet.on_router():
            all_packets.append(
                [packet, packet.src, packet.dst, packet.curr_router.actions])

            # if packet.on_wire():
            #     packet.push_to_router()

        return all_packets

    # for each router, choose action

    def choose_action(self, packet, dst):
        self.network.update_packet_hop(packet, dst)


# Example usage
if __name__ == '__main__':
    e = env(15, 100)
    observation = e.reset()
    episodes = 10

    brain = Agent(len(e.network.network.nodes),
                  (30,), 1, 512, batch_size=50, lr=0.05, gamma=0.99, replace_thresh=10,
                  buffer_size=5000000)

    print(observation)
    print(e.network.packets[0].src_id)
