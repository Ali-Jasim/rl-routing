from Network import Network

N = Network()

N.generate_packets(9)

while N.packets:
    # prints packets when they arrive at destination
    N.shortest_path_step()
