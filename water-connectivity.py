import networkx as nx
import numpy as np
import rasterio
from scipy.ndimage import label

def main():
    """
    Main function to execute the connectivity calculation and print the results.
    """
    # Path to the binary image
    binary_image_path = '/Users/chollid1/Desktop/Water_coverage GeoTiff/2015.tif'
    
    # Load the binary image
    binary_image = load_binary_image(binary_image_path)
    
    # Convert the binary image to a graph
    G, labeled_array = binary_image_to_graph(binary_image)
    
    # Calculate connectivity metrics
    metrics = calculate_connectivity_metrics(G)
    
    # Print metrics
    print(f"Number of Edges: {metrics['num_edges']}")
    print(f"Largest Component Size: {metrics['largest_component_size']}")
    print(f"Number of Nodes: {metrics['num_nodes']}")
    print(f"Average Number of Node Connections: {metrics['avg_node_connections']:.2f}")
    print(f"Number of Components: {metrics['num_components']}")
    print(f"Connectivity Metric: {metrics['connectivity']:.2f}")

def load_binary_image(binary_image_path):
    """Load binary image from a GeoTIFF file."""
    try:
        with rasterio.open(binary_image_path) as src:
            binary_image = src.read(1)  # Read the first band
        return binary_image
    except Exception as e:
        print(f"Error loading image: {e}")
        raise

def binary_image_to_graph(binary_image):
    """Convert binary image to a graph representation."""
    print("Converting binary image to graph...")
    
    # Label connected components
    labeled_array, num_features = label(binary_image == 0)
    print(f"Labeled array shape: {labeled_array.shape}")
    print(f"Number of features: {num_features}")
    
    # Create a graph
    G = nx.Graph()
    
    # Add nodes and edges to the graph
    for y in range(binary_image.shape[0]):
        for x in range(binary_image.shape[1]):
            if binary_image[y, x] == 0:  # Only consider water pixels
                G.add_node((y, x))
                # Add edges to adjacent nodes
                for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < binary_image.shape[0] and 0 <= nx < binary_image.shape[1]:
                        if binary_image[ny, nx] == 0:
                            G.add_edge((y, x), (ny, nx))
    
    print(f"Number of nodes in graph: {G.number_of_nodes()}")
    print(f"Number of edges in graph: {G.number_of_edges()}")
    
    return G, labeled_array

def calculate_connectivity_metrics(G):
    """Calculate connectivity metrics for the graph."""
    try:
        num_edges = G.number_of_edges()
        largest_component_size = max(len(c) for c in nx.connected_components(G)) if G.number_of_nodes() > 0 else 0
        num_nodes = G.number_of_nodes()
        avg_node_connections = sum(deg for node, deg in G.degree()) / num_nodes if num_nodes > 0 else 0
        num_components = len(list(nx.connected_components(G)))
        connectivity = (num_edges - largest_component_size**2) / (num_nodes) * (1 + avg_node_connections / num_components) if num_nodes > 0 else 0

        return {
            'num_edges': num_edges,
            'largest_component_size': largest_component_size,
            'num_nodes': num_nodes,
            'avg_node_connections': avg_node_connections,
            'num_components': num_components,
            'connectivity': connectivity
        }
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        raise

if __name__ == "__main__":
    main()
