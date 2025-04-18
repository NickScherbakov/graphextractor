import cv2
import numpy as np
from typing import Dict, Any, Tuple

class ImageEnhancer:
    """Class for enhancing image quality to improve graph detection."""
    
    def __init__(self, config: Dict = None):
        """
        Initialize the image enhancer.
        
        Args:
            config: Configuration parameters for enhancement
        """
        self.config = config or {}
        self.default_kernel_size = self.config.get("kernel_size", 5)
        self.clahe_clip_limit = self.config.get("clahe_clip_limit", 2.0)
        self.clahe_grid_size = self.config.get("clahe_grid_size", (8, 8))
        
    def enhance(self, image: np.ndarray) -> np.ndarray:
        """
        Apply enhancements to improve image quality.
        
        Args:
            image: Input image
            
        Returns:
            Enhanced image
        """
        # Check image
        if image is None:
            raise ValueError("Image is None")
            
        # Convert to grayscale if needed
        if len(image.shape) > 2 and image.shape[2] > 1:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(
            clipLimit=self.clahe_clip_limit, 
            tileGridSize=self.clahe_grid_size
        )
        equalized = clahe.apply(gray)
        
        # Apply bilateral filtering to preserve edges
        filtered = cv2.bilateralFilter(
            equalized, 
            d=9, 
            sigmaColor=75, 
            sigmaSpace=75
        )
        
        return filtered
    
    def apply_adaptive_enhancement(self, image: np.ndarray) -> np.ndarray:
        """
        Apply adaptive enhancement based on image characteristics.
        
        Args:
            image: Input image
            
        Returns:
            Enhanced image with methods chosen based on content
        """
        # Analyze image to determine required enhancements
        brightness = np.mean(image)
        contrast = np.std(image)
        
        enhanced = image.copy()
        
        # Low contrast image - apply contrast enhancement
        if contrast < 30:
            enhanced = self.enhance(enhanced)
            
        # Low brightness - apply brightness adjustment
        if brightness < 100:
            enhanced = cv2.convertScaleAbs(
                enhanced, 
                alpha=self.config.get("brightness_alpha", 1.3), 
                beta=self.config.get("brightness_beta", 10)
            )
        
        # High noise scenario - apply denoising
        if contrast < 10 and brightness < 80:
            # Use fastNlMeans for better quality despite performance impact
            enhanced = cv2.fastNlMeansDenoising(
                enhanced, 
                h=self.config.get("denoise_h", 10)
            )
            
        return enhanced
    
    def sharpen_edges(self, image: np.ndarray) -> np.ndarray:
        """
        Apply edge sharpening to make graph elements more defined.
        
        Args:
            image: Input image
            
        Returns:
            Edge-sharpened image
        """
        # Create sharpening kernel
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        
        # Apply kernel
        sharpened = cv2.filter2D(image, -1, kernel)
        
        return sharpened
