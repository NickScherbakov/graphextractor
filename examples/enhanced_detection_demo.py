"""
Demonstration of enhanced graph detection capabilities.
This script showcases the improvements made to overcome limitations.
"""

import os
import argparse
import time
import cv2
import matplotlib.pyplot as plt
import networkx as nx
import sys

# Add parent directory to path to import graphextractor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphextractor.detector import GraphDetector
from graphextractor.graph_builder import NetworkXBuilder
from graphextractor.preprocessing import ImageEnhancer, QualityAnalyzer
from graphextractor.text_recognition import OCRProcessor, TextMapper
from graphextractor.caching import CacheManager, ImageHashProvider

def show_image(image, title):
    """Show an image with matplotlib."""
    plt.figure(figsize=(12, 8))
    plt.title(title)
    if len(image.shape) == 3:
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    else:
        plt.imshow(image, cmap='gray')
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Demo of enhanced graph detection capabilities")
    parser.add_argument("image_path", help="Path to the image file")
    parser.add_argument("--output_dir", default="output", help="Output directory")
    parser.add_argument("--no_cache", action="store_true", help="Disable caching")
    parser.add_argument("--no_ocr", action="store_true", help="Disable OCR")
    parser.add_argument("--no_enhance", action="store_true", help="Disable image enhancement")
    parser.add_argument("--show_steps", action="store_true", help="Show intermediate steps")
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Processing image: {args.image_path}")
    
    # 1. First, analyze image quality
    print("\n--- Analyzing image quality ---")
    quality_analyzer = QualityAnalyzer()
    
    image = cv2.imread(args.image_path)
    if image is None:
        print(f"Error: Could not load image from {args.image_path}")
        return 1
        
    quality_info = quality_analyzer.analyze(image)
    print(f"Image quality level: {quality_info['quality_level']}")
    print(f"Quality metrics: Brightness={quality_info['brightness']:.1f}, "
          f"Contrast={quality_info['contrast']:.1f}, "
          f"Blur level={quality_info['blur_level']:.1f}, "
          f"Noise level={quality_info['noise_level']:.1f}")
    
    # 2. Demonstrate image enhancement if requested
    if not args.no_enhance:
        print("\n--- Enhancing image ---")
        enhancer = ImageEnhancer()
        enhanced = enhancer.apply_adaptive_enhancement(image)
        
        if args.show_steps:
            show_image(image, "Original Image")
            show_image(enhanced, "Enhanced Image")
            
        # Save enhanced image
        enhanced_path = os.path.join(args.output_dir, "enhanced_image.png")
        cv2.imwrite(enhanced_path, enhanced)
        print(f"Enhanced image saved to: {enhanced_path}")
    
    # 3. Demonstrate text recognition if requested
    if not args.no_ocr:
        print("\n--- Recognizing text ---")
        ocr = OCRProcessor(languages=['en'])
        text_regions = ocr.extract_text(image)
        
        print(f"Found {len(text_regions)} text regions")
        for i, region in enumerate(text_regions):
            print(f"  Text {i+1}: '{region['text']}' (confidence: {region['confidence']:.2f})")
        
        # Create visualization with text boxes
        if args.show_steps and text_regions:
            vis_img = image.copy()
            for region in text_regions:
                bbox = np.array(region["bounding_box"], dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(vis_img, [bbox], True, (0, 255, 0), 2)
                cv2.putText(vis_img, region["text"], region["centroid"], 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            show_image(vis_img, "Detected Text")
            
            # Save text visualization
            text_vis_path = os.path.join(args.output_dir, "text_visualization.png")
            cv2.imwrite(text_vis_path, vis_img)
            print(f"Text visualization saved to: {text_vis_path}")
    
    # 4. Now perform full graph detection with all enhancements
    print("\n--- Performing graph detection ---")
    
    config = {
        "ocr_enabled": not args.no_ocr,
        "caching_enabled": not args.no_cache,
        "enhancer": {"enabled": not args.no_enhance}
    }
    
    # Measure performance
    start_time = time.time()
    
    # First run might include model loading time
    detector = GraphDetector(config=config)
    detection_result = detector.detect(args.image_path)
    
    # Second run to test caching if enabled
    if not args.no_cache:
        print("Running second detection to test caching...")
        cache_start_time = time.time()
        cached_result = detector.detect(args.image_path)
        cache_time = time.time() - cache_start_time
        print(f"Cached detection time: {cache_time:.3f} seconds")
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"Detection completed in {processing_time:.3f} seconds")
    print(f"Detected {len(detection_result['nodes'])} nodes and {len(detection_result['edges'])} edges")
    
    # 5. Convert to NetworkX graph
    builder = NetworkXBuilder()
    graph = builder.build_graph(detection_result)
    
    # Save the graph in GEXF format
    graph_path = os.path.join(args.output_dir, "detected_graph.gexf")
    builder.save_graph(graph, graph_path, format="gexf")
    print(f"Graph saved to: {graph_path}")
    
    # Generate visualization
    vis_path = os.path.join(args.output_dir, "graph_visualization.png")
    builder.visualize_graph(graph, vis_path, with_labels=True)
    print(f"Graph visualization saved to: {vis_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
