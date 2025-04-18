import cv2
import numpy as np
from typing import Dict, Any

class NoiseReducer:
    """Class for reducing noise in graph images."""
    
    def __init__(self, config: Dict = None):
        """
        Initialize the noise reducer.
        
        Args:
            config: Configuration parameters
        """
        self.config = config or {}
        self.denoise_strength = self.config.get("denoise_strength", 10)
        self.median_kernel = self.config.get("median_kernel", 3)
        self.gaussian_kernel = self.config.get("gaussian_kernel", (5, 5))
        self.gaussian_sigma = self.config.get("gaussian_sigma", 0)
        
    def reduce_noise(self, image: np.ndarray) -> np.ndarray:
        """
        Apply noise reduction to the image.
        
        Args:
            image: Input image
            
        Returns:
            Denoised image
        """
        # Make sure image is not None
        if image is None:
            raise ValueError("Input image is None")
            
        # Convert to grayscale if needed
        if len(image.shape) > 2 and image.shape[2] > 1:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            is_color = True
        else:
            gray = image.copy()
            is_color = False
            
        # Apply median filter to remove salt-and-pepper noise
        median = cv2.medianBlur(gray, self.median_kernel)
        
        # Apply Gaussian blur to reduce high-frequency noise
        gaussian = cv2.GaussianBlur(
            median, 
            self.gaussian_kernel,
            self.gaussian_sigma
        )
        
        # If original was color, we need to denoise color image
        if is_color:
            # Apply Non-local Means Denoising on the color image
            denoised = cv2.fastNlMeansDenoisingColored(
                image,
                None,
                h=self.denoise_strength,
                hColor=self.denoise_strength,
                templateWindowSize=7,
                searchWindowSize=21
            )
            return denoised
        else:
            # Apply Non-local Means Denoising on grayscale
            denoised = cv2.fastNlMeansDenoising(
                gaussian,
                None,
                h=self.denoise_strength,
                templateWindowSize=7,
                searchWindowSize=21
            )
            return denoised
    
    def apply_adaptive_denoising(self, image: np.ndarray, 
                               noise_level: float = None) -> np.ndarray:
        """
        Apply denoising with parameters adapted to estimated noise level.
        
        Args:
            image: Input image
            noise_level: Estimated noise level (if None, it will be estimated)
            
        Returns:
            Denoised image
        """
        # Estimate noise level if not provided
        if noise_level is None:
            # Simple noise estimation using difference from median filter
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) > 2 else image
            median = cv2.medianBlur(gray, 3)
            noise = cv2.absdiff(gray, median)
            noise_level = np.mean(noise)
            
        # Adjust denoising parameters based on estimated noise level
        if noise_level < 5:
            # Low noise - light denoising
            denoised = self.reduce_noise_light(image)
        elif noise_level < 15:
            # Medium noise - standard denoising
            denoised = self.reduce_noise(image)
        else:
            # High noise - aggressive denoising
            denoised = self.reduce_noise_aggressive(image)
            
        return denoised
    
    def reduce_noise_light(self, image: np.ndarray) -> np.ndarray:
        """Light denoising for images with low noise."""
        # Use smaller kernel size and strength for subtle denoising
        temp_median_kernel = self.median_kernel
        temp_denoise_strength = self.denoise_strength
        
        self.median_kernel = 3
        self.denoise_strength = 5
        
        result = self.reduce_noise(image)
        
        # Restore original parameters
        self.median_kernel = temp_median_kernel
        self.denoise_strength = temp_denoise_strength
        
        return result
    
    def reduce_noise_aggressive(self, image: np.ndarray) -> np.ndarray:
        """Aggressive denoising for images with heavy noise."""
        # Use larger kernel size and strength for heavy denoising
        temp_median_kernel = self.median_kernel
        temp_denoise_strength = self.denoise_strength
        temp_gaussian_kernel = self.gaussian_kernel
        
        self.median_kernel = 5
        self.denoise_strength = 15
        self.gaussian_kernel = (7, 7)
        
        result = self.reduce_noise(image)
        
        # Restore original parameters
        self.median_kernel = temp_median_kernel
        self.denoise_strength = temp_denoise_strength
        self.gaussian_kernel = temp_gaussian_kernel
        
        return result
