import torch as t
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

# plugging in a simple nueral network into this environment


class Simple_Network(nn.Module):
    def __init__(self, input_shape, actions, lr):
        super().__init__()
        self.layer1 = nn.Linear(*input_shape, 256)
        self.layer2 = nn.Linear(256, 256)
        self.layer3 = nn.Linear(256, actions)

        self.optimizer = optim.Adam(self.parameters(), lr=lr)
        self.loss = nn.MSELoss()
        self.device = 'cuda' if t.cuda.is_available() else 'cpu'
        self.to(self.device)

    def forward(self, state):
        state = t.tensor(state).to(self.device)

        l1 = F.sigmoid(self.layer1(state))
        l2 = F.sigmoid(self.layer2(l1))
        l3 = F.softmax(self.layer3(l2))

        return l3

    def learn(self, data, labels):
        self.optimizer.zero_grad()
        data = t.tensor(data).to(self.device)
        labels = t.tensor(labels).to(self.device)

        predictions = self.forward(data)

        self.loss(predictions, labels).backward()
        self.optimizer.step()
