# 🚚 Sistema de Gestión Logística e Interfaz de Rutas

[![CI/CD Pipeline](https://github.com//jfrometa88/proyecto_geo_moplan/actions/workflows/main.yml/badge.svg)](https://github.com/TU_USUARIO/TU_REPO/actions)
![Python Version](https://img.shields.io/badge/python-3.13-blue)
![Docker](https://img.shields.io/badge/docker-%E2%9C%94-blue)

Esta aplicación es una solución integral para la visualización y optimización de rutas logísticas. Extrae datos de planificación de una API externa, gestiona una base de datos local en SQLite, utiliza un motor de rutas con caché (OSRM) y presenta los resultados en un dashboard interactivo construido con **Dash** y **Leaflet**.

## 🚀 Características Principales

* **ETL Automatizado:** Conexión con API de planificación y actualización de maestros de orígenes/destinos.
* **Motor de Rutas Inteligente:** Integración con OSRM para cálculo de rutas reales por carretera (no líneas rectas).
* **Caché de Geometría:** Sistema de persistencia en SQLite para evitar consultas redundantes a la API de mapas.
* **Dashboard Interactivo:** Selección de pedidos, visualización de rutas en mapa dinámico y métricas de viaje (km/tiempo).
* **Logs en tiempo real:** Endpoint dedicado para monitoreo del sistema bajo demanda.

## 🛠️ Stack Tecnológico

* **Frontend:** Dash (Plotly), Dash Bootstrap Components, Dash Leaflet.
* **Backend:** Python 3.13, Flask, SQLAlchemy.
* **Base de Datos:** SQLite.
* **Infraestructura:** Docker, Gunicorn.
* **CI/CD:** GitHub Actions.

## 📦 Instalación y Despliegue con Docker

La forma recomendada de ejecutar esta aplicación es mediante **Docker Compose** para asegurar la persistencia de los datos y logs.

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/jfrometa88/proyecto_geo_moplan.git](https://github.com/jfrometa88/proyecto_geo_moplan.git)
    cd proyecto_geo_moplan
    ```

2.  **Configurar variables de entorno:**
    Crea un archivo `.env` en la raíz con tus credenciales:
    ```env
    API_USER=tu_usuario
    API_PASSWORD=tu_password
    LOGS_TOKEN=tu_token_secreto
    ```

3.  **Levantar el contenedor:**
    ```bash
    docker-compose up -d --build
    ```

La aplicación estará disponible en: `http://localhost:8050`

## 📂 Estructura del Proyecto

```text
├── .github/workflows/  # Pipelines de CI/CD
├── logs/               # Logs persistentes (mapeado por volumen)
├── router.py           # Lógica de OSRM y gestión de caché
├── data_fetcher.py     # utilidad para carga de datos
├── main_interfaz_datos.py  # Modelos de SQLAlchemy y conexión SQLite
├── database.py         # Modelos de SQLAlchemy y conexión SQLite
├── logistica.db           # BBDD de SQLite
├── process.py           # procesador de datos
├── logger.py           # Para logging
├── app.py              # Aplicación principal de Dash
├── test_logic.py           # Prueba unitaria de lógica
├── Dockerfile          # Definición de la imagen de contenedor
├── docker-compose.yml  # Orquestación de servicios y volúmenes
└── requirements.txt    # Dependencias del proyecto