# Implementation Plan – проект ETL (variant_04, London)

## Общая цель
Построить воспроизводимый ETL-пайплайн:  
`API → raw JSON → normalized CSV → mart CSV → PostgreSQL`  
с поддержкой full/incremental загрузки, визуализацией, DQ-проверками и unit-тестами.

---

## Неделя 1 – Настройка окружения и структура

### Выполненные задачи
1. Установлен **Anaconda**, работает окружение `base`.
2. Создан скрипт `scripts/setup_env.bat` для установки **pandas**.
3. Создан GitHub-репозиторий `python_labi`.
4. Создана базовая структура проекта:
   - `data/raw`, `data/normalized`, `data/mart`
   - `configs/`
   - `src/`
   - `notebooks/`
   - `scripts/`
   - `tests/`

### Артефакты
- `scripts/setup_env.bat`
- GitHub-репозиторий `python_labi`

> **Статус**: неделя 1 завершена. Окружение и структура готовы.

---

## Неделя 2 – HTTP и API (extract)

### Выполненные задачи
1. Написан модуль `src/extract/extract.py` с фиксированным периодом извлечения.
2. Добавлены:
   - `timeout` для запросов
   - обработка ошибок
   - логирование
3. Создан конфиг `configs/variant_04.yml` (город **Лондон**).
4. Raw JSON сохраняются в `data/raw/variant_04/raw_YYYY-MM-DD.json`.

### Артефакты
- `src/extract/extract.py`
- `configs/variant_04.yml`
- Файлы `data/raw/variant_04/raw_YYYY-MM-DD.json`

> **Статус**: неделя 2 завершена. Экспорт из API работает.

---

## Неделя 3 – Normalize (почасовой слой)

### Выполненные задачи
1. Создан ноутбук `notebooks/week3_eda.ipynb`, читающий raw JSON.
2. Извлечён массив `hourly`, переименовано поле `time` → `ts`.
3. Добавлено поле `city_id = GB_LON`.
4. Сохранение нормализованных данных в `data/normalized/variant_04/hourly_data.csv`.
5. Проверены:
   - типы данных
   - пропуски
   - дубликаты

### Артефакты
- `notebooks/week3_eda.ipynb`
- `data/normalized/variant_04/hourly_data.csv`

> **Статус**: неделя 3 завершена. Нормализованный почасовой слой готов.

---

## Неделя 4 – Mart (суточная витрина)

### Выполненные задачи
1. Создан ноутбук `notebooks/week4_mart.ipynb`, читающий normalized CSV.
2. Добавлено поле `date` из `ts`.
3. Выполнена агрегация по дням:
   - средняя температура (`avg_temp`)
   - минимальная температура (`min_temp`)
   - максимальная температура (`max_temp`)
   - сумма осадков (`total_precip`)
   - средняя влажность (`avg_humidity`)
   - средняя скорость ветра (`avg_windspeed`)
4. Сохранение витрины в `data/mart/variant_04/daily_weather.csv`.

### Артефакты
- `notebooks/week4_mart.ipynb`
- `data/mart/variant_04/daily_weather.csv`

> **Статус**: неделя 4 завершена. Суточная витрина `daily_weather` готова.

---

## Неделя 5 – Загрузка в PostgreSQL

### Выполненные задачи
1. Запущен Docker-контейнер `postgres_lab` (образ `postgres:15-alpine`).
2. Создана база данных `mydb`, пользователь `postgres`, пароль `mysecretpassword`.
3. Написан модуль `src/load/load.py` для полной замены таблицы `daily_weather`.
4. Выполнена загрузка mart-данных в PostgreSQL.
5. Проведена проверка через `sql_checks.md`.

### Артефакты
- `src/load/load.py`
- `sql_checks.md`
- Таблица `daily_weather` в БД `mydb`

> **Статус**: неделя 5 завершена. Данные загружены в PostgreSQL.

---

## Неделя 6 – ETL pipeline (full/incremental, state)

### Выполненные задачи
1. Создан `src/extract/extract_incremental.py` – поддержка `state.json`, извлечение по дням.
2. Создан `src/transform/normalize.py` – нормализация нескольких raw JSON, защита от дублей.
3. Создан `src/transform/build_mart.py` – полное перестроение витрины.
4. Создан `src/load/load_incremental.py` – загрузка с режимами `replace` / `append`.
5. Создан `src/pipeline/pipeline.py` – CLI с аргументом `--mode {full,incremental}`.
6. Создан `scripts/pipeline.bat` – обёртка с установкой `PYTHONPATH`.
7. Добавлен `data/state/state.json` для watermark (`last_date`).
8. Проверена **идемпотентность** пайплайна.

### Артефакты
- `src/extract/extract_incremental.py`
- `src/transform/normalize.py`
- `src/transform/build_mart.py`
- `src/load/load_incremental.py`
- `src/pipeline/pipeline.py`
- `scripts/pipeline.bat`
- `data/state/state.json`

