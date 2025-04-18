"""
Скрипт для тестирования API сервера GraphExtractor.
"""

import os
import glob
import json
import time
import requests
import subprocess
import signal
from pathlib import Path

def test_api():
    """Тестирует API сервер GraphExtractor."""
    
    api_url = "http://localhost:8000"
    results_dir = "test_results/api_test"
    os.makedirs(results_dir, exist_ok=True)
    
    # Получаем список всех изображений для тестирования
    image_files = glob.glob("test_images/*.png") + \
                 glob.glob("test_images/*.jpg") + \
                 glob.glob("test_images/*.jpeg")
    
    if not image_files:
        print("Ошибка: Изображения для тестирования не найдены")
        return False
    
    # Запускаем API сервер
    print("Запуск API сервера...")
    try:
        server_process = subprocess.Popen(
            ["python", "-m", "graphextractor.api.app"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Даем серверу время на запуск
        time.sleep(5)
        
        # Проверяем, что сервер запущен
        try:
            response = requests.get(f"{api_url}/docs")
            if response.status_code != 200:
                print(f"Ошибка: API сервер не отвечает. Код: {response.status_code}")
                server_process.kill()
                return False
        except requests.exceptions.ConnectionError:
            print("Ошибка: Не удалось подключиться к API серверу")
            server_process.kill()
            return False
            
        print("API сервер успешно запущен")
        
        # Тестируем каждое изображение
        results = []
        
        for image_path in image_files:
            image_name = Path(image_path).name
            print(f"Тестирование изображения: {image_name}")
            
            try:
                # 1. Распознавание графа
                with open(image_path, "rb") as img_file:
                    files = {"file": (image_name, img_file, "image/png")}
                    data = {
                        "output_format": "gexf",
                        "visualize": "true",
                        "enable_ocr": "true",
                        "enable_cache": "true",
                        "enhance_image": "true"
                    }
                    
                    start_time = time.time()
                    response = requests.post(
                        f"{api_url}/extract_graph/",
                        files=files,
                        data=data
                    )
                    process_time = time.time() - start_time
                    
                if response.status_code != 200:
                    print(f"Ошибка при обработке {image_name}: {response.text}")
                    results.append({
                        "image_name": image_name,
                        "status": "error",
                        "status_code": response.status_code,
                        "error": response.text
                    })
                    continue
                
                result = response.json()
                
                # 2. Загрузка результатов
                graph_filename = os.path.basename(result["graph_file"])
                graph_response = requests.get(f"{api_url}/download/{graph_filename}")
                
                if graph_response.status_code == 200:
                    with open(os.path.join(results_dir, graph_filename), "wb") as f:
                        f.write(graph_response.content)
                
                # 3. Загрузка визуализации, если доступна
                vis_filename = ""
                if "visualization_file" in result:
                    vis_filename = os.path.basename(result["visualization_file"])
                    vis_response = requests.get(f"{api_url}/download/{vis_filename}")
                    
                    if vis_response.status_code == 200:
                        with open(os.path.join(results_dir, vis_filename), "wb") as f:
                            f.write(vis_response.content)
                
                # 4. Повторный запрос для проверки кэширования
                print("  Тестирование кэширования...")
                
                with open(image_path, "rb") as img_file:
                    files = {"file": (image_name, img_file, "image/png")}
                    
                    start_time_cached = time.time()
                    response_cached = requests.post(
                        f"{api_url}/extract_graph/",
                        files=files,
                        data=data
                    )
                    process_time_cached = time.time() - start_time_cached
                
                # 5. Запись результатов
                results.append({
                    "image_name": image_name,
                    "status": "success",
                    "nodes_count": result["nodes_count"],
                    "edges_count": result["edges_count"],
                    "first_request_time": process_time,
                    "cached_request_time": process_time_cached,
                    "cache_speedup": process_time / max(process_time_cached, 0.001),
                    "graph_file": os.path.join(results_dir, graph_filename),
                    "visualization_file": os.path.join(results_dir, vis_filename) if vis_filename else None
                })
                
                print(f"  Узлов: {result['nodes_count']}, Рёбер: {result['edges_count']}")
                print(f"  Время обработки: {process_time:.2f} сек")
                print(f"  Время с кэшированием: {process_time_cached:.2f} сек")
                print(f"  Ускорение: {process_time / max(process_time_cached, 0.001):.1f}x")
                
            except Exception as e:
                print(f"  Ошибка при тестировании {image_name}: {str(e)}")
                results.append({
                    "image_name": image_name,
                    "status": "error",
                    "error": str(e)
                })
        
        # Сохраняем результаты
        with open(os.path.join(results_dir, "api_results.json"), "w") as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": results
            }, f, indent=2)
            
        print(f"\nРезультаты API-тестирования сохранены в {os.path.join(results_dir, 'api_results.json')}")
        
    except Exception as e:
        print(f"Ошибка при тестировании API: {str(e)}")
        return False
    finally:
        # Останавливаем сервер
        print("Остановка API сервера...")
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except:
            server_process.kill()
    
    return True

if __name__ == "__main__":
    test_api()
