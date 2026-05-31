## 1 Неделя
## Описание:
Учебный проект по курсу анализа данных. Настройка окружения и базовая структура репозитория.
## Результат проверки:
```bash
python: D:\anaconda\anaconda3\python.exe
pandas: 2.3.3
```
### Проверка пройдена успешно
```
## Быстрый старт:
##  Инструкция для Windows

### 1. Запуск скрипта настройки окружения

Скрипт `setup_env.bat` автоматически установит все зависимости и проверит работоспособность.

**Способ 1 (рекомендуемый):**
1. Откройте папку проекта `python_labi`
2. Перейдите в папку `scripts`
3. Дважды кликните по файлу `setup_env.bat`

**Способ 2 (через командную строку):**
```cmd
cd C:\Users\пользователь\Desktop\python_labi\scripts
setup_env.bat
```
### 2. Выполнение smoke test
```
cd C:\Users\пользователь\Desktop\python_labi
python broken_env.py
```
Ожидаемый вывод:
```
python: D:\anaconda\anaconda3\python.exe
pandas: 2.3.3
```
### 3. Быстрый запуск
При запуске setup_env.bat smoke test выполняется автоматически. Успешное выполнение завершается сообщением [OK].

## Week 2 — API Extract (variant_04)

### Вариант 1
conda run -n my_ml_env python src/extract/extract.py

### Вариант 2
python src/extract/extract.py (если активирована среда)

---

### Ожидаемый результат

Variant: 4 - Погода (архив) - Лондон

URL: https://archive-api.open-meteo.com/v1/archive

Params: {'latitude': 51.5072, 'longitude': -0.1276, 'timezone': 'Europe/London', 'start_date': '2024-01-01', 'end_date': '2024-01-07', 'hourly': ['temperature_2m', 'relative_humidity_2m', 'precipitation', 'wind_speed_10m']}

Status: 200

Saved: data/raw/variant_04/2024-01-01_2024-01-07_2026-05-28_14-30-00.json

---

### Файлы создаются

data/raw/variant_04/YYYY-MM-DD_HH-MM-SS.json  ← raw API ответ  
docs/Data_Contract.md                         ← документация API  
docs/Implementation_Plan.md                   ← план реализации  
docs/LLM_Usage_Log.md                         ← лог использования LLM  

---

### Требования
- Windows 10/11
- Anaconda/Miniconda
## Week 3 — Data Normalization (Pandas)

### Что сделано
- raw JSON преобразован в DataFrame
- определено зерно: 1 строка = 1 час наблюдения
- выполнена базовая очистка данных

### Очистка
- `timestamp` → `datetime`
- числовые колонки → `float64`
- проверка и заполнение пропусков (осадки)
- удаление дубликатов
- переименование колонок для удобства
- добавлены служебные поля: `city`, `variant_id`

### Результат
Данные сохранены в: `data/normalized/variant_04/*.csv`

Параметр: `index=False`

### Data Contract
Добавлена схема normalized‑слоя:

| Поле | Тип | Nullable | Описание |
|------|-----|----------|-----------|
| datetime_utc | datetime64[ns] | No | Временная метка (UTC) |
| temp_c | float64 | No | Температура на 2 м, °C |
| rel_humidity_percent | float64 | No | Относительная влажность, % |
| precip_mm | float64 | No | Осадки, мм |
| wind_kmh | float64 | No | Скорость ветра на 10 м, км/ч |
| city | object | No | Город (London) |
| variant_id | object | No | Идентификатор варианта (04) |

### Итог
Собран pipeline: raw JSON → DataFrame → очистка → CSV
## Week 4 — Mart (Группировки и агрегаты)

### Что сделано
- normalized-данные (почасовые) агрегированы в дневную витрину  
- добавлен `city_id = 'GB_LON'` (из конфига variant_04.yml)  
- использован справочник `configs/cities.csv` (содержит city_id, city_name, country_code)  
- выполнен `LEFT JOIN` по `city_id`  
- проверено отсутствие many‑to‑many (число строк не изменилось)  
- рассчитаны KPI согласно варианту

### Гранулярность
Одна строка = один день (для Лондона)

### KPI витрины
- `avg_temp_c` – средняя температура за день, °C  
- `max_temp_c` – максимальная температура за день, °C  
- `total_precip_mm` – сумма осадков за день, мм  
- `rainy_hours` – количество часов с осадками > 0  
- `max_wind_kmh` – максимальная скорость ветра за день, км/ч  

*(дополнительно: топ‑5 дней по ветру – как пример использования витрины)*

### Результат
Витрина сохраняется в: `data/mart/variant_04/mart_daily_YYYY-MM-DD_HH-MM-SS.csv`

### Итог
Собран полный pipeline:  
`raw JSON (Open‑Meteo Archive)` → `normalized CSV (почасовой)` → `mart CSV (суточный)`

### Схема витрины (mart)

| Поле | Тип | Описание |
|------|-----|-----------|
| date | object (date) | Дата (UTC) |
| avg_temp_c | float64 | Средняя температура за день, °C |
| max_temp_c | float64 | Максимальная температура за день, °C |
| total_precip_mm | float64 | Сумма осадков, мм |
| rainy_hours | int64 | Количество часов с осадками > 0 |
| max_wind_kmh | float64 | Максимальная скорость ветра, км/ч |
| city_id | object | Код города (GB_LON) |
| city_name | object | Название города (Лондон) |
| country_code | object | Код страны (GB) |
## Week 5 — PostgreSQL (Загрузка и SQL-проверки)

### Что происходит
1. Чтение mart CSV.
2. Проверка структуры DataFrame: `shape`, `columns`, `dtypes`.
3. Подключение к базе PostgreSQL.
4. Загрузка данных в таблицу `mart_variant_04_daily`.

### Идемпотентность
Повторный запуск не создаёт дубли: таблица пересоздаётся при каждой загрузке с помощью:

```sql
DROP TABLE IF EXISTS ...
```

и

```python
to_sql(..., if_exists='replace')
```

### SQL-проверки
Проверки описаны в: `docs/sql_checks.md`

Выполнены проверки:
- таблица не пустая (`COUNT`);
- диапазон дат (`MIN/MAX`) — ожидается `2024-01-01 … 2024-01-07`;
- `NULL` в ключевых колонках: `date`, `city_id`, `avg_temp_c`;
- дубли по `(date, city_id)`;
- нет отрицательных осадков (`total_precip_mm >= 0`).

### Что сделано
1. Mart-данные (суточная витрина по Лондону) загружены в PostgreSQL.
2. Реализован скрипт загрузки: `src/load/load.py`.
3. Использована транзакция через `engine.begin()` (автоматический commit).
4. Обеспечена идемпотентность загрузки: таблица пересоздаётся при каждом запуске.
5. Выполнены SQL-проверки качества данных.

### Подключение
- **host:** `localhost`
- **port:** `5432`
- **database:** `mydb`
- **user:** `myuser`
- **password:** `mysecretpassword`

### Загрузка
**Запуск:**
```bash
python src/load/load.py
```

### Результат
Данные загружены в PostgreSQL, таблица: `mart_variant_04_daily`.
SQL-запросы успешно выполняются, данные прошли базовые проверки качества.
# Week 6 — ETL Pipeline (variant_04, London)

## Что сделано

- Объединены все этапы в единый pipeline (`src/pipeline/pipeline.py`)
- Реализована единая команда запуска (`scripts/pipeline.bat`)
- Добавлены режимы:
  - `full`
  - `incremental`
- Устранён хардкод путей во всех слоях
- Реализовано автоматическое связывание слоёв (raw → normalized → mart)
- Добавлен `data/state/state.json` для хранения состояния пайплайна
- Реализован watermark (по максимальной дате `last_date`)
- Обеспечена идемпотентность пайплайна

## Запуск pipeline

Из корня проекта:

```batch
scripts\pipeline.bat --mode full
scripts\pipeline.bat --mode incremental
```

Или напрямую:

```bash
python src/pipeline/pipeline.py --mode full
python src/pipeline/pipeline.py --mode incremental
```

## Что происходит

Pipeline выполняет следующие шаги:

### 1. Extract (`extract_incremental.py`)

- Получение данных из Open‑Meteo Archive API (Лондон, координаты из `configs/variant_04.yml`)
- При `full` – загрузка всех дат из `date_range` (2024-01-01 … 2024-01-07)
- При `incremental` – загрузка только новых дней, начиная с `state.last_date + 1`
- Сохранение в `data/raw/variant_04/raw_YYYY-MM-DD.json`

### 2. Transform – Normalize (`normalize.py`)

- Читает все загруженные raw JSON
- Преобразует `time` → `ts`, добавляет `city_id = GB_LON`
- Сохраняет в `data/normalized/variant_04/hourly_data.csv`
- При инкременте – дозаписывает новые строки, удаляя дубли по `(ts, city_id)`

### 3. Transform – Mart (`build_mart.py`)

- Читает полный `hourly_data.csv`
- Агрегирует по дням:
  - средняя / мин / макс температура
  - сумма осадков
  - средняя влажность и скорость ветра
- Сохраняет в `data/mart/variant_04/daily_weather.csv` (всегда перезаписывает)

### 4. Load (`load_incremental.py`)

- Загружает `daily_weather.csv` в PostgreSQL (таблица `daily_weather`)
- `full` → полная замена таблицы (`if_exists='replace'`)
- `incremental` → добавление только тех строк, чьи даты ещё не присутствуют в таблице

## State пайплайна

**Файл**: `data/state/state.json`

**Пример содержимого**:

```json
{"last_date": "2024-01-14"}
```

**Поля**:

- `last_date` – максимальная дата, успешно извлечённая из API (watermark)

**Обновление**: после каждого успешного извлечения дня.

## Watermark

- Используется поле: `date` (в mart и state)
- Определяется как максимальная дата среди загруженных дней
- При `incremental` стартовая дата = `watermark + 1`
- Пример: `watermark = 2024-01-14`

## Business key

- Одна строка витрины = один день по одному городу
- Business key: `date` + `city_id` (GB_LON)

## Идемпотентность

- Повторный запуск `--mode full` полностью пересоздаёт все слои и таблицу → результат одинаков
- Повторный запуск `--mode incremental` без новых данных ничего не меняет (сообщение `No new data`)
- При `incremental` с новыми данными старые строки не дублируются:
  - в нормализованном CSV удаляются дубли по `(ts, city_id)`
  - перед загрузкой в PostgreSQL отфильтровываются уже существующие даты

## Режимы работы

### Full

- Извлекаются все даты из `date_range` (начало → конец)
- Нормализованный CSV создаётся заново (если файл существует – перезаписывается)
- Витрина полностью пересобирается
- Таблица в БД заменяется (`replace`)

### Incremental

- Используется `state.json` для определения последней загруженной даты
- Извлекаются только дни от `last_date + 1` до `date_range.end`
- Нормализованный CSV дополняется новыми строками (без дублей)
- Витрина перестраивается полностью (на основе всех накопленных данных)
- В БД добавляются только те даты, которых ещё нет в таблице

## Итог

Собран полноценный ETL pipeline:

```text
API → raw JSON → normalized CSV → mart CSV → PostgreSQL (daily_weather)
```

**Свойства**:

- единая точка входа
- повторяемость
- идемпотентность
- поддержка incremental
- хранение состояния (state + watermark)
