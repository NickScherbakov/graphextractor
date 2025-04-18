from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
import networkx as nx
from tempfile import NamedTemporaryFile
import uvicorn
from typing import Optional, List, Dict, Any

from graphextractor.detector import GraphDetector
from graphextractor.graph_builder import NetworkXBuilder
from graphextractor.caching import CacheManager, ImageHashProvider

app = FastAPI(title="Graph Extractor API", 
             description="API for extracting graph structures from images")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
os.makedirs("temp_uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)
os.makedirs("cache", exist_ok=True)

# Initialize cache manager for API
cache_manager = CacheManager(cache_dir="cache")
hash_provider = ImageHashProvider()

@app.post("/extract_graph/")
async def extract_graph(
    file: UploadFile = File(...),
    output_format: str = Form("gexf"),
    visualize: bool = Form(False),
    enable_ocr: bool = Form(True),
    enable_cache: bool = Form(True),
    enhance_image: bool = Form(True),
    ocr_languages: str = Form("en")
):
    """
    Extract graph structure from an uploaded image.
    
    Args:
        file: The image file to process
        output_format: Format to save the graph (gexf, graphml, gml)
        visualize: Whether to generate visualization
        enable_ocr: Enable OCR for text recognition
        enable_cache: Enable caching of results
        enhance_image: Apply image enhancement
        ocr_languages: Languages for OCR (comma-separated)
        
    Returns:
        Dictionary with graph data and file paths
    """
    # Validate output format
    if output_format not in ["gexf", "graphml", "gml"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported output format: {output_format}"
        )
    
    # Process OCR languages
    languages_list = [lang.strip() for lang in ocr_languages.split(",")]
    
    # Generate a unique ID for this job
    job_id = str(uuid.uuid4())
    
    # Create a temporary file
    input_file_path = os.path.join("temp_uploads", f"{job_id}_{file.filename}")
    
    try:
        # Save uploaded file
        with open(input_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Configure the detector
        detector_config = {
            "ocr_enabled": enable_ocr,
            "ocr_languages": languages_list,
            "caching_enabled": enable_cache,
            "enhancer": {
                "enabled": enhance_image
            }
        }
        
        # Process the image
        detector = GraphDetector(config=detector_config)
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
        
        # Extract text labels from nodes if available
        node_labels = {}
        if enable_ocr:
            for node in detection_result.get("nodes", []):
                if "label" in node and node["label"]:
                    node_labels[node["id"]] = {
                        "text": node["label"],
                        "confidence": node.get("label_confidence", 0)
                    }
        
        # Prepare response
        response = {
            "job_id": job_id,
            "nodes_count": len(graph.nodes),
            "edges_count": len(graph.edges),
            "graph_file": graph_output_path,
            "quality_info": detection_result.get("quality_info", {})
        }
        
        if enable_ocr:
            response["text_found"] = len(detection_result.get("text_regions", [])) > 0
            response["node_labels"] = node_labels
            
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

@app.post("/clear_cache/")
async def clear_cache():
    """Clear the cache."""
    try:
        cache_manager.clear()
        return {"status": "success", "message": "Cache cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/image_quality/")
async def analyze_image_quality(file: UploadFile = File(...)):
    """
    Analyze the quality of an uploaded image.
    
    Args:
        file: The image file to analyze
        
    Returns:
        Quality analysis results
    """
    # Generate a unique ID for this job
    job_id = str(uuid.uuid4())
    
    # Create a temporary file
    input_file_path = os.path.join("temp_uploads", f"{job_id}_{file.filename}")
    
    try:
        # Save uploaded file
        with open(input_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Load the image
        import cv2
        image = cv2.imread(input_file_path)
        if image is None:
            raise ValueError("Could not read image")
        
        # Analyze image quality
        from graphextractor.preprocessing import QualityAnalyzer
        analyzer = QualityAnalyzer()
        quality_info = analyzer.analyze(image)
        
        return {
            "filename": file.filename,
            "quality_info": quality_info
        }
        
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(input_file_path):
            os.remove(input_file_path)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Always clean up
        if os.path.exists(input_file_path):
            os.remove(input_file_path)

@app.on_event("shutdown")
def cleanup():
    """Clean up temporary files when shutting down."""
    shutil.rmtree("temp_uploads", ignore_errors=True)

def start_server():
    """Start the API server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_server()
