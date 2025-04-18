import argparse
import os
from .detector import GraphDetector
from .graph_builder import NetworkXBuilder

def main():
    """Command line interface for graph extractor."""
    parser = argparse.ArgumentParser(
        description="Extract graph structures from images")
    
    parser.add_argument("input", help="Input image file or directory")
    parser.add_argument(
        "--output", "-o", 
        help="Output directory (default: current directory)",
        default="."
    )
    parser.add_argument(
        "--format", "-f", 
        help="Output graph format (gexf, graphml, gml)",
        default="gexf",
        choices=["gexf", "graphml", "gml"]
    )
    parser.add_argument(
        "--visualize", "-v", 
        help="Generate visualization", 
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Process single file or directory
    if os.path.isfile(args.input):
        process_file(args.input, args.output, args.format, args.visualize)
    elif os.path.isdir(args.input):
        for filename in os.listdir(args.input):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                file_path = os.path.join(args.input, filename)
                process_file(file_path, args.output, args.format, args.visualize)
    else:
        print(f"Error: {args.input} is not a valid file or directory")
        return 1
    
    return 0

def process_file(file_path, output_dir, output_format, visualize):
    """Process a single image file."""
    try:
        print(f"Processing {file_path}...")
        
        # Extract base filename without extension
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Detect graph elements
        detector = GraphDetector()
        detection_result = detector.detect(file_path)
        
        # Build graph
        builder = NetworkXBuilder()
        graph = builder.build_graph(detection_result)
        
        # Save graph
        graph_output_path = os.path.join(output_dir, f"{base_name}.{output_format}")
        builder.save_graph(graph, graph_output_path, format=output_format)
        
        print(f"Saved graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges to {graph_output_path}")
        
        # Generate visualization if requested
        if visualize:
            vis_output_path = os.path.join(output_dir, f"{base_name}_graph.png")
            builder.visualize_graph(graph, vis_output_path)
            print(f"Visualization saved to {vis_output_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    exit(main())
