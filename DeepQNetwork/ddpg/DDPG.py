import torch as T
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np



class Network(nn.Module):
    def __init__(self, lr, input_shape, action_shape, hidden_layer=128):
        super.__init__()
        self.l1 = nn.Linear(*input_shape, hidden_layer)
        self.l2 = nn.Linear(hidden_layer, action_shape)
        self.optim = optim.Adam(lr=lr)

        self.device = "cuda" if T.cuda.is_available() else "cpu"

    def forward(self, state):

        state = T.tensor(state).to(self.device)

        x = F.relu(self.l1(state))
        x = self.l2(x)

        return x


class Agent():
    def __init__(self, lr, input_shape, gamma=.99, actions=4):
        self.gamma = gamma
        self.lr = lr
        self.input_shape = input_shape
        self.reward_memory = []
        self.action_memory = []

        self.policy = Network(self.lr, input_shape, actions)

    def choose_action(self, observation):
        state = T.Tensor([observation]).to(self.policy.device)
        probs = F.softmax(self.policy.forward(state))
        action_probs = T.distributions.Categorical(probs)
        action = action_probs.sample()
        log_probs = action_probs.log_prob(action)
        self.action_memory.append(log_probs)

        return action.item()

    def store_rewards(self, reward):
        self.reward_memory.append(reward)

    def learn(self):
        self.policy.optim.zero_grad()

        # G_t = R_T+1 + gamma + R_t+2 + gamma**2 * R_t+3
        # G_t = sum from k=0 to k=t (gamma**k) + R_t+k+1

        G = np.zeros_like(self.reward_memory, dtype=np.float32)

        for t in range(len(self.reward_memory)):
            G_sum = 0
            discount = 1
            for k in range(t, len(self.reward_memory)):
                G_sum += self.reward_memory[k]
                discount *= self.gamma
            G[t] = G_sum
        G = T.tensor(G,dtype=T.float).to(self.policy.device)
        loss = 0
        for g, logprob in zip(G, self.action_memory):
            loss += -g *logprob
        
        loss.backward()
        self.policy.optim.step()

        self.action_memory = []
        self.reward_memory = []