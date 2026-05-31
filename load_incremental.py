from sqlalchemy import create_engine, text
import pandas as pd
import os

def load_to_postgres(csv_path, table_name, mode="full",
                     connection_string="postgresql://postgres:mysecretpassword@localhost:5432/mydb"):
    engine = create_engine(connection_string)

    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    if mode == "full":
        print(f"Full load: replacing table {table_name}")
        df.to_sql(table_name, engine, if_exists='replace', index=False)
    else:  # incremental
        print(f"Incremental load: appending to table {table_name}")
        with engine.connect() as conn:
            existing_dates = pd.read_sql(f"SELECT date FROM {table_name}", conn)
            if not existing_dates.empty:
                df = df[~df['date'].isin(existing_dates['date'])]

        if not df.empty:
            df.to_sql(table_name, engine, if_exists='append', index=False)
            print(f"Added {len(df)} new rows")
        else:
            print("No new rows to add")

    # Проверка
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        print(f"Table {table_name} now has {count} rows")