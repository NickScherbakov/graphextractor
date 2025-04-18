import numpy as np
import cv2
import imagehash
from typing import Union, Tuple
from PIL import Image
import io

class ImageHashProvider:
    """Generate perceptual hashes for images to use as cache keys."""
    
    def __init__(self, hash_size: int = 8, 
                scale_width: int = 256, 
                scale_height: int = 256):
        """
        Initialize the image hasher.
        
        Args:
            hash_size: Size of hash in bits
            scale_width: Width to scale images to before hashing
            scale_height: Height to scale images to before hashing
        """
        self.hash_size = hash_size
        self.scale_width = scale_width
        self.scale_height = scale_height
    
    def compute_hash(self, image: Union[str, np.ndarray]) -> str:
        """
        Compute a perceptual hash for the image.
        
        Args:
            image: Image path or numpy array
            
        Returns:
            Hash string
        """
        # Load image if path is provided
        if isinstance(image, str):
            pil_image = Image.open(image)
        else:
            # Convert OpenCV image to PIL
            if len(image.shape) > 2 and image.shape[2] == 3:
                # Convert BGR to RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                # Grayscale
                image_rgb = image
                
            pil_image = Image.fromarray(image_rgb)
            
        # Resize image for consistency
        pil_image = pil_image.resize(
            (self.scale_width, self.scale_height), 
            Image.LANCZOS
        )
            
        # Compute different types of hashes and combine them
        phash = imagehash.phash(pil_image, hash_size=self.hash_size)
        dhash = imagehash.dhash(pil_image, hash_size=self.hash_size)
        
        # Combine hashes to make it more robust
        combined_hash = str(phash) + "_" + str(dhash)
        
        return combined_hash
    
    def are_similar(self, hash1: str, hash2: str, threshold: int = 10) -> bool:
        """
        Check if two image hashes are similar.
        
        Args:
            hash1: First hash string
            hash2: Second hash string
            threshold: Maximum difference to be considered similar
            
        Returns:
            True if images are similar, False otherwise
        """
        # Split combined hashes
        phash1, dhash1 = hash1.split("_")
        phash2, dhash2 = hash2.split("_")
        
        # Convert string hashes to imagehash objects
        phash1 = imagehash.hex_to_hash(phash1)
        dhash1 = imagehash.hex_to_hash(dhash1)
        phash2 = imagehash.hex_to_hash(phash2)
        dhash2 = imagehash.hex_to_hash(dhash2)
        
        # Calculate differences
        phash_diff = phash1 - phash2
        dhash_diff = dhash1 - dhash2
        
        # Average difference
        avg_diff = (phash_diff + dhash_diff) / 2
        
        return avg_diff <= threshold