> **Статус**: неделя 6 завершена. Пайплайн поддерживает full и incremental режимы.

---

## Неделя 7 – Визуализация (matplotlib, data storytelling)

### Выполненные задачи
1. Создан ноутбук `notebooks/week7_viz.ipynb`.
2. Загружен mart-файл, проверен тип поля `date`.
3. Построены 3 графика:
   - **временной ряд** температуры (line plot)
   - **распределение температур** (гистограмма)
   - **топ-5 дней по осадкам** (bar chart)
4. Оформлены:
   - подписи осей
   - заголовки
   - единицы измерения
5. Сформулированы **выводы** (минимум 3).
6. Сохранены PNG в `docs/figures/`.

### Артефакты
- `notebooks/week7_viz.ipynb`
- `docs/figures/` (PNG-файлы графиков)

> **Статус**: неделя 7 завершена. Визуализация и data storytelling готовы.

---

## Неделя 8 – Data Quality и тестирование

### Выполненные задачи
1. Создан модуль `src/dq.py` с **10 проверками** (6 FAIL, 4 WARNING).
2. Реализованы проверки:
   - пустая таблица
   - NULL в ключевом поле
   - дубликаты
   - диапазон температур
   - логика `min ≤ avg ≤ max`
   - осадки (неотрицательность)
   - влажность (0–100%)
   - ветер (неотрицательность)
   - сортировка по дате
   - отсутствие будущих дат
3. Результаты сохраняются в `data/dq_report.json`.
4. Написаны **unit-тесты** в `tests/test_dq.py`:
   - позитивные сценарии
   - негативные сценарии
   - граничные случаи
5. Тесты запускаются через **pytest**.
6. Демонстрировано срабатывание проверок на искусственно сломанных данных.

Пайплайн готов:  
`API → raw → normalized → mart → PostgreSQL → DQ → визуализация → тесты`

### Артефакты
- `src/dq.py`
- `data/dq_report.json`
- `tests/test_dq.py`

> **Статус**: неделя 8 завершена. Data Quality и тестирование реализованы.

---

## Неделя 9 – Data Governance (контракт и словарь данных)

### Выполненные задачи
1. Составлен **Data Contract** (`docs/Data_Contract.md`, версия 1.0):
   - Описаны все поля витрины `daily_weather`:  
     `date`, `avg_temp`, `min_temp`, `max_temp`, `avg_humidity`, `total_precip`, `avg_windspeed`, `city_id`.
   - Указаны единицы измерения (°C, %, мм, м/с), допустимые значения, nullable.
   - Прописаны правила валидации (`min ≤ avg ≤ max`, диапазоны температур).
   - Добавлен **changelog** с версионированием.
2. Создан **Data Dictionary** (`docs/data_dictionary.md`):
   - Подробное описание каждого поля с типами данных, примерами и бизнес-правилами.
   - Пояснения по источнику (Open-Meteo API, город Лондон).
3. Утверждены контракты и словарь для использования в ETL и проверках качества.

### Артефакты
- `docs/Data_Contract.md`
- `docs/data_dictionary.md`

### Связь с другими модулями
- Модуль `dq.py` (неделя 8) реализует проверки, описанные в контракте.
- Структура `daily_weather` в PostgreSQL соответствует контракту.

> **Статус**: неделя 9 завершена. Документы переданы команде и зафиксированы в репозитории.

---

## Неделя 10 – Визуализация в Metabase (Docker + BI)

### Выполненные задачи
1. Развёрнуты контейнеры **PostgreSQL** и **Metabase** через `docker-compose.yml`.
2. Данные за период **2024-01-01 … 2024-01-14** загружены в таблицу `daily_weather` (всего **14 строк**).
3. Metabase подключён к базе данных `mydb` с следующими параметрами:
   - `host = postgres`
   - `port = 5432`
   - `user = myuser`
   - `password = mysecretpassword`
4. Созданы три визуализации:
   - **Линейный график**: динамика средней температуры (`avg_temp` по датам).
   - **Столбчатая диаграмма**: топ-5 дней по сумме осадков (`total_precip`).
   - **Гистограмма**: распределение средней температуры (бинация по целым градусам).
5. Собран дашборд **Weather Analytics London (variant_04)**.

### Используемые команды

```bash
docker compose up -d          # запуск контейнеров
docker compose down           # остановка контейнеров
docker compose logs -f        # просмотр логов в реальном времени
```

### Тома (Volumes)

| Том            | Назначение                                      |
|----------------|-------------------------------------------------|
| `pgdata`       | Сохраняет данные PostgreSQL                     |
| `metabase_data`| Сохраняет настройки Metabase (дашборды, вопросы, подключения) |

### Скрины

- `docs/bi/dashboard_full.png` – общий вид дашборда  
- `docs/bi/line_chart_temp.png` – динамика температуры  
- `docs/bi/bar_chart_precip.png` – топ-5 дней по осадкам  
- `docs/bi/histogram_temp.png` – распределение температуры  
