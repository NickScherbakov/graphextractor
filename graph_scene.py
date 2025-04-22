from manim import *

class GraphFromImage(Scene):
    def construct(self):
        vertices = ["А", "Б", "В", "Г", "Д", "Е", "К"]
        edges = [
            ("А", "Б"), ("А", "В"),
            ("Б", "В"),
            ("В", "Г"), ("В", "Д"), ("В", "Е"),
            ("Г", "Е"), ("Г", "К"),
            ("Д", "Е"),
            ("Е", "К")
        ]

        # Approximate layout based on the image
        layout = {
            "А": [-4, 0, 0],
            "Б": [-2.5, 1.5, 0],
            "В": [-1, 0, 0],
            "Г": [1.5, -1.5, 0],
            "Д": [1, 1.5, 0],
            "Е": [2.5, 0, 0],
            "К": [5, 0, 0]
        }

        # Configure vertex appearance (optional, adjust as needed)
        vertex_config = {
            "А": {"radius": 0.15, "color": WHITE},
            "Б": {"radius": 0.15, "color": WHITE},
            "В": {"radius": 0.15, "color": WHITE},
            "Г": {"radius": 0.15, "color": WHITE},
            "Д": {"radius": 0.15, "color": WHITE},
            "Е": {"radius": 0.15, "color": WHITE},
            "К": {"radius": 0.15, "color": WHITE},
        }

        # Configure label appearance and position
        label_config = {
            "А": {"font_size": 36, "buff": 0.3, "direction": LEFT},
            "Б": {"font_size": 36, "buff": 0.3, "direction": UP},
            "В": {"font_size": 36, "buff": 0.3, "direction": DOWN},
            "Г": {"font_size": 36, "buff": 0.3, "direction": DOWN},
            "Д": {"font_size": 36, "buff": 0.3, "direction": UP},
            "Е": {"font_size": 36, "buff": 0.3, "direction": UP},
            "К": {"font_size": 36, "buff": 0.3, "direction": RIGHT},
        }


        graph = Graph(
            vertices,
            edges,
            layout=layout,
            labels=label_config, # Use label_config for labels
            vertex_config=vertex_config,
            edge_config={"color": WHITE, "stroke_width": 2}
        )

        self.play(Create(graph))
        self.wait(1)

# To render this scene, save it as a Python file (e.g., graph_scene.py)
# and run the following command in your terminal:
# manim -pql graph_scene.py GraphFromImage