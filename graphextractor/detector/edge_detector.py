import cv2
import numpy as np
from typing import Dict, List, Tuple
from skimage.morphology import skeletonize
from skimage import img_as_bool, img_as_ubyte

class EdgeDetector:
    """Class for detecting edges connecting nodes in graph images."""
    
    def __init__(self, line_thickness_threshold: int = 5):
        """
        Initialize the edge detector.
        
        Args:
            line_thickness_threshold: Maximum thickness to consider as a line
        """
        self.line_thickness_threshold = line_thickness_threshold
    
    def detect(self, image: np.ndarray, nodes: List[Dict]) -> List[Dict]:
        """
        Detect edges between nodes in the image.
        
        Args:
            image: Input image
            nodes: List of detected nodes
            
        Returns:
            List of detected edges
        """
        # Convert to grayscale if needed
        if len(image.shape) > 2:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Preprocess for line detection
        _, binary = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        
        # Create a mask for nodes to exclude them from edge detection
        node_mask = np.zeros_like(binary)
        for node in nodes:
            if node.get("is_likely_node", True):
                x, y, w, h = node["bounding_box"]
                # Add padding around the node
                padding = 5
                x_min = max(0, x - padding)
                y_min = max(0, y - padding)
                x_max = min(binary.shape[1], x + w + padding)
                y_max = min(binary.shape[0], y + h + padding)
                node_mask[y_min:y_max, x_min:x_max] = 255
        
        # Subtract nodes from binary image
        edges_only = cv2.subtract(binary, node_mask)
        
        # Skeletonize to thin the lines
        skeleton = skeletonize(img_as_bool(edges_only))
        skeleton_img = img_as_ubyte(skeleton)
        
        # Use HoughLinesP to detect line segments
        lines = cv2.HoughLinesP(
            skeleton_img, 1, np.pi/180, 
            threshold=10, minLineLength=30, maxLineGap=10
        )
        
        edges = []
        if lines is not None:
            for i, line in enumerate(lines):
                x1, y1, x2, y2 = line[0]
                
                # Find which nodes this line connects
                source_node = None
                target_node = None
                min_start_dist = float('inf')
                min_end_dist = float('inf')
                
                for node in nodes:
                    # DEBUG: print node position type and value
                    print(f"DEBUG: node['position'] type={type(node['position'])}, value={node['position']}")
                    node_pos = node["position"]
                    if not (isinstance(node_pos, (list, tuple)) and len(node_pos) == 2):
                        node_pos = (0, 0)
                    node_x, node_y = node_pos
                    
                    # Calculate distance to line start
                    start_dist = np.sqrt((node_x - x1)**2 + (node_y - y1)**2)
                    if start_dist < min_start_dist:
                        min_start_dist = start_dist
                        source_node = node["id"]
                        
                    # Calculate distance to line end
                    end_dist = np.sqrt((node_x - x2)**2 + (node_y - y2)**2)
                    if end_dist < min_end_dist:
                        min_end_dist = end_dist
                        target_node = node["id"]
                
                # Only add valid edges
                if source_node is not None and target_node is not None and source_node != target_node:
                    # Calculate edge length
                    edge_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    
                    edges.append({
                        "id": i,
                        "source": source_node,
                        "target": target_node,
                        "weight": edge_length,
                        "points": [(x1, y1), (x2, y2)]
                    })
        
        return edges
