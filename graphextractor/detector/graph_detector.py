import cv2
import numpy as np
from typing import Dict, List, Tuple, Any

class GraphDetector:
    """Main class for detecting graph structures in images."""
    
    def __init__(self, config: Dict = None):
        """
        Initialize the graph detector.
        
        Args:
            config: Configuration parameters for detection
        """
        self.config = config or {}
        
    def detect(self, image_path: str) -> Dict[str, Any]:
        """
        Detect graph structures in the given image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing detected graph elements
        """
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        # Preprocess the image
        preprocessed = self._preprocess(image)
        
        # Detect nodes
        nodes = self._detect_nodes(preprocessed)
        
        # Detect edges
        edges = self._detect_edges(preprocessed, nodes)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "image_path": image_path,
            "image_shape": image.shape
        }
    
    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocess the image for better detection."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(blurred, 0, 255, 
                                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        return binary
    
    def _detect_nodes(self, preprocessed: np.ndarray) -> List[Dict]:
        """
        Detect nodes in the preprocessed image.
        
        This is a simplified implementation. In a real application,
        this would use more sophisticated computer vision techniques.
        """
        # Find contours in the binary image
        contours, _ = cv2.findContours(
            preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        nodes = []
        for i, contour in enumerate(contours):
            # Calculate centroid of the contour
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                # Create node representation
                node = {
                    "id": i,
                    "position": (cX, cY),
                    "contour": contour.tolist(),
                    "area": cv2.contourArea(contour)
                }
                
                # Filter small contours that might be noise
                if node["area"] > 100:  # Minimum area threshold
                    nodes.append(node)
        
        return nodes
    
    def _detect_edges(self, preprocessed: np.ndarray, 
                     nodes: List[Dict]) -> List[Dict]:
        """
        Detect edges between nodes in the preprocessed image.
        
        Simplified implementation for demonstration purposes.
        """
        edges = []
        if len(nodes) <= 1:
            return edges
            
        # For simplicity, we'll connect nodes based on proximity
        # A more sophisticated approach would trace lines between nodes
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                node1 = nodes[i]
                node2 = nodes[j]
                
                # Calculate distance between nodes
                pos1 = node1["position"]
                pos2 = node2["position"]
                distance = np.sqrt((pos1[0] - pos2[0])**2 + 
                                  (pos1[1] - pos2[1])**2)
                
                # Connect only if they are close enough
                # This is a very naive approach
                if distance < 200:  # Distance threshold
                    edges.append({
                        "id": len(edges),
                        "source": node1["id"],
                        "target": node2["id"],
                        "weight": distance
                    })
        
        return edges
