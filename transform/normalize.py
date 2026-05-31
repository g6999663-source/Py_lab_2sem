import pandas as pd
import os

def normalize_raw_to_csv(raw_data_list, city_id, output_dir="data/normalized/variant_04"):
    os.makedirs(output_dir, exist_ok=True)
    all_hourly = []

    for data in raw_data_list:
        if not data or 'hourly' not in data:
            continue

        hourly = data['hourly']
        df = pd.DataFrame(hourly)
        # Переименовываем time -> ts в соответствии со схемой
        df.rename(columns={'time': 'ts'}, inplace=True)
        df['ts'] = pd.to_datetime(df['ts'])
        df['city_id'] = city_id

        # Извлекаем метаданные (необязательно)
        if 'latitude' in data:
            df['latitude'] = data['latitude']
            df['longitude'] = data['longitude']

        all_hourly.append(df)

    if not all_hourly:
        print("No data to normalize")
        return None

    final_df = pd.concat(all_hourly, ignore_index=True)
    csv_path = f"{output_dir}/hourly_data.csv"

    # Append mode для инкрементальной загрузки
    if os.path.exists(csv_path):
        existing = pd.read_csv(csv_path, parse_dates=['ts'])
        final_df = pd.concat([existing, final_df], ignore_index=True)
        final_df = final_df.drop_duplicates(subset=['ts', 'city_id'])

    final_df.to_csv(csv_path, index=False)
    print(f"Saved normalized data to {csv_path}")
    return final_df

def normalize_raw_to_csv(raw_data_list, city_id, output_dir="data/normalized/variant_04"):
    os.makedirs(output_dir, exist_ok=True)
    all_hourly = []

    for data in raw_data_list:
        if not data or 'hourly' not in data:
            continue

        hourly = data['hourly']
        df = pd.DataFrame(hourly)
        # Переименовываем time -> ts в соответствии со схемой
        df.rename(columns={'time': 'ts'}, inplace=True)
        df['ts'] = pd.to_datetime(df['ts'])
        df['city_id'] = city_id

        # Извлекаем метаданные (необязательно)
        if 'latitude' in data:
            df['latitude'] = data['latitude']
            df['longitude'] = data['longitude']

        all_hourly.append(df)

    if not all_hourly:
        print("No data to normalize")
        return None

    final_df = pd.concat(all_hourly, ignore_index=True)
    csv_path = f"{output_dir}/hourly_data.csv"

    # Append mode для инкрементальной загрузки
    if os.path.exists(csv_path):
        existing = pd.read_csv(csv_path, parse_dates=['ts'])
        final_df = pd.concat([existing, final_df], ignore_index=True)
        final_df = final_df.drop_duplicates(subset=['ts', 'city_id'])

    final_df.to_csv(csv_path, index=False)
    print(f"Saved normalized data to {csv_path}")
    return final_df