import cv2
import numpy as np
from typing import Dict, List, Tuple

class NodeDetector:
    """Class for detecting nodes in graph images."""
    
    def __init__(self, min_area: int = 100, max_area: int = 10000,
                 circularity_threshold: float = 0.7):
        """
        Initialize the node detector.
        
        Args:
            min_area: Minimum contour area to consider
            max_area: Maximum contour area to consider
            circularity_threshold: Threshold for determining if a contour is circular
        """
        self.min_area = min_area
        self.max_area = max_area
        self.circularity_threshold = circularity_threshold
    
    def detect(self, image: np.ndarray) -> List[Dict]:
        """
        Detect nodes in the image.
        
        Args:
            image: Input image (grayscale or binary)
            
        Returns:
            List of detected nodes with properties
        """
        # Ensure the image is grayscale
        if len(image.shape) > 2:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find contours
        contours, _ = cv2.findContours(
            binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        
        nodes = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Filter by area
            if self.min_area < area < self.max_area:
                # Calculate circularity
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                else:
                    circularity = 0
                
                # Calculate centroid
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    
                    # Create node object
                    node = {
                        "id": i,
                        "position": (cX, cY),
                        "area": area,
                        "circularity": circularity,
                        "bounding_box": cv2.boundingRect(contour),
                        "is_likely_node": circularity > self.circularity_threshold
                    }
                    nodes.append(node)
        
        return nodes
