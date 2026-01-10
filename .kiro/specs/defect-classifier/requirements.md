# Requirements Document

## Introduction

Сервис для автоматической обработки Excel-файлов с комментариями о дефектах. Система разделяет комментарии на отдельные дефекты с помощью LLM, затем классифицирует каждый дефект по категориям из справочника. Результат — новый Excel-файл с размноженными строками и проставленными категориями.

## Glossary

- **Job**: Задача обработки одного загруженного файла
- **Defect**: Отдельный дефект, выделенный из комментария
- **Category_Index**: Индекс для быстрого поиска похожих категорий (fuzzy/vector)
- **Split_Service**: Компонент для разделения комментариев на дефекты через LLM
- **Classify_Service**: Компонент для классификации дефектов по категориям
- **Worker**: Фоновый процесс обработки задач (Celery/RQ)
- **Category_Reference**: Справочник категорий дефектов на сервере

## Requirements

### Requirement 1: Загрузка файла

**User Story:** As a пользователь, I want загрузить Excel-файл с комментариями, so that система может его обработать.

#### Acceptance Criteria

1. WHEN пользователь отправляет файл через API THEN THE System SHALL принять только файлы формата .xlsx
2. WHEN файл успешно загружен THEN THE System SHALL вернуть уникальный job_id
3. WHEN файл загружен THEN THE System SHALL сохранить его во временное хранилище
4. IF файл имеет неверный формат THEN THE System SHALL вернуть ошибку с описанием проблемы
5. WHEN файл загружен THEN THE System SHALL создать задачу в очереди для обработки

### Requirement 2: Чтение и парсинг Excel

**User Story:** As a система, I want прочитать загруженный файл, so that можно извлечь комментарии для обработки.

#### Acceptance Criteria

1. WHEN Worker получает задачу THEN THE System SHALL открыть XLSX файл с помощью openpyxl
2. WHEN файл открыт THEN THE System SHALL найти столбец "КОММЕНТАРИЙ" по названию
3. WHEN столбец найден THEN THE System SHALL извлечь все строки с данными
4. IF столбец "КОММЕНТАРИЙ" не найден THEN THE System SHALL завершить задачу с ошибкой

### Requirement 3: Разделение комментариев (Split)

**User Story:** As a система, I want разделить каждый комментарий на отдельные дефекты, so that каждый дефект можно классифицировать отдельно.

#### Acceptance Criteria

1. WHEN комментарий пустой или содержит "нет замечаний" THEN THE Split_Service SHALL вернуть пустой список дефектов
2. WHEN комментарий содержит текст THEN THE Split_Service SHALL отправить его в LLM для разделения
3. WHEN LLM возвращает ответ THEN THE Split_Service SHALL распарсить JSON формата {"defects":[{"text":"..."}]}
4. WHEN комментарии обрабатываются THEN THE Split_Service SHALL группировать их в батчи по 20-50 штук
5. WHEN комментарий уже обрабатывался THEN THE Split_Service SHALL использовать кэшированный результат по hash(comment)

### Requirement 4: Размножение строк (Expand)

**User Story:** As a система, I want создать отдельную строку для каждого дефекта, so that каждый дефект имеет свою категорию.

#### Acceptance Criteria

1. WHEN дефекты извлечены из комментария THEN THE System SHALL создать отдельную строку для каждого дефекта
2. WHEN строка создаётся THEN THE System SHALL скопировать все исходные столбцы
3. WHEN строка создаётся THEN THE System SHALL заменить значение столбца "КОММЕНТАРИЙ" на текст дефекта
4. WHEN комментарий содержит 5 дефектов THEN THE System SHALL создать 5 строк с одинаковыми полями кроме "КОММЕНТАРИЙ"

### Requirement 5: Управление справочником категорий

**User Story:** As a система, I want загрузить и индексировать справочник категорий, so that можно быстро находить подходящие категории.

#### Acceptance Criteria

1. WHEN сервис запускается THEN THE System SHALL загрузить справочник категорий из data/categories.xlsx
2. WHEN справочник загружен THEN THE Category_Index SHALL построить индекс для fuzzy-поиска
3. WHEN файл справочника изменился THEN THE System SHALL пересобрать индекс автоматически
4. WHEN индекс готов THEN THE Category_Index SHALL хранить его в памяти для быстрого доступа

### Requirement 6: Классификация дефектов

**User Story:** As a система, I want присвоить категорию каждому дефекту, so that пользователь получит классифицированные данные.

#### Acceptance Criteria

1. WHEN дефект готов к классификации THEN THE Category_Index SHALL найти top-N (N=10) похожих категорий
2. WHEN кандидаты найдены THEN THE Classify_Service SHALL отправить дефект и кандидатов в LLM
3. WHEN LLM возвращает ответ THEN THE Classify_Service SHALL распарсить JSON формата {"chosen":"категория"}
4. WHEN категория определена THEN THE System SHALL записать её в столбец "Категория дефекта"
5. WHEN дефекты классифицируются THEN THE Classify_Service SHALL группировать их в батчи по 50 штук
6. WHEN дефект уже классифицировался THEN THE Classify_Service SHALL использовать кэшированный результат

### Requirement 7: Формирование результата

**User Story:** As a система, I want создать выходной Excel-файл, so that пользователь может скачать результат.

#### Acceptance Criteria

1. WHEN все дефекты классифицированы THEN THE System SHALL создать новый XLSX файл
2. WHEN файл создаётся THEN THE System SHALL включить все исходные столбцы плюс "Категория дефекта"
3. WHEN файл готов THEN THE System SHALL сохранить его в results/{job_id}_processed.xlsx
4. WHEN файл сохранён THEN THE System SHALL обновить статус задачи на "completed"

### Requirement 8: API статуса и скачивания

**User Story:** As a пользователь, I want отслеживать статус обработки и скачать результат, so that я получу обработанный файл.

#### Acceptance Criteria

1. WHEN пользователь запрашивает статус THEN THE System SHALL вернуть текущий статус, прогресс и download_url
2. WHEN задача завершена THEN THE System SHALL предоставить ссылку для скачивания
3. WHEN пользователь запрашивает скачивание THEN THE System SHALL отдать файл результата
4. IF задача не найдена THEN THE System SHALL вернуть ошибку 404

### Requirement 9: Web-интерфейс

**User Story:** As a пользователь, I want использовать простой веб-интерфейс, so that я могу загружать файлы и скачивать результаты без API.

#### Acceptance Criteria

1. WHEN пользователь открывает сайт THEN THE System SHALL показать страницу с формой загрузки файла
2. WHEN файл загружается THEN THE System SHALL показать прогресс обработки
3. WHEN обработка завершена THEN THE System SHALL показать кнопку "Скачать результат"
4. WHILE файл обрабатывается THEN THE System SHALL показывать текущий этап: "Разделяю комментарии" / "Проставляю категории"
