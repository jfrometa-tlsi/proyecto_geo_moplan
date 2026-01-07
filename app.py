from pathlib import Path
from flask import Response, request, abort
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import pandas as pd
from database import DatabaseManager  # Tu clase de base de datos
from router import RouteProvider      # Tu motor de rutas con caché
from process import procesar_rutas   # Tu función de procesamiento de rutas
from logger import setup_logger

logger = setup_logger("app")

# 1. Inicialización
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server  # Para despliegue en plataformas como Heroku
db = DatabaseManager()
router = RouteProvider(db)

LOG_FOLDER = Path("logs")
LOG_FILE = LOG_FOLDER / "logs.log"

@app.server.route("/health")
def health_check():
    # Intenta una consulta simple a SQLite
    try:
        db.engine.connect()
        return {"status": "ok", "database": "connected"}, 200
    except Exception:
        return {"status": "error"}, 500

@app.server.route("/view-logs")
def view_logs():
    
    # Verificación con pathlib
    if not LOG_FILE.exists():
        return f"El archivo {LOG_FILE} no existe todavía.", 404

    try:
        # Leemos el archivo de forma segura
        lineas = LOG_FILE.read_text(encoding="utf-8").splitlines()
        ultimas_lineas = lineas[-100:]
        return Response("\n".join(ultimas_lineas), mimetype="text/plain")
    except Exception as e:
        return f"Error al leer los logs: {e}", 500

# Obtener lista inicial de pedidos para el Dropdown
def get_lista_pedidos():
    df = db.leer_tabla("planificaciones")
    if not df.empty:
        return [{"label": str(p), "value": str(p)} for p in df['pedido'].unique()]
    return []

# 2. Layout (Diseño de la Interfaz)
app.layout = dbc.Container([
    dbc.Row([
        # Columna Lateral (Sidebar)
        dbc.Col([
            html.H2("Gestión de Cargas", className="display-6 text-primary"),
            html.Hr(),
            html.P("Selecciona una planificación para visualizar la ruta:"),
            
            dcc.Dropdown(
                id="selector-pedido",
                options=get_lista_pedidos(),
                placeholder="Buscar pedido...",
                className="mb-4"
            ),
            
            html.Div(id="info-ruta-card") # Aquí irán los km y tiempo
        ], width=3, className="bg-light p-4 shadow-sm", style={"height": "100vh"}),

        # Columna Principal (Mapa)
        dbc.Col([
            dl.Map([
                dl.TileLayer(), # Fondo de OpenStreetMap
                dl.LayerGroup(id="capa-marcadores"), # Para los pins de origen/destino
                dl.LayerGroup(id="capa-ruta"),       # Para la línea de la carretera
            ], 
            id="mapa-logistico",
            center=[40.4167, -3.7037], # Centro de España
            zoom=6, 
            style={'width': '100%', 'height': '100%'})
        ], width=9, className="p-0")
    ], className="g-0") # g_0 elimina los espacios entre columnas
], fluid=True)

# 3. Callback (Lógica de Interacción)
@app.callback(
    [Output("capa-marcadores", "children"),
     Output("capa-ruta", "children"),
     Output("info-ruta-card", "children"),
     Output("mapa-logistico", "center")], # Para centrar el mapa al cargar],
    [Input("selector-pedido", "value")]
)
def actualizar_mapa(cod_pedido):
    if not cod_pedido:
        logger.info("No se ha seleccionado ningún pedido.")
        return [], [], "", [40.4167, -3.7037]
    df_rutas = procesar_rutas(cod_pedido)
    row = df_rutas.iloc[0]
    lo_o, la_o = row['longitud_origen'], row['latitud_origen']
    lo_d, la_d = row['longitud_destino'], row['latitud_destino']
    cod_planta = row['codigoPlanta']
    cod_cargadero = row['codigoCargadero']    

    # Validación robusta: pd.isna() detecta tanto None como np.nan
    coords = [lo_o, la_o, lo_d, la_d]
    if any(pd.isna(c) for c in coords):
        logger.error(f"Coordenadas inválidas (NaN o None) para el pedido: {cod_pedido}")
        return [], [], dbc.Alert("Faltan coordenadas geográficas en el maestro de orígenes/destinos.", color="danger"), [40.4167, -3.7037]

    # Si pasa el filtro, procedemos
    ruta = router.get_route(lo_o, la_o, lo_d, la_d)
    logger.info(f"Tipo de geometría: {type(ruta['geometria'])}")
    if not ruta:
        logger.error(f"No se pudo obtener la ruta para el pedido: {cod_pedido}")
        return [], [], dbc.Alert("No se pudo obtener la ruta.", color="danger"), [40.4167, -3.7037]
    
    # Marcadores de origen y destino
    marcador_origen = dl.Marker(position=[la_o, lo_o], children=dl.Tooltip(f"Origen: {cod_cargadero}"))
    marcador_destino = dl.Marker(position=[la_d, lo_d], children=dl.Tooltip(f"Destino: {cod_planta}"))

    # 4. Crear la Polilínea de la ruta
    # OSRM devuelve GeoJSON, Dash Leaflet lo lee directamente
    geojson_data = {
        "type": "Feature",
        "geometry": ruta['geometria'], # El diccionario que mencionamos antes
        "properties": {}
    }
    ruta_geojson = dl.GeoJSON(data=geojson_data, style={"color": "#2c3e50", "weight": 5},id="ruta-geojson")
    # 5. Crear tarjeta de información técnica
    card_info = dbc.Card([
        dbc.CardBody([
            html.H5("Detalles del Viaje", className="card-title"),
            html.P(f"Distancia: {ruta['distancia_km']} km", className="mb-1"),
            html.P(f"Tiempo est.: {ruta['duracion_min']} min", className="mb-0"),
            html.Small("Datos calculados vía OSRM/Caché local", className="text-muted")
        ])
    ], color="light", className="mt-3 shadow-sm")
    # Centro del mapa: El punto de origen
    nuevo_centro = [la_o, lo_o]
    return [marcador_origen, marcador_destino], [ruta_geojson], card_info, nuevo_centro

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8040, debug=True)