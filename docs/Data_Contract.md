# Data Contract: Open‑Meteo Archive API → ETL → Mart → DQ (variant_04, London)

## Версия контракта

- **Версия:** 2.0
- **Дата последнего обновления:** 2026-05-31
- **Статус:** действует для всех слоёв (raw, normalized, mart, DQ)

---

## 1. Источник данных

| Свойство       | Значение                                      |
|----------------|-----------------------------------------------|
| **API**        | Open‑Meteo Historical Weather Archive         |
| **Endpoint**   | `https://archive-api.open-meteo.com/v1/archive` |
| **Метод**      | GET                                           |
| **Аутентификация** | не требуется                              |
| **Город**      | Лондон (Великобритания)                       |
| **Координаты** | широта 51.5072, долгота -0.1276               |
| **Часовой пояс** | Europe/London                              |

### Параметры запроса (из `configs/variant_04.yml`)

```yaml
latitude: 51.5072
longitude: -0.1276
hourly: [temperature_2m, relative_humidity_2m, precipitation, wind_speed_10m]
timezone: Europe/London
```

---

## 2. Raw JSON (непосредственно от API)

Пример структуры:

```json
{
  "hourly": {
    "time": ["2024-01-01T00:00", "2024-01-01T01:00", ...],
    "temperature_2m": [5.2, 4.8, ...],
    "relative_humidity_2m": [87, 85, ...],
    "precipitation": [0.0, 0.0, ...],
    "wind_speed_10m": [12.3, 11.7, ...]
  }
}
```

**Хранение:** `data/raw/variant_04/raw_YYYY-MM-DD.json`

---

## 3. Normalized dataset (почасовой слой)

- **Гранулярность:** 1 строка = 1 час наблюдения
- **Источник:** raw JSON → `src/transform/normalize.py`
- **Файл:** `data/normalized/variant_04/hourly_data.csv`

### Схема normalized

| поле                   | тип     | nullable | единица      | описание                          |
|------------------------|---------|----------|--------------|-----------------------------------|
| ts                     | datetime| no       | Europe/London| локальное время измерения         |
| temperature_2m         | float   | no       | °C           | температура на высоте 2 м         |
| relative_humidity_2m   | float   | no       | %            | относительная влажность           |
| precipitation          | float   | no       | мм           | осадки                            |
| wind_speed_10m         | float   | no       | км/ч         | скорость ветра на высоте 10 м     |
| city_id                | string  | no       | –            | GB_LON                            |

**Сортировка:** по `ts` (монотонно возрастает)

---

## 4. Mart dataset (суточная витрина)

- **Гранулярность:** 1 строка = 1 день × 1 город (Лондон)
- **Источник:** normalized CSV → `src/transform/build_mart.py`
- **Файл:** `data/mart/variant_04/daily_weather.csv`
- **Таблица PostgreSQL:** `daily_weather`

### Схема mart

| поле          | тип    | nullable | единица | описание                       |
|---------------|--------|----------|---------|--------------------------------|
| date          | date   | no       | –       | календарная дата               |
| avg_temp      | float  | no       | °C      | средняя температура за день    |
| min_temp      | float  | no       | °C      | минимальная температура за день|
| max_temp      | float  | no       | °C      | максимальная температура за день|
| avg_humidity  | float  | no       | %       | средняя относительная влажность|
| total_precip  | float  | no       | мм      | сумма осадков за день          |
| avg_windspeed | float  | no       | км/ч    | средняя скорость ветра за день |
| city_id       | string | no       | –       | GB_LON                         |

### Бизнес-ключ

`(date, city_id)` – уникальный идентификатор строки витрины.

### Логика расчёта

- `avg_temp` = среднее из `temperature_2m` за день
- `min_temp` = минимум из `temperature_2m`
- `max_temp` = максимум из `temperature_2m`
- `avg_humidity` = среднее из `relative_humidity_2m`
- `total_precip` = сумма `precipitation`
- `avg_windspeed` = среднее из `wind_speed_10m`

---

## 5. Data Quality правила (8 неделя)

| ID  | Правило                     | Слой   | Критичность | Детали                                      |
|-----|-----------------------------|--------|-------------|---------------------------------------------|
| DQ1 | Таблица не пустая           | mart   | FAIL        | Количество строк > 0                        |
| DQ2 | Нет NULL в бизнес-ключе     | mart   | FAIL        | `date` и `city_id` не NULL                  |
| DQ3 | Уникальность бизнес-ключа   | mart   | FAIL        | Нет дубликатов `(date, city_id)`            |
| DQ4 | Диапазон температур         | mart   | FAIL        | `min_temp`, `avg_temp`, `max_temp` ∈ [-80, 60] °C |
| DQ5 | Логика температур           | mart   | FAIL        | `min_temp` ≤ `avg_temp` ≤ `max_temp`        |
| DQ6 | Неотрицательные осадки      | mart   | WARNING     | `total_precip` ≥ 0                          |
| DQ7 | Диапазон влажности          | mart   | WARNING     | `avg_humidity` ∈ [0, 100]                   |
| DQ8 | Неотрицательная скорость ветра | mart | WARNING  | `avg_windspeed` ≥ 0                         |
| DQ9 | Сортировка дат              | mart   | WARNING     | Даты по возрастанию                         |
| DQ10| Нет будущих дат             | mart   | WARNING     | `date` ≤ сегодня                            |

**Отчёт:** `data/dq_report.json`

---

## 6. Идемпотентность и state

- **Watermark:** `last_date` в `data/state/state.json`
- **Полный режим (`--mode full`)** – пересоздаёт все слои, замена таблицы.
- **Инкрементальный режим (`--mode incremental`)** – загружает только новые дни, избегает дублей.

---

## 7. Визуализация (неделя 7)

Созданы три графика в `notebooks/week7_viz.ipynb`:

1. Временной ряд температуры
2. Распределение температур (гистограмма)
3. Топ дней по осадкам (bar chart)

**Артефакты:** `docs/figures/week7_*.png`

---

## 8. Unit-тесты (неделя 8)

- **Фреймворк:** pytest
- **Модуль тестов:** `tests/test_dq.py`
- **Покрытие:** все DQ-правила (позитивные, негативные, граничные кейсы)
- **Запуск:** `pytest tests/test_dq.py -v`

---

## Changelog

| Версия | Дата       | Изменения                                      |
|--------|------------|------------------------------------------------|
| 1.0    | 2026-05-20 | Начальная версия (API, raw, normalized, mart)  |
| 2.0    | 2026-05-31 | Добавлены DQ-правила, тестирование, визуализация, watermark |
