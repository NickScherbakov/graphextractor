# GraphExtractor

GraphExtractor is a service for detecting and extracting graph structures from images and documents. It can identify nodes and edges in diagrams, charts, and other graphical representations, and convert them into structured graph objects.

## Features

- Detect graph structures in images
- Extract nodes and edges
- Convert to NetworkX graph objects
- Save in various formats (GEXF, GraphML, GML)
- Generate visualizations
- API for integration into other systems

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/graphextractor.git
cd graphextractor

# Install the package
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Process a single image
python -m graphextractor.cli path/to/image.png --output results --format gexf --visualize

# Process a directory of images
python -m graphextractor.cli path/to/image_dir --output results
```

### Python API

```python
from graphextractor.detector import GraphDetector
from graphextractor.graph_builder import NetworkXBuilder

# Detect graph in image
detector = GraphDetector()
result = detector.detect("path/to/image.png")

# Build NetworkX graph
builder = NetworkXBuilder()
graph = builder.build_graph(result)

# Save and visualize
builder.save_graph(graph, "output.gexf", format="gexf")
builder.visualize_graph(graph, "visualization.png")
```

### REST API

Start the server:

```bash
python -m graphextractor.api.app
```

The API will be available at `http://localhost:8000`.

#### API Endpoints

- **POST /extract_graph/**: Extract graph from uploaded image
- **GET /download/{file_path}**: Download generated files

## Requirements

- Python 3.8+
- OpenCV
- NetworkX
- scikit-image
- matplotlib
- FastAPI (for API)
- PyTorch (optional, for advanced detection)

## License

MIT

## Acknowledgements

This project was inspired by research in document analysis, graph recognition, and computer vision techniques. It builds upon several open-source projects in these fields.