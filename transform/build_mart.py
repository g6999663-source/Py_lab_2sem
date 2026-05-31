import pandas as pd
import os

def build_daily_mart(normalized_csv_path="data/normalized/variant_04/hourly_data.csv",
                     output_dir="data/mart/variant_04"):
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(normalized_csv_path):
        print(f"Normalized file not found: {normalized_csv_path}")
        return None

    df = pd.read_csv(normalized_csv_path, parse_dates=['ts'])

    # Добавим столбец даты
    df['date'] = df['ts'].dt.date

    # Агрегация по дням (используем корректные имена колонок)
    daily = df.groupby('date').agg({
        'temperature_2m': ['mean', 'min', 'max'],
        'relative_humidity_2m': 'mean',
        'precipitation': 'sum',
        'wind_speed_10m': 'mean'
    }).round(2)

    daily.columns = ['avg_temp', 'min_temp', 'max_temp', 'avg_humidity', 'total_precip', 'avg_windspeed']
    daily = daily.reset_index()
    daily['date'] = pd.to_datetime(daily['date']).dt.strftime('%Y-%m-%d')

    # Добавим city_id (константа, можно взять из первой строки)
    if 'city_id' in df.columns:
        city_id = df['city_id'].iloc[0]
        daily['city_id'] = city_id

    mart_path = f"{output_dir}/daily_weather.csv"
    daily.to_csv(mart_path, index=False)
    print(f"Saved mart to {mart_path}")

    return daily