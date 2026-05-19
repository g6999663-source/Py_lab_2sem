

![Status](https://img.shields.io/badge/status-OK-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Pandas](https://img.shields.io/badge/Pandas-2.3.3-purple)
#python_labi

## Описание:
Учебный проект по курсу анализа данных. Настройка окружения и базовая структура репозитория.
## Результат проверки:
```bash
python: D:\anaconda\anaconda3\python.exe
pandas: 2.3.3
```
### Проверка пройдена успешно
## Структура проекта:
```
python_labi/
│
├── broken_env.py          # Диагностика
├── requirements.txt       # Зависимости
├── README.md              # Документация
│
├── scripts/
│   └── setup_env.bat      # Автоматическая настройка
│
├── src/                   # Исходный код
├── data/                  # Данные
├── notebooks/             # Ноутбуки
├── docs/                  # Документы
├── configs/               # Конфиги
└── tests/                 # Тесты
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
