import cv2
import numpy as np
from typing import Dict, Any, Tuple
from enum import Enum

class ImageQualityLevel(Enum):
    """Enumeration for image quality levels."""
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    VERY_LOW = 0

class QualityAnalyzer:
    """Class to analyze the quality of input images."""
    
    def __init__(self):
        """Initialize the quality analyzer."""
        pass
    
    def analyze(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze image quality and return metrics.
        
        Args:
            image: Input image
            
        Returns:
            Dictionary with quality metrics
        """
        if image is None:
            raise ValueError("Image is None")
            
        # Convert to grayscale if needed
        if len(image.shape) > 2 and image.shape[2] > 1:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Calculate basic statistics
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Calculate blur level using Laplacian variance
        laplacian_var = self._calculate_blur_level(gray)
        
        # Calculate noise level using homogeneity
        noise_level = self._estimate_noise(gray)
        
        # Edge density to estimate complexity
        edge_density = self._calculate_edge_density(gray)
        
        # Determine overall quality level
        quality_level = self._determine_quality_level(
            brightness, contrast, laplacian_var, noise_level
        )
        
        return {
            "brightness": float(brightness),
            "contrast": float(contrast),
            "blur_level": float(laplacian_var),
            "noise_level": float(noise_level),
            "edge_density": float(edge_density),
            "quality_level": quality_level.name,
            "quality_score": quality_level.value
        }
    
    def _calculate_blur_level(self, image: np.ndarray) -> float:
        """
        Calculate blur level using Laplacian variance.
        Lower values indicate more blur.
        """
        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        return np.var(laplacian)
    
    def _estimate_noise(self, image: np.ndarray) -> float:
        """
        Estimate noise level in image.
        Higher values indicate more noise.
        """
        # Apply median filter
        median_filtered = cv2.medianBlur(image, 3)
        
        # Calculate difference with original
        noise = cv2.absdiff(image, median_filtered)
        
        # Return average noise level
        return np.mean(noise)
    
    def _calculate_edge_density(self, image: np.ndarray) -> float:
        """
        Calculate edge density to estimate image complexity.
        """
        edges = cv2.Canny(image, 100, 200)
        return np.sum(edges > 0) / (image.shape[0] * image.shape[1])
    
    def _determine_quality_level(self, brightness: float, contrast: float, 
                                blur_level: float, noise_level: float) -> ImageQualityLevel:
        """
        Determine overall image quality level.
        """
        # Compute score based on metrics
        score = 0
        
        # Brightness score (0-1)
        if 80 <= brightness <= 220:
            score += 1
            
        # Contrast score (0-1)
        if contrast > 40:
            score += 1
            
        # Blur score (0-1)
        if blur_level > 100:
            score += 1
            
        # Noise score (0-1)
        if noise_level < 10:
            score += 1
            
        # Map score to quality level
        if score >= 3:
            return ImageQualityLevel.HIGH
        elif score == 2:
            return ImageQualityLevel.MEDIUM
        elif score == 1:
            return ImageQualityLevel.LOW
        else:
            return ImageQualityLevel.VERY_LOW
