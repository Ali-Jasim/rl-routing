# environment libraries
from Network import Network
import networkx as nx
import numpy as np

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

    def reset(self):
        self.network.generate_packets(self.customer_buffer_size - 1)
        self.network.congestion_count = 0

        return self.create_observation()

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

    # action here will be a list of packets and next hop
    def step(self, custom=False):
        # our agent takes a step
        if custom:
            return
        else:
            # just take shortest path
            reward = self.network.shortest_path_step()

        info = []
        return self.create_observation(), reward, self.done(), info

    def done(self):
        return len(self.network.packets) == 0

    # return list of all actions, buffer sizes, src id, dst id
    # return state of network, and anything related to the packets

    def create_observation(self):

        # this shows connectivity of graph
        # good repersentation for neural network
        adj_matrix = np.array(nx.adjacency_matrix(self.network.network))
        # grab buffer_sizes in network
        buffers = np.array(self.network.buffer_sizes)
        # grab all packets src and dst
        packet_path = np.array(self.network.src_dst)
        # grab all actions
        all_actions = np.array(self.network.all_actions)

        # convert to tensor
        return np.array([adj_matrix, buffers, all_actions, packet_path])

    # attempt #1, choose action for every packet on every timestep
    def get_actions(self):
        all_packets = np.array(self.network.packets)

        return all_packets

    def choose_action(self, packet, dst):
        self.network.update_packet_hop(packet, dst)

# todo : add customizable agent


if __name__ == '__main__':
    e = env(25, 10)
    # e.reset()
    episodes = 10

    congestions = []
    steps = []
    eps = []

    for ep in range(episodes):
        e.reset()
        n = 0
        while not e.done():
            cv2.imshow("network", e.render(mode='opencv'))
            cv2.waitKey()
            print(e.step(None))
            n += 1

        steps.append(n)
        congestions.append(e.network.congestion_count)
        eps.append(1)

    # plot results
    plt.plot(eps, steps)
    plt.plot(eps, congestions)

    plt.tight_layout()
    plt.show()

    print(f"completed in {np.mean(n)} timesteps")
    print(f"Congestions encountered: {np.mean(congestions)}")
