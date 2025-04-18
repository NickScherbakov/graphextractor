from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
import uuid
import networkx as nx
from tempfile import NamedTemporaryFile
import uvicorn
from typing import Optional

from graphextractor.detector import GraphDetector
from graphextractor.graph_builder import NetworkXBuilder

app = FastAPI(title="Graph Extractor API", 
             description="API for extracting graph structures from images")

# Create directories if they don't exist
os.makedirs("temp_uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)

@app.post("/extract_graph/")
async def extract_graph(
    file: UploadFile = File(...),
    output_format: str = "gexf",
    visualize: bool = False
):
    """
    Extract graph structure from an uploaded image.
    
    Args:
        file: The image file to process
        output_format: Format to save the graph (gexf, graphml, gml)
        visualize: Whether to generate visualization
        
    Returns:
        Dictionary with graph data and file paths
    """
    # Validate output format
    if output_format not in ["gexf", "graphml", "gml"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported output format: {output_format}"
        )
    
    # Generate a unique ID for this job
    job_id = str(uuid.uuid4())
    
    # Create a temporary file
    input_file_path = os.path.join("temp_uploads", f"{job_id}_{file.filename}")
    
    try:
        # Save uploaded file
        with open(input_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the image
        detector = GraphDetector()
        detection_result = detector.detect(input_file_path)
        
        # Build networkx graph
        builder = NetworkXBuilder()
        graph = builder.build_graph(detection_result)
        
        # Generate output paths
        graph_output_path = os.path.join("output", f"{job_id}_graph.{output_format}")
        vis_output_path = None
        
        # Save the graph
        builder.save_graph(graph, graph_output_path, format=output_format)
        
        # Generate visualization if requested
        if visualize:
            vis_output_path = os.path.join("output", f"{job_id}_visualization.png")
            builder.visualize_graph(graph, vis_output_path)
        
        # Prepare response
        response = {
            "job_id": job_id,
            "nodes_count": len(graph.nodes),
            "edges_count": len(graph.edges),
            "graph_file": graph_output_path,
        }
        
        if visualize and vis_output_path:
            response["visualization_file"] = vis_output_path
            
        return response
        
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(input_file_path):
            os.remove(input_file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """
    Download a generated file.
    
    Args:
        file_path: Path to the file to download
        
    Returns:
        File response
    """
    # Ensure the file is from our output directory
    if not file_path.startswith("output/"):
        file_path = os.path.join("output", file_path)
        
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_path)

@app.on_event("shutdown")
def cleanup():
    """Clean up temporary files when shutting down."""
    shutil.rmtree("temp_uploads", ignore_errors=True)

def start_server():
    """Start the API server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_server()
