"""Coberturas del suelo de Cartago a partir de ESA WorldCover 10 m 2021 (v200).

FUENTES
  ESA WorldCover 10 m 2021 v200, tesela N03W078 (3x3 grados, COG en EPSG:4326, 1/12000 grados ≈ 9,3 m).
  https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N03W078_Map.tif
  Licencia: Creative Commons Atribución 4.0 Internacional (CC BY 4.0).
  Cita (verificada en Zenodo y en el Product User Manual v2.0, sección 5.2):
    Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W., Brockmann, C., Kirches, G.,
    Wevers, J., Cartus, O., Santoro, M., Fritz, S., Lesiv, M., Herold, M., Tsendbazar, N.E., Xu, P.,
    Ramoino, F., Arino, O., 2022. ESA WorldCover 10 m 2021 v200. doi:10.5281/zenodo.7254221
  Atribución en mapas (PUM v2.0, 5.2): '© ESA WorldCover project 2021 / Contains modified Copernicus
    Sentinel data (2021) processed by ESA WorldCover consortium'.
  Exactitud global declarada: 76,7 ± 0,5 %; Suramérica 77,9 ± 1,1 % (PUM v2.0, tabla 4).
  Definiciones de clase (PUM v2.0, tabla 3) y limitaciones conocidas, incluida la de 'hard borders' (PUM §4).
  NO se mezcla con WorldCover 2020 v100: el algoritmo cambió y las diferencias no son cambios reales.

  Geometría auxiliar (solo para zonas de resumen y para la huella de Zaragoza):
  - OpenStreetMap (ODbL 1.0, © colaboradores de OpenStreetMap) vía comun.osm(): comunas, cabecera,
    municipio, ejes de los ríos La Vieja y Cauca, Parque Bolívar, pista; nodo de Zaragoza (4.6968, -75.9264).
  - DANE, Marco Geoestadístico Nacional 2024 (servicio ArcGIS REST del Geoportal DANE; CC BY 4.0 según
    'Licencia y condiciones de uso' del Geoportal; cita exigida: "Departamento Administrativo Nacional de
    Estadística - DANE: www.dane.gov.co"): zona urbana (capa 305), sector urbano (246) y municipios (317).
    Se usa como límite independiente de Zaragoza (el sector urbano que contiene el nodo OSM) y para
    saber a qué municipio pertenece la otra orilla del río La Vieja.

  - OpenStreetMap, fuentes/osm-base.json (caché de scripts/osm.py): vías 749764338 + 1126843631 del río La Vieja
    COMPLETAS, para medir longitudes (comun.lineas_rio() está recortado a la rejilla + 0,01°); y
    fuentes/osm-verdes-equipamientos.json: polígonos natural=wetland, para contrastar la clase 90.

  Normas citadas como contexto (texto verificado en el Gestor Normativo de Función Pública):
  Decreto-Ley 2811 de 1974, art. 83 lit. d) (faja paralela al cauce permanente, hasta de 30 m, bien inalienable e
  imprescriptible del Estado; https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=1551);
  Decreto 2245 de 2017, art. 2.2.3.2.3A.2 (adiciona la sección 3A al Decreto 1076 de 2015: la ronda hídrica
  comprende esa faja y el área de protección o conservación aferente; su acotamiento corresponde a la autoridad
  ambiental competente; https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=85056).
  Humedales de Cartago citados como contexto (documentos de la CVC): plan de manejo de la madrevieja La Culebrera
  (https://cvc.gov.co/sites/default/files/2025-04/Plan%20de%20Manejo%20La%20Culebrera.pdf) y boletín sobre la
  madrevieja La Zapata (https://www.cvc.gov.co/2021015).

PASOS
  1. Lee del COG remoto SOLO la ventana que cubre la rejilla común + 0,01° de margen, en trozos
     alineados con los bloques internos de 1024 px, con 6 hilos y reintentos. Cada trozo se guarda
     en fuentes/worldcover/trozos/ (para reanudar tras un corte) y la ventana completa en
     fuentes/worldcover/ (caché; no se publica). Si un trozo falla tras los reintentos, el script
     se detiene sin escribir capas.
  2. Para cada clase (10 arbolado, 20 arbustos, 30 pasto, 40 cultivo, 50 construido, 60 suelo
     desnudo, 80 agua, 90 humedal) crea una máscara binaria (1 = clase, 0 = otra clase, NaN = sin
     dato) y la lleva a la rejilla común (0,00025°) con remuestreo por PROMEDIO (comun.reproyectar).
     Promedio × 100 = % de la celda clasificado en la clase. Como 0,00025° = 3 píxeles exactos de
     WorldCover y los orígenes coinciden, cada celda es la media de 3×3 píxeles (valores múltiplos
     de 100/9 %); se verifica contra ese promedio por bloques exacto.
  3. Descarga (una vez, con caché en fuentes/worldcover/) las capas del MGN 2024 del DANE. Si falla,
     se omiten las zonas y validaciones que dependen de él, sin detener el producto.
  4. Zaragoza: píxeles construidos (clase 50) conectados en 8 direcciones al píxel construido más
     cercano al nodo OSM; se vectoriza, se dilata 30 m (supuesto) y se simplifica 10 m en UTM 18N.
     Se escribe datos/zaragoza.json solo si 0,05 km² <= área <= 3 km². Se informa la sensibilidad
     del área a la dilatación y la coincidencia con el sector urbano del DANE.
  5. Publica 'arbolado', 'construido' y 'agua' con comun.guardar_capa (escala 0,01; unidad %).
     Las demás clases quedan solo como fuentes/rejilla/cob_<clase>.npy con su cob_<clase>.json.
  6. Resúmenes por zona (comunas, Zaragoza con dos límites, cabecera, parte del municipio dentro de la
     rejilla y corredor del río La Vieja separado por orilla) y verificaciones (rangos, puntos de control,
     orientación norte/sur, PNG decodificada vs .npy, múltiplos de 1/9).
  6b. La rejilla cubre solo ~54 % del municipio. Para cifras municipales se lee (con caché en
     fuentes/worldcover/) una ventana ampliada de la MISMA tesela que contiene todo el polígono OSM del
     municipio, se comprueba que coincide píxel a píxel con la ventana de la rejilla en el solape y se
     cuentan píxeles de 10 m: municipio completo, parte fuera y parte dentro de la rejilla (control), y
     orilla de Cartago a ≤ 100 m del eje COMPLETO del La Vieja. No cambia la rejilla ni las capas.
     También: longitud del La Vieja que limita con Cartago (eje completo), clases de WorldCover en los
     humedales OSM y sensibilidad del % construido de Zaragoza al corte supuesto.

Uso: .venv/bin/python scripts/worldcover.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comun  # noqa: E402

URL = ("https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
       "ESA_WorldCover_10m_2021_v200_N03W078_Map.tif")
DIR = os.path.join(comun.FUENTES, "worldcover")
CACHE = os.path.join(DIR, "ESA_WorldCover_10m_2021_v200_N03W078_ventana_cartago.tif")
MARGEN = 0.01  # grados; 0,01 × 12000 = 120 píxeles exactos
# Ventana ampliada que cubre TODO el municipio (polígono OSM + MARGEN). Solo para resúmenes a 10 m
# (zonas «Municipio de Cartago completo» y corredor del La Vieja en todo el tramo limítrofe);
# no cambia la rejilla común ni las capas publicadas.
CACHE_MUN = os.path.join(DIR, "ESA_WorldCover_10m_2021_v200_N03W078_ventana_municipio.tif")
OSM_BASE = os.path.join(comun.FUENTES, "osm-base.json")                     # vías OSM completas (sin recortar)
OSM_VERDES = os.path.join(comun.FUENTES, "osm-verdes-equipamientos.json")   # incluye natural=wetland
VIAS_LA_VIEJA = (749764338, 1126843631)  # vías OSM del eje del río La Vieja (las mismas que usa scripts/osm.py)
DIST_LIMITE_M = 300.0  # tramo del río "que limita con Cartago": eje a ≤ 300 m del límite municipal OSM
CORTES_ZARAGOZA = (4.700, 4.703, 4.705, 4.7065, 4.708, 4.710, 4.715)  # sensibilidad del corte supuesto

# código WorldCover → (clave, nombre en español)
CLASES = {
    10: ("arbolado", "arbolado"),
    20: ("arbustos", "arbustos"),
    30: ("pasto", "pastos y herbazales"),
    40: ("cultivo", "cultivos anuales"),
    50: ("construido", "área construida"),
    60: ("suelo", "suelo desnudo o vegetación escasa"),
    80: ("agua", "cuerpos de agua permanentes"),
    90: ("humedal", "humedal herbáceo"),
}
NOMBRE_EN = {10: "Tree cover", 20: "Shrubland", 30: "Grassland", 40: "Cropland", 50: "Built-up",
             60: "Bare / sparse vegetation", 80: "Permanent water bodies", 90: "Herbaceous wetland"}
PUBLICADAS = ("arbolado", "construido", "agua")

ZARAGOZA_NODO = (4.6968, -75.9264)  # lat, lon (nodo OSM del centro poblado)
DILATACION_M = 30.0                 # supuesto de la especificación
SIMPLIFICACION_M = 10.0
HUECO_MIN_M2 = 5000.0  # huecos interiores más pequeños se consideran artefactos de la dilatación
CORTE_ZARAGOZA_LAT = 4.7065  # SUPUESTO: latitud donde la franja vial del sector DANE se une al núcleo
DIST_CABECERA_M = 250.0      # SUPUESTO: tramo del corredor "junto a la cabecera"
UTM = "EPSG:32618"

Z_HUELLA = "Zaragoza (corregimiento)"
Z_DANE = "Zaragoza: sector urbano DANE MGN 2024 completo (incluye la franja vial hacia la cabecera)"
Z_DANE_SUR = "Zaragoza: sector urbano DANE MGN 2024 al sur de 4,7065° (núcleo; corte supuesto)"
Z_MUN = "Municipio de Cartago (parte dentro de la rejilla)"  # nombre conservado; NO es el municipio completo
Z_MUN_COMPLETO = "Municipio de Cartago completo (10 m; ventana ampliada de la misma tesela)"
Z_MUN_FUERA = "Municipio de Cartago: parte fuera de la rejilla (10 m; sur, oriente y franja norte)"
Z_MUN_DENTRO_10M = "Municipio de Cartago: parte dentro de la rejilla (10 m; control)"
Z_CORR_TODO = "Corredor río La Vieja 0–100 m del eje completo, orilla de Cartago, todo el tramo limítrofe (10 m)"
Z_CORR_DENTRO = "Corredor río La Vieja 0–100 m del eje completo, orilla de Cartago, parte dentro de la rejilla (10 m)"
Z_CORR_FUERA = "Corredor río La Vieja 0–100 m del eje completo, orilla de Cartago, parte fuera de la rejilla (10 m)"
Z_LEJOS = "Corredor 0–100 m, tramo alejado de la cabecera (>250 m), orilla de Cartago"

# Normas citadas como contexto, con su fuente oficial (texto verificado en el Gestor Normativo de Función Pública)
NORMAS = [
    {"norma": "Decreto-Ley 2811 de 1974, art. 83 lit. d)",
     "contenido": "faja paralela a la línea de mareas máximas o a la del cauce permanente de ríos y lagos, hasta de treinta metros de ancho (bien inalienable e imprescriptible del Estado)",
     "url": "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=1551"},
    {"norma": "Decreto 2245 de 2017 (adiciona la sección 3A al Decreto 1076 de 2015), art. 2.2.3.2.3A.2",
     "contenido": "ronda hídrica: comprende la faja paralela del art. 83 d) y el área de protección o conservación aferente; su acotamiento corresponde a la autoridad ambiental competente",
     "url": "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=85056"},
]
# Humedales reconocidos por la CVC en Cartago (verificados en documentos de la CVC; solo como contexto)
HUMEDALES_CVC = [
    {"nombre": "Madrevieja La Culebrera",
     "dato": "margen izquierda del río La Vieja, corregimiento Cauca; huella del humedal 5,86 ha y área forestal protectora 5,56 ha (plan de manejo, Convenio CVC 131 de 2021, julio de 2023)",
     "url": "https://cvc.gov.co/sites/default/files/2025-04/Plan%20de%20Manejo%20La%20Culebrera.pdf"},
    {"nombre": "Madrevieja La Zapata",
     "dato": "antiguo cauce del río La Vieja en las comunas 6 y 7, entre el antiguo Matadero Municipal y el barrio Cámbulos (boletín CVC, 3 de febrero de 2021)",
     "url": "https://www.cvc.gov.co/2021015"},
]
INVENTARIO_HUMEDALES_CVC = {
    "nombre": "CVC y ASOCARS (2015). Inventario de humedales lénticos del corredor del río Cauca (modelo digital de elevación LiDAR)",
    "url": "https://ecopedia.cvc.gov.co/biodiversidad/humedales/inventario-de-humedales-lenticos-del-corredor-del-rio-cauca",
}

FUENTE = {
    "nombre": "ESA WorldCover 10 m 2021 v200 (tesela N03W078)",
    "url": "https://doi.org/10.5281/zenodo.7254221",
    "licencia": "CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)",
    "cita": ("Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W., Brockmann, C., Kirches, G., "
             "Wevers, J., Cartus, O., Santoro, M., Fritz, S., Lesiv, M., Herold, M., Tsendbazar, N.E., Xu, P., "
             "Ramoino, F., Arino, O., 2022. ESA WorldCover 10 m 2021 v200. doi:10.5281/zenodo.7254221"),
    "atribucion": ("© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) "
                   "processed by ESA WorldCover consortium"),
    "datos_crudos": URL,
}
FUENTE_OSM = {
    "nombre": "OpenStreetMap: polígonos de comunas, cabecera y municipio; ejes de los ríos La Vieja y Cauca; nodo de Zaragoza",
    "url": "https://www.openstreetmap.org/copyright",
    "licencia": "ODbL 1.0 (https://opendatacommons.org/licenses/odbl/1-0/)",
    "cita": "© colaboradores de OpenStreetMap",
    "uso": "solo para definir las zonas de 'por_zona' y la huella de Zaragoza; los valores de la capa salen de WorldCover",
}
DANE_BASE = "https://geoportal.dane.gov.co/mparcgis/rest/services/MGN2024/Serv_CapasMGN_2024/FeatureServer"
FUENTE_DANE = {
    "nombre": "DANE, Marco Geoestadístico Nacional (MGN) 2024: zona urbana (capa 305), sector urbano (246) y municipios (317)",
    "url": "https://geoportal.dane.gov.co/",
    "servicio": DANE_BASE,
    "licencia": "CC BY 4.0 (Geoportal DANE, 'Licencia y condiciones de uso')",
    "cita": "Departamento Administrativo Nacional de Estadística - DANE: www.dane.gov.co",
    "uso": "límite independiente de Zaragoza (sector urbano que contiene el nodo OSM) y municipio de la otra orilla del río La Vieja",
}


def fmt(x, nd=1):
    """Número con coma decimal (textos en español)."""
    return f"{x:.{nd}f}".replace(".", ",")


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- 1. lectura de la ventana

def descargar_ventana(limites=None, cache=CACHE, nombre_trozos="trozos"):
    """Devuelve (arr uint8, transform, crs, nodata) de una ventana de la tesela, usando la caché si existe.

    limites = (oeste, sur, este, norte) en grados; por defecto, la rejilla común + MARGEN.
    """
    import rasterio
    from rasterio.windows import Window, from_bounds

    if os.path.exists(cache):
        with rasterio.open(cache) as s:
            log(f"[caché] {os.path.relpath(cache, comun.RAIZ)}")
            return s.read(1), s.transform, s.crs, s.nodata
    if limites is None:
        limites = (comun.OESTE - MARGEN, comun.SUR - MARGEN, comun.ESTE + MARGEN, comun.NORTE + MARGEN)

    os.makedirs(DIR, exist_ok=True)
    ruta = "/vsicurl/" + URL
    with rasterio.open(ruta) as src:
        assert src.crs.to_epsg() == 4326, src.crs
        win = from_bounds(*limites, transform=src.transform).round_offsets().round_lengths()
        tr = src.window_transform(win)
        crs, nodata = src.crs, src.nodata
        bh, bw = src.block_shapes[0]
        tags = src.tags()
    r0, c0, h, w = int(win.row_off), int(win.col_off), int(win.height), int(win.width)
    log(f"ventana: filas {r0}–{r0 + h}, columnas {c0}–{c0 + w} ({w}×{h} px)")

    # trozos alineados con los bloques internos del COG (cada bloque se pide una sola vez)
    trozos = []
    for rb in range(r0 // bh, (r0 + h - 1) // bh + 1):
        for cb in range(c0 // bw, (c0 + w - 1) // bw + 1):
            a0, a1 = max(r0, rb * bh), min(r0 + h, (rb + 1) * bh)
            b0, b1 = max(c0, cb * bw), min(c0 + w, (cb + 1) * bw)
            trozos.append((a0, a1, b0, b1))

    dir_trozos = os.path.join(DIR, nombre_trozos)
    os.makedirs(dir_trozos, exist_ok=True)

    def leer(t):
        """Lee un trozo (o lo toma de la caché por trozo, para reanudar tras un corte)."""
        a0, a1, b0, b1 = t
        ruta_t = os.path.join(dir_trozos, f"f{a0}-{a1}_c{b0}-{b1}.npy")
        if os.path.exists(ruta_t):
            return t, np.load(ruta_t)
        for intento in range(1, 6):
            try:
                t0 = time.time()
                # a partir del 2.º intento se desactiva la caché de /vsicurl/ para este archivo,
                # que puede retener un error de red del intento anterior
                opciones = {"CPL_VSIL_CURL_NON_CACHED": ruta} if intento > 1 else {}
                with rasterio.Env(**opciones), rasterio.open(ruta) as s:
                    x = s.read(1, window=Window(b0, a0, b1 - b0, a1 - a0))
                np.save(ruta_t + ".tmp.npy", x)
                os.replace(ruta_t + ".tmp.npy", ruta_t)
                log(f"  trozo filas {a0}-{a1} cols {b0}-{b1}: {time.time() - t0:.1f} s")
                return t, x
            except Exception as e:  # red lenta o cortes: reintento con espera creciente
                log(f"  trozo {t} intento {intento} falló: {e}")
                time.sleep(5 * intento)
        return t, None

    arr = np.zeros((h, w), dtype=np.uint8)
    fallidos = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for (a0, a1, b0, b1), x in ex.map(leer, trozos):
            if x is None:
                fallidos.append((a0, a1, b0, b1))
            else:
                arr[a0 - r0:a1 - r0, b0 - c0:b1 - c0] = x
    if fallidos:
        raise RuntimeError(f"trozos sin leer tras 5 intentos: {fallidos}. Vuelva a ejecutar: los demás quedaron en caché.")

    perfil = {"driver": "GTiff", "dtype": "uint8", "count": 1, "width": w, "height": h, "crs": crs,
              "transform": tr, "nodata": nodata, "compress": "deflate", "tiled": True,
              "blockxsize": 256, "blockysize": 256}
    tmp = cache + ".tmp.tif"
    with rasterio.open(tmp, "w", **perfil) as d:
        d.write(arr, 1)
        d.update_tags(**tags, fuente_url=URL, ventana=f"row_off={r0},col_off={c0},w={w},h={h}")
    os.replace(tmp, cache)
    return arr, tr, crs, nodata


# ---------------------------------------------------------------- 2. fracciones por clase

def fracciones(arr, tr, crs, nodata):
    valido = arr != (nodata if nodata is not None else 0)
    pct, exacto = {}, {}
    # desfase entre el origen de la ventana y el de la rejilla, en píxeles WorldCover
    fac = comun.RES / tr.a
    col0 = (comun.OESTE - tr.c) / tr.a
    fil0 = (tr.f - comun.NORTE) / (-tr.e)
    alineado = all(abs(v - round(v)) < 1e-6 for v in (fac, col0, fil0))
    for cod, (clave, _) in CLASES.items():
        m = (arr == cod).astype(np.float32)
        m[~valido] = np.nan
        pct[clave] = comun.reproyectar(m, tr, crs, remuestreo="average") * 100.0
        if alineado:
            k, c, r = int(round(fac)), int(round(col0)), int(round(fil0))
            sub = m[r:r + k * comun.ALTO, c:c + k * comun.ANCHO]
            exacto[clave] = sub.reshape(comun.ALTO, k, comun.ANCHO, k).mean(axis=(1, 3)) * 100.0
    return pct, exacto, alineado, valido



# ---------------------------------------------------------------- 3. DANE MGN 2024 (límites independientes)

def descargar_dane():
    """Consulta el servicio ArcGIS REST del MGN 2024 (con caché). Devuelve {clave: geojson o None}."""
    import requests
    lat0, lon0 = ZARAGOZA_NODO
    caja = f"{comun.OESTE},{comun.SUR},{comun.ESTE},{comun.NORTE}"
    consultas = {
        "zona_urbana": (305, {"geometry": caja, "geometryType": "esriGeometryEnvelope"}),
        "sector_urbano_zaragoza": (246, {"geometry": f"{lon0},{lat0}", "geometryType": "esriGeometryPoint"}),
        # generalización de ~11 m para aligerar la respuesta (solo se usa para saber de qué municipio es cada celda)
        "municipios": (317, {"geometry": caja, "geometryType": "esriGeometryEnvelope", "maxAllowableOffset": "0.0001"}),
    }
    out = {}
    for clave, (capa, extra) in consultas.items():
        ruta = os.path.join(DIR, f"dane_mgn2024_{clave}.geojson")
        if not os.path.exists(ruta):
            params = {"inSR": "4326", "outSR": "4326", "spatialRel": "esriSpatialRelIntersects", "outFields": "*",
                      "returnGeometry": "true", "f": "geojson", **extra}
            for intento in range(1, 5):
                try:
                    t0 = time.time()
                    r = requests.get(f"{DANE_BASE}/{capa}/query", params=params, timeout=240)
                    r.raise_for_status()
                    d = r.json()
                    if not d.get("features"):
                        raise ValueError(f"respuesta sin entidades: {str(d)[:200]}")
                    if d.get("exceededTransferLimit") or d.get("properties", {}).get("exceededTransferLimit"):
                        raise ValueError("el servicio truncó la respuesta (exceededTransferLimit)")
                    comun.guardar_json(ruta + ".tmp", d)
                    os.replace(ruta + ".tmp", ruta)
                    log(f"  DANE {clave}: {len(d['features'])} entidades en {time.time() - t0:.1f} s")
                    break
                except Exception as e:
                    log(f"  DANE {clave} intento {intento} falló: {e}")
                    time.sleep(5 * intento)
        if os.path.exists(ruta):
            with open(ruta, encoding="utf-8") as f:
                out[clave] = json.load(f)
        else:
            out[clave] = None
            log(f"AVISO: sin DANE '{clave}': se omiten las zonas y validaciones que dependen de él")
    return out


def _dane_geom(dane, clave, filtro=None):
    from shapely.geometry import shape
    from shapely.ops import unary_union
    if not dane or not dane.get(clave):
        return None
    gs = [shape(f["geometry"]) for f in dane[clave]["features"] if filtro is None or filtro(f["properties"])]
    return unary_union(gs) if gs else None


# ---------------------------------------------------------------- 4. huella de Zaragoza

def _a_utm():
    from pyproj import Transformer
    return Transformer.from_crs("EPSG:4326", UTM, always_xy=True).transform


def _a_geo():
    from pyproj import Transformer
    return Transformer.from_crs(UTM, "EPSG:4326", always_xy=True).transform


def _poligono_huella(u, dil):
    """Dilata dil m, simplifica y rellena huecos interiores < HUECO_MIN_M2. Devuelve (geom, n_huecos, m2_huecos)."""
    from shapely.geometry import MultiPolygon, Polygon
    if dil <= 0:  # sin dilatación: la unión de píxeles tal cual
        return u, 0, 0.0
    h = u.buffer(dil).simplify(SIMPLIFICACION_M, preserve_topology=True)
    partes = list(h.geoms) if h.geom_type == "MultiPolygon" else [h]
    nuevas, n, m2 = [], 0, 0.0
    for p in partes:
        chicos = [hh for hh in p.interiors if Polygon(hh).area < HUECO_MIN_M2]
        n += len(chicos)
        m2 += sum(Polygon(hh).area for hh in chicos)
        nuevas.append(Polygon(p.exterior, [hh for hh in p.interiors if Polygon(hh).area >= HUECO_MIN_M2]))
    return (nuevas[0] if len(nuevas) == 1 else MultiPolygon(nuevas)), n, m2


def huella_zaragoza(arr, tr, dane):
    from rasterio.features import shapes
    from scipy import ndimage
    from shapely.geometry import box, mapping, shape
    from shapely.ops import transform as stransform, unary_union

    lat0, lon0 = ZARAGOZA_NODO
    construido = arr == 50
    etiquetas, n = ndimage.label(construido, structure=np.ones((3, 3), dtype=bool))  # 8-conectividad
    filas, cols = np.nonzero(construido)
    lat = tr.f + (filas + 0.5) * tr.e
    lon = tr.c + (cols + 0.5) * tr.a
    dist = np.hypot((lon - lon0) * 111320.0 * np.cos(np.radians(lat0)), (lat - lat0) * 110574.0)
    i = int(np.argmin(dist))
    eti = etiquetas[filas[i], cols[i]]
    comp = etiquetas == eti
    toca_borde = bool(comp[0].any() or comp[-1].any() or comp[:, 0].any() or comp[:, -1].any())
    info = {"distancia_nodo_pixel_m": round(float(dist[i]), 1), "pixeles": int(comp.sum()),
            "componentes_construidos_en_ventana": int(n), "toca_borde_ventana": toca_borde}

    geoms = [shape(g) for g, v in shapes(comp.astype(np.uint8), mask=comp, transform=tr, connectivity=8) if v == 1]
    union = unary_union(geoms)
    u = stransform(_a_utm(), union)
    info["area_pixeles_km2"] = round(u.area / 1e6, 4)
    # sensibilidad del área al supuesto de dilatación (mismo procedimiento)
    info["sensibilidad_area_km2"] = {f"dilatacion_{int(d)}_m": round(_poligono_huella(u, d)[0].area / 1e6, 4)
                                     for d in (0.0, 15.0, 30.0, 45.0)}
    h, nh, m2h = _poligono_huella(u, DILATACION_M)
    info["huecos_rellenados"] = nh
    info["area_huecos_rellenados_m2"] = round(m2h, 1)
    info["area_km2"] = round(h.area / 1e6, 4)
    g = stransform(_a_geo(), h)
    info["bbox"] = [round(v, 5) for v in g.bounds]

    # validación con límites independientes del DANE (MGN 2024)
    val = None
    zu = _dane_geom(dane, "zona_urbana", lambda p: p.get("mpio_cdpmp") == "76147" and p.get("clas_ccdgo") == "1")
    sec = _dane_geom(dane, "sector_urbano_zaragoza")
    if zu is not None and sec is not None:
        zu_u, sec_u = stransform(_a_utm(), zu), stransform(_a_utm(), sec)
        sur_u = stransform(_a_utm(), sec.intersection(box(-180, -90, 180, CORTE_ZARAGOZA_LAT)))
        props = dane["sector_urbano_zaragoza"]["features"][0]["properties"]
        hay_cp_zaragoza = any("ZARAGOZA" in str(f["properties"].get("zu_cnmbre", "")).upper()
                              for f in dane["zona_urbana"]["features"])
        val = {
            "fuente": FUENTE_DANE["cita"] + " (MGN 2024, CC BY 4.0)",
            "hallazgo": ((f"En la capa de zona urbana del MGN 2024 no hay un centro poblado llamado Zaragoza dentro de la rejilla; "
                          if not hay_cp_zaragoza else "El MGN 2024 tiene además un centro poblado llamado Zaragoza; ")
                         + f"el {fmt(100 * h.intersection(zu_u).area / h.area)} % de la huella está dentro de la zona urbana "
                         f"'Cabecera municipal' de Cartago (clase 1), en el sector urbano {props.get('setu_ccdgo')}."),
            "sector_urbano": props.get("setu_ccnct"),
            "area_sector_km2": round(sec_u.area / 1e6, 4),
            "area_sector_al_sur_de_4_7065_km2": round(sur_u.area / 1e6, 4),
            "fraccion_huella_dentro_zona_urbana_dane": round(h.intersection(zu_u).area / h.area, 3),
            "fraccion_huella_dentro_sector": round(h.intersection(sec_u).area / h.area, 3),
            "iou_huella_vs_sector": round(h.intersection(sec_u).area / h.union(sec_u).area, 3),
            "iou_huella_vs_sector_sur": round(h.intersection(sur_u).area / h.union(sur_u).area, 3),
            "fraccion_sector_sur_cubierta_por_huella": round(h.intersection(sur_u).area / sur_u.area, 3),
        }
    info["validacion_dane"] = val

    geo = json.loads(json.dumps(mapping(g)), parse_float=lambda s: round(float(s), 6))
    s = info["sensibilidad_area_km2"]
    props = {
        "nombre": "Zaragoza (corregimiento)",
        "fuente": "ESA WorldCover 2021: área construida conectada al centro poblado (nodo OSM)",
        "area_km2": info["area_km2"],
        "metodo": ("píxeles de clase 50 (área construida) de ESA WorldCover 10 m 2021 v200 conectados en "
                   "8 direcciones al píxel construido más cercano al nodo OSM (4.6968, -75.9264); "
                   "dilatación de 30 m, simplificación de 10 m y relleno de huecos interiores menores de 0,5 ha "
                   "(artefactos de la dilatación) en UTM 18N"),
        "uso": ("Zona de trabajo para estadísticas zonales; no es un límite oficial. Su área depende del supuesto de "
                f"dilatación (0 m: {fmt(s['dilatacion_0_m'], 2)} km²; 15 m: {fmt(s['dilatacion_15_m'], 2)}; "
                f"30 m: {fmt(s['dilatacion_30_m'], 2)}; 45 m: {fmt(s['dilatacion_45_m'], 2)} km²), y como se construyó con los píxeles construidos, su % construido "
                "(≈ 55 %) sale por construcción: no es un dato de densidad construida ni es comparable con el de las comunas."),
        "area_pixeles_construidos_km2": info["area_pixeles_km2"],
        "sensibilidad_area_km2": s,
        "licencia": "ESA WorldCover: CC BY 4.0; nodo: OpenStreetMap (ODbL); validación: DANE MGN 2024 (CC BY 4.0)",
        "cita": FUENTE["cita"],
        "atribucion": FUENTE["atribucion"] + " · © colaboradores de OpenStreetMap",
    }
    if val:
        props["validacion_dane_mgn2024"] = val
    feature = {"type": "Feature", "properties": props, "geometry": geo}
    return feature, info


# ---------------------------------------------------------------- 6. zonas de resumen

def distancia_m(geom_lonlat):
    """Distancia (m, UTM 18N) de cada centro de celda a una geometría lon/lat."""
    import shapely
    from shapely.ops import transform as stransform
    g = stransform(_a_utm(), geom_lonlat)
    lat, lon = comun.centros_celdas()
    x, y = _a_utm()(lon.ravel(), lat.ravel())
    return shapely.distance(shapely.points(np.c_[x, y]), g).reshape(lat.shape)


def distancia_rio_m(nombre="rio_la_vieja"):
    return distancia_m(comun.lineas_rio(nombre))


def rasterizar(geom, valor=1):
    from rasterio.features import rasterize
    return rasterize([(geom, valor)], out_shape=(comun.ALTO, comun.ANCHO), transform=comun.transformacion(),
                     fill=0, dtype="uint8").astype(bool)


def zonas_resumen(dane):
    """Máscaras booleanas con nombre, más información de contexto para las definiciones."""
    from shapely.geometry import box
    from shapely.ops import transform as stransform
    zonas = comun.comunas()
    mz = comun.mascara_zonas(zonas)
    out, info = {}, {}
    for z in zonas:
        out[z["nombre"]] = mz == z["indice"]
    out["Cabecera municipal (OSM)"] = comun.mascara_urbana()
    mun_geom = comun._poligono(comun.osm()["municipio"])
    mun = rasterizar(mun_geom)
    out[Z_MUN] = mun
    # fracción del municipio (polígono OSM) cubierta por la rejilla, en UTM 18N
    U = _a_utm()
    rej_geo = box(comun.OESTE, comun.SUR, comun.ESTE, comun.NORTE)
    mun_km2 = stransform(U, mun_geom).area / 1e6
    dentro_km2 = stransform(U, mun_geom.intersection(rej_geo)).area / 1e6
    info["municipio_osm_km2"] = round(mun_km2, 1)
    info["municipio_osm_km2_en_rejilla"] = round(dentro_km2, 1)
    info["municipio_osm_km2_fuera_rejilla"] = round(mun_km2 - dentro_km2, 1)
    info["municipio_pct_en_rejilla"] = round(100.0 * dentro_km2 / mun_km2, 1)
    fuera_geo = mun_geom.difference(rej_geo)
    info["municipio_fuera_partes"] = sorted(
        [{"km2": round(stransform(U, g).area / 1e6, 2), "bbox_lon_lat": [round(v, 4) for v in g.bounds]}
         for g in getattr(fuera_geo, "geoms", [fuera_geo]) if stransform(U, g).area > 1e4],
        key=lambda x: -x["km2"])
    dmun = _dane_geom(dane, "municipios", lambda p: p.get("mpio_cdpmp") == "76147")
    if dmun is not None:
        info["municipio_dane_km2"] = round(stransform(U, dmun).area / 1e6, 1)
        props = [f["properties"] for f in dane["municipios"]["features"] if f["properties"].get("mpio_cdpmp") == "76147"]
        if props and props[0].get("mpio_narea"):
            info["municipio_dane_mpio_narea_km2"] = round(float(props[0]["mpio_narea"]), 1)

    sec = _dane_geom(dane, "sector_urbano_zaragoza")
    if sec is not None:
        out[Z_DANE] = rasterizar(sec)
        out[Z_DANE_SUR] = rasterizar(sec.intersection(box(-180, -90, 180, CORTE_ZARAGOZA_LAT)))

    d_vieja = distancia_rio_m("rio_la_vieja")
    d_cab = distancia_m(comun._poligono(comun.osm()["cabecera"]))
    c = {b: d_vieja <= b for b in (50, 100, 200)}
    for b in (50, 100, 200):
        out[f"Corredor río La Vieja 0–{b} m del eje, ambas orillas"] = c[b]
        out[f"Corredor río La Vieja 0–{b} m del eje, orilla de Cartago"] = c[b] & mun
    out["Corredor río La Vieja 0–100 m del eje, otra orilla (fuera del municipio)"] = c[100] & ~mun
    junto = c[100] & (d_cab <= DIST_CABECERA_M)
    lejos = c[100] & (d_cab > DIST_CABECERA_M)
    out["Corredor 0–100 m, tramo junto a la cabecera (≤250 m), ambas orillas"] = junto
    out["Corredor 0–100 m, tramo junto a la cabecera (≤250 m), orilla de Cartago"] = junto & mun
    out["Corredor 0–100 m, tramo junto a la cabecera (≤250 m), otra orilla"] = junto & ~mun
    out[Z_LEJOS] = lejos & mun
    out["Corredor 0–100 m, tramo alejado de la cabecera (>250 m), otra orilla"] = lejos & ~mun

    # longitud del La Vieja que limita con Cartago y parte cubierta por la rejilla, con el eje OSM COMPLETO
    # (comun.lineas_rio() está recortado a la rejilla + 0,01° y no sirve para medir longitudes)
    info["la_vieja"] = longitudes_la_vieja(mun_geom)
    dmun_l = _dane_geom(dane, "municipios", lambda p: p.get("mpio_cdpmp") == "76147")
    if dmun_l is not None and "error" not in info["la_vieja"]:
        ld = longitudes_la_vieja(dmun_l)
        info["la_vieja"]["control_con_limite_dane"] = {k: ld[k] for k in ("km_limitrofes_con_cartago", "km_limitrofes_dentro_de_la_rejilla",
                                                                          "pct_limitrofe_dentro_de_la_rejilla")}

    # ¿de qué municipio (DANE) es la otra orilla?
    otra = c[100] & ~mun
    info["otra_orilla_celdas"] = int(otra.sum())
    if dane and dane.get("municipios"):
        from rasterio.features import rasterize
        from shapely.geometry import shape
        feats = dane["municipios"]["features"]
        idx = rasterize([(shape(f["geometry"]), k + 1) for k, f in enumerate(feats)], out_shape=(comun.ALTO, comun.ANCHO),
                        transform=comun.transformacion(), fill=0, dtype="uint8")
        comp = {}
        for k, f in enumerate(feats):
            nn = int((idx[otra] == k + 1).sum())
            if nn:
                p = f["properties"]
                comp[f"{p.get('mpio_cnmbr')} ({p.get('dpto_cnmbr')})"] = round(100.0 * nn / otra.sum(), 1)
        info["otra_orilla_municipio_dane_pct"] = comp
        # composición de TODA la rejilla por municipio (DANE): a qué corresponden las 'estadisticas' de los cob_*
        rej_mun = {}
        for k, f in enumerate(feats):
            nn = int((idx == k + 1).sum())
            if nn:
                p = f["properties"]
                rej_mun[f"{p.get('mpio_cnmbr')} ({p.get('dpto_cnmbr')})"] = round(100.0 * nn / idx.size, 1)
        info["rejilla_por_municipio_dane_pct"] = dict(sorted(rej_mun.items(), key=lambda kv: -kv[1]))
        k_cart = [k for k, f in enumerate(feats) if f["properties"].get("mpio_cdpmp") == "76147"]
        if k_cart:
            orilla_c = c[100] & mun
            info["orilla_cartago_osm_dentro_cartago_dane_pct"] = round(100.0 * float((idx[orilla_c] == k_cart[0] + 1).mean()), 1)
    pc = _dane_geom(dane, "zona_urbana", lambda p: p.get("zu_cnmbre") == "PUERTO CALDAS")
    if pc is not None:
        mpc = rasterizar(pc)
        info["otra_orilla_celdas_en_puerto_caldas_dane"] = int((otra & mpc).sum())
        info["otra_orilla_junto_cabecera_celdas_en_puerto_caldas_dane"] = int((junto & ~mun & mpc).sum())
    return out, d_vieja, info


# ---------------------------------------------------------------- 6b. municipio completo y río completo (10 m)

def eje_la_vieja_completo():
    """Eje OSM completo del río La Vieja (vías 749764338 + 1126843631 de fuentes/osm-base.json, sin recortar).

    comun.lineas_rio() está recortado a la rejilla + 0,01° (scripts/osm.py descarta los nodos de fuera y deja
    cuerdas), así que no sirve para medir longitudes. Devuelve (LineString lon/lat, descripción) o (None, motivo).
    """
    from shapely.geometry import LineString
    from shapely.ops import linemerge
    if not os.path.exists(OSM_BASE):
        return None, f"no existe {os.path.relpath(OSM_BASE, comun.RAIZ)}"
    with open(OSM_BASE, encoding="utf-8") as f:
        d = json.load(f)
    vias = {e["id"]: e for e in d["elements"] if e["type"] == "way" and e["id"] in VIAS_LA_VIEJA}
    if set(vias) != set(VIAS_LA_VIEJA):
        return None, f"faltan vías del La Vieja en osm-base.json: {set(VIAS_LA_VIEJA) - set(vias)}"
    g = linemerge([LineString([(p["lon"], p["lat"]) for p in vias[k]["geometry"]]) for k in VIAS_LA_VIEJA])
    if g.geom_type != "LineString":
        return None, "las vías del La Vieja no forman una línea continua"
    fecha = d.get("osm3s", {}).get("timestamp_osm_base", "")
    return g, f"vías OSM {' + '.join(map(str, VIAS_LA_VIEJA))} completas (fuentes/osm-base.json, OSM {fecha[:10]})"


def longitudes_la_vieja(mun_geom):
    """Longitud del eje completo del La Vieja que limita con Cartago y la parte cubierta por la rejilla."""
    from shapely.geometry import box
    from shapely.ops import transform as stransform
    eje, desc = eje_la_vieja_completo()
    if eje is None:
        return {"error": desc}
    U, Gt = _a_utm(), _a_geo()
    rio = stransform(U, eje)
    mun_u = stransform(U, mun_geom)
    junto_u = rio.intersection(mun_u.exterior.buffer(DIST_LIMITE_M))  # distancias en UTM 18N
    # Los recortes por cajas lon/lat se hacen en grados (en UTM los paralelos son curvos y una caja de esquinas
    # transformadas no sigue la latitud); luego se mide la longitud en UTM.
    junto = stransform(Gt, junto_u)
    km = lambda g: stransform(U, g).length / 1e3  # noqa: E731
    dentro = junto.intersection(box(comun.OESTE, comun.SUR, comun.ESTE, comun.NORTE))
    # fuera de la rejilla, por dirección (franjas que no se solapan)
    G = 1.0  # grados alrededor de la rejilla (el eje completo está dentro de ±0,5°)
    o, s_, e, n = comun.OESTE - G, comun.SUR - G, comun.ESTE + G, comun.NORTE + G
    assert box(o, s_, e, n).contains(eje), "el eje del La Vieja sale de la caja de franjas"
    franjas = {
        "al sur": box(o, s_, e, comun.SUR),
        "al norte": box(o, comun.NORTE, e, n),
        "al oriente": box(comun.ESTE, comun.SUR, e, comun.NORTE),
        "al occidente": box(o, comun.SUR, comun.OESTE, comun.NORTE),
    }
    fuera = {k: round(km(junto.intersection(b)), 1) for k, b in franjas.items()}
    fuera = {k: v for k, v in fuera.items() if v > 0}
    km_junto, km_dentro = km(junto), km(dentro)
    assert abs(km_junto - junto_u.length / 1e3) < 0.01
    assert abs(km_dentro + sum(fuera.values()) - km_junto) < 0.3, "las franjas no suman el tramo limítrofe"
    rec = stransform(U, comun.lineas_rio("rio_la_vieja"))
    return {
        "eje": desc,
        "km_eje_completo_en_osm": round(rio.length / 1e3, 1),
        "km_limitrofes_con_cartago": round(km_junto, 1),
        "criterio_limitrofe": f"eje a ≤ {int(DIST_LIMITE_M)} m del límite del polígono OSM del municipio (UTM 18N)",
        "km_limitrofes_dentro_de_la_rejilla": round(km_dentro, 1),
        "pct_limitrofe_dentro_de_la_rejilla": round(100.0 * km_dentro / km_junto, 1) if km_junto else None,
        "km_limitrofes_fuera_de_la_rejilla_por_direccion": fuera,
        "km_eje_recortado_comun_lineas_rio": round(rec.length / 1e3, 1),
        "nota_eje_recortado": ("comun.lineas_rio() (js/datos-osm.js) es el eje recortado por scripts/osm.py a la rejilla + 0,01°, "
                               "con cuerdas donde descartó nodos: sirve para las máscaras dentro de la rejilla, no para longitudes"),
    }


def limites_ventana_municipio(mun_geom):
    o, s_, e, n = mun_geom.bounds
    return (min(o, comun.OESTE) - MARGEN, min(s_, comun.SUR) - MARGEN,
            max(e, comun.ESTE) + MARGEN, max(n, comun.NORTE) + MARGEN)


def ventana_municipio(mun_geom, arr_rej, tr_rej):
    """Lee (con caché) la ventana ampliada de la misma tesela que cubre todo el municipio.

    Comprueba que, donde se solapa con la ventana de la rejilla, es idéntica píxel a píxel.
    Devuelve (arr, transform, nodata) o None si la red falla (se omiten las zonas de 10 m).
    """
    try:
        arr, tr, crs, nodata = descargar_ventana(limites_ventana_municipio(mun_geom), CACHE_MUN, "trozos_municipio")
    except Exception as e:  # red lenta: el producto sigue sin las zonas ampliadas
        log(f"AVISO: no se pudo leer la ventana ampliada del municipio ({e}); se omiten las zonas de 10 m")
        return None
    assert abs(tr.a - tr_rej.a) < 1e-12 and abs(tr.e - tr_rej.e) < 1e-12
    dc = (tr_rej.c - tr.c) / tr.a
    df = (tr_rej.f - tr.f) / tr.e
    assert abs(dc - round(dc)) < 1e-6 and abs(df - round(df)) < 1e-6, "ventanas no alineadas"
    dc, df = int(round(dc)), int(round(df))
    h, w = arr_rej.shape
    iguales = np.array_equal(arr[df:df + h, dc:dc + w], arr_rej)
    log(f"ventana ampliada {arr.shape}; idéntica a la ventana de la rejilla en el solape: {iguales}")
    assert iguales, "la ventana ampliada no coincide con la caché de la rejilla"
    return arr, tr, nodata


def resumen_nativo(arr, tr, nodata, mascaras):
    """% de píxeles de 10 m de cada clase (sobre los píxeles con dato) dentro de cada máscara de la ventana."""
    lat = tr.f + (np.arange(arr.shape[0]) + 0.5) * tr.e
    a_fila = (abs(tr.e) * 110574.0) * (tr.a * 111320.0 * np.cos(np.radians(lat)))  # m² por píxel, por fila
    valido = arr != (nodata if nodata is not None else 0)
    out = {}
    for nombre, m in mascaras.items():
        mv = m & valido
        n = int(mv.sum())
        fila = {"celdas": None, "pixeles_10m": n,
                "area_km2": round(float((m * a_fila[:, None]).sum()) / 1e6, 2)}
        for cod, (clave, _) in CLASES.items():
            fila[clave] = round(100.0 * float((arr[mv] == cod).sum()) / n, 2) if n else None
        fila["nota"] = ("calculado a 10 m (% de píxeles de WorldCover cuyo centro cae en la zona) sobre una ventana ampliada "
                        "de la misma tesela; no son celdas de la rejilla ('celdas' = null)")
        out[nombre] = fila
    return out


def zonas_nativas(arr, tr, nodata, mun_geom):
    """Máscaras sobre la ventana ampliada (10 m) y su resumen. Devuelve (por_zona_nativo, info)."""
    from rasterio.features import rasterize
    from shapely.geometry import box
    from shapely.ops import transform as stransform
    forma = arr.shape
    ras = lambda g: rasterize([(g, 1)], out_shape=forma, transform=tr, fill=0, dtype="uint8").astype(bool)  # noqa: E731
    mun = ras(mun_geom)
    rej = ras(box(comun.OESTE, comun.SUR, comun.ESTE, comun.NORTE))
    alto, ancho = forma
    caja_ventana = box(tr.c, tr.f + alto * tr.e, tr.c + ancho * tr.a, tr.f)
    info = {"municipio_contenido_en_la_ventana": bool(caja_ventana.contains(mun_geom)),
            "ventana_px": [int(ancho), int(alto)], "ventana_bbox": [round(v, 5) for v in caja_ventana.bounds]}
    assert info["municipio_contenido_en_la_ventana"], "la ventana ampliada no cubre todo el municipio"
    m = {
        Z_MUN_COMPLETO: mun,
        Z_MUN_FUERA: mun & ~rej,
        Z_MUN_DENTRO_10M: mun & rej,
    }
    eje, desc = eje_la_vieja_completo()
    if eje is not None:
        U, Gt = _a_utm(), _a_geo()
        corr = ras(stransform(Gt, stransform(U, eje).buffer(100.0)))
        m[Z_CORR_TODO] = corr & mun
        m[Z_CORR_DENTRO] = corr & mun & rej
        m[Z_CORR_FUERA] = corr & mun & ~rej
        info["eje_corredor_10m"] = desc
    v, c = np.unique(arr[mun], return_counts=True)
    info["hist_municipio_10m"] = {int(k): int(n) for k, n in zip(v, c)}
    # ¿dónde están los pocos píxeles de humedal herbáceo (clase 90) del municipio? (distancia al eje del La Vieja)
    f90, c90 = np.nonzero(mun & (arr == 90))
    if f90.size and eje is not None:
        import shapely
        lat90, lon90 = tr.f + (f90 + 0.5) * tr.e, tr.c + (c90 + 0.5) * tr.a
        x, y = _a_utm()(lon90, lat90)
        dist = shapely.distance(shapely.points(np.c_[x, y]), stransform(_a_utm(), eje))
        info["clase90_en_municipio"] = {"pixeles": int(f90.size),
                                        "lat_lon_min": [round(float(lat90.min()), 4), round(float(lon90.min()), 4)],
                                        "lat_lon_max": [round(float(lat90.max()), 4), round(float(lon90.max()), 4)],
                                        "dist_min_eje_la_vieja_km": round(float(dist.min()) / 1e3, 1)}
    return resumen_nativo(arr, tr, nodata, m), info


def humedales_osm(arr, tr, nodata):
    """Clases de WorldCover dentro de los polígonos OSM natural=wetland de la caché OSM (si los hay)."""
    from rasterio.features import rasterize
    from shapely.geometry import Polygon
    from shapely.ops import transform as stransform
    if not os.path.exists(OSM_VERDES):
        return []
    with open(OSM_VERDES, encoding="utf-8") as f:
        d = json.load(f)
    out = []
    for e in d["elements"]:
        t = e.get("tags", {})
        if e["type"] != "way" or t.get("natural") != "wetland" or len(e.get("geometry", [])) < 4:
            continue
        g = Polygon([(p["lon"], p["lat"]) for p in e["geometry"]])
        m = rasterize([(g, 1)], out_shape=arr.shape, transform=tr, fill=0, dtype="uint8").astype(bool)
        m &= arr != (nodata if nodata is not None else 0)
        n = int(m.sum())
        if not n:
            continue
        cuenta = {CLASES[c][0]: int((arr[m] == c).sum()) for c in CLASES if (arr[m] == c).any()}
        c = g.centroid
        out.append({"osm": f"way {e['id']}", "etiquetas": {k: t[k] for k in ("natural", "wetland", "water", "name") if k in t},
                    "centro_lat_lon": [round(c.y, 4), round(c.x, 4)],
                    "area_ha": round(stransform(_a_utm(), g).area / 1e4, 2), "pixeles_10m": n,
                    "pixeles_por_clase_worldcover": cuenta})
    return out


def sensibilidad_corte_zaragoza(pct, dane):
    """% construido y arbolado del sector DANE de Zaragoza recortado a distintas latitudes (corte supuesto)."""
    from shapely.geometry import box
    sec = _dane_geom(dane, "sector_urbano_zaragoza")
    if sec is None:
        return None
    out = {}
    for lat in CORTES_ZARAGOZA:
        m = rasterizar(sec.intersection(box(-180, -90, 180, lat)))
        out[f"{lat:.4f}".rstrip("0")] = {"celdas": int(m.sum()),
                                         "construido": round(float(np.nanmean(pct["construido"][m])), 1),
                                         "arbolado": round(float(np.nanmean(pct["arbolado"][m])), 1)}
    return out


def _pct_clases(fila, claves=("arbolado", "pasto", "cultivo", "construido")):
    return ", ".join(f"{k} {fmt(fila[k])} %" for k in claves if fila.get(k) is not None)


def txt_municipio(info, nat):
    """Frase sobre la fracción del municipio cubierta por la rejilla y la composición del municipio completo."""
    t = (f"La rejilla cubre {fmt(info['municipio_osm_km2_en_rejilla'])} de los {fmt(info['municipio_osm_km2'])} km² del polígono "
         f"OSM del municipio ({fmt(info['municipio_pct_en_rejilla'])} %"
         + (f"; el MGN 2024 del DANE da {fmt(info['municipio_dane_km2'])} km²" if "municipio_dane_km2" in info else "")
         + f"). Quedan fuera {fmt(info['municipio_osm_km2_fuera_rejilla'])} km², casi todos rurales: el sur y el oriente del "
         "municipio y una franja al norte.")
    if nat and Z_MUN_COMPLETO in nat:
        c, f_, d_ = nat[Z_MUN_COMPLETO], nat.get(Z_MUN_FUERA), nat.get(Z_MUN_DENTRO_10M)
        t += (f" En el municipio completo (conteo a 10 m): {_pct_clases(c)}. En la parte dentro de la rejilla: {_pct_clases(d_)}; "
              f"en la parte fuera: {_pct_clases(f_)}. Por eso las cifras de la zona '{Z_MUN}' no son municipales: "
              f"su construido ({fmt(d_['construido'])} %) es {fmt(d_['construido'] / c['construido'])} veces el del municipio "
              f"completo ({fmt(c['construido'])} %) y su arbolado es menor ({fmt(d_['arbolado'])} frente a {fmt(c['arbolado'])} %).")
    return t


def txt_la_vieja(lv):
    """Frase sobre la cobertura del corredor del La Vieja, medida con el eje OSM completo."""
    if not lv or "error" in lv:
        return f"No se pudo medir el tramo limítrofe del La Vieja ({(lv or {}).get('error', 'sin datos')})."
    fuera = lv["km_limitrofes_fuera_de_la_rejilla_por_direccion"]
    nombres = {"al oriente": "al oriente", "al sur": "al sur (suroriente del municipio)", "al norte": "al norte",
               "al occidente": "al occidente"}
    partes = "; ".join(f"{fmt(v)} km {nombres[k]}" for k, v in sorted(fuera.items(), key=lambda kv: -kv[1]))
    return (f"Los corredores del La Vieja de la rejilla cubren solo {fmt(lv['km_limitrofes_dentro_de_la_rejilla'])} de los "
            f"{fmt(lv['km_limitrofes_con_cartago'])} km del río que limitan con Cartago "
            f"({fmt(lv['pct_limitrofe_dentro_de_la_rejilla'])} %). El resto queda fuera de la rejilla: {partes}. "
            f"Tramo limítrofe = {lv['criterio_limitrofe']}, medido con las vías OSM completas "
            f"{' + '.join(map(str, VIAS_LA_VIEJA))} (el eje recortado de comun.lineas_rio() mide "
            f"{fmt(lv['km_eje_recortado_comun_lineas_rio'])} km y no sirve para longitudes)"
            + (f"; con el límite municipal del MGN 2024 del DANE da {fmt(lv['control_con_limite_dane']['km_limitrofes_dentro_de_la_rejilla'])} "
               f"de {fmt(lv['control_con_limite_dane']['km_limitrofes_con_cartago'])} km" if "control_con_limite_dane" in lv else "")
            + ".")


def txt_corte_zaragoza(sens):
    if not sens:
        return ""
    con = [v["construido"] for v in sens.values()]
    arb = [v["arbolado"] for v in sens.values()]
    cortes = [fmt(float(k), 3) for k in sens]
    central = sens.get(f"{CORTE_ZARAGOZA_LAT:.4f}".rstrip("0"))
    return (f"el % construido depende mucho del corte supuesto: va de {fmt(min(con))} a {fmt(max(con))} % según la "
            f"latitud del corte (de {cortes[0]}° a {cortes[-1]}°)"
            + (f"; con 4,7065° es {fmt(central['construido'])} %" if central else "")
            + f". El arbolado es estable ({fmt(min(arb))}–{fmt(max(arb))} %). Usar el rango, no el valor central.")


def txt_ausentes(hist_rejilla, hist_mun, hum, c90=None):
    """Frase sobre las clases 20 y 90: ausencia en el clasificador, no en el terreno."""
    t = ("WorldCover no clasifica ningún píxel de la rejilla como arbustos (clase 20) ni como humedal herbáceo (clase 90)"
         if hist_rejilla.get(20, 0) == 0 and hist_rejilla.get(90, 0) == 0 else
         f"WorldCover clasifica muy pocos píxeles de la rejilla como arbustos ({hist_rejilla.get(20, 0)}) o humedal herbáceo ({hist_rejilla.get(90, 0)})")
    if hist_mun is not None:
        t += (f". En el municipio completo hay {hist_mun.get(20, 0)} y {hist_mun.get(90, 0)} píxeles de 10 m, respectivamente"
              + (f"; los de clase 90 están al sur de la rejilla, a {fmt(c90['dist_min_eje_la_vieja_km'])} km o más del eje del La Vieja"
                 if c90 else ""))
    t += (". Eso describe al clasificador, NO al terreno. Cartago tiene humedales y madreviejas reconocidos por la CVC "
          "(p. ej., La Culebrera, 5,86 ha en la margen izquierda del La Vieja, con plan de manejo; La Zapata, antiguo cauce del "
          "La Vieja en las comunas 6 y 7), que este mapa no clasifica como humedal: quedan dentro de otras clases (pasto, agua, "
          "arbolado u otras).")
    for h in hum or []:
        c = h["pixeles_por_clase_worldcover"]
        t += (f" Comprobación: el polígono OSM {h['osm']} ({', '.join(f'{k}={v}' for k, v in h['etiquetas'].items())}; "
              f"{fmt(h['area_ha'])} ha) tiene {h['pixeles_10m']} píxeles: "
              + ", ".join(f"{v} de {k}" for k, v in sorted(c.items(), key=lambda kv: -kv[1]))
              + f" y {c.get('humedal', 0)} de humedal.")
    t += (" Para cualquier decisión sobre humedales, usar el inventario y los planes de manejo de la CVC, no esta capa.")
    return t


def hallazgos(info, nat, txt_aus, sens):
    h = [txt_municipio(info, nat)]
    t = txt_la_vieja(info.get("la_vieja"))
    if nat and Z_CORR_DENTRO in nat and Z_CORR_FUERA in nat:
        a, b = nat[Z_CORR_DENTRO], nat[Z_CORR_FUERA]
        t += (f" En la orilla de Cartago (0–100 m del eje completo, conteo a 10 m), la parte fuera de la rejilla "
              f"({fmt(b['area_km2'], 2)} km²) es {'mayor' if b['area_km2'] > a['area_km2'] else 'menor'} que la de dentro "
              f"({fmt(a['area_km2'], 2)} km²) y tiene otra composición: pasto {fmt(b['pasto'])} frente a {fmt(a['pasto'])} %, "
              f"agua {fmt(b['agua'])} frente a {fmt(a['agua'])} %, cultivo {fmt(b['cultivo'])} frente a {fmt(a['cultivo'])} %; "
              f"el arbolado es parecido ({fmt(b['arbolado'])} frente a {fmt(a['arbolado'])} %). Por eso el 'tramo alejado "
              "de la cabecera' de la rejilla no representa todo el corredor rural del La Vieja.")
    h.append(t)
    h.append(txt_aus)
    if sens:
        h.append(f"Zaragoza (sector urbano DANE al sur del corte supuesto): {txt_corte_zaragoza(sens)}")
    return h


def definiciones(info, zinfo, sens=None, nat=None, nat_info=None):
    s = zinfo["sensibilidad_area_km2"]
    otra = info.get("otra_orilla_municipio_dane_pct")
    txt_otra = (f"Según el MGN 2024 del DANE (límites generalizados a ~11 m), las celdas de la otra orilla (0–100 m) son de: "
                + ", ".join(f"{k} {fmt(v)} %" for k, v in sorted(otra.items(), key=lambda kv: -kv[1])) + ". ") if otra else ""
    if "orilla_cartago_osm_dentro_cartago_dane_pct" in info:
        txt_otra += (f"Los límites OSM y DANE no coinciden del todo junto al cauce: el "
                     f"{fmt(100 - info['orilla_cartago_osm_dentro_cartago_dane_pct'])} % de las celdas 'orilla de Cartago' "
                     "queda fuera de Cartago según el DANE, y la parte de 'otra orilla' que el DANE asigna a Cartago es la "
                     "indicada arriba. ")
    lv = info.get("la_vieja") or {}
    d = {
        "unidad": ("porcentaje medio de las celdas de la rejilla cuyo centro cae en la zona (equivale al % del área clasificada "
                   "en cada clase). Las zonas marcadas '(10 m)' son % de píxeles de WorldCover de 10 m (ver su 'nota')."),
        "Comuna 1 … Comuna 7": "polígonos OSM de las comunas (comun.comunas()); © colaboradores de OpenStreetMap, ODbL",
        Z_HUELLA: ("huella derivada de este mismo producto (datos/zaragoza.json): píxeles construidos de WorldCover conectados "
                   "al nodo OSM, dilatados 30 m (supuesto). Es una zona de trabajo, no un límite oficial. Su % construido "
                   "(y por complemento el de las demás clases) sale POR CONSTRUCCIÓN y no es comparable con el de las comunas; "
                   f"su área depende de la dilatación (0 m: {fmt(s['dilatacion_0_m'], 2)} km²; 30 m: {fmt(s['dilatacion_30_m'], 2)} km²). "
                   f"Para comparar, usar '{Z_DANE_SUR}' y su rango de sensibilidad."),
        "Cabecera municipal (OSM)": "polígono OSM de la cabecera (comun.mascara_urbana()); no incluye Zaragoza",
        Z_MUN: ("polígono OSM del municipio recortado a la rejilla común. NO representa al municipio. "
                + txt_municipio(info, nat)
                + (f" Para cifras municipales usar '{Z_MUN_COMPLETO}'." if nat else
                   " No se pudo leer la ventana ampliada: no hay cifra del municipio completo en esta ejecución.")),
        "Corredor río La Vieja 0–N m del eje": (
            "celdas cuyo centro está a ≤ N m del eje OSM del río La Vieja dentro de la rejilla (comun.lineas_rio(), medido en "
            "UTM 18N). " + txt_la_vieja(lv)
            + (f" Para la orilla de Cartago en todo el tramo limítrofe usar '{Z_CORR_TODO}' y sus partes dentro y fuera de la rejilla."
               if nat and Z_CORR_TODO in nat else "")
            + " SUPUESTO de trabajo: el eje no es la orilla, y 0–100 m del eje aproxima semiancho del cauce + faja de 30 m + "
            "una celda de rejilla."),
        "ambas orillas / orilla de Cartago / otra orilla": (
            "orilla de Cartago = centro de celda dentro del polígono OSM del municipio; otra orilla = fuera de él. "
            + txt_otra +
            "En el tramo norte el eje OSM del río (vía 749764338) está etiquetado como límite departamental (admin_level=4). "
            "Las cifras de 'ambas orillas' mezclan Cartago con otros municipios (sobre todo Pereira, Risaralda): para "
            "decisiones sobre Cartago usar 'orilla de Cartago'."),
        "tramo junto a / alejado de la cabecera": (
            "corredor 0–100 m dividido según si la celda está a ≤ 250 m (supuesto) del polígono OSM de la cabecera. "
            "Frente a la cabecera, en la otra orilla, está Puerto Caldas (centro poblado de Pereira en el MGN 2024). "
            "El 'tramo alejado de la cabecera' es solo la parte rural del corredor que cae dentro de la rejilla: NO representa "
            "todo el corredor rural del La Vieja, cuya mayor parte queda fuera de la rejilla"
            + (f" y tiene otra composición (orilla de Cartago, 0–100 m, fuera de la rejilla: {_pct_clases(nat[Z_CORR_FUERA], ('arbolado', 'pasto', 'cultivo', 'agua'))})"
               if nat and Z_CORR_FUERA in nat else "") + "."),
        "pasto y cultivo (columnas)": (
            "el reparto entre pasto (clase 30) y cultivo (clase 40) puede estar confundido en el valle plano al occidente y "
            "suroccidente de la cabecera (patrón compatible con el artefacto de 'hard borders' del PUM v2.0, §4; la clase 30 "
            "puede contener cultivos sin cosecha en 2021). Ver la limitación completa en fuentes/rejilla/cob_pasto.json y "
            "cob_cultivo.json. La suma pasto + cultivo es más fiable que cada clase por separado."),
        "arbustos y humedal (columnas)": (
            "0 significa que WorldCover no asignó esa clase a ningún píxel de la zona, no que no haya arbustales o humedales "
            "en el terreno: los humedales y madreviejas de Cartago reconocidos por la CVC quedan aquí dentro de otras "
            "clases (pasto, agua, arbolado u otras; ver 'hallazgos')."),
        "contexto normativo (no es un límite de estas zonas)": (
            "El art. 83 lit. d) del Decreto-Ley 2811 de 1974 declara bien inalienable e imprescriptible del Estado una "
            "faja paralela al cauce permanente de los ríos 'hasta de treinta metros de ancho' (faja de dominio público), "
            "medida desde el cauce, no desde el eje. La ronda hídrica comprende esa faja y el área de protección o "
            "conservación aferente (Decreto 2245 de 2017, que adiciona la sección 3A al Decreto 1076 de 2015, art. "
            "2.2.3.2.3A.2), y su acotamiento corresponde a la autoridad ambiental competente (en el Valle del Cauca, la CVC). "
            "Ninguna de estas zonas ni de estas capas la reemplaza. Textos oficiales en 'normas_citadas' (Gestor Normativo "
            "de Función Pública)."),
    }
    if nat:
        d["zonas '(10 m)'"] = (
            "calculadas sobre una ventana ampliada de la misma tesela N03W078 (leída solo para estos resúmenes; no cambia la "
            "rejilla común ni las capas publicadas), contando píxeles de 10 m cuyo centro cae en la zona. "
            f"'{Z_MUN_COMPLETO}': polígono OSM completo del municipio. '{Z_CORR_TODO}': píxeles a ≤ 100 m del eje OSM COMPLETO "
            "del La Vieja (vías 749764338 + 1126843631 de fuentes/osm-base.json) y dentro del polígono OSM del municipio. "
            f"Control: '{Z_MUN_DENTRO_10M}' reproduce las cifras de '{Z_MUN}' "
            f"({_pct_clases(nat[Z_MUN_DENTRO_10M])}), porque cada celda es la media exacta de 3×3 píxeles.")
    if Z_DANE in info.get("zonas", []):
        d[Z_DANE] = ("sector urbano del MGN 2024 del DANE que contiene el nodo OSM de Zaragoza (el DANE lo incluye en la zona "
                     "urbana 'Cabecera municipal' de Cartago). Límite independiente de WorldCover; incluye una franja a lo "
                     "largo de la vía que lo une con la ciudad. DANE, CC BY 4.0.")
        d[Z_DANE_SUR] = ("el mismo sector DANE recortado al sur de la latitud 4,7065° (SUPUESTO: corte donde la franja vial se "
                         "une al núcleo de Zaragoza). Es la zona independiente recomendada para comparar Zaragoza; "
                         + txt_corte_zaragoza(sens))
    return d


NOTAS_ZONA = {
    Z_HUELLA: "construido y demás clases por construcción (zona definida con los mismos píxeles construidos); no comparable",
}


def resumir(pct, mascaras, notas=None):
    notas = {**NOTAS_ZONA, **(notas or {})}
    res = {}
    for nombre, m in mascaras.items():
        fila = {"celdas": int(m.sum())}
        for clave, v in pct.items():
            x = v[m & np.isfinite(v)]
            fila[clave] = round(float(x.mean()), 2) if x.size else None
        if nombre in notas:
            fila["nota"] = notas[nombre]
        res[nombre] = fila
    return res


# ---------------------------------------------------------------- metadatos

def _proc_comun(verif):
    return [
        "Lectura por ventana del COG público de la tesela N03W078 (rejilla común + 0,01°), sin descargar la tesela completa.",
        "Máscara binaria de la clase (1 = clase, 0 = otra clase, sin dato = código 0 de WorldCover).",
        "Remuestreo por promedio a la rejilla común de 0,00025° (≈27,7 m): cada celda es la media de 3×3 píxeles de WorldCover (rejillas anidadas); × 100 = porcentaje de la celda.",
        f"Verificación: diferencia máxima frente al promedio exacto 3×3 = {verif['dif_max_vs_bloques_pct']} puntos porcentuales.",
        "Solo para los resúmenes '(10 m)' de 'por_zona' (municipio completo y corredor del La Vieja en todo el tramo limítrofe): ventana ampliada de la misma tesela que contiene todo el municipio, idéntica píxel a píxel a la de la rejilla en el solape; % = conteo de píxeles de 10 m. No cambia la rejilla ni las capas.",
    ]


def _txt_rejilla_municipios(info):
    comp = info.get("rejilla_por_municipio_dane_pct")
    if not comp:
        return "al otro lado de los ríos La Vieja y Cauca"
    return "según el MGN 2024 del DANE, la rejilla es " + ", ".join(f"{k} {fmt(v)} %" for k, v in comp.items())


def _lim_comun(info, cob=False):
    cobertura = (f"solo cubre el {fmt(info['municipio_pct_en_rejilla'])} % del municipio de Cartago "
                 f"({fmt(info['municipio_osm_km2_en_rejilla'])} de {fmt(info['municipio_osm_km2'])} km² del polígono OSM; "
                 "faltan el sur y el oriente rurales y una franja al norte)")
    if cob:
        ult = (f"La rejilla incluye terrenos de otros municipios ({_txt_rejilla_municipios(info)}) y {cobertura}: las "
               "'estadisticas' de este archivo (min, media, max, celdas) son de toda la rejilla, no de Cartago. Las cifras de "
               "Cartago están en 'estadisticas_zonas' (parte del municipio dentro de la rejilla, cabecera y, si se pudo leer "
               "la ventana ampliada, municipio completo a 10 m).")
    else:
        ult = (f"La rejilla incluye terrenos de otros municipios ({_txt_rejilla_municipios(info)}) y {cobertura}: las "
               f"estadísticas de 'extension' no son del municipio, y tampoco lo es la zona '{Z_MUN}' de 'por_zona'. Para cifras "
               f"municipales usar '{Z_MUN_COMPLETO}'; para el corredor del río, las zonas 'orilla de Cartago' (y las '(10 m)' "
               "para todo el tramo limítrofe).")
    return [
        "Mapa clasificado por aprendizaje automático: exactitud global declarada 76,7 ± 0,5 % (Suramérica 77,9 ± 1,1 %; ESA WorldCover PUM v2.0, tabla 4); en una celda concreta puede haber errores de clase.",
        "Representa el año 2021; no muestra cambios posteriores.",
        "No comparable con WorldCover 2020 (v100): el algoritmo cambió y las diferencias entre ambos mapas mezclan cambios reales con cambios de método.",
        "Cada píxel de 10 m recibe una sola clase (la dominante): el porcentaje cuenta píxeles clasificados, no la superficie real de cada cobertura.",
        "Cada celda es la media de 3×3 píxeles, así que solo toma valores múltiplos de 100/9 ≈ 11,1 % (0; 11,1; 22,2; … 100).",
        ult,
    ]


def lim_humedales(hist_rejilla):
    """Limitación sobre humedales: la ausencia de las clases 20 y 90 es del clasificador, no del terreno."""
    n20, n90 = hist_rejilla.get(20, 0), hist_rejilla.get(90, 0)
    t = ("WorldCover no clasifica como humedal herbáceo (clase 90) ni como arbustos (clase 20) ningún píxel de la rejilla; "
         if n20 == 0 and n90 == 0 else
         f"WorldCover clasifica muy pocos píxeles de la rejilla como humedal herbáceo ({n90}) o arbustos ({n20}); ")
    return t + ("eso describe al clasificador, no al terreno. Los humedales y madreviejas de Cartago reconocidos por la CVC "
                "(p. ej., La Culebrera junto al La Vieja y La Zapata en las comunas 6 y 7) no aparecen como humedal: quedan "
                "dentro de otras clases (pasto, agua, arbolado u otras; un humedal cartografiado en OSM resultó pasto y "
                "arbolado). Para decisiones sobre humedales usar el inventario y los planes de manejo de la CVC (ver "
                "'referencias_humedales'), no este mapa.")


def _refs_humedales():
    return {"humedales_cvc_en_cartago": HUMEDALES_CVC, "inventario_cvc": INVENTARIO_HUMEDALES_CVC}


def meta_capa(clave, por_zona, verif, def_zonas, agua_eje_vieja, fuentes_aux, ctx):
    lim_c = _lim_comun(ctx["info"])
    base = {
        "unidad": "%",
        "fuente": FUENTE,
        "fuentes_auxiliares": fuentes_aux,
        "periodo": "2021 (enero–diciembre)",
        "resolucion_original_m": 10,
        "procesamiento": _proc_comun(verif),
        "rango_visual": [0, 100],
        "por_zona": por_zona,
        "por_zona_definicion": def_zonas,
        "hallazgos": ctx["hallazgos"],
        "normas_citadas": NORMAS,
        "referencias_humedales": _refs_humedales(),
    }
    if clave == "arbolado":
        return base | {
            "titulo": "Área clasificada como arbolado (ESA WorldCover 2021)",
            "descripcion": "Porcentaje de cada celda de unos 28 m cuyos píxeles de 10 m el mapa satelital ESA WorldCover 2021 clasifica como arbolado. Señala dónde dominan los árboles (bosques de galería, arbolado urbano denso, plantaciones); no mide la copa de los árboles.",
            "limitaciones": lim_c + [
                "No es fracción de copa (dosel): un píxel 'arbolado' es un área dominada por árboles con cobertura ≥ 10 %, y debajo puede haber pasto, construcciones o agua, incluso con más densidad que los árboles (PUM v2.0, tabla 3). Sobrestima la copa en potreros con árboles dispersos y en bosques abiertos, y la subestima donde los árboles de calles y patios quedan dentro de píxeles construidos. No sirve para medir metas de cobertura de copa por barrio.",
                "Incluye plantaciones forestales y cultivos arbóreos (PUM v2.0, tabla 3): no distingue bosque natural de plantación.",
                "El café y otros cultivos perennes leñosos pueden quedar como arbolado o arbustos según su porte.",
            ],
            "paleta": ["#f7fcf5", "#c7e9c0", "#74c476", "#238b45", "#00441b"],
            "interpretacion": "100 % = los 9 píxeles de 10 m de la celda están clasificados como arbolado (cada uno dominado por árboles con cobertura ≥ 10 %); no equivale a dosel completo. 0 % = ningún píxel clasificado como arbolado, aunque puede haber árboles aislados dentro de píxeles de otra clase. No se aplican umbrales normativos: no hay en esta capa una meta de cobertura arbórea verificada para Cartago.",
            "clase_worldcover": {"codigo": 10, "nombre": "Tree cover"},
        }
    if clave == "construido":
        return base | {
            "titulo": "Área clasificada como construida (ESA WorldCover 2021)",
            "descripcion": "Porcentaje de cada celda de unos 28 m cuyos píxeles de 10 m el mapa satelital ESA WorldCover 2021 clasifica como construidos (edificaciones, vías y otras estructuras). Indica qué tan edificado está cada lugar.",
            "limitaciones": lim_c + [
                "La clase 'Built-up' incluye edificios, vías y estructuras como vías férreas; excluye parques y escenarios deportivos, y los botaderos y canteras se clasifican como suelo desnudo (PUM v2.0, tabla 3).",
                "Vías angostas y viviendas dispersas bajo árboles pueden no detectarse; los invernaderos se cuentan como construidos.",
                "No es un mapa catastral: no sirve para delimitar predios ni licencias.",
            ],
            "paleta": ["#fff5eb", "#fdd0a2", "#fd8d3c", "#d94801", "#7f2704"],
            "interpretacion": "100 % = los 9 píxeles de 10 m de la celda están clasificados como construidos; 0 % = ninguno. No mide la huella exacta de las edificaciones. Sin umbrales normativos.",
            "clase_worldcover": {"codigo": 50, "nombre": "Built-up"},
        }
    return base | {
        "titulo": "Agua superficial permanente (ESA WorldCover 2021)",
        "descripcion": "Porcentaje de cada celda de unos 28 m cuyos píxeles de 10 m el mapa satelital ESA WorldCover 2021 clasifica como agua la mayor parte del año (ríos, lagos, embalses). Muestra el cauce visible de los ríos La Vieja y Cauca y los cuerpos de agua.",
        "limitaciones": lim_c + [
            "La clase 'Permanent water bodies' exige agua durante más de 9 meses del año (PUM v2.0, tabla 3): no representa zonas inundables ni la ronda hídrica.",
            f"Los tramos angostos del cauce o cubiertos por el dosel de la vegetación ribereña pueden clasificarse como arbolado (la clase arbolado admite agua bajo el dosel, PUM v2.0) u otra clase, por lo que el río aparece interrumpido: a ≤ 30 m del eje OSM del río La Vieja solo el {fmt(agua_eje_vieja)} % de la superficie es agua en este mapa. No sirve para delimitar el cauce.",
            "Quebradas y canales de pocos metros de ancho no se detectan a 10 m.",
            ctx["lim_humedales"],
        ],
        "paleta": ["#f7fbff", "#c6dbef", "#6baed6", "#2171b5", "#08306b"],
        "interpretacion": "100 % = los 9 píxeles de 10 m de la celda están clasificados como agua permanente; 0 % = ninguno. Sin umbrales normativos. No equivale a la faja de dominio público del art. 83 lit. d) del Decreto-Ley 2811 de 1974 (faja paralela al cauce permanente, hasta de 30 m de ancho, medida desde el cauce) ni a la ronda hídrica, que comprende esa faja y el área de protección o conservación aferente y cuyo acotamiento corresponde a la autoridad ambiental competente (CVC; Decreto 2245 de 2017). Ninguna de las dos se deriva de esta capa.",
        "clase_worldcover": {"codigo": 80, "nombre": "Permanent water bodies"},
    }


LIM_PASTO_CULTIVO = (
    "Posible confusión entre pasto y cultivo en el valle plano al occidente y suroccidente de la cabecera: una mancha "
    "continua de clase 30 (pasto) con bordes curvos atraviesa lotes rectangulares de clase 40 (cultivo), patrón compatible "
    "con el artefacto de 'hard borders' que el PUM v2.0 (§4) reconoce en zonas de alta confusión entre clases. Además, por "
    "definición (PUM v2.0, tabla 3), la clase 30 puede contener tierras de cultivo sin cosecha ni periodo de suelo desnudo "
    "en el año de referencia. SUPUESTO no verificado: parte de esa mancha podría ser caña de azúcar u otro cultivo de ciclo "
    "largo. Antes de usar el reparto pasto/cultivo para decisiones, contrastar con series multitemporales de Sentinel-2 o con "
    "información de la CVC o de los ingenios.")


def meta_cob(cod, valores, pix_rejilla, pix_ventana, verif, ctx):
    clave, nombre = CLASES[cod]
    x = valores[np.isfinite(valores)]
    lim = _lim_comun(ctx["info"], cob=True)
    if clave in ("pasto", "cultivo"):
        lim = lim + [LIM_PASTO_CULTIVO]
    if clave == "cultivo":
        lim = lim + ["La clase 40 es cultivo anual (cosechable al menos una vez en 12 meses); los cultivos perennes leñosos (café, frutales) van como arbolado o arbustos (PUM v2.0, tabla 3)."]
    if clave == "suelo":
        lim = lim + ["Incluye botaderos y sitios de extracción (canteras), que WorldCover clasifica como suelo desnudo (PUM v2.0, tabla 3)."]
    hist_mun = ctx.get("hist_mun")
    if pix_rejilla == 0:
        donde = ("" if pix_ventana == 0 else
                 f" En el margen de 0,01° de la ventana leída, fuera de la rejilla, hay {pix_ventana} píxeles de esta clase.")
        en_mun = (f" En el municipio completo (ventana ampliada) hay {hist_mun.get(cod, 0)} píxeles de 10 m de esta clase."
                  if hist_mun is not None else "")
        lim = lim + [f"WorldCover no clasifica ningún píxel de la rejilla como {nombre} (clase {cod}): la capa es toda 0.{donde}"
                     f"{en_mun} Eso describe al clasificador, no al terreno: 0 = 'WorldCover no asignó esta clase', no "
                     "'no hay' ni 'sin dato'. Se conserva para documentar esa ausencia."]
    if clave == "humedal":
        lim = lim + [ctx["txt_ausentes"]]
    elif clave in ("arbustos", "pasto"):
        lim = lim + [ctx["lim_humedales"]]
    # cifras de Cartago (las 'estadisticas' son de toda la rejilla)
    ez = {}
    for z in (Z_MUN, "Cabecera municipal (OSM)", Z_MUN_COMPLETO, Z_MUN_FUERA):
        fila = ctx["por_zona_todas"].get(z)
        if fila is not None:
            ez[z] = {"media_pct": fila.get(clave), "celdas": fila.get("celdas")}
            if fila.get("pixeles_10m") is not None:
                ez[z]["pixeles_10m"] = fila["pixeles_10m"]
                ez[z]["area_km2"] = fila["area_km2"]
    meta = {
        "nombre": f"cob_{clave}",
        "titulo": f"Área clasificada como {nombre} (ESA WorldCover 2021)",
        "publicada": False,
        "nota": "Arreglo de trabajo en fuentes/rejilla/ (no se publica en datos/capas/). float32 de 428 × 520 en la rejilla común (fila 0 = norte), NaN = sin dato.",
        "unidad": "%",
        "clase_worldcover": {"codigo": cod, "nombre": NOMBRE_EN[cod]},
        "fuente": FUENTE,
        "periodo": "2021 (enero–diciembre)",
        "resolucion_original_m": 10,
        "procesamiento": _proc_comun(verif),
        "limitaciones": lim,
        "estadisticas": {"ambito": "toda la rejilla común (incluye terrenos de otros municipios; ver limitaciones)",
                         "min": round(float(x.min()), 4), "media": round(float(x.mean()), 4), "max": round(float(x.max()), 4),
                         "celdas_con_la_clase": int((x > 0).sum()), "celdas": int(x.size),
                         "pixeles_10m_de_la_clase_en_la_rejilla": int(pix_rejilla),
                         "pixeles_10m_de_la_clase_en_la_ventana": int(pix_ventana)},
        "estadisticas_zonas": ez,
        "estadisticas_zonas_definicion": ("media_pct = % del área de la zona clasificada en esta clase. Zonas definidas en "
                                          "'por_zona_definicion' de datos/capas/arbolado.json; las '(10 m)' son conteos de "
                                          "píxeles de 10 m sobre una ventana ampliada de la misma tesela."),
        "fecha_proceso": date.today().isoformat(),
    }
    if clave in ("humedal", "arbustos", "pasto"):
        meta["referencias_humedales"] = _refs_humedales()
    return meta


# ---------------------------------------------------------------- verificaciones

def celda(lat, lon):
    f = int((comun.NORTE - lat) / comun.RES)
    c = int((lon - comun.OESTE) / comun.RES)
    return f, c


def decodificar_png(nombre, escala, desp):
    from PIL import Image
    a = np.asarray(Image.open(os.path.join(comun.CAPAS, f"{nombre}.png"))).astype(np.int64)
    v = a[..., 0] * 256 + a[..., 1]
    out = np.where(v == 0, np.nan, (v - 1) * escala + desp)
    return out


def main():
    t0 = time.time()
    arr, tr, crs, nodata = descargar_ventana()
    log(f"ventana {arr.shape}, origen ({tr.c:.6f}, {tr.f:.6f}), paso {tr.a:.10f}°, nodata={nodata}")
    cods, cuentas = np.unique(arr, return_counts=True)
    hist = {int(k): int(v) for k, v in zip(cods, cuentas)}
    log("histograma de clases en la ventana:", hist)
    fuera = {k: v for k, v in hist.items() if k not in CLASES and k != 0}
    if fuera:
        log(f"AVISO: clases no contempladas presentes en la ventana: {fuera}")

    pct, exacto, alineado, valido = fracciones(arr, tr, crs, nodata)
    dif = max(float(np.nanmax(np.abs(pct[k] - exacto[k]))) for k in pct) if alineado else None
    log(f"rejillas anidadas: {alineado}; diferencia máx. promedio GDAL vs bloques 3×3: {dif}")
    suma = sum(pct.values())
    log(f"suma de las 8 clases: min {np.nanmin(suma):.4f} max {np.nanmax(suma):.4f}; celdas sin dato: {int(np.isnan(suma).sum())}")
    # píxeles nativos dentro de la rejilla (sub-ventana anidada)
    k_ = int(round(comun.RES / tr.a))
    c_ = int(round((comun.OESTE - tr.c) / tr.a))
    r_ = int(round((tr.f - comun.NORTE) / (-tr.e)))
    sub = arr[r_:r_ + k_ * comun.ALTO, c_:c_ + k_ * comun.ANCHO]
    hist_rejilla = {cod: int((sub == cod).sum()) for cod in CLASES}
    log(f"píxeles por clase dentro de la rejilla [{r_}:{r_ + k_ * comun.ALTO}, {c_}:{c_ + k_ * comun.ANCHO}]: {hist_rejilla}")
    multiplos = max(float(np.nanmax(np.abs(v * 9 / 100 - np.round(v * 9 / 100)))) for v in pct.values())
    log(f"desviación máx. respecto de múltiplos de 1/9: {multiplos:.2e}")

    # 3. DANE
    dane = descargar_dane()

    # 4. Zaragoza (antes de los resúmenes, para que comun.comunas() use la huella derivada)
    feature, zinfo = huella_zaragoza(arr, tr, dane)
    log("Zaragoza:", json.dumps(zinfo, ensure_ascii=False))
    ruta_z = os.path.join(comun.DATOS, "zaragoza.json")
    zaragoza_escrito = False
    if 0.05 <= zinfo["area_km2"] <= 3.0 and not zinfo["toca_borde_ventana"]:
        tmp = ruta_z + ".tmp"
        comun.guardar_json(tmp, feature)
        os.replace(tmp, ruta_z)
        zaragoza_escrito = True
        log(f"escrito {os.path.relpath(ruta_z, comun.RAIZ)} ({zinfo['area_km2']} km²)")
    else:
        log(f"NO se escribe zaragoza.json: área {zinfo['area_km2']} km² fuera de [0,05; 3] o toca el borde")
        if os.path.exists(ruta_z):
            log("AVISO: existe un zaragoza.json previo que no corresponde a esta ejecución")

    # 6. resúmenes
    mascaras, d_vieja, zinfo_zonas = zonas_resumen(dane)
    zinfo_zonas["zonas"] = list(mascaras)
    notas = {
        Z_MUN: (f"solo el {fmt(zinfo_zonas['municipio_pct_en_rejilla'])} % del municipio ({fmt(zinfo_zonas['municipio_osm_km2_en_rejilla'])} "
                f"de {fmt(zinfo_zonas['municipio_osm_km2'])} km²; excluye el sur y el oriente rurales): NO son cifras municipales; "
                f"ver '{Z_MUN_COMPLETO}'"),
        Z_LEJOS: "solo la parte rural del corredor que cae dentro de la rejilla; no representa todo el corredor rural del La Vieja",
    }
    sens = sensibilidad_corte_zaragoza(pct, dane)
    if sens:
        con = [v["construido"] for v in sens.values()]
        notas[Z_DANE_SUR] = (f"construido entre {fmt(min(con))} y {fmt(max(con))} % según el corte supuesto "
                             f"({fmt(min(CORTES_ZARAGOZA), 3)}°–{fmt(max(CORTES_ZARAGOZA), 3)}°); usar el rango, no el valor central")
    por_zona = resumir(pct, mascaras, notas)

    # 6b. municipio completo y corredor del La Vieja en todo el tramo limítrofe, a 10 m (ventana ampliada de la
    #     misma tesela; solo para estos resúmenes, no cambia la rejilla ni las capas)
    mun_geom = comun._poligono(comun.osm()["municipio"])
    vm = ventana_municipio(mun_geom, arr, tr)
    pz_nat, nat_info, hist_mun = None, None, None
    if vm is not None:
        pz_nat, nat_info = zonas_nativas(*vm, mun_geom)
        hist_mun = nat_info["hist_municipio_10m"]
        dif_ctl = max(abs(pz_nat[Z_MUN_DENTRO_10M][k] - por_zona[Z_MUN][k]) for k, _ in CLASES.values())
        nat_info["control_dif_max_pp_10m_vs_rejilla"] = round(dif_ctl, 3)
        log(f"control municipio dentro de la rejilla, 10 m frente a rejilla: dif. máx. {dif_ctl:.3f} pp")
        assert dif_ctl < 1.0, "el conteo a 10 m no reproduce la zona municipal de la rejilla"
        nuevo = {}
        for k, v in por_zona.items():
            nuevo[k] = v
            if k == Z_MUN:
                for z in (Z_MUN_COMPLETO, Z_MUN_FUERA, Z_MUN_DENTRO_10M):
                    nuevo[z] = pz_nat[z]
        for z in (Z_CORR_TODO, Z_CORR_DENTRO, Z_CORR_FUERA):
            if z in pz_nat:
                nuevo[z] = pz_nat[z]
        por_zona = nuevo
    hum = humedales_osm(arr, tr, nodata)
    def_zonas = definiciones(zinfo_zonas, zinfo, sens, pz_nat, nat_info)
    txt_aus = txt_ausentes(hist_rejilla, hist_mun, hum, (nat_info or {}).get("clase90_en_municipio"))
    hall = hallazgos(zinfo_zonas, pz_nat, txt_aus, sens)
    agua_eje_vieja = float(np.nanmean(pct["agua"][d_vieja <= 30]))
    fuentes_aux = [FUENTE_OSM] + ([FUENTE_DANE] if dane.get("sector_urbano_zaragoza") or dane.get("municipios") else [])
    ctx = {"info": zinfo_zonas, "hallazgos": hall, "lim_humedales": lim_humedales(hist_rejilla), "txt_ausentes": txt_aus,
           "hist_mun": hist_mun, "por_zona_todas": por_zona}

    verif = {"dif_max_vs_bloques_pct": round(dif, 6) if dif is not None else "rejillas no anidadas"}
    for clave in PUBLICADAS:
        est = comun.guardar_capa(clave, pct[clave], 0.01, 0.0,
                                 meta_capa(clave, por_zona, verif, def_zonas, agua_eje_vieja, fuentes_aux, ctx))
        log(f"capa {clave}: extensión {est['extension']}; cabecera {est['cabecera_urbana']}")
    for cod, (clave, _) in CLASES.items():
        if clave not in PUBLICADAS:
            np.save(os.path.join(comun.REJILLA_NPY, f"cob_{clave}.npy"), pct[clave].astype(np.float32))
            comun.guardar_json(os.path.join(comun.REJILLA_NPY, f"cob_{clave}.json"),
                               meta_cob(cod, pct[clave], hist_rejilla[cod], hist.get(cod, 0), verif, ctx))
            log(f"npy cob_{clave}: media {np.nanmean(pct[clave]):.2f} %, máx {np.nanmax(pct[clave]):.1f} %, "
                f"píxeles en la rejilla {hist_rejilla[cod]} (en la ventana {hist.get(cod, 0)})")

    # ------------------------------------------------ verificaciones
    log("\n=== VERIFICACIONES ===")
    for clave in PUBLICADAS:
        dec = decodificar_png(clave, 0.01, 0.0)
        npy = comun.cargar_capa(clave)
        ok_nan = np.array_equal(np.isnan(dec), np.isnan(npy))
        dmax = float(np.nanmax(np.abs(dec - npy)))
        log(f"PNG vs npy {clave}: NaN iguales={ok_nan}, dif máx={dmax:.4f} (≤0,005 esperado)")
        assert ok_nan and dmax <= 0.0051
        assert np.nanmin(npy) >= 0 and np.nanmax(npy) <= 100.0001
    assert multiplos < 1e-3, "las fracciones deberían ser múltiplos de 1/9"
    from shapely.geometry import LineString
    pista = LineString([(lo, la) for la, lo in comun.osm()["pista"]]).interpolate(0.5, normalized=True)
    puntos = {
        "Parque Bolívar": (4.7497, -75.9132),
        "Aeropuerto Santa Ana: punto dado junto a la pista (no es la plataforma)": (4.7601, -75.9545),
        "Pista: punto medio real del eje OSM (aeroway=runway)": (round(pista.y, 5), round(pista.x, 5)),
        "Rural oeste (hacia el Cauca)": (4.7200, -75.9700),
        "Zaragoza (nodo OSM)": ZARAGOZA_NODO,
    }
    for nom, (la, lo) in puntos.items():
        f, c = celda(la, lo)
        vent = {k: round(float(np.nanmean(v[max(f - 1, 0):f + 2, max(c - 1, 0):c + 2])), 1) for k, v in pct.items()}
        log(f"{nom} ({la}, {lo}) celda[{f},{c}] media 3×3: {vent}")
    lat_c, lon_c = comun.centros_celdas()
    cerca_pb = np.hypot((lon_c + 75.9132) * 111320 * np.cos(np.radians(4.7497)), (lat_c - 4.7497) * 110574) <= 300
    log("centro (≤300 m del Parque Bolívar): " + ", ".join(f"{k} {np.nanmean(v[cerca_pb]):.1f}" for k, v in pct.items()))
    # río: agua cerca del eje frente al resto y frente a la rejilla invertida (prueba norte/sur)
    agua = pct["agua"]
    cerca = d_vieja <= 30
    log(f"agua media a ≤30 m del eje del La Vieja: {np.nanmean(agua[cerca]):.1f} % "
        f"(invertida N/S: {np.nanmean(np.flipud(agua)[cerca]):.1f} %; resto de la rejilla: {np.nanmean(agua[d_vieja > 300]):.2f} %)")
    d_cauca = distancia_rio_m("rio_cauca")
    cc = d_cauca <= 30
    log(f"agua media a ≤30 m del eje del Cauca: {np.nanmean(agua[cc]):.1f} % (invertida N/S: {np.nanmean(np.flipud(agua)[cc]):.1f} %)")
    # alineación: desplazamientos de ±1 celda del agua frente al eje del Cauca (el máximo debe estar en 0,0)
    despl = {(a, b): float(np.nanmean(np.roll(np.roll(agua, a, 0), b, 1)[cc])) for a in (-1, 0, 1) for b in (-1, 0, 1)}
    mejor = max(despl, key=despl.get)
    log(f"alineación con el eje del Cauca: máximo en desplazamiento {mejor} ({despl[mejor]:.1f} %)")
    urb = comun.mascara_urbana()
    con = pct["construido"]
    log(f"construido medio en la cabecera: {np.nanmean(con[urb]):.1f} % (invertida N/S: {np.nanmean(np.flipud(con)[urb]):.1f} %; fuera: {np.nanmean(con[~urb]):.1f} %)")

    # cruce con el conteo nativo a 10 m dentro de la cabecera
    from rasterio.features import rasterize
    cab_nat = rasterize([(comun._poligono(comun.osm()["cabecera"]), 1)], out_shape=arr.shape, transform=tr, fill=0,
                        dtype="uint8").astype(bool)
    nat = {CLASES[k][0]: round(100.0 * float((arr[cab_nat] == k).mean()), 2) for k in CLASES}
    log(f"cabecera, conteo nativo 10 m: arbolado {nat['arbolado']} %, construido {nat['construido']} %, agua {nat['agua']} %")

    # contraste (orientativo) de la mancha de pasto del valle con el NDVI Sentinel-2 2024–2025 de otro producto
    ndvi_chk = None
    if os.path.exists(os.path.join(comun.REJILLA_NPY, "ndvi.npy")):
        ndvi = comun.cargar_capa("ndvi")
        reg = lambda w, e, s, n: (lon_c >= w) & (lon_c <= e) & (lat_c >= s) & (lat_c <= n)  # noqa: E731
        casos = {"pasto, mancha del valle": reg(-75.965, -75.935, 4.705, 4.745) & (pct["pasto"] >= 99),
                 "cultivo, misma caja": reg(-75.965, -75.935, 4.705, 4.745) & (pct["cultivo"] >= 99),
                 "cultivo, valle suroccidente": reg(-75.985, -75.955, 4.69, 4.72) & (pct["cultivo"] >= 99),
                 "pasto, laderas al oriente": reg(-75.90, -75.855, 4.688, 4.73) & (pct["pasto"] >= 99)}
        ndvi_chk = {k: {"celdas": int(m.sum()), "ndvi_medio": round(float(np.nanmean(ndvi[m])), 3)} for k, m in casos.items()}
        log(f"NDVI medio 2024–2025 (orientativo): {ndvi_chk}")

    log("\n=== COBERTURA DEL LA VIEJA (eje OSM completo) ===")
    log(json.dumps(zinfo_zonas.get("la_vieja"), ensure_ascii=False))
    log("\n=== HUMEDALES OSM frente a WorldCover ===")
    log(json.dumps(hum, ensure_ascii=False))
    log("\n=== SENSIBILIDAD DEL CORTE DE ZARAGOZA ===")
    log(json.dumps(sens, ensure_ascii=False))
    log("\n=== HALLAZGOS ===")
    for h in hall:
        log("- " + h)
    log("\n=== CONTEXTO DE LAS ZONAS ===")
    log(json.dumps({k: v for k, v in zinfo_zonas.items() if k != "zonas"}, ensure_ascii=False))
    log("\n=== RESUMEN POR ZONA (% de la zona) ===")
    for nom, fila in por_zona.items():
        log(f"{nom}: " + ", ".join(f"{k} {v}" for k, v in fila.items() if k != "nota"))

    resumen = {"hist": hist, "hist_rejilla": hist_rejilla, "dif": dif, "zaragoza": zinfo,
               "zaragoza_escrito": zaragoza_escrito, "contexto_zonas": zinfo_zonas, "por_zona": por_zona,
               "por_zona_definicion": def_zonas, "cabecera_nativo_10m": nat, "ndvi_orientativo": ndvi_chk,
               "alineacion_cauca": {str(k): round(v, 1) for k, v in despl.items()},
               "ventana_municipio": nat_info, "humedales_osm": hum, "sensibilidad_corte_zaragoza": sens,
               "hallazgos": hall}
    comun.guardar_json(os.path.join(DIR, "resumen_ultima_ejecucion.json"), resumen)
    log(f"\nlisto en {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
