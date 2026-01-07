from database import DatabaseManager
import pandas as pd
from logger import setup_logger

logger = setup_logger("process_manager")

def procesar_rutas(cod_pedido: str) -> pd.DataFrame:
    """""" 
    query = """
    SELECT p.pedido, p.codigoPlanta, p.codigoCargadero,
           o.longitud as longitud_origen, o.latitud as latitud_origen, 
           d.longitud as longitud_destino, d.latitud as latitud_destino
    FROM planificaciones p
    LEFT JOIN maestro_origenes o ON p.codigoCargadero = o.codigo
    LEFT JOIN maestro_destinos d ON p.codigoPlanta = d.codigoPlanta
    WHERE p.pedido = :cp
    """
    try:
        db_manager = DatabaseManager()
        pedidos_df = pd.read_sql(query, con=db_manager.engine, params={"cp": str(cod_pedido)})
        if pedidos_df.empty:
            logger.warning(f"No se encontraron datos para el pedido: {cod_pedido}")
            return pd.DataFrame()
        logger.info(f"Procesando rutas para cod_pedido: {cod_pedido} con {len(pedidos_df)} registros.")
        return pedidos_df

    except Exception as e:
        logger.error(f"Error al leer datos de la base de datos: {e}")
        return pd.DataFrame()
    
if __name__ == "__main__":
    # Ejemplo de uso
    df =procesar_rutas("2800759255040")
    if not df.empty:
        print(df.head())
        print(df.info())
    else:
        print("No se procesaron datos.")