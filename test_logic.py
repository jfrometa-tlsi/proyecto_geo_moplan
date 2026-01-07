import pytest
from router import RouteProvider

def test_id_ruta_consistencia():
    # Simulamos un db_manager simple
    router = RouteProvider(None)
    id1 = router._generar_id_ruta(-3.7, 40.4, -0.3, 39.4)
    id2 = router._generar_id_ruta(-3.7, 40.4, -0.3, 39.4)
    
    assert id1 == id2  # El ID debe ser idéntico para las mismas coordenadas