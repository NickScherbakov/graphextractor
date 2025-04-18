import cv2
import numpy as np
from typing import Dict, List, Tuple, Any

# Импортируем новые модули
from ..preprocessing import ImageEnhancer, QualityAnalyzer
from ..text_recognition import OCRProcessor, TextMapper
from ..caching import CacheManager, ImageHashProvider

class GraphDetector:
    """Main class for detecting graph structures in images."""
    
    def __init__(self, config: Dict = None):
        """
        Initialize the graph detector.
        
        Args:
            config: Configuration parameters for detection
        """
        self.config = config or {}
        
        # Initialize preprocessing components
        self.enhancer = ImageEnhancer(self.config.get("enhancer", {}))
        self.quality_analyzer = QualityAnalyzer()
        
        # Initialize text recognition if enabled
        self.ocr_enabled = self.config.get("ocr_enabled", True)
        if self.ocr_enabled:
            self.ocr_processor = OCRProcessor(
                languages=self.config.get("ocr_languages", ["en"]),
                gpu=self.config.get("use_gpu", False)
            )
            self.text_mapper = TextMapper(
                proximity_threshold=self.config.get("text_proximity_threshold", 50.0)
            )
        
        # Initialize caching if enabled
        self.caching_enabled = self.config.get("caching_enabled", True)
        if self.caching_enabled:
            self.cache_manager = CacheManager(
                cache_dir=self.config.get("cache_dir", "cache"),
                redis_url=self.config.get("redis_url", None),
                ttl=self.config.get("cache_ttl", 3600)
            )
            self.hash_provider = ImageHashProvider()
        
    def detect(self, image_path: str) -> Dict[str, Any]:
        """
        Detect graph structures in the given image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing detected graph elements
        """
        # Check cache first if enabled
        if self.caching_enabled:
            # Load image for hash calculation
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Generate hash for the image
            image_hash = self.hash_provider.compute_hash(image)
            
            # Look up in cache
            cached_result = self.cache_manager.get(image_hash)
            if cached_result:
                print(f"Using cached result for image: {image_path}")
                return cached_result
        else:
            # Load the image if not already loaded for caching
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
        # Analyze image quality
        quality_info = self.quality_analyzer.analyze(image)
        print(f"Image quality: {quality_info['quality_level']} (score: {quality_info['quality_score']})")
        
        # Apply appropriate preprocessing based on quality
        if quality_info['quality_score'] < 2:  # Low or very low quality
            print("Applying adaptive enhancement for low quality image")
            preprocessed = self.enhancer.apply_adaptive_enhancement(image)
        else:
            # Standard preprocessing for higher quality images
            preprocessed = self._preprocess(image)
            
        # Extract text if OCR is enabled
        text_regions = []
        if self.ocr_enabled:
            print("Extracting text with OCR...")
            text_regions = self.ocr_processor.extract_text(image)
            text_regions = self.ocr_processor.filter_text_by_size(
                text_regions, 
                min_confidence=self.config.get("min_text_confidence", 0.3)
            )
            print(f"Found {len(text_regions)} text regions")
        
        # Detect nodes
        nodes = self._detect_nodes(preprocessed)
        
        # Map text to nodes if available
        if self.ocr_enabled and text_regions:
            nodes = self.text_mapper.map_text_to_nodes(nodes, text_regions)
        
        # Detect edges
        edges = self._detect_edges(preprocessed, nodes)
        
        # Map text to edges if available
        if self.ocr_enabled and text_regions:
            edges = self.text_mapper.map_text_to_edges(edges, text_regions, nodes)
        
        # Prepare result
        result = {
            "nodes": nodes,
            "edges": edges,
            "image_path": image_path,
            "image_shape": image.shape,
            "quality_info": quality_info
        }
        
        if self.ocr_enabled:
            result["text_regions"] = text_regions
        
        # Cache result if enabled
        if self.caching_enabled:
            self.cache_manager.set(image_hash, result)
            
        return result
    
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
                # DEBUG: print detected node position
                print(f"DEBUG: _detect_nodes node position = ({cX}, {cY})")
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
                print(f"DEBUG: _detect_edges pos1 type={type(pos1)}, value={pos1}; pos2 type={type(pos2)}, value={pos2}")
                # ...existing code...
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
