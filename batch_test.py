"""
Скрипт для пакетного тестирования GraphExtractor на наборе изображений.
"""

import os
import time
import glob
import sys
import json
from pathlib import Path

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graphextractor.detector import GraphDetector
from graphextractor.graph_builder import NetworkXBuilder
from graphextractor.preprocessing import QualityAnalyzer, ImageEnhancer

def run_batch_test(images_dir="test_images", results_dir="test_results"):
    """Выполняет тестирование GraphExtractor на всех изображениях в указанной директории."""
    
    # Создаем директорию для результатов
    os.makedirs(results_dir, exist_ok=True)
    
    # Получаем список всех изображений
    image_files = glob.glob(os.path.join(images_dir, "*.png")) + \
                 glob.glob(os.path.join(images_dir, "*.jpg")) + \
                 glob.glob(os.path.join(images_dir, "*.jpeg"))
    
    if not image_files:
        print(f"Ошибка: Изображения не найдены в директории {images_dir}")
        return False
    
    print(f"Найдено {len(image_files)} тестовых изображений")
    
    # Анализатор качества
    quality_analyzer = QualityAnalyzer()
    
    # Улучшитель изображений
    enhancer = ImageEnhancer()
    
    # Общие результаты теста
    test_results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "images_tested": len(image_files),
        "results": []
    }
    
    # Тестируем каждое изображение
    for i, image_path in enumerate(image_files):
        image_name = os.path.basename(image_path)
        print(f"\n[{i+1}/{len(image_files)}] Тестирование {image_name}...")
        
        # Создаем поддиректорию для результатов этого изображения
        image_result_dir = os.path.join(results_dir, Path(image_name).stem)
        os.makedirs(image_result_dir, exist_ok=True)
        
        try:
            # 1. Тестирование без улучшения и OCR
            print("  Базовое распознавание без улучшений...")
            start_time = time.time()
            detector_base = GraphDetector(config={
                "ocr_enabled": False,
                "enhancer": {"enabled": False},
                "caching_enabled": False
            })
            result_base = detector_base.detect(image_path)
            base_time = time.time() - start_time
            
            # Сохраняем базовый результат
            builder = NetworkXBuilder()
            graph_base = builder.build_graph(result_base)
            base_graph_path = os.path.join(image_result_dir, "base_graph.gexf")
            builder.save_graph(graph_base, base_graph_path)
            base_viz_path = os.path.join(image_result_dir, "base_visualization.png")
            builder.visualize_graph(graph_base, base_viz_path)
            
            # 2. Тестирование с улучшением и OCR
            print("  Расширенное распознавание с улучшениями и OCR...")
            start_time = time.time()
            detector_enhanced = GraphDetector(config={
                "ocr_enabled": True,
                "enhancer": {"enabled": True},
                "caching_enabled": False
            })
            result_enhanced = detector_enhanced.detect(image_path)
            enhanced_time = time.time() - start_time
            
            # Сохраняем улучшенный результат
            graph_enhanced = builder.build_graph(result_enhanced)
            enhanced_graph_path = os.path.join(image_result_dir, "enhanced_graph.gexf")
            builder.save_graph(graph_enhanced, enhanced_graph_path)
            enhanced_viz_path = os.path.join(image_result_dir, "enhanced_visualization.png")
            builder.visualize_graph(graph_enhanced, enhanced_viz_path)
            
            # 3. Тест кэширования
            print("  Тестирование кэширования...")
            detector_cached = GraphDetector(config={
                "ocr_enabled": True,
                "enhancer": {"enabled": True},
                "caching_enabled": True
            })
            
            # Первый запуск (должен создать кэш)
            start_time = time.time()
            detector_cached.detect(image_path)
            first_cached_time = time.time() - start_time
            
            # Второй запуск (должен использовать кэш)
            start_time = time.time()
            detector_cached.detect(image_path)
            second_cached_time = time.time() - start_time
            
            # Запись результатов для этого изображения
            image_result = {
                "image_name": image_name,
                "base_nodes": len(result_base["nodes"]),
                "base_edges": len(result_base["edges"]),
                "base_time": base_time,
                "enhanced_nodes": len(result_enhanced["nodes"]),
                "enhanced_edges": len(result_enhanced["edges"]),
                "enhanced_time": enhanced_time,
                "cache_first_time": first_cached_time,
                "cache_second_time": second_cached_time,
                "cache_speedup": first_cached_time / max(second_cached_time, 0.001),
                "quality_level": result_enhanced.get("quality_info", {}).get("quality_level", "N/A"),
                "ocr_texts": len(result_enhanced.get("text_regions", [])),
                "base_graph_path": base_graph_path,
                "base_viz_path": base_viz_path,
                "enhanced_graph_path": enhanced_graph_path,
                "enhanced_viz_path": enhanced_viz_path
            }
            
            test_results["results"].append(image_result)
            
            print(f"  Базовое распознавание: {len(result_base['nodes'])} узлов, " 
                 f"{len(result_base['edges'])} ребер за {base_time:.2f} сек")
            print(f"  Улучшенное распознавание: {len(result_enhanced['nodes'])} узлов, "
                 f"{len(result_enhanced['edges'])} ребер за {enhanced_time:.2f} сек")
            print(f"  Ускорение кэширования: {image_result['cache_speedup']:.1f}x "
                 f"({first_cached_time:.2f} сек -> {second_cached_time:.2f} сек)")
            
        except Exception as e:
            print(f"  Ошибка при обработке {image_name}: {str(e)}")
            test_results["results"].append({
                "image_name": image_name,
                "error": str(e)
            })
    
    # Сохраняем общие результаты
    summary_path = os.path.join(results_dir, "test_summary.json")
    with open(summary_path, "w") as f:
        json.dump(test_results, f, indent=2)
    
    # Выводим сводку
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*50)
    print(f"Обработано изображений: {len(image_files)}")
    print(f"Успешно: {len([r for r in test_results['results'] if 'error' not in r])}")
    print(f"С ошибками: {len([r for r in test_results['results'] if 'error' in r])}")
    print(f"Сводка сохранена в: {summary_path}")
    
    return True

if __name__ == "__main__":
    run_batch_test()
