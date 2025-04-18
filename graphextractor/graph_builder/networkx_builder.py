import networkx as nx
from typing import Dict, Any
import copy

class NetworkXBuilder:
    """
    Class for building NetworkX graph objects from detected nodes and edges.
    """
    
    def __init__(self):
        """Initialize the NetworkX graph builder."""
        pass
    
    def build_graph(self, detection_result: Dict[str, Any]) -> nx.Graph:
        """
        Build a NetworkX graph from detector output.
        
        Args:
            detection_result: Dictionary containing nodes and edges
            
        Returns:
            NetworkX graph object
        """
        # Create a new undirected graph
        G = nx.Graph()
        for node in detection_result.get("nodes", []):
            node_attrs = {k: (list(v) if isinstance(v, tuple) else v) for k, v in node.items() if k not in ["id", "contour"]}
            # Ensure 'pos' is always a tuple of two numbers for NetworkX
            pos_val = None
            if "pos" in node_attrs:
                pos_val = node_attrs["pos"]
            elif "position" in node_attrs:
                pos_val = node_attrs["position"]
                del node_attrs["position"]
            if pos_val is not None:
                if isinstance(pos_val, (list, tuple)) and len(pos_val) == 2:
                    node_attrs["pos"] = tuple(pos_val)
                elif isinstance(pos_val, int):
                    node_attrs["pos"] = (pos_val, 0)
                else:
                    node_attrs["pos"] = (0, 0)
            G.add_node(
                node["id"],
                **node_attrs
            )
        for edge in detection_result.get("edges", []):
            edge_attrs = {k: (list(v) if isinstance(v, tuple) else v) for k, v in edge.items() if k not in ["id", "source", "target"]}
            G.add_edge(
                edge["source"],
                edge["target"],
                **edge_attrs
            )
        return G

    def save_graph(self, graph: nx.Graph, output_path: str, format: str = "gexf") -> None:
        """
        Save the graph to a file.
        Converts all tuple attributes to list for serialization.
        """
        graph_to_save = graph.copy()
        for n, attrs in graph_to_save.nodes(data=True):
            for k, v in list(attrs.items()):
                if isinstance(v, tuple):
                    attrs[k] = list(v)
        for u, v, attrs in graph_to_save.edges(data=True):
            for k, val in list(attrs.items()):
                if isinstance(val, tuple):
                    attrs[k] = list(val)
        if format == "gexf":
            nx.write_gexf(graph_to_save, output_path)
        elif format == "graphml":
            nx.write_graphml(graph_to_save, output_path)
        elif format == "gml":
            nx.write_gml(graph_to_save, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def visualize_graph(self, graph: nx.Graph, output_path: str = None, 
                       with_labels: bool = True) -> None:
        """
        Visualize the graph.
        
        Args:
            graph: NetworkX graph object
            output_path: Path to save the visualization
            with_labels: Whether to show node labels
        """
        import matplotlib.pyplot as plt
        
        # Get node positions if available
        pos = nx.get_node_attributes(graph, 'pos')
        if not pos:  # If positions not available, use spring layout
            pos = nx.spring_layout(graph)
        
        plt.figure(figsize=(12, 10))
        nx.draw(
            graph, pos, with_labels=with_labels, 
            node_size=500, node_color="lightblue", 
            font_size=10, edge_color="gray"
        )
        
        if output_path:
            plt.savefig(output_path)
        plt.show()
