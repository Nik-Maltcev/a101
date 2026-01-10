# Implementation Plan: Defect Classifier

## Overview

Реализация сервиса для обработки Excel-файлов с комментариями о дефектах. Используем Python, FastAPI, Celery, Redis, openpyxl, rapidfuzz и LLM API.

## Tasks

- [x] 1. Настройка проекта и базовой структуры
  - [x] 1.1 Создать структуру директорий и файлы конфигурации
    - Создать app/, data/, uploads/, results/, static/, tests/
    - Создать requirements.txt с зависимостями
    - Создать config.py с настройками
    - _Requirements: 1.1, 1.3_
  - [x] 1.2 Настроить FastAPI приложение
    - Создать main.py с базовым приложением
    - Настроить CORS и статические файлы
    - _Requirements: 9.1_
  - [x] 1.3 Настроить Celery и Redis
    - Создать worker/tasks.py с базовой конфигурацией
    - _Requirements: 1.5_

- [x] 2. Реализовать модели данных
  - [x] 2.1 Создать Pydantic схемы
    - JobStatus enum, Job, JobResponse, JobStatusResponse
    - SplitResult, ClassifyResult, ExpandedRow
    - _Requirements: 8.1_
  - [ ]* 2.2 Написать property-тест для моделей
    - **Property 7: Split Response Parsing Round-Trip**
    - **Property 12: Classify Response Parsing Round-Trip**
    - **Validates: Requirements 3.3, 6.3**

- [x] 3. Реализовать ExcelReader
  - [x] 3.1 Создать класс ExcelReader
    - Метод read_file для чтения xlsx
    - Метод find_comment_column для поиска столбца
    - _Requirements: 2.1, 2.2, 2.3_
  - [ ]* 3.2 Написать property-тесты для ExcelReader
    - **Property 4: Comment Column Detection**
    - **Property 5: Row Extraction Completeness**
    - **Validates: Requirements 2.2, 2.3**

- [x] 4. Реализовать CategoryIndex
  - [x] 4.1 Создать класс CategoryIndex
    - Метод load_categories для загрузки справочника
    - Метод build_index для построения fuzzy-индекса
    - Метод find_top_n для поиска кандидатов
    - Метод check_and_rebuild для отслеживания изменений
    - _Requirements: 5.1, 5.2, 5.3, 6.1_
  - [ ]* 4.2 Написать property-тест для CategoryIndex
    - **Property 11: Category Search Result Count**
    - **Validates: Requirements 5.2, 6.1**

- [x] 5. Реализовать LLM Client
  - [x] 5.1 Создать класс LLMClient
    - Метод split_comments для разделения комментариев
    - Метод classify_defects для классификации
    - Поддержка батчевой обработки
    - _Requirements: 3.2, 3.4, 6.2, 6.5_

- [x] 6. Checkpoint - Базовые компоненты
  - Убедиться что все тесты проходят
  - Проверить что CategoryIndex загружает справочник

- [x] 7. Реализовать SplitService
  - [x] 7.1 Создать класс SplitService
    - Метод split_comment для одного комментария
    - Метод split_batch для батчевой обработки
    - Кэширование по hash(comment)
    - Обработка пустых комментариев
    - _Requirements: 3.1, 3.3, 3.4, 3.5_
  - [ ]* 7.2 Написать property-тесты для SplitService
    - **Property 6: Empty Comment Handling**
    - **Property 8: Split Caching Idempotence**
    - **Validates: Requirements 3.1, 3.5**

- [x] 8. Реализовать функцию Expand
  - [x] 8.1 Создать функцию expand_rows
    - Размножение строк по количеству дефектов
    - Копирование всех столбцов
    - Замена КОММЕНТАРИЙ на текст дефекта
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [ ]* 8.2 Написать property-тесты для expand
    - **Property 9: Row Expansion Count**
    - **Property 10: Column Preservation Invariant**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 7.2**

- [x] 9. Реализовать ClassifyService
  - [x] 9.1 Создать класс ClassifyService
    - Метод classify_defect для одного дефекта
    - Метод classify_batch для батчевой обработки
    - Кэширование результатов
    - _Requirements: 6.1, 6.3, 6.4, 6.5, 6.6_
  - [ ]* 9.2 Написать property-тесты для ClassifyService
    - **Property 13: Category Assignment Completeness**
    - **Property 14: Classify Caching Idempotence**
    - **Validates: Requirements 6.4, 6.6**

- [x] 10. Реализовать ExcelWriter
  - [x] 10.1 Создать класс ExcelWriter
    - Метод write_result для записи результата
    - Добавление столбца "Категория дефекта"
    - _Requirements: 7.1, 7.2, 7.3_
  - [ ]* 10.2 Написать property-тест для ExcelWriter
    - **Property 15: Output File Path Convention**
    - **Validates: Requirements 7.3**

- [x] 11. Checkpoint - Все сервисы готовы
  - Убедиться что все тесты проходят
  - Проверить интеграцию сервисов

- [x] 12. Реализовать API endpoints
  - [x] 12.1 Создать POST /jobs endpoint
    - Валидация формата файла
    - Сохранение файла в uploads/
    - Создание задачи в очереди
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  - [ ]* 12.2 Написать property-тесты для загрузки
    - **Property 1: File Format Validation**
    - **Property 2: Job ID Uniqueness**
    - **Property 3: File Persistence Round-Trip**
    - **Validates: Requirements 1.1, 1.2, 1.3**
  - [x] 12.3 Создать GET /jobs/{job_id} endpoint
    - Возврат статуса, прогресса, download_url
    - _Requirements: 8.1, 8.2_
  - [ ]* 12.4 Написать property-тесты для статуса
    - **Property 17: Status Response Completeness**
    - **Property 18: Download URL Availability**
    - **Validates: Requirements 8.1, 8.2**
  - [x] 12.5 Создать GET /jobs/{job_id}/download endpoint
    - Отдача файла результата
    - _Requirements: 8.3, 8.4_
  - [ ]* 12.6 Написать property-тест для скачивания
    - **Property 19: Download Round-Trip**
    - **Validates: Requirements 8.3**

- [x] 13. Реализовать Celery task
  - [x] 13.1 Создать task process_job
    - Чтение файла через ExcelReader
    - Разделение комментариев через SplitService
    - Размножение строк через expand_rows
    - Классификация через ClassifyService
    - Запись результата через ExcelWriter
    - Обновление статуса задачи
    - _Requirements: 2.1, 3.1, 4.1, 6.1, 7.1, 7.4_
  - [ ]* 13.2 Написать property-тест для статуса
    - **Property 16: Status Update on Completion**
    - **Validates: Requirements 7.4**

- [x] 14. Checkpoint - Backend готов
  - Убедиться что все тесты проходят
  - Протестировать полный цикл через API

- [x] 15. Реализовать Web UI
  - [x] 15.1 Создать HTML страницу
    - Форма загрузки файла
    - Отображение прогресса
    - Кнопка скачивания результата
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 16. Финальный checkpoint
  - Убедиться что все тесты проходят
  - Проверить работу через веб-интерфейс

## Notes

- Задачи с `*` опциональны и могут быть пропущены для быстрого MVP
- Каждая задача ссылается на конкретные требования
- Property-тесты используют pytest + hypothesis
- Для тестирования LLM используем mock-ответы
