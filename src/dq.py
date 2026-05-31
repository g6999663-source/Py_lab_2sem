"""
Data Quality модуль для проверки качества данных (variant_04, London)
Проверяет mart-слой (daily_weather.csv)
"""

import pandas as pd
import json
import os
from datetime import datetime

# Конфигурация проверок
# FAIL - критично, WARNING - некритично
CHECKS_CONFIG = {
    "table_not_empty": {"type": "FAIL", "description": "Таблица не должна быть пустой"},
    "no_null_in_key": {"type": "FAIL", "description": "Нет NULL в бизнес-ключе (date, city_id)"},
    "unique_business_key": {"type": "FAIL", "description": "Бизнес-ключ (date + city_id) уникален"},
    "temperature_range": {"type": "FAIL", "description": "Температура в диапазоне [-80, +60] °C"},
    "non_negative_precipitation": {"type": "WARNING", "description": "Осадки неотрицательны"},
    "humidity_range": {"type": "WARNING", "description": "Влажность в диапазоне [0, 100] %"},
    "wind_speed_non_negative": {"type": "WARNING", "description": "Скорость ветра неотрицательна"},
    "date_order": {"type": "WARNING", "description": "Даты отсортированы по возрастанию"},
    "no_future_dates": {"type": "WARNING", "description": "Нет дат в будущем"},
    "temp_min_max_logic": {"type": "FAIL", "description": "min_temp <= avg_temp <= max_temp"}
}

def load_mart(mart_path="data/mart/variant_04/daily_weather.csv"):
    """Загружает mart-файл и преобразует дату"""
    if not os.path.exists(mart_path):
        return None
    df = pd.read_csv(mart_path)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df

def check_table_not_empty(df):
    """Проверка 1: таблица не пустая"""
    name = "table_not_empty"
    if df is None or len(df) == 0:
        return name, "FAIL", "Таблица пуста или файл не найден"
    return name, "PASS", f"В таблице {len(df)} строк"

def check_no_null_in_key(df):
    """Проверка 2: нет NULL в бизнес-ключе (date, city_id)"""
    name = "no_null_in_key"
    null_date = df['date'].isna().sum()
    null_city = df['city_id'].isna().sum()
    if null_date > 0 or null_city > 0:
        return name, "FAIL", f"NULL в date: {null_date}, NULL в city_id: {null_city}"
    return name, "PASS", "NULL в ключевых полях отсутствуют"

def check_unique_business_key(df):
    """Проверка 3: бизнес-ключ (date + city_id) уникален"""
    name = "unique_business_key"
    duplicates = df.duplicated(subset=['date', 'city_id']).sum()
    if duplicates > 0:
        return name, "FAIL", f"Найдено {duplicates} дубликатов по ключу (date, city_id)"
    return name, "PASS", "Бизнес-ключ уникален"

def check_temperature_range(df):
    """Проверка 4: температура в разумных пределах [-80, +60]"""
    name = "temperature_range"
    violations = 0
    for col in ['avg_temp', 'min_temp', 'max_temp']:
        if col in df.columns:
            out_of_range = ((df[col] < -80) | (df[col] > 60)).sum()
            violations += out_of_range
    if violations > 0:
        return name, "FAIL", f"Найдено {violations} записей с температурой вне диапазона [-80, 60]"
    return name, "PASS", "Все температуры в допустимом диапазоне"

def check_non_negative_precipitation(df):
    """Проверка 5: осадки неотрицательны"""
    name = "non_negative_precipitation"
    if 'total_precip' not in df.columns:
        return name, "WARNING", "Колонка total_precip отсутствует"
    negative = (df['total_precip'] < 0).sum()
    if negative > 0:
        return name, "WARNING", f"Найдено {negative} записей с отрицательными осадками"
    return name, "PASS", "Все значения осадков неотрицательны"

def check_humidity_range(df):
    """Проверка 6: влажность в пределах [0, 100]"""
    name = "humidity_range"
    if 'avg_humidity' not in df.columns:
        return name, "WARNING", "Колонка avg_humidity отсутствует"
    out_of_range = ((df['avg_humidity'] < 0) | (df['avg_humidity'] > 100)).sum()
    if out_of_range > 0:
        return name, "WARNING", f"Найдено {out_of_range} записей с влажностью вне [0, 100]"
    return name, "PASS", "Влажность в допустимом диапазоне"

