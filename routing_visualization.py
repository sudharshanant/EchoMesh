import networkx as nx
import matplotlib.pyplot as plt
import random

# Create network graph
G = nx.erdos_renyi_graph(15, 0.3)

# Select source and control node
source = random.randint(0, 14)
control = 0

print("Source Node:", source)
print("Control Node:", control)

# Try to find path
try:
    path = nx.shortest_path(G, source=source, target=control)
    print("SOS Delivered!")
    print("Path:", path)
except:
    print("No Path Found!")
    path = []

# Simulate node failure
failed_node = random.randint(0, 14)
print("Node Failed:", failed_node)

if failed_node in G:
    G.remove_node(failed_node)

# Check again after failure
try:
    new_path = nx.shortest_path(G, source=source, target=control)
    print("SOS Delivered After Failure!")
    print("New Path:", new_path)
except:
    print("Network Broken After Failure!")
    new_path = []

# Visualization
pos = nx.spring_layout(G, seed=42)

node_colors = []
for node in G.nodes():
    if node == source:
        node_colors.append("blue")      # Source
    elif node == control:
        node_colors.append("yellow")    # Control node
    else:
        node_colors.append("lightgray") # Other nodes

nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=700)

# Highlight original path
if path:
    edge_list = list(zip(path, path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=edge_list, width=3, edge_color="green")

# Highlight new path after failure
if new_path:
    edge_list2 = list(zip(new_path, new_path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=edge_list2, width=3, edge_color="red")

plt.title("EchoMesh Emergency Routing with Node Failure")
plt.show()
