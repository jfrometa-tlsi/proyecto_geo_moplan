from data_fetcher import DataFetcher
from database import DatabaseManager
from logger import setup_logger

logger = setup_logger("main_interfaz_datos")

def integrar_datos() -> None:
    """Función principal para integrar la obtención y almacenamiento de datos."""
    try:
        # 1. Traer los datos (lo que ya lograste)
        fetcher = DataFetcher()
        df_origenes = fetcher.fetch_cargaderos()
        df_destinos = fetcher.fetch_destinos()
        df_planificaciones = fetcher.fetch_planificaciones()

        # 2. Inicializar la base de datos
        db = DatabaseManager()

        # 3. Guardar todo
        db.guardar_datos(df_origenes, "maestro_origenes")
        db.guardar_datos(df_destinos, "maestro_destinos")
        db.guardar_datos(df_planificaciones, "planificaciones")
        logger.info("Todos los datos se han integrado y almacenado correctamente.")
    except Exception as e:
        logger.error(f"Error en la integración de datos: {e}")

if __name__ == "__main__":
    integrar_datos()