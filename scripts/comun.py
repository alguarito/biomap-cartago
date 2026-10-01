"""Contrato común de todas las capas de BioMap Cartago.

Todas las capas se entregan sobre UNA rejilla de análisis en EPSG:4326:
  extensión  oeste -75.985, este -75.855, sur 4.688, norte 4.795
  resolución 0.00025° (≈ 27,7 m)  →  520 columnas × 428 filas
  fila 0 = norte, columna 0 = oeste (orden de imagen)

Salidas de cada capa (función guardar_capa):
  datos/capas/<nombre>.png   RGBA, valor codificado en 16 bits:
                             v = R*256 + G ; v = 0 → sin dato ;
                             valor = (v - 1) * escala + desplazamiento ; B = 0 ; A = 255
  datos/capas/<nombre>.json  metadatos: unidad, escala, desplazamiento, fuente,
                             licencia, periodo, procesamiento, limitaciones, estadísticas
  fuentes/rejilla/<nombre>.npy  float32 con NaN como sin dato (para estadísticas y calibración)

Uso: .venv/bin/python scripts/<capa>.py  (desde la raíz del proyecto o cualquier sitio)
"""
from __future__ import annotations

import json
import math
import os
import re
from datetime import date

import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTES = os.path.join(RAIZ, "fuentes")
DATOS = os.path.join(RAIZ, "datos")
CAPAS = os.path.join(DATOS, "capas")
REJILLA_NPY = os.path.join(FUENTES, "rejilla")
for d in (FUENTES, DATOS, CAPAS, REJILLA_NPY):
    os.makedirs(d, exist_ok=True)

OESTE, ESTE, SUR, NORTE = -75.985, -75.855, 4.688, 4.795
RES = 0.00025
ANCHO = int(round((ESTE - OESTE) / RES))   # 520
ALTO = int(round((NORTE - SUR) / RES))     # 428
CRS = "EPSG:4326"
CENTRO = (4.7464, -75.9117)

# Configuración de GDAL para leer COG públicos por HTTP sin credenciales
os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("AWS_NO_SIGN_REQUEST", "YES")
os.environ.setdefault("GDAL_HTTP_MULTIRANGE", "YES")
os.environ.setdefault("GDAL_HTTP_MERGE_CONSECUTIVE_RANGES", "YES")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif,.TIF,.tiff,.vrt,.jp2")
os.environ.setdefault("GDAL_HTTP_MAX_RETRY", "4")
os.environ.setdefault("GDAL_HTTP_RETRY_DELAY", "2")


def transformacion():
    from rasterio.transform import from_origin
    return from_origin(OESTE, NORTE, RES, RES)


def centros_celdas():
    """Devuelve (lat, lon) 2D de los centros de celda."""
    lons = OESTE + (np.arange(ANCHO) + 0.5) * RES
    lats = NORTE - (np.arange(ALTO) + 0.5) * RES
    return np.meshgrid(lats, lons, indexing="ij")


def area_celda_m2():
    """Área de cada celda en m² (varía levemente con la latitud)."""
    lat, _ = centros_celdas()
    return (RES * 110574.0) * (RES * 111320.0 * np.cos(np.radians(lat)))


# ---------------------------------------------------------------- geometría OSM

def osm():
    """Lee js/datos-osm.js (comunas, cabecera, ríos, vías principales, parques)."""
    with open(os.path.join(RAIZ, "js", "datos-osm.js"), encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r"window\.BM_OSM\s*=\s*(\{.*\});", txt, re.S)
    return json.loads(m.group(1))


def _poligono(anillo_latlon):
    from shapely.geometry import Polygon
    return Polygon([(lon, lat) for lat, lon in anillo_latlon])


def comunas():
    """Lista de zonas: Comunas 1–7 (OSM) y Zaragoza (área aproximada).

    Cada zona: {id, nombre, fuente, geom (shapely, lon/lat), indice (1..n)}.
    Si existe datos/zaragoza.json (huella derivada de datos), se usa en lugar del círculo.
    """
    from shapely.geometry import Point, shape
    d = osm()
    zonas = [
        {"id": c["id"], "nombre": c["nombre"], "fuente": "OpenStreetMap", "osm": c["osm"], "geom": _poligono(c["anillo"])}
        for c in d["comunas"]
    ]
    ruta_z = os.path.join(DATOS, "zaragoza.json")
    if os.path.exists(ruta_z):
        z = json.load(open(ruta_z, encoding="utf-8"))
        geom, fuente = shape(z["geometry"]), z["properties"].get("fuente", "derivada")
    else:
        # círculo de 450 m alrededor del nodo OSM del centro poblado
        lat0, lon0 = 4.6968, -75.9264
        geom = Point(lon0, lat0).buffer(450 / 111320.0, resolution=24)
        geom = _escalar_lon(geom, lat0)
        fuente = "aproximada (círculo de 450 m)"
    zonas.append({"id": "zaragoza", "nombre": "Zaragoza (corregimiento)", "fuente": fuente, "geom": geom})
    for i, z in enumerate(zonas, 1):
        z["indice"] = i
    return zonas


def _escalar_lon(geom, lat0):
    from shapely import affinity
    return affinity.scale(geom, xfact=1 / math.cos(math.radians(lat0)), yfact=1.0, origin=geom.centroid)


