import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from logger import setup_logger
import certifi
import urllib3

http = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs=certifi.where()
)


logger = setup_logger("data_fetcher")

# Cargar credenciales
load_dotenv()

class DataFetcher:
    def __init__(self):
        self.base_url = "https://moplan.esk.es:8082"
        self.user = os.getenv("API_USER")
        self.password = os.getenv("API_PASSWORD")
        self.session = requests.Session()
        self.token = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://moplan.esk.es:4433",
            "Referer": "https://moplan.esk.es:4433/"
        }

    def login(self):
        """Autenticación para obtener el Bearer Token."""
        url = f"{self.base_url}/login"
        payload = {
            "username": self.user,
            "password": self.password
        }
        
        try:
            response = self.session.post(url, json=payload, headers=self.headers, timeout=10,verify=False)
            response.raise_for_status()
            data = response.json()
            
            self.token = data.get("token")
            # Actualizamos los headers globales de la sesión con el token
            self.headers["Authorization"] = f"Bearer {self.token}"
            logger.info(f"[{datetime.now()}] Login exitoso. Token obtenido.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en el login: {e}")
            return False

    def fetch_destinos(self)-> pd.DataFrame:
        """Obtiene el maestro de destinos.
        returns: pd.DataFrame con los datos de destinos.
        """
        if not self.token:
            if not self.login():
                return pd.DataFrame()

        url = f"{self.base_url}/proc/p_manPlantas"
        payload = {"accion": "SELECT_INICIO"}

        try:
            # Usamos PUT como identificaste en el navegador
            response = self.session.put(url, json=payload, headers=self.headers, timeout=15,verify=False)
            response.raise_for_status()
            
            # Convertimos la respuesta JSON directamente a DataFrame
            df = pd.DataFrame(response.json())
            
            if not df.empty:
                logger.info(f"[{datetime.now()}] Se han recuperado {len(df)} registros de destinos.")
                return self._clean_plantas_data(df)
            else:
                logger.info("La API devolvió una lista vacía.")
                return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener los destinos: {e}")
            return pd.DataFrame()   

    def fetch_cargaderos(self) -> pd.DataFrame:
        """Obtiene el maestro de cargaderos.
        returns: pd.DataFrame con los datos de cargaderos.
        """
        if not self.token:
            if not self.login():
                return pd.DataFrame()

        url = f"{self.base_url}/proc/p_manCargaderos"
        payload = {"accion": "SELECT_INICIO"}

        try:
            # Usamos PUT como identificaste en el navegador
            response = self.session.put(url, json=payload, headers=self.headers, timeout=15,verify=False)
            response.raise_for_status()
            
            # Convertimos la respuesta JSON directamente a DataFrame
            df = pd.DataFrame(response.json())
            
            if not df.empty:
                logger.info(f"[{datetime.now()}] Se han recuperado {len(df)} registros de cargaderos.")
                return self._clean_plantas_data(df)
            else:
                logger.info("La API devolvió una lista vacía.")
                return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener cargaderos: {e}")
            return pd.DataFrame()

    def _clean_plantas_data(self, df) -> pd.DataFrame:
        """Limpieza inicial de datos (tipos y coordenadas).
        Args:
            df (pd.DataFrame): DataFrame con los datos sin procesar.
        Returns:
            pd.DataFrame: DataFrame limpio.
        """
        # Aquí puedes renombrar columnas si los nombres de la API son crípticos
        # Ejemplo: df.rename(columns={'pla_lat': 'latitud', 'pla_lon': 'longitud'}, inplace=True)
            
        # Asegurar que las coordenadas sean numéricas (sustituyendo coma por punto si fuera necesario)
        cols_coord = [c for c in df.columns if 'lat' in c.lower() or 'lon' in c.lower()]
        for col in cols_coord:
            df[col] = pd.to_numeric(df[col], errors='coerce')            
        return df
        
    def fetch_planificaciones(self) -> pd.DataFrame:
        """Obtiene el maestro de cargaderos."""
        if not self.token:
            if not self.login():
                return pd.DataFrame()

        url = f"{self.base_url}/proc/p_planificaciones"
        payload = {"accion": "SELECT_INICIO"}

        try:
            # Usamos PUT como identificaste en el navegador
            response = self.session.put(url, json=payload, headers=self.headers, timeout=15,verify=False)
            response.raise_for_status()
            
            # Convertimos la respuesta JSON directamente a DataFrame
            df = pd.DataFrame(response.json())
            
            if not df.empty:
                logger.info(f"[{datetime.now()}] Se han recuperado {len(df)} registros de planificaciones.")
                return df
            else:
                logger.info("La API devolvió una lista vacía.")
                return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener planificaciones: {e}")
            return pd.DataFrame()

# Ejemplo de uso rápido para probar el módulo
if __name__ == "__main__":
    fetcher = DataFetcher()
    df_destinos = fetcher.fetch_destinos()
    df_cargaderos = fetcher.fetch_cargaderos()
    df_planificaciones = fetcher.fetch_planificaciones()
    if not any([df_destinos.empty, df_cargaderos.empty, df_planificaciones.empty]):
        print(df_destinos.head())
        print(df_cargaderos.head())
        print(df_planificaciones.head())
    else:
        print("No se obtuvieron datos de destinos, cargaderos o planificaciones.")