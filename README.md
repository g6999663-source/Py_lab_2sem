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
