"""NDVI de Sentinel-2 L2A (2024–2025) para BioMap Cartago.

Producto «sentinel2»: capas 'ndvi' (mediana 2024–2025), 'ndvi_n' (observaciones válidas por celda)
y, si hay observaciones suficientes, 'ndvi_seco' (mediana de los meses dic–feb y jun–ago), más una
serie por fecha y resumen mensual (datos/series/sentinel2.json) y el manifiesto de items STAC
(scripts/sentinel2_items.json, versionable: permite reconstruir el catálogo exacto).

FUENTE
  Sentinel-2 Nivel 2A (reflectancia de superficie, Sen2Cor), Programa Copernicus (ESA/UE),
  en formato COG publicado por Element 84 en AWS Open Data (Registry of Open Data:
  «Sentinel-2 Cloud-Optimized GeoTIFFs»), catalogado en Earth Search:
    STAC  https://earth-search.aws.element84.com/v1   colección sentinel-2-l2a
    COG   https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/...
  Assets usados: red (B04, 10 m), nir (B08, 10 m), scl (clasificación de escena, 20 m),
  aot (espesor óptico de aerosoles de Sen2Cor; el STAC dice 20 m pero el COG es de 60 m; solo para
  marcar escenas con bruma).
  LICENCIA: datos Copernicus Sentinel, uso libre y abierto (Aviso legal de los datos
  Sentinel de Copernicus, Reglamento Delegado (UE) 1159/2013). Atribución obligatoria:
  «Contiene datos modificados de Copernicus Sentinel [2024–2025], procesados por BioMap Cartago».

PASOS
  1. Catálogo STAC: bbox de la rejilla común, 2024-01-01/2025-12-31, SIN filtro de nubes en la
     consulta (fuentes/sentinel2/stac_items.json). Se consideran los items con eo:cloud_cover
     < NUBES_MAX = 90 %. Ese porcentaje es de la tesela MGRS completa (110 km); la zona es ≈ 1,4 %
     de ella, así que la selección real la hace la SCL local (paso 4). Si falta el catálogo, se
     reconstruye con los IDs de scripts/sentinel2_items.json; --refrescar repite la consulta.
  2. Rejilla de trabajo a 10 m en UTM 18N (EPSG:32618) que cubre la rejilla común (+~65 m),
     alineada a múltiplos de 20 m: coincide píxel a píxel con las teselas MGRS 18NUL y 18NVL
     (mismo huso, orígenes múltiplos de 20 m), así que no hay remuestreo a 10 m.
  3. Agrupación por adquisición (plataforma, fecha, órbita relativa): la misma pasada aparece
     en dos teselas (18NUL y 18NVL se solapan ~10 km) y, a veces, en dos datastrips de la misma
     tesela (items _0/_1/_2: distinto datastrip_id e inicio de adquisición, no reprocesos).
     Mosaico por adquisición: 18NUL primero y, dentro de cada tesela, el item que más cubre la
     zona (evita costuras entre dos corridas de Sen2Cor). Así no se cuenta dos veces una pasada.
  4. SCL (20 m) leída solo en la ventana (~60 kB por item). Válidos: 4 vegetación, 5 no vegetado,
     6 agua. Descartados: 0 sin dato, 1 saturado/defectuoso, 2 sombra topográfica/áreas oscuras,
     3 sombra de nube, 7 sin clasificar («clouds low probability / unclassified»; < 1 % de las
     observaciones), 8 y 9 nube, 10 cirros, 11 nieve. Además, margen de 40 m alrededor de
     3, 8, 9 y 10 (criterio propio). Se usan las adquisiciones con ≥ 50 % de píxeles válidos
     en la parte de la zona que cubren (FRAC_MIN). Los porcentajes de clases se calculan sobre
     las observaciones (clases 1–11), sin la clase 0 (sin dato / fuera de la pasada).
  5. B04 y B08 leídos por bloques internos del COG (1024×1024 px): solo los bloques con al menos
     UMBRAL_BLOQUE píxeles válidos. Caché por bloque en fuentes/sentinel2/cache/ (no se publica);
     la ejecución es reanudable (--minutos, --max-bloques, --sin-descarga). AOT (20 m) leído en la
     ventana de los items de las adquisiciones seleccionadas.
  6. Reflectancia = DN × 0,0001. OJO: 'raster:bands' declara offset −0,1 (el BOA_ADD_OFFSET
     = −1000 de ESA para baseline ≥ 04.00), pero Earth Search YA lo restó a los DN de los COG
     (earthsearch:boa_offset_applied). Evidencia: (a) el mismo producto en Planetary Computer
     (DN de ESA sin tocar) tiene exactamente DN_PC = DN_ES + 1000 (--comparar-pc);
     (b) DN del rojo en vegetación (SCL 4): mediana ≈ 516, 92 % < 1000 (con el offset la
     reflectancia sería negativa). Cinco items usados con boa_offset_applied = false (18NUL de
     2024-12-16, 2025-01-22, 2025-01-25, 2025-02-19 y 2025-03-08) también traen el offset restado
     (2025-02-19: DN_PC − DN_ES = 1000 exacto): la prueba física por item decide.
     Los COG recortan a DN = 1 las reflectancias que con el offset serían ≤ 0 (DN_PC 931 → DN_ES 1):
     DN ≤ 1 en B04 o B08 se trata como dato censurado y se descarta.
  7. NDVI = (NIR − Rojo)/(NIR + Rojo) por escena a 10 m. Mediana por píxel (N ≥ 5);
     seco: meses 12, 1, 2, 6, 7, 8 (N ≥ 3). Diagnósticos (no publicados como capa): ventana
     posterior a las temporadas secas (meses 2, 3, 8, 9) y sensibilidad a las escenas con AOT
     atípico (> Q3 + 1,5·IQR de las fechas, criterio propio). Con la lluvia mensual CHIRPS v3 del producto
     'clima' (datos/series/clima.json, si existe): correlación NDVI rural mensual–lluvia con desfases de
     0–3 meses y mediana de las fechas tras los 2 meses más secos (tercil inferior; criterio propio).
     CHIRPS v3: CC BY 4.0, Funk et al. (2026) Scientific Data 13:718.
  8. Promedio (remuestreo «average» de GDAL, ponderado por área) a la rejilla común
     0,00025° (≈ 27,7 m) con comun.reproyectar; guardar_capa('ndvi', escala 0.0001,
     desplazamiento −1). N por celda = media de N SOLO de los píxeles de 10 m que aportan
     mediana; se publica como capa 'ndvi_n' (escala 0.01) junto con la fracción de píxeles que aportan.
  9. Verificaciones (fuentes/sentinel2/verificacion.json): PNG decodificado = .npy, orientación
     N/S, puntos y polígonos OSM de control (Parque Bolívar, aeródromo, pista, río La Vieja).

USO
  .venv/bin/python scripts/sentinel2.py                 # todo (descarga por ventanas y bloques)
  .venv/bin/python scripts/sentinel2.py --solo-scl      # solo SCL y plan de descarga
  .venv/bin/python scripts/sentinel2.py --sin-descarga  # reprocesa con lo que haya en caché
  .venv/bin/python scripts/sentinel2.py --comparar-pc [item ...]   # evidencia del offset
  Sin librerías adicionales (numpy, rasterio, pyproj, shapely, scipy, pystac-client,
  planetary-computer, pillow del entorno del proyecto).
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import sys
import threading
import time
import warnings
from collections import defaultdict
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comun  # noqa: E402

import numpy as np  # noqa: E402

os.environ.setdefault("GDAL_HTTP_TIMEOUT", "1800")
os.environ.setdefault("GDAL_HTTP_LOW_SPEED_TIME", "120")    # abortar conexiones atascadas (< 200 B/s durante 2 min)
os.environ.setdefault("GDAL_HTTP_LOW_SPEED_LIMIT", "200")
os.environ.setdefault("GDAL_HTTP_CONNECTTIMEOUT", "60")
os.environ.setdefault("VSI_CACHE", "FALSE")

STAC_URL = "https://earth-search.aws.element84.com/v1"
COLECCION = "sentinel-2-l2a"
PERIODO = "2024-01-01/2025-12-31"
NUBES_MAX = 90                   # % de nubes de la TESELA (110 km); la SCL local decide (FRAC_MIN)
CRS_UTM = "EPSG:32618"
MARGEN_GRADOS = 0.0006           # ~65 m alrededor de la rejilla común
SCL_VALIDAS = (4, 5, 6)          # 7 (sin clasificar) excluida: ver decisión en meta["procesamiento"]
MESES_SECOS = (12, 1, 2, 6, 7, 8)
MESES_POST_SECO = (2, 3, 8, 9)   # diagnóstico: transiciones tras las temporadas secas (Cenicaña 2010)
UMBRAL_BLOQUE = 2000             # píxeles válidos de 10 m (0,2 km²) para descargar un bloque
N_MIN = 5                        # observaciones mínimas por píxel de 10 m para la mediana anual
N_MIN_SECO = 3                   # ídem para la mediana de meses secos (y el diagnóstico post-seco)
BLOQUE = 1024                    # bloque interno de los COG de 10 m (verificado en la cabecera)
POR_MES = 0                      # tope de adquisiciones por mes (año-mes); 0 = todas
FRAC_MIN = 0.5                   # fracción mínima despejada (SCL válida) de la parte de la zona que cubre la adquisición
BUFFER_NUBE_M = 40               # margen alrededor de nubes, sombras y cirros (clases 3, 8, 9, 10), múltiplo de 20 m
NUBE = (3, 8, 9, 10)
DN_CENSURA = 1                   # DN ≤ 1: reflectancia recortada por Earth Search (≤ 0 tras el offset)
AOT_ESCALA = 0.001               # AOT_QUANTIFICATION_VALUE = 1000 (MTD_MSIL2A; raster:bands scale 0.001)

DIR = os.path.join(comun.FUENTES, "sentinel2")
CACHE = os.path.join(DIR, "cache")
CATALOGO = os.path.join(DIR, "stac_items.json")
MANIFIESTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sentinel2_items.json")
SERIES = os.path.join(comun.DATOS, "series")
os.makedirs(CACHE, exist_ok=True)
os.makedirs(SERIES, exist_ok=True)

_lock = threading.Lock()
_bytes = {"leidos": 0}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ---------------------------------------------------------------- 1. catálogo

def buscar_items(refrescar=False):
    """Catálogo completo (sin filtro de nubes). Orden de preferencia: caché local, manifiesto de IDs
    versionado (scripts/sentinel2_items.json), consulta nueva al STAC."""
    if os.path.exists(CATALOGO) and not refrescar:
        return json.load(open(CATALOGO, encoding="utf-8"))
    from pystac_client import Client
    cli = Client.open(STAC_URL)
    if os.path.exists(MANIFIESTO) and not refrescar:
        ids = json.load(open(MANIFIESTO, encoding="utf-8"))["catalogo"]
        log(f"reconstruyendo el catálogo desde el manifiesto ({len(ids)} IDs)")
        items = []
        for i in range(0, len(ids), 100):
            items += [x.to_dict() for x in cli.search(collections=[COLECCION], ids=ids[i:i + 100], max_items=200).items()]
        faltan = sorted(set(ids) - {x["id"] for x in items})
        if faltan:
            log(f"AVISO: {len(faltan)} items del manifiesto ya no están en el STAC: {faltan[:5]} …")
    else:
        s = cli.search(collections=[COLECCION], bbox=[comun.OESTE, comun.SUR, comun.ESTE, comun.NORTE],
                       datetime=PERIODO, max_items=5000)
        items = [i.to_dict() for i in s.items()]
    comun.guardar_json(CATALOGO, items)
    return items


# ---------------------------------------------------------------- 2. rejilla de trabajo UTM 10 m

def rejilla_utm():
    from rasterio.transform import from_origin
    from rasterio.warp import transform_bounds
    x0, y0, x1, y1 = transform_bounds(comun.CRS, CRS_UTM, comun.OESTE - MARGEN_GRADOS, comun.SUR - MARGEN_GRADOS,
                                      comun.ESTE + MARGEN_GRADOS, comun.NORTE + MARGEN_GRADOS, densify_pts=51)
    x0, y0 = np.floor(x0 / 20) * 20, np.floor(y0 / 20) * 20
    x1, y1 = np.ceil(x1 / 20) * 20, np.ceil(y1 / 20) * 20
    ancho, alto = int((x1 - x0) / 10), int((y1 - y0) / 10)
    return {"x0": float(x0), "y1": float(y1), "ancho": ancho, "alto": alto,
            "transform": from_origin(x0, y1, 10, 10)}


def ventana_item(item, asset, R, res):
    """Desplazamientos (fila, col) de la rejilla de trabajo dentro de la imagen del asset."""
    t = item["assets"][asset]["proj:transform"]
    assert abs(t[0] - res) < 1e-6 and abs(t[4] + res) < 1e-6, (item["id"], asset, t)
    col = (R["x0"] - t[2]) / res
    fila = (t[5] - R["y1"]) / res
    assert abs(col - round(col)) < 1e-6 and abs(fila - round(fila)) < 1e-6, "rejilla no alineada"
    alto_img, ancho_img = item["assets"][asset]["proj:shape"]
    return int(round(fila)), int(round(col)), alto_img, ancho_img


def orbita(item):
    return item["properties"]["s2:product_uri"].split("_")[4]


def adquisiciones(items):
    """{clave: [items]} con clave = fecha_plataforma_órbita (el orden se fija tras leer la SCL)."""
    g = defaultdict(list)
    for it in items:
        p = it["properties"]
        clave = f'{p["datetime"][:10]}_{p["platform"][-2:].upper()}_{orbita(it)}'
        g[clave].append(it)
    return dict(sorted(g.items()))


def ordenar_grupo(grupo, cobertura):
    """18NUL primero; dentro de cada tesela, el item con más píxeles con dato en la zona (luego por id)."""
    return sorted(grupo, key=lambda i: (i["properties"]["grid:code"] != "MGRS-18NUL", -cobertura[i["id"]], i["id"]))


# ---------------------------------------------------------------- lectura remota con reintentos

def leer_remoto(url, f0, c0, alto, ancho, intentos=5):
    """Lee la ventana [f0:f0+alto, c0:c0+ancho] (dentro de la imagen) de un COG remoto."""
    import rasterio
    from rasterio.windows import Window
    ultimo = None
    for k in range(intentos):
        try:
            with rasterio.open(url) as s:
                arr = s.read(1, window=Window(c0, f0, ancho, alto))
            return arr
        except Exception as e:  # red lenta / cortes: reintentar
            ultimo = e
            log(f"  reintento {k + 1}/{intentos} {os.path.basename(os.path.dirname(url))}/{os.path.basename(url)}: {str(e)[:120]}")
            time.sleep(5 * (k + 1))
    raise RuntimeError(f"lectura fallida {url}: {ultimo}")


def leer_en_rejilla(item, asset, R, res, sub=None, dtype=None):
    """Lee el asset en la rejilla de trabajo (a su resolución) y devuelve un arreglo con 0 fuera.

    sub = (f0, c0, alto, ancho) en píxeles de la rejilla de trabajo a esa resolución (opcional).
    """
    H, W = (R["alto"], R["ancho"]) if res == 10 else (R["alto"] // 2, R["ancho"] // 2)
    f_off, c_off, alto_img, ancho_img = ventana_item(item, asset, R, res)
    sf0, sc0, sh, sw = sub if sub else (0, 0, H, W)
    # intersección con la imagen
    a0, b0 = max(sf0 + f_off, 0), max(sc0 + c_off, 0)
    a1, b1 = min(sf0 + sh + f_off, alto_img), min(sc0 + sw + c_off, ancho_img)
    out = np.zeros((sh, sw), dtype=dtype or (np.uint16 if res == 10 else np.uint8))
    if a1 <= a0 or b1 <= b0:
        return out
    arr = leer_remoto(item["assets"][asset]["href"], a0, b0, a1 - a0, b1 - b0)
    out[a0 - f_off - sf0:a1 - f_off - sf0, b0 - c_off - sc0:b1 - c_off - sc0] = arr
    return out


# ---------------------------------------------------------------- 3–4. SCL y AOT por item

def _intersecta(item):
    from shapely.geometry import box, shape
    aoi = box(comun.OESTE - MARGEN_GRADOS, comun.SUR - MARGEN_GRADOS, comun.ESTE + MARGEN_GRADOS, comun.NORTE + MARGEN_GRADOS)
    return shape(item["geometry"]).intersects(aoi)


def scl_item(item, R):
    ruta = os.path.join(CACHE, item["id"], "scl.npy")
    if os.path.exists(ruta):
        return np.load(ruta)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    arr = leer_en_rejilla(item, "scl", R, 20) if _intersecta(item) else np.zeros((R["alto"] // 2, R["ancho"] // 2), np.uint8)
    np.save(ruta, arr)
    return arr


def aot_item(item, R, intentos=5):
    """AOT de Sen2Cor (DN) llevado a la rejilla de trabajo de 20 m (vecino más cercano); 0 = sin dato.

    OJO: el STAC declara el asset 'aot' a 20 m (proj:shape 5490), pero el COG AOT.tif de Earth Search
    es de 60 m (1830 × 1830 px). Por eso se usa la georreferenciación del propio archivo.
    """
    ruta = os.path.join(CACHE, item["id"], "aot.npy")
    if os.path.exists(ruta):
        return np.load(ruta)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    dst = np.zeros((R["alto"] // 2, R["ancho"] // 2), np.uint16)
    if _intersecta(item):
        import rasterio
        from rasterio.transform import from_origin
        from rasterio.warp import reproject, Resampling
        from rasterio.windows import Window
        x0, y1 = R["x0"], R["y1"]
        x1, y0 = x0 + R["ancho"] * 10, y1 - R["alto"] * 10
        ultimo = None
        for k in range(intentos):
            try:
                with rasterio.open(item["assets"]["aot"]["href"]) as s:
                    T = s.transform
                    c0 = max(int(np.floor((x0 - T.c) / T.a)), 0)
                    c1 = min(int(np.ceil((x1 - T.c) / T.a)), s.width)
                    f0 = max(int(np.floor((T.f - y1) / -T.e)), 0)
                    f1 = min(int(np.ceil((T.f - y0) / -T.e)), s.height)
                    if c1 <= c0 or f1 <= f0:
                        break
                    w = Window(c0, f0, c1 - c0, f1 - f0)
                    arr, tr = s.read(1, window=w), s.window_transform(w)
                reproject(arr, dst, src_transform=tr, src_crs=CRS_UTM, src_nodata=0, dst_transform=from_origin(x0, y1, 20, 20),
                          dst_crs=CRS_UTM, dst_nodata=0, resampling=Resampling.nearest)
                ultimo = None
                break
            except Exception as e:
                ultimo = e
                log(f"  reintento AOT {k + 1}/{intentos} {item['id']}: {str(e)[:120]}")
                time.sleep(5 * (k + 1))
        if ultimo is not None:
            raise RuntimeError(f"AOT fallida {item['id']}: {ultimo}")
    np.save(ruta + ".tmp.npy", dst)
    os.replace(ruta + ".tmp.npy", ruta)
    return dst


def mosaico_scl(grupo, sccls):
    """SCL a 10 m de la adquisición y el índice (en grupo) del item fuente por píxel (−1 = ninguno)."""
    scl = np.zeros_like(sccls[0])
    fuente = np.full(scl.shape, -1, np.int8)
    for k, s in enumerate(sccls):
        m = (scl == 0) & (s > 0)
        scl[m] = s[m]
        fuente[m] = k
    scl10 = np.repeat(np.repeat(scl, 2, 0), 2, 1)
    fuente10 = np.repeat(np.repeat(fuente, 2, 0), 2, 1)
    return scl10, fuente10


def mascara_valida(scl10):
    """Píxeles válidos a 10 m: SCL en SCL_VALIDAS y a más de BUFFER_NUBE_M de nube, sombra o cirro.

    La SCL es de 20 m (scl10 es su ampliación ×2), así que la dilatación se hace a 20 m.
    """
    from scipy.ndimage import binary_dilation
    scl20 = scl10[::2, ::2]
    nube = np.isin(scl20, NUBE)
    if BUFFER_NUBE_M:
        nube = binary_dilation(nube, structure=np.ones((3, 3), bool), iterations=BUFFER_NUBE_M // 20)
    v20 = np.isin(scl20, np.array(SCL_VALIDAS)) & ~nube
    return np.repeat(np.repeat(v20, 2, 0), 2, 1)


def pct_clases(cnt):
    """Porcentaje de cada clase SCL sobre las OBSERVACIONES (clases 1–11; la 0 es sin dato)."""
    cnt = np.asarray(cnt, np.float64)
    obs = cnt[1:].sum()
    p = {int(c): round(100 * float(cnt[c]) / obs, 2) for c in range(1, 12) if cnt[c]}
    return {"por_clase": p, "observaciones": int(obs), "sin_dato_clase0": int(cnt[0]),
            "validas_4_6": round(100 * float(cnt[4:7].sum()) / obs, 2),
            "nubes_8_10": round(100 * float(cnt[8:11].sum()) / obs, 2),
            "sombra_nube_3": round(100 * float(cnt[3]) / obs, 2),
            "sin_clasificar_7": round(100 * float(cnt[7]) / obs, 2)}


# ---------------------------------------------------------------- 5. bloques B04/B08

def bloques_item(item, R):
    """Sub-ventanas de la rejilla de trabajo que caen en un único bloque interno del COG de 10 m."""
    f_off, c_off, alto_img, ancho_img = ventana_item(item, "red", R, 10)
    subs = []
    f = max(f_off, 0)
    while f < min(f_off + R["alto"], alto_img):
        f_fin = min((f // BLOQUE + 1) * BLOQUE, f_off + R["alto"], alto_img)
        c = max(c_off, 0)
        while c < min(c_off + R["ancho"], ancho_img):
            c_fin = min((c // BLOQUE + 1) * BLOQUE, c_off + R["ancho"], ancho_img)
            subs.append((f - f_off, c - c_off, f_fin - f, c_fin - c, f // BLOQUE, c // BLOQUE))
            c = c_fin
        f = f_fin
    return subs


def ruta_bloque(item, banda, sub):
    return os.path.join(CACHE, item["id"], f"{banda}_{sub[4]}_{sub[5]}.npy")


def leer_bloque(item, sub, R):
    f0, c0, h, w, bi, bj = sub
    os.makedirs(os.path.join(CACHE, item["id"]), exist_ok=True)
    salida = []
    for banda in ("red", "nir"):
        ruta = ruta_bloque(item, banda, sub)
        if os.path.exists(ruta):
            salida.append(np.load(ruta))
            continue
        arr = leer_en_rejilla(item, banda, R, 10, sub=(f0, c0, h, w))
        np.save(ruta + ".tmp.npy", arr)
        os.replace(ruta + ".tmp.npy", ruta)
        with _lock:
            _bytes["leidos"] += 1
        salida.append(arr)
    return salida


# ---------------------------------------------------------------- 6. offset de reflectancia

def escala_offset(item, banda, offset_aplicado=None):
    """Escala y desplazamiento DN → reflectancia.

    'raster:bands' trae scale 0.0001 y offset −0.1 en TODOS los items 2024–2025, pero la propiedad
    'earthsearch:boa_offset_applied' = True indica que Element 84 ya restó a los DN del COG el
    BOA_ADD_OFFSET (−1000) de ESA. Evidencia (ver JSON de la capa, 'evidencia_offset'):
      · DN del rojo en vegetación (SCL 4): mediana ≈ 500–600 y > 90 % por debajo de 1000; con el
        offset de raster:bands la reflectancia saldría negativa en casi toda la vegetación;
      · comparación píxel a píxel con el mismo producto en Planetary Computer (DN de ESA sin tocar):
        DN_EarthSearch = DN_PC − 1000.
    Por eso el offset solo se aplica si el COG conserva los DN originales (boa_offset_applied False),
    y la decisión se comprueba por item con la prueba física (offset_aplicado = resultado de la prueba).
    """
    rb = item["assets"][banda].get("raster:bands", [{}])[0]
    escala = float(rb.get("scale", 1e-4))
    aplicado = item["properties"].get("earthsearch:boa_offset_applied") if offset_aplicado is None else offset_aplicado
    return escala, (0.0 if aplicado else float(rb.get("offset", -0.1)))


def prueba_offset(red, sc):
    """Fracción de píxeles de vegetación (SCL 4) con DN del rojo < 1000.

    Con DN originales (+1000) eso implicaría reflectancia negativa (≈ 0 %); con el offset ya restado
    la vegetación tiene rojo < 0,1 casi siempre (≫ 50 %). Devuelve (fracción, n, veredicto).
    """
    v = red[(sc == 4) & (red > 0)]
    if v.size < 1000:
        return None, int(v.size), None
    f = float((v < 1000).mean())
    return round(f, 4), int(v.size), (True if f > 0.5 else False if f < 0.02 else None)


# ---------------------------------------------------------------- principal

def estadistica_grupo(grupo, scls, dentro):
    scl10, fuente10 = mosaico_scl(grupo, scls)
    cnt = np.bincount(scl10[dentro], minlength=12)
    valido = mascara_valida(scl10) & dentro
    cubierto = (scl10 > 0) & dentro
    return scl10, fuente10, cnt, valido, {
        "items": [it["id"] for it in grupo],
        "nubosidad_tesela_min": round(min(it["properties"]["eo:cloud_cover"] for it in grupo), 1),
        "frac_valida": round(float(valido.sum() / dentro.sum()), 4),
        "frac_despejada": round(float(valido.sum() / max(1, cubierto.sum())), 4),
        "frac_con_dato": round(float(cubierto.sum() / dentro.sum()), 4),
        "clases": {int(c): int(n) for c, n in enumerate(cnt) if n}}


def diagnostico_tesela(todos, R, dentro, frac_min):
    """¿Cuántas adquisiciones pasarían FRAC_MIN según la nubosidad de tesela? (solo SCL en caché)."""
    con_scl = [it for it in todos if os.path.exists(os.path.join(CACHE, it["id"], "scl.npy"))]
    d20 = dentro[::2, ::2]
    tramos = [(0, 50), (50, 80), (80, 90), (90, 95), (95, 100.01)]
    res = {f"{a:g}-{b:g}": {"adquisiciones": 0, "pasan_frac_min": 0} for a, b in tramos}
    for clave, grupo in adquisiciones(con_scl).items():
        scls = {it["id"]: np.load(os.path.join(CACHE, it["id"], "scl.npy")) for it in grupo}
        cob = {k: int((s[d20] > 0).sum()) for k, s in scls.items()}
        grupo = ordenar_grupo(grupo, cob)
        *_, r = estadistica_grupo(grupo, [scls[it["id"]] for it in grupo], dentro)
        if r["frac_con_dato"] == 0:
            continue
        for a, b in tramos:
            if a <= r["nubosidad_tesela_min"] < b:
                t = res[f"{a:g}-{b:g}"]
                t["adquisiciones"] += 1
                t["pasan_frac_min"] += int(r["frac_despejada"] >= frac_min)
    return {"items_catalogo": len(todos), "items_con_scl": len(con_scl),
            "criterio": f"adquisición agrupada por la nubosidad de tesela mínima de sus items; pasa si su fracción despejada local ≥ {frac_min}",
            "por_tramo_nubosidad_tesela_pct": res}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refrescar", action="store_true", help="volver a consultar el STAC")
    ap.add_argument("--solo-scl", action="store_true", help="detenerse tras leer la SCL")
    ap.add_argument("--hilos", type=int, default=5)
    ap.add_argument("--max-bloques", type=int, default=0, help="tope de bloques nuevos a descargar (0 = sin tope)")
    ap.add_argument("--umbral-bloque", type=int, default=UMBRAL_BLOQUE)
    ap.add_argument("--sin-descarga", action="store_true", help="usar solo bloques ya en caché")
    ap.add_argument("--por-mes", type=int, default=POR_MES, help="adquisiciones por mes (año-mes)")
    ap.add_argument("--frac-min", type=float, default=FRAC_MIN, help="fracción válida mínima de la adquisición")
    ap.add_argument("--nubes-max", type=float, default=NUBES_MAX, help="nubosidad máxima de la tesela (eo:cloud_cover)")
    ap.add_argument("--minutos", type=float, default=0, help="tope de tiempo de descarga (0 = sin tope)")
    args = ap.parse_args()

    t0 = time.time()
    todos = buscar_items(args.refrescar)
    items = [it for it in todos if it["properties"]["eo:cloud_cover"] < args.nubes_max]
    R = rejilla_utm()
    log(f"catálogo STAC: {len(todos)} items; con nubosidad de tesela < {args.nubes_max:g} %: {len(items)}; "
        f"rejilla de trabajo {R['ancho']}×{R['alto']} px de 10 m (EPSG:32618)")

    # ---- SCL de todos los items considerados (barata: ~60 kB por item)
    pendientes = [it for it in items if not os.path.exists(os.path.join(CACHE, it["id"], "scl.npy"))]
    log(f"SCL: {len(items) - len(pendientes)} en caché, {len(pendientes)} por leer")
    fallidos = set()
    with cf.ThreadPoolExecutor(args.hilos) as ex:
        futs = {ex.submit(scl_item, it, R): it for it in pendientes}
        for k, f in enumerate(cf.as_completed(futs), 1):
            it = futs[f]
            try:
                f.result()
            except Exception as e:
                fallidos.add(it["id"])
                log(f"  SCL fallida {it['id']}: {e}")
            if k % 20 == 0:
                log(f"  SCL {k}/{len(pendientes)}")
    items = [it for it in items if it["id"] not in fallidos]

    # rejilla común → máscara en la rejilla de trabajo
    from rasterio.warp import reproject, Resampling
    dentro = np.zeros((R["alto"], R["ancho"]), np.float32)
    reproject(np.ones((comun.ALTO, comun.ANCHO), np.float32), dentro, src_transform=comun.transformacion(),
              src_crs=comun.CRS, dst_transform=R["transform"], dst_crs=CRS_UTM, resampling=Resampling.nearest)
    dentro = dentro > 0.5
    urb = np.zeros_like(dentro, dtype=np.float32)
    reproject(comun.mascara_urbana().astype(np.float32), urb, src_transform=comun.transformacion(), src_crs=comun.CRS,
              dst_transform=R["transform"], dst_crs=CRS_UTM, resampling=Resampling.nearest)
    urb = urb > 0.5
    d20 = dentro[::2, ::2]

    # ---- agrupación, orden de mosaico, estadísticas y plan de bloques
    grupos = adquisiciones(items)
    plan = []          # (validos_en_bloque, clave, idx_item, sub)
    resumen = {}
    clases_tot = np.zeros(12, np.int64)
    clases_urb = np.zeros(12, np.int64)
    for clave in list(grupos):
        scls = {it["id"]: np.load(os.path.join(CACHE, it["id"], "scl.npy")) for it in grupos[clave]}
        cob = {k: int((s[d20] > 0).sum()) for k, s in scls.items()}
        grupo = grupos[clave] = ordenar_grupo(grupos[clave], cob)
        scl10, fuente10, cnt, valido, r = estadistica_grupo(grupo, [scls[it["id"]] for it in grupo], dentro)
        if r["frac_con_dato"] == 0:
            del grupos[clave]
            continue
        resumen[clave] = r
        clases_tot += cnt
        clases_urb += np.bincount(scl10[dentro & urb], minlength=12)
        for k, it in enumerate(grupo):
            for sub in bloques_item(it, R):
                f0, c0, h, w = sub[:4]
                nv = int((valido[f0:f0 + h, c0:c0 + w] & (fuente10[f0:f0 + h, c0:c0 + w] == k)).sum())
                if nv >= args.umbral_bloque:
                    plan.append((nv, clave, k, sub))
    log(f"adquisiciones con dato en la zona (plataforma+fecha+órbita): {len(resumen)}")
    pc_tot, pc_urb = pct_clases(clases_tot), pct_clases(clases_urb)
    log(f"clases SCL (% de observaciones, sin clase 0) en la rejilla: {pc_tot['por_clase']}")
    log(f"clases SCL en la cabecera: {pc_urb['por_clase']}")
    fr = sorted(v["frac_despejada"] for v in resumen.values())
    log(f"fracción despejada por adquisición: mediana {np.median(fr):.2f}; ≥{args.frac_min}: {sum(x >= args.frac_min for x in fr)} de {len(fr)}")
    en_cache = sum(1 for _, clave, k, sub in plan if os.path.exists(ruta_bloque(grupos[clave][k], "nir", sub)))
    log(f"plan: {len(plan)} bloques (×2 bandas) con ≥{args.umbral_bloque} píxeles válidos; {en_cache} ya en caché")
    diag = diagnostico_tesela(todos, R, dentro, args.frac_min)
    log(f"diagnóstico nubosidad de tesela: {json.dumps(diag['por_tramo_nubosidad_tesela_pct'])}")
    comun.guardar_json(os.path.join(DIR, "resumen_scl.json"), {
        "nubes_max_tesela": args.nubes_max, "clases_rejilla": clases_tot, "clases_cabecera": clases_urb,
        "pct_clases_rejilla": pc_tot, "pct_clases_cabecera": pc_urb, "diagnostico_tesela": diag,
        "adquisiciones": resumen, "plan_bloques": len(plan)})
    if args.solo_scl:
        log(f"fin (--solo-scl) en {time.time() - t0:.0f} s")
        return

    # ---- selección: adquisiciones con fracción despejada ≥ FRAC_MIN (opcional: tope por mes)
    por_mes = defaultdict(list)
    for cl, r in resumen.items():
        if r["frac_despejada"] >= args.frac_min:
            por_mes[cl[:7]].append(cl)
    rango = {}
    for mes, cls in por_mes.items():
        for k, cl in enumerate(sorted(cls, key=lambda c: -resumen[c]["frac_valida"])[:args.por_mes or None]):
            rango[cl] = k
    plan = [p for p in plan if p[1] in rango]
    meses_todos = [f"{a}-{m:02d}" for a in (2024, 2025) for m in range(1, 13)]
    sin_mes = {}
    for ym in meses_todos:
        if ym not in por_mes:
            cand = [(cl, r) for cl, r in resumen.items() if cl.startswith(ym)]
            mejor = max(cand, key=lambda x: x[1]["frac_despejada"]) if cand else None
            sin_mes[ym] = {"adquisiciones_con_dato": len(cand),
                           "mejor": None if not mejor else {"adquisicion": mejor[0], "frac_despejada": mejor[1]["frac_despejada"],
                                                            "nubosidad_tesela_min": mejor[1]["nubosidad_tesela_min"]}}
    log(f"selección: {len(rango)} adquisiciones (fracción despejada ≥ {args.frac_min}) en {len(por_mes)} meses; "
        f"{len(plan)} bloques; meses sin ninguna: {sin_mes}")

    # ---- AOT (20 m) de los items de las adquisiciones seleccionadas (~100–300 kB por item)
    ids_sel = [it for cl in rango for it in grupos[cl]]
    pend_aot = [it for it in ids_sel if not os.path.exists(os.path.join(CACHE, it["id"], "aot.npy"))]
    log(f"AOT: {len(ids_sel) - len(pend_aot)} en caché, {len(pend_aot)} por leer")
    if not args.sin_descarga:
        with cf.ThreadPoolExecutor(args.hilos) as ex:
            futs = {ex.submit(aot_item, it, R): it for it in pend_aot}
            for k, f in enumerate(cf.as_completed(futs), 1):
                try:
                    f.result()
                except Exception as e:
                    log(f"  AOT fallida {futs[f]['id']}: {e}")
                if k % 20 == 0:
                    log(f"  AOT {k}/{len(pend_aot)}")

    # descarga por rondas: la mejor de cada mes primero, luego la segunda...
    plan.sort(key=lambda p: (rango[p[1]], p[1], p[3][4], p[3][5]))
    nuevos = [p for p in plan if not (os.path.exists(ruta_bloque(grupos[p[1]][p[2]], "red", p[3]))
                                      and os.path.exists(ruta_bloque(grupos[p[1]][p[2]], "nir", p[3])))]
    if args.sin_descarga:
        nuevos = []
    if args.max_bloques:
        nuevos = nuevos[:args.max_bloques]
    log(f"descargando {len(nuevos)} bloques nuevos (×2 bandas) con {args.hilos} hilos; tope {args.minutos or '∞'} min")
    t1 = time.time()
    fallidos_b, cancelado = 0, False
    with cf.ThreadPoolExecutor(args.hilos) as ex:
        futs = {ex.submit(leer_bloque, grupos[cl][k], sub, R): (cl, k, sub) for _, cl, k, sub in nuevos}
        for n, f in enumerate(cf.as_completed(futs), 1):
            cl, k, sub = futs[f]
            try:
                f.result()
            except cf.CancelledError:
                continue
            except Exception as e:
                fallidos_b += 1
                log(f"  bloque fallido {cl} {sub[4:]}: {e}")
            if n % 5 == 0 or n == len(nuevos):
                dt = time.time() - t1
                log(f"  bloques {n}/{len(nuevos)}  {dt / 60:.1f} min  (~{dt / n * (len(nuevos) - n) / 60:.0f} min restantes)")
            if args.minutos and time.time() - t1 > args.minutos * 60 and not cancelado:
                cancelado = True
                log("  tope de tiempo alcanzado: se cancelan los bloques pendientes")
                for g_ in futs:
                    g_.cancel()
    # solo adquisiciones completas (todos sus bloques planificados en caché) para evitar costuras
    completas = {cl for cl in rango}
    for _, cl, k, sub in plan:
        it = grupos[cl][k]
        if not (os.path.exists(ruta_bloque(it, "red", sub)) and os.path.exists(ruta_bloque(it, "nir", sub))):
            completas.discard(cl)
    log(f"adquisiciones completas: {len(completas)} de {len(rango)} seleccionadas; bloques fallidos {fallidos_b}")
    plan = [p for p in plan if p[1] in completas]
    seleccion = {"nubes_max_tesela": args.nubes_max, "por_mes": args.por_mes, "frac_min": args.frac_min,
                 "umbral_bloque": args.umbral_bloque, "items_catalogo": len(todos), "items_considerados": len(items),
                 "disponibles": len(resumen), "seleccionadas": len(rango), "completas": len(completas),
                 "meses_con_datos": len(por_mes), "meses_sin_adquisicion_util": sin_mes}

    procesar(grupos, resumen, plan, R, dentro, urb, t0, seleccion, todos, items)


# ---------------------------------------------------------------- 7–8. NDVI, mediana y rejilla común

def mediana_por_franjas(stack, sel, n_min):
    """Mediana (float32, NaN) y número de observaciones por píxel sobre las capas sel del stack int16."""
    H, W = stack.shape[1:]
    med = np.full((H, W), np.nan, np.float32)
    n = np.zeros((H, W), np.int16)
    idx = np.flatnonzero(sel)
    if idx.size == 0:
        return med, n
    for f in range(0, H, 100):
        x = stack[idx, f:f + 100].astype(np.float32)
        x[x == -32768] = np.nan
        cnt = np.isfinite(x).sum(0)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            m = np.nanmedian(x, axis=0) / 10000.0
        m[cnt < n_min] = np.nan
        med[f:f + 100] = m
        n[f:f + 100] = cnt
    return med, n


def mascaras_rejilla():
    """Máscaras en la rejilla común: cabecera, corredor de 200 m del río La Vieja, rural del municipio."""
    from pyproj import Transformer
    from rasterio.features import rasterize
    from shapely.ops import transform as stransform
    a_utm = Transformer.from_crs(comun.CRS, CRS_UTM, always_xy=True).transform
    a_geo = Transformer.from_crs(CRS_UTM, comun.CRS, always_xy=True).transform
    rio = stransform(a_utm, comun.lineas_rio())
    corredor = stransform(a_geo, rio.buffer(200))
    d = comun.osm()
    muni = comun._poligono(d["municipio"])
    kw = dict(out_shape=(comun.ALTO, comun.ANCHO), transform=comun.transformacion(), fill=0, dtype="uint8")
    m_corr = rasterize([(corredor, 1)], **kw).astype(bool)
    m_muni = rasterize([(muni, 1)], **kw).astype(bool)
    urb = comun.mascara_urbana()
    return {"cabecera": urb, "corredor_la_vieja_200m": m_corr, "rural_municipio": m_muni & ~urb,
            "rural_municipio_sin_corredor": m_muni & ~urb & ~m_corr, "municipio_en_rejilla": m_muni}


def mes_previo(ym, k):
    a, m = int(ym[:4]), int(ym[5:7]) - k
    while m <= 0:
        m, a = m + 12, a - 1
    return f"{a}-{m:02d}"


def lluvia_chirps():
    """Lluvia mensual CHIRPS v3 de la huella urbana (producto 'clima' de BioMap: datos/series/clima.json)."""
    ruta = os.path.join(SERIES, "clima.json")
    if not os.path.exists(ruta):
        return None, None
    c = json.load(open(ruta, encoding="utf-8"))
    m = c["mensual"]
    ll = {k: v for k, v in zip(m["mes"], m["precip_chirps"]) if v is not None}
    return ll, c["climatologia_mensual"]["normal_1991_2020"]["precip_chirps"]


def celda(lat, lon):
    return int((comun.NORTE - lat) / comun.RES), int((lon - comun.OESTE) / comun.RES)


def verificar(nombre, valores, meta_guardada, puntos=True):
    """Comprobaciones: PNG decodificado = .npy; orientación N/S; puntos de control."""
    from PIL import Image
    img = np.asarray(Image.open(os.path.join(comun.CAPAS, f"{nombre}.png"))).astype(np.int64)
    v = img[..., 0] * 256 + img[..., 1]
    dec = np.where(v == 0, np.nan, (v - 1) * meta_guardada["escala"] + meta_guardada["desplazamiento"])
    npy = comun.cargar_capa(nombre)
    mismo_nan = bool(np.array_equal(np.isnan(dec), np.isnan(npy)))
    dif = float(np.nanmax(np.abs(dec - npy)))
    out = {"png_igual_npy": {"mismos_nan": mismo_nan, "dif_max": round(dif, 6), "tolerancia": meta_guardada["escala"] / 2,
                             "canal_B_cero": bool((img[..., 2] == 0).all()), "canal_A_255": bool((img[..., 3] == 255).all())}}
    if puntos:
        urb = comun.mascara_urbana()
        m_urb, m_inv = float(np.nanmean(valores[urb])), float(np.nanmean(valores[::-1][urb]))
        pts = {}
        for k, (la, lo) in {"parque_bolivar": (4.7497, -75.9132), "aeropuerto_santa_ana": (4.7601, -75.9545)}.items():
            f, c = celda(la, lo)
            pts[k] = {"celda": float(round(valores[f, c], 3)), "vecindad_3x3": float(round(np.nanmean(valores[f - 1:f + 2, c - 1:c + 2]), 3))}
        out["orientacion"] = {"media_cabecera": round(m_urb, 3), "media_cabecera_si_se_invirtiera_NS": round(m_inv, 3),
                              "correcta": m_urb < m_inv}
        out["puntos"] = pts
    return out


def _r(x, d=3):
    return None if x is None or not np.isfinite(x) else round(float(x), d)


def procesar(grupos, resumen, plan, R, dentro, urb10, t0, seleccion, todos, considerados):
    from rasterio.warp import reproject, Resampling  # noqa: F401
    H, W = R["alto"], R["ancho"]
    disp = defaultdict(list)
    for nv, cl, k, sub in plan:
        it = grupos[cl][k]
        if os.path.exists(ruta_bloque(it, "red", sub)) and os.path.exists(ruta_bloque(it, "nir", sub)):
            disp[cl].append((k, sub))
    claves = sorted(disp)
    log(f"procesando {len(claves)} adquisiciones con bloques en caché ({sum(len(v) for v in disp.values())} bloques)")
    stack = np.full((len(claves), H, W), -32768, np.int16)
    meses = np.array([int(cl[5:7]) for cl in claves])
    serie = []
    dn_rojo_veg, dn_nir_agua = [], []
    pruebas = []
    items_con_datos = set()
    censura = {"validos_scl": 0, "censurados": 0, "validos_agua_scl6": 0, "censurados_agua_scl6": 0,
               "censurados_agua_nir": 0, "validos_tierra_scl4_5": 0, "censurados_tierra_rojo": 0}
    m_rur10 = dentro & ~urb10
    d20 = dentro[::2, ::2]
    for a, cl in enumerate(claves):
        grupo = grupos[cl]
        scls = [np.load(os.path.join(CACHE, it["id"], "scl.npy")) for it in grupo]
        scl10, fuente10 = mosaico_scl(grupo, scls)
        valido10 = mascara_valida(scl10)
        # prueba física del offset por item (sobre todos sus bloques)
        decision = {}
        for k in sorted({k for k, _ in disp[cl]}):
            it = grupo[k]
            reds, scs = [], []
            for kk, sub in disp[cl]:
                if kk == k:
                    f0, c0, h, w = sub[:4]
                    reds.append(np.load(ruta_bloque(it, "red", sub)).ravel())
                    scs.append(np.where(fuente10[f0:f0 + h, c0:c0 + w] == k, scl10[f0:f0 + h, c0:c0 + w], 0).ravel())
            frac, nveg, veredicto = prueba_offset(np.concatenate(reds), np.concatenate(scs))
            bandera = it["properties"].get("earthsearch:boa_offset_applied")
            usar = bandera if veredicto is None else veredicto
            decision[k] = usar
            pruebas.append({"item": it["id"], "boa_offset_applied": bandera, "frac_dn_rojo_veg_menor_1000": frac,
                            "pixeles_veg": nveg, "veredicto_fisico": veredicto, "offset_restado_en_cog": usar,
                            "coincide": None if veredicto is None else veredicto == bandera})
            if veredicto is not None and veredicto != bandera:
                log(f"  AVISO {it['id']}: boa_offset_applied={bandera} pero la prueba física dice {veredicto} (frac {frac}); se sigue la prueba")
        veg_n, veg_bajo = 0, 0
        for k, sub in disp[cl]:
            it = grupo[k]
            f0, c0, h, w = sub[:4]
            red = np.load(ruta_bloque(it, "red", sub)).astype(np.float32)
            nir = np.load(ruta_bloque(it, "nir", sub)).astype(np.float32)
            s_r, o_r = escala_offset(it, "red", decision[k])
            s_n, o_n = escala_offset(it, "nir", decision[k])
            sc = scl10[f0:f0 + h, c0:c0 + w]
            m = valido10[f0:f0 + h, c0:c0 + w] & (fuente10[f0:f0 + h, c0:c0 + w] == k) & (red > 0) & (nir > 0)
            cens = m & ((red <= DN_CENSURA) | (nir <= DN_CENSURA))
            censura["validos_scl"] += int(m.sum())
            censura["censurados"] += int(cens.sum())
            censura["validos_agua_scl6"] += int((m & (sc == 6)).sum())
            censura["censurados_agua_scl6"] += int((cens & (sc == 6)).sum())
            censura["censurados_agua_nir"] += int((m & (sc == 6) & (nir <= DN_CENSURA)).sum())
            tierra = m & ((sc == 4) | (sc == 5))
            censura["validos_tierra_scl4_5"] += int(tierra.sum())
            censura["censurados_tierra_rojo"] += int((tierra & (red <= DN_CENSURA)).sum())
            m &= ~cens
            rng = np.random.default_rng(a * 100 + k)
            v4 = red[(sc == 4) & m]
            if v4.size:
                dn_rojo_veg.append(rng.choice(v4, min(v4.size, 2000), replace=False))
            v6 = nir[(sc == 6) & m]
            if v6.size:
                dn_nir_agua.append(rng.choice(v6, min(v6.size, 500), replace=False))
            rr, nn = red * s_r + o_r, nir * s_n + o_n
            m &= (rr > 0) & (nn > 0)
            veg = (sc == 4) & m
            veg_n += int(veg.sum())
            veg_bajo += int((veg & (rr < 0.1)).sum())
            ndvi = np.clip((nn - rr) / np.where(m, nn + rr, 1), -1, 1)
            blk = stack[a, f0:f0 + h, c0:c0 + w]
            blk[m] = np.round(ndvi[m] * 10000).astype(np.int16)
            if m.any():
                items_con_datos.add(it["id"])
        capa = stack[a]
        ok = capa != -32768

        def med_zona(mz):
            sel = ok & mz
            if sel.sum() < 0.3 * mz.sum():
                return None
            return round(float(np.median(capa[sel])) / 10000, 4)
        # AOT (Sen2Cor, 550 nm) sobre los píxeles válidos de la zona
        f20, v20 = fuente10[::2, ::2], valido10[::2, ::2] & d20
        vals = []
        for k, it in enumerate(grupo):
            ra = os.path.join(CACHE, it["id"], "aot.npy")
            if os.path.exists(ra):
                aa = np.load(ra)
                vals.append(aa[v20 & (f20 == k) & (aa > 0)])
        vals = np.concatenate(vals) if vals else np.array([])
        serie.append({"adquisicion": cl, "fecha": cl[:10], "plataforma": "Sentinel-" + cl[11:13], "orbita_relativa": cl[14:],
                      "items": resumen[cl]["items"], "nubosidad_tesela_min": resumen[cl]["nubosidad_tesela_min"],
                      "frac_valida_scl": resumen[cl]["frac_valida"],
                      "frac_usada": round(float((ok & dentro).sum() / dentro.sum()), 4),
                      "ndvi_mediana_cabecera": med_zona(urb10), "ndvi_mediana_rural_rejilla": med_zona(m_rur10),
                      "aot_mediana": round(float(np.median(vals)) * AOT_ESCALA, 3) if vals.size > 1000 else None,
                      "frac_veg_rojo_menor_0_1": round(veg_bajo / veg_n, 4) if veg_n > 1000 else None})

    # ---- escenas con AOT atípico (criterio propio: > Q3 + 1,5·IQR de las fechas)
    aots = np.array([s["aot_mediana"] for s in serie if s["aot_mediana"] is not None])
    if aots.size < 10:
        raise RuntimeError(f"AOT disponible solo en {aots.size} fechas: ejecute sin --sin-descarga para leer el asset 'aot'")
    q1, q3 = np.percentile(aots, [25, 75])
    aot_lim = float(q3 + 1.5 * (q3 - q1))
    for s in serie:
        s["aot_atipico"] = None if s["aot_mediana"] is None else bool(s["aot_mediana"] > aot_lim)
    marca = np.array([bool(s["aot_atipico"]) for s in serie])

    def corr(xk, yk):
        p = [(s[xk], s[yk]) for s in serie if s[xk] is not None and s[yk] is not None]
        if len(p) < 5:
            return None
        x, y = np.array(p).T
        return {"r": round(float(np.corrcoef(x, y)[0, 1]), 3), "fechas": len(p)}
    diag_aot = {"aot_por_fecha": {"min": _r(aots.min()), "p25": _r(q1), "mediana": _r(np.median(aots)), "p75": _r(q3), "max": _r(aots.max()),
                                  "fechas": int(aots.size)},
                "limite_atipico": round(aot_lim, 3), "criterio": "AOT mediano de la zona > Q3 + 1,5·IQR de las fechas (regla de Tukey; criterio propio)",
                "fechas_atipicas": [{"fecha": s["fecha"], "aot": s["aot_mediana"], "ndvi_rural": s["ndvi_mediana_rural_rejilla"]}
                                    for s in serie if s["aot_atipico"]],
                "correlacion_ndvi_rural_vs_aot": corr("aot_mediana", "ndvi_mediana_rural_rejilla"),
                "correlacion_ndvi_rural_vs_frac_veg_rojo_menor_0_1": corr("frac_veg_rojo_menor_0_1", "ndvi_mediana_rural_rejilla"),
                "correlacion_aot_vs_frac_veg_rojo_menor_0_1": corr("aot_mediana", "frac_veg_rojo_menor_0_1")}
    log("AOT:", json.dumps(diag_aot, ensure_ascii=False)[:900])

    # ---- evidencia del offset
    rv = np.concatenate(dn_rojo_veg) if dn_rojo_veg else np.array([])
    na = np.concatenate(dn_nir_agua) if dn_nir_agua else np.array([])
    evid = {"dn_rojo_vegetacion_scl4": {"p01": float(np.percentile(rv, 1)), "p50": float(np.median(rv)), "p99": float(np.percentile(rv, 99)),
                                        "frac_menor_1000": round(float((rv < 1000).mean()), 5), "muestras": int(rv.size)} if rv.size else None,
            "dn_nir_agua_scl6_sin_censurados": {"p01": float(np.percentile(na, 1)), "p50": float(np.median(na)), "p99": float(np.percentile(na, 99)),
                                                "frac_menor_1000": round(float((na < 1000).mean()), 5), "muestras": int(na.size)} if na.size else None,
            "censura_dn_1": dict(censura, frac_censurados=round(censura["censurados"] / max(1, censura["validos_scl"]), 5),
                                 frac_censurados_agua=round(censura["censurados_agua_scl6"] / max(1, censura["validos_agua_scl6"]), 4),
                                 frac_rojo_censurado_tierra=round(censura["censurados_tierra_rojo"] / max(1, censura["validos_tierra_scl4_5"]), 5))}
    evid["prueba_fisica_por_item"] = {
        "criterio": "fracción de píxeles SCL 4 (vegetación) con DN rojo < 1000: > 0,5 ⇒ offset ya restado en el COG; < 0,02 ⇒ DN originales de ESA (+1000)",
        "items": len(pruebas), "coinciden_con_bandera": sum(1 for p in pruebas if p["coincide"] is True),
        "contradicen_bandera": [p for p in pruebas if p["coincide"] is False],
        "sin_veredicto": [p["item"] for p in pruebas if p["coincide"] is None],
        "bandera_false": [p for p in pruebas if p["boa_offset_applied"] is False]}
    comun.guardar_json(os.path.join(DIR, "pruebas_offset.json"), pruebas)
    comp = os.path.join(DIR, "comparacion_pc.json")
    if os.path.exists(comp):
        evid["comparacion_planetary_computer"] = json.load(open(comp, encoding="utf-8"))
    log("evidencia offset:", json.dumps(evid, ensure_ascii=False)[:700])

    # ---- lluvia CHIRPS (diagnóstico): meses con la lluvia acumulada de los 2 meses previos en el tercil más bajo
    lluvia, normal = lluvia_chirps()
    diag_lluvia, sel_baja = None, None
    if lluvia:
        meses24 = [f"{a}-{m:02d}" for a in (2024, 2025) for m in range(1, 13)]
        p2 = {k: lluvia[mes_previo(k, 1)] + lluvia[mes_previo(k, 2)] for k in meses24
              if mes_previo(k, 1) in lluvia and mes_previo(k, 2) in lluvia}
        lim_p2 = float(np.percentile(list(p2.values()), 100 / 3))
        meses_baja = sorted(k for k, v in p2.items() if v <= lim_p2)
        sel_baja = np.array([cl[:7] in meses_baja for cl in claves])
        ym = defaultdict(list)
        for x in serie:
            if x["ndvi_mediana_rural_rejilla"] is not None:
                ym[x["fecha"][:7]].append(x["ndvi_mediana_rural_rejilla"])
        kk = sorted(k for k in ym if all(mes_previo(k, l) in lluvia for l in range(4)))
        nd = np.array([np.median(ym[k]) for k in kk])
        corr_l = {}
        for l in range(4):
            corr_l[f"lluvia_mes_menos_{l}"] = round(float(np.corrcoef([lluvia[mes_previo(k, l)] for k in kk], nd)[0, 1]), 3)
        corr_l["lluvia_acumulada_meses_menos_1_y_2"] = round(float(np.corrcoef([lluvia[mes_previo(k, 1)] + lluvia[mes_previo(k, 2)] for k in kk], nd)[0, 1]), 3)
        ventana_humeda = [{"mes": k, "lluvia_mm": round(lluvia[k], 1), "normal_1991_2020_mm": round(normal[int(k[5:7]) - 1], 1)}
                          for k in meses24 if int(k[5:7]) in MESES_SECOS and k in lluvia and lluvia[k] > normal[int(k[5:7]) - 1]]
        seco_mm = [lluvia[k] for k in meses24 if k in lluvia and int(k[5:7]) in MESES_SECOS]
        otro_mm = [lluvia[k] for k in meses24 if k in lluvia and int(k[5:7]) not in MESES_SECOS]
        diag_lluvia = {
            "fuente": {"nombre": "CHIRPS v3.0 mensual (Climate Hazards Center, UCSB), media sobre la huella urbana; tomado del producto 'clima' de BioMap Cartago (datos/series/clima.json)",
                       "url": "https://www.chc.ucsb.edu/data/chirps3", "licencia": "CC BY 4.0",
                       "cita": "Funk, C., Peterson, P., Harrison, L. et al. (2026). The Climate Hazards Center Infrared Precipitation with Stations, Version 3. Scientific Data 13, 718. doi:10.1038/s41597-026-07096-4"},
            "correlacion_ndvi_rural_mensual_vs_lluvia": dict(corr_l, meses=len(kk),
                                                             nota="NDVI rural = mediana de las fechas de cada año-mes; 24 meses: indicativo"),
            "lluvia_media_mensual_2024_2025_mm": {"meses_secos_calendario": round(float(np.mean(seco_mm)), 1), "otros_meses": round(float(np.mean(otro_mm)), 1)},
            "lluvia_media_mensual_normal_1991_2020_mm": {"meses_secos_calendario": round(float(np.mean([normal[m - 1] for m in MESES_SECOS])), 1),
                                                         "otros_meses": round(float(np.mean([normal[m - 1] for m in range(1, 13) if m not in MESES_SECOS])), 1)},
            "meses_secos_calendario_mas_lluviosos_que_su_normal": ventana_humeda,
            "tras_lluvia_baja": {"criterio": f"meses cuya lluvia acumulada de los 2 meses previos ≤ {lim_p2:.0f} mm (tercil inferior de 2024–2025; criterio propio)",
                                 "meses": meses_baja, "adquisiciones": int(sel_baja.sum())},
        }
        log("lluvia CHIRPS:", json.dumps(diag_lluvia, ensure_ascii=False)[:900])

    # ---- medianas a 10 m (anual, seco, post-seco y anual sin escenas de AOT atípico)
    todas = np.ones(len(claves), bool)
    med, n = mediana_por_franjas(stack, todas, N_MIN)
    seco = np.isin(meses, MESES_SECOS)
    med_s, n_s = mediana_por_franjas(stack, seco, N_MIN_SECO)
    post = np.isin(meses, MESES_POST_SECO)
    med_p, _ = mediana_por_franjas(stack, post, N_MIN_SECO)
    med_a, _ = mediana_por_franjas(stack, ~marca, N_MIN) if marca.any() else (med, n)
    med_b = mediana_por_franjas(stack, sel_baja, N_MIN_SECO)[0] if sel_baja is not None and sel_baja.any() else None
    del stack
    aporta, aporta_s = np.isfinite(med), np.isfinite(med_s)
    with np.errstate(all="ignore"):
        frac_seco_px = np.where(aporta & (n > 0), n_s / np.maximum(n, 1), np.nan)
    sens = med_a - med
    sens_d = sens[dentro & np.isfinite(sens)]
    sensibilidad_aot = {"escenas_excluidas": int(marca.sum()),
                        "dif_ndvi_10m_sin_menos_con": {"p01": _r(np.percentile(sens_d, 1), 4), "mediana": _r(np.median(sens_d), 4),
                                                        "p99": _r(np.percentile(sens_d, 99), 4),
                                                        "frac_abs_mayor_0_02": _r(np.mean(np.abs(sens_d) > 0.02), 4)} if sens_d.size else None}
    log(f"10 m: píxeles con mediana {aporta[dentro].mean():.4f}; N mediano {np.median(n[dentro & aporta]):.0f} "
        f"(p5 {np.percentile(n[dentro & aporta], 5):.0f}); seco: {seco.sum()} adquisiciones, N mediano {np.median(n_s[dentro & aporta_s]):.0f}; "
        f"fracción de observaciones en meses secos (mediana por píxel) {np.nanmedian(frac_seco_px[dentro]):.3f}; sensibilidad AOT {sensibilidad_aot}")

    # ---- a la rejilla común (N: solo píxeles que aportan mediana)
    rep = lambda x: comun.reproyectar(x.astype(np.float32), R["transform"], CRS_UTM, "average")  # noqa: E731
    ndvi, ndvi_s, ndvi_p = rep(med), rep(med_s), rep(med_p)
    ndvi_b = rep(med_b) if med_b is not None else None
    ndvi_n = rep(np.where(aporta, n, np.nan))
    ndvi_s_n = rep(np.where(aporta_s, n_s, np.nan))
    frac_aporta = rep(aporta.astype(np.float32))
    frac_aporta_s = rep(aporta_s.astype(np.float32))
    frac_seco = rep(frac_seco_px)
    np.save(os.path.join(comun.REJILLA_NPY, "ndvi_seco_n.npy"), ndvi_s_n.astype(np.float32))
    np.save(os.path.join(comun.REJILLA_NPY, "ndvi_frac_aporta.npy"), frac_aporta.astype(np.float32))

    fechas = [s["fecha"] for s in serie]
    items_sel = sorted({i for cl in claves for i in resumen[cl]["items"]})
    clases_usadas = np.zeros(12, np.int64)
    for cl in claves:
        for c, v in resumen[cl]["clases"].items():
            clases_usadas[int(c)] += v
    clases_consid = np.zeros(12, np.int64)
    for r in resumen.values():
        for c, v in r["clases"].items():
            clases_consid[int(c)] += v
    pc_us, pc_con = pct_clases(clases_usadas), pct_clases(clases_consid)
    urb_r = comun.mascara_urbana()
    fuente = {"nombre": "Copernicus Sentinel-2 L2A (ESA/UE), COG de Element 84 en AWS Open Data (Earth Search)",
              "url": "https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a",
              "licencia": "Datos Copernicus Sentinel: acceso libre y abierto (Aviso legal de uso de datos Sentinel de Copernicus; Reglamento Delegado (UE) 1159/2013)",
              "cita": f"Contiene datos modificados de Copernicus Sentinel [{fechas[0][:4]}–{fechas[-1][:4]}], procesados por BioMap Cartago"}
    tope = (f"hasta {seleccion['por_mes']} por mes (las más despejadas)" if seleccion["por_mes"] else "todas")
    n_mes = {m: int((meses == m).sum()) for m in range(1, 13)}
    proc_comun = [
        f"Catálogo STAC de Earth Search (colección sentinel-2-l2a), {PERIODO}, sin filtro de nubes en la consulta: {seleccion['items_catalogo']} items de las teselas MGRS 18NUL y 18NVL. "
        f"Se consideran los {seleccion['items_considerados']} con nubosidad de tesela < {seleccion['nubes_max_tesela']:g} % (eo:cloud_cover se calcula sobre la tesela de 110 km, de la que la zona es ≈ 1,4 %); la selección real la hace la SCL local. "
        "Lista de IDs versionada en scripts/sentinel2_items.json.",
        f"Mosaico por adquisición de las dos teselas y de los datastrips de una misma tesela, con 18NUL primero y, dentro de cada tesela, el item que más cubre la zona: {seleccion['disponibles']} adquisiciones (plataforma+fecha+órbita) con dato en la zona. "
        "Cuando una tesela tiene dos items el mismo día (_0 y _1/_2) son datastrips distintos de la misma pasada (distinto datastrip_id y hora de inicio), no reprocesos; en la zona se solapan con 95–99 % de acuerdo en la SCL, y tomar el que más cubre evita costuras entre dos corridas de Sen2Cor.",
        f"Máscara SCL (20 m, ampliada a 10 m): válidas las clases {list(SCL_VALIDAS)} (vegetación, no vegetado, agua); se descartan 0–3 y 8–11. La clase 7 (sin clasificar, «clouds low probability / unclassified» en la documentación de Copernicus) también se descarta: es el {pc_us['sin_clasificar_7']} % de las observaciones (clases 1–11) de las adquisiciones usadas, así que la decisión casi no cambia el resultado.",
        f"Además se descartan los píxeles a menos de {BUFFER_NUBE_M} m de nube, sombra de nube o cirro (clases 3, 8, 9, 10), porque los bordes de nube suelen escapar a la SCL (criterio propio).",
        f"Se usan {tope} las adquisiciones cuya parte de la zona cubierta tenga ≥ {int(seleccion['frac_min'] * 100)} % de píxeles válidos: {seleccion['seleccionadas']} de {seleccion['disponibles']}; {seleccion['completas']} descargadas por completo y usadas. Fechas por mes calendario (2024+2025): {n_mes}.",
        f"Solo se descargaron los bloques internos del COG (1024×1024 px) con al menos {seleccion['umbral_bloque']} píxeles válidos en la zona (red lenta); los demás píxeles de esas escenas no se usan. "
        f"{len(items_con_datos)} items aportaron píxeles, de {len(items_sel)} items en las adquisiciones usadas (el resto solo cubre zonas nubladas o ya cubiertas por el otro item de la misma pasada).",
        "Reflectancia = DN × 0,0001. Los productos son baseline 05.10/05.11 (BOA_ADD_OFFSET = −1000 en sus metadatos de ESA), pero Earth Search ya restó ese offset a los DN de los COG (propiedad earthsearch:boa_offset_applied = true), aunque 'raster:bands' sigue declarando offset −0,1: aplicarlo restaría dos veces. Se verificó por item (DN del rojo en vegetación) y contra Planetary Computer; si un COG conservara los DN originales se usaría DN × 0,0001 − 0,1. Ver 'evidencia_offset'.",
        f"Los COG de Earth Search recortan a DN = 1 las reflectancias que tras el offset serían ≤ 0 (comparación con Planetary Computer: DN 931 → 1). DN ≤ 1 en B04 o B08 se trata como dato censurado y se descarta: {100 * evid['censura_dn_1']['frac_censurados']:.2f} % de los píxeles válidos por SCL, {100 * evid['censura_dn_1']['frac_censurados_agua']:.1f} % de los de agua (SCL 6).",
        "NDVI = (B08 − B04)/(B08 + B04) por escena a 10 m; se descartan píxeles con reflectancia ≤ 0 en alguna banda.",
        f"Bruma: se calcula el AOT de Sen2Cor (asset 'aot', 550 nm; el COG es de 60 m aunque el STAC declare 20 m, y se lee con su propia georreferenciación) mediano de cada fecha (rango {diag_aot['aot_por_fecha']['min']}–{diag_aot['aot_por_fecha']['max']}). "
        + (f"{len(diag_aot['fechas_atipicas'])} fechas superan Q3 + 1,5·IQR ({diag_aot['limite_atipico']}; criterio propio) y se marcan en la serie, pero no se excluyen: quitarlas cambia el NDVI de 10 m en una mediana de {sensibilidad_aot['dif_ndvi_10m_sin_menos_con']['mediana']} (ver 'sensibilidad_aot')."
           if diag_aot["fechas_atipicas"] else
           f"Ninguna fecha supera Q3 + 1,5·IQR ({diag_aot['limite_atipico']}; criterio propio), así que no se excluye ninguna escena por bruma. "
           f"El AOT no explica bien las fechas de NDVI bajo (r = {diag_aot['correlacion_ndvi_rural_vs_aot']['r']} con el NDVI rural por fecha)."),
    ]
    frac_seco_med = float(np.nanmedian(frac_seco[np.isfinite(frac_seco)]))
    _, lon_c = comun.centros_celdas()
    n_oeste, n_este = float(np.nanmedian(ndvi_n[lon_c < -75.93])), float(np.nanmedian(ndvi_n[lon_c > -75.88]))
    lim_comun = [
        "Mediana de reflectancia de superficie Sen2Cor sin corrección BRDF ni armonización entre S2A, S2B y S2C; NDVI mide verdor, no es lo mismo que cobertura arbórea.",
        "La máscara SCL de Sen2Cor puede dejar pasar bruma y sombras finas; la mediana y el margen de 40 m reducen, pero no eliminan, ese efecto. El AOT de Sen2Cor no detecta toda la bruma o el humo (p. ej., de quemas).",
        "Cada celda de ≈ 27,7 m promedia ≈ 7,7 píxeles de 10 m: en el cauce del río y en calles arboladas se mezclan agua, vegetación y techos.",
        f"El número de observaciones no es uniforme (capa ndvi_n): baja de oeste a este (N mediano {n_oeste:.0f} al occidente de −75,93° y {n_este:.0f} al oriente de −75,88°) porque el borde de la franja de barrido de la órbita relativa 068 cruza la zona y solo las pasadas de la órbita 025 la cubren entera; también es menor en el agua (reflectancias censuradas) y junto a techos muy brillantes confundidos con nube.",
        f"Los meses lluviosos aportan menos fechas despejadas: en el píxel típico el {100 * frac_seco_med:.0f} % de las observaciones son de meses de temporada seca (dic–feb, jun–ago, que son la mitad del año); la mediana pesa algo más esas épocas.",
        f"En el agua se descartan las observaciones con reflectancia censurada (DN ≤ 1, {100 * evid['censura_dn_1']['frac_censurados_agua']:.0f} % de las de SCL 6, casi todas por el NIR: {evid['censura_dn_1']['censurados_agua_nir']} de {evid['censura_dn_1']['censurados_agua_scl6']}): las que quedan tienen NIR algo mayor, así que el NDVI del agua queda sesgado hacia valores menos negativos. "
        f"En tierra (SCL 4–5) el rojo está censurado en el {100 * evid['censura_dn_1']['frac_rojo_censurado_tierra']:.2f} % de las observaciones (vegetación muy oscura); descartarlas baja muy poco el NDVI de esas zonas.",
    ]
    clase7 = {"pct_observaciones_usadas": pc_us["sin_clasificar_7"],
              "pct_observaciones_consideradas": pc_con["sin_clasificar_7"],
              "nota": "porcentajes sobre las observaciones (clases 1–11), sin la clase 0 (sin dato o fuera de la pasada)",
              "decision": "excluida"}
    paleta = ["#8c6d31", "#d6c27c", "#c3df8f", "#5aa95a", "#1b5e20"]
    interp = ("Umbrales orientativos del USGS («NDVI, the Foundation for Remote Sensing Phenology»): ≤ 0,1 roca, arena o superficies sin "
              "vegetación (en la ciudad: techos, pavimento, agua); ≈ 0,2–0,5 vegetación dispersa, pastos o cultivos en senescencia; "
              "≈ 0,6–0,9 vegetación densa (bosques, cultivos en pleno desarrollo). Son rangos generales, no calibrados para Cartago.")
    nstat = lambda x: {"min": round(float(np.nanmin(x)), 1), "p5": round(float(np.nanpercentile(x, 5)), 1),  # noqa: E731
                       "mediana": round(float(np.nanmedian(x)), 1), "max": round(float(np.nanmax(x)), 1),
                       "celdas_menor_10": int(np.sum(x < 10)), "celdas_menor_20": int(np.sum(x < 20))}

    meta = {
        "titulo": "Vegetación (NDVI) 2024–2025",
        "descripcion": "Verdor de la vegetación medido por los satélites Sentinel-2 entre 2024 y 2025 (valor típico de todas las fechas sin nubes). Valores altos: árboles y cultivos vigorosos; valores bajos: techos, pavimento, suelo desnudo o agua.",
        "unidad": "NDVI (adimensional, −1 a 1)",
        "fuente": fuente,
        "periodo": f"{fechas[0]} a {fechas[-1]} ({len(claves)} adquisiciones con datos)",
        "resolucion_original_m": 10,
        "procesamiento": proc_comun + [
            f"Mediana por píxel de 10 m de todas las escenas válidas; se exige N ≥ {N_MIN} observaciones.",
            "Promedio ponderado por área (GDAL «average») a la rejilla común de 0,00025° (≈ 27,7 m).",
        ],
        "limitaciones": lim_comun,
        "rango_visual": [0.0, 0.9],
        "paleta": paleta,
        "interpretacion": interp,
        "observaciones_por_celda": "capa publicada datos/capas/ndvi_n.png (media de N de los píxeles de 10 m que aportan valor)",
        "evidencia_offset": evid,
        "clase_7": clase7,
        "clases_scl_pct_observaciones": {"adquisiciones_usadas": pc_us, "adquisiciones_consideradas": pc_con},
        "aot": diag_aot,
        "sensibilidad_aot": sensibilidad_aot,
        "fechas_por_mes": n_mes,
        "items_stac": {"catalogo": seleccion["items_catalogo"], "considerados": seleccion["items_considerados"],
                       "en_adquisiciones_usadas": len(items_sel), "con_datos_usados": len(items_con_datos),
                       "manifiesto": "scripts/sentinel2_items.json"},
        "seleccion": seleccion,
        "n_obs_celda": nstat(ndvi_n),
    }
    est = comun.guardar_capa("ndvi", ndvi, 0.0001, -1, meta)
    log("ndvi:", json.dumps(est, ensure_ascii=False))

    # ---- capa de observaciones por celda
    fa = frac_aporta[np.isfinite(frac_aporta)]
    p99 = float(np.nanpercentile(ndvi_n, 99))
    meta_n = {
        "titulo": "Observaciones válidas del NDVI 2024–2025",
        "descripcion": "Cuántas fechas sin nubes de Sentinel-2 sostienen el valor de NDVI de cada celda. Más fechas significa un valor más estable; pocas fechas, más incertidumbre.",
        "unidad": "número de adquisiciones (media de los píxeles de 10 m de la celda)",
        "fuente": fuente,
        "periodo": meta["periodo"],
        "resolucion_original_m": 10,
        "procesamiento": proc_comun + [
            f"N por píxel de 10 m = número de adquisiciones con NDVI válido; solo cuentan los píxeles con N ≥ {N_MIN} (los que aportan mediana a la capa ndvi).",
            "Promedio ponderado por área (GDAL «average») a la rejilla común; los píxeles de 10 m que no aportan quedan fuera del promedio.",
            "Fracción de píxeles de 10 m de la celda que aportan: ver 'fraccion_pixeles_aportan' (fuentes/rejilla/ndvi_frac_aporta.npy).",
        ],
        "limitaciones": lim_comun[3:5] + ["Es una medida de cantidad de datos, no de error: no incluye la variabilidad entre fechas ni los errores de la SCL."],
        "rango_visual": [0.0, float(np.ceil(p99 / 10) * 10)],
        "paleta": ["#f7fbff", "#c6dbef", "#6baed6", "#2171b5", "#08306b"],
        "interpretacion": f"No hay un umbral normativo. En este producto un píxel de 10 m necesita N ≥ {N_MIN} para tener mediana (criterio propio); con N bajo la mediana es más sensible a una sola fecha con bruma o nube no detectada.",
        "n_obs_celda": nstat(ndvi_n),
        "fraccion_pixeles_aportan": {"mediana": _r(np.median(fa)), "min": _r(fa.min()), "celdas_menor_1": int((fa < 0.999).sum()),
                                     "celdas_menor_0_5": int((fa < 0.5).sum())},
        "seco": {"n_obs_celda": nstat(ndvi_s_n), "archivo": "fuentes/rejilla/ndvi_seco_n.npy (no publicado)"},
    }
    est_n = comun.guardar_capa("ndvi_n", ndvi_n, 0.01, 0, meta_n)
    log("ndvi_n:", json.dumps(est_n, ensure_ascii=False))

    def dif_stats(x):
        dif = x - ndvi

        def q(m):
            d = dif[m & np.isfinite(dif)]
            return {"p10": round(float(np.percentile(d, 10)), 3), "mediana": round(float(np.median(d)), 3), "p90": round(float(np.percentile(d, 90)), 3),
                    "frac_menor_-0_05": round(float(np.mean(d < -0.05)), 4), "frac_mayor_0_05": round(float(np.mean(d > 0.05)), 4)}
        return {"cabecera": q(urb_r), "fuera_de_la_cabecera": q(~urb_r)}

    hay_seco = bool(np.isfinite(ndvi_s).mean() >= 0.9)
    dif_seco = dif_stats(ndvi_s) if hay_seco else None
    dif_post = dif_stats(ndvi_p) if np.isfinite(ndvi_p).mean() >= 0.9 else None
    if diag_lluvia is not None and ndvi_b is not None:
        diag_lluvia["tras_lluvia_baja"]["cobertura_pct"] = round(100 * float(np.isfinite(ndvi_b).mean()), 2)
        diag_lluvia["tras_lluvia_baja"]["diferencia_con_anual"] = dif_stats(ndvi_b)
        diag_lluvia["tras_lluvia_baja"]["uso"] = "diagnóstico exploratorio; no se publica como capa"
    est_s = None
    if hay_seco:
        cob_s = round(100 * float(np.isfinite(ndvi_s).mean()), 4)
        meta_s = dict(meta)
        for k in ("observaciones_por_celda", "n_obs_celda"):
            meta_s.pop(k, None)
        meta_s.update({
            "titulo": "Vegetación (NDVI) en meses de temporada seca 2024–2025",
            "descripcion": ("Verdor típico de la vegetación en los meses de temporada seca del calendario (diciembre–febrero y junio–agosto) de 2024 y 2025. "
                            + ("En esos dos años casi no se diferencia de la capa anual (varios de esos meses llovieron más de lo normal y el verdor responde a la lluvia con uno o dos meses de retraso), "
                               if diag_lluvia else "En esos dos años casi no se diferencia de la capa anual, ")
                            + "así que no sirve para señalar zonas que pierden verdor por falta de lluvia."),
            "periodo": f"meses 12, 1, 2, 6, 7 y 8 entre {fechas[0]} y {fechas[-1]} ({int(seco.sum())} adquisiciones)",
            "procesamiento": proc_comun + [
                "Solo adquisiciones de diciembre–febrero y junio–agosto: aproximación por meses calendario de las dos temporadas secas del valle del río Cauca "
                "(16 dic–15 feb y 16 jun–26 ago según Cortés y Barrios, Cenicaña, Carta Trimestral 3-4/2010; 14 estaciones del valle cañero; se asume válido para Cartago).",
                f"Mediana por píxel de 10 m; se exige N ≥ {N_MIN_SECO} observaciones.",
                "Promedio ponderado por área (GDAL «average») a la rejilla común de 0,00025° (≈ 27,7 m).",
            ],
            "limitaciones": lim_comun + [
                "Menos observaciones que la capa anual (resumen en 'n_obs_celda_seco'); 2024 y 2025 no fueron años climáticamente idénticos.",
                f"No muestra contraste estacional en 2024–2025: frente a la capa anual la diferencia mediana es {dif_seco['fuera_de_la_cabecera']['mediana']:+.3f} fuera de la cabecera y {dif_seco['cabecera']['mediana']:+.3f} en ella; "
                f"solo el {100 * dif_seco['fuera_de_la_cabecera']['frac_menor_-0_05']:.1f} % de las celdas rurales baja más de 0,05 y el {100 * dif_seco['fuera_de_la_cabecera']['frac_mayor_0_05']:.1f} % sube más de 0,05. No es una capa de estrés hídrico.",
                f"La capa anual ya está cargada hacia los meses secos (en el píxel típico el {100 * frac_seco_med:.0f} % de sus observaciones son de esos meses), lo que reduce el contraste.",
            ] + ([
                "Meses calendario sin desfase, aunque el verdor responde con retraso a la lluvia: con CHIRPS v3 (producto 'clima'), el NDVI rural mensual de 2024–2025 se correlaciona "
                f"r = {diag_lluvia['correlacion_ndvi_rural_mensual_vs_lluvia']['lluvia_mes_menos_0']} con la lluvia del mismo mes, "
                f"r = {diag_lluvia['correlacion_ndvi_rural_mensual_vs_lluvia']['lluvia_mes_menos_1']} con la del mes anterior y "
                f"r = {diag_lluvia['correlacion_ndvi_rural_mensual_vs_lluvia']['lluvia_acumulada_meses_menos_1_y_2']} con la acumulada de los dos meses previos "
                f"({diag_lluvia['correlacion_ndvi_rural_mensual_vs_lluvia']['meses']} meses; indicativo). Ver 'diagnostico_lluvia_chirps'.",
                "Además, en 2024–2025 varios meses de la ventana seca llovieron más que su normal 1991–2020 (CHIRPS): "
                + ", ".join(f"{v['mes']} {v['lluvia_mm']:.0f} mm (normal {v['normal_1991_2020_mm']:.0f})" for v in diag_lluvia["meses_secos_calendario_mas_lluviosos_que_su_normal"]) + ".",
            ] if diag_lluvia else [
                "Meses calendario sin desfase: si la vegetación responde con retraso a la lluvia (supuesto, no verificado con datos locales), el mínimo de verdor caería después de cada temporada seca.",
            ]),
            "diferencia_con_anual": dif_seco,
            "diagnostico_lluvia_chirps": diag_lluvia,
            "ventana_posterior_seca": {"meses": list(MESES_POST_SECO), "adquisiciones": int(post.sum()),
                                       "fundamento": "transiciones tras las temporadas secas: 16 feb–25 mar y 27 ago–5 oct (Cenicaña 2010); aproximadas por meses calendario",
                                       "diferencia_con_anual": dif_post,
                                       "uso": "diagnóstico exploratorio; no se publica como capa"},
            "n_obs_celda_seco": nstat(ndvi_s_n),
            "fraccion_pixeles_aportan": {"mediana": _r(np.nanmedian(frac_aporta_s)), "min": _r(np.nanmin(frac_aporta_s))},
            "cobertura_real_pct": cob_s,
        })
        est_s = comun.guardar_capa("ndvi_seco", ndvi_s, 0.0001, -1, meta_s)
        log("ndvi_seco:", json.dumps(est_s, ensure_ascii=False))
        log("diferencias seco:", json.dumps(dif_seco), "post-seco:", json.dumps(dif_post))
    else:
        log(f"ndvi_seco NO se publica: solo {np.isfinite(ndvi_s).mean():.1%} de celdas con N ≥ {N_MIN_SECO}")

    # ---- hallazgos y verificaciones
    M = mascaras_rejilla()
    zonas = comun.comunas()
    mz = comun.mascara_zonas(zonas)

    def st(x, m):
        v = x[m & np.isfinite(x)]
        return None if v.size == 0 else {"mediana": round(float(np.median(v)), 3), "p10": round(float(np.percentile(v, 10)), 3),
                                          "p90": round(float(np.percentile(v, 90)), 3), "celdas": int(v.size)}
    hall = {"anual": {k: st(ndvi, m) for k, m in M.items()},
            "seco": {k: st(ndvi_s, m) for k, m in M.items()} if hay_seco else None,
            "post_seco": {k: st(ndvi_p, m) for k, m in M.items()},
            "por_zona": {z["nombre"]: st(ndvi, mz == z["indice"]) for z in zonas},
            "n_obs": {k: st(ndvi_n, m) for k, m in M.items()},
            "n_obs_seco": {k: st(ndvi_s_n, m) for k, m in M.items()}}
    ver = {"ndvi": verificar("ndvi", ndvi, json.load(open(os.path.join(comun.CAPAS, "ndvi.json"), encoding="utf-8"))),
           "ndvi_n": verificar("ndvi_n", ndvi_n, json.load(open(os.path.join(comun.CAPAS, "ndvi_n.json"), encoding="utf-8")), puntos=False)}
    if hay_seco:
        ver["ndvi_seco"] = verificar("ndvi_seco", ndvi_s, json.load(open(os.path.join(comun.CAPAS, "ndvi_seco.json"), encoding="utf-8")))
    # río: eje (≤ 30 m) vs franja 30–200 m
    from pyproj import Transformer
    from shapely.ops import transform as stransform
    from shapely.geometry import LineString, Point
    from rasterio.features import rasterize
    a_utm = Transformer.from_crs(comun.CRS, CRS_UTM, always_xy=True).transform
    a_geo = Transformer.from_crs(CRS_UTM, comun.CRS, always_xy=True).transform
    rio = stransform(a_utm, comun.lineas_rio())
    cauca = stransform(a_utm, comun.lineas_rio("rio_cauca"))
    kw = dict(out_shape=(comun.ALTO, comun.ANCHO), transform=comun.transformacion(), fill=0, dtype="uint8")
    eje = rasterize([(stransform(a_geo, rio.buffer(30)), 1)], **kw).astype(bool)
    ver["rio_la_vieja"] = {"eje_30m": st(ndvi, eje), "franja_30_200m": st(ndvi, M["corredor_la_vieja_200m"] & ~eje),
                           "n_obs_eje_30m": st(ndvi_n, eje)}
    d = comun.osm()
    pista = stransform(a_geo, stransform(a_utm, LineString([(lo, la) for la, lo in d["pista"]])).buffer(15))
    ver["poligonos_osm"] = {
        "parque_bolivar": st(ndvi, rasterize([(comun._poligono(d["parque_bolivar"]), 1)], all_touched=True, **kw).astype(bool)),
        "aerodromo": st(ndvi, rasterize([(comun._poligono(d["aerodromo"]), 1)], **kw).astype(bool)),
        "pista_15m": st(ndvi, rasterize([(pista, 1)], all_touched=True, **kw).astype(bool))}
    # ubicación del mínimo de N
    f, c = np.unravel_index(np.nanargmin(ndvi_n), ndvi_n.shape)
    la, lo = comun.NORTE - (f + 0.5) * comun.RES, comun.OESTE + (c + 0.5) * comun.RES
    p = Point(*a_utm(lo, la))
    agua = comun.cargar_capa("agua") if os.path.exists(os.path.join(comun.REJILLA_NPY, "agua.npy")) else None
    ver["minimo_n"] = {"n": round(float(ndvi_n[f, c]), 2), "lat": round(la, 5), "lon": round(lo, 5),
                       "ndvi": _r(ndvi[f, c]), "agua_worldcover_pct": None if agua is None else _r(agua[f, c], 1),
                       "dist_eje_la_vieja_m": round(p.distance(rio)), "dist_eje_cauca_m": round(p.distance(cauca)),
                       "frac_pixeles_aportan": _r(frac_aporta[f, c])}
    if agua is not None:
        ag = agua >= 50
        ver["n_obs_por_agua"] = {"celdas_agua_ge50pct": st(ndvi_n, ag), "resto": st(ndvi_n, ~ag)}
    ver["cobertura_pct"] = {"ndvi": round(100 * float(np.isfinite(ndvi).mean()), 4),
                            "ndvi_seco": round(100 * float(np.isfinite(ndvi_s).mean()), 4),
                            "celdas_nan_ndvi_seco": int((~np.isfinite(ndvi_s)).sum())}

    # ---- serie y resumen mensual (indicativo)
    por_mes = {}
    for m in range(1, 13):
        xs = [s for s in serie if int(s["fecha"][5:7]) == m and s["ndvi_mediana_rural_rejilla"] is not None]
        v = np.array([s["ndvi_mediana_rural_rejilla"] for s in xs])
        va = [s["aot_mediana"] for s in xs if s["aot_mediana"] is not None]
        por_mes[m] = {"fechas": len(xs), "fechas_2024": sum(s["fecha"][:4] == "2024" for s in xs),
                      "fechas_2025": sum(s["fecha"][:4] == "2025" for s in xs),
                      "ndvi_rural_mediana": _r(np.median(v)) if v.size else None,
                      "ndvi_rural_min": _r(v.min()) if v.size else None, "ndvi_rural_max": _r(v.max()) if v.size else None,
                      "aot_mediana": _r(np.median(va)) if va else None}
    orden_aot_marzo = 1 + sum(1 for r in por_mes.values() if r["aot_mediana"] is not None and por_mes[3]["aot_mediana"] is not None
                              and r["aot_mediana"] > por_mes[3]["aot_mediana"])
    serie_doc = {"titulo": "NDVI por adquisición Sentinel-2 (2024–2025)", "fuente": fuente,
                 "descripcion": "Mediana del NDVI de cada adquisición en la cabecera y en el resto de la rejilla, solo si la escena dejó ver ≥ 30 % de la zona. Cifras por escena: sensibles a nubes residuales, bruma y humo.",
                 "nota_robustez": (f"Solo dos años y entre {min(r['fechas'] for r in por_mes.values())} y {max(r['fechas'] for r in por_mes.values())} fechas por mes calendario: "
                                   "el patrón mensual es indicativo, no un ciclo estacional establecido. Las fechas con NDVI bajo pueden reflejar senescencia o cosecha real, "
                                   "pero también bruma o humo que la SCL no detecta; 'aot_mediana' y 'frac_veg_rojo_menor_0_1' ayudan a distinguirlo, sin resolverlo. "
                                   f"Correlaciones entre fechas: NDVI rural vs AOT r = {diag_aot['correlacion_ndvi_rural_vs_aot']['r']}; "
                                   f"NDVI rural vs fracción de vegetación con rojo < 0,1 r = {diag_aot['correlacion_ndvi_rural_vs_frac_veg_rojo_menor_0_1']['r']}. "
                                   f"El AOT mediano de marzo ({por_mes[3]['aot_mediana']}) es el {orden_aot_marzo}.º más alto de los 12 meses (mediana de todas las fechas {diag_aot['aot_por_fecha']['mediana']}): "
                                   "el mínimo de NDVI de marzo puede deberse en parte a bruma, sin que el AOT de Sen2Cor permita separarla de la senescencia o la cosecha."),
                 "campos": {"nubosidad_tesela_min": "eo:cloud_cover mínimo de los items de la adquisición (% de la tesela de 110 km, no de la zona)",
                            "frac_valida_scl": "fracción de la rejilla con SCL válida (clases 4–6, fuera del margen de 40 m de nubes)",
                            "frac_usada": "fracción de la rejilla con NDVI calculado (bloques descargados, reflectancias > 0, sin censurados)",
                            "ndvi_mediana_cabecera": "mediana del NDVI de 10 m en la cabecera (null si se vio < 30 % de ella)",
                            "ndvi_mediana_rural_rejilla": "ídem en la rejilla fuera de la cabecera (incluye municipios vecinos)",
                            "aot_mediana": "espesor óptico de aerosoles de Sen2Cor (550 nm) mediano en los píxeles válidos de la zona",
                            "aot_atipico": f"AOT > {round(aot_lim, 3)} (Q3 + 1,5·IQR de las fechas; criterio propio)",
                            "frac_veg_rojo_menor_0_1": "fracción de píxeles SCL 4 (vegetación) con reflectancia roja < 0,1; baja con senescencia, suelo expuesto o bruma"},
                 "resumen_mensual_indicativo": por_mes,
                 "campos_resumen_mensual": {"fechas": "adquisiciones del mes (2024+2025) con mediana rural, es decir, que dejaron ver ≥ 30 % de la zona rural de la rejilla",
                                            "ndvi_rural_mediana": "mediana, entre esas fechas, de 'ndvi_mediana_rural_rejilla'",
                                            "aot_mediana": "mediana, entre esas fechas, de 'aot_mediana'"},
                 "aot": diag_aot,
                 "lluvia_chirps": diag_lluvia,
                 "serie": serie,
                 "no_usadas": [{"adquisicion": cl, "frac_despejada": r["frac_despejada"], "nubosidad_tesela_min": r["nubosidad_tesela_min"]}
                               for cl, r in sorted(resumen.items()) if cl not in disp]}
    comun.guardar_json(os.path.join(SERIES, "sentinel2.json"), serie_doc)

    # ---- manifiesto versionable de items (reconstruye el catálogo exacto)
    comun.guardar_json(MANIFIESTO, {
        "descripcion": "IDs de items STAC (Earth Search, sentinel-2-l2a) usados por scripts/sentinel2.py. 'catalogo': respuesta completa de la consulta "
                       "(bbox de la rejilla común, " + PERIODO + ", sin filtro de nubes); buscar_items() la reconstruye por IDs si falta fuentes/sentinel2/stac_items.json.",
        "stac": STAC_URL, "coleccion": COLECCION, "periodo": PERIODO, "fecha_consulta_o_proceso": date.today().isoformat(),
        "nubes_max_tesela": seleccion["nubes_max_tesela"],
        "catalogo": sorted(i["id"] for i in todos),
        "considerados": sorted(i["id"] for i in considerados),
        "en_adquisiciones_usadas": items_sel,
        "con_datos_usados": sorted(items_con_datos)})

    comun.guardar_json(os.path.join(DIR, "verificacion.json"), {"hallazgos": hall, "verificaciones": ver, "sensibilidad_aot": sensibilidad_aot,
                                                               "frac_obs_meses_secos_mediana": round(frac_seco_med, 4)})
    log("hallazgos:", json.dumps(hall["anual"], ensure_ascii=False))
    log("hallazgos seco:", json.dumps(hall["seco"], ensure_ascii=False))
    log("hallazgos post-seco:", json.dumps(hall["post_seco"], ensure_ascii=False))
    log("por zona:", json.dumps(hall["por_zona"], ensure_ascii=False))
    log("n_obs:", json.dumps(hall["n_obs"], ensure_ascii=False))
    log("por mes:", json.dumps(por_mes, ensure_ascii=False))
    log("verificaciones:", json.dumps(ver, ensure_ascii=False))
    log(f"fin en {(time.time() - t0) / 60:.1f} min")


# ---------------------------------------------------------------- comparación con Planetary Computer

def comparar_pc(item_id="S2B_18NUL_20240830_0_L2A", banda_es="red", banda_pc="B04", sub=None):
    """Lee la misma ventana del mismo producto en Planetary Computer (DN de ESA sin modificar) y la compara."""
    import planetary_computer
    import pystac_client
    items = {i["id"]: i for i in buscar_items()}
    it = items[item_id]
    R = rejilla_utm()
    subs = bloques_item(it, R)
    sub = sub or next(s for s in subs if os.path.exists(ruta_bloque(it, banda_es, s)))
    es = np.load(ruta_bloque(it, banda_es, sub))
    cli = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=planetary_computer.sign_inplace)
    uri = it["properties"]["s2:product_uri"].replace(".SAFE", "")
    p = uri.split("_")
    pc_id = "_".join([p[0], p[1], p[2], p[4], p[5], p[6]])
    pcs = list(cli.search(collections=["sentinel-2-l2a"], ids=[pc_id]).items())
    if not pcs:  # PC puede tener otra fecha de generación del mismo dato: buscar por fecha y tesela
        dia = it["properties"]["datetime"][:10]
        pcs = [x for x in cli.search(collections=["sentinel-2-l2a"], bbox=[comun.OESTE, comun.SUR, comun.ESTE, comun.NORTE],
                                     datetime=f"{dia}/{dia}").items()
               if x.id.startswith("_".join(p[:3])) and p[5] in x.id and p[4] in x.id]
    assert pcs, f"no está en Planetary Computer: {pc_id}"
    pit = pcs[0].to_dict()
    pc_id = pcs[0].id
    pit["assets"]["red"] = pit["assets"][banda_pc]
    # ventana pequeña (256×256) dentro del bloque para ahorrar red
    f0, c0, h, w = sub[:4]
    hh, ww = min(h, 256), min(w, 256)
    pc = leer_en_rejilla(pit, "red", R, 10, sub=(f0, c0, hh, ww))
    a, b = es[:hh, :ww].astype(np.int64), pc.astype(np.int64)
    m = (a > 0) & (b > 0)
    res = {"item_earth_search": item_id, "item_planetary_computer": pc_id, "banda": banda_pc,
           "pixeles": int(m.sum()), "dn_es_p50": float(np.median(a[m])), "dn_pc_p50": float(np.median(b[m])),
           "diferencia_es_menos_pc": {"min": int((a - b)[m].min()), "p50": float(np.median((a - b)[m])), "max": int((a - b)[m].max())},
           "baseline": it["properties"]["s2:processing_baseline"],
           "baseline_pc": pit["properties"].get("s2:processing_baseline"),
           "producto_es": it["properties"]["s2:product_uri"], "producto_pc": pit["properties"].get("s2:product_uri"),
           "earthsearch:boa_offset_applied": it["properties"].get("earthsearch:boa_offset_applied"),
           "raster_bands_es": it["assets"][banda_es].get("raster:bands")}
    log("comparación PC:", res)
    return res


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "--comparar-pc":
    out = []
    for i in sys.argv[2:] or ["S2B_18NUL_20240830_0_L2A", "S2C_18NVL_20250125_0_L2A"]:
        try:
            out.append(comparar_pc(i))
        except Exception as e:  # el producto puede no estar en PC
            log(f"comparación PC no disponible para {i}: {e}")
            out.append({"item_earth_search": i, "error": str(e)[:200]})
    comun.guardar_json(os.path.join(DIR, "comparacion_pc.json"), out)
    sys.exit(0)


if __name__ == "__main__":
    main()
