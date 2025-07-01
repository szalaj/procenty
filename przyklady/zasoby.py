import numpy as np
from dataclasses import dataclass
import networkx as nx

# tutaj będą klasy związane z obsługą podstawywych obszarów gospodarczych - zon

def merge_nodes(G, node1, node2, merged_node_id=None):
    """
    Merge two nodes in a graph G.
    
    Parameters:
    - G: NetworkX graph
    - node1, node2: Nodes to merge
    - merged_node_id: ID for the new merged node (default: 'node1_node2')
    
    Returns:
    - Modified graph with merged nodes
    """
    if merged_node_id is None:
        merged_node_id = f"{node1}_{node2}"
    
    # Create a copy of the graph to avoid modifying the original during iteration
    G_new = G.copy()
    
    # Add the new merged node
    G_new.add_node(merged_node_id)
    
    # Combine node attributes
    for attr in G_new.nodes[node1]:
        if attr in G_new.nodes[node2]:
            # For dictionaries like 'zasoby', combine them
            if isinstance(G_new.nodes[node1][attr], dict) and isinstance(G_new.nodes[node2][attr], dict):
                G_new.nodes[merged_node_id][attr] = {}
                for key in set(G_new.nodes[node1][attr].keys()) | set(G_new.nodes[node2][attr].keys()):
                    G_new.nodes[merged_node_id][attr][key] = G_new.nodes[node1][attr].get(key, 0) + G_new.nodes[node2][attr].get(key, 0)
            # For numeric values like 'produkcja', sum them
            elif isinstance(G_new.nodes[node1][attr], (int, float)) and isinstance(G_new.nodes[node2][attr], (int, float)):
                G_new.nodes[merged_node_id][attr] = G_new.nodes[node1][attr] + G_new.nodes[node2][attr]
            # For other attributes, use the value from node1
            else:
                G_new.nodes[merged_node_id][attr] = G_new.nodes[node1][attr]
    
    # Connect the merged node to all neighbors of both original nodes
    for neighbor in set(G_new.neighbors(node1)) | set(G_new.neighbors(node2)):
        if neighbor != node1 and neighbor != node2:  # Avoid self-loops
            G_new.add_edge(merged_node_id, neighbor)
    
    # Remove the original nodes
    G_new.remove_node(node1)
    G_new.remove_node(node2)
    
    return G_new


class Zona:
    pass

class HexZona(Zona):
    pass

@dataclass
class GPol:
    name: str
    value: int = 0




