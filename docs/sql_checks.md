# SQL checks для таблицы `daily_weather` (variant_04, London)

## 1. Таблица не пустая

```sql
SELECT COUNT(*) AS row_count FROM daily_weather;
```

**Ожидается:** `> 0` (после `full` – 7, после `incremental` – 14).

---

## 2. Диапазон дат

```sql
SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM daily_weather;
```

**Ожидается:** `2024-01-01` и `2024-01-07` (после расширения – `2024-01-14`).

---

## 3. NULL в ключевых колонках

```sql
SELECT COUNT(*) AS null_count FROM daily_weather
WHERE date IS NULL OR city_id IS NULL;
```

**Ожидается:** `0`.

---

## 4. Дубликаты по бизнес-ключу `(date, city_id)`

```sql
SELECT date, city_id, COUNT(*) FROM daily_weather
GROUP BY date, city_id
HAVING COUNT(*) > 1;
```

**Ожидается:** пусто.

---

## 5. Диапазон температур (разумные пределы)

```sql
SELECT MIN(min_temp) AS global_min, MAX(max_temp) AS global_max FROM daily_weather;
```

**Ожидается:** для Лондона зимой примерно от `-5` до `+15`.

---

## 6. Логика `min ≤ avg ≤ max`

```sql
SELECT COUNT(*) AS violations FROM daily_weather
WHERE min_temp > avg_temp OR avg_temp > max_temp;
```

**Ожидается:** `0`.

---

## 7. Неотрицательные осадки

```sql
SELECT COUNT(*) FROM daily_weather WHERE total_precip < 0;
```

**Ожидается:** `0`.

---

## 8. Влажность в диапазоне `[0, 100]`

```sql
SELECT COUNT(*) FROM daily_weather WHERE avg_humidity < 0 OR avg_humidity > 100;
```

**Ожидается:** `0`.

---

## 9. Скорость ветра неотрицательна

```sql
SELECT COUNT(*) FROM daily_weather WHERE avg_windspeed < 0;
```

**Ожидается:** `0`.

---

## 10. Идемпотентность (хеш до и после повторного инкремента)

```sql
SELECT MD5(STRING_AGG(CONCAT(date, city_id, avg_temp), ',' ORDER BY date)) FROM daily_weather;
```

**Ожидается:** хеш не должен меняться при повторном `--mode incremental` без новых данных.