def check_wind_speed_non_negative(df):
    """Проверка 7: скорость ветра неотрицательна"""
    name = "wind_speed_non_negative"
    if 'avg_windspeed' not in df.columns:
        return name, "WARNING", "Колонка avg_windspeed отсутствует"
    negative = (df['avg_windspeed'] < 0).sum()
    if negative > 0:
        return name, "WARNING", f"Найдено {negative} записей с отрицательной скоростью ветра"
    return name, "PASS", "Скорость ветра неотрицательна"

def check_date_order(df):
    """Проверка 8: даты отсортированы по возрастанию"""
    name = "date_order"
    if not df['date'].is_monotonic_increasing:
        return name, "WARNING", "Даты не отсортированы по возрастанию"
    return name, "PASS", "Даты отсортированы корректно"

def check_no_future_dates(df):
    """Проверка 9: нет дат в будущем"""
    name = "no_future_dates"
    today = datetime.now().date()
    future = (df['date'].dt.date > today).sum()
    if future > 0:
        return name, "WARNING", f"Найдено {future} дат в будущем"
    return name, "PASS", "Дат в будущем нет"

def check_temp_min_max_logic(df):
    """Проверка 10: min_temp <= avg_temp <= max_temp"""
    name = "temp_min_max_logic"
    violations = ((df['min_temp'] > df['avg_temp']) | (df['avg_temp'] > df['max_temp'])).sum()
    if violations > 0:
        return name, "FAIL", f"Найдено {violations} записей с нарушением min <= avg <= max"
    return name, "PASS", "Логика температур корректна"

def run_all_checks(df):
    """Запускает все проверки и возвращает список результатов"""
    checks = [
        check_table_not_empty,
        check_no_null_in_key,
        check_unique_business_key,
        check_temperature_range,
        check_non_negative_precipitation,
        check_humidity_range,
        check_wind_speed_non_negative,
        check_date_order,
        check_no_future_dates,
        check_temp_min_max_logic
    ]

    results = []
    for check in checks:
        result = check(df)
        results.append({
            "check": result[0],
            "status": result[1],
            "message": result[2],
            "description": CHECKS_CONFIG.get(result[0], {}).get("description", "")
        })
    return results

def generate_report(results, output_path="data/dq_report.json"):
    """Сохраняет отчёт в JSON и печатает в консоль"""
    # Подсчёт статусов
    status_counts = {"PASS": 0, "FAIL": 0, "WARNING": 0}
    for r in results:
        status_counts[r["status"]] += 1

    report = {
        "timestamp": datetime.now().isoformat(),
        "layer": "mart",
        "variant": "04",
        "dataset": "daily_weather.csv",
        "summary": status_counts,
        "results": results
    }

    # Сохраняем JSON
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Печатаем в консоль
    print("\n" + "="*60)
    print("DATA QUALITY REPORT - variant_04 (London)")
    print("="*60)
    print(f"Timestamp: {report['timestamp']}")
    print(f"Dataset: {report['dataset']}")
    print(f"Summary: PASS={status_counts['PASS']}, FAIL={status_counts['FAIL']}, WARNING={status_counts['WARNING']}")
    print("-"*60)
    for r in results:
        status_icon = "✅" if r["status"] == "PASS" else ("❌" if r["status"] == "FAIL" else "⚠️")
        print(f"{status_icon} [{r['status']}] {r['check']}: {r['message']}")
    print("="*60)

    # Возвращаем статус: есть ли FAIL
    has_fail = status_counts["FAIL"] > 0
    return has_fail

def main():
    """Основная функция"""
    print("Loading mart data...")
    df = load_mart()

    if df is None:
        print("ERROR: Mart file not found or empty!")
        return 1

    print(f"Loaded {len(df)} rows from daily_weather.csv")

    results = run_all_checks(df)
    has_fail = generate_report(results)

    if has_fail:
        print("\n❌ DQ FAILED: Критические ошибки обнаружены!")
        return 1
    else:
        print("\n✅ DQ PASSED: Все критические проверки пройдены")
        return 0

if __name__ == "__main__":
    exit(main())