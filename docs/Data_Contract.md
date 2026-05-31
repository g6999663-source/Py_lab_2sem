# Data Contract: Open‑Meteo Archive API (variant_04 – London)

**Contract version:** 1.0  
**Last updated:** 2026-05-31  
**Status:** Active

---

## 1. Общая информация

| Параметр | Значение |
|----------|----------|
| Название проекта | python_labi |
| Вариант | 04 |
| Город | Лондон (London) |
| Источник данных | Open‑Meteo Historical Weather Archive |
| Endpoint | `https://archive-api.open-meteo.com/v1/archive` |
| Часовой пояс | Europe/London (GMT/BST) |
| Гранулярность normalized | 1 строка = 1 час |
| Гранулярность mart | 1 строка = 1 день × 1 город |

---

## 2. Источник данных (API)

**Параметры запроса:**
| Параметр | Значение | Описание |
|----------|----------|----------|
| latitude | 51.5072 | Широта Лондона |
| longitude | -0.1276 | Долгота Лондона |
| timezone | Europe/London | Часовой пояс |
| hourly | temperature_2m, relative_humidity_2m, precipitation, wind_speed_10m | Почасовые метеопараметры |

**Ограничения источника:**
- Архивные данные доступны до 70 лет назад
- API-ключ не требуется
- Бесплатный лимит: ~10 000 запросов в день

---

## 3. Схема normalized (почасовой слой)

**Файл:** `data/normalized/variant_04/hourly_data.csv`

| Колонка | Тип | Nullable | Единица | Описание |
|---------|-----|----------|---------|----------|
| ts | timestamp | NO | Europe/London | Локальное время измерения |
| temperature_2m | float | NO | °C | Температура воздуха на высоте 2 м |
| relative_humidity_2m | float | NO | % | Относительная влажность |
| precipitation | float | NO | мм | Количество осадков |
| wind_speed_10m | float | NO | км/ч | Скорость ветра на высоте 10 м |
| city_id | string | NO | - | Идентификатор города (GB_LON) |

**Источник:** raw JSON → `src/transform/normalize.py`

---

## 4. Схема mart (суточная витрина)

**Файл:** `data/mart/variant_04/daily_weather.csv`  
**Таблица в PostgreSQL:** `daily_weather`

| Колонка | Тип | Nullable | Единица | Описание |
|---------|-----|----------|---------|----------|
| date | date | NO | - | Календарная дата (UTC) |
| avg_temp | float | NO | °C | Средняя температура за день |
| min_temp | float | NO | °C | Минимальная температура за день |
| max_temp | float | NO | °C | Максимальная температура за день |
| avg_humidity | float | NO | % | Средняя влажность за день |
| total_precip | float | NO | мм | Сумма осадков за день |
| avg_windspeed | float | NO | км/ч | Средняя скорость ветра за день |
| city_id | string | NO | - | Идентификатор города (GB_LON) |

**Бизнес-ключ:** `date + city_id`

---

## 5. Логика расчёта KPI

| KPI | Формула | Источник |
|-----|---------|----------|
| avg_temp | AVG(temperature_2m) | normalized.temperature_2m |
| min_temp | MIN(temperature_2m) | normalized.temperature_2m |
| max_temp | MAX(temperature_2m) | normalized.temperature_2m |
| avg_humidity | AVG(relative_humidity_2m) | normalized.relative_humidity_2m |
| total_precip | SUM(precipitation) | normalized.precipitation |
| avg_windspeed | AVG(wind_speed_10m) | normalized.wind_speed_10m |

---

## 6. Правила именования (Naming Conventions)

| Правило | Пример |
|---------|--------|
| snake_case для всех колонок | `avg_temp`, `city_id` |
| *_id для идентификаторов | `city_id` |
| date для календарных дат | `date` |
| ts для временных меток | `ts` |
| Префиксы агрегаций: avg_, min_, max_, sum_, cnt_ | `avg_temp`, `total_precip` |
| Запрещены: value, metric1, data1 | - |
| Без кириллицы и пробелов | - |

---

## 7. Единицы измерения (Units)

| Величина | Единица | Обозначение |
|----------|---------|-------------|
| Температура | Градус Цельсия | °C |
| Влажность | Процент | % |
| Осадки | Миллиметр | мм |
| Скорость ветра | Километр в час | км/ч |
| Координаты | Градусы | degrees |

---

## 8. Ограничения качества (Constraints)

| Ограничение | Слой | Описание |
|-------------|------|----------|
| ts NOT NULL | normalized | Время не может быть пустым |
| city_id NOT NULL | normalized, mart | Город всегда указан |
| temperature_2m ∈ [-80, 60] | normalized | Физический диапазон температур |
| relative_humidity_2m ∈ [0, 100] | normalized | Влажность не может выходить за пределы |
| precipitation ≥ 0 | normalized | Осадки не могут быть отрицательными |
| Нет дубликатов по (city_id, ts) | normalized | Уникальность почасовых записей |
| Нет дубликатов по (date, city_id) | mart | Уникальность дневных записей |
| min_temp ≤ avg_temp ≤ max_temp | mart | Логическая согласованность температур |

---

## 9. Версионирование и Changelog

### Changelog

| Версия | Дата | Изменение | Причина |
|--------|------|-----------|---------|
| 0.1 | 2026-04-29 | Начальная версия контракта | Создание базовой документации |
| 0.2 | 2026-05-11 | Добавлен BI/PostgreSQL слой | Интеграция с Metabase |
| 0.3 | 2026-05-18 | Добавлен Airflow DAG | Оркестрация пайплайна |
| 0.4 | 2026-05-24 | Переход на инкрементальный режим | Quality Gate до загрузки |
| 0.5 | 2026-05-28 | Добавлен ML/аналитический слой | Поиск аномалий |
| 1.0 | 2026-05-31 | Полная версия контракта | Завершение недели 9 |

---

## 10. Контактная информация

| Роль | Ответственный |
|------|---------------|
| Производитель данных | Студент (variant_04) |
| Потребители | Аналитики, BI, ML-модели |
