"""
Скрипт для запуска всех тестов GraphExtractor в правильной последовательности.
"""

import os
import sys
import time
import subprocess
import argparse

def run_command(command, description):
    """Запускает команду и печатает результат."""
    print(f"\n{'-'*60}")
    print(f"Запуск: {description}")
    print(f"{'-'*60}\n")
    
    start_time = time.time()
    result = subprocess.run(command, shell=True)
    end_time = time.time()
    
    if result.returncode == 0:
        print(f"\n✅ {description} выполнено успешно за {end_time - start_time:.2f} секунд\n")
        return True
    else:
        print(f"\n❌ {description} завершилось с ошибкой (код: {result.returncode})\n")
        return False

def check_opencv():
    """Проверяет наличие OpenCV и системных зависимостей."""
    try:
        # Пробуем импортировать OpenCV
        import cv2
        print("✅ OpenCV доступен и работает корректно")
        return True
    except ImportError as e:
        print("⚠️ Проблема с OpenCV: " + str(e))
        print("\nДля решения проблемы с libGL.so.1 установите системные зависимости:")
        print("  sudo apt-get update && sudo apt-get install -y libgl1-mesa-glx libglib2.0-0")
        print("\nВы можете продолжить с ограниченным тестированием без OpenCV.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Запуск тестов GraphExtractor")
    parser.add_argument("--skip-basic", action="store_true", help="Пропустить базовые тесты")
    parser.add_argument("--skip-batch", action="store_true", help="Пропустить пакетное тестирование")
    parser.add_argument("--skip-api", action="store_true", help="Пропустить тестирование API")
    parser.add_argument("--skip-viz", action="store_true", help="Пропустить визуализацию результатов")
    parser.add_argument("--no-opencv", action="store_true", help="Запустить тесты, не требующие OpenCV")
    args = parser.parse_args()
    
    # Проверяем OpenCV
    has_opencv = check_opencv()
    if args.no_opencv or not has_opencv:
        print("Запуск в режиме без OpenCV.")
        args.skip_batch = True  # batch_test требует OpenCV
        args.skip_api = True    # API тестирование требует OpenCV
    
    # Проверка наличия тестовых изображений
    if not os.path.exists("test_images") or not os.listdir("test_images"):
        print("⚠️ Тестовые изображения не найдены. Создаем тестовое изображение...")
        os.makedirs("test_images", exist_ok=True)
        
        try:
            from PIL import Image, ImageDraw
            import numpy as np
            
            # Создаем простое изображение графа
            width, height = 800, 600
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # Определяем узлы
            nodes = [
                (200, 150, 'A'),
                (500, 150, 'B'),
                (200, 400, 'C'),
                (500, 400, 'D'),
            ]
            
            # Рисуем ребра
            for i, (x1, y1, _) in enumerate(nodes):
                for j, (x2, y2, _) in enumerate(nodes):
                    if i < j and ((i + j) % 3 != 0):
                        draw.line([(x1, y1), (x2, y2)], fill='black', width=2)
            
            # Рисуем узлы
            for x, y, label in nodes:
                # Оранжевый круг с черной обводкой
                draw.ellipse((x-30, y-30, x+30, y+30), fill=(255, 120, 0), outline='black', width=2)
                # Текст
                draw.text((x-10, y-10), label, fill='black')
            
            # Сохраняем изображение
            image.save("test_images/simple_graph.png")
            print("✅ Тестовое изображение создано: test_images/simple_graph.png")
        except Exception as e:
            print(f"❌ Не удалось создать тестовое изображение: {str(e)}")
            print("⚠️ Пожалуйста, добавьте изображения в директорию test_images вручную")
            return 1
    
    # 0. Создаем директорию для результатов тестов
    os.makedirs("test_results", exist_ok=True)
    
    # 1. Запуск базового теста
    if not args.skip_basic:
        if not run_command("python quick_test.py", "Базовое тестирование"):
            print("⚠️ Базовое тестирование завершилось с ошибками.")
    
    # 2. Запуск пакетного тестирования
    if not args.skip_batch:
        if not run_command("python batch_test.py", "Пакетное тестирование"):
            print("⚠️ Пакетное тестирование завершилось с ошибками.")
    
    # 3. Запуск API тестирования
    if not args.skip_api:
        if not run_command("python test_api.py", "Тестирование API"):
            print("⚠️ Тестирование API завершилось с ошибками.")
    
    # 4. Визуализация результатов
    if not args.skip_viz:
        if os.path.exists("test_results/test_summary.json"):
            if not run_command("python visualize_results.py", "Визуализация результатов"):
                print("⚠️ Визуализация результатов завершилась с ошибками.")
        else:
            print("⚠️ Файл с результатами тестирования не найден, визуализация пропущена.")
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*60)
    print("\nПроверьте результаты в директории test_results.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
