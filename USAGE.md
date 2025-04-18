# GraphExtractor: Руководство пользователя

## Введение

GraphExtractor - это инструмент для распознавания и извлечения графовых структур из изображений. Данное руководство описывает основные функции библиотеки и демонстрирует различные способы её использования.

## Установка

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/graphextractor.git
cd graphextractor

# Установка зависимостей
pip install -e .
```

## Базовое использование

### Через командную строку

```bash
# Обработка одного изображения
python -m graphextractor.cli path/to/image.png --output results --format gexf --visualize

# Обработка директории с изображениями
python -m graphextractor.cli path/to/images_dir --output results
```

### Через Python API

```python
from graphextractor.detector import GraphDetector
from graphextractor.graph_builder import NetworkXBuilder

# Создание детектора с настройками
detector = GraphDetector(config={
    "ocr_enabled": True,    # Включить распознавание текста
    "caching_enabled": True # Включить кэширование
})

# Обнаружение графа на изображении
result = detector.detect("path/to/image.png")

# Создание объекта NetworkX из результатов
builder = NetworkXBuilder()
graph = builder.build_graph(result)

# Сохранение результата
builder.save_graph(graph, "output.gexf", format="gexf")
builder.visualize_graph(graph, "visualization.png")
```

## Расширенные возможности

### Улучшение качества изображения

GraphExtractor включает модули для улучшения качества входных изображений:

```python
from graphextractor.preprocessing import ImageEnhancer, QualityAnalyzer

# Анализ качества изображения
quality_analyzer = QualityAnalyzer()
image = cv2.imread("path/to/image.png")
quality_info = quality_analyzer.analyze(image)
print(f"Quality level: {quality_info['quality_level']}")

# Улучшение изображения
enhancer = ImageEnhancer()
enhanced_image = enhancer.apply_adaptive_enhancement(image)
cv2.imwrite("enhanced.png", enhanced_image)
```

### Распознавание текста

Для распознавания текстовых меток на узлах и рёбрах:

```python
from graphextractor.text_recognition import OCRProcessor, TextMapper

# Распознавание текста на изображении
ocr = OCRProcessor(languages=['en', 'ru'])
text_regions = ocr.extract_text(image)

# Связывание текста с узлами графа
text_mapper = TextMapper()
labeled_nodes = text_mapper.map_text_to_nodes(nodes, text_regions)
labeled_edges = text_mapper.map_text_to_edges(edges, text_regions, nodes)
```

### Кэширование результатов

Для оптимизации повторной обработки одинаковых изображений:

```python
from graphextractor.caching import CacheManager, ImageHashProvider

# Создание хэша для изображения
hash_provider = ImageHashProvider()
image_hash = hash_provider.compute_hash(image)

# Работа с кэшем
cache = CacheManager(cache_dir="cache")
cached_result = cache.get(image_hash)
if not cached_result:
    result = process_image(image)
    cache.set(image_hash, result)
```

## REST API

Для запуска API-сервера:

```bash
python -m graphextractor.api.app
```

API будет доступен по адресу `http://localhost:8000`. Оно предоставляет следующие эндпоинты:

* `POST /extract_graph/` - Извлечение графа из загруженного изображения
* `GET /image_quality/` - Анализ качества загруженного изображения
* `GET /download/{file_path}` - Загрузка созданного файла
* `POST /clear_cache/` - Очистка кэша

### Пример запроса с использованием cURL

```bash
curl -X POST http://localhost:8000/extract_graph/ \
  -F "file=@path/to/image.png" \
  -F "output_format=gexf" \
  -F "visualize=true" \
  -F "enable_ocr=true"
```

## Демонстрация

Запустите демонстрационный скрипт для тестирования всех возможностей:

```bash
python examples/enhanced_detection_demo.py path/to/image.png --show_steps
```

## Устранение ограничений

GraphExtractor содержит ряд решений, преодолевающих ранее обнаруженные ограничения:

1. **Улучшенная точность распознавания**:
   - Адаптивная предобработка изображений
   - Анализ качества и выбор оптимальной стратегии

2. **Распознавание текста**:
   - OCR для обнаружения меток на графе
   - Привязка текста к узлам и рёбрам

3. **Улучшенное обнаружение связей**:
   - Более точное определение связей между узлами
   - Обработка разных типов линий и стрелок

4. **Устойчивость к низкому качеству**:
   - Анализ и улучшение изображений с шумом и низким контрастом
   - Адаптивные фильтры для разных условий освещения

5. **Кэширование результатов**:
   - Перцептуальное хэширование изображений
   - Сохранение промежуточных результатов для ускорения повторной обработки
