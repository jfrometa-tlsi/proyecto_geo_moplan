from sqlalchemy import create_engine, text
import pandas as pd
from logger import setup_logger

logger = setup_logger("database_manager")


class DatabaseManager:
    def __init__(self, db_name="logistica.db") -> None:
        # Creamos la conexión a SQLite (el archivo se creará automáticamente)
        self.engine = create_engine(f"sqlite:///{db_name}")

    def crear_tablas_cache(self) -> None:
        query = """
        CREATE TABLE IF NOT EXISTS cache_rutas (
            route_id TEXT PRIMARY KEY,
            geometria TEXT NOT NULL,
            distancia_km REAL,
            duracion_min REAL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self.engine.begin() as conn:
            conn.execute(text(query))
            logger.info("Tabla de caché creada correctamente.")
    
    def guardar_datos(self, df: pd.DataFrame, table_name: str, if_exists='replace'):
        """
        Guarda un DataFrame en una tabla específica.
        if_exists: 'replace' para sobrescribir, 'append' para añadir datos nuevos.
        """
        if df.empty:
            logger.warning(f"Advertencia: El DataFrame para {table_name} está vacío. No se guardará nada.")
            return
        
        try:
            # .to_sql es la magia de Pandas + SQLAlchemy
            # index=False evita que se cree una columna extra con los índices de Pandas
            df.to_sql(table_name, con=self.engine, if_exists=if_exists, index=False)
            logger.info(f"Éxito: Tabla '{table_name}' actualizada con {len(df)} registros.")
        except Exception as e:
            logger.error(f"Error al guardar en la base de datos: {e}")

    def leer_tabla(self, table_name) -> pd.DataFrame:
        """Recupera una tabla completa como DataFrame."""
        return pd.read_sql(f"SELECT * FROM {table_name}", con=self.engine)