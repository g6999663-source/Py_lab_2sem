
---

### 2. `Implementation_Plan.md` (недели 1–8)

```markdown
# Implementation Plan – проект ETL (variant_04, London)

## Общая цель
Построить воспроизводимый ETL-пайплайн:  
`API → raw JSON → normalized CSV → mart CSV → PostgreSQL`  
с поддержкой full/incremental загрузки, визуализацией, DQ-проверками и unit-тестами.

---

## Неделя 1 – Настройка окружения и структура
- [x] Установлен Anaconda, работает `base`
- [x] Создан `scripts/setup_env.bat` для установки pandas
- [x] Создан GitHub-репозиторий `python_labi`
- [x] Базовая структура: `data/raw|normalized|mart`, `configs/`, `src/`, `notebooks/`, `scripts/`, `tests/`

---

## Неделя 2 – HTTP и API (extract)
- [x] Написан `src/extract/extract.py` с фиксированным периодом
- [x] Добавлены `timeout`, обработка ошибок, логи
- [x] Конфигурация в `configs/variant_04.yml` (Лондон)
- [x] Raw JSON сохраняются в `data/raw/variant_04/raw_YYYY-MM-DD.json`

---

## Неделя 3 – Normalize (почасовой слой)
- [x] Ноутбук `notebooks/week3_eda.ipynb` читает raw JSON
- [x] Извлечён массив `hourly`, переименован `time` → `ts`
- [x] Добавлен `city_id = GB_LON`
- [x] Сохранение в `data/normalized/variant_04/hourly_data.csv`
- [x] Проверены типы, пропуски, дубли

---

## Неделя 4 – Mart (суточная витрина)
- [x] Ноутбук `notebooks/week4_mart.ipynb` читает normalized CSV
- [x] Добавлено поле `date` из `ts`
- [x] Агрегация по дням: средняя, мин, макс температура, сумма осадков, средняя влажность и ветер
- [x] Сохранение в `data/mart/variant_04/daily_weather.csv`

---

## Неделя 5 – Загрузка в PostgreSQL
- [x] Запущен Docker-контейнер `postgres_lab` (postgres:15-alpine)
- [x] Создана БД `mydb`, пользователь `postgres`, пароль `mysecretpassword`
- [x] Написан `src/load/load.py` для полной замены таблицы `daily_weather`
- [x] Загрузка mart в PostgreSQL, проверка через `sql_checks.md`

---

## Неделя 6 – ETL pipeline (full/incremental, state)
- [x] Создан `src/extract/extract_incremental.py` – поддержка `state.json`, извлечение по дням
- [x] Создан `src/transform/normalize.py` – нормализация нескольких raw JSON, защита от дублей
- [x] Создан `src/transform/build_mart.py` – полное перестроение витрины
- [x] Создан `src/load/load_incremental.py` – загрузка с режимами `replace` / `append`
- [x] Создан `src/pipeline/pipeline.py` – CLI с аргументом `--mode {full,incremental}`
- [x] Создан `scripts/pipeline.bat` – обёртка с установкой `PYTHONPATH`
- [x] Добавлен `data/state/state.json` для watermark (`last_date`)
- [x] Проверена идемпотентность

---

## Неделя 7 – Визуализация (matplotlib, data storytelling)
- [x] Создан ноутбук `notebooks/week7_viz.ipynb`
- [x] Загружен mart-файл, проверен тип `date`
- [x] Построены 3 графика:
  - временной ряд температуры (line plot)
  - распределение температур (гистограмма)
  - топ-5 дней по осадкам (bar chart)
- [x] Оформлены подписи осей, заголовки, единицы измерения
- [x] Сформулированы выводы (минимум 3)
- [x] Сохранены PNG в `docs/figures/`

---

## Неделя 8 – Data Quality и тестирование
- [x] Создан модуль `src/dq.py` с 10 проверками (6 FAIL, 4 WARNING)
- [x] Проверки: пустая таблица, NULL в ключе, дубли, диапазон температур, логика min≤avg≤max, осадки, влажность, ветер, сортировка, будущие даты
- [x] Результаты сохраняются в `data/dq_report.json`
- [x] Написаны unit-тесты в `tests/test_dq.py` (позитивные, негативные, граничные)
- [x] Тесты запускаются через pytest
- [x] Демонстрация срабатывания проверок на искусственно сломанных данных

---

## Текущий статус
**Завершены недели 1–8.**  
Пайплайн готов:  
`API → raw → normalized → mart → PostgreSQL → DQ → визуализация → тесты`

Дальнейшие недели (9–14) – по желанию (data governance, Docker Compose, Airflow, ML-аналитика).
