import requests
import json
import hashlib
from datetime import datetime
import pandas as pd
from logger import setup_logger


logger = setup_logger("route_provider")



class RouteProvider:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.base_url = "http://router.project-osrm.org/route/v1/driving/"

    def _generar_id_ruta(self, lon1, lat1, lon2, lat2):
        """Crea un ID único para un par de coordenadas (redondeando a 5 decimales)."""
        # Redondeamos para evitar que micro-diferencias generen rutas nuevas
        s = f"{round(lon1,5)},{round(lat1,5)}-{round(lon2,5)},{round(lat2,5)}"
        return hashlib.md5(s.encode()).hexdigest()

    def get_route(self, lon_origen, lat_origen, lon_destino, lat_destino):
        route_id = self._generar_id_ruta(lon_origen, lat_origen, lon_destino, lat_destino)
        self.db_manager.crear_tablas_cache()
        # 1. Intentar buscar en la base de datos local
        query = "SELECT * FROM cache_rutas WHERE route_id = :rid"
        try:
            cache = pd.read_sql(query, con=self.db_manager.engine, params={"rid": route_id})
            if not cache.empty:
                logger.info(">>> Ruta recuperada de la CACHÉ local.")
                res = cache.iloc[0]
                return {
                    "geometria": json.loads(res['geometria']), # Convertir string a diccionario
                    "distancia_km": res['distancia_km'],
                    "duracion_min": res['duracion_min']
                }
        except Exception as e:
            logger.error(f"Error consultando caché: {e}")
            return None
        
        # 2. Si no está en caché, llamar a OSRM (lo que ya tenías)
        logger.info(">>> Ruta no encontrada. Consultando OSRM...")
        coords = f"{lon_origen},{lat_origen};{lon_destino},{lat_destino}"
        url = f"{self.base_url}{coords}"
        
        # Pedimos explícitamente el resumen y la geometría en formato geojson
        params = {
            "overview": "full",
            "geometries": "geojson"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Error llamando a OSRM: {e}")
            return None

        if data.get("code") == "Ok":
            route = data["routes"][0]
            info = {
                "route_id": route_id,
                "geometria": json.dumps(route["geometry"]), # Convertir diccionario a string
                "distancia_km": round(route["distance"] / 1000, 2),
                "duracion_min": round(route["duration"] / 60, 2),
                "updated_at": datetime.now()
            }
            
            # 3. Guardar en SQLite para la próxima vez
            df_save = pd.DataFrame([info])
            df_save.to_sql("cache_rutas", con=self.db_manager.engine, if_exists='append', index=False)
            
            # Devolver formato limpio
            logger.info(">>> Ruta guardada en la CACHÉ local.")
            return {
                "geometria": route["geometry"],
                "distancia_km": info["distancia_km"],
                "duracion_min": info["duracion_min"]
            }
        logger.error("Error: OSRM no devolvió una ruta válida.")
        return None
        
if __name__ == "__main__":    
    # Ejemplo de uso
    from process import procesar_rutas
    from database import DatabaseManager
    db_manager = DatabaseManager()
    rp = RouteProvider(db_manager)
    df = procesar_rutas("2800759255040")
    long_origen = df.iloc[0]['longitud_origen']
    lat_origen = df.iloc[0]['latitud_origen']
    long_destino = df.iloc[0]['longitud_destino']
    lat_destino = df.iloc[0]['latitud_destino']
    ruta = rp.get_route(long_origen, lat_origen, long_destino, lat_destino)
    if ruta:
        print(f"Distancia: {ruta['distancia_km']} km, Duración: {ruta['duracion_min']} min")
        #print("Geometría de la ruta (GeoJSON):")
        #print(ruta["geometria"])
    else:
        print("No se pudo obtener la ruta.")