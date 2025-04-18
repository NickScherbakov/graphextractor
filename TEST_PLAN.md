# План тестирования GraphExtractor

## 1. Установка проекта

```bash
# Установка зависимостей
cd /workspaces/graphextractor
pip install -e .

# Проверка установки
python -c "import graphextractor; print(f'GraphExtractor version: {graphextractor.__version__}')"
```

## 2. Подготовка тестовых данных

Для полноценного тестирования требуются изображения с различными типами графовых структур:
- Простые графы с четкими узлами и ребрами
- Изображения с текстовыми метками на узлах и ребрах
- Изображения с шумом и низким качеством
- Сложные графовые структуры (например, направленные графы)

Тестовые изображения можно положить в директорию `/workspaces/graphextractor/test_images/`.

## 3. Тестирование основного функционала

### 3.1. Тестирование через CLI

```bash
# Создаем директорию для результатов
mkdir -p /workspaces/graphextractor/test_results

# Запускаем распознавание через CLI
python -m graphextractor.cli /workspaces/graphextractor/test_images/simple_graph.png \
  --output /workspaces/graphextractor/test_results \
  --format gexf \
  --visualize
```

### 3.2. Тестирование Python API

```python
from graphextractor.detector import GraphDetector
from graphextractor.graph_builder import NetworkXBuilder

# Базовое распознавание
detector = GraphDetector()
result = detector.detect("/workspaces/graphextractor/test_images/simple_graph.png")

# Построение графа
builder = NetworkXBuilder()
graph = builder.build_graph(result)

# Проверка результатов
print(f"Detected {len(result['nodes'])} nodes and {len(result['edges'])} edges")
print(f"Graph has {len(graph.nodes)} nodes and {len(graph.edges)} edges")

# Сохранение и визуализация
builder.save_graph(graph, "/workspaces/graphextractor/test_results/test_graph.gexf")
builder.visualize_graph(graph, "/workspaces/graphextractor/test_results/test_viz.png")
```

## 4. Тестирование расширенных функций

### 4.1. Запуск демонстрационного скрипта

```bash
# Запуск с подробным выводом процесса
python /workspaces/graphextractor/examples/enhanced_detection_demo.py \
  /workspaces/graphextractor/test_images/complex_graph.png \
  --output_dir /workspaces/graphextractor/test_results \
  --show_steps
```

### 4.2. Тестирование OCR и обработки низкокачественных изображений

```python
import cv2
from graphextractor.preprocessing import ImageEnhancer, QualityAnalyzer
from graphextractor.text_recognition import OCRProcessor, TextMapper

# Загрузка изображения
image = cv2.imread("/workspaces/graphextractor/test_images/noisy_graph.png")

# Анализ качества
analyzer = QualityAnalyzer()
quality_info = analyzer.analyze(image)
print(f"Image quality: {quality_info['quality_level']}")

# Улучшение изображения
enhancer = ImageEnhancer()
enhanced = enhancer.apply_adaptive_enhancement(image)
cv2.imwrite("/workspaces/graphextractor/test_results/enhanced.png", enhanced)

# Распознавание текста
ocr = OCRProcessor(languages=['en'])
text_regions = ocr.extract_text(enhanced)
print(f"Found {len(text_regions)} text regions")
for region in text_regions[:5]:  # Первые 5 для примера
    print(f"  Text: '{region['text']}' (confidence: {region['confidence']:.2f})")
```

### 4.3. Тестирование кэширования

```python
from graphextractor.caching import CacheManager, ImageHashProvider

# Хэширование изображения
hasher = ImageHashProvider()
image = cv2.imread("/workspaces/graphextractor/test_images/simple_graph.png")
image_hash = hasher.compute_hash(image)
print(f"Image hash: {image_hash}")

# Работа с кэшем
cache = CacheManager(cache_dir="/workspaces/graphextractor/test_results/cache")
fake_result = {"test": "data"}
cache.set(image_hash, fake_result)

# Проверка получения из кэша
cached = cache.get(image_hash)
print(f"Retrieved from cache: {cached == fake_result}")
```

## 5. Тестирование REST API

### 5.1. Запуск API сервера

```bash
# Запуск в отдельном терминале или с nohup
python -m graphextractor.api.app &
```

### 5.2. Выполнение тестовых запросов

```bash
# Тестирование распознавания графа
curl -X POST http://localhost:8000/extract_graph/ \
  -F "file=@/workspaces/graphextractor/test_images/simple_graph.png" \
  -F "visualize=true" > /workspaces/graphextractor/test_results/api_response.json

# Проверка анализа качества изображения
curl -X POST http://localhost:8000/image_quality/ \
  -F "file=@/workspaces/graphextractor/test_images/noisy_graph.png" > /workspaces/graphextractor/test_results/quality_response.json
```

## 6. Оценка результатов

После проведения тестов необходимо проверить:

1. **Корректность распознавания** - правильно ли определены узлы и ребра
2. **Качество OCR** - насколько точно распознаны текстовые метки
3. **Эффективность улучшения качества** - насколько улучшилось распознавание после обработки
4. **Скорость работы** - особенно в сравнении с и без кэширования
5. **Стабильность API** - отсутствие сбоев при обработке различных изображений

## 7. Типичные проблемы и их решения

| Проблема | Возможное решение |
|----------|-------------------|
| Не распознаются некоторые узлы | Настройка параметров порогов в NodeDetector |
| Ложные срабатывания OCR | Увеличение минимального порога уверенности |
| Медленная работа API | Оптимизация параметров обработки или аппаратных ресурсов |
| Ошибки при работе с большими изображениями | Добавление предварительного масштабирования |

## 8. Контрольные тестовые случаи

1. **Простой граф** - проверка базовой функциональности
2. **Граф с текстовыми метками** - проверка работы OCR
3. **Низкокачественное изображение** - проверка улучшения качества
4. **Повторное распознавание** - проверка работы кэширования
5. **Несколько одновременных запросов к API** - проверка стабильности
