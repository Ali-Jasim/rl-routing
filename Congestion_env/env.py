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

    def reset(self):
        self.network.packets = []

        for i, router in enumerate(self.network.routers):
            self.network.routers[i].clear_buffer()

        for i, wire in enumerate(self.network.wires):
            self.network.wires[i].clear_buffer()

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
            if packet.on_router():
                all_packets.append(
                    [packet, packet.src, packet.dst, packet.curr.actions])

            if packet.on_wire():
                packet.push_to_router()

        return all_packets

    # we can only choose actions when the packet is at a router

    def choose_action(self, packet, dst):
        self.network.update_packet_hop(packet, dst)


# Example usage
if __name__ == '__main__':
    e = env(50, 5)
    observation = e.reset()
    episodes = 10
    print(observation.shape)
    brain = Agent(len(e.network.network.nodes),
                  (100,), 1, 256, batch_size=512, lr=0.05, gamma=0.9, replace_thresh=10)

    congestions = []
    steps = []
    eps = []

    for ep in range(episodes):
        #ep = 0
        n = 0
        while not e.done():
            cv2.imshow("network", e.render(mode='opencv'))
            cv2.waitKey(1)
            rewards = 0
            step_count = 0
            if e.get_actions():

                for action in e.get_actions():

                    packet = action[0]
                    a = action[1].actions
                    s = action[1].id
                    d = action[2].id

                    state_mask = [True for _ in range(
                        (len(e.network.network.nodes,)))]

                    state_mask = np.array(state_mask)

                    state_mask[a] = False

                    observation[state_mask, 0] = s
                    observation[state_mask, 1] = d

                    state = np.array(
                        observation, dtype=np.float32).flatten()

                    action = brain.choose_action(state)

                    e.choose_action(packet, action)

                    observation, reward, done, packet = e.step(
                        custom=True, packet=packet)

                    if packet:
                        a = packet.curr_router.actions
                        d = [packet.dst.id]
                        s = [packet.src.id]

                    state_mask = [True for _ in range(
                        (len(e.network.network.nodes,)))]

                    state_mask = np.array(state_mask)

                    state_mask[a] = False
                    state_mask[d] = False

                    observation[state_mask, 0] = s
                    observation[state_mask, 1] = d

                    next_state = np.array(
                        observation, dtype=np.float32).flatten()

                    rewards += reward

                    brain.store_transition(
                        state, float(action), float(rewards), next_state, float(done))

            brain.learn()
            n += 1
            if n % 500 == 0:
                observation = e.reset()

                n = 0
                ep += 1

            print(
                f"step: {n} step rewards: {rewards}, packets: {len(e.network.packets)}")
            rewards = 0

        steps.append(n)
        congestions.append(e.network.congestion_count)
        eps.append(1)
        e.reset()

    print(f"completed in {np.mean(n)} timesteps")
    print(f"Congestions encountered: {np.mean(congestions)}")
