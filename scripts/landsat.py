"""Producto «landsat»: temperatura superficial (LST) y NDVI de Landsat Collection 2 Nivel 2.

FUENTES Y LICENCIAS
  * Landsat Collection 2 Level-2 Science Products (USGS), servidos como COG por
    Microsoft Planetary Computer, colección «landsat-c2-l2»
    (https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2).
      - Landsat 8-9 OLI/TIRS C2 L2 ......... doi:10.5066/P9OGBGM6
      - Landsat 7 ETM+ C2 L2 ................ doi:10.5066/P9C7I13B
      - Landsat 4-5 TM C2 L2 ................ doi:10.5066/P9IAXOVV
    Licencia: dominio público del Gobierno de EE. UU.; el USGS indica que no hay
    restricciones de uso ni redistribución y pide citar la fuente
    («Landsat ... courtesy of the U.S. Geological Survey»).
    https://www.usgs.gov/faqs/are-there-any-restrictions-use-or-redistribution-landsat-data
  * Geometría de la cabecera y de los ríos: OpenStreetMap (ODbL 1.0), vía comun.mascara_urbana() / comun.osm().
  * Capas auxiliares de otros productos del proyecto (se leen de fuentes/rejilla/, NO se descargan aquí):
      - altitud.npy   Copernicus DEM GLO-30 (licencia Copernicus WorldDEM-30, libre con atribución)
      - construido.npy y agua.npy   ESA WorldCover 10 m 2021 v200 (CC BY 4.0)
    Se usan solo para definir la referencia rural (misma franja de altitud que la cabecera, sin
    construcción ni agua) y el «núcleo construido» de la cabecera. Si faltan, el script se detiene.

REFERENCIAS VERIFICADAS
  * Bits de QA_PIXEL (Collection 2): https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands
    y guías LSDS-1619 (L8-9) / LSDS-1618 (L4-7; en L4-7 el bit 2 «cirro» no se usa).
  * Factores de escala: https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products
      ST: K = DN * 0.00341802 + 149.0      SR: ρ = DN * 0.0000275 - 0.2   (DN 0 = relleno)
  * ST_QA (incertidumbre de ST, K) y ST_CDIST (distancia a la nube más cercana marcada en QA_PIXEL, km):
    INT16, relleno −9999, factor 0,01 (LSDS-1619 v5, tabla de bandas; sección «ST intermediate bands»).
    https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/LSDS-1619_Landsat8-9-Collection2-Level2-Science-Product-Guide-v5.pdf
  * Tier 1 = «suitable for time-series analysis», RMSE ≤ 12 m:
    https://www.usgs.gov/landsat-missions/landsat-collection-2-level-1-data
  * Falla del SLC de Landsat 7 el 31-05-2003 (≈22 % de píxeles sin barrer por escena):
    https://www.usgs.gov/faqs/what-landsat-7-etm-slc-data
  * Huecos fijos de ST donde falta la emisividad ASTER GED:
    https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-temperature-data-gaps-due-missing-aster-ged
  * Continuidad de NDVI ETM+ → OLI: Roy, D. P. et al. (2016). Characterization of Landsat-7 to Landsat-8
    reflective wavelength and normalized difference vegetation index continuity. Remote Sensing of
    Environment 185: 57–70.
  * Reanálisis atmosférico del producto ST (verificado 2026-10-01): GEOS-5 FP-IT para adquisiciones hasta el
    31-12-2023 y GEOS-5 IT (GEOS-IT) desde el 1-1-2024. LSDS-1619 v6.0 (mayo de 2024), sección 3 punto 4 y
    secciones 7.2.2-7.2.3; el MTL lo registra en LEVEL2_PROCESSING_RECORD/DATA_SOURCE_REANALYSIS.
    https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/LSDS-1619_Landsat8-9-Collection2-Level2-Science-Product-Guide-v6.pdf
    https://www.usgs.gov/landsat-missions/news/changes-landsat-surface-temperature-atmospheric-auxiliary-data
    Comprobado en los MTL de 009/057: LC08 2023-12-19 → «GEOS-5 FP-IT»; LC08 2024-01-04 → «GEOS-5 IT».
  * El Niño 2023-2024 terminaba en mayo de 2024 (NOAA Climate Prediction Center, ENSO update de mayo de 2024):
    https://www.climate.gov/news-features/blogs/enso/may-2024-enso-update-were-10

MÁSCARA DE NUBES (QA_PIXEL, bit = 1 → se descarta el píxel)
  bit 0 relleno · bit 1 nube dilatada · bit 2 cirro de alta confianza (solo L8/L9)
  bit 3 nube · bit 4 sombra de nube · bit 5 nieve/hielo
  Además se descarta QA = 0 (valor imposible en un píxel con datos) y DN = 0 en ST/SR.
  El bit 7 (agua) no se descarta: se usa solo para construir la máscara de agua.

ZONAS DE RESUMEN (todas fijas en el tiempo)
  cabecera ........ polígono OSM de la cabecera (comun.mascara_urbana()); es heterogéneo: incluye barrios densos
                    y zonas verdes periurbanas, por eso su mediana espacial es inestable.
  núcleo construido  celdas de la cabecera con ≥ 80 % construido según WorldCover 2021 (supuesto).
  periurbano verde   celdas de la cabecera con < 20 % construido según WorldCover 2021.
  rural ........... fuera de la cabecera, a > 500 m de ella, sin agua (bit 7 de QA_PIXEL en ≥ 50 % de las
                    observaciones y WorldCover agua < 50 %), con construido < 10 % y altitud a ± 30 m de la
                    mediana de la cabecera (supuestos; evita comparar la ciudad con las colinas más frescas
                    de 1 000-1 300 m del oriente).

PASOS
  (a) capa «lst» (prioridad)
    1. Búsqueda STAC (bbox de la rejilla común, 2000-2025) guardada en
       fuentes/landsat/stac_items.json (las URL se firman en el momento de leer).
    2. Escenas Landsat 8 y 9, Tier 1, ruta/fila WRS-2 009/057, 2022-01-01 a 2025-12-31.
    3. Para cada escena se lee SOLO la ventana del área (+0,005°) de QA_PIXEL; se calcula
       el % despejado de la rejilla. Con ≥ MIN_DESPEJADO % se leen también ST_B10, ST_CDIST y ST_QA.
       Cada ventana leída se guarda en fuentes/landsat/escenas/ (caché reejecutable).
    4. LST °C = DN*0.00341802 + 149.0 − 273.15 en píxeles despejados; se lleva a la rejilla
       común con remuestreo bilineal (GDAL ignora los NaN y renormaliza pesos).
    5. Filtro de nubes no detectadas (supuesto empírico, no normativo): se descarta la escena si ≥ 20 % de
       sus píxeles despejados están > 10 °C por debajo de la referencia (QA_PIXEL deja pasar nubes delgadas y
       bruma). Referencia de la 1.ª pasada: mediana de todas las escenas; luego, el compuesto de las escenas
       aceptadas, y se repite hasta que el conjunto aceptado no cambia (convergencia). Se compara con máscaras
       por píxel basadas en ST_CDIST y ST_QA (tabla de sensibilidad en lst.json); no se adoptan porque, solas,
       no eliminan las escenas frías.
       Procedencia: de cada escena usada se lee su MTL (caché fuentes/landsat/mtl/) y se guarda el reanálisis
       atmosférico del ST (DATA_SOURCE_REANALYSIS), el algoritmo ST y el software; si el MTL no se puede leer,
       el reanálisis se asigna por fecha (GEOS-IT desde el 1-1-2024). Sensibilidad: compuesto por reanálisis.
    6. Mediana por celda de las escenas restantes; n = observaciones válidas por celda
       (fuentes/rejilla/lst_n.npy). Celdas con n < N_MIN → sin dato. Máscara de agua auxiliar
       (frecuencia del bit 7) en fuentes/rejilla/landsat_agua_frec.npy.
    7. guardar_capa('lst', escala=0.01, desplazamiento=-20).
  (b) serie anual 2000-2025 (datos/series/landsat.json)
    1. Por año: 2013-2025 → Landsat 8/9 (ST_B10, SR_B4, SR_B5); 2000-2012 → Landsat 5/7
       (ST_B6, SR_B3, SR_B4). Solo Tier 1, ruta/fila 009/057.
    2. Preselección IGUAL en todos los años: las CANDIDATOS_POR_ANIO escenas de menor eo:cloud_cover;
       se lee su QA_PIXEL y se mide el % despejado sobre la rejilla.
    3. Selección: hasta 6 escenas con ≥ MIN_DESPEJADO %, primero las más despejadas sobre el
       área con máximo 2 por trimestre (para repartirlas en el año) y luego se completan.
       Se aplica el mismo filtro de nubes no detectadas, con el compuesto (a) como referencia;
       una escena descartada se reemplaza por la siguiente candidata.
    4. Por celda, mediana anual de LST (°C) y NDVI = (NIR − Rojo)/(NIR + Rojo) con SR; celdas con menos de
       N_MIN_ANUAL observaciones → NaN. Rejillas en fuentes/rejilla/lst_<año>.npy, ndvi_<año>.npy (float32, NaN)
       y n.º de observaciones en lst_n_<año>.npy, ndvi_n_<año>.npy (uint8).
    5. Métricas por año y por variante: mediana y media del polígono, mediana del núcleo construido,
       mediana por escena; rural con la referencia de altitud; isla_calor = urbana − rural.
       Año «confiable» si tiene ≥ 4 escenas en ≥ 3 trimestres y ≥ 30 % de la cabecera con dato.
    6. Solape 2013-2016: compuestos Landsat 7 y Landsat 8 del mismo periodo y misma hora de paso → efecto
       de sensor (L8 − L7) por métrica con IC 95 % bootstrap por escenas. Serie «armonizada» = años
       2000-2012 + ese efecto (supuesto: el efecto estimado con L7 vale también para L5).
    7. Tendencias por tramo (2000-2012 L5/L7, 2013-2025 L8/9, 2000-2025 armonizada) y por variante:
       Sen (IC 95 %) + Mann-Kendall (τ de Kendall año–valor) y MCO con IC 95 % y p-valor (scipy), por década.
       Se publica el RANGO entre variantes y una lectura automática; no una única cifra con p-valor.
       En el tramo armonizado la conclusión debe sostenerse también con los extremos del IC del efecto de sensor.
    8. Control con un solo sensor: la misma serie solo con Landsat 7 en 2000-2016 (no escribe rejillas), para ver si
       el salto de 2012-2013 aparece también sin cambio de sensor (su hora de paso se retrasa con los años).
    9. Zona «construida ya en 2000» (supuesto): celdas de la cabecera con NDVI medio 2000-2002 < 0,25 (rejillas
       ndvi_2000..2002.npy de esta serie). Variante adicional de la isla y de la LST urbana con polígono fijo y
       estado inicial, frente al núcleo WorldCover 2021, que condiciona sobre el estado final.
   10. Métricas por escena (variante mediana_por_escena): solo escenas «aptas» con ≥ 30 % de la cabecera despejada,
       ≥ 30 % de la referencia rural con dato y < 20 % de la cabecera más de 10 °C por debajo del compuesto (supuestos).
   11. Controles y síntesis: NDVI rural y periurbano como control del NDVI urbano; tramo L8/9 2013-2023 (solo GEOS
       FP-IT) y regresión con escalón en 2024; regresión por escena del control L7 (isla ~ periodo + hora de paso +
       mes); síntesis del salto 2012-2013 («sintesis_salto_2012_2013» y «hallazgos»).

SALIDAS
  datos/capas/lst.png + lst.json              capa publicable (°C, escala 0,01, desplazamiento −20)
  fuentes/rejilla/lst.npy, lst_n.npy          rejilla float32 y n.º de observaciones por celda
  fuentes/rejilla/landsat_agua_frec.npy       frecuencia del bit «agua» de QA_PIXEL (máscara rural)
  fuentes/rejilla/lst_<año>.npy, ndvi_<año>.npy, lst_n_<año>.npy, ndvi_n_<año>.npy   2000-2025
  datos/series/landsat.json                   serie anual, solape de sensores, tendencias y advertencias
  fuentes/landsat/                            caché STAC, ventanas leídas (escenas/), metadatos MTL (mtl/), listas de
                                              escenas y log

USO
  .venv/bin/python scripts/landsat.py                 # (a) y (b)
  .venv/bin/python scripts/landsat.py --solo lst      # solo (a)
  .venv/bin/python scripts/landsat.py --solo serie [--desde 2013]   # requiere (a) hecho; reescribe la serie
                                                                    # solo con los años pedidos
  Todo lo leído queda en caché: una segunda ejecución completa no descarga nada y da salidas idénticas.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import warnings
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comun  # noqa: E402

import numpy as np  # noqa: E402

DIR = os.path.join(comun.FUENTES, "landsat")
DIR_ESC = os.path.join(DIR, "escenas")
DIR_MTL = os.path.join(DIR, "mtl")
STAC_CACHE = os.path.join(DIR, "stac_items.json")
LOG = os.path.join(DIR, "landsat.log")
os.makedirs(DIR_ESC, exist_ok=True)
os.makedirs(DIR_MTL, exist_ok=True)

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
BBOX = [comun.OESTE, comun.SUR, comun.ESTE, comun.NORTE]
MARGEN = 0.005            # grados alrededor de la rejilla al leer ventanas
MIN_DESPEJADO = 10.0      # % mínimo de la rejilla despejado para usar una escena (supuesto)
N_MIN = 3                 # observaciones mínimas por celda en el compuesto LST (supuesto)
N_MIN_ANUAL = 3           # observaciones mínimas por celda en las rejillas anuales (supuesto)
CANDIDATOS_POR_ANIO = 12  # escenas de menor eo:cloud_cover cuyo QA se revisa por año (igual en todos los años)
MAX_POR_ANIO = 6
MAX_POR_TRIMESTRE = 2
CONF_MIN_ESCENAS = 4      # año confiable: ≥ 4 escenas …
CONF_MIN_TRIMESTRES = 3   # … repartidas en ≥ 3 trimestres …
CONF_MIN_PCT_URBANO = 30.0  # … y ≥ 30 % de la cabecera con dato
FRIO_C = 10.0             # °C por debajo de la referencia que delatan nube no detectada (supuesto)
FRIO_FRAC = 0.20          # fracción de píxeles «fríos» a partir de la cual se descarta la escena (supuesto)
MAX_PASADAS_FILTRO = 20   # pasadas máximas del filtro de nubes no detectadas hasta converger
MIN_CABECERA_ESCENA = 30.0  # métricas por escena: ≥ 30 % de la cabecera despejada (supuesto)
MIN_RURAL_ESCENA = 30.0     # … y ≥ 30 % de la referencia rural con dato (supuesto)
NDVI_CONSTRUIDO_2000 = 0.25  # zona «construida ya en 2000»: NDVI medio 2000-2002 < 0,25 (supuesto)
ANIOS_NDVI_2000 = (2000, 2001, 2002)
GEOS_IT_DESDE = "2024-01-01"  # USGS: el ST usa GEOS-IT en lugar de GEOS FP-IT desde esta fecha de adquisición
RURAL_DIST_M = 500.0      # rural: a más de 500 m de la cabecera
RURAL_ALT_BANDA_M = 30.0  # rural: altitud a ± 30 m de la mediana de la cabecera (supuesto)
RURAL_CONSTRUIDO_MAX = 10.0   # rural: WorldCover construido < 10 % (supuesto)
NUCLEO_CONSTRUIDO_MIN = 80.0  # núcleo construido: ≥ 80 % construido (supuesto)
PERIURB_CONSTRUIDO_MAX = 20.0  # periurbano verde: < 20 % construido
SOLAPE = (2013, 2016)     # años de solape Landsat 7 / Landsat 8 para estimar el efecto de sensor
BOOT = 200                # réplicas bootstrap del efecto de sensor
SIG_P = 0.05
HILOS = 5
UTC_LOCAL = -5            # Colombia, sin horario de verano

ST_ESCALA, ST_DESPL = 0.00341802, 149.0
SR_ESCALA, SR_DESPL = 0.0000275, -0.2
AUX_ESCALA = 0.01         # ST_QA (K) y ST_CDIST (km)
BITS_L89 = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5)
BITS_L457 = (1 << 0) | (1 << 1) | (1 << 3) | (1 << 4) | (1 << 5)
BIT_AGUA = 1 << 7

SENSOR = {"landsat-5": "L5 TM", "landsat-7": "L7 ETM+", "landsat-8": "L8 OLI/TIRS", "landsat-9": "L9 OLI-2/TIRS-2"}


def log(*a):
    txt = " ".join(str(x) for x in a)
    linea = f"[{datetime.now().strftime('%H:%M:%S')}] {txt}"
    print(linea, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def fc(x, dec=1, signo=False):
    """Número con coma decimal para los textos en español."""
    if x is None:
        return "?"
    return (f"{x:+.{dec}f}" if signo else f"{x:.{dec}f}").replace(".", ",")


def fg(x):
    return f"{x:g}".replace(".", ",")


# ------------------------------------------------------------------ catálogo STAC

def buscar_items():
    """Ítems landsat-c2-l2 2000-2025 sobre la rejilla (caché JSON con URL sin firmar)."""
    if os.path.exists(STAC_CACHE):
        return json.load(open(STAC_CACHE, encoding="utf-8"))["items"]
    import pystac_client
    log("Buscando escenas en Planetary Computer (2000-2025), año por año y solo con los campos necesarios…")
    cat = pystac_client.Client.open(STAC_URL)
    claves = ("qa_pixel", "lwir11", "lwir", "red", "nir08")
    campos = {"include": ["id", "properties.datetime", "properties.platform", "properties.landsat:wrs_path",
                          "properties.landsat:wrs_row", "properties.landsat:collection_category",
                          "properties.eo:cloud_cover", "properties.sci:doi"] + [f"assets.{k}.href" for k in claves],
              "exclude": ["links", "geometry", "bbox", "stac_extensions"]}
    items = []
    for anio in range(2000, 2026):
        for intento in range(5):
            try:
                s = cat.search(collections=["landsat-c2-l2"], bbox=BBOX, datetime=f"{anio}-01-01/{anio}-12-31",
                               limit=100, fields=campos)
                lote = list(s.items_as_dicts())
                break
            except Exception as e:  # páginas cortadas por la red lenta
                log(f"  búsqueda {anio} intento {intento + 1}: {type(e).__name__}: {str(e)[:120]}")
                time.sleep(5 * (intento + 1))
        else:
            raise SystemExit(f"No fue posible consultar el catálogo para {anio}")
        for d in lote:
            p, a = d["properties"], d.get("assets", {})
            items.append({
                "id": d["id"], "datetime": p["datetime"], "platform": p["platform"],
                "path": p.get("landsat:wrs_path"), "row": p.get("landsat:wrs_row"),
                "tier": p.get("landsat:collection_category"), "cloud": p.get("eo:cloud_cover"),
                "doi": p.get("sci:doi"),
                "assets": {k: a[k]["href"].split("?")[0] for k in claves if k in a},
            })
        log(f"  {anio}: {len(lote)} ítems")
    items.sort(key=lambda d: d["datetime"])
    comun.guardar_json(STAC_CACHE, {"consulta": {"coleccion": "landsat-c2-l2", "bbox": BBOX, "periodo": "2000-01-01/2025-12-31",
                                                 "fecha": datetime.now().isoformat(timespec="seconds")}, "items": items})
    log(f"  {len(items)} ítems")
    return items


def fecha(it):
    return datetime.fromisoformat(it["datetime"].replace("Z", "+00:00"))


def hora_local(it):
    return fecha(it) + timedelta(hours=UTC_LOCAL)


def minutos_locales(it):
    h = hora_local(it)
    return round(h.hour * 60 + h.minute + h.second / 60, 2)


def es_l89(it):
    return it["platform"] in ("landsat-8", "landsat-9")


def banda_st(it):
    return "lwir11" if es_l89(it) else "lwir"


def es_009057_t1(it):
    return it["tier"] == "T1" and it["path"] == "009" and it["row"] == "057"


# ------------------------------------------------------------------ lectura con caché

# Bandas auxiliares del producto ST que la caché STAC no guarda: su URL se deriva de la de la banda ST
# (mismo directorio, mismo prefijo de producto; nombres de archivo de LSDS-1619 / LSDS-1618).
SUFIJO_AUX = {"cdist": "_ST_CDIST.TIF", "stqa": "_ST_QA.TIF"}


def href_banda(it, clave):
    if clave in SUFIJO_AUX:
        base = it["assets"].get(banda_st(it))
        if not base:
            return None
        sufijo_st = "_ST_B10.TIF" if es_l89(it) else "_ST_B6.TIF"
        return base[: -len(sufijo_st)] + SUFIJO_AUX[clave] if base.endswith(sufijo_st) else None
    return it["assets"].get(clave)


def leer(it, clave):
    """Ventana de una banda: (arr, transform, crs) o None si falla tras reintentos."""
    from affine import Affine
    ruta = os.path.join(DIR_ESC, f"{it['id']}_{clave}.npz")
    if os.path.exists(ruta):
        try:
            z = np.load(ruta, allow_pickle=False)
            return z["arr"], Affine(*z["tr"].tolist()), str(z["crs"])
        except Exception:
            os.remove(ruta)
    import planetary_computer
    href = href_banda(it, clave)
    if not href:
        return None
    for intento in range(4):
        try:
            t0 = time.time()
            url = planetary_computer.sign(href)
            arr, tr, crs, _ = comun.leer_ventana(url, margen_grados=MARGEN)
            tmp = ruta[:-4] + ".tmp.npz"
            np.savez_compressed(tmp, arr=arr, tr=np.array(tr[:6], dtype=np.float64), crs=np.array(crs.to_string()))
            os.replace(tmp, ruta)
            log(f"  leído {it['id']} {clave} {arr.shape} en {time.time() - t0:.1f} s")
            return arr, tr, crs.to_string()
        except Exception as e:  # red lenta / firmas / HTTP 5xx
            log(f"  fallo {it['id']} {clave} intento {intento + 1}: {type(e).__name__}: {str(e)[:160]}")
            time.sleep(5 * (intento + 1))
    return None


def leer_varios(pares):
    """Lee en paralelo [(item, clave)] → dict {(id, clave): resultado}."""
    out = {}
    with ThreadPoolExecutor(HILOS) as ex:
        futuros = {ex.submit(leer, it, c): (it["id"], c) for it, c in pares}
        for f, k in futuros.items():
            out[k] = f.result()
    return out


# ------------------------------------------------------------------ procedencia (MTL)

def reanalisis_por_fecha(it):
    """Reanálisis del ST según la fecha de adquisición (LSDS-1619 v6.0; USGS, cambio del 1-1-2024)."""
    return "GEOS-5 IT" if it["datetime"][:10] >= GEOS_IT_DESDE else "GEOS-5 FP-IT"


def _registro_l2_txt(txt):
    """LEVEL2_PROCESSING_RECORD de un MTL en texto («CLAVE = valor» entre GROUP y END_GROUP)."""
    rec, dentro = {}, False
    for linea in txt.splitlines():
        t = linea.strip()
        if t == "GROUP = LEVEL2_PROCESSING_RECORD":
            dentro = True
        elif t == "END_GROUP = LEVEL2_PROCESSING_RECORD":
            break
        elif dentro and " = " in t:
            k, v = t.split(" = ", 1)
            rec[k.strip()] = v.strip().strip('"')
    return rec or None


def _leer_mtl_cache(it):
    for ext in ("json", "txt"):
        ruta = os.path.join(DIR_MTL, f"{it['id']}_MTL.{ext}")
        if os.path.exists(ruta):
            try:
                txt = open(ruta, encoding="utf-8").read()
                rec = (json.loads(txt)["LANDSAT_METADATA_FILE"]["LEVEL2_PROCESSING_RECORD"] if ext == "json"
                       else _registro_l2_txt(txt))
                if rec:
                    return rec
            except Exception:
                pass
            os.remove(ruta)
    return None


def procedencia(it):
    """Registro de procesamiento Nivel 2 del MTL de la escena (caché fuentes/landsat/mtl/).

    El MTL está junto a las bandas (mismo prefijo de producto): se prueba _MTL.json y, si no existe en el
    almacenamiento (ocurre aunque el ítem STAC lo liste), _MTL.txt. Si no se puede leer, el reanálisis se
    asigna por fecha y se marca el origen."""
    rec = _leer_mtl_cache(it)
    base = it["assets"].get("qa_pixel")
    if rec is None and base and base.endswith("_QA_PIXEL.TIF"):
        import planetary_computer
        import requests
        raiz = base[: -len("_QA_PIXEL.TIF")]
        for ext in ("json", "txt"):
            for intento in range(3):
                try:
                    r = requests.get(planetary_computer.sign(f"{raiz}_MTL.{ext}"), timeout=90)
                    if r.status_code == 404:
                        break
                    r.raise_for_status()
                    ruta = os.path.join(DIR_MTL, f"{it['id']}_MTL.{ext}")
                    with open(ruta + ".tmp", "w", encoding="utf-8") as f:
                        f.write(r.text)
                    os.replace(ruta + ".tmp", ruta)
                    rec = _leer_mtl_cache(it)
                    break
                except Exception as e:  # red lenta / firmas
                    log(f"  fallo MTL {it['id']} ({ext}) intento {intento + 1}: {type(e).__name__}: {str(e)[:100]}")
                    time.sleep(3 * (intento + 1))
            if rec is not None:
                break
    if rec and rec.get("DATA_SOURCE_REANALYSIS"):
        bruto = rec.get("DATA_SOURCE_REANALYSIS")
        # el MTL escribe la misma fuente como «GEOS-5 FP-IT» o «GEOS-5FP-IT»: se normaliza
        rean = "GEOS-5 FP-IT" if "FP-IT" in bruto.replace(" ", "") else ("GEOS-5 IT" if bruto.replace(" ", "").endswith("IT") else bruto)
        return {"reanalisis_st": rean, "algoritmo_st": rec.get("ALGORITHM_SOURCE_SURFACE_TEMPERATURE"),
                "algoritmo_sr": rec.get("ALGORITHM_SOURCE_SURFACE_REFLECTANCE"),
                "aux_atm_sr": rec.get("DATA_SOURCE_WATER_VAPOR"),
                "software_l2": rec.get("PROCESSING_SOFTWARE_VERSION"), "fecha_producto": (rec.get("DATE_PRODUCT_GENERATED") or "")[:10],
                "procedencia_origen": "MTL"}
    return {"reanalisis_st": reanalisis_por_fecha(it), "algoritmo_st": None, "algoritmo_sr": None, "aux_atm_sr": None,
            "software_l2": None, "fecha_producto": None, "procedencia_origen": "asignado por fecha (MTL no disponible)"}


def procedencias(its):
    """procedencia() en paralelo → {id: dict}."""
    with ThreadPoolExecutor(HILOS) as ex:
        return dict(zip([it["id"] for it in its], ex.map(procedencia, its)))


# ------------------------------------------------------------------ máscaras y conversión

def valido_qa(qa, it):
    bits = BITS_L89 if es_l89(it) else BITS_L457
    return (qa != 0) & ((qa & bits) == 0)


def a_rejilla(arr, tr, crs, remuestreo="bilinear"):
    return comun.reproyectar(arr.astype(np.float32), tr, crs, remuestreo=remuestreo)


_URB = None


def urbana():
    global _URB
    if _URB is None:
        _URB = comun.mascara_urbana()
    return _URB


_AUX = {}


def capa_aux(nombre):
    """Rejilla de otro producto del proyecto (fuentes/rejilla/<nombre>.npy); se detiene si falta."""
    if nombre not in _AUX:
        ruta = os.path.join(comun.REJILLA_NPY, f"{nombre}.npy")
        if not os.path.exists(ruta):
            raise SystemExit(f"Falta fuentes/rejilla/{nombre}.npy (capa de otro producto del proyecto): "
                             "ejecute antes su script (worldcover.py / altitud).")
        _AUX[nombre] = np.load(ruta)
    return _AUX[nombre]


def fuente_aux(nombre, uso):
    """Atribución de una capa auxiliar, leída de su propio datos/capas/<nombre>.json."""
    ruta = os.path.join(comun.CAPAS, f"{nombre}.json")
    f = json.load(open(ruta, encoding="utf-8")).get("fuente", {}) if os.path.exists(ruta) else {}
    return {"uso": uso, "capa": f"datos/capas/{nombre}.json", "nombre": f.get("nombre"), "url": f.get("url"),
            "licencia": f.get("licencia"), "cita": f.get("cita")}


def fuentes_secundarias():
    return [
        {"uso": "Polígono de la cabecera (zona urbana y su entorno de 500 m) y ejes de los ríos para verificación",
         "nombre": "OpenStreetMap (vía js/datos-osm.js, comun.mascara_urbana())",
         "url": "https://www.openstreetmap.org/copyright", "licencia": "ODbL 1.0",
         "cita": "© colaboradores de OpenStreetMap"},
        fuente_aux("construido", "Núcleo construido (≥ 80 %) y periurbano verde (< 20 %) de la cabecera; exclusión de "
                                 "celdas construidas (≥ 10 %) de la referencia rural"),
        fuente_aux("agua", "Exclusión de agua (≥ 50 %) de la referencia rural"),
        fuente_aux("altitud", "Referencia rural en la misma franja de altitud que la cabecera (± 30 m de su mediana)"),
    ]


def distancia_a_cabecera_m():
    from scipy.ndimage import distance_transform_edt
    lat, _ = comun.centros_celdas()
    dy = comun.RES * 110574.0
    dx = comun.RES * 111320.0 * np.cos(np.radians(lat.mean()))
    return distance_transform_edt(~urbana(), sampling=(dy, dx))


def mascaras(frec_agua=None):
    """Zonas de resumen: cabecera, núcleo construido, periurbano verde, rural (y la rural amplia anterior)."""
    urb = urbana()
    if frec_agua is None:
        ruta = os.path.join(comun.REJILLA_NPY, "landsat_agua_frec.npy")
        if not os.path.exists(ruta):
            raise SystemExit("Falta la máscara de agua (ejecute primero la parte (a)).")
        frec_agua = np.load(ruta)
    alt, con, agua_wc = capa_aux("altitud"), capa_aux("construido"), capa_aux("agua")
    dist = distancia_a_cabecera_m()
    agua_qa = np.nan_to_num(frec_agua, nan=0.0) >= 0.5
    alt0 = float(np.nanmedian(alt[urb]))
    amplia = (~urb) & (dist > RURAL_DIST_M) & (~agua_qa)
    with np.errstate(invalid="ignore"):
        rural = amplia & (np.nan_to_num(agua_wc, nan=100.0) < 50) & (np.abs(alt - alt0) <= RURAL_ALT_BANDA_M) \
            & (np.nan_to_num(con, nan=100.0) < RURAL_CONSTRUIDO_MAX)
        nucleo = urb & (np.nan_to_num(con, nan=0.0) >= NUCLEO_CONSTRUIDO_MIN)
        periurb = urb & (np.nan_to_num(con, nan=100.0) < PERIURB_CONSTRUIDO_MAX)
    return {"urbana": urb, "nucleo": nucleo, "periurbano": periurb, "rural": rural, "rural_amplia": amplia,
            "alt_cabecera_mediana": alt0,
            "descripcion": {
                "cabecera_celdas": int(urb.sum()),
                "nucleo_celdas": int(nucleo.sum()), "nucleo_frac_cabecera": round(float(nucleo.sum() / urb.sum()), 3),
                "periurbano_celdas": int(periurb.sum()), "periurbano_frac_cabecera": round(float(periurb.sum() / urb.sum()), 3),
                "rural_celdas": int(rural.sum()),
                "rural_altitud_m": [round(alt0 - RURAL_ALT_BANDA_M, 1), round(alt0 + RURAL_ALT_BANDA_M, 1)],
                "cabecera_altitud_p10_p50_p90_m": [round(float(x), 1) for x in np.nanpercentile(alt[urb], [10, 50, 90])],
                "rural_altitud_p10_p50_p90_m": [round(float(x), 1) for x in np.nanpercentile(alt[rural], [10, 50, 90])],
                "rural_amplia_altitud_p10_p50_p90_m": [round(float(x), 1) for x in np.nanpercentile(alt[amplia], [10, 50, 90])],
            }}


def evaluar_qa(it, r):
    """% de la rejilla (y de la cabecera) con píxeles despejados en la escena."""
    qa, tr, crs = r
    ok = valido_qa(qa, it).astype(np.float32)
    g = a_rejilla(ok, tr, crs, "nearest")
    desp = np.nan_to_num(g, nan=0.0) > 0.5
    return round(100.0 * desp.mean(), 2), round(100.0 * desp[urbana()].mean(), 2)


def lst_escena(it, qa_r, st_r, extra=None):
    qa, tr, crs = qa_r
    st, tr2, crs2 = st_r
    assert qa.shape == st.shape and tuple(tr) == tuple(tr2), "QA y ST no alineadas"
    v = valido_qa(qa, it) & (st != 0)
    if extra is not None:
        v &= extra
    c = np.where(v, st.astype(np.float64) * ST_ESCALA + ST_DESPL - 273.15, np.nan).astype(np.float32)
    agua = np.where(v, ((qa & BIT_AGUA) > 0).astype(np.float32), np.nan).astype(np.float32)
    return a_rejilla(c, tr, crs, "bilinear"), a_rejilla(agua, tr, crs, "nearest")


def ndvi_escena(it, qa_r, red_r, nir_r):
    qa, tr, crs = qa_r
    red = red_r[0].astype(np.float64) * SR_ESCALA + SR_DESPL
    nir = nir_r[0].astype(np.float64) * SR_ESCALA + SR_DESPL
    v = valido_qa(qa, it) & (red_r[0] != 0) & (nir_r[0] != 0)
    # reflectancias físicamente válidas (0, 1]; fuera de ese rango el NDVI no es interpretable
    v &= (red > 0) & (red <= 1) & (nir > 0) & (nir <= 1)
    nd = np.where(v, (nir - red) / (nir + red), np.nan).astype(np.float32)
    return a_rejilla(nd, tr, crs, "bilinear")


def frac_frio(c, ref):
    """Fracción de píxeles válidos de la escena más de FRIO_C °C por debajo de la referencia."""
    v = np.isfinite(c) & np.isfinite(ref)
    return float((c[v] < ref[v] - FRIO_C).mean()) if v.any() else 0.0


def hhmm(minutos):
    t = int(round(float(minutos)))
    return f"{t // 60:02d}:{t % 60:02d}"


def mediana_pila(capas):
    pila = np.stack(capas, axis=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        med = np.nanmedian(pila, axis=0).astype(np.float32)
    n = np.isfinite(pila).sum(axis=0).astype(np.float32)
    return med, n


def med(a, m):
    x = a[m]
    x = x[np.isfinite(x)]
    return float(np.median(x)) if x.size else None


def media(a, m):
    x = a[m]
    x = x[np.isfinite(x)]
    return float(np.mean(x)) if x.size else None


def resta(a, b):
    return None if a is None or b is None else a - b


def r3(x):
    return None if x is None else round(float(x), 3)


def metricas(lst, ndvi, M):
    """Métricas espaciales de una rejilla LST (y NDVI) por zona y variante."""
    lu, lr = med(lst, M["urbana"]), med(lst, M["rural"])
    mu, mr = media(lst, M["urbana"]), media(lst, M["rural"])
    ln = med(lst, M["nucleo"])
    d = {"lst_mediana_urbana": lu, "lst_media_urbana": mu, "lst_mediana_nucleo": ln,
         "lst_mediana_periurbano": med(lst, M["periurbano"]), "lst_mediana_rural": lr, "lst_media_rural": mr,
         "isla_calor": resta(lu, lr), "isla_calor_media": resta(mu, mr), "isla_calor_nucleo": resta(ln, lr)}
    if M.get("construido_2000") is not None:
        lc = med(lst, M["construido_2000"])
        d.update({"lst_mediana_construido_2000": lc, "isla_calor_construido_2000": resta(lc, lr)})
    if ndvi is not None:
        d.update({"ndvi_mediana_urbana": med(ndvi, M["urbana"]), "ndvi_media_urbana": media(ndvi, M["urbana"]),
                  "ndvi_mediana_nucleo": med(ndvi, M["nucleo"]), "ndvi_mediana_periurbano": med(ndvi, M["periurbano"]),
                  "ndvi_mediana_rural": med(ndvi, M["rural"]), "ndvi_media_rural": media(ndvi, M["rural"])})
        if M.get("construido_2000") is not None:
            d["ndvi_mediana_construido_2000"] = med(ndvi, M["construido_2000"])
    return {k: r3(v) for k, v in d.items()}


def mascara_construido_2000(M):
    """Celdas de la cabecera con NDVI medio 2000-2002 < NDVI_CONSTRUIDO_2000 (ya construidas o desnudas en 2000).

    Usa las rejillas anuales ndvi_<año>.npy de la serie (Landsat 5/7); None si faltan."""
    rutas = [os.path.join(comun.REJILLA_NPY, f"ndvi_{a}.npy") for a in ANIOS_NDVI_2000]
    if not all(os.path.exists(r) for r in rutas):
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        n0 = np.nanmean(np.stack([np.load(r) for r in rutas]), 0)
    with np.errstate(invalid="ignore"):
        return M["urbana"] & np.isfinite(n0) & (n0 < NDVI_CONSTRUIDO_2000)


# ------------------------------------------------------------------ (a) capa LST

def items_lst(items):
    return [it for it in items if es_l89(it) and es_009057_t1(it) and "2022-01-01" <= it["datetime"][:10] <= "2025-12-31"]


def compuesto(capas, idx):
    m_, n_ = mediana_pila([capas[i] for i in idx])
    return np.where(n_ >= N_MIN, m_, np.nan), n_


def capa_lst(items):
    sel = items_lst(items)
    log(f"(a) LST: {len(sel)} escenas L8/L9 T1 009/057 2022-2025; leyendo QA_PIXEL…")
    qas = leer_varios([(it, "qa_pixel") for it in sel])
    evaluadas = []
    for it in sel:
        r = qas[(it["id"], "qa_pixel")]
        if r is None:
            log(f"  sin QA: {it['id']} (se omite)")
            continue
        pd, pu = evaluar_qa(it, r)
        evaluadas.append((it, pd, pu))
    usar = [(it, pd, pu) for it, pd, pu in evaluadas if pd >= MIN_DESPEJADO]
    log(f"  {len(usar)} de {len(evaluadas)} escenas con ≥ {MIN_DESPEJADO} % de la rejilla despejado; leyendo ST_B10, ST_CDIST y ST_QA…")
    sts = leer_varios([(it, k) for it, _, _ in usar for k in ("lwir11", "cdist", "stqa")])
    proc_mtl = procedencias([it for it, _, _ in usar])
    capas, aguas, escenas, its = [], [], [], []
    for it, pd, pu in usar:
        st = sts[(it["id"], "lwir11")]
        if st is None:
            log(f"  sin ST: {it['id']} (se omite)")
            continue
        c, a = lst_escena(it, qas[(it["id"], "qa_pixel")], st)
        capas.append(c)
        aguas.append(a)
        its.append(it)
        u = c[urbana()]
        escenas.append({"id": it["id"], "fecha": it["datetime"][:10], "hora_local": hora_local(it).strftime("%H:%M"),
                        "minutos_locales": minutos_locales(it),
                        "plataforma": it["platform"], "eo_cloud_cover": it["cloud"], "pct_despejado_rejilla": pd,
                        "pct_despejado_cabecera": pu,
                        "lst_mediana_cabecera": None if np.isfinite(u).sum() == 0 else round(float(np.nanmedian(u)), 2),
                        "lst_mediana_rejilla": round(float(np.nanmedian(c)), 2)} | proc_mtl[it["id"]])
    if len(capas) < 5:
        raise SystemExit(f"Solo {len(capas)} escenas utilizables: no se construye la capa LST.")

    # Filtro de nubes no detectadas: QA_PIXEL deja pasar nubes delgadas y bruma, que enfrían la LST.
    # Pasada 1: referencia = mediana de todas las escenas. Pasadas siguientes: referencia = compuesto de las
    # escenas aceptadas (la capa final). Se descarta la escena si ≥ FRIO_FRAC de sus píxeles válidos están más de
    # FRIO_C °C por debajo de la referencia; se repite hasta que el conjunto aceptado no cambia.
    ref = mediana_pila(capas)[0]
    ok_prev, pasadas, ff1, convergio = None, [], None, False
    for k in range(MAX_PASADAS_FILTRO):
        ff = [frac_frio(c, ref) for c in capas]
        ok = [i for i, f in enumerate(ff) if f < FRIO_FRAC]
        if ff1 is None:
            ff1 = ff
        pasadas.append({"pasada": k + 1, "referencia": "mediana de todas las escenas" if k == 0 else
                        "compuesto de las escenas aceptadas en la pasada anterior",
                        "escenas_aceptadas": len(ok),
                        "descartadas": [escenas[i]["fecha"] for i in range(len(capas)) if i not in set(ok)]})
        if ok == ok_prev:
            convergio = True
            break
        ok_prev = ok
        ref = compuesto(capas, ok)[0]
    if not convergio:
        log(f"  AVISO: el filtro de nubes no convergió en {MAX_PASADAS_FILTRO} pasadas; se usa la última")
    ok1 = [i for i, f in enumerate(ff1) if f < FRIO_FRAC]
    for e, f, f1 in zip(escenas, ff, ff1):
        e["frac_frio"] = round(f, 4)
        e["frac_frio_pasada_1"] = round(f1, 4)
        e["usada"] = f < FRIO_FRAC
    rechazadas = [e for e in escenas if not e["usada"]]
    log(f"  filtro de nubes no detectadas: {len(pasadas)} pasadas ({'converge' if convergio else 'NO converge'}); "
        f"se descartan {len(rechazadas)} escenas ({', '.join(e['fecha'] for e in rechazadas)})")
    med_, n = mediana_pila([capas[i] for i in ok])
    # frecuencia de agua (bit 7) entre las observaciones despejadas de las escenas usadas
    pa = np.stack([aguas[i] for i in ok], 0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        frec_agua = (np.nansum(pa, 0) / np.isfinite(pa).sum(0)).astype(np.float32)
    del pa, aguas
    np.save(os.path.join(comun.REJILLA_NPY, "landsat_agua_frec.npy"), frec_agua)
    np.save(os.path.join(comun.REJILLA_NPY, "lst_n.npy"), n)
    lst = np.where(n >= N_MIN, med_, np.nan).astype(np.float32)
    usadas = [escenas[i] for i in ok]

    hora_media = hhmm(np.mean([e["minutos_locales"] for e in usadas]))
    hmin, hmax = min(e["hora_local"] for e in usadas), max(e["hora_local"] for e in usadas)
    plat = Counter(e["plataforma"] for e in usadas)
    rean = Counter(e["reanalisis_st"] for e in usadas)
    orig_mtl = Counter(e["procedencia_origen"] for e in usadas)
    alg = Counter(e["algoritmo_st"] for e in usadas if e.get("algoritmo_st"))
    fin = np.isfinite(lst)
    p2, p98 = np.percentile(lst[fin], [2, 98])
    rango = [float(np.floor(p2)), float(np.ceil(p98))]
    M = mascaras(frec_agua)
    urb, rural, nuc = M["urbana"], M["rural"], M["nucleo"]
    est_zonas = metricas(lst, None, M)
    rur_med, urb_med = est_zonas["lst_mediana_rural"], est_zonas["lst_mediana_urbana"]
    rur_amplia = r3(med(lst, M["rural_amplia"]))
    alt_r = M["descripcion"]["rural_altitud_m"]

    # ---- sensibilidad del nivel absoluto al tratamiento de nubes (filtro por escena y máscaras por píxel)
    def fila(comp, n_, idx):
        ff_ = [frac_frio(capas_v[i], comp) for i in idx]
        return {"escenas": len(idx), "cabecera": r3(med(comp, urb)), "nucleo": r3(med(comp, nuc)),
                "rural": r3(med(comp, rural)), "isla_cabecera": r3(resta(med(comp, urb), med(comp, rural))),
                "isla_nucleo": r3(resta(med(comp, nuc), med(comp, rural))),
                "obs_por_celda_mediana": float(np.median(n_)),
                "escenas_aun_frias": int(sum(f >= FRIO_FRAC for f in ff_))}
    sens = {}
    todas = list(range(len(capas)))
    estrictas = [i for i, e in enumerate(escenas) if e["frac_frio"] < 0.05]
    capas_v = capas
    for nombre, idx in (("solo_qa_pixel", todas), ("qa_pixel_mas_filtro_escena_una_pasada", ok1),
                        ("qa_pixel_mas_filtro_escena_USADO", ok), ("filtro_escena_estricto_5pct", estrictas)):
        comp, n_ = compuesto(capas_v, idx)
        sens[nombre] = fila(comp, n_, idx)
    # máscaras por píxel con las bandas del propio producto ST (umbrales: supuestos)
    variantes_pix = (("cdist_1km", lambda cd, sq: cd >= 1.0 / AUX_ESCALA),
                     ("cdist_2km", lambda cd, sq: cd >= 2.0 / AUX_ESCALA),
                     ("stqa_5K", lambda cd, sq: (sq >= 0) & (sq <= 5.0 / AUX_ESCALA)))
    faltan_aux = [it["id"] for it in its if sts.get((it["id"], "cdist")) is None or sts.get((it["id"], "stqa")) is None]
    if not faltan_aux:
        for nombre, f in variantes_pix:
            capas_v = []
            for it in its:
                extra = f(sts[(it["id"], "cdist")][0], sts[(it["id"], "stqa")][0])
                capas_v.append(lst_escena(it, qas[(it["id"], "qa_pixel")], sts[(it["id"], "lwir11")], extra)[0])
            for sufijo, idx in (("", todas), ("_mas_filtro_escena", ok)):
                comp, n_ = compuesto(capas_v, idx)
                sens[nombre + sufijo] = fila(comp, n_, idx)
            del capas_v
    else:
        log(f"  sin ST_CDIST/ST_QA para {len(faltan_aux)} escenas: no se calcula esa parte de la sensibilidad")
    capas_v = capas
    log(f"  sensibilidad: {json.dumps(sens, ensure_ascii=False)}")
    niveles = [v["cabecera"] for v in sens.values()]
    islas = [v["isla_cabecera"] for v in sens.values()]
    islas_n = [v["isla_nucleo"] for v in sens.values()]
    pix_sin_filtro = [v["escenas_aun_frias"] for k, v in sens.items() if k in ("cdist_1km", "cdist_2km", "stqa_5K")]

    # ---- sensibilidad al reanálisis atmosférico del ST (GEOS-5 FP-IT hasta 2023, GEOS-IT desde 2024)
    sens_rean = {}
    for nombre_r in sorted(rean):
        idx = [i for i in ok if escenas[i]["reanalisis_st"] == nombre_r]
        if len(idx) >= 5:
            comp, n_ = compuesto(capas, idx)
            sens_rean[nombre_r] = fila(comp, n_, idx) | {
                "anios": sorted({escenas[i]["fecha"][:4] for i in idx}),
                "celdas_con_dato_pct": round(100.0 * float(np.isfinite(comp).mean()), 1)}
    log(f"  sensibilidad al reanálisis: {json.dumps(sens_rean, ensure_ascii=False)}")

    capas = [capas[i] for i in ok]
    vacias = int((n == 0).sum())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        for e, c in zip(usadas, capas):
            e["anomalia_mediana_c"] = round(float(np.nanmedian(c - med_)), 2)
    amin = min(e["anomalia_mediana_c"] for e in usadas)
    amax = max(e["anomalia_mediana_c"] for e in usadas)
    cab_rech = [e["lst_mediana_cabecera"] for e in rechazadas if e["lst_mediana_cabecera"] is not None]
    cab_usad = [e["lst_mediana_cabecera"] for e in usadas if e["lst_mediana_cabecera"] is not None]

    if len(sens_rean) == 2:
        (r1, s1), (r2, s2) = sorted(sens_rean.items(), key=lambda kv: kv[1]["anios"][0])
        txt_rean = (f" Por separado: con {r1} ({s1['escenas']} escenas de {'-'.join([s1['anios'][0], s1['anios'][-1]])}) la "
                    f"cabecera da {fc(s1['cabecera'])} °C, la isla {fc(s1['isla_cabecera'], signo=True)} °C y la del núcleo "
                    f"{fc(s1['isla_nucleo'], signo=True)} °C; con {r2} ({s2['escenas']} escenas de "
                    f"{'-'.join([s2['anios'][0], s2['anios'][-1]])}), {fc(s2['cabecera'])} °C, "
                    f"{fc(s2['isla_cabecera'], signo=True)} °C y {fc(s2['isla_nucleo'], signo=True)} °C (tabla "
                    "sensibilidad_reanalisis). Esa diferencia no se puede atribuir al reanálisis: los dos grupos son años "
                    "distintos, con otras fechas despejadas y otro clima (2024 incluye el final de El Niño 2023-2024, que "
                    "terminaba en mayo de 2024 según NOAA).")
    else:
        txt_rean = ""
    n_mtl = orig_mtl.get("MTL", 0)

    meta = {
        "titulo": "Temperatura superficial terrestre (Landsat 8 y 9, 2022–2025)",
        "descripcion": ("Temperatura de la superficie (techos, vías, suelo, vegetación, agua) medida por satélite hacia las "
                        f"{hora_media} de la mañana en días despejados; mediana de {len(capas)} pasos entre 2022 y 2025. "
                        "No es la temperatura del aire que se siente a la sombra."),
        "unidad": "°C",
        "fuente": {
            "nombre": "USGS Landsat 8-9 OLI/TIRS Collection 2 Level-2 (ST_B10, QA_PIXEL), vía Microsoft Planetary Computer",
            "url": "https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2",
            "licencia": "Dominio público (USGS): sin restricciones de uso ni redistribución; se pide citar la fuente",
            "cita": ("Landsat 8-9 OLI/TIRS Collection 2 Level-2 Science Products courtesy of the U.S. Geological Survey. "
                     "doi:10.5066/P9OGBGM6"),
        },
        "fuentes_secundarias": fuentes_secundarias(),
        "periodo": (f"2022-01-01 a 2025-12-31 ({len(capas)} escenas de días con al menos parte del área despejada; "
                    f"hora local media de paso {hora_media}, rango {hmin}–{hmax})"),
        "resolucion_original_m": 100,
        "procesamiento": [
            f"Búsqueda STAC en Planetary Computer: {len(sel)} escenas Landsat 8 y 9, Tier 1, ruta/fila WRS-2 009/057, 2022–2025.",
            "Lectura solo de la ventana del área (COG) de QA_PIXEL, ST_B10, ST_CDIST y ST_QA, y del archivo de metadatos MTL "
            "de cada escena (reanálisis atmosférico, versión del algoritmo ST y del software).",
            "Máscara QA_PIXEL de Collection 2: se descartan los píxeles con bit 0 (relleno), 1 (nube dilatada), 2 (cirro alta "
            "confianza), 3 (nube), 4 (sombra de nube) o 5 (nieve) activos, QA = 0 y ST = 0.",
            f"Se leen las escenas con al menos {fg(MIN_DESPEJADO)} % de la rejilla despejado: {len(escenas)} de {len(evaluadas)}.",
            "ST_B10 → K = DN × 0,00341802 + 149,0; °C = K − 273,15.",
            "Reproyección de UTM 18N (30 m) a la rejilla común EPSG:4326 de 0,00025° con remuestreo bilineal que ignora píxeles sin dato.",
            f"Filtro empírico de nubes no detectadas por QA_PIXEL (supuesto propio): se descarta la escena si al menos el "
            f"{fg(100 * FRIO_FRAC)} % de sus píxeles despejados está más de {fg(FRIO_C)} °C por debajo de la referencia. En la "
            "primera pasada la referencia es la mediana de todas las escenas; luego, el compuesto de las aceptadas, y se repite "
            f"hasta que el conjunto no cambia ({len(pasadas)} pasadas{'' if convergio else ', sin converger'}). Se descartan "
            f"{len(rechazadas)} escenas (con una sola pasada eran {len(escenas) - len(ok1)}). Quedan {len(capas)}.",
            f"Mediana por celda de las observaciones despejadas; se dejan sin dato las celdas con menos de {N_MIN} observaciones.",
            "El número de observaciones por celda se guarda en fuentes/rejilla/lst_n.npy.",
            "Estadísticas por zona: cabecera (polígono OSM), núcleo construido (≥ 80 % construido según WorldCover 2021), "
            "periurbano verde (< 20 % construido) y referencia rural (fuera de la cabecera, a más de 500 m, sin agua, construido "
            f"< 10 % y altitud entre {fc(alt_r[0])} y {fc(alt_r[1])} m, ± 30 m de la mediana de la cabecera según Copernicus DEM).",
        ],
        "limitaciones": [
            "Es temperatura de la superficie (piel radiativa), no temperatura del aire; en días soleados puede superar en "
            "muchos grados a la del aire.",
            f"Describe solo la mañana de días con cielo despejado sobre la celda (paso del satélite hacia las {hora_media} "
            "hora local); no informa sobre la tarde, la noche ni los días nublados.",
            "El sensor térmico TIRS mide a 100 m; el USGS lo entrega remuestreado a 30 m. Detalles menores a una manzana "
            "(un techo, una calle) no se resuelven.",
            "El nivel absoluto depende del tratamiento de nubes. QA_PIXEL deja pasar nubes delgadas y bruma; el filtro por "
            "escena es un umbral propio y no separa limpiamente"
            + (f": las escenas descartadas tenían medianas de cabecera de {fc(min(cab_rech))} a {fc(max(cab_rech))} °C y "
               f"entre las usadas hay medianas desde {fc(min(cab_usad))} °C. " if cab_rech else ". ")
            + f"Según la variante (tabla sensibilidad_nubes), la mediana de la cabecera va de {fc(min(niveles))} a "
            f"{fc(max(niveles))} °C; la diferencia cabecera − rural cambia poco ({fc(min(islas))} a {fc(max(islas))} °C) y la "
            f"del núcleo construido va de {fc(min(islas_n))} a {fc(max(islas_n))} °C."
            + (f" Las máscaras por píxel con ST_CDIST o ST_QA, sin el filtro por escena, dejan {min(pix_sin_filtro)} a "
               f"{max(pix_sin_filtro)} escenas con ≥ {fg(100 * FRIO_FRAC)} % de píxeles fríos, por eso no lo reemplazan."
               if pix_sin_filtro else ""),
            "Cambio de procesamiento del USGS dentro del periodo: el producto ST corrige la atmósfera con el reanálisis "
            "GEOS-5 FP-IT en las adquisiciones hasta el 31-12-2023 y con GEOS-5 IT (GEOS-IT) desde el 1-1-2024 (guía "
            "LSDS-1619 v6.0 del USGS, mayo de 2024; campo DATA_SOURCE_REANALYSIS del MTL, leído en "
            f"{n_mtl} de {len(usadas)} escenas{'' if n_mtl == len(usadas) else ' y asignado por fecha en el resto'}). "
            f"El compuesto mezcla {' y '.join(f'{v} escenas con {k}' for k, v in sorted(rean.items()))}." + txt_rean
            + "".join(f" Además, según los MTL el algoritmo ST pasó de {c['antes']} a {c['despues']} entre las adquisiciones "
                      f"del {c['ultima_adquisicion_antes']} y el {c['primera_adquisicion_despues']} (no se encontró documentación "
                      "del USGS sobre ese cambio)." for c in cambios_version(usadas, "algoritmo_st"))
            + " Las actualizaciones con escenas de 2026 en adelante serán solo GEOS-IT.",
            "El polígono OSM de la cabecera es heterogéneo: el "
            f"{fc(100 * M['descripcion']['periurbano_frac_cabecera'], 0)} % de sus celdas tiene menos de 20 % construido y el "
            f"{fc(100 * M['descripcion']['nucleo_frac_cabecera'], 0)} % tiene 80 % o más. La LST de la cabecera es bimodal "
            f"(núcleo construido {fc(est_zonas['lst_mediana_nucleo'])} °C, periurbano verde "
            f"{fc(est_zonas['lst_mediana_periurbano'])} °C) y su mediana cae entre ambos modos; para comparar zonas conviene "
            "usar el núcleo construido o la media.",
            "Las escenas despejadas no se reparten igual en todos los meses ni en todos los años; la mediana de cada escena "
            f"difiere de la del compuesto entre {fc(amin, signo=True)} y {fc(amax, signo=True)} °C según la fecha. El "
            "compuesto describe 2022–2025 en conjunto, no un día ni un año típico.",
            f"{vacias} celdas sin ninguna observación válida por huecos fijos del producto ST del USGS, que no tiene dato donde "
            "falta la emisividad de ASTER GED (https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-temperature-data-gaps-due-missing-aster-ged).",
            "La emisividad del producto USGS combina ASTER GED con NDVI; en techos metálicos y superficies muy reflectivas el error es mayor.",
            "La referencia rural depende de capas de otros productos (WorldCover 2021 y Copernicus DEM) y de umbrales propios "
            f"(± {fg(RURAL_ALT_BANDA_M)} m, construido < {fg(RURAL_CONSTRUIDO_MAX)} %). Con la definición anterior (todo lo de "
            f"fuera a más de 500 m, sin agua, incluidas las colinas de 1 000-1 300 m) la mediana rural era {fc(rur_amplia)} °C.",
        ],
        "rango_visual": rango,
        "paleta": ["#313695", "#74add1", "#ffffbf", "#f46d43", "#a50026"],
        "interpretacion": (
            "No existe un umbral normativo de temperatura superficial. Se interpreta en relación con el campo a la misma "
            f"altitud: mediana rural {fc(rur_med)} °C (fuera de la cabecera, a más de 500 m, sin agua ni construcción, entre "
            f"{fc(alt_r[0])} y {fc(alt_r[1])} m). La cabecera da {fc(urb_med)} °C en mediana "
            f"({fc(est_zonas['isla_calor'], signo=True)} °C), su núcleo construido {fc(est_zonas['lst_mediana_nucleo'])} °C "
            f"({fc(est_zonas['isla_calor_nucleo'], signo=True)} °C) y sus zonas verdes periurbanas "
            f"{fc(est_zonas['lst_mediana_periurbano'])} °C. Celdas varios grados por encima de la mediana rural indican "
            "superficies que acumulan calor (cubiertas, pavimento, suelo desnudo); valores bajos, vegetación densa o agua."),
        "escenas_usadas": len(capas),
        "escenas_descartadas_por_nube_no_detectada": [e["fecha"] for e in rechazadas],
        "filtro_nubes_pasadas": pasadas,
        "filtro_nubes_convergio": convergio,
        "escenas_por_plataforma": dict(plat),
        "escenas_por_reanalisis_st": dict(rean),
        "escenas_por_algoritmo_st": dict(alg),
        "procedencia_reanalisis": dict(orig_mtl),
        "hora_local_media_paso": hora_media,
        "hora_local_rango_paso": [hmin, hmax],
        "observaciones_por_celda": {"min": int(n.min()), "p10": float(np.percentile(n, 10)), "mediana": float(np.median(n)),
                                    "max": int(n.max()), "archivo": "fuentes/rejilla/lst_n.npy"},
        "celdas_sin_observacion": vacias,
        "lst_mediana_rural_c": rur_med,
        "lst_mediana_cabecera_c": urb_med,
        "lst_media_cabecera_c": est_zonas["lst_media_urbana"],
        "lst_mediana_nucleo_construido_c": est_zonas["lst_mediana_nucleo"],
        "lst_mediana_periurbano_verde_c": est_zonas["lst_mediana_periurbano"],
        "isla_calor_cabecera_c": est_zonas["isla_calor"],
        "isla_calor_nucleo_construido_c": est_zonas["isla_calor_nucleo"],
        "lst_mediana_rural_definicion_anterior_c": rur_amplia,
        "zonas": M["descripcion"],
        "sensibilidad_nubes": sens,
        "sensibilidad_reanalisis": sens_rean,
    }
    est = comun.guardar_capa("lst", lst, 0.01, -20, meta)
    comun.guardar_json(os.path.join(DIR, "escenas_lst.json"), {"escenas": escenas, "evaluadas": [
        {"id": it["id"], "fecha": it["datetime"][:10], "eo_cloud_cover": it["cloud"], "pct_despejado_rejilla": pd,
         "pct_despejado_cabecera": pu} for it, pd, pu in evaluadas]})
    log(f"(a) LST lista: {len(capas)} escenas, hora media {hora_media} ({hmin}–{hmax}), n por celda "
        f"{int(n.min())}–{int(n.max())} (mediana {np.median(n):.0f}), cabecera {urb_med:.2f} °C, núcleo "
        f"{est_zonas['lst_mediana_nucleo']:.2f} °C, rural {rur_med:.2f} °C")
    log("    estadísticas:", json.dumps(est, ensure_ascii=False))
    return lst, n, frec_agua


# ------------------------------------------------------------------ (b) serie anual

def candidatos(items, anio, plataformas):
    c = [it for it in items if es_009057_t1(it) and it["datetime"][:4] == str(anio) and it["platform"] in plataformas]
    c.sort(key=lambda it: (it["cloud"] if it["cloud"] is not None else 101, it["datetime"]))
    return c[:CANDIDATOS_POR_ANIO]


def candidatos_anio(items, anio):
    plats = ("landsat-8", "landsat-9") if anio >= 2013 else ("landsat-5", "landsat-7")
    return candidatos(items, anio, plats)


def seleccionar(evaluadas, maximo=MAX_POR_ANIO):
    """evaluadas: [(it, pct_rejilla, pct_urbano)] → hasta `maximo`, repartidas por trimestre."""
    elegibles = sorted([e for e in evaluadas if e[1] >= MIN_DESPEJADO], key=lambda e: (-e[1], e[0]["datetime"]))
    elegidas, por_trim = [], Counter()
    for e in elegibles:
        t = (fecha(e[0]).month - 1) // 3
        if por_trim[t] < MAX_POR_TRIMESTRE and len(elegidas) < maximo:
            elegidas.append(e)
            por_trim[t] += 1
    for e in elegibles:
        if len(elegidas) >= maximo:
            break
        if e not in elegidas:
            elegidas.append(e)
    return sorted(elegidas, key=lambda e: e[0]["datetime"])


def evaluar_candidatas(cand):
    qas = leer_varios([(it, "qa_pixel") for it in cand])
    evaluadas = []
    for it in cand:
        r = qas[(it["id"], "qa_pixel")]
        if r is not None:
            pd, pu = evaluar_qa(it, r)
            evaluadas.append((it, pd, pu))
    return evaluadas, qas


def procesar_escenas(nuevas, qas, ref, M):
    """Lee ST/rojo/NIR de las escenas y aplica el filtro de nubes no detectadas.

    Devuelve (procesadas {id: (lst, ndvi, meta)}, rechazadas {id: info})."""
    pares = []
    for it, _, _ in nuevas:
        pares += [(it, banda_st(it)), (it, "red"), (it, "nir08")]
    datos = leer_varios(pares)
    prov = procedencias([it for it, _, _ in nuevas])
    proc, rech = {}, {}
    for it, pd, pu in nuevas:
        qa_r = qas[(it["id"], "qa_pixel")]
        st_r, red_r, nir_r = (datos[(it["id"], k)] for k in (banda_st(it), "red", "nir08"))
        if st_r is None or red_r is None or nir_r is None:
            log(f"  {it['id']}: faltan bandas, se descarta")
            rech[it["id"]] = {"id": it["id"], "fecha": it["datetime"][:10], "motivo": "lectura fallida"}
            continue
        c, _ = lst_escena(it, qa_r, st_r)
        ff = frac_frio(c, ref)
        if ff >= FRIO_FRAC:
            rech[it["id"]] = {"id": it["id"], "fecha": it["datetime"][:10], "sensor": SENSOR[it["platform"]],
                              "motivo": "nube no detectada", "frac_frio": round(ff, 4)}
            continue
        nd = ndvi_escena(it, qa_r, red_r, nir_r)
        m = metricas(c, nd, M)
        ff_cab = frac_frio(np.where(M["urbana"], c, np.nan), ref)
        pr_val = round(100.0 * float(np.isfinite(c[M["rural"]]).mean()), 1)
        motivos = []
        if pu < MIN_CABECERA_ESCENA:
            motivos.append(f"cabecera despejada {fc(pu)} % (< {fg(MIN_CABECERA_ESCENA)} %)")
        if pr_val < MIN_RURAL_ESCENA:
            motivos.append(f"referencia rural con dato {fc(pr_val)} % (< {fg(MIN_RURAL_ESCENA)} %)")
        if ff_cab >= FRIO_FRAC:
            motivos.append(f"{fc(100 * ff_cab, 0)} % de la cabecera más de {fg(FRIO_C)} °C bajo el compuesto (nube no detectada)")
        proc[it["id"]] = (c, nd, {
            "id": it["id"], "fecha": it["datetime"][:10], "hora_local": hora_local(it).strftime("%H:%M"),
            "minutos_locales": minutos_locales(it),
            "sensor": SENSOR[it["platform"]], "eo_cloud_cover": it["cloud"],
            "pct_despejado_rejilla": pd, "pct_despejado_cabecera": pu, "pct_valido_rural": pr_val,
            "frac_frio": round(ff, 4), "frac_frio_cabecera": round(ff_cab, 4),
            "slc_off": it["platform"] == "landsat-7" and it["datetime"][:10] >= "2003-05-31",
            "lst_mediana_urbana": m["lst_mediana_urbana"], "lst_mediana_rural": m["lst_mediana_rural"],
            "isla_calor": m["isla_calor"], "ndvi_mediana_urbana": m["ndvi_mediana_urbana"],
            "ndvi_mediana_rural": m["ndvi_mediana_rural"],
            "apta_metricas_escena": not motivos, **({"motivo_no_apta": motivos} if motivos else {}),
            **prov[it["id"]]})
    return proc, rech


def mediana_escenas(escenas, campo):
    """Mediana entre escenas de una métrica por escena; solo escenas aptas (cabecera y rural despejadas)."""
    x = [e[campo] for e in escenas if e.get(campo) is not None and e.get("apta_metricas_escena", True)]
    return r3(np.median(x)) if x else None


def serie(items, M, desde=2000, hasta=2025, plataformas=None, guardar=True, etiqueta="(b)"):
    """Serie anual. plataformas=None → L5/L7 hasta 2012 y L8/L9 desde 2013; si no, solo esas plataformas.
    guardar=False no escribe rejillas anuales (serie de control)."""
    urb = M["urbana"]
    ref = comun.cargar_capa("lst")  # compuesto 2022-2025 de la parte (a): referencia para el filtro de nubes
    anios = []
    for anio in range(desde, hasta + 1):
        cand = candidatos(items, anio, plataformas) if plataformas else candidatos_anio(items, anio)
        log(f"{etiqueta} {anio}: {len(cand)} candidatas; leyendo QA…")
        evaluadas, qas = evaluar_candidatas(cand)
        # Selección iterativa: si una escena delata nubes no detectadas se descarta y se elige otra.
        procesadas, rechazadas = {}, {}
        while True:
            elegidas = seleccionar([e for e in evaluadas if e[0]["id"] not in rechazadas])
            nuevas = [e for e in elegidas if e[0]["id"] not in procesadas]
            if not nuevas:
                break
            p, r = procesar_escenas(nuevas, qas, ref, M)
            procesadas.update(p)
            rechazadas.update(r)
        finales = [procesadas[e[0]["id"]] for e in elegidas if e[0]["id"] in procesadas]
        lsts = [f[0] for f in finales]
        ndvis = [f[1] for f in finales]
        escenas = [f[2] for f in finales]
        log(f"  {anio}: elegidas {[(e['sensor'], e['fecha'], e['pct_despejado_rejilla']) for e in escenas]}; "
            f"descartadas {[(r['fecha'], r.get('frac_frio')) for r in rechazadas.values()]}")
        trimestres = sorted({(int(e["fecha"][5:7]) - 1) // 3 + 1 for e in escenas})
        reg = {"anio": anio, "n_escenas": len(escenas), "trimestres": trimestres,
               "sensores": sorted({e["sensor"] for e in escenas}),
               "fechas": [e["fecha"] for e in escenas], "escenas": escenas, "candidatas_revisadas": len(evaluadas),
               "escenas_descartadas": list(rechazadas.values())}
        if not escenas:
            reg.update({"lst_mediana_urbana": None, "ndvi_mediana_urbana": None, "lst_mediana_rural": None,
                        "isla_calor": None, "pct_urbano_valido": 0.0, "pct_rural_valido": 0.0, "confiable": False,
                        "motivo_no_confiable": ["sin escenas utilizables"]})
            anios.append(reg)
            log(f"  {anio}: sin escenas utilizables")
            continue
        lst_a, n_l = mediana_pila(lsts)
        ndvi_a, n_n = mediana_pila(ndvis)
        lst_a = np.where(n_l >= N_MIN_ANUAL, lst_a, np.nan).astype(np.float32)
        ndvi_a = np.where(n_n >= N_MIN_ANUAL, ndvi_a, np.nan).astype(np.float32)
        if guardar:
            np.save(os.path.join(comun.REJILLA_NPY, f"lst_{anio}.npy"), lst_a)
            np.save(os.path.join(comun.REJILLA_NPY, f"ndvi_{anio}.npy"), ndvi_a)
            np.save(os.path.join(comun.REJILLA_NPY, f"lst_n_{anio}.npy"), n_l.astype(np.uint8))
            np.save(os.path.join(comun.REJILLA_NPY, f"ndvi_n_{anio}.npy"), n_n.astype(np.uint8))

        pu_val = round(100.0 * np.isfinite(lst_a[urb]).mean(), 1)
        pr_val = round(100.0 * np.isfinite(lst_a[M["rural"]]).mean(), 1)
        motivos = []
        if len(escenas) < CONF_MIN_ESCENAS:
            motivos.append(f"{len(escenas)} escenas (< {CONF_MIN_ESCENAS})")
        if len(trimestres) < CONF_MIN_TRIMESTRES:
            motivos.append(f"escenas en {len(trimestres)} trimestre(s) (< {CONF_MIN_TRIMESTRES}): poco representativo del año")
        if pu_val < CONF_MIN_PCT_URBANO:
            motivos.append(f"{pu_val} % de la cabecera con dato (< {CONF_MIN_PCT_URBANO:g} %)")
        reg.update(metricas(lst_a, ndvi_a, M))
        reg.update({
            "lst_urbana_por_escena": mediana_escenas(escenas, "lst_mediana_urbana"),
            "lst_rural_por_escena": mediana_escenas(escenas, "lst_mediana_rural"),
            "isla_calor_por_escena": mediana_escenas(escenas, "isla_calor"),
            "ndvi_urbano_por_escena": mediana_escenas(escenas, "ndvi_mediana_urbana"),
            "ndvi_rural_por_escena": mediana_escenas(escenas, "ndvi_mediana_rural"),
            "escenas_aptas_metricas_escena": sum(bool(e.get("apta_metricas_escena")) for e in escenas),
            "reanalisis_st": sorted({e["reanalisis_st"] for e in escenas}),
            "pct_urbano_valido": pu_val, "pct_rural_valido": pr_val,
            "obs_por_celda_urbana_mediana": float(np.median(n_l[urb])),
            "celdas_frias_residuales": int((np.isfinite(lst_a) & np.isfinite(ref) & (lst_a < ref - FRIO_C)).sum()),
            "hora_local_media": hhmm(np.mean([e["minutos_locales"] for e in escenas])),
            "confiable": not motivos,
        })
        if motivos:
            reg["motivo_no_confiable"] = motivos
        anios.append(reg)
        log(f"  {anio}: n={len(escenas)} trim={trimestres} {reg['sensores']} urb={reg['lst_mediana_urbana']} "
            f"nuc={reg['lst_mediana_nucleo']} rur={reg['lst_mediana_rural']} isla={reg['isla_calor']} "
            f"ndvi_urb={reg['ndvi_mediana_urbana']} %urb={pu_val} confiable={reg['confiable']} {motivos or ''}")
    return anios


# ------------------------------------------------------------------ solape Landsat 7 / Landsat 8

CAMPOS_GRILLA = ("lst_mediana_urbana", "lst_media_urbana", "lst_mediana_nucleo", "lst_mediana_construido_2000",
                 "lst_mediana_rural", "lst_media_rural",
                 "isla_calor", "isla_calor_media", "isla_calor_nucleo", "isla_calor_construido_2000",
                 "ndvi_mediana_urbana", "ndvi_media_urbana", "ndvi_mediana_nucleo", "ndvi_mediana_construido_2000",
                 "ndvi_mediana_periurbano",
                 "ndvi_mediana_rural", "ndvi_media_rural")
CAMPOS_ESCENA = {"lst_urbana_por_escena": "lst_mediana_urbana", "lst_rural_por_escena": "lst_mediana_rural",
                 "isla_calor_por_escena": "isla_calor", "ndvi_urbano_por_escena": "ndvi_mediana_urbana",
                 "ndvi_rural_por_escena": "ndvi_mediana_rural"}


def solape_l7_l8(items, M):
    """Efecto de sensor (L8 − L7) con escenas de ambos en 2013-2016 (misma ruta/fila y hora de paso similar)."""
    ref = comun.cargar_capa("lst")
    grupos = {}
    for plat in ("landsat-7", "landsat-8"):
        cand = [it for anio in range(SOLAPE[0], SOLAPE[1] + 1) for it in candidatos(items, anio, (plat,))]
        log(f"(b) solape {SOLAPE[0]}-{SOLAPE[1]} {SENSOR[plat]}: {len(cand)} candidatas; leyendo QA…")
        evaluadas, qas = evaluar_candidatas(cand)
        eleg = [e for e in evaluadas if e[1] >= MIN_DESPEJADO]
        proc, rech = procesar_escenas(eleg, qas, ref, M)
        orden = sorted(proc, key=lambda k: proc[k][2]["fecha"])
        grupos[plat] = {"lst": [proc[k][0] for k in orden], "ndvi": [proc[k][1] for k in orden],
                        "escenas": [proc[k][2] for k in orden], "descartadas": len(rech), "candidatas": len(cand),
                        "con_despejado_minimo": len(eleg)}
        log(f"  {SENSOR[plat]}: {len(orden)} escenas usadas, {len(rech)} descartadas por nube no detectada")
    if min(len(g["lst"]) for g in grupos.values()) < 5:
        log("  solape insuficiente (< 5 escenas por sensor): no se estima efecto de sensor")
        return None

    # Solo interesan las celdas de las zonas de resumen: se apilan una vez y el bootstrap remuestrea filas.
    celdas = M["urbana"] | M["rural"]
    for g in grupos.values():
        g["pl"] = np.stack([x[celdas] for x in g["lst"]])
        g["pn"] = np.stack([x[celdas] for x in g["ndvi"]])

    def a_rejilla_completa(vals):
        out = np.full(celdas.shape, np.nan, dtype=np.float32)
        out[celdas] = vals
        return out

    def comp_metricas(g, idx):
        idx = np.asarray(idx)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            pl, pn = g["pl"][idx], g["pn"][idx]
            lst = np.where(np.isfinite(pl).sum(0) >= N_MIN, np.nanmedian(pl, 0), np.nan)
            nd = np.where(np.isfinite(pn).sum(0) >= N_MIN, np.nanmedian(pn, 0), np.nan)
        m = metricas(a_rejilla_completa(lst), a_rejilla_completa(nd), M)
        for campo, campo_esc in CAMPOS_ESCENA.items():
            m[campo] = mediana_escenas([g["escenas"][i] for i in idx], campo_esc)
        return m

    g7, g8 = grupos["landsat-7"], grupos["landsat-8"]
    m7 = comp_metricas(g7, list(range(len(g7["lst"]))))
    m8 = comp_metricas(g8, list(range(len(g8["lst"]))))
    campos = list(CAMPOS_GRILLA) + list(CAMPOS_ESCENA)
    delta = {c: r3(resta(m8.get(c), m7.get(c))) for c in campos}
    rng = np.random.default_rng(20130411)
    boot = {c: [] for c in campos}
    for _ in range(BOOT):
        i7 = rng.integers(0, len(g7["lst"]), len(g7["lst"]))
        i8 = rng.integers(0, len(g8["lst"]), len(g8["lst"]))
        b7, b8 = comp_metricas(g7, i7), comp_metricas(g8, i8)
        for c in campos:
            d = resta(b8.get(c), b7.get(c))
            if d is not None:
                boot[c].append(d)
    ic = {c: [r3(np.percentile(v, 2.5)), r3(np.percentile(v, 97.5))] if v else None for c, v in boot.items()}

    def resumen_grupo(g):
        es = g["escenas"]
        return {"candidatas": g["candidatas"], "con_despejado_minimo": g["con_despejado_minimo"],
                "usadas": len(es), "descartadas_nube_no_detectada": g["descartadas"],
                "hora_local_media": hhmm(np.mean([e["minutos_locales"] for e in es])),
                "hora_local_rango": [min(e["hora_local"] for e in es), max(e["hora_local"] for e in es)],
                "meses": dict(sorted(Counter(e["fecha"][5:7] for e in es).items())),
                "fechas": [e["fecha"] for e in es]}
    sol = {"periodo": f"{SOLAPE[0]}-{SOLAPE[1]}",
           "metodo": (f"Escenas Tier 1 009/057 de {SOLAPE[0]}-{SOLAPE[1]}: por año y sensor, las {CANDIDATOS_POR_ANIO} de "
                      f"menor eo:cloud_cover; se usan todas las que tienen ≥ {MIN_DESPEJADO:g} % despejado y pasan el filtro "
                      "de nubes no detectadas. Compuesto mediano por sensor con las mismas zonas que la serie; efecto = "
                      f"L8 − L7. IC 95 % por bootstrap de escenas ({BOOT} réplicas, semilla fija)."),
           "landsat_7": resumen_grupo(g7), "landsat_8": resumen_grupo(g8),
           "metricas_landsat_7": m7, "metricas_landsat_8": m8,
           "efecto_sensor_l8_menos_l7": delta, "efecto_sensor_ic95": ic,
           "limitaciones": [
               "Landsat 7 tiene SLC-off en todo el solape (bandas sin dato) y sus fechas despejadas no coinciden con las de "
               "Landsat 8: parte del efecto puede ser de muestreo (meses distintos), no del sensor.",
               "El efecto se estima con Landsat 7 y se aplica también a los años con Landsat 5 (2000-2011), cuyo sensor TM "
               "y hora de paso difieren de ETM+ (supuesto).",
               "En el solape ambos sensores pasan a la misma hora; la diferencia de hora de paso de 2000-2012 (más temprana) "
               "frente a 2013-2025 no queda corregida por este efecto.",
               "Los IC 95 % son anchos porque cada sensor ve días distintos; excluyen el 0 solo en: "
               + (", ".join(c for c, v in ic.items() if v and (v[0] > 0 or v[1] < 0)) or "ninguna métrica") + ".",
           ]}
    log(f"  efecto de sensor L8 − L7: {json.dumps(delta, ensure_ascii=False)}")
    log(f"  IC95: {json.dumps(ic, ensure_ascii=False)}")
    return sol


# ------------------------------------------------------------------ tendencias

FAMILIAS = {
    "isla_calor": ("°C/década", {"mediana_poligono": "isla_calor", "media_poligono": "isla_calor_media",
                                 "nucleo_construido": "isla_calor_nucleo", "mediana_por_escena": "isla_calor_por_escena",
                                 "construido_en_2000": "isla_calor_construido_2000"}),
    "lst_urbana": ("°C/década", {"mediana_poligono": "lst_mediana_urbana", "media_poligono": "lst_media_urbana",
                                 "nucleo_construido": "lst_mediana_nucleo", "mediana_por_escena": "lst_urbana_por_escena",
                                 "construido_en_2000": "lst_mediana_construido_2000"}),
    "lst_rural": ("°C/década", {"mediana": "lst_mediana_rural", "media": "lst_media_rural",
                                "mediana_por_escena": "lst_rural_por_escena"}),
    "ndvi_urbano": ("NDVI/década", {"mediana_poligono": "ndvi_mediana_urbana", "media_poligono": "ndvi_media_urbana",
                                    "nucleo_construido": "ndvi_mediana_nucleo", "mediana_por_escena": "ndvi_urbano_por_escena",
                                    "construido_en_2000": "ndvi_mediana_construido_2000"}),
    # controles del NDVI urbano: el campo a la misma altitud y las zonas verdes de la cabecera
    "ndvi_rural": ("NDVI/década", {"mediana": "ndvi_mediana_rural", "media": "ndvi_media_rural",
                                   "mediana_por_escena": "ndvi_rural_por_escena"}),
    "ndvi_periurbano": ("NDVI/década", {"mediana": "ndvi_mediana_periurbano"}),
}
# El NDVI de la zona construida en 2000 se selecciona con el propio NDVI de 2000-2002: en tramos que incluyen esos años
# la selección sesga el resultado (regresión a la media), así que esa variante solo se usa desde 2003.
SOLO_DESDE = {("ndvi_urbano", "construido_en_2000"): 2003}


def variantes_de(fam, desde):
    """Variantes de una familia utilizables en un tramo que empieza en `desde`."""
    return {var: campo for var, campo in FAMILIAS[fam][1].items() if desde >= SOLO_DESDE.get((fam, var), 0)}


TRAMOS = (("2013_2025_landsat_8_9", 2013, 2025, False),
          ("2013_2023_landsat_8_9_geos_fp_it", 2013, 2023, False),
          ("2000_2012_landsat_5_7", 2000, 2012, False),
          ("2000_2025_armonizada", 2000, 2025, True))


def valor(r, campo, armonizada, delta):
    v = r.get(campo)
    if v is None or not armonizada or r["anio"] >= 2013:
        return v
    d = (delta or {}).get(campo)
    return None if d is None else v + d


def tendencia(registros, campo, desde, hasta, armonizada=False, delta=None):
    from scipy import stats
    pts = [(r["anio"], valor(r, campo, armonizada, delta)) for r in registros
           if r.get("confiable") and desde <= r["anio"] <= hasta]
    pts = [p for p in pts if p[1] is not None]
    if len(pts) < 6:
        return {"n_anios": len(pts), "nota": "menos de 6 años confiables: no se estima tendencia"}
    x = np.array([p[0] for p in pts], float)
    y = np.array([p[1] for p in pts], float)
    n = len(x)
    sen = stats.theilslopes(y, x, alpha=0.95)
    mk = stats.kendalltau(x, y)
    ols = stats.linregress(x, y)
    tc = stats.t.ppf(0.975, n - 2)
    return {
        "n_anios": n, "anios": [int(a) for a in x],
        "sen_por_decada": round(10 * sen[0], 3), "sen_ic95_por_decada": [round(10 * sen[2], 3), round(10 * sen[3], 3)],
        "mann_kendall_tau": round(float(mk.statistic), 3), "mann_kendall_p": float(f"{mk.pvalue:.3g}"),
        "mco_por_decada": round(10 * ols.slope, 3),
        "mco_ic95_por_decada": [round(10 * (ols.slope - tc * ols.stderr), 3), round(10 * (ols.slope + tc * ols.stderr), 3)],
        "mco_p": float(f"{ols.pvalue:.3g}"), "mco_r2": round(float(ols.rvalue ** 2), 3),
    }


def significativa(t):
    return ("sen_por_decada" in t and t["mann_kendall_p"] < SIG_P and t["mco_p"] < SIG_P
            and (t["sen_ic95_por_decada"][0] > 0 or t["sen_ic95_por_decada"][1] < 0))


def fmt(x, unidad):
    dec = 3 if unidad.startswith("NDVI") else 2
    return f"{x:+.{dec}f}".replace(".", ",")


def lectura(variantes, unidad):
    vals = {k: v for k, v in variantes.items() if "sen_por_decada" in v}
    if not vals:
        return {"lectura": "Sin años suficientes para estimar tendencia."}
    sens = [v["sen_por_decada"] for v in vals.values()]
    sig = [k for k, v in vals.items() if significativa(v)]
    signos_sig = {np.sign(vals[k]["sen_por_decada"]) for k in sig}
    rango = f"entre {fmt(min(sens), unidad)} y {fmt(max(sens), unidad)} {unidad}"
    if len(vals) == 1:
        rango = f"{fmt(sens[0], unidad)} {unidad}"
    if len(sig) == len(vals) and len(signos_sig) == 1:
        quien = "la única variante da una pendiente" if len(vals) == 1 else f"las {len(vals)} variantes dan pendientes"
        txt = (f"{'Aumento' if signos_sig == {1.0} else 'Disminución'} consistente: {quien} "
               f"de Sen {rango}, con Mann-Kendall y MCO p < {str(SIG_P).replace(".", ",")} e IC 95 % de Sen que excluye 0.")
        robusta = True
    elif not sig:
        quien = "la única variante no es significativa" if len(vals) == 1 else f"ninguna de las {len(vals)} variantes es significativa"
        txt = f"Sin tendencia detectable: {quien} (Sen {rango})."
        robusta = False
    else:
        txt = (f"Sin evidencia robusta: solo {len(sig)} de {len(vals)} variantes ({', '.join(sig)}) "
               f"{'es significativa' if len(sig) == 1 else 'son significativas'} (Sen {rango}); el resultado depende del método.")
        robusta = False
    return {"sen_min": min(sens), "sen_max": max(sens), "variantes_significativas": sig,
            "n_variantes": len(vals), "robusta": robusta, "lectura": txt}


def lectura_armonizada(central, extremos, unidad):
    """Como lectura(), pero exige que la conclusión se mantenga con los extremos del IC del efecto de sensor."""
    le = lectura(central, unidad)
    if not le.get("robusta"):
        return le | {"lectura": le["lectura"].rstrip(".") + " (serie armonizada con el efecto de sensor central)."}
    signo = np.sign(le["sen_min"])
    fallos = {}
    for nombre, vs in extremos.items():
        ok = [k for k, v in vs.items() if significativa(v) and np.sign(v["sen_por_decada"]) == signo]
        if len(ok) < len(vs):
            sens = [v["sen_por_decada"] for v in vs.values() if "sen_por_decada" in v]
            fallos[nombre] = (len(ok), len(vs), min(sens), max(sens))
    if not fallos:
        return le | {"lectura": le["lectura"] + " Se mantiene con ambos extremos del IC 95 % del efecto de sensor."}
    det = "; ".join(f"con el extremo {n} " + (f"ninguna de las {t} variantes es significativa" if k == 0 else
                                               f"solo {k} de {t} variantes son significativas")
                    + f" (Sen entre {fmt(a, unidad)} y {fmt(b, unidad)} {unidad})" for n, (k, t, a, b) in fallos.items())
    return le | {"robusta": False, "lectura": (
        f"Depende de la corrección entre sensores: con el efecto de sensor central las {le['n_variantes']} variantes son "
        f"significativas (Sen entre {fmt(le['sen_min'], unidad)} y {fmt(le['sen_max'], unidad)} {unidad}), pero {det}. "
        "No es una conclusión robusta.")}


def salto_entre_sensores(anios, sol):
    from scipy import stats
    delta = (sol or {}).get("efecto_sensor_l8_menos_l7", {})
    ic = (sol or {}).get("efecto_sensor_ic95", {})
    out = {}
    for fam in FAMILIAS:
        for var, campo in variantes_de(fam, 2000).items():
            a = [r[campo] for r in anios if r.get("confiable") and r["anio"] < 2013 and r.get(campo) is not None]
            b = [r[campo] for r in anios if r.get("confiable") and r["anio"] >= 2013 and r.get(campo) is not None]
            if len(a) < 3 or len(b) < 3:
                continue
            w = stats.ttest_ind(b, a, equal_var=False)
            dif = float(np.mean(b) - np.mean(a))
            d = delta.get(campo)
            out[campo] = {"media_2000_2012": r3(np.mean(a)), "media_2013_2025": r3(np.mean(b)),
                          "diferencia": r3(dif), "p_welch": float(f"{w.pvalue:.3g}"),
                          "efecto_sensor_estimado": d, "efecto_sensor_ic95": ic.get(campo),
                          "diferencia_sin_efecto_sensor": r3(resta(dif, d))}
    return out


CONTROL_L7 = (2000, 2016)


def mco(X, y, nombres, robusto=True):
    """MCO con errores estándar robustos a heterocedasticidad (HC1) o clásicos; IC 95 % con t de Student.

    Devuelve {nombre: {"coef", "ic95", "p"}} y n, gl. Implementación propia (numpy/scipy)."""
    from scipy import stats
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    n, k = X.shape
    xtx = np.linalg.pinv(X.T @ X)
    b = xtx @ X.T @ y
    e = y - X @ b
    if robusto:
        s = (X * e[:, None]).T @ (X * e[:, None])
        V = xtx @ s @ xtx * n / (n - k)
    else:
        V = xtx * float(e @ e) / (n - k)
    se = np.sqrt(np.diag(V))
    tc = stats.t.ppf(0.975, n - k)
    out = {}
    for i, nm in enumerate(nombres):
        p = 2 * stats.t.sf(abs(b[i] / se[i]), n - k) if se[i] > 0 else float("nan")
        out[nm] = {"coef": r3(b[i]), "ic95": [r3(b[i] - tc * se[i]), r3(b[i] + tc * se[i])], "p": float(f"{p:.3g}")}
    return out | {"n": int(n), "gl": int(n - k)}


def regresion_escalon_escenas(escenas, campo, corte, con_minutos=True, con_mes=True):
    """Regresión por escena: campo ~ escalón(año ≥ corte) + minutos de paso + efectos fijos de mes (HC1)."""
    d = [e for e in escenas if e.get(campo) is not None and e.get("apta_metricas_escena", True)]
    if len(d) < 12 or len({int(e["fecha"][:4]) >= corte for e in d}) < 2:
        return None
    cols, nom = [np.ones(len(d)), np.array([int(e["fecha"][:4]) >= corte for e in d], float)], ["const", "escalon"]
    if con_minutos:
        cols.append(np.array([e["minutos_locales"] for e in d], float))
        nom.append("minutos_paso")
    if con_mes:
        meses = sorted({int(e["fecha"][5:7]) for e in d})
        for m_ in meses[1:]:
            cols.append(np.array([int(e["fecha"][5:7]) == m_ for e in d], float))
            nom.append(f"mes_{m_:02d}")
    r = mco(np.column_stack(cols), [e[campo] for e in d], nom)
    return {"escalon_c": r["escalon"], "minutos_paso_c_por_min": r.get("minutos_paso"), "n_escenas": r["n"],
            "efectos_fijos_mes": con_mes}


def pendiente_minutos(escenas, campo, desde, hasta):
    """Dentro de un tramo con un solo sensor: campo ~ minutos de paso (+ mes), por escena."""
    d = [e for e in escenas if e.get(campo) is not None and e.get("apta_metricas_escena", True)
         and desde <= int(e["fecha"][:4]) <= hasta]
    if len(d) < 12:
        return None
    meses = sorted({int(e["fecha"][5:7]) for e in d})
    cols = [np.ones(len(d)), np.array([e["minutos_locales"] for e in d], float)]
    cols += [np.array([int(e["fecha"][5:7]) == m_ for e in d], float) for m_ in meses[1:]]
    r = mco(np.column_stack(cols), [e[campo] for e in d], ["const", "minutos"] + [f"m{m_}" for m_ in meses[1:]])
    return {"c_por_min": r["minutos"], "n_escenas": r["n"],
            "rango_minutos": [hhmm(min(e["minutos_locales"] for e in d)), hhmm(max(e["minutos_locales"] for e in d))]}


def por_periodo_escenas(escenas, campo, periodos):
    out = {}
    for nombre, (a, b) in periodos.items():
        x = [e for e in escenas if a <= int(e["fecha"][:4]) <= b and e.get(campo) is not None
             and e.get("apta_metricas_escena", True)]
        if x:
            out[nombre] = {"n_escenas": len(x), "media": r3(np.mean([e[campo] for e in x])),
                           "mediana": r3(np.median([e[campo] for e in x])),
                           "hora_paso": [min(e["hora_local"] for e in x), max(e["hora_local"] for e in x)]}
    return out


def resumen_control(control):
    """Serie de control con un solo sensor (Landsat 7) a ambos lados del cambio de sensor de 2013."""
    from scipy import stats
    if not control:
        return None
    escenas = [e for r in control for e in r["escenas"]]
    tend, lect, pre = {}, {}, {}
    for fam, (unidad, _) in FAMILIAS.items():
        vs = variantes_de(fam, CONTROL_L7[0])
        variantes = {var: tendencia(control, campo, CONTROL_L7[0], CONTROL_L7[1]) for var, campo in vs.items()}
        le = lectura(variantes, unidad)
        tend[fam] = {"unidad": unidad, "variantes": variantes, "resumen": le}
        # ¿tendencia gradual o escalón? tendencia dentro de 2000-2012 (mismo sensor, misma regla)
        pre[fam] = lectura({var: tendencia(control, campo, CONTROL_L7[0], 2012) for var, campo in vs.items()}, unidad)
        tend[fam]["solo_2000_2012"] = pre[fam]
        txt = le["lectura"]
        if le.get("variantes_significativas") and "sen_min" in pre[fam] and not pre[fam].get("variantes_significativas"):
            txt = (txt.rstrip(".") + ". No hay cambio gradual en 2000-2012: dentro de ese tramo ninguna variante tiene "
                   f"tendencia significativa (Sen {fmt(pre[fam]['sen_min'], unidad)} a {fmt(pre[fam]['sen_max'], unidad)} {unidad}); "
                   "la pendiente 2000-2016 se debe a que 2013-2016 está en otro nivel (antes_y_despues_de_2013"
                   + ("; ver sintesis_salto_2012_2013)." if fam == "isla_calor" else ")."))
        lect[fam] = txt
    comp = {}
    for fam in FAMILIAS:
        for campo in variantes_de(fam, CONTROL_L7[0]).values():
            a = [r[campo] for r in control if r.get("confiable") and r["anio"] < 2013 and r.get(campo) is not None]
            b = [r[campo] for r in control if r.get("confiable") and r["anio"] >= 2013 and r.get(campo) is not None]
            if len(a) >= 3 and len(b) >= 3:
                w = stats.ttest_ind(b, a, equal_var=False)
                comp[campo] = {"media_2000_2012": r3(np.mean(a)), "media_2013_2016": r3(np.mean(b)),
                               "diferencia": r3(np.mean(b) - np.mean(a)), "p_welch": float(f"{w.pvalue:.3g}")}

    def horas(d, h):
        x = [r["hora_local_media"] for r in control if d <= r["anio"] <= h and r.get("hora_local_media")]
        return [min(x), max(x)] if x else None
    hp = {"2000-2009": horas(2000, 2009), "2010-2012": horas(2010, 2012), "2013-2016": horas(2013, 2016)}
    periodos = {"2000-2009": (2000, 2009), "2010-2012": (2010, 2012), "2013-2016": (2013, 2016)}
    reg = {
        "descripcion": ("Por escena apta (ver metodo.metricas_por_escena), solo Landsat 7. «escalon» = diferencia "
                        "2013-2016 menos 2000-2012 controlando la hora de paso (minutos, lineal) y el mes (efectos fijos); "
                        "MCO con errores robustos HC1 e IC 95 %."),
        "isla_calor_por_periodo": por_periodo_escenas(escenas, "isla_calor", periodos),
        "isla_calor_por_anio": {str(a): por_periodo_escenas(escenas, "isla_calor", {"x": (a, a)}).get("x")
                                for a in range(2009, 2016)},
        "isla_calor_escalon_2013": regresion_escalon_escenas(escenas, "isla_calor", 2013),
        "isla_calor_escalon_2013_sin_hora": regresion_escalon_escenas(escenas, "isla_calor", 2013, con_minutos=False),
        "isla_calor_escalon_2013_solo_2010_2016": regresion_escalon_escenas(
            [e for e in escenas if e["fecha"][:4] >= "2010"], "isla_calor", 2013),
        "isla_calor_vs_hora_2000_2012": pendiente_minutos(escenas, "isla_calor", 2000, 2012),
        "lst_urbana_escalon_2013": regresion_escalon_escenas(escenas, "lst_mediana_urbana", 2013),
        "lst_rural_escalon_2013": regresion_escalon_escenas(escenas, "lst_mediana_rural", 2013),
    }
    procs = {}
    for nombre, (a, b) in periodos.items():
        x = [e for e in escenas if a <= int(e["fecha"][:4]) <= b]
        procs[nombre] = {"escenas": len(x), "con_MTL": sum(e.get("procedencia_origen") == "MTL" for e in x),
                         "software_l2": sorted({e.get("software_l2") for e in x if e.get("software_l2")}),
                         "algoritmo_st": sorted({e.get("algoritmo_st") for e in x if e.get("algoritmo_st")}),
                         "reanalisis_st": sorted({e.get("reanalisis_st") for e in x if e.get("reanalisis_st")}),
                         "fecha_producto": sorted({(e.get("fecha_producto") or "")[:7] for e in x if e.get("fecha_producto")})}
    claves = ["anio", "n_escenas", "trimestres", "fechas", "hora_local_media", "confiable", "motivo_no_confiable",
              "pct_urbano_valido", "escenas_aptas_metricas_escena"] + list(CAMPOS_GRILLA) + list(CAMPOS_ESCENA)
    esc = reg["isla_calor_escalon_2013"]
    pm = reg["isla_calor_vs_hora_2000_2012"]
    lim_hora = "Hora de paso no disponible."
    if hp["2000-2009"] and hp["2013-2016"]:
        lim_hora = (f"La hora de paso de Landsat 7 se fue retrasando (deriva orbital): {hp['2000-2009'][0]}–{hp['2000-2009'][1]} "
                    f"en 2000-2009, {hp['2010-2012'][0]}–{hp['2010-2012'][1]} en 2010-2012 y {hp['2013-2016'][0]}–"
                    f"{hp['2013-2016'][1]} en 2013-2016 (medias anuales). Pasar más tarde podría aumentar el contraste "
                    "ciudad-campo")
        if pm and esc:
            lim_hora += (f", pero en 2000-2012 la isla por escena no aumenta con la hora de paso ("
                         f"{fc(pm['c_por_min']['coef'], 2, True)} °C por minuto, p = {fc(pm['c_por_min']['p'], 2)}) y, "
                         f"controlando hora de paso y mes, el escalón 2013 sigue siendo {fc(esc['escalon_c']['coef'], 2, True)} °C "
                         f"(IC 95 % {fc(esc['escalon_c']['ic95'][0], 2, True)} a {fc(esc['escalon_c']['ic95'][1], 2, True)}; "
                         "regresiones_por_escena). No hay indicios de que la deriva de la hora explique el salto.")
        else:
            lim_hora += "."
    return {
        "descripcion": (f"Misma metodología que la serie principal pero solo con Landsat 7 ETM+ en {CONTROL_L7[0]}-{CONTROL_L7[1]}: "
                        "un único sensor a ambos lados de 2013, para separar el salto de 2012-2013 del cambio de sensor. "
                        "No escribe rejillas anuales."),
        "hora_local_paso": hp,
        "anios": [{k: r[k] for k in claves if k in r} for r in control],
        "antes_y_despues_de_2013": comp,
        "regresiones_por_escena": reg,
        "procesamiento_usgs_por_periodo": procs,
        "tendencias": tend,
        "lectura": lect,
        "limitaciones": [
            lim_hora,
            "Landsat 7 tiene SLC-off desde el 31-05-2003 (bandas sin dato); 2000-2002 no.",
            "2013-2016 son solo 4 años: el control muestra el nivel después de 2013, no una tendencia posterior.",
        ],
    }


def cambios_version(escenas, campo):
    """Cambios de un campo de procedencia (MTL) a lo largo de las fechas de adquisición."""
    f = sorted((e["fecha"], e.get(campo)) for e in escenas if e.get(campo) and e.get("procedencia_origen") == "MTL")
    return [{"antes": a0, "ultima_adquisicion_antes": f0, "despues": a1, "primera_adquisicion_despues": f1}
            for (f0, a0), (f1, a1) in zip(f, f[1:]) if a1 != a0]


def sensibilidad_geos_it(anios, tend):
    """Sensibilidad del tramo Landsat 8/9 al cambio de reanálisis GEOS-5 FP-IT → GEOS-IT (adquisiciones desde 2024)."""
    from scipy import stats
    corte = int(GEOS_IT_DESDE[:4])
    escenas = [e for r in anios if r["anio"] >= 2013 for e in r["escenas"]]
    cuenta = Counter((e["reanalisis_st"], e["procedencia_origen"]) for e in escenas)
    escalon = {}
    for fam, (unidad, vs) in FAMILIAS.items():
        escalon[fam] = {}
        for var, campo in vs.items():
            pts = [(r["anio"], r[campo]) for r in anios if r.get("confiable") and 2013 <= r["anio"] <= 2025
                   and r.get(campo) is not None]
            if len(pts) < 8 or sum(a >= corte for a, _ in pts) < 1:
                continue
            x = np.array([a for a, _ in pts], float)
            X = np.column_stack([np.ones(len(x)), (x - 2013) / 10.0, (x >= corte).astype(float)])
            r = mco(X, [v for _, v in pts], ["const", "pendiente_por_decada", "escalon_2024"], robusto=False)
            escalon[fam][var] = {"pendiente_por_decada": r["pendiente_por_decada"], "escalon_2024": r["escalon_2024"],
                                 "n_anios": r["n"]}
    por_escena = {}
    for campo in ("isla_calor", "lst_mediana_urbana", "lst_mediana_rural"):
        a = [e[campo] for e in escenas if e["reanalisis_st"] == "GEOS-5 FP-IT" and e.get(campo) is not None
             and e.get("apta_metricas_escena", True)]
        b = [e[campo] for e in escenas if e["reanalisis_st"] == "GEOS-5 IT" and e.get(campo) is not None
             and e.get("apta_metricas_escena", True)]
        if len(a) >= 3 and len(b) >= 3:
            w = stats.ttest_ind(b, a, equal_var=False)
            por_escena[campo] = {"media_geos_fp_it_2013_2023": r3(np.mean(a)), "n_fp_it": len(a),
                                 "media_geos_it_2024_2025": r3(np.mean(b)), "n_it": len(b),
                                 "diferencia": r3(np.mean(b) - np.mean(a)), "p_welch": float(f"{w.pvalue:.3g}")}
    l13_23 = {fam: (t.get("2013_2023_landsat_8_9_geos_fp_it") or {}).get("resumen", {}).get("lectura")
              for fam, t in tend.items()}
    cambios = {c: cambios_version(escenas, c) for c in ("reanalisis_st", "algoritmo_st", "aux_atm_sr")}
    algs = {}
    for r in anios:
        for e in r["escenas"]:
            if e.get("algoritmo_st"):
                algs.setdefault(e["algoritmo_st"], set()).add(r["anio"])
    return {
        "descripcion": ("El USGS cambió el reanálisis atmosférico del producto ST de GEOS-5 FP-IT a GEOS-5 IT para las "
                        f"adquisiciones desde el {GEOS_IT_DESDE} (LSDS-1619 v6.0, mayo de 2024; MTL DATA_SOURCE_REANALYSIS). "
                        "Sensibilidades: (1) tramo 2013-2023 solo FP-IT (tendencias/lectura_de_tendencias, clave "
                        "2013_2023_landsat_8_9_geos_fp_it); (2) MCO anual 2013-2025 con un escalón en 2024 (pocas observaciones "
                        "después del corte: orientativo); (3) métricas por escena antes y después del cambio."),
        "escenas_serie_l8_9_por_reanalisis": {f"{k[0]} ({k[1]})": v for k, v in sorted(cuenta.items())},
        "versiones_algoritmo_st_por_anio": {k: sorted(v) for k, v in sorted(algs.items())},
        "cambios_de_procesamiento_l8_9_segun_mtl": cambios,
        "lectura_2013_2023": l13_23,
        "mco_con_escalon_2024": escalon,
        "por_escena": por_escena,
    }


def sintesis_salto(anios, sol, rc, salto, tend):
    """Conclusión de síntesis sobre el salto de la isla de calor entre 2012 y 2013, construida con los datos."""
    out = {"pregunta": "¿Creció la isla de calor superficial de la cabecera entre 2000 y 2025?"}
    variantes = FAMILIAS["isla_calor"][1]
    sal = {v: salto.get(c) for v, c in variantes.items() if salto.get(c)}
    if not sal:
        return None
    difs = [s["diferencia"] for s in sal.values()]
    sin_sensor = [s["diferencia_sin_efecto_sensor"] for s in sal.values() if s.get("diferencia_sin_efecto_sensor") is not None]
    efectos = [s["efecto_sensor_estimado"] for s in sal.values() if s.get("efecto_sensor_estimado") is not None]
    ic_con_0 = all(s["efecto_sensor_ic95"][0] <= 0 <= s["efecto_sensor_ic95"][1] for s in sal.values()
                   if s.get("efecto_sensor_ic95"))
    out["serie_principal_2013_2025_menos_2000_2012"] = sal
    t_ant = tend["isla_calor"]["2000_2012_landsat_5_7"]["resumen"]
    t_nue = tend["isla_calor"]["2013_2025_landsat_8_9"]["resumen"]
    sin_tend = not t_ant.get("variantes_significativas") and not t_nue.get("variantes_significativas")
    out["tendencia_dentro_de_cada_tramo"] = {"2000_2012": t_ant.get("lectura"), "2013_2025": t_nue.get("lectura")}
    reg = (rc or {}).get("regresiones_por_escena") or {}
    pp = reg.get("isla_calor_por_periodo") or {}
    esc = reg.get("isla_calor_escalon_2013")
    esc_1016 = reg.get("isla_calor_escalon_2013_solo_2010_2016")
    pm = reg.get("isla_calor_vs_hora_2000_2012")
    c2000 = salto.get("isla_calor_construido_2000")
    c2000_l7 = ((rc or {}).get("antes_y_despues_de_2013") or {}).get("isla_calor_construido_2000")
    procs = (rc or {}).get("procesamiento_usgs_por_periodo") or {}
    out.update({"control_landsat_7": {"isla_por_periodo": pp, "escalon_controlando_hora_y_mes": esc,
                                      "escalon_solo_2010_2016": esc_1016, "isla_vs_hora_2000_2012": pm},
                "zona_construida_en_2000": {"serie_principal": c2000, "control_landsat_7": c2000_l7},
                "procesamiento_usgs_landsat_7": procs})

    txt = [(f"La isla de calor superficial de la cabecera (mañana, días despejados) es en 2013-2025 entre "
            f"{fc(min(difs), 1, True)} y {fc(max(difs), 1, True)} °C mayor que en 2000-2012 según la variante"
            + (f" ({fc(min(sin_sensor), 1, True)} a {fc(max(sin_sensor), 1, True)} °C descontando el efecto de sensor estimado)"
               if sin_sensor else "") + ".")]
    if sin_tend:
        txt.append("No es un aumento gradual: ni dentro de 2000-2012 ni dentro de 2013-2025 hay tendencia significativa en "
                   "ninguna variante. El cambio es un escalón entre 2012 y 2013.")
    else:
        txt.append(f"Dentro de cada tramo: 2000-2012, {t_ant.get('lectura')} 2013-2025, {t_nue.get('lectura')}")
    causas = []
    if efectos and ic_con_0 and pp.get("2010-2012") and pp.get("2013-2016"):
        causas.append(
            f"No lo explica el cambio de sensor: el efecto L8 − L7 medido en el solape es pequeño ({fc(min(efectos), 1, True)} a "
            f"{fc(max(efectos), 1, True)} °C, IC 95 % que incluye 0 en todas las variantes) y con un solo sensor (Landsat 7) la "
            f"isla por escena pasa de {fc(pp['2010-2012']['media'])} °C en 2010-2012 a {fc(pp['2013-2016']['media'])} °C en "
            f"2013-2016 ({fc(pp['2000-2009']['media'])} °C en 2000-2009)." if pp.get("2000-2009") else "")
    if esc and pm:
        e_, cm = esc["escalon_c"], pm["c_por_min"]
        sube = cm["coef"] > 0 and cm["p"] < SIG_P
        hora_ok = e_["ic95"][0] > 0 and not sube
        sub = ""
        if esc_1016:
            e2 = esc_1016["escalon_c"]
            sub = (f"; solo con 2010-2016, cuando las horas de paso se solapan, {fc(e2['coef'], 1, True)} °C (IC 95 % "
                   f"{fc(e2['ic95'][0], 1, True)} a {fc(e2['ic95'][1], 1, True)}"
                   + (", parecido pero menos preciso por tener menos escenas)" if e2["ic95"][0] <= 0 <= e2["ic95"][1] else ")"))
        causas.append(
            ("No hay indicios de que lo expliquen la hora de paso ni la estación: " if hora_ok else
             "La hora de paso y la estación podrían explicar parte del salto: ")
            + (f"dentro de 2000-2012 la isla sube {fc(cm['coef'], 2, True)} °C por minuto de retraso del paso (p = {fc(cm['p'], 2)})"
               if sube else f"dentro de 2000-2012 la isla no sube cuando Landsat 7 pasa más tarde ({fc(cm['coef'], 2, True)} °C "
               f"por minuto, p = {fc(cm['p'], 2)})")
            + f", y con una regresión por escena (isla ~ periodo + hora de paso + mes) el escalón de Landsat 7 es "
            f"{fc(e_['coef'], 1, True)} °C (IC 95 % {fc(e_['ic95'][0], 1, True)} a {fc(e_['ic95'][1], 1, True)})" + sub + ".")
    if c2000 and c2000.get("p_welch") is not None:
        causas.append(
            f"No es solo expansión urbana: en las celdas ya construidas en 2000 (NDVI medio 2000-2002 < "
            f"{fc(NDVI_CONSTRUIDO_2000, 2)}) la isla pasa de {fc(c2000['media_2000_2012'])} a {fc(c2000['media_2013_2025'])} °C "
            f"({fc(c2000['diferencia'], 1, True)} °C, Welch p = {fc(c2000['p_welch'], 2)})"
            + (f" y, solo con Landsat 7, de {fc(c2000_l7['media_2000_2012'])} a {fc(c2000_l7['media_2013_2016'])} °C "
               f"(Welch p = {fc(c2000_l7['p_welch'], 2)})" if c2000_l7 else "") + ".")
    p12, p13 = procs.get("2010-2012") or {}, procs.get("2013-2016") or {}
    if p12.get("con_MTL") and p13.get("con_MTL"):
        igual = all(p12.get(k) == p13.get(k) for k in ("software_l2", "algoritmo_st", "reanalisis_st"))
        causas.append(
            ("Los metadatos MTL de Landsat 7 no registran cambio de procesamiento entre 2012 y 2013 (mismo software "
             f"{', '.join(p12['software_l2'])}, algoritmo {', '.join(p12['algoritmo_st'])} y reanálisis "
             f"{', '.join(p12['reanalisis_st'])}); eso no descarta cambios no registrados en el MTL." if igual else
             f"Los metadatos MTL de Landsat 7 sí cambian entre 2010-2012 ({p12}) y 2013-2016 ({p13})."))
    txt += [c for c in causas if c]
    txt.append("La causa del escalón no está determinada: puede ser un cambio real (de la superficie o del clima de esos "
               "años) o un artefacto del producto que no aparece en sus metadatos; con estos datos no se puede decidir. "
               "Para decidir: no leer el salto 2012-2013 como una tendencia de calentamiento urbano"
               + (f"; la isla de 2013-2025 no muestra tendencia significativa en ninguna variante (Sen entre "
                  f"{fmt(t_nue['sen_min'], '°C')} y {fmt(t_nue['sen_max'], '°C')} °C/década)."
                  if "sen_min" in t_nue and not t_nue.get("variantes_significativas") else
                  f"; en 2013-2025: {t_nue.get('lectura')}"))
    out["texto"] = txt
    out["conclusion"] = " ".join(txt)
    return out


def escribir_serie(anios, sol, M, control=None):
    conf = [r for r in anios if r["confiable"]]
    no_conf = {r["anio"]: r.get("motivo_no_confiable", []) for r in anios if not r["confiable"]}
    horas = [e["hora_local"] for r in anios for e in r["escenas"]]
    hmin, hmax = (min(horas), max(horas)) if horas else ("?", "?")
    ant = [e["hora_local"] for r in anios if r["anio"] < 2013 for e in r["escenas"]] or ["?"]
    nue = [e["hora_local"] for r in anios if r["anio"] >= 2013 for e in r["escenas"]] or ["?"]
    h_ant, h_nue = (min(ant), max(ant)), (min(nue), max(nue))
    m_ant = [e["minutos_locales"] for r in anios if r["anio"] < 2013 for e in r["escenas"]]
    m_nue = [e["minutos_locales"] for r in anios if r["anio"] >= 2013 for e in r["escenas"]]
    n_slc = sum(e["slc_off"] for r in anios for e in r["escenas"])
    n_tot = sum(r["n_escenas"] for r in anios)
    frias = {r["anio"]: r["celdas_frias_residuales"] for r in anios if r.get("celdas_frias_residuales")}
    delta = (sol or {}).get("efecto_sensor_l8_menos_l7")
    ic = (sol or {}).get("efecto_sensor_ic95") or {}
    delta_ext = {"inferior": {c: v[0] for c, v in ic.items() if v}, "superior": {c: v[1] for c, v in ic.items() if v}}
    tend, lect = {}, {}
    for fam, (unidad, vs) in FAMILIAS.items():
        tend[fam] = {"unidad": unidad}
        lect[fam] = {}
        for tramo, d, h, arm in TRAMOS:
            if arm and not delta:
                continue
            vs = variantes_de(fam, d)
            variantes = {var: tendencia(anios, campo, d, h, arm, delta) for var, campo in vs.items()}
            if arm:
                extremos = {n: {var: tendencia(anios, campo, d, h, True, dx) for var, campo in vs.items()}
                            for n, dx in delta_ext.items()}
                le = lectura_armonizada(variantes, extremos, unidad)
                tend[fam][tramo] = {"variantes": variantes, "con_extremos_ic95_efecto_sensor": extremos, "resumen": le}
            else:
                le = lectura(variantes, unidad)
                tend[fam][tramo] = {"variantes": variantes, "resumen": le}
            lect[fam][tramo] = le["lectura"]
    for r in anios:  # valores armonizados (L5/L7 + efecto de sensor) para trazabilidad
        if r["anio"] < 2013 and delta:
            r["armonizado_a_landsat_8"] = {c: r3(valor(r, c, True, delta)) for c in list(CAMPOS_GRILLA) + list(CAMPOS_ESCENA)
                                           if r.get(c) is not None}
    salto = salto_entre_sensores(anios, sol)
    rc = resumen_control(control)
    if rc:
        hp = rc["hora_local_paso"]
        for fam in lect:
            lect[fam][f"{CONTROL_L7[0]}_{CONTROL_L7[1]}_solo_landsat_7"] = (
                rc["lectura"][fam].rstrip(".") + f" (control con un solo sensor; hora de paso {hp['2000-2009'][0]}–"
                f"{hp['2000-2009'][1]} en 2000-2009, {hp['2010-2012'][0]}–{hp['2010-2012'][1]} en 2010-2012 y "
                f"{hp['2013-2016'][0]}–{hp['2013-2016'][1]} en 2013-2016).")
    geos = sensibilidad_geos_it(anios, tend)
    sint = sintesis_salto(anios, sol, rc, salto, tend)
    hallazgos = []
    if sint:
        hallazgos += ["Isla de calor 2000-2025. " + sint["texto"][0]] + sint["texto"][1:]
    pe = geos["por_escena"].get("isla_calor")
    esc24 = [v["escalon_2024"] for v in geos["mco_con_escalon_2024"].get("isla_calor", {}).values()]
    t23 = tend["isla_calor"]["2013_2023_landsat_8_9_geos_fp_it"]["resumen"]
    t25 = tend["isla_calor"]["2013_2025_landsat_8_9"]["resumen"]
    calg = geos["cambios_de_procesamiento_l8_9_segun_mtl"].get("algoritmo_st") or []
    if pe:
        hallazgos.append(
            "Cambio de procesamiento del USGS en 2024 (reanálisis GEOS-5 FP-IT → GEOS-IT en la temperatura superficial): la "
            f"isla por escena es {fc(pe['media_geos_it_2024_2025'])} °C en 2024-2025 ({pe['n_it']} escenas) frente a "
            f"{fc(pe['media_geos_fp_it_2013_2023'])} °C en 2013-2023 ({pe['n_fp_it']}; Welch p = {fc(pe['p_welch'], 2)})"
            + (f"; un escalón en 2024 en la serie anual da entre {fc(min(e['coef'] for e in esc24), 1, True)} y "
               f"{fc(max(e['coef'] for e in esc24), 1, True)} °C según la variante, "
               + ("ninguno con IC 95 % que excluya 0" if all(e["ic95"][0] <= 0 <= e["ic95"][1] for e in esc24)
                  else "alguno con IC 95 % que excluye 0") if esc24 else "")
            + (f". Sin 2024-2025 (todo con FP-IT) la pendiente de Sen de la isla es de {fmt(t23['sen_min'], '°C')} a "
               f"{fmt(t23['sen_max'], '°C')} °C/década, frente a {fmt(t25['sen_min'], '°C')} a {fmt(t25['sen_max'], '°C')} con "
               f"2024-2025; {'ninguna variante es significativa en ninguno de los dos tramos' if not t23.get('variantes_significativas') and not t25.get('variantes_significativas') else 'ver lectura_de_tendencias'}"
               if "sen_min" in t23 and "sen_min" in t25 else "")
            + ". No se puede separar el efecto del reanálisis del clima de 2024-2025 (incluye el final de El Niño 2023-2024)."
            + "".join(f" Además, según los MTL el algoritmo ST pasó de {c['antes']} a {c['despues']} entre las adquisiciones del "
                      f"{c['ultima_adquisicion_antes']} y el {c['primera_adquisicion_despues']} (no se encontró documentación "
                      "del USGS sobre ese cambio)." for c in calg))
    l_u = lect["ndvi_urbano"]["2013_2025_landsat_8_9"]
    l_r = lect["ndvi_rural"]["2013_2025_landsat_8_9"]
    l_p = lect["ndvi_periurbano"]["2013_2025_landsat_8_9"]
    ru = tend["ndvi_urbano"]["2013_2025_landsat_8_9"]["resumen"]
    rr = tend["ndvi_rural"]["2013_2025_landsat_8_9"]["resumen"]
    rp = tend["ndvi_periurbano"]["2013_2025_landsat_8_9"]["resumen"]
    local = ru.get("robusta") and not rr.get("variantes_significativas") and not rp.get("variantes_significativas")
    v2000 = tend["ndvi_urbano"]["2013_2025_landsat_8_9"]["variantes"].get("construido_en_2000") or {}

    def mi(t):
        return t[:1].lower() + t[1:]
    hallazgos.append(
        f"Vegetación 2013-2025 (Landsat 8/9). En la cabecera, {mi(l_u)} En el campo a la misma altitud (control), {mi(l_r)} "
        f"En las zonas verdes de la cabecera (periurbano), {mi(l_p)} "
        + ("La caída se concentra en la parte construida de la cabecera; no la reproduce el campo, así que no parece un "
           "efecto del sensor ni un cambio regional de la vegetación. " if local else
           "La comparación con el campo no permite decir que la caída sea solo local. ")
        + "El núcleo se define con WorldCover 2021 y puede incluir celdas construidas después de 2013"
        + (f"; en las celdas ya construidas en 2000 la caída también aparece (Sen {fmt(v2000['sen_por_decada'], 'NDVI')} "
           f"NDVI/década, IC 95 % {fmt(v2000['sen_ic95_por_decada'][0], 'NDVI')} a {fmt(v2000['sen_ic95_por_decada'][1], 'NDVI')})"
           ", de modo que no es solo urbanización nueva." if v2000.get("sen_por_decada") is not None and significativa(v2000)
           else "; con estos datos no se separa la urbanización nueva de la pérdida de vegetación en lo ya construido."))
    efectos_isla = [salto[c] for c in FAMILIAS["isla_calor"][1].values() if salto.get(c) and salto[c].get("efecto_sensor_ic95")]
    pp_ = (((rc or {}).get("regresiones_por_escena") or {}).get("isla_calor_por_periodo") or {})
    if efectos_isla and pp_.get("2010-2012") and pp_.get("2013-2016"):
        adv_sensor = (
            "El salto de la isla de calor entre 2012 y 2013 coincide con el cambio de sensor, pero el efecto de sensor "
            f"estimado en el solape 2013-2016 va de {fc(min(x['efecto_sensor_estimado'] for x in efectos_isla), 1, True)} a "
            f"{fc(max(x['efecto_sensor_estimado'] for x in efectos_isla), 1, True)} °C según la variante "
            + ("(IC 95 % que incluye 0 en todas)" if all(x["efecto_sensor_ic95"][0] <= 0 <= x["efecto_sensor_ic95"][1]
                                                         for x in efectos_isla) else "(con algún IC 95 % que excluye 0)")
            + f" y con un solo sensor (Landsat 7) la isla por escena pasa de {fc(pp_['2010-2012']['media'])} °C en 2010-2012 a "
            f"{fc(pp_['2013-2016']['media'])} °C en 2013-2016 (sintesis_salto_2012_2013). En la LST absoluta (urbana y "
            "rural) el efecto de sensor estimado es mayor y su IC 95 % es ancho (salto_entre_sensores).")
    else:
        adv_sensor = ("El salto entre 2012 y 2013 coincide con el cambio de sensor; el solape 2013-2016 permite estimar cuánto "
                      "se debe al sensor (salto_entre_sensores).")
    pm_ = ((rc or {}).get("regresiones_por_escena") or {}).get("isla_calor_vs_hora_2000_2012")
    adv_hora = ""
    if pm_:
        c_ = pm_["c_por_min"]
        adv_hora = (f" Para la isla de calor, dentro de 2000-2012 con Landsat 7 la relación con la hora de paso es "
                    f"{fc(c_['coef'], 2, True)} °C por minuto (IC 95 % {fc(c_['ic95'][0], 2, True)} a {fc(c_['ic95'][1], 2, True)}; "
                    "control_solo_landsat_7.regresiones_por_escena).")
    desc = M["descripcion"]
    salida = {
        "titulo": "Serie anual Landsat 2000–2025: temperatura superficial y NDVI de Cartago",
        "descripcion": (f"Por año, mediana por celda de hasta 6 escenas Landsat despejadas (media mañana, entre {hmin} y {hmax} "
                        "hora local según el año) y luego resumen espacial en la cabecera, su núcleo construido y el campo a "
                        "la misma altitud. La isla de calor superficial es la diferencia ciudad − campo. Las tendencias se "
                        "dan como rango entre métodos y por tramo de sensor; no hay una cifra única."),
        "unidades": {"lst": "°C", "ndvi": "adimensional (−1 a 1)", "isla_calor": "°C", "pct": "%"},
        "fuente": {
            "nombre": "USGS Landsat Collection 2 Level-2 (L5 TM, L7 ETM+, L8-9 OLI/TIRS), vía Microsoft Planetary Computer",
            "url": "https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2",
            "licencia": "Dominio público (USGS): sin restricciones de uso ni redistribución; se pide citar la fuente",
            "cita": ("Landsat Collection 2 Level-2 Science Products courtesy of the U.S. Geological Survey. "
                     "doi:10.5066/P9IAXOVV (L4-5), doi:10.5066/P9C7I13B (L7), doi:10.5066/P9OGBGM6 (L8-9)"),
        },
        "fuentes_secundarias": fuentes_secundarias(),
        "hallazgos": hallazgos,
        "lectura_de_tendencias": lect,
        "sintesis_salto_2012_2013": sint,
        "metodo": {
            "sensores_por_periodo": {"2000-2012": "Landsat 5 TM y Landsat 7 ETM+ (ST_B6; rojo SR_B3, NIR SR_B4)",
                                     "2013-2025": "Landsat 8 y 9 (ST_B10; rojo SR_B4, NIR SR_B5)"},
            "escenas": "Solo Tier 1, ruta/fila WRS-2 009/057.",
            "seleccion": (f"La misma regla en todos los años: se preseleccionan las {CANDIDATOS_POR_ANIO} escenas de menor "
                          f"eo:cloud_cover, se mide con QA_PIXEL el % despejado sobre la rejilla y se eligen hasta {MAX_POR_ANIO} con "
                          f"≥ {fg(MIN_DESPEJADO)} %, las más despejadas primero con un máximo de {MAX_POR_TRIMESTRE} por trimestre; "
                          "si faltan, se completan sin esa restricción."),
            "mascara_qa": "QA_PIXEL bits 0,1,2(solo L8/9),3,4,5 = 1 → descartado.",
            "filtro_nubes_no_detectadas": (f"Se descarta la escena si ≥ {fg(100 * FRIO_FRAC)} % de sus píxeles despejados están más de "
                                           f"{fg(FRIO_C)} °C por debajo del compuesto LST 2022-2025 (capa lst, que a su vez usa el "
                                           "mismo filtro iterado hasta converger) y se reemplaza por la siguiente candidata. "
                                           "Umbrales propios (supuesto empírico), no normativos."),
            "metricas_por_escena": (f"La variante mediana_por_escena usa solo escenas «aptas»: ≥ {fg(MIN_CABECERA_ESCENA)} % de la "
                                    f"cabecera despejada, ≥ {fg(MIN_RURAL_ESCENA)} % de la referencia rural con dato y menos del "
                                    f"{fg(100 * FRIO_FRAC)} % de la cabecera más de {fg(FRIO_C)} °C bajo el compuesto (supuestos). "
                                    "Las demás escenas siguen en la rejilla anual (campos apta_metricas_escena y motivo_no_apta)."),
            "procedencia": ("De cada escena se lee su MTL (LEVEL2_PROCESSING_RECORD; _MTL.json o, si falta en el "
                            "almacenamiento, _MTL.txt): reanálisis atmosférico del ST (DATA_SOURCE_REANALYSIS, normalizado: el "
                            "MTL escribe «GEOS-5 FP-IT» o «GEOS-5FP-IT»), versiones de los algoritmos ST y SR, dato auxiliar "
                            "atmosférico de la reflectancia (DATA_SOURCE_WATER_VAPOR), software y fecha de producción (campos "
                            "reanalisis_st, algoritmo_st, algoritmo_sr, aux_atm_sr, software_l2, fecha_producto). Si el MTL no "
                            f"se puede leer, el reanálisis se asigna por fecha (GEOS-IT desde el {GEOS_IT_DESDE}) y "
                            "procedencia_origen lo indica."),
            "lst": "K = DN×0,00341802 + 149,0; °C = K − 273,15.",
            "ndvi": "SR = DN×0,0000275 − 0,2; NDVI = (NIR − Rojo)/(NIR + Rojo), con reflectancias en (0, 1].",
            "rejilla": (f"Bilineal a la rejilla común (0,00025°, EPSG:4326); mediana anual por celda; celdas con menos de "
                        f"{N_MIN_ANUAL} observaciones en el año → sin dato."),
            "zonas": {
                "cabecera": "comun.mascara_urbana() (polígono OSM actual, fijo en toda la serie).",
                "nucleo_construido": f"Celdas de la cabecera con ≥ {fg(NUCLEO_CONSTRUIDO_MIN)} % construido (WorldCover 2021).",
                "rural": (f"Fuera de la cabecera, a más de {fg(RURAL_DIST_M)} m, sin agua (bit 7 de QA_PIXEL en ≥ 50 % de las "
                          "observaciones 2022-2025 y WorldCover agua < 50 %), construido < "
                          f"{fg(RURAL_CONSTRUIDO_MAX)} % y altitud entre {fc(desc['rural_altitud_m'][0])} y "
                          f"{fc(desc['rural_altitud_m'][1])} m (± {fg(RURAL_ALT_BANDA_M)} m de la mediana de la cabecera, "
                          "Copernicus DEM)."),
                "construido_en_2000": (f"Celdas de la cabecera con NDVI medio 2000-2002 < {fc(NDVI_CONSTRUIDO_2000, 2)} (supuesto; "
                                       "rejillas anuales de Landsat 5/7 de esta serie): superficie ya construida o desnuda en "
                                       "2000. Polígono fijo definido con el estado inicial, a diferencia del núcleo WorldCover "
                                       f"2021. {int(M['construido_2000'].sum()) if M.get('construido_2000') is not None else 0} celdas. "
                                       "Como se selecciona con datos de 2000-2002, esos años pueden salir algo más «construidos» "
                                       "de lo que son (regresión a la media): en la isla eso tiende a subestimar el salto "
                                       "posterior; el NDVI de esta zona solo se usa en tramos desde 2003."),
                "descripcion": desc,
            },
            "variantes": {
                "mediana_poligono": "Mediana espacial de la rejilla anual en la cabecera (menos rural).",
                "media_poligono": "Media espacial en la cabecera (menos media rural).",
                "nucleo_construido": "Mediana espacial en el núcleo construido (menos mediana rural).",
                "mediana_por_escena": "Mediana entre las escenas aptas del año de la métrica calculada escena por escena.",
                "construido_en_2000": "Mediana espacial en la zona construida ya en 2000 (menos mediana rural).",
                "mediana / media (ndvi_rural, ndvi_periurbano)": ("Controles del NDVI urbano: campo a la misma altitud y "
                                                                  "zonas verdes (< 20 % construido) de la cabecera."),
            },
            "confiable": (f"≥ {CONF_MIN_ESCENAS} escenas, en ≥ {CONF_MIN_TRIMESTRES} trimestres distintos y ≥ "
                          f"{fg(CONF_MIN_PCT_URBANO)} % de las celdas de la cabecera con dato."),
            "tendencias": ("Solo años confiables. Pendiente de Sen con IC 95 % (scipy.stats.theilslopes), prueba de Mann-Kendall "
                           "como τ de Kendall entre año y valor (scipy.stats.kendalltau) y MCO con IC 95 % (t de Student) y "
                           "p-valor (scipy.stats.linregress). Unidades por década. Una variante cuenta como significativa si "
                           f"Mann-Kendall y MCO dan p < {str(SIG_P).replace(".", ",")} y el IC 95 % de Sen excluye 0; la tendencia es «robusta» solo "
                           "si todas las variantes lo son con el mismo signo."),
            "tramos": {"2013_2025_landsat_8_9": ("Un solo tipo de sensor (TIRS); tramo preferente. Incluye el cambio de "
                                                 "reanálisis del USGS en 2024 (ver sensibilidad_geos_it)."),
                       "2013_2023_landsat_8_9_geos_fp_it": ("Sensibilidad: Landsat 8/9 sin 2024-2025, todo con el reanálisis "
                                                            "GEOS-5 FP-IT."),
                       "2000_2012_landsat_5_7": "Landsat 5 TM y 7 ETM+ (SLC-off desde mayo de 2003).",
                       "2000_2025_armonizada": ("Años 2000-2012 + efecto de sensor L8 − L7 estimado en el solape "
                                                f"{SOLAPE[0]}-{SOLAPE[1]} (ver solape_landsat_7_8). Orientativa; se exige "
                                                "que la conclusión se mantenga con ambos extremos del IC 95 % del efecto."),
                       f"{CONTROL_L7[0]}_{CONTROL_L7[1]}_solo_landsat_7": ("Control con un único sensor (Landsat 7) a ambos "
                                                                          "lados de 2013; ver control_solo_landsat_7.")},
            "rejillas_anuales": ("fuentes/rejilla/lst_<año>.npy y ndvi_<año>.npy (float32, NaN = sin dato) y "
                                 "lst_n_<año>.npy, ndvi_n_<año>.npy (uint8, observaciones por celda), no publicadas."),
        },
        "advertencias": [
            "No decidir con una sola cifra de tendencia ni con su p-valor: el resultado cambia con la zona (polígono, núcleo "
            "construido), el estadístico (mediana, media, por escena) y el tramo de sensor. Úsese «lectura_de_tendencias».",
            "Cambio de sensor: 2000–2012 proviene de Landsat 5/7 (banda térmica única, 120 m en TM y 60 m en ETM+) y 2013–2025 de "
            "Landsat 8/9 (TIRS, 100 m). " + adv_sensor,
            "Cambio de procesamiento del USGS: desde las adquisiciones del 1-1-2024 el producto ST usa el reanálisis GEOS-5 IT "
            "(GEOS-IT) en lugar de GEOS-5 FP-IT (guía LSDS-1619 v6.0, mayo de 2024; campo DATA_SOURCE_REANALYSIS del MTL, "
            "guardado por escena en reanalisis_st). El tramo Landsat 8/9 no es homogéneo en 2024-2025 y sus extremos pesan "
            "más en la pendiente: compárese con el tramo 2013_2023_landsat_8_9_geos_fp_it y con sensibilidad_geos_it. Las "
            "actualizaciones con 2026 en adelante serán solo GEOS-IT."
            + "".join(f" Los MTL registran además el paso del algoritmo ST de {c['antes']} a {c['despues']} entre las "
                      f"adquisiciones del {c['ultima_adquisicion_antes']} y el {c['primera_adquisicion_despues']} (sin "
                      "documentación del USGS encontrada)." for c in geos["cambios_de_procesamiento_l8_9_segun_mtl"]["algoritmo_st"])
            + "".join(f" Para la reflectancia (NDVI), el dato auxiliar atmosférico pasa de {c['antes']} a {c['despues']} entre el "
                      f"{c['ultima_adquisicion_antes']} y el {c['primera_adquisicion_despues']} (LSDS-1619 v6.0: MODIS C6 hasta el "
                      "16-2-2023, C6.1 hasta el 30-9-2023 y VIIRS desde el 1-10-2023)."
                      for c in geos["cambios_de_procesamiento_l8_9_segun_mtl"]["aux_atm_sr"]),
            "Landsat 7 perdió el corrector de líneas (SLC) el 31 de mayo de 2003: desde entonces cada escena tiene bandas sin "
            f"datos (≈ 22 % de los píxeles en el conjunto de la escena). En esta serie {n_slc} de {n_tot} escenas son SLC-off.",
            f"Con {min(r['n_escenas'] for r in anios)} a {max(r['n_escenas'] for r in anios)} escenas por año, la mediana "
            "depende de qué meses quedaron despejados (temporada seca o lluviosa) y de la hora de paso; la variación entre "
            "años no es solo climática."
            + (f" Años no confiables: {', '.join(f'{a} ({'; '.join(m)})' for a, m in no_conf.items())}." if no_conf else ""),
            f"Hora de paso: Landsat 5/7 entre {h_ant[0]} y {h_ant[1]} (media {hhmm(np.mean(m_ant)) if m_ant else '?'}) y Landsat "
            f"8/9 entre {h_nue[0]} y {h_nue[1]} (media {hhmm(np.mean(m_nue)) if m_nue else '?'}), hora local. A media mañana la "
            "superficie se calienta rápido, así que esa diferencia también puede mover la LST absoluta." + adv_hora,
            "NDVI entre sensores: OLI (Landsat 8/9) tiene bandas más estrechas que TM/ETM+ y, sobre vegetación, su NDVI es en "
            "promedio mayor que el de ETM+ (Roy et al., 2016, Remote Sensing of Environment 185: 57–70). Solo se corrige con el "
            "efecto medido en el solape (serie armonizada, orientativa).",
            "La cabecera es el polígono actual de OpenStreetMap para todos los años, y el núcleo construido sale de WorldCover "
            "2021: una celda que se urbanizó después de 2000 cuenta como urbana en toda la serie, de modo que los cambios de la "
            "isla de calor y del NDVI urbano mezclan expansión y densificación con cambios dentro del área ya construida. "
            "Definir el núcleo con el estado final (2021) selecciona celdas que se construyeron entre 2013 y 2021 y sesga el "
            "NDVI del núcleo hacia la caída; la variante construido_en_2000 (estado inicial) y los controles ndvi_rural y "
            "ndvi_periurbano sirven de contraste.",
            f"El polígono de la cabecera es heterogéneo ({fc(100 * desc['periurbano_frac_cabecera'], 0)} % de sus celdas con menos de "
            f"20 % construido, {fc(100 * desc['nucleo_frac_cabecera'], 0)} % con 80 % o más): la LST y el NDVI de la cabecera son "
            "bimodales y su mediana espacial cae entre los dos modos, donde un cambio pequeño la mueve mucho. Por eso la "
            "mediana del polígono exagera la caída del NDVI urbano frente a la media o al núcleo construido.",
            "La referencia rural (misma franja de altitud, sin construcción ni agua) depende de umbrales propios y de capas de "
            "otros productos (WorldCover 2021, Copernicus DEM).",
            "La LST es temperatura de superficie a media mañana en días despejados, no temperatura del aire.",
            "La prueba de Mann-Kendall no corrige autocorrelación; con 13 años por tramo los p-valores son orientativos.",
            ("Nubes residuales en las rejillas anuales: aun con el filtro por escena y el mínimo de "
             f"{N_MIN_ANUAL} observaciones por celda, quedan celdas más de {fg(FRIO_C)} °C por debajo del compuesto 2022-2025 "
             f"(campo celdas_frias_residuales; máximo {max(frias.values())} celdas en {max(frias, key=frias.get)}, "
             f"{fc(100 * max(frias.values()) / (comun.ALTO * comun.ANCHO), 2)} % de la rejilla). Mueven poco las medianas "
             "espaciales, pero los valores por celda de esos años deben leerse con cautela." if frias else
             "No quedan celdas más de 10 °C por debajo del compuesto 2022-2025 en las rejillas anuales."),
        ],
        "solape_landsat_7_8": sol,
        "control_solo_landsat_7": rc,
        "salto_entre_sensores": salto,
        "sensibilidad_geos_it": geos,
        "tendencias": tend,
        "anios": anios,
        "anios_confiables": [r["anio"] for r in conf],
        "anios_no_confiables": no_conf,
        "fecha_proceso": datetime.now().date().isoformat(),
    }
    ruta = os.path.join(comun.DATOS, "series", "landsat.json")
    comun.guardar_json(ruta, salida)
    log(f"(b) serie escrita en {ruta}: {len(conf)} años confiables de {len(anios)}")
    for fam, t in lect.items():
        for tramo, txt in t.items():
            log(f"    {fam} [{tramo}]: {txt}")
    return salida


def completar_construido_2000(anios, M):
    """Añade a la serie principal las métricas de la zona construida ya en 2000 desde las rejillas anuales guardadas."""
    if M.get("construido_2000") is None:
        return
    for r in anios:
        rl = os.path.join(comun.REJILLA_NPY, f"lst_{r['anio']}.npy")
        rn = os.path.join(comun.REJILLA_NPY, f"ndvi_{r['anio']}.npy")
        if r.get("n_escenas") and os.path.exists(rl) and os.path.exists(rn):
            m = metricas(np.load(rl), np.load(rn), M)
            for k in ("lst_mediana_construido_2000", "isla_calor_construido_2000", "ndvi_mediana_construido_2000"):
                r[k] = m[k]


# ------------------------------------------------------------------ principal

def main():
    global HILOS
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--solo", choices=["lst", "serie"], default=None)
    ap.add_argument("--desde", type=int, default=2000)
    ap.add_argument("--hasta", type=int, default=2025)
    ap.add_argument("--hilos", type=int, default=HILOS)
    a = ap.parse_args()
    HILOS = a.hilos
    t0 = time.time()
    items = buscar_items()
    log(f"Catálogo: {len(items)} ítems; por plataforma {dict(Counter(i['platform'] for i in items))}")
    if a.solo in (None, "lst"):
        capa_lst(items)
    if a.solo in (None, "serie"):
        M = mascaras()
        anios = serie(items, M, a.desde, a.hasta)
        # zona construida ya en 2000 (necesita ndvi_2000..2002.npy de la serie); la usan el solape y el control
        M["construido_2000"] = mascara_construido_2000(M)
        if M["construido_2000"] is not None:
            M["descripcion"]["construido_2000_celdas"] = int(M["construido_2000"].sum())
            log(f"(b) zona construida en 2000: {int(M['construido_2000'].sum())} celdas de la cabecera")
        completar_construido_2000(anios, M)
        sol = solape_l7_l8(items, M) if a.desde <= SOLAPE[0] and a.hasta >= SOLAPE[1] else None
        control = (serie(items, M, CONTROL_L7[0], CONTROL_L7[1], ("landsat-7",), guardar=False, etiqueta="(control L7)")
                   if a.desde <= CONTROL_L7[0] and a.hasta >= CONTROL_L7[1] else None)
        escribir_serie(anios, sol, M, control)
    resumen()
    log(f"Fin en {(time.time() - t0) / 60:.1f} min")


def resumen():
    """Imprime un resumen de lo que haya en disco (capa lst y serie)."""
    print("\n================ RESUMEN landsat ================")
    ruta = os.path.join(comun.CAPAS, "lst.json")
    if os.path.exists(ruta):
        m = json.load(open(ruta, encoding="utf-8"))
        e = m["estadisticas"]
        print(f"Capa lst: {m['escenas_usadas']} escenas {m['escenas_por_plataforma']}, hora local media {m['hora_local_media_paso']}")
        print(f"  cabecera p10/p50/p90 = {e['cabecera_urbana']['p10']:.1f} / {e['cabecera_urbana']['p50']:.1f} / "
              f"{e['cabecera_urbana']['p90']:.1f} °C ; núcleo construido {m.get('lst_mediana_nucleo_construido_c')} °C ; "
              f"periurbano verde {m.get('lst_mediana_periurbano_verde_c')} °C ; rural {m['lst_mediana_rural_c']} °C ; "
              f"extensión {e['extension']['min']:.1f}–{e['extension']['max']:.1f} °C ; cobertura {m['cobertura_pct']} %")
        print(f"  observaciones por celda: {m['observaciones_por_celda']}")
        for k, v in m.get("sensibilidad_nubes", {}).items():
            print(f"  sensibilidad {k:36s} {v}")
    ruta = os.path.join(comun.DATOS, "series", "landsat.json")
    if os.path.exists(ruta):
        d = json.load(open(ruta, encoding="utf-8"))
        print("Serie anual (año, n, trimestres, sensores, LST urb, núcleo, rural, isla, isla núcleo, NDVI urb med/media/núcleo, conf):")
        for r in d["anios"]:
            print(f"  {r['anio']} {r['n_escenas']} {r.get('trimestres')} {'+'.join(r['sensores']):24s} {r['lst_mediana_urbana']} "
                  f"{r.get('lst_mediana_nucleo')} {r['lst_mediana_rural']} {r['isla_calor']} {r.get('isla_calor_nucleo')} "
                  f"{r['ndvi_mediana_urbana']}/{r.get('ndvi_media_urbana')}/{r.get('ndvi_mediana_nucleo')} {r['confiable']}")
        if d.get("solape_landsat_7_8"):
            s = d["solape_landsat_7_8"]
            print(f"Solape {s['periodo']}: L7 {s['landsat_7']['usadas']} escenas ({s['landsat_7']['hora_local_media']}), "
                  f"L8 {s['landsat_8']['usadas']} ({s['landsat_8']['hora_local_media']})")
            for c, v in s["efecto_sensor_l8_menos_l7"].items():
                print(f"  efecto sensor {c}: {v} IC95 {s['efecto_sensor_ic95'].get(c)}")
        for fam, t in d.get("lectura_de_tendencias", {}).items():
            for tramo, txt in t.items():
                print(f"  {fam} [{tramo}]: {txt}")


if __name__ == "__main__":
    main()
