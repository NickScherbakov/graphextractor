#!/usr/bin/env python
"""
Функциональное тестирование GraphExtractor для проверки основной функциональности извлечения графов из изображений.
"""

import os
import sys
import time
import json
from pathlib import Path

# Добавляем корневую директорию в sys.path для импорта модулей
sys.path.insert(0, os.path.abspath('.'))

def run_functional_tests():
    """Запускает функциональные тесты основного функционала GraphExtractor."""
    print("="*60)
    print("ФУНКЦИОНАЛЬНОЕ ТЕСТИРОВАНИЕ ОСНОВНОГО ФУНКЦИОНАЛА")
    print("="*60)
    
    # Проверяем импорт основных функциональных модулей
    try:
        from graphextractor.detector.graph_detector import GraphDetector
        from graphextractor.graph_builder.networkx_builder import NetworkXBuilder
        print("✓ Успешно импортированы основные модули")
    except ImportError as e:
        print(f"✗ Ошибка импорта основных модулей: {e}")
        return False
    
    # Создаем директории для результатов тестирования
    output_dir = Path("test_results/functional_test")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Получаем список тестовых изображений
    test_images = list(Path("test_images").glob("*.png"))
    if not test_images:
        print("✗ Тестовые изображения не найдены")
        return False
    
    print(f"\nНайдено {len(test_images)} тестовых изображений")
    
    # Создаем экземпляры детектора и построителя графов
    try:
        detector = GraphDetector()
        builder = NetworkXBuilder()
        print("✓ Успешно созданы экземпляры детектора и построителя графов")
    except Exception as e:
        print(f"✗ Ошибка при создании экземпляров: {e}")
        return False
    
    # Результаты тестов
    test_results = []
    
    # Тестируем обработку каждого изображения
    for img_path in test_images:
        img_name = img_path.name
        print(f"\nТестирование изображения: {img_name}")
        
        result = {
            "image": img_name,
            "success": False,
            "nodes": 0,
            "edges": 0,
            "processing_time": 0,
            "errors": []
        }
        
        try:
            # Измеряем время обработки
            start_time = time.time()
            
            # Обнаруживаем граф на изображении
            graph_data = detector.detect(str(img_path))
            
            # Строим граф NetworkX
            graph = builder.build_graph(graph_data)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Сохраняем результаты
            output_file = output_dir / f"{img_name.split('.')[0]}_graph.gexf"
            nx_success = builder.save_graph(graph, str(output_file))
            
            # Собираем метрики
            result["success"] = True
            result["nodes"] = len(graph.nodes)
            result["edges"] = len(graph.edges)
            result["processing_time"] = processing_time
            
            print(f"  ✓ Обработка успешна: {result['nodes']} узлов, {result['edges']} рёбер")
            print(f"  ✓ Время обработки: {processing_time:.2f} сек")
            print(f"  ✓ Результат сохранен в {output_file}")
            
        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
            print(f"  ✗ Ошибка при обработке: {e}")
        
        test_results.append(result)
    
    # Сохраняем общий результат тестирования
    results_summary = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_images": len(test_images),
        "successful_images": sum(r["success"] for r in test_results),
        "total_nodes": sum(r["nodes"] for r in test_results),
        "total_edges": sum(r["edges"] for r in test_results),
        "average_time": sum(r["processing_time"] for r in test_results) / len(test_results) if test_results else 0,
        "results": test_results
    }
    
    # Сохраняем результаты в JSON
    with open(output_dir / "functional_test_results.json", "w") as f:
        json.dump(results_summary, f, indent=2)
    
    # Выводим сводку
    print("\n" + "="*60)
    print("СВОДКА ФУНКЦИОНАЛЬНОГО ТЕСТИРОВАНИЯ")
    print("="*60)
    print(f"Всего изображений: {results_summary['total_images']}")
    print(f"Успешно обработано: {results_summary['successful_images']}")
    print(f"Всего узлов обнаружено: {results_summary['total_nodes']}")
    print(f"Всего рёбер обнаружено: {results_summary['total_edges']}")
    print(f"Среднее время обработки: {results_summary['average_time']:.2f} сек")
    print("\nРезультаты тестирования сохранены в:")
    print(f"  {output_dir / 'functional_test_results.json'}")
    
    return results_summary['successful_images'] == results_summary['total_images']

if __name__ == "__main__":
    success = run_functional_tests()
    sys.exit(0 if success else 1)
