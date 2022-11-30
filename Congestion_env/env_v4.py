from Network import Network

N = Network()

N.generate_packets(9)
n = 0

# on each timestep, packets all packets try to move to dst
while N.packets:
    # prints packets when they arrive at destination
    N.shortest_path_step()
    n += 1

print(f"completed in {n} timesteps")
print(f"Congestions encountered: {N.congestion_count}")
