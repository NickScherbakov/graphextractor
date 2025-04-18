import cv2
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import easyocr
import os

class OCRProcessor:
    """Class for OCR processing of graph images to extract text labels."""
    
    def __init__(self, languages: List[str] = None, gpu: bool = False):
        """
        Initialize the OCR processor.
        
        Args:
            languages: List of languages to recognize (default: ['en'])
            gpu: Whether to use GPU acceleration
        """
        self.languages = languages or ['en']
        self.gpu = gpu
        
        # Initialize OCR reader (lazy loading to avoid immediate resource usage)
        self._reader = None
        
    @property
    def reader(self):
        """Lazy initialization of OCR reader."""
        if self._reader is None:
            self._reader = easyocr.Reader(
                self.languages,
                gpu=self.gpu,
                model_storage_directory=os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), 
                    '..', 'models'
                )
            )
        return self._reader
    
    def extract_text(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Extract text regions and content from the image.
        
        Args:
            image: Input image
            
        Returns:
            List of dictionaries containing text and bounding box information
        """
        # Make a copy of the image for visualization
        visualization = image.copy() if len(image.shape) > 2 else cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        # Run OCR detection
        results = self.reader.readtext(image)
        
        text_regions = []
        for i, (bbox, text, prob) in enumerate(results):
            # Convert points to more usable format
            pts = np.array(bbox, np.int32).reshape((-1, 1, 2))
            
            # Calculate centroid
            centroid = np.mean(bbox, axis=0, dtype=np.int32)
            
            # Create structured output
            text_region = {
                "id": i,
                "text": text,
                "confidence": float(prob),
                "bounding_box": bbox,
                "centroid": (int(centroid[0]), int(centroid[1])),
                "area": cv2.contourArea(pts)
            }
            text_regions.append(text_region)
            
            # Draw bounding box on visualization
            cv2.polylines(visualization, [pts], True, (0, 255, 0), 2)
            cv2.putText(
                visualization, 
                text, 
                (int(centroid[0]), int(centroid[1])), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
                (0, 0, 255), 
                1
            )
        
        return text_regions
    
    def filter_text_by_size(self, text_regions: List[Dict[str, Any]], 
                           min_confidence: float = 0.3) -> List[Dict[str, Any]]:
        """
        Filter text regions by size and confidence.
        
        Args:
            text_regions: List of text regions
            min_confidence: Minimum confidence threshold
            
        Returns:
            Filtered list of text regions
        """
        return [
            region for region in text_regions 
            if region["confidence"] >= min_confidence
        ]
