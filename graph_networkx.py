#!/usr/bin/env python3
# filepath: /workspaces/graphextractor/graph_networkx.py
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend that doesn't require a display
import matplotlib.pyplot as plt
import networkx as nx

def create_graph():
    # Создаем вершины графа - те же, что и в оригинальном скрипте
    vertices = ["А", "Б", "В", "Г", "Д", "Е", "К"]
    
    # Создаем рёбра - те же, что и в оригинальном скрипте
    edges = [
        ("А", "Б"), ("А", "В"),
        ("Б", "В"),
        ("В", "Г"), ("В", "Д"), ("В", "Е"),
        ("Г", "Е"), ("Г", "К"),
        ("Д", "Е"),
        ("Е", "К")
    ]
    
    # Создаем граф
    G = nx.Graph()
    
    # Добавляем вершины и рёбра
    G.add_nodes_from(vertices)
    G.add_edges_from(edges)
    
    # Определяем расположение вершин - аналогично оригинальному скрипту
    pos = {
        "А": (-4, 0),
        "Б": (-2.5, 1.5),
        "В": (-1, 0),
        "Г": (1.5, -1.5),
        "Д": (1, 1.5),
        "Е": (2.5, 0),
        "К": (5, 0)
    }
    
    # Настраиваем визуализацию
    plt.figure(figsize=(10, 6))
    
    # Рисуем рёбра
    nx.draw_networkx_edges(G, pos, width=2, edge_color='black')
    
    # Рисуем вершины
    nx.draw_networkx_nodes(G, pos, node_color='white', edgecolors='black', 
                          node_size=700, linewidths=2)
    
    # Добавляем метки к вершинам с немного увеличенным размером шрифта
    nx.draw_networkx_labels(G, pos, font_size=16, font_family='sans-serif')
    
    # Убираем оси
    plt.axis('off')
    
    # Сохраняем изображение
    plt.savefig('graph_output.png', dpi=300, bbox_inches='tight')
    
    # Показываем граф
    plt.show()

if __name__ == "__main__":
    create_graph()
