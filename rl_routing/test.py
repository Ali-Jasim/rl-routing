from env import NetworkEnv
import networkx as nx
from matplotlib import pyplot as plt
import numpy as np
import cv2
from matplotlib.figure import Figure
from collections import defaultdict
import seaborn as sns

G = nx.random_internet_as_graph(100)
pos = nx.spring_layout(G)
nx.set_node_attributes(G, pos, "pos")


class ShortestPathAgent():
    def actions(self, observation):
        actions = -1*np.ones((len(G.nodes), len(G.nodes)), dtype=np.int32)
        adj_matrix, wires, packets, routes = observation
        # shortest path routes are returned as part of observation
        # as a baseline we construct an action based on this
        for f in routes.keys():
            for t in routes[f].keys():
                actions[f][t] = routes[f][t]
        return actions

# using opencv to draw pictures for display
#todo add functionality to conintously generate packets, but only from nodes that are NOT occupied.

def draw_output(img):
    cv2.imshow('img', img)
    cv2.waitKey()


env = NetworkEnv(graph=G, fig=Figure(figsize=(6, 6)))
i = 100

agent = ShortestPathAgent()
observation = env.reset(initial_packets=5)

total_rewards = []
total_collisions = []

for s in range(1000):

    actions = agent.actions(observation)
    # actions is a list of steps to be taken for each node
    # the packet with the highest value (earliest created) is sent based on step's input
    observation, reward, done, info = env.step(actions)

    img = env.render()
    draw_output(img)
    print("Step Reward", reward)
    print("Total Reward", env.completed_packets)
    print('total collisions,', env.collisions)
    print(f"Step {s}/1000")

    total_rewards.append(env.completed_packets)
    total_collisions.append(env.collisions)
    env.collisions = 0

    # Give a more efficient the agent to achieve more score
    if env.done():
        print('finished')
        break
    if s % 2 == 0:
        env.create_packets(n=5)


sns.lineplot(x=range(len(total_collisions)), y=total_collisions)
plt.xlabel("Step")
plt.ylabel("collisions")
plt.show()
print(f"Solved in {len(total_rewards)} steps")
