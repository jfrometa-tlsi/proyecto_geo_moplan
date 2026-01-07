# Imagen base ligera
FROM python:3.13-slim

# Evita que Python genere archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalar dependencias del sistema (necesarias para algunas librerías de Python)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto que usa Dash (por defecto 8050)
EXPOSE 8050

# Comando para ejecutar la app (usando Gunicorn para producción)
# Instalalo en tu requirements.txt: pip install gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "app:server"]