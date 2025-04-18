"""
Скрипт для проверки и исправления проблем с зависимостями.
"""

import subprocess
import sys
import os
import importlib
import pkg_resources

def print_section(title):
    """Печатает заголовок раздела."""
    print("\n" + "="*60)
    print(title)
    print("="*60)

def check_system_dependencies():
    """Проверяет системные зависимости."""
    print("Проверка системных библиотек...")
    
    # Проверяем системные библиотеки для OpenCV
    libraries = [
        "libGL.so.1",
        "libglib-2.0.so",
        "libSM.so",
        "libXrender.so",
        "libXext.so"
    ]
    
    for lib in libraries:
        try:
            # Проверяем наличие библиотеки
            result = subprocess.run(
                ["ldconfig", "-p"], 
                capture_output=True, 
                text=True
            )
            if lib in result.stdout:
                print(f"✓ {lib} найдена")
            else:
                print(f"✗ {lib} не найдена")
        except Exception:
            print(f"? Не удалось проверить {lib}")
    
    print("\nРекомендации по установке системных зависимостей:")
    print("sudo apt-get update && sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6")

def check_package_versions():
    """Проверяет версии установленных пакетов."""
    print("Проверка версий пакетов...")
    
    packages = [
        "opencv-python",
        "torch",
        "torchvision",
        "easyocr",
        "numpy",
        "networkx",
        "matplotlib",
        "fastapi",
        "uvicorn",
        "scikit-image",
        "pillow"
    ]
    
    for package in packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"✓ {package}: версия {version}")
        except pkg_resources.DistributionNotFound:
            print(f"✗ {package}: не установлен")
        except Exception as e:
            print(f"? {package}: ошибка при проверке - {str(e)}")

def fix_torch_dependencies():
    """Исправляет проблемы с torch и torchvision."""
    print("Попытка исправить проблемы с PyTorch...")
    
    try:
        # Проверяем текущие версии
        torch_version = None
        torchvision_version = None
        
        try:
            torch_version = pkg_resources.get_distribution("torch").version
            print(f"Текущая версия torch: {torch_version}")
        except:
            print("Torch не установлен")
            
        try:
            torchvision_version = pkg_resources.get_distribution("torchvision").version
            print(f"Текущая версия torchvision: {torchvision_version}")
        except:
            print("Torchvision не установлен")
        
        # Выводим рекомендации
        print("\nРекомендации по исправлению:")
        print("1. Переустановите совместимые версии:")
        print("   pip uninstall -y torch torchvision")
        print("   pip install torch==1.13.1 torchvision==0.14.1")
        print("\n2. Или используйте CPU-версии:")
        print("   pip install torch==1.13.1+cpu torchvision==0.14.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html")
        
    except Exception as e:
        print(f"Ошибка при проверке torch: {str(e)}")

def create_minimal_test():
    """Создает минимальный тест для проверки работоспособности."""
    print("Создание минимального теста...")
    
    # Создаем директории
    os.makedirs("test_results", exist_ok=True)
    
    # Пробуем запустить самые базовые компоненты
    try:
        # Проверка networkx
        import networkx as nx
        G = nx.Graph()
        G.add_node(1, name="Node 1")
        G.add_node(2, name="Node 2")
        G.add_edge(1, 2, weight=1.0)
        print(f"✓ NetworkX работает: {len(G.nodes)} узлов, {len(G.edges)} ребер")
        
        # Проверка matplotlib (базовая)
        import matplotlib
        matplotlib.use('Agg')  # Не-интерактивный бэкенд
        print("✓ Matplotlib работает")
        
        # Создание тестовой сводки
        import json
        test_data = {"test": "data", "status": "ok"}
        with open("test_results/minimal_test.json", "w") as f:
            json.dump(test_data, f)
        print("✓ JSON запись работает")
        
    except Exception as e:
        print(f"✗ Ошибка при выполнении минимального теста: {str(e)}")

def main():
    print_section("ПРОВЕРКА ЗАВИСИМОСТЕЙ ПРОЕКТА")
    
    check_system_dependencies()
    
    print_section("ПРОВЕРКА PYTHON-ПАКЕТОВ")
    
    check_package_versions()
    
    print_section("РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ PYTORCH")
    
    fix_torch_dependencies()
    
    print_section("МИНИМАЛЬНЫЙ ТЕСТ")
    
    create_minimal_test()
    
    print_section("ИТОГИ И РЕКОМЕНДАЦИИ")
    
    print("""
1. Если вы видите ошибку с libGL.so.1, установите системные зависимости:
   sudo apt-get update && sudo apt-get install -y libgl1-mesa-glx libglib2.0-0

2. Если есть проблемы с torch/torchvision, переустановите их совместимые версии:
   pip uninstall -y torch torchvision
   pip install torch==1.13.1 torchvision==0.14.1

3. Для тестирования без OpenCV и сложных зависимостей:
   python run_all_tests.py --no-opencv

4. Для просмотра результатов визуализации:
   python visualize_results.py
""")

if __name__ == "__main__":
    main()
