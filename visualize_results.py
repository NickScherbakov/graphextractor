"""
Скрипт для визуализации сравнения результатов тестирования GraphExtractor.
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np
import sys

def visualize_test_results(results_file="test_results/test_summary.json"):
    """Визуализирует результаты тестирования."""
    
    # Проверяем наличие файла с результатами
    if not os.path.exists(results_file):
        print(f"Ошибка: Файл с результатами не найден: {results_file}")
        return False
    
    # Загружаем результаты
    with open(results_file, "r") as f:
        test_results = json.load(f)
    
    results = test_results["results"]
    
    # Отфильтровываем результаты без ошибок
    valid_results = [r for r in results if "error" not in r]
    
    if not valid_results:
        print("Нет валидных результатов для визуализации.")
        return False
    
    # Получаем данные для графиков
    image_names = [r["image_name"] for r in valid_results]
    base_nodes = [r["base_nodes"] for r in valid_results]
    enhanced_nodes = [r["enhanced_nodes"] for r in valid_results]
    base_edges = [r["base_edges"] for r in valid_results]
    enhanced_edges = [r["enhanced_edges"] for r in valid_results]
    base_times = [r["base_time"] for r in valid_results]
    enhanced_times = [r["enhanced_time"] for r in valid_results]
    cache_speedups = [r["cache_speedup"] for r in valid_results]
    
    # Создаем директорию для графиков
    charts_dir = os.path.join(os.path.dirname(results_file), "charts")
    os.makedirs(charts_dir, exist_ok=True)
    
    # 1. График сравнения количества узлов
    plt.figure(figsize=(10, 6))
    x = np.arange(len(image_names))
    width = 0.35
    
    plt.bar(x - width/2, base_nodes, width, label='Базовое распознавание')
    plt.bar(x + width/2, enhanced_nodes, width, label='Улучшенное распознавание')
    
    plt.xlabel('Изображение')
    plt.ylabel('Количество узлов')
    plt.title('Сравнение количества распознанных узлов')
    plt.xticks(x, [os.path.basename(name) for name in image_names], rotation=45)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig(os.path.join(charts_dir, "nodes_comparison.png"))
    
    # 2. График сравнения количества ребер
    plt.figure(figsize=(10, 6))
    
    plt.bar(x - width/2, base_edges, width, label='Базовое распознавание')
    plt.bar(x + width/2, enhanced_edges, width, label='Улучшенное распознавание')
    
    plt.xlabel('Изображение')
    plt.ylabel('Количество ребер')
    plt.title('Сравнение количества распознанных ребер')
    plt.xticks(x, [os.path.basename(name) for name in image_names], rotation=45)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig(os.path.join(charts_dir, "edges_comparison.png"))
    
    # 3. График сравнения времени обработки
    plt.figure(figsize=(10, 6))
    
    plt.bar(x - width/2, base_times, width, label='Базовое распознавание')
    plt.bar(x + width/2, enhanced_times, width, label='Улучшенное распознавание')
    
    plt.xlabel('Изображение')
    plt.ylabel('Время обработки (сек)')
    plt.title('Сравнение времени обработки')
    plt.xticks(x, [os.path.basename(name) for name in image_names], rotation=45)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig(os.path.join(charts_dir, "time_comparison.png"))
    
    # 4. График ускорения с кэшированием
    plt.figure(figsize=(10, 6))
    
    plt.bar(x, cache_speedups, width)
    
    plt.xlabel('Изображение')
    plt.ylabel('Ускорение (раз)')
    plt.title('Ускорение за счет кэширования')
    plt.xticks(x, [os.path.basename(name) for name in image_names], rotation=45)
    plt.axhline(y=1.0, color='r', linestyle='--', label='Без ускорения')
    plt.legend()
    plt.tight_layout()
    
    plt.savefig(os.path.join(charts_dir, "cache_speedup.png"))
    
    print(f"Графики результатов сохранены в директорию: {charts_dir}")
    return True

if __name__ == "__main__":
    # Используем файл по умолчанию или путь, указанный в аргументах
    if len(sys.argv) > 1:
        visualize_test_results(sys.argv[1])
    else:
        visualize_test_results()
