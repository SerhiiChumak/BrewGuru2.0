# Використовуємо легку версію Python
FROM python:3.11-slim

# Встановлюємо системні залежності для Postgres
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо список залежностей та встановлюємо їх
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код проєкту
COPY . .

# Відкриваємо порт 8000
EXPOSE 8000

# Команда для запуску додатка
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
