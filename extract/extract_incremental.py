import requests
import json
import os
from datetime import datetime, timedelta, date

def load_state(state_path="data/state/state.json"):
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    if os.path.exists(state_path) and os.path.getsize(state_path) > 0:
        with open(state_path, 'r') as f:
            return json.load(f)
    return {"last_date": None}

def save_state(state_path, last_date):
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with open(state_path, 'w') as f:
        json.dump({"last_date": last_date}, f)

def to_date_str(value):
    """Преобразует строку, date или datetime в строку YYYY-MM-DD"""
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d")
    return str(value)

def extract_incremental(config, mode="full", state_path="data/state/state.json"):
    base_url = config['api']['base_url']
    lat = config['entity']['latitude']
    lon = config['entity']['longitude']
    hourly_params = config['api']['params']['hourly']
    timezone = config['entity']['timezone']

    # Извлечение дат с защитой от типов
    if 'date_range' in config:
        start_date_raw = config['date_range']['start']
        end_date_raw = config['date_range']['end']
        start_date_str = to_date_str(start_date_raw)
        end_date_str = to_date_str(end_date_raw)
    else:
        start_date_str = "2024-01-01"
        end_date_str = "2024-01-07"
        print(f"⚠️ date_range not found, using defaults: {start_date_str} to {end_date_str}")

    state = load_state(state_path)

    if mode == "incremental" and state.get("last_date"):
        last_date_str = to_date_str(state["last_date"])
        start_date = datetime.strptime(last_date_str, "%Y-%m-%d") + timedelta(days=1)
        start_date = max(start_date, datetime.strptime(start_date_str, "%Y-%m-%d"))
    else:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    if start_date > end_date:
        print(f"No new data to extract. Last date: {state.get('last_date')}")
        return None

    current_date = start_date
    all_data = []

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": date_str,
            "end_date": date_str,
            "hourly": hourly_params,
            "timezone": timezone
        }

        print(f"Extracting data for {date_str}...")
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            raw_dir = "data/raw/variant_04"
            os.makedirs(raw_dir, exist_ok=True)
            with open(f"{raw_dir}/raw_{date_str}.json", 'w') as f:
                json.dump(data, f)
            all_data.append(data)
            save_state(state_path, date_str)
        else:
            print(f"Failed for {date_str}: {response.status_code}")

        current_date += timedelta(days=1)

    return all_data if all_data else None