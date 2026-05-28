# SQL-проверки качества данных (неделя 5)

## 1. Количество строк
```sql
SELECT COUNT(*) FROM mart_variant_04_daily;
```
Ожидается: 7 (или больше 0).
## 2. Диапазон дат
```sql
SELECT MIN(date), MAX(date) FROM mart_variant_04_daily;
```
Ожидается: 2024-01-01 – 2024-01-07.
## 3. NULL в ключевых колонках
```sql
SELECT 
    SUM(CASE WHEN date IS NULL THEN 1 ELSE 0 END) AS null_date,
    SUM(CASE WHEN city_id IS NULL THEN 1 ELSE 0 END) AS null_city,
    SUM(CASE WHEN avg_temp_c IS NULL THEN 1 ELSE 0 END) AS null_temp
FROM mart_variant_04_daily;
```
Ожидается: все нули.
## 4. дубликаты по (date,city_id)
```sql
SELECT date, city_id, COUNT(*) 
FROM mart_variant_04_daily 
GROUP BY date, city_id 
HAVING COUNT(*) > 1;
```
Ожидается: пустой результат.
## 5. Отрицательные значения осадков
```sql
SELECT * FROM mart_variant_04_daily WHERE total_precip_mm < 0;
```
Ожидается: 0 строк.

---

### 8. Выполнение SQL-проверок (через Python)

Добавьте блок проверок в конец `load.py` (перед финальным print) или создайте отдельный скрипт. Пример (можно вставить в `load.py` после загрузки):

```python
with engine.connect() as conn:
    # проверка 1
    cnt = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}")).fetchone()[0]
    print(f"Check 1 (count): {cnt}")
    # проверка 2 – диапазон дат
    min_max = conn.execute(text(f"SELECT MIN(date), MAX(date) FROM {TABLE_NAME}")).fetchone()
    print(f"Check 2 (date range): {min_max[0]} to {min_max[1]}")
    # проверка 3 – NULL
    nulls = conn.execute(text(f"""
        SELECT SUM(CASE WHEN date IS NULL THEN 1 ELSE 0 END),
               SUM(CASE WHEN city_id IS NULL THEN 1 ELSE 0 END)
        FROM {TABLE_NAME}
    """)).fetchone()
    print(f"Check 3 (NULLs): date={nulls[0]}, city_id={nulls[1]}")
    # проверка 4 – дубликаты
    dups = conn.execute(text(f"""
        SELECT COUNT(*) FROM (
            SELECT date, city_id, COUNT(*) 
            FROM {TABLE_NAME} 
            GROUP BY date, city_id 
            HAVING COUNT(*) > 1
        ) t
    """)).fetchone()[0]
    print(f"Check 4 (duplicates): {dups}")
    # проверка 5 – отрицательные осадки
    neg_precip = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE total_precip_mm < 0")).fetchone()[0]
    print(f"Check 5 (negative precip): {neg_precip}")