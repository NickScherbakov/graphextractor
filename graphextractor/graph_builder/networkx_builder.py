import networkx as nx
from typing import Dict, Any

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
        
        # Add nodes to the graph
        for node in detection_result.get("nodes", []):
            G.add_node(
                node["id"],
                pos=node["position"],
                area=node["area"],
                **{k: v for k, v in node.items() if k not in ["id", "position", "area", "contour"]}
            )
        
        # Add edges to the graph
        for edge in detection_result.get("edges", []):
            G.add_edge(
                edge["source"],
                edge["target"],
                weight=edge["weight"],
                **{k: v for k, v in edge.items() if k not in ["id", "source", "target", "weight"]}
            )
        
        return G
    
    def save_graph(self, graph: nx.Graph, output_path: str, format: str = "gexf") -> None:
        """
        Save the graph to a file.
        
        Args:
            graph: NetworkX graph object
            output_path: Path to save the graph
            format: Format to save (gexf, graphml, gml, etc.)
        """
        if format == "gexf":
            nx.write_gexf(graph, output_path)
        elif format == "graphml":
            nx.write_graphml(graph, output_path)
        elif format == "gml":
            nx.write_gml(graph, output_path)
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
