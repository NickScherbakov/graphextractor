import numpy as np
from typing import Dict, List, Any, Tuple

class TextMapper:
    """Class for mapping recognized text to graph elements."""
    
    def __init__(self, proximity_threshold: float = 50.0):
        """
        Initialize the text mapper.
        
        Args:
            proximity_threshold: Maximum distance between text and node to be considered related
        """
        self.proximity_threshold = proximity_threshold
    
    def map_text_to_nodes(self, 
                          nodes: List[Dict[str, Any]], 
                          text_regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map text regions to nodes based on proximity.
        
        Args:
            nodes: List of detected nodes
            text_regions: List of detected text regions
            
        Returns:
            Nodes with mapped text labels
        """
        # Create a copy of nodes to add text attributes
        labeled_nodes = []
        
        for node in nodes:
            node_copy = node.copy()
            node_position = node["position"]
            print(f"DEBUG: text_mapper node['position'] type={type(node_position)}, value={node_position}")
            # Ensure node_position is valid
            if not (isinstance(node_position, (list, tuple)) and len(node_position) == 2):
                node_position = (0, 0)
            closest_text = None
            min_distance = float('inf')
            
            # Find closest text region
            for text_region in text_regions:
                text_centroid = text_region["centroid"]
                
                # Calculate distance
                distance = np.sqrt(
                    (node_position[0] - text_centroid[0])**2 + 
                    (node_position[1] - text_centroid[1])**2
                )
                
                # Update closest text if this one is closer
                if distance < min_distance and distance < self.proximity_threshold:
                    min_distance = distance
                    closest_text = text_region
            
            # Add label information if found
            if closest_text:
                node_copy["label"] = closest_text["text"]
                node_copy["label_confidence"] = closest_text["confidence"]
                node_copy["label_id"] = closest_text["id"]
                node_copy["label_distance"] = min_distance
            else:
                node_copy["label"] = ""
                
            labeled_nodes.append(node_copy)
            
        return labeled_nodes
    
    def map_text_to_edges(self, 
                          edges: List[Dict[str, Any]], 
                          text_regions: List[Dict[str, Any]],
                          nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map text regions to edges based on proximity to midpoints.
        
        Args:
            edges: List of detected edges
            text_regions: List of detected text regions
            nodes: List of detected nodes (needed to compute edge midpoints)
            
        Returns:
            Edges with mapped text labels
        """
        # Create a dictionary for quick node lookup
        node_dict = {node["id"]: node for node in nodes}
        
        # Create a copy of edges to add text attributes
        labeled_edges = []
        
        for edge in edges:
            edge_copy = edge.copy()
            
            # Get source and target nodes
            source_node = node_dict.get(edge["source"])
            target_node = node_dict.get(edge["target"])
            
            if source_node and target_node:
                # DEBUG: print type and value of source_pos and target_pos
                print(f"DEBUG: text_mapper source_pos type={type(source_node['position'])}, value={source_node['position']}")
                print(f"DEBUG: text_mapper target_pos type={type(target_node['position'])}, value={target_node['position']}")
                # Calculate midpoint of the edge
                source_pos = source_node["position"]
                target_pos = target_node["position"]
                # Ensure both are valid (list/tuple of length 2)
                if not (isinstance(source_pos, (list, tuple)) and len(source_pos) == 2):
                    source_pos = (0, 0)
                if not (isinstance(target_pos, (list, tuple)) and len(target_pos) == 2):
                    target_pos = (0, 0)
                midpoint = (
                    (source_pos[0] + target_pos[0]) // 2,
                    (source_pos[1] + target_pos[1]) // 2
                )
                
                closest_text = None
                min_distance = float('inf')
                
                # Find closest text region to the midpoint
                for text_region in text_regions:
                    text_centroid = text_region["centroid"]
                    
                    # Calculate distance
                    distance = np.sqrt(
                        (midpoint[0] - text_centroid[0])**2 + 
                        (midpoint[1] - text_centroid[1])**2
                    )
                    
                    # Update closest text if this one is closer
                    if distance < min_distance and distance < self.proximity_threshold:
                        min_distance = distance
                        closest_text = text_region
                
                # Add midpoint to edge data
                edge_copy["midpoint"] = midpoint
                
                # Add label information if found
                if closest_text:
                    edge_copy["label"] = closest_text["text"]
                    edge_copy["label_confidence"] = closest_text["confidence"]
                    edge_copy["label_id"] = closest_text["id"]
                    edge_copy["label_distance"] = min_distance
                else:
                    edge_copy["label"] = ""
            
            labeled_edges.append(edge_copy)
            
        return labeled_edges
