# Requirements Document

## Introduction

Интерактивный дашборд аналитики для проектной группы. После обработки файла с дефектами пользователь получает визуальную аналитику: статистику по категориям дефектов и динамическую аналитику по любым колонкам из загруженного файла.

## Glossary

- **Dashboard**: Интерактивная панель с графиками и статистикой
- **Defect_Category**: Категория дефекта, присвоенная системой
- **Dynamic_Column**: Любая колонка из загруженного Excel файла
- **Analytics_API**: Эндпоинт для получения агрегированных данных

## Requirements

### Requirement 1: Современный UI для загрузки файлов

**User Story:** As a проектный менеджер, I want красивый и интуитивный интерфейс загрузки, so that работа с системой была приятной.

#### Acceptance Criteria

1. THE UI SHALL display a modern card-based design with gradient backgrounds and shadows
2. THE UI SHALL support drag-and-drop file upload with visual feedback
3. THE UI SHALL show upload progress with animated progress bar
4. THE UI SHALL display processing stages (splitting, classifying) with clear status messages in Russian

### Requirement 2: Дашборд аналитики после обработки

**User Story:** As a проектный менеджер, I want видеть аналитику сразу после обработки файла, so that я мог быстро оценить ситуацию.

#### Acceptance Criteria

1. WHEN processing is completed, THE Dashboard SHALL display analytics view with charts and statistics
2. THE Dashboard SHALL show summary cards: total rows, total defects, unique categories count
3. THE Dashboard SHALL provide prominent download button for processed Excel file
4. THE Dashboard SHALL allow returning to upload new file

### Requirement 3: Аналитика по категориям дефектов

**User Story:** As a проектный менеджер, I want видеть распределение дефектов по категориям, so that я мог выявить системные проблемы.

#### Acceptance Criteria

1. THE Dashboard SHALL display horizontal bar chart with top-15 defect categories
2. THE Dashboard SHALL show count and percentage for each category
3. THE Dashboard SHALL use color coding to highlight most frequent categories
4. THE Dashboard SHALL show "НЕ ОПРЕДЕЛЕНО" category separately if present

### Requirement 4: Динамическая аналитика по колонкам

**User Story:** As a проектный менеджер, I want видеть статистику по любой колонке из файла, so that я мог анализировать данные в разных разрезах.

#### Acceptance Criteria

1. THE Dashboard SHALL auto-detect all columns from uploaded file
2. THE Dashboard SHALL provide dropdown to select column for grouping
3. WHEN column is selected, THE Dashboard SHALL display bar chart with value distribution
4. THE Dashboard SHALL handle text, numeric and date columns appropriately

### Requirement 5: Таблица с данными

**User Story:** As a проектный менеджер, I want видеть детальные данные в таблице, so that я мог просмотреть конкретные записи.

#### Acceptance Criteria

1. THE Dashboard SHALL display paginated data table with all rows
2. THE Dashboard SHALL show defect text and assigned category in table
3. THE Dashboard SHALL support sorting by any column
4. THE Dashboard SHALL support text search across all columns

### Requirement 6: Интерактивные фильтры

**User Story:** As a проектный менеджер, I want фильтровать данные, so that я мог анализировать конкретные срезы.

#### Acceptance Criteria

1. THE Dashboard SHALL provide filter by defect category (multi-select)
2. THE Dashboard SHALL provide filter by any detected column values
3. WHEN filters are applied, THE Dashboard SHALL update all charts in real-time
4. THE Dashboard SHALL show active filter count

### Requirement 7: Экспорт результатов

**User Story:** As a проектный менеджер, I want скачать обработанный файл, so that я мог использовать данные в других системах.

#### Acceptance Criteria

1. THE Dashboard SHALL provide button to download processed Excel file
2. THE Download_Button SHALL be prominently displayed
3. THE Filename SHALL include original name and "_classified" suffix

### Requirement 8: API для аналитики

**User Story:** As a система, I want API endpoint для получения аналитики, so that фронтенд мог отображать данные.

#### Acceptance Criteria

1. WHEN job is completed, THE API SHALL provide GET /jobs/{job_id}/analytics endpoint
2. THE API SHALL return JSON with category distribution statistics
3. THE API SHALL return JSON with column names from original file
4. THE API SHALL return JSON with value distribution for any requested column
5. THE API SHALL return paginated raw data for table view