def mascara_zonas(zonas=None):
    """Rejilla uint8 con el índice de zona (0 = fuera de toda zona)."""
    from rasterio.features import rasterize
    zonas = zonas or comunas()
    return rasterize(
        [(z["geom"], z["indice"]) for z in zonas],
        out_shape=(ALTO, ANCHO), transform=transformacion(), fill=0, dtype="uint8", all_touched=False,
    )


def mascara_urbana():
    """Rejilla booleana de la cabecera municipal (OSM)."""
    from rasterio.features import rasterize
    cab = _poligono(osm()["cabecera"])
    return rasterize([(cab, 1)], out_shape=(ALTO, ANCHO), transform=transformacion(), fill=0, dtype="uint8").astype(bool)


def lineas_rio(nombre="rio_la_vieja"):
    """Eje del río como shapely LineString (lon/lat)."""
    from shapely.geometry import LineString
    return LineString([(lon, lat) for lat, lon in osm()[nombre]])


# ---------------------------------------------------------------- lectura y reproyección

def reproyectar(fuente, transform_fuente, crs_fuente, remuestreo="average", nodata_fuente=None):
    """Lleva un arreglo 2D a la rejilla común. Devuelve float32 con NaN como sin dato."""
    from rasterio.warp import reproject, Resampling
    destino = np.full((ALTO, ANCHO), np.nan, dtype=np.float32)
    src = fuente.astype(np.float32)
    if nodata_fuente is not None:
        src = np.where(src == nodata_fuente, np.nan, src)
    reproject(
        source=src, destination=destino,
        src_transform=transform_fuente, src_crs=crs_fuente, src_nodata=np.nan,
        dst_transform=transformacion(), dst_crs=CRS, dst_nodata=np.nan,
        resampling=getattr(Resampling, remuestreo),
    )
    return destino


def leer_ventana(url, margen_grados=0.01, banda=1, nivel_resumen=None):
    """Lee de un raster remoto (COG) la ventana que cubre la rejilla común (+ margen).

    Devuelve (arreglo, transform, crs, nodata).
    """
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds
    with rasterio.open(url, overview_level=nivel_resumen) if nivel_resumen is not None else rasterio.open(url) as src:
        b = transform_bounds(CRS, src.crs, OESTE - margen_grados, SUR - margen_grados, ESTE + margen_grados, NORTE + margen_grados)
        ventana = from_bounds(*b, transform=src.transform).round_offsets().round_lengths()
        arr = src.read(banda, window=ventana, boundless=True, fill_value=src.nodata if src.nodata is not None else 0)
        return arr, src.window_transform(ventana), src.crs, src.nodata


# ---------------------------------------------------------------- salida

def guardar_capa(nombre, valores, escala, desplazamiento, meta):
    """Escribe la capa en el formato del contrato y devuelve sus estadísticas.

    valores: float 2D (ALTO, ANCHO) con NaN como sin dato.
    meta: dict con al menos titulo, unidad, fuente{nombre,url,licencia,cita}, periodo,
          resolucion_original_m, procesamiento[list], limitaciones[list], rango_visual[min,max].
    """
    from PIL import Image
    assert valores.shape == (ALTO, ANCHO), f"forma {valores.shape} != {(ALTO, ANCHO)}"
    v = np.asarray(valores, dtype=np.float64)
    valido = np.isfinite(v)
    cod = np.zeros(v.shape, dtype=np.uint32)
    cod[valido] = np.clip(np.round((v[valido] - desplazamiento) / escala) + 1, 1, 65535).astype(np.uint32)
    rgba = np.zeros((ALTO, ANCHO, 4), dtype=np.uint8)
    rgba[..., 0] = (cod >> 8) & 255
    rgba[..., 1] = cod & 255
    rgba[..., 3] = 255
    Image.fromarray(rgba, "RGBA").save(os.path.join(CAPAS, f"{nombre}.png"), optimize=True)
    np.save(os.path.join(REJILLA_NPY, f"{nombre}.npy"), v.astype(np.float32))

    urb = mascara_urbana()
    def resumen(mask):
        x = v[mask & valido]
        if x.size == 0:
            return None
        return {k: float(round(f(x), 4)) for k, f in {
            "min": np.min, "p10": lambda a: np.percentile(a, 10), "media": np.mean,
            "p50": np.median, "p90": lambda a: np.percentile(a, 90), "max": np.max}.items()} | {"celdas": int(x.size)}
    meta = dict(meta)
    meta.update({
        "nombre": nombre, "escala": escala, "desplazamiento": desplazamiento,
        "codificacion": "RGBA 16 bits: v=R*256+G; v=0 sin dato; valor=(v-1)*escala+desplazamiento",
        "rejilla": {"oeste": OESTE, "este": ESTE, "sur": SUR, "norte": NORTE, "res": RES, "ancho": ANCHO, "alto": ALTO, "crs": CRS},
        "estadisticas": {"extension": resumen(np.ones_like(valido)), "cabecera_urbana": resumen(urb)},
        "cobertura_pct": round(100.0 * valido.mean(), 2),
        "fecha_proceso": date.today().isoformat(),
    })
    guardar_json(os.path.join(CAPAS, f"{nombre}.json"), meta)
    return meta["estadisticas"]


def cargar_capa(nombre):
    """float32 (ALTO, ANCHO) con NaN; lee el .npy generado por guardar_capa."""
    return np.load(os.path.join(REJILLA_NPY, f"{nombre}.npy"))


def guardar_json(ruta, obj):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, default=_json_default)


def _json_default(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))
