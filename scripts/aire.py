"""Producto «aire» de BioMap Cartago: serie modelada de calidad del aire y capa de exposición a tráfico.

PARTE A — Serie modelada de calidad del aire (CAMS global vía Open-Meteo)
  Fuente: Open-Meteo Air Quality API, https://air-quality-api.open-meteo.com/v1/air-quality
          (documentación: https://open-meteo.com/en/docs/air-quality-api), que sirve el pronóstico
          global de composición atmosférica de Copernicus (CAMS global atmospheric composition forecasts).
  Licencias: datos de la API de Open-Meteo bajo CC BY 4.0 (https://open-meteo.com/en/licence);
             CAMS global publicado con licencia CC-BY (Atmosphere Data Store,
             https://ads.atmosphere.copernicus.eu/datasets/cams-global-atmospheric-composition-forecasts).
             Atribución: «Contiene información modificada del Copernicus Atmosphere Monitoring Service
             [año]» y «Datos de Open-Meteo.com».
  Resolución: CAMS global ≈ 40 km (0,4° × 0,4°). Es contexto REGIONAL, no la calle ni el barrio.
             Open-Meteo lo declara «3-Hourly»: en el crudo, los gases (NO₂, O₃, CO) muestran nodos cada 3 h
             (valores horarios interpolados); PM2,5 y PM10 no muestran esa estructura.
  Serie NO homogénea: CAMS cambió de ciclo de modelo dentro del periodo (tabla «Evolution of the CAMS
  global forecasting system», Copernicus Knowledge Base):
      47r3 (desde 2021-10-12) → 48r1 el 2023-06-27 → 49r1 el 2024-11-12 (corrida 12 UTC) → 50r1 el
      2026-05-12 (corrida 12 UTC).
    En 49r1 se cambió la distribución de tamaños usada para el diagnóstico de PM: «significantly higher PM1
    and PM2.5 and has a small impact on PM10» (Rémy et al., 2024, GMD 17:7539–7567, secc. 2.3.4,
    doi:10.5194/gmd-17-7539-2024). En los datos, el cociente horario PM10/PM2,5 pasa de ≈ 1,43 a ≈ 1,05 en
    la hora 07 local (12 UTC) del 2024-11-12. Por eso todos los resúmenes se dan también por ciclo de modelo
    y las diferencias entre años NO se presentan como tendencias.
  Pasos:
    1. Descubre el rango que acepta la API (mensaje de error con start_date fuera de rango) y busca por
       bisección el primer día con datos no nulos (CAMS global en Open-Meteo empieza en agosto de 2022).
    2. Descarga por años (caché en fuentes/aire/), desde ese día hasta AYER (hora de Bogotá), variables
       horarias nitrogen_dioxide, pm2_5, pm10, ozone, carbon_monoxide (µg/m³), domains=cams_global.
    3. Depuración: los valores negativos (artefacto de la interpolación) se recortan a 0 y se cuentan.
       Control de calidad: estructura de 3 h por variable, saltos en las horas de empalme de corridas
       (00 y 12 UTC) y cociente PM10/PM2,5.
    4. Medias diarias (día local, ≥ 18 h válidas), máximo diario de los valores horarios de NO₂ y CO
       (interpolados: subestiman el pico horario real), máximo diario de la media móvil de 8 h de O₃ y CO;
       medias mensuales (≥ 75 % de los días) y anuales.
    5. Etiqueta cada día con el ciclo de modelo; el día de cada cambio se excluye de los resúmenes por
       ciclo. Para cada cambio: cociente PM10/PM2,5 antes/después, búsqueda del salto horario del cociente
       (mediana de 24 h antes frente a 24 h después) y cambio de la media de 30 días antes/después de cada
       contaminante, comparado con la distribución de ese mismo estadístico en fechas sin cambio de ciclo.
    6. Resultado principal: resúmenes por ciclo de modelo, con los meses del año que cubre cada ciclo y una versión
       con los meses equiponderados. También por año calendario (con la mezcla de ciclos declarada) y por periodo de
       fórmula de PM (antes / desde 49r1), este último solo como referencia y con advertencia: cada grupo junta dos
       ciclos con un salto entre ellos. Climatología mensual por ciclo; temporada alta de O₃ por año y por ciclo.
       Sensibilidad del cambio de fórmula de 49r1 con dos supuestos (cota con PM10 sin cambio; reparto de la media de
       30 días en la fecha del cambio) y hallazgos para decidir, todos por ciclo (campo «hallazgos»).
    7. Compara con las Directrices mundiales de la OMS sobre calidad del aire 2021 (Cuadro 0.1) y con la
       Resolución 2254 de 2017 del MADS (Tablas 1 y 2, Parágrafo 1 del Art. 2). Valores verificados en:
         - OMS 2021, Resumen ejecutivo en español, ISBN 978-92-4-003546-1:
           https://www.miteco.gob.es/content/dam/miteco/es/calidad-y-evaluacion-ambiental/temas/atmosfera-y-calidad-del-aire/guiaoms2021-spa_tcm30-530942.pdf
         - Res. 2254/2017: https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=82634
           y https://www.icbf.gov.co/cargues/avance/docs/resolucion_minambienteds_2254_2017.htm
         - Condiciones de referencia (25 °C, 760 mm Hg): Decreto 1076 de 2015,
           https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=78153
    8. Escribe datos/series/aire.json. `--sin-red` rehace todo desde la caché de fuentes/aire/ sin consultar la API
       (la serie termina en el último día descargado).

PARTE B — Capa «trafico»: índice relativo de exposición a tráfico vehicular (0–100)
  Fuente: fuentes/osm-vias.json (OpenStreetMap, © colaboradores de OpenStreetMap, ODbL 1.0,
          https://www.openstreetmap.org/copyright). Overpass está bloqueado desde la terminal de este
          proyecto: el archivo se descargó aparte. La consulta original no se conservó; esta es la consulta
          equivalente (la función verificar_osm comprueba que todas las vías tienen highway=* y tocan la caja):
              [out:json][timeout:180];
              way["highway"](4.688,-75.985,4.795,-75.855);
              out geom;
          (POST a https://overpass-api.de/api/interpreter; `--descargar-osm` la ejecuta y guarda el resultado
          en fuentes/aire/osm-vias-descarga.json sin tocar fuentes/osm-vias.json, que usan otros scripts).
  Pasos:
    1. Peso por clase de vía (highway=*): motorway/trunk 1,0; primary 0,8; secondary 0,6; tertiary 0,4;
       unclassified 0,2; residential/living_street 0,1; service 0,05; *_link con el peso de su clase;
       peatonal, ciclovía, sendero, escaleras, en construcción 0. Supuestos propios: track (vía agrícola o
       de finca) 0,05 como service; vías con access=no o motor_vehicle=no: 0.
    2. Reproyecta a UTM 18N (EPSG:32618) y muestrea cada segmento cada ≤ 1 m.
    3. Regla de calzadas dobles (supuesto explícito): una vía dividida cartografiada como dos vías
       oneway (motorway/trunk/primary/secondary/tertiary, sin *_link ni glorietas) se cuenta UNA vez:
       las muestras que tienen, a ≤ 40 m, una muestra de otra vía oneway de la misma clase en sentido
       contrario (|u₁ + u₂| ≤ 0,5, es decir, ≥ ~151° entre sentidos de circulación) pesan × 0,5.
       Las calles de un solo sentido (sin calzada opuesta a ≤ 40 m) pesan completo.
    4. Rasteriza la LONGITUD de vía ponderada en una rejilla de 10 m con 400 m de margen.
    5. Núcleo gaussiano isotrópico σ = 50 m (normalizado, suma 1) → densidad vial ponderada suavizada
       (km de vía ponderada por km²). Fundamento: Karner, Eisinger y Niemeier (2010), Environ. Sci.
       Technol. 44(14):5334–5344, doi:10.1021/es100008x: casi todos los contaminantes del tráfico decaen
       al fondo entre 115 y 570 m del borde de la vía, y los de decaimiento más rápido (CO, número de
       partículas ultrafinas) bajan al menos 50 % hacia los 150 m. Con σ = 50 m el perfil transversal a
       una vía cae a la mitad a ≈ 59 m y a ≈ 1 % a 150 m: el índice representa la proximidad inmediata
       (zona de gradiente fuerte) y no la cola lenta del NO₂ hasta ~500 m (ver limitaciones).
    6. Promedia a la rejilla común (EPSG:4326, 0,00025°) y normaliza: percentil 99 dentro de la cabecera
       urbana = 100; se recorta a [0, 100].
    7. guardar_capa('trafico', valores, escala=0.01, desplazamiento=0) y, en trafico.json, estadísticas
       por zona (comun.mascara_zonas vigente) con tres denominadores: área del polígono, población (capa
       'poblacion', media ponderada: la que ordena) y celdas construidas (capa 'construido' ≥ 50 %);
       verificaciones (puntos de control, río, zona rural, medianas por clase, perfil perpendicular, índice por
       distancia a vías principales, norte/sur, saturación y enlaces *_link, PNG = .npy) y sensibilidad a σ, a
       la regla de calzadas dobles y al peso de los enlaces (0,5 × clase; no se aplica a la capa).
       Dependencia: las estadísticas por zona leen poblacion.npy y construido.npy (otros productos): si se
       regeneran, reejecutar `--solo-trafico` (la capa no cambia, solo trafico.json).

PARTE C (opcional, --evaluar-s5p | --recalcular-s5p) — Viabilidad de NO₂ troposférico de Sentinel-5P en Planetary Computer
  Consulta la colección 'sentinel-5p-l2-netcdf' (producto L2__NO2___), mide tamaños de archivo por órbita,
  latencia y ancho de banda con GET por rango, y hace una extracción ACOTADA (300 s) de una órbita OFFL por
  /vsicurl/ (driver HDF5 de GDAL): columna central de PRODUCT/latitude para hallar las filas de Cartago,
  latitude/longitude en esas filas, y nitrogendioxide_tropospheric_column y qa_value solo en la ventana de
  ±0,05°. Cuenta peticiones y bytes en el registro de depuración de GDAL.
  Órbitas por año: se cuentan en el año calendario anterior completo (metadatos STAC; caché s5p_orbitas.json), no
  en la ventana reciente, que la latencia de OFFL recorta; el costo de un año normal = tasa diaria mediana × 365.
  Cada medición de red se añade al registro acumulativo fuentes/aire/s5p_red.jsonl y el peor caso sale de ahí.
  `--recalcular-s5p` reutiliza la evaluación guardada y solo añade una medición ligera de red (`--sin-red`: ninguna).
  Resultado en fuentes/aire/s5p_evaluacion.json (+ s5p_vsicurl.log, una línea JSON por paso).

Uso:
  .venv/bin/python scripts/aire.py              # partes A y B
  .venv/bin/python scripts/aire.py --solo-serie | --solo-trafico | --evaluar-s5p | --recalcular-s5p | --descargar-osm
  .venv/bin/python scripts/aire.py --sin-red    # serie desde la caché (sin API) + capa de tráfico
"""
from __future__ import annotations

import argparse
import calendar
import json
import math
import os
import re
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comun  # noqa: E402

DIR = os.path.join(comun.FUENTES, "aire")
os.makedirs(DIR, exist_ok=True)
SERIES = os.path.join(comun.DATOS, "series")
os.makedirs(SERIES, exist_ok=True)

# ============================================================================ PARTE A: serie CAMS

API = "https://air-quality-api.open-meteo.com/v1/air-quality"
LAT, LON = 4.7464, -75.9117
VARIABLES = ["nitrogen_dioxide", "pm2_5", "pm10", "ozone", "carbon_monoxide"]
CLAVE = {"nitrogen_dioxide": "no2", "pm2_5": "pm2_5", "pm10": "pm10", "ozone": "o3", "carbon_monoxide": "co"}
NOMBRE = {"no2": "Dióxido de nitrógeno (NO₂)", "pm2_5": "Material particulado PM2,5", "pm10": "Material particulado PM10",
          "o3": "Ozono (O₃)", "co": "Monóxido de carbono (CO)"}
CONTAM = ("no2", "pm2_5", "pm10", "o3", "co")
CORTO = {"no2": "NO₂", "pm2_5": "PM2,5", "pm10": "PM10", "o3": "O₃", "co": "CO"}
TZ = "America/Bogota"

# Directrices OMS 2021 (Cuadro 0.1 del resumen ejecutivo; µg/m³ salvo CO, que la OMS da en mg/m³ y aquí se pasa a µg/m³).
# Los niveles de corto plazo (24 h y 8 h) se expresan como percentil 99 (3–4 días de superación por año).
OMS = {
    "pm2_5": {"anual": 5, "24h": 15, "metas_intermedias_anual": [35, 25, 15, 10], "metas_intermedias_24h": [75, 50, 37.5, 25]},
    "pm10": {"anual": 15, "24h": 45, "metas_intermedias_anual": [70, 50, 30, 20], "metas_intermedias_24h": [150, 100, 75, 50]},
    "no2": {"anual": 10, "24h": 25, "1h_vigente_2005": 200, "metas_intermedias_anual": [40, 30, 20], "metas_intermedias_24h": [120, 50]},
    "o3": {"temporada_alta": 60, "8h": 100, "metas_intermedias_8h": [160, 120], "metas_intermedias_temporada_alta": [100, 70]},
    "co": {"24h": 4000, "8h_vigente": 10000, "1h_vigente": 35000, "metas_intermedias_24h": [7000]},
}
# Resolución 2254 de 2017 (MADS), Tabla 1 (desde 1-ene-2018; PM 24 h desde 1-jul-2018 por Parágrafo 1) y Tabla 2 (desde 1-ene-2030).
RES2254 = {
    "pm10": {"anual": 50, "24h": 75, "anual_2030": 30},
    "pm2_5": {"anual": 25, "24h": 37, "anual_2030": 15},
    "no2": {"anual": 60, "1h": 200, "anual_2030": 40},
    "o3": {"8h": 100},
    "co": {"8h": 5000, "1h": 35000},
}

# Ciclos del sistema global de CAMS (tabla «Evolution of the CAMS global forecasting system»).
URL_CKB = "https://confluence.ecmwf.int/display/CKB/CAMS%3A+Global+atmospheric+composition+forecast+data+documentation"
CICLOS_CAMS = [
    {"ciclo": "47r3", "inicio": "2021-10-12", "hora_utc": None, "fuentes": [URL_CKB],
     "cambios": "Ciclo vigente al empezar la serie. La tabla del CKB registra ajustes menores sin cambio de ciclo el 2022-12-15 y el 2023-02-01."},
    {"ciclo": "48r1", "inicio": "2023-06-27", "hora_utc": None,
     "fuentes": [URL_CKB, "https://doi.org/10.5194/acp-24-9475-2024"],
     "cambios": "Química estratosférica completa; polvo redistribuido hacia tamaños mayores con más carga global; dos especies nuevas de aerosol "
                "orgánico secundario (Eskes et al., 2024, Atmos. Chem. Phys. 24:9475–9514)."},
    {"ciclo": "49r1", "inicio": "2024-11-12", "hora_utc": 12,
     "fuentes": ["https://forum.ecmwf.int/t/cams-model-cy49r1-successfully-upgraded-on-12-november-2024/7622",
                 "https://doi.org/10.5194/gmd-17-7539-2024"],
     "cambios": "EQSAM4Clim (partición nitrato/amonio) y otros cambios de aerosol; la distribución de tamaños usada para los diagnósticos de PM "
                "se alineó con la de la óptica de aerosoles: «significantly higher PM1 and PM2.5 and has a small impact on PM10» "
                "(Rémy et al., 2024, Geosci. Model Dev. 17:7539–7567, secc. 2.3.4)."},
    {"ciclo": "50r1", "inicio": "2026-05-12", "hora_utc": 12,
     "fuentes": ["https://forum.ecmwf.int/t/copernicus-atmosphere-monitoring-service-cams-implementation-of-cycle-50r1/14851",
                 "https://confluence.ecmwf.int/spaces/CKB/pages/621050847/Implementation+of+IFS+cycle+50R1+for+CAMS"],
     "cambios": "Cambios en aerosoles (equilibrio nitrato/amonio, crecimiento higroscópico de OM/SOA/nitrato, sedimentación) y en gases reactivos; "
                "emisiones antropogénicas CAMS-GLOB-ANT-M1 con ciclo semanal, BVOC en línea y GFAS 1.4.2."},
]
UMBRAL_SALTO_COCIENTE = 0.15   # diferencia de medianas de 24 h del cociente PM10/PM2,5 para declarar salto


def _get(params, intentos=6, timeout=120):
    import requests
    ultimo = None
    for i in range(intentos):
        try:
            r = requests.get(API, params=params, timeout=timeout)
            if r.status_code == 400:
                return r.json()
            r.raise_for_status()
            return r.json()
        except Exception as e:  # red lenta o intermitente: reintenta con espera creciente
            ultimo = e
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"Open-Meteo no respondió tras {intentos} intentos: {ultimo}")


def _params(inicio, fin, variables=VARIABLES):
    return {"latitude": LAT, "longitude": LON, "hourly": ",".join(variables), "timezone": TZ,
            "start_date": inicio.isoformat(), "end_date": fin.isoformat(), "domains": "cams_global"}


def _hay_datos(dia):
    d = _get(_params(dia, dia))
    if d.get("error"):
        raise RuntimeError(d.get("reason"))
    return any(v is not None for k in VARIABLES for v in d["hourly"][k])


def descubrir_inicio(ayer):
    """Rango aceptado por la API y primer día con datos (bisección, con caché verificada)."""
    d = _get(_params(date(1900, 1, 1), date(1900, 1, 1)))
    m = re.search(r"from (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})", d.get("reason", ""))
    if not m:
        raise RuntimeError(f"No se pudo leer el rango permitido: {d}")
    minimo = date.fromisoformat(m.group(1))
    rango = {"mensaje_api": d.get("reason"), "minimo_aceptado": m.group(1), "maximo_aceptado": m.group(2)}
    cache = os.path.join(DIR, "inicio.json")
    if os.path.exists(cache):
        c = json.load(open(cache))
        dia = date.fromisoformat(c["primer_dia_con_datos"])
        if _hay_datos(dia) and not _hay_datos(dia - timedelta(days=1)):
            c.update(rango)
            return dia, c
    lo, hi = minimo, ayer          # invariante: lo sin datos (o mínimo), hi con datos
    if _hay_datos(lo):
        dia = lo
    else:
        if not _hay_datos(hi):
            raise RuntimeError("No hay datos ni siquiera ayer")
        while (hi - lo).days > 1:
            mid = lo + timedelta(days=(hi - lo).days // 2)
            if _hay_datos(mid):
                hi = mid
            else:
                lo = mid
        dia = hi
    c = {"primer_dia_con_datos": dia.isoformat(), "metodo": "bisección sobre días (petición de 1 día)", **rango,
         "fecha_consulta": date.today().isoformat()}
    comun.guardar_json(cache, c)
    return dia, c


def descargar(inicio, ayer):
    """Descarga por años con caché. Los años completos ya descargados no se vuelven a pedir."""
    trozos = []
    a = inicio
    while a <= ayer:
        fin = min(date(a.year, 12, 31), ayer)
        trozos.append((a, fin))
        a = fin + timedelta(days=1)

    def uno(t):
        ini, fin = t
        ruta = os.path.join(DIR, f"cams_global_{ini.isoformat()}_{fin.isoformat()}.json")
        if os.path.exists(ruta):
            return ruta, "caché"
        d = _get(_params(ini, fin), timeout=300)
        if d.get("error"):
            raise RuntimeError(d.get("reason"))
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(d, f)
        # elimina descargas viejas del mismo año que terminaban antes (año en curso)
        for x in os.listdir(DIR):
            if x.startswith(f"cams_global_{ini.isoformat()}_") and x != os.path.basename(ruta):
                os.remove(os.path.join(DIR, x))
        return ruta, "descargado"

    with ThreadPoolExecutor(max_workers=4) as ex:
        res = list(ex.map(uno, trozos))
    tiempos, datos, meta = [], {CLAVE[v]: [] for v in VARIABLES}, None
    for ruta, estado in res:
        d = json.load(open(ruta))
        meta = meta or {k: d[k] for k in ("latitude", "longitude", "elevation", "timezone", "utc_offset_seconds", "hourly_units")}
        tiempos += d["hourly"]["time"]
        for v in VARIABLES:
            datos[CLAVE[v]] += [np.nan if x is None else float(x) for x in d["hourly"][v]]
        print(f"  {os.path.basename(ruta)}: {estado}")
    t = np.array([np.datetime64(x) for x in tiempos]).astype("datetime64[h]")
    orden = np.argsort(t)
    t = t[orden]
    datos = {k: np.array(v)[orden] for k, v in datos.items()}
    return t, datos, meta


def _media_movil(x, n=8, minimo=6):
    """Media móvil de n horas que termina en cada hora (requiere ≥ minimo horas válidas)."""
    v = np.where(np.isfinite(x), x, 0.0)
    c = np.isfinite(x).astype(float)
    sv = np.convolve(v, np.ones(n), "full")[: len(x)]
    sc = np.convolve(c, np.ones(n), "full")[: len(x)]
    out = np.where(sc >= minimo, sv / np.maximum(sc, 1), np.nan)
    out[: n - 1] = np.nan
    return out


def _r(x, nd=1):
    if x is None:
        return None
    x = float(x)
    return None if not math.isfinite(x) else round(x, nd)


def _pct(x, qs=(1, 10, 50, 90, 99), nd=3):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return None
    return {f"p{q}": _r(np.percentile(x, q), nd) for q in qs} | {"n": int(x.size)}


def _factor_referencia(h_m=919.0, t_k=298.15):
    p = 101325.0 * (1 - 2.25577e-5 * h_m) ** 5.25588  # atmósfera estándar
    return (101325.0 / p) * (t_k / 298.15)


FACTOR_REF = _factor_referencia()


def estructura_temporal(t, h, utc_offset_s):
    """Evidencia de la resolución temporal nativa y de los empalmes de corridas, por variable.

    - Segunda diferencia horaria |x[t+1] − 2x[t] + x[t−1]|: si los valores horarios se interpolan entre nodos cada 3 h,
      es mayor en las horas nodo (UTC múltiplo de 3) que en las intermedias (casi lineales).
    - |Δ| horario medio al entrar en las 00 y 12 UTC (empalme de corridas de pronóstico cada 12 h) frente a la mediana de
      las demás horas.
    """
    hl = (t.astype("datetime64[h]").astype(np.int64)) % 24
    hu = (hl - utc_offset_s // 3600) % 24
    hora_local_de_utc = {u: int((u + utc_offset_s // 3600) % 24) for u in (0, 12)}
    res = {}
    for k in CONTAM:
        x = h[k]
        d2 = np.abs(x[2:] - 2 * x[1:-1] + x[:-2])
        hh = hu[1:-1]
        a = float(np.nanmedian(d2[hh % 3 == 0]))
        b = float(np.nanmedian(d2[hh % 3 != 0]))
        por_clase = [_r(np.nanmedian(d2[hh % 3 == j]), 2) for j in range(3)]
        d1 = np.abs(np.diff(x))
        h1 = hu[1:]
        por_hora = {j: float(np.nanmean(d1[h1 == j])) for j in range(24)}
        resto = float(np.median([v for j, v in por_hora.items() if j not in (0, 12)]))
        res[k] = {
            "mediana_abs_2a_diferencia_horas_utc_multiplo_3": _r(a, 2),
            "mediana_abs_2a_diferencia_resto_de_horas": _r(b, 2),
            "mediana_abs_2a_diferencia_por_hora_utc_mod_3": por_clase,
            "cociente": _r(a / b if b > 0 else np.nan, 2),
            "nodos_cada_3h": bool(b > 0 and a / b >= 1.5),
            "media_abs_dif_horaria_al_entrar_00utc": _r(por_hora[0], 2),
            "media_abs_dif_horaria_al_entrar_12utc": _r(por_hora[12], 2),
            "mediana_abs_dif_horaria_otras_horas": _r(resto, 2),
        }
    return res, hora_local_de_utc


def etiquetar_ciclos(fechas):
    """Ciclo de CAMS de cada día. El día de un cambio queda como 'cambio_<ciclo>' (mezcla de dos ciclos)."""
    inicios = [np.datetime64(c["inicio"]) for c in CICLOS_CAMS]
    et = np.empty(len(fechas), dtype=object)
    for i, f in enumerate(fechas):
        j = max(k for k, s in enumerate(inicios) if s <= f)
        et[i] = f"cambio_{CICLOS_CAMS[j]['ciclo']}" if (j > 0 and f == inicios[j]) else CICLOS_CAMS[j]["ciclo"]
    return et


def ultimo_dia_en_cache():
    """Último día cubierto por las descargas de fuentes/aire/ (cams_global_<inicio>_<fin>.json)."""
    fines = [date.fromisoformat(m.group(1)) for x in os.listdir(DIR)
             for m in [re.match(r"cams_global_\d{4}-\d{2}-\d{2}_(\d{4}-\d{2}-\d{2})\.json$", x)] if m]
    return max(fines) if fines else None


def serie(sin_red=False):
    """sin_red=True: no consulta la API; usa fuentes/aire/inicio.json y las descargas en caché (la serie termina en el último día descargado)."""
    if sin_red:
        ayer = ultimo_dia_en_cache()
        if ayer is None:
            raise RuntimeError("--sin-red: no hay descargas en fuentes/aire/")
        info_inicio = json.load(open(os.path.join(DIR, "inicio.json")))
        inicio = date.fromisoformat(info_inicio["primer_dia_con_datos"])
        print(f"[A] Serie CAMS global (Open-Meteo) desde la caché, hasta {ayer} (sin consultar la API)")
        t, h, meta = descargar(inicio, ayer)
        return _serie(t, h, meta, inicio, ayer, info_inicio)
    hoy_bogota = datetime.now(__import__("zoneinfo").ZoneInfo(TZ)).date()
    ayer = hoy_bogota - timedelta(days=1)
    print(f"[A] Serie CAMS global (Open-Meteo) hasta {ayer}")
    inicio, info_inicio = descubrir_inicio(ayer)
    print(f"  primer día con datos: {inicio}  (la API acepta {info_inicio['minimo_aceptado']}–{info_inicio['maximo_aceptado']})")
    t, h, meta = descargar(inicio, ayer)
    return _serie(t, h, meta, inicio, ayer, info_inicio)


def _es(x, nd=1):
    """Número con coma decimal (texto en español)."""
    if x is None:
        return "s. d."
    return f"{x:.{nd}f}".replace(".", ",")


def _es_s(x, nd=1):
    """Número con signo explícito (+ / −) y coma decimal."""
    if x is None:
        return "s. d."
    return ("+" if x > 0 else "−" if x < 0 else "") + _es(abs(x), nd)


MESES_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def _mes_es(fecha):
    s = str(fecha)
    return f"{MESES_ES[int(s[5:7]) - 1]}-{s[:4]}"


def _serie(t, h, meta, inicio, ayer, info_inicio):
    paso = np.diff(t).astype("timedelta64[h]").astype(int)
    huecos_tiempo = int((paso != 1).sum())

    # ---- depuración y control de calidad horario
    negativos = {k: int(np.nansum(h[k] < 0)) for k in CONTAM}
    minimos_negativos = {k: _r(np.nanmin(h[k]), 2) for k in CONTAM if negativos[k]}
    ceros = {k: int(np.nansum(h[k] == 0)) for k in CONTAM}
    for k in CONTAM:
        h[k] = np.where(h[k] < 0, 0.0, h[k])          # NaN se conserva
    estructura, hora_local_empalme = estructura_temporal(t, h, meta["utc_offset_seconds"])

    dias = t.astype("datetime64[D]")
    ud = np.unique(dias)
    idx = np.searchsorted(ud, dias)
    fechas = ud.astype("datetime64[D]")
    ciclo_dia = etiquetar_ciclos(fechas)
    ciclo_hora = ciclo_dia[idx]

    m8 = {"o3": _media_movil(h["o3"]), "co": _media_movil(h["co"])}
    diario = {"fecha": [str(d) for d in ud]}
    for k in CONTAM:
        x = h[k]
        ok = np.isfinite(x)
        n = np.bincount(idx, weights=ok, minlength=len(ud))
        s = np.bincount(idx, weights=np.where(ok, x, 0), minlength=len(ud))
        diario[k] = np.where(n >= 18, s / np.maximum(n, 1), np.nan)

    def max_diario(x, minimo=18):
        ok = np.isfinite(x)
        n = np.bincount(idx, weights=ok, minlength=len(ud))
        mx = np.full(len(ud), -np.inf)
        np.maximum.at(mx, idx, np.where(ok, x, -np.inf))
        return np.where(n >= minimo, mx, np.nan)
    diario["no2_max1h"] = max_diario(h["no2"])
    diario["co_max1h"] = max_diario(h["co"])
    diario["o3_max8h"] = max_diario(m8["o3"])
    diario["co_max8h"] = max_diario(m8["co"])
    diario["pm10_pm25"] = diario["pm10"] / diario["pm2_5"]
    validos = int(np.isfinite(diario["pm2_5"]).sum())
    print(f"  {len(t)} horas, {len(ud)} días ({validos} con media diaria válida), huecos horarios: {huecos_tiempo}; "
          f"negativos recortados a 0: {negativos}")

    anios = fechas.astype("datetime64[Y]").astype(int) + 1970
    meses_num = fechas.astype("datetime64[M]")
    claves = ["no2", "pm2_5", "pm10", "o3", "co", "o3_max8h", "no2_max1h", "co_max8h"]

    # ---- mensual
    um = np.unique(meses_num)
    mensual = {"mes": [str(m) for m in um], "dias_validos": [], "completo": [], "ciclo_modelo": [], "ciclo_unico": []}
    for k in claves + ["pm10_pm25"]:
        mensual[k] = []
    for m in um:
        sel = meses_num == m
        y, mo = int(str(m)[:4]), int(str(m)[5:7])
        ndias = calendar.monthrange(y, mo)[1]
        nv = int(np.isfinite(diario["pm2_5"][sel]).sum())
        mensual["dias_validos"].append(nv)
        mensual["completo"].append(nv >= 0.75 * ndias)
        etiquetas = sorted(set(ciclo_dia[sel]), key=lambda e: [c["ciclo"] for c in CICLOS_CAMS].index(e.replace("cambio_", "")))
        mensual["ciclo_modelo"].append("/".join(dict.fromkeys(e.replace("cambio_", "") for e in etiquetas)))
        mensual["ciclo_unico"].append(etiquetas[0] if len(etiquetas) == 1 and not etiquetas[0].startswith("cambio_") else None)
        for k in claves + ["pm10_pm25"]:
            x = diario[k][sel]
            mensual[k].append(float(np.nanmean(x)) if np.isfinite(x).sum() >= 0.75 * ndias else None)

    # ---- bloques de resumen
    def bloque(sel, etiqueta, completo):
        nd = int(sel.sum())
        nv = int(np.isfinite(diario["pm2_5"][sel]).sum())
        b = {"periodo": etiqueta, "dias": nd, "dias_validos": nv, "completo_75pct": completo}
        cic = Counter(str(x) for x in ciclo_dia[sel])
        b["ciclos_modelo_dias"] = dict(cic)
        b["mezcla_ciclos_modelo"] = len({c.replace("cambio_", "") for c in cic}) > 1
        b["media"] = {k: _r(np.nanmean(diario[k][sel])) for k in CONTAM}
        b["p99_diario"] = {k: _r(np.nanpercentile(diario[k][sel], 99)) for k in ("no2", "pm2_5", "pm10", "co")}
        b["p99_diario"]["o3_max8h"] = _r(np.nanpercentile(diario["o3_max8h"][sel], 99))
        b["maximo_diario"] = {k: _r(np.nanmax(diario[k][sel])) for k in ("no2", "pm2_5", "pm10", "co")}
        b["maximo_diario"]["o3_max8h"] = _r(np.nanmax(diario["o3_max8h"][sel]))
        b["maximo_horario"] = {"no2": _r(np.nanmax(diario["no2_max1h"][sel])), "co": _r(np.nanmax(diario["co_max1h"][sel])),
                               "nota": "Máximo de valores horarios interpolados desde nodos de 3 h: subestima el pico horario real."}
        b["cociente_pm10_pm25_diario"] = {"mediana": _r(np.nanmedian(diario["pm10_pm25"][sel]), 3),
                                          "p10": _r(np.nanpercentile(diario["pm10_pm25"][sel], 10), 3),
                                          "p90": _r(np.nanpercentile(diario["pm10_pm25"][sel], 90), 3)}
        oms = {
            "pm2_5_24h_15": int(np.nansum(diario["pm2_5"][sel] > OMS["pm2_5"]["24h"])),
            "pm10_24h_45": int(np.nansum(diario["pm10"][sel] > OMS["pm10"]["24h"])),
            "no2_24h_25": int(np.nansum(diario["no2"][sel] > OMS["no2"]["24h"])),
            "o3_8h_100": int(np.nansum(diario["o3_max8h"][sel] > OMS["o3"]["8h"])),
            "co_24h_4000": int(np.nansum(diario["co"][sel] > OMS["co"]["24h"])),
        }
        b["dias_sobre_guia_diaria_oms_2021"] = oms
        b["dias_sobre_guia_oms_por_365_dias_validos"] = {k: _r(v * 365.0 / max(nv, 1)) for k, v in oms.items()}
        b["dias_sobre_res_2254"] = {
            "pm2_5_24h_37": int(np.nansum(diario["pm2_5"][sel] > RES2254["pm2_5"]["24h"])),
            "pm10_24h_75": int(np.nansum(diario["pm10"][sel] > RES2254["pm10"]["24h"])),
            "no2_1h_200": int(np.nansum(diario["no2_max1h"][sel] > RES2254["no2"]["1h"])),
            "o3_8h_100": int(np.nansum(diario["o3_max8h"][sel] > RES2254["o3"]["8h"])),
            "co_8h_5000": int(np.nansum(diario["co_max8h"][sel] > RES2254["co"]["8h"])),
            "co_1h_35000": int(np.nansum(diario["co_max1h"][sel] > RES2254["co"]["1h"])),
        }
        f = FACTOR_REF   # sensibilidad: la Res. 2254 está a condiciones de referencia (25 °C, 760 mm Hg)
        b["dias_sobre_res_2254_corregido_a_referencia"] = {
            "factor": round(f, 3),
            "pm2_5_24h_37": int(np.nansum(diario["pm2_5"][sel] * f > RES2254["pm2_5"]["24h"])),
            "pm10_24h_75": int(np.nansum(diario["pm10"][sel] * f > RES2254["pm10"]["24h"])),
            "no2_1h_200": int(np.nansum(diario["no2_max1h"][sel] * f > RES2254["no2"]["1h"])),
            "o3_8h_100": int(np.nansum(diario["o3_max8h"][sel] * f > RES2254["o3"]["8h"])),
        }
        return b

    anual = []
    for y in np.unique(anios):
        sel = anios == y
        ndias_anio = 366 if calendar.isleap(int(y)) else 365
        nv = int(np.isfinite(diario["pm2_5"][sel]).sum())
        anual.append(bloque(sel, str(int(y)), nv >= 0.75 * ndias_anio))
    ult = fechas > (np.datetime64(ayer) - np.timedelta64(365, "D"))
    ultimos365 = bloque(ult, f"{fechas[ult][0]} a {fechas[ult][-1]}", True)
    todo = bloque(np.ones(len(fechas), bool), f"{fechas[0]} a {fechas[-1]}", True)

    # ---- por ciclo de modelo (resultado principal): meses del año que cubre cada ciclo y resumen con los meses equiponderados
    mes_cal = fechas.astype("datetime64[M]").astype(int) % 12 + 1
    dias_mes_tipo = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    def equilibrado_por_mes(sel, min_dias=20):
        """Cada mes calendario con ≥ min_dias días válidos pesa igual (corrige que un ciclo cubra dos veces unos meses y ninguna otros)."""
        meses, med, e25, e10, o3e = [], {k: [] for k in CONTAM}, [], [], []
        for mo in range(1, 13):
            q = sel & (mes_cal == mo) & np.isfinite(diario["pm2_5"])
            if q.sum() < min_dias:
                continue
            meses.append(MESES_ES[mo - 1])
            for k in CONTAM:
                med[k].append(np.nanmean(diario[k][q]))
            e25.append(np.mean(diario["pm2_5"][q] > OMS["pm2_5"]["24h"]))
            o3e.append(np.nanmean(diario["o3_max8h"][q] > OMS["o3"]["8h"]))
        if not meses:
            return None
        return {"meses_calendario_con_20_dias_o_mas": len(meses), "meses": meses,
                "media": {k: _r(np.mean(v)) for k, v in med.items()},
                "dias_pm2_5_sobre_15_por_365": _r(365 * np.mean(e25)),
                "dias_o3_8h_sobre_100_por_365": _r(365 * np.mean(o3e)),
                "nota": "Media de las medias de cada mes calendario cubierto (cada mes pesa igual), para separar el efecto de qué meses cubre el ciclo."}

    por_ciclo = {}
    for c in CICLOS_CAMS:
        sel = ciclo_dia == c["ciclo"]
        if sel.sum() == 0:
            continue
        b = bloque(sel, f"{fechas[sel][0]} a {fechas[sel][-1]}", None)
        b["ciclo"] = c["ciclo"]
        b["nota"] = "Excluye el día del cambio de ciclo (mezcla de dos versiones)."
        dias_por_mes = {MESES_ES[mo - 1]: int((sel & (mes_cal == mo)).sum()) for mo in range(1, 13)}
        faltan = [mn for mn, n in dias_por_mes.items() if n < 20]
        dobles = [mn for (mn, n), dm in zip(dias_por_mes.items(), dias_mes_tipo) if n >= 1.5 * dm]
        b["meses_cubiertos_dias"] = dias_por_mes
        b["cobertura"] = (f"{_mes_es(fechas[sel][0])} a {_mes_es(fechas[sel][-1])}: {12 - len(faltan)} de 12 meses del año con ≥ 20 días"
                          + (f"; sin {', '.join(faltan)}" if faltan else "")
                          + (f"; cubiertos dos veces (dos años): {', '.join(dobles)}" if dobles else ""))
        b["equilibrado_por_mes"] = equilibrado_por_mes(sel)
        por_ciclo[c["ciclo"]] = b
    grupos_pm = {"antes_cy49r1": np.isin(ciclo_dia, ["47r3", "48r1"]), "desde_cy49r1": np.isin(ciclo_dia, ["49r1", "50r1"])}
    por_formula_pm = {}

    # ---- análisis de cada cambio de ciclo
    cambios, nula_resumen = analizar_cambios(t, h, ciclo_hora, diario, ciclo_dia, fechas)
    saltos = {c["ciclo"]: {k: v["cambio_pct"] for k, v in c["cambio_30_dias"].items() if v["indicio_de_salto"] and k != "pm10_pm25"}
              for c in cambios}
    for g, sel in grupos_pm.items():
        if sel.sum():
            b = bloque(sel, f"{fechas[sel][0]} a {fechas[sel][-1]}", None)
            ciclos_g = [c for c in ("47r3", "48r1", "49r1", "50r1") if (sel & (ciclo_dia == c)).any()]
            interno = [c for c in ciclos_g[1:] if saltos.get(c)]
            b["advertencia"] = ("Agrupa dos ciclos de modelo (" + " y ".join(ciclos_g) + ")"
                                + (": dentro del grupo hay un cambio de ciclo con indicio de salto ("
                                   + "; ".join(f"{c}: " + ", ".join(f"{CORTO[k]} {_es_s(v)} %" for k, v in saltos[c].items()) for c in interno) + ")"
                                   if interno else "")
                                + ". No usar para comparar «antes» y «desde» 49r1 ni como resultado: use por_ciclo_modelo.")
            por_formula_pm[g] = b

    # ---- sensibilidad del cambio de fórmula de 49r1: ¿subió o bajó el PM2,5 respecto de 48r1? (dos supuestos igual de compatibles)
    r_h = h["pm10"] / h["pm2_5"]
    sens_pm = {}
    c49 = next((c for c in cambios if c["ciclo"] == "49r1"), None)
    if c49 and "48r1" in por_ciclo and "49r1" in por_ciclo:
        r48 = float(np.nanmedian(r_h[ciclo_hora == "48r1"]))
        r49 = float(np.nanmedian(r_h[ciclo_hora == "49r1"]))
        s48, s49 = ciclo_dia == "48r1", ciclo_dia == "49r1"
        c30 = c49["cambio_30_dias"]
        f25 = 1 + c30["pm2_5"]["exceso_sobre_media_otros_anios_pct"] / 100

        def escenario(pm25_eq_todo, texto):
            """pm25_eq_todo: arreglo diario completo; solo se usan los días de 49r1."""
            pm25_eq = np.where(s49 & np.isfinite(diario["pm2_5"]), pm25_eq_todo, np.nan)
            eq_mes = []
            for mo in range(1, 13):
                q = (mes_cal == mo) & np.isfinite(pm25_eq)
                if q.sum() >= 20:
                    eq_mes.append(np.mean(pm25_eq[q]))
            m49, m48 = float(np.nanmean(pm25_eq)), por_ciclo["48r1"]["media"]["pm2_5"]
            e48 = por_ciclo["48r1"]["equilibrado_por_mes"]["media"]["pm2_5"]
            return {"supuesto": texto,
                    "pm2_5_49r1_equivalente_formula_anterior_media": _r(m49),
                    "pm2_5_49r1_equivalente_meses_equiponderados": _r(np.mean(eq_mes)) if eq_mes else None,
                    "efecto_de_la_formula_sobre_pm2_5_pct": _r(100 * (por_ciclo["49r1"]["media"]["pm2_5"] / m49 - 1)),
                    "dias_pm2_5_sobre_15_por_365": _r(365 * np.nansum(pm25_eq > 15) / max(np.isfinite(pm25_eq).sum(), 1)),
                    "pm2_5_48r1_media": m48, "pm2_5_48r1_meses_equiponderados": e48,
                    "cambio_48r1_a_49r1_pct": _r(100 * (m49 / m48 - 1)),
                    "cambio_48r1_a_49r1_meses_equiponderados_pct": _r(100 * (np.mean(eq_mes) / e48 - 1)) if eq_mes else None}

        cota = escenario(diario["pm10"] / r48,
                         f"Cota: todo el cambio del cociente PM10/PM2,5 ({_es(r48, 2)} en 48r1 → {_es(r49, 2)} en 49r1, medianas horarias) "
                         "se atribuye al PM2,5 y el PM10 no cambió («small impact on PM10», Rémy et al., 2024, a escala global). "
                         "PM2,5 equivalente = PM10 de 49r1 / cociente de 48r1.")
        alternativa = escenario(diario["pm2_5"] / f25,
                                f"Alternativa: el reparto que sugiere el cambio de la media de 30 días en la fecha del cambio, descontado el de las "
                                f"mismas fechas en otros años: PM2,5 {_es_s(c30['pm2_5']['exceso_sobre_media_otros_anios_pct'])} % y PM10 "
                                f"{_es_s(c30['pm10']['exceso_sobre_media_otros_anios_pct'])} %. Ambos cambios de 30 días están dentro de la "
                                f"variabilidad sin cambio de ciclo (percentiles {_es(c30['pm2_5']['percentil_en_distribucion_sin_cambio'], 0)} y "
                                f"{_es(c30['pm10']['percentil_en_distribucion_sin_cambio'], 0)}): el reparto es solo indicativo. "
                                "PM2,5 equivalente = PM2,5 de 49r1 / (1 + cambio del PM2,5).")
        signos = {np.sign(x["cambio_48r1_a_49r1_pct"]) for x in (cota, alternativa)} | \
                 {np.sign(x["cambio_48r1_a_49r1_meses_equiponderados_pct"]) for x in (cota, alternativa)}
        sens_pm = {
            "pregunta": "¿Subió o bajó el PM2,5 regional al pasar de 48r1 a 49r1, descontado el cambio de fórmula del diagnóstico de PM?",
            "cociente_pm10_pm25_mediano_horario": {"48r1": round(r48, 3), "49r1": round(r49, 3)},
            "escenario_cota_pm10_sin_cambio": cota,
            "escenario_alternativo_reparto_30_dias": alternativa,
            "conclusion": (("No se puede saber: el signo del cambio depende del supuesto. " if len(signos) > 1 else
                            "Ambos supuestos dan el mismo signo, pero la magnitud depende del supuesto. ")
                           + f"Con la cota, el PM2,5 de 49r1 equivaldría a {_es(cota['pm2_5_49r1_equivalente_formula_anterior_media'])} µg/m³ "
                           f"({_es_s(cota['cambio_48r1_a_49r1_pct'])} % frente a 48r1, {_es(por_ciclo['48r1']['media']['pm2_5'])}; con los meses equiponderados "
                           f"{_es_s(cota['cambio_48r1_a_49r1_meses_equiponderados_pct'])} %); con la "
                           f"alternativa, a {_es(alternativa['pm2_5_49r1_equivalente_formula_anterior_media'])} µg/m³ "
                           f"({_es_s(alternativa['cambio_48r1_a_49r1_pct'])} %; equiponderados {_es_s(alternativa['cambio_48r1_a_49r1_meses_equiponderados_pct'])} %). "
                           f"El efecto de la fórmula sobre el PM2,5 queda entre {_es_s(alternativa['efecto_de_la_formula_sobre_pm2_5_pct'], 0)} % y "
                           f"{_es_s(cota['efecto_de_la_formula_sobre_pm2_5_pct'], 0)} %. Además, 48r1 y 49r1 cubren años distintos (meteorología "
                           "distinta): aun con la fórmula corregida, la diferencia no sería una tendencia."),
            "nota": ("Solo sensibilidad, no son datos. 50r1 no se incluye: tiene su propio salto de PM y NO₂ (ver analisis) y la misma "
                     "distribución de tamaños que 49r1."),
        }

    # ---- climatología mensual (meses completos de un solo ciclo): por ciclo y por periodo de fórmula de PM
    def climatologia(ciclos):
        clim = {"mes": list(range(1, 13)), "n_meses": [], "meses_usados": []}
        for k in CONTAM:
            clim[k] = []
        mm = np.array([int(m[5:7]) for m in mensual["mes"]])
        ok = np.array([bool(c) and u in ciclos for c, u in zip(mensual["completo"], mensual["ciclo_unico"])])
        for mo in range(1, 13):
            sel = (mm == mo) & ok
            clim["n_meses"].append(int(sel.sum()))
            clim["meses_usados"].append([f"{mensual['mes'][i]} ({mensual['ciclo_unico'][i]})" for i in np.where(sel)[0]])
            for k in CONTAM:
                vals = np.array([mensual[k][i] for i in np.where(sel)[0]], dtype=float)
                clim[k].append(_r(np.nanmean(vals)) if vals.size else None)
        clim["meses_que_mezclan_ciclos"] = sum(len({u.split("(")[1] for u in us}) > 1 for us in clim["meses_usados"])
        return clim

    def ejemplo_mezcla(grupo, ciclos):
        """Mes del grupo cuya media mezcla ciclos con la mayor diferencia de PM2,5 entre ellos."""
        mejor = None
        for i, m in enumerate(mensual["mes"]):
            if not (mensual["completo"][i] and mensual["ciclo_unico"][i] in ciclos):
                continue
            for j, m2 in enumerate(mensual["mes"]):
                if (j > i and m2[5:7] == m[5:7] and mensual["completo"][j] and mensual["ciclo_unico"][j] in ciclos
                        and mensual["ciclo_unico"][j] != mensual["ciclo_unico"][i]):
                    dif = abs(mensual["pm2_5"][i] - mensual["pm2_5"][j])
                    if mejor is None or dif > mejor[0]:
                        mejor = (dif, i, j)
        if not mejor:
            return ""
        _, i, j = mejor
        mo = int(mensual["mes"][i][5:7])
        return (f" (p. ej., {MESES_ES[mo - 1]} = media de {mensual['mes'][i]} ({mensual['ciclo_unico'][i]}, PM2,5 {_es(mensual['pm2_5'][i])}) "
                f"y {mensual['mes'][j]} ({mensual['ciclo_unico'][j]}, {_es(mensual['pm2_5'][j])}) = "
                f"{_es(grupo['pm2_5'][mo - 1])} µg/m³)")
    clim_antes, clim_desde = climatologia({"47r3", "48r1"}), climatologia({"49r1", "50r1"})
    clim = {
        "nota": ("Promedio de las medias mensuales de meses completos (≥ 75 % de días) de un solo ciclo de modelo; con 1–2 años por mes es una "
                 "descripción, no una climatología robusta. Use por_ciclo (cada valor de un solo ciclo). Los grupos antes_cy49r1 y desde_cy49r1 "
                 f"mezclan ciclos: «antes» promedia 47r3 y 48r1 en {clim_antes['meses_que_mezclan_ciclos']} de 12 meses"
                 + ejemplo_mezcla(clim_antes, {"47r3", "48r1"})
                 + f", y «desde» promedia 49r1 y 50r1 en {clim_desde['meses_que_mezclan_ciclos']} meses"
                 + ejemplo_mezcla(clim_desde, {"49r1", "50r1"})
                 + ". En ambos grupos hay un cambio de ciclo con indicio de salto de PM (48r1 y 50r1): sus diferencias no son estacionalidad."),
        "por_ciclo": {c["ciclo"]: climatologia({c["ciclo"]}) for c in CICLOS_CAMS if (ciclo_dia == c["ciclo"]).any()},
        "antes_cy49r1": clim_antes,
        "desde_cy49r1": clim_desde,
    }

    # ---- temporada alta de O3 (OMS): media de 6 meses consecutivos del máximo diario de 8 h; máximo por año y por ciclo
    o3m = np.array([np.nan if v is None else v for v in mensual["o3_max8h"]], dtype=float)
    def temporada(permitido):
        mejor = None
        for i in range(len(o3m) - 5):
            if not all(permitido[i:i + 6]) or not np.isfinite(o3m[i:i + 6]).all():
                continue
            v = float(np.mean(o3m[i:i + 6]))
            if mejor is None or v > mejor["valor"]:
                mejor = {"valor": _r(v), "desde": mensual["mes"][i], "hasta": mensual["mes"][i + 5],
                         "ciclos": "/".join(dict.fromkeys("/".join(mensual["ciclo_modelo"][i:i + 6]).split("/")))}
        return mejor
    anio_mes = np.array([int(m[:4]) for m in mensual["mes"]])
    temporada_o3 = {
        "guia_oms": OMS["o3"]["temporada_alta"],
        "definicion": "Media de los máximos diarios de 8 h de O₃ en los 6 meses consecutivos con la media móvil de 6 meses más alta.",
        "por_anio": {str(int(y)): temporada([a == y for a in anio_mes]) for y in np.unique(anio_mes)},
        "por_ciclo": {c["ciclo"]: temporada([u == c["ciclo"] for u in mensual["ciclo_unico"]]) for c in CICLOS_CAMS},
        "maximo_registro": temporada([True] * len(o3m)),
        "nota": ("Por año: ventanas dentro del año calendario (pueden mezclar ciclos; ver 'ciclos'). Por ciclo: solo meses de un único ciclo. "
                 "El máximo del registro mezcla ciclos de modelo. null = no hay 6 meses consecutivos completos en ese periodo."),
    }

    def comparar(b):
        m = b["media"]
        out = {}
        for k in ("pm2_5", "pm10", "no2"):
            out[k] = {"media": m[k], "oms_2021": OMS[k]["anual"], "res2254_vigente": RES2254[k]["anual"], "res2254_2030": RES2254[k]["anual_2030"],
                      "veces_guia_oms": _r(m[k] / OMS[k]["anual"], 2)}
        out["ciclos_modelo_dias"] = b["ciclos_modelo_dias"]
        return out

    hallazgos = hallazgos_aire(por_ciclo, saltos, sens_pm, temporada_o3)

    salida = {
        "titulo": "Calidad del aire modelada (CAMS global) — Cartago",
        "descripcion": ("Concentraciones de contaminantes en superficie estimadas por el modelo global de Copernicus (CAMS) para la celda "
                        "que contiene a Cartago. Es un modelo de unos 40 km de resolución: describe el aire de la región, no el de una calle, "
                        "y no son mediciones de una estación. El modelo cambió de versión tres veces durante la serie (en 2023, 2024 y 2026; "
                        "el 12-nov-2024 cambió además la forma de calcular el PM2,5): los resultados se dan por versión del modelo y las "
                        "diferencias entre años no son tendencias."),
        "hallazgos": hallazgos,
        "fuente": {
            "nombre": "Copernicus Atmosphere Monitoring Service (CAMS) — pronóstico global de composición atmosférica, servido por Open-Meteo Air Quality API",
            "url": "https://open-meteo.com/en/docs/air-quality-api",
            "url_cams": "https://ads.atmosphere.copernicus.eu/datasets/cams-global-atmospheric-composition-forecasts",
            "licencia": "CC BY 4.0 (Open-Meteo: https://open-meteo.com/en/licence; CAMS: licencia CC-BY declarada en el Atmosphere Data Store)",
            "cita": f"Contiene información modificada del Copernicus Atmosphere Monitoring Service {date.today().year}. Datos de Open-Meteo.com (https://open-meteo.com/).",
            "consulta": {"url": API, **{k: v for k, v in _params(inicio, ayer).items()}},
        },
        "punto": {"lat_solicitada": LAT, "lon_solicitada": LON, "lat_devuelta_api": meta["latitude"], "lon_devuelta_api": meta["longitude"],
                  "elevacion_api_m": meta["elevation"], "zona_horaria": meta["timezone"],
                  "nota": ("La API devuelve el centro de la celda usada («might be a few kilometres away»): 4,70/−75,90, unos 5 km al SSE del punto "
                           "pedido. La elevación devuelta proviene de un modelo digital de elevación de 90 m (documentación general de Open-Meteo); "
                           "no es la orografía de la celda de ~40 km del modelo.")},
        "periodo": {"inicio": str(fechas[0]), "fin": str(fechas[-1]), "primer_dia_con_datos_api": info_inicio["primer_dia_con_datos"],
                    "rango_aceptado_api": [info_inicio["minimo_aceptado"], info_inicio["maximo_aceptado"]],
                    "nota": "Antes del primer día con datos la API acepta fechas pero devuelve valores nulos para el dominio CAMS global."},
        "resolucion_original_km": 40,
        "resolucion_nota": "CAMS global: ≈ 40 km, distribuido en rejilla de 0,4° × 0,4°; Open-Meteo lo describe como «0.4° (~45 km)».",
        "resolucion_temporal": {
            "declarada_open_meteo": "3-Hourly (tabla de fuentes de https://open-meteo.com/en/docs/air-quality-api)",
            "observada": {k: ("nodos cada 3 h: valores horarios interpolados" if v["nodos_cada_3h"] else "sin estructura de 3 h")
                          for k, v in estructura.items()},
            "consecuencia": ("no2_max1h, co_max1h y maximo_horario son máximos de valores interpolados y subestiman el pico horario real; la "
                             "comparación con el límite de 1 h de la Res. 2254 es solo orientativa."),
        },
        "uso_en_aplicacion": ("Un único valor regional para todo el municipio: no se debe repartir por zona ni por calle ni mezclar con la capa "
                              "'trafico' (índice adimensional). Mostrar siempre la advertencia del modelo de ~40 km y del cambio de versión del "
                              "2024-11-12."),
        "unidades": {k: "µg/m³" for k in claves} | {"pm10_pm25": "adimensional"},
        "contaminantes": NOMBRE,
        "cambios_de_version_modelo": {
            "resumen": ("CAMS global no es una serie homogénea: cambió de ciclo el 2023-06-27 (48r1), el 2024-11-12 (49r1) y el 2026-05-12 (50r1). "
                        + (f"El cambio de 49r1 es inequívoco en los datos (cociente PM10/PM2,5 {_es(c49['salto_cociente_pm10_pm25']['media_24h_antes'], 2)} → "
                           f"{_es(c49['salto_cociente_pm10_pm25']['media_24h_despues'], 2)} en una hora) y coincide con la documentación (a escala global, "
                           "PM2,5 «significativamente más alto», PM10 casi sin cambio); en Cartago no se puede separar cuánto subió el PM2,5 y cuánto "
                           "bajó el PM10 (ver sensibilidad_pm2_5_formula_anterior). " if c49 else "")
                        + "".join(f"El cambio a {c} muestra indicio de salto en " + ", ".join(f"{CORTO[k]} {_es_s(v)} %" for k, v in sv.items()) + " (media de 30 días). "
                                  for c, sv in saltos.items() if sv and c != "49r1")
                        + "Indicio de salto = el cambio de 30 días cae fuera del rango 2,5–97,5 % de las fechas sin cambio de ciclo y es más extremo "
                        "que en las mismas fechas de otros años; dentro de ese rango no se puede separar el efecto del modelo del de la meteorología. "
                        "Por eso los resultados se dan por ciclo y no se agrupan ciclos."),
            "ciclos": CICLOS_CAMS,
            "fuente_tabla": URL_CKB,
            "analisis": cambios,
            "distribucion_cambio_30d_sin_cambio_de_ciclo_pct": nula_resumen,
            "sensibilidad_pm2_5_formula_anterior": sens_pm,
        },
        "diario": {"fecha": diario["fecha"], **{k: [_r(v) for v in diario[k]] for k in claves},
                   "pm10_pm25": [_r(v, 3) for v in diario["pm10_pm25"]], "ciclo_modelo": [str(x) for x in ciclo_dia]},
        "diario_campos": {"no2/pm2_5/pm10/o3/co": "media de 24 h del día local (≥ 18 h válidas)",
                          "o3_max8h": "máximo diario de la media móvil de 8 h de O₃", "co_max8h": "máximo diario de la media móvil de 8 h de CO",
                          "no2_max1h": "máximo diario de los valores horarios de NO₂ (interpolados desde nodos de 3 h; subestima el pico real)",
                          "pm10_pm25": "cociente de las medias diarias PM10/PM2,5 (control de calidad: ≈ 1,43 hasta el 2024-11-11, ≈ 1,0 después)",
                          "ciclo_modelo": "ciclo de CAMS; 'cambio_<ciclo>' = día del cambio (mezcla de dos versiones)"},
        "mensual": {"mes": mensual["mes"], "dias_validos": mensual["dias_validos"], "completo": mensual["completo"],
                    "ciclo_modelo": mensual["ciclo_modelo"],
                    **{k: [_r(v) for v in mensual[k]] for k in claves}, "pm10_pm25": [_r(v, 3) for v in mensual["pm10_pm25"]]},
        "climatologia_mensual": clim,
        "anual": anual,
        "ultimos_365_dias": ultimos365,
        "periodo_completo": todo,
        "por_ciclo_modelo": por_ciclo,
        "por_formula_pm": por_formula_pm,
        "comparacion_anual": {
            "advertencia": ("Las diferencias entre años mezclan cambios del aire con cambios de versión del modelo. En particular, PM2,5 y PM10 "
                            "antes y después del 2024-11-12 no son comparables (cambió la fórmula del diagnóstico de PM), y PM10 posterior a esa "
                            "fecha no debe compararse con la guía OMS como si fuera la misma serie. Use por_ciclo_modelo (cada valor de una sola "
                            "versión del modelo); veces_guia_oms es orientativo y depende de la versión."),
            "por_ciclo_modelo": {c: comparar(b) | {"cobertura": b["cobertura"]} for c, b in por_ciclo.items()},
            "por_periodo": {b["periodo"]: comparar(b) for b in anual if b["completo_75pct"]} | {"ultimos_365_dias": comparar(ultimos365)},
            "por_formula_pm": {g: comparar(b) for g, b in por_formula_pm.items()},
            "por_formula_pm_advertencia": ("No comparar antes_cy49r1 con desde_cy49r1: cada grupo junta dos ciclos y contiene un cambio de ciclo con "
                                           "indicio de salto de PM (ver por_formula_pm.*.advertencia); la diferencia entre ambos no mide ni el efecto "
                                           "de la fórmula ni un cambio del aire."),
        },
        "o3_temporada_alta_oms": temporada_o3,
        "umbrales": {
            "oms_2021": {"valores": OMS, "unidad": "µg/m³ (CO convertido desde mg/m³)",
                         "nota": "Niveles de corto plazo (24 h, 8 h) definidos como percentil 99 (3–4 días de superación por año). Por eso se informan "
                                 "tanto los días por encima como el percentil 99 de las medias diarias.",
                         "fuente": "OMS (2021). Directrices mundiales de la OMS sobre la calidad del aire. Resumen ejecutivo, Cuadro 0.1 y 0.2. ISBN 978-92-4-003546-1.",
                         "url": "https://www.who.int/publications/i/item/9789240034228",
                         "url_texto_verificado": "https://www.miteco.gob.es/content/dam/miteco/es/calidad-y-evaluacion-ambiental/temas/atmosfera-y-calidad-del-aire/guiaoms2021-spa_tcm30-530942.pdf"},
            "res_2254_2017": {"valores": RES2254, "unidad": "µg/m³ a condiciones de referencia",
                              "nota": ("Tabla 1 (vigente desde 1-ene-2018; PM10 y PM2,5 de 24 h en 75 y 37 µg/m³ desde 1-jul-2018 por el Parágrafo 1 del Art. 2) "
                                       "y Tabla 2 (anuales desde 1-ene-2030). La norma se verifica por punto de monitoreo (Parágrafo 2): "
                                       "un modelo de 40 km no sirve para declarar cumplimiento o incumplimiento."),
                              "condiciones_referencia": "25 °C y 760 mm Hg (Decreto 1076 de 2015, definición de «condiciones de referencia»)",
                              "fuente": "Ministerio de Ambiente y Desarrollo Sostenible, Resolución 2254 del 1 de noviembre de 2017.",
                              "url": "https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=82634"},
        },
        "correccion_condiciones_referencia": {
            "factor": round(FACTOR_REF, 4),
            "metodo": ("760 mm Hg / presión de la atmósfera estándar a 919 m, con T = 25 °C (supuesto). 919 m es la elevación que devuelve la API, "
                       "tomada de un MDE de 90 m; no es la presión de superficie ni la orografía de la celda del modelo (~40 km), que no se conocen."),
            "uso": "Solo análisis de sensibilidad (dias_sobre_res_2254_corregido_a_referencia). Se asume que los µg/m³ de Open-Meteo están a condiciones locales.",
        },
        "control_calidad": {
            "horas": int(len(t)), "huecos_horarios": huecos_tiempo, "dias": int(len(ud)), "dias_validos_pm2_5": validos,
            "horas_nulas": {k: int((~np.isfinite(h[k])).sum()) for k in CONTAM},
            "valores_negativos_recortados_a_0": negativos, "minimo_negativo_original": minimos_negativos,
            "ceros_exactos": ceros,
            "estructura_temporal": estructura,
            "estructura_temporal_nota": (f"Horas de empalme de corridas (00 y 12 UTC) = {hora_local_empalme[0]} h y {hora_local_empalme[12]} h locales. "
                                         "Si el |Δ| horario medio al entrar en esas horas es varias veces el de las demás, los valores horarios "
                                         "tienen discontinuidades de empalme (no separables del ciclo diario de la capa límite); las medias "
                                         "diarias son más robustas que los valores horarios."),
            "cociente_pm10_pm25_horario_por_ciclo": {c["ciclo"]: _pct(r_h[ciclo_hora == c["ciclo"]]) for c in CICLOS_CAMS if (ciclo_hora == c["ciclo"]).any()},
        },
        "procesamiento": [
            "Descubrimiento del primer día con datos por bisección (peticiones de un día) y descarga horaria por años, desde ese día hasta ayer (hora de Bogotá).",
            "domains=cams_global (equivale a 'auto' fuera de Europa; se fija para que sea explícito).",
            "Valores negativos (artefacto de interpolación) recortados a 0 antes de agregar; se cuentan en control_calidad.",
            "Media diaria con ≥ 18 de 24 horas válidas; media móvil de 8 h (≥ 6 de 8 horas) para O₃ y CO; máximo diario de los valores horarios de NO₂ y CO.",
            "Media mensual con ≥ 75 % de los días del mes; media anual por año calendario (completo si ≥ 75 % de los días) y de los últimos 365 días.",
            "Cada día se etiqueta con su ciclo de CAMS; el resultado principal son los resúmenes por ciclo (sin el día del cambio), con los meses del año "
            "que cubre cada uno y una versión con los meses equiponderados. Los grupos por periodo de fórmula de PM (antes / desde 49r1) se conservan "
            "solo como referencia, con advertencia.",
            "Sensibilidad del cambio de fórmula de 49r1 con dos supuestos: cota (PM10 sin cambio) y reparto de la media de 30 días en la fecha del cambio.",
            "Detección del salto: cociente horario PM10/PM2,5 (mediana de 24 h antes frente a 24 h después, ±2 días alrededor de cada cambio) y "
            "cambio de la media de 30 días antes/después de cada contaminante frente a su distribución en fechas sin cambio de ciclo.",
            "Excedencias: días con media diaria (o máximo de 8 h / 1 h según el contaminante) estrictamente mayor que el umbral; también por 365 días válidos.",
        ],
        "limitaciones": [
            "Es un MODELO global de ≈ 40 km: representa el fondo regional del valle (Cartago, Pereira, Dosquebradas, norte del Valle), no la exposición junto a una vía ni diferencias entre barrios.",
            "La serie NO es homogénea: CAMS cambió de ciclo el 2023-06-27, el 2024-11-12 y el 2026-05-12. Las diferencias entre años no son tendencias.",
            "Desde el 2024-11-12 (49r1) el PM2,5 se calcula con otra distribución de tamaños («significantly higher PM2.5», Rémy et al., 2024, a escala "
            "global) y el cociente PM10/PM2,5 cae de ≈ 1,43 a ≈ 1,0. En Cartago no se puede separar cuánto subió el PM2,5 y cuánto bajó el PM10 "
            + (f"(efecto de la fórmula sobre el PM2,5 entre {_es_s(sens_pm['escenario_alternativo_reparto_30_dias']['efecto_de_la_formula_sobre_pm2_5_pct'], 0)} % "
               f"y {_es_s(sens_pm['escenario_cota_pm10_sin_cambio']['efecto_de_la_formula_sobre_pm2_5_pct'], 0)} % según el supuesto), así que no se sabe "
               "si el PM2,5 subió o bajó respecto de 48r1. " if sens_pm else "") +
            "Un PM2,5 casi igual al PM10 "
            "es poco verosímil en un valle con polvo resuspendido y quemas de caña: al menos una de las dos fracciones está sesgada, y sin mediciones locales "
            "no se sabe cuál. PM10 posterior a esa fecha no es comparable con la guía como si fuera la misma serie.",
            "No se ha validado con mediciones locales (estaciones del SVCA de la CVC o del SISAIRE); los sesgos del modelo en esta zona son desconocidos.",
            "Los gases (NO₂, O₃, CO) tienen nodos cada 3 h interpolados a 1 h: los máximos horarios subestiman los picos reales.",
            "Las emisiones de CAMS son inventarios globales que pueden no reflejar el tráfico, la quema de caña o la industria locales.",
            "Datos de 'pronóstico' archivado de CAMS global (no un reanálisis).",
            "La Res. 2254 se verifica en puntos de monitoreo y a condiciones de referencia: estas comparaciones son orientativas, no una declaratoria de cumplimiento.",
            "La serie empieza en agosto de 2022: 2022 y el año en curso son años incompletos.",
        ],
        "interpretacion": {
            "guia_oms": "Las guías OMS 2021 son niveles con base sanitaria (no obligatorios). Superar el nivel de 24 h más de 3–4 días por año (percentil 99) indica exposición por encima de la guía.",
            "res_2254": "Norma colombiana obligatoria para las autoridades ambientales, medida en estaciones; más permisiva que la OMS (p. ej., PM2,5 de 24 h: 37 frente a 15 µg/m³).",
            "comparacion_entre_periodos": ("Compare solo dentro de un mismo ciclo de modelo (por_ciclo_modelo). Los grupos por periodo de fórmula de PM "
                                           "(por_formula_pm) juntan dos ciclos con un salto entre ellos y no sirven para comparar. Los días de superación "
                                           "varían mucho entre ciclos: léalos como un rango, no como una cifra."),
            "dias_de_superacion": "Por ciclo, por 365 días válidos (dias_sobre_guia_oms_por_365_dias_validos) y con los meses equiponderados (equilibrado_por_mes).",
        },
        "fecha_proceso": date.today().isoformat(),
    }
    comun.guardar_json(os.path.join(SERIES, "aire.json"), salida)

    print("  Promedios (µg/m³), días sobre guía diaria OMS 2021 y ciclos de modelo:")
    for b in anual + [ultimos365] + list(por_ciclo.values()) + list(por_formula_pm.values()):
        m, e = b["media"], b["dias_sobre_guia_diaria_oms_2021"]
        print(f"   {b['periodo']:>25} ({b['dias_validos']:3d} d{' ' if b['completo_75pct'] else '*'}) "
              f"PM2.5 {m['pm2_5']:5.1f} PM10 {m['pm10']:5.1f} NO2 {m['no2']:5.1f} O3 {m['o3']:5.1f} CO {m['co']:6.0f} | "
              f"OMS>: PM2.5 {e['pm2_5_24h_15']} PM10 {e['pm10_24h_45']} NO2 {e['no2_24h_25']} O3 {e['o3_8h_100']} | "
              f"PM10/PM2.5 {b['cociente_pm10_pm25_diario']['mediana']} | ciclos {b['ciclos_modelo_dias']}")
    for c in cambios:
        s = c["salto_cociente_pm10_pm25"]
        print(f"   cambio {c['ciclo']} {c['fecha']}: salto cociente {s['diferencia']} en {s['hora_local']} (detectado: {s['detectado']}); "
              + ", ".join(f"{k} {v['cambio_pct']:+.1f}% (p{v['percentil_en_distribucion_sin_cambio']:.0f}; otros años {v['mismas_fechas_otros_anios_pct']}; "
                          f"indicio {v['indicio_de_salto']})" for k, v in c["cambio_30_dias"].items()))
    print(f"   sensibilidad PM2.5 fórmula anterior: {sens_pm.get('conclusion')}")
    print("   hallazgos:\n    - " + "\n    - ".join(hallazgos))
    print(f"   temporada alta O3: {json.dumps(temporada_o3['por_anio'], ensure_ascii=False)} | por ciclo {json.dumps(temporada_o3['por_ciclo'], ensure_ascii=False)}")
    print(f"   estructura 3 h: {json.dumps({k: (v['cociente'], v['media_abs_dif_horaria_al_entrar_00utc'], v['media_abs_dif_horaria_al_entrar_12utc'], v['mediana_abs_dif_horaria_otras_horas']) for k, v in estructura.items()})}")
    print(f"  → {os.path.join(SERIES, 'aire.json')}")
    return salida


def hallazgos_aire(por_ciclo, saltos, sens_pm, temporada_o3):
    """Hallazgos para decidir, todos por ciclo de modelo (nunca grupos de ciclos). Cada cifra sale de los bloques ya calculados."""
    cic = [c for c in ("47r3", "48r1", "49r1", "50r1") if c in por_ciclo]
    if not cic:
        return []
    b = por_ciclo

    def rango(vals, nd=1):
        v = [x for x in vals if x is not None]
        return f"{_es(min(v), nd)}–{_es(max(v), nd)}"

    def todos(cond):
        return "en los {} ciclos".format(len(cic)) if all(cond(c) for c in cic) else \
               ("en ningún ciclo" if not any(cond(c) for c in cic) else
                "en {} de {} ciclos ({})".format(sum(cond(c) for c in cic), len(cic), ", ".join(c for c in cic if cond(c))))

    def r10(x):
        return int(round(x / 10.0) * 10)

    out = []
    g25 = OMS["pm2_5"]["anual"]
    pm = {c: b[c]["media"]["pm2_5"] for c in cic}
    out.append(
        "Resultado principal, por versión (ciclo) del modelo CAMS: PM2,5 medio regional "
        + "; ".join(f"{c} {_es(pm[c])} µg/m³ ({b[c]['cobertura'].split(':')[0]}, {b[c]['dias_validos']} días)" for c in cic)
        + f". Por encima de la guía anual de la OMS ({g25} µg/m³) {todos(lambda c: pm[c] > g25)}: entre "
        + f"{_es(min(pm.values()) / g25)} y {_es(max(pm.values()) / g25)} veces la guía. Lo robusto es que el fondo regional modelado "
        "supera la guía en todas las versiones (sin validar con mediciones locales); el valor exacto depende de la versión del modelo y del año.")
    d = {c: b[c]["dias_sobre_guia_oms_por_365_dias_validos"]["pm2_5_24h_15"] for c in cic}
    deq = {c: (b[c]["equilibrado_por_mes"] or {}).get("dias_pm2_5_sobre_15_por_365") for c in cic}
    parcial = [c for c in cic if (b[c]["equilibrado_por_mes"] or {}).get("meses_calendario_con_20_dias_o_mas", 0) < 10]
    out.append(
        f"Días con PM2,5 diario > {OMS['pm2_5']['24h']} µg/m³ (nivel de 24 h de la OMS, que admite 3–4 días por año): entre ≈ {r10(min(d.values()))} y "
        f"≈ {r10(max(d.values()))} por año según la versión del modelo (" + "; ".join(f"{c} {_es(d[c])}" for c in cic)
        + " por 365 días válidos). Con los meses del año equiponderados la horquilla se mantiene (" + rango(deq.values())
        + "): no se explica por los meses que cubre cada ciclo"
        + (f" ({', '.join(parcial)} solo cubre {', '.join(str(b[c]['equilibrado_por_mes']['meses_calendario_con_20_dias_o_mas']) + ' meses' for c in parcial)})" if parcial else "")
        + f". La cifra no es robusta; lo robusto es que se superan los 3–4 días por año {todos(lambda c: d[c] > 4)}.")
    o3 = {c: b[c]["dias_sobre_guia_oms_por_365_dias_validos"]["o3_8h_100"] for c in cic}
    temp = {c: v["valor"] for c, v in (temporada_o3.get("por_ciclo") or {}).items() if v}
    out.append(
        f"Ozono: días con máximo de 8 h > {OMS['o3']['8h']} µg/m³ entre ≈ {_es(min(o3.values()), 0)} y ≈ {_es(max(o3.values()), 0)} por año según la versión ("
        + "; ".join(f"{c} {_es(o3[c])}" for c in cic) + ")"
        + (f"; temporada alta (6 meses) " + "; ".join(f"{c} {_es(v)}" for c, v in temp.items())
           + f" µg/m³ frente a la guía de {OMS['o3']['temporada_alta']} en los ciclos con 6 meses completos" if temp else "")
        + f". Supera el margen de 3–4 días por año {todos(lambda c: o3[c] > 4)}; la magnitud depende de la versión.")
    no2 = {c: b[c]["media"]["no2"] for c in cic}
    pm10 = {c: b[c]["media"]["pm10"] for c in cic}
    dn = sum(b[c]["dias_sobre_guia_diaria_oms_2021"]["no2_24h_25"] for c in cic)
    dp = sum(b[c]["dias_sobre_guia_diaria_oms_2021"]["pm10_24h_45"] for c in cic)

    def juicio(vals, guia):
        n = sum(v > guia for v in vals.values())
        if n == len(vals):
            return "por encima en todas las versiones"
        if n == 0:
            return "por debajo en todas las versiones"
        return f"por encima {todos(lambda c: vals[c] > guia)}: no se puede afirmar si supera la guía"
    out.append(
        f"NO₂ medio regional {rango(no2.values())} µg/m³ según la versión (guía anual {OMS['no2']['anual']}): {juicio(no2, OMS['no2']['anual'])}; "
        f"{dn} días con media > {OMS['no2']['24h']} µg/m³ en toda la serie. PM10 medio {rango(pm10.values())} µg/m³ (guía {OMS['pm10']['anual']}): "
        f"{juicio(pm10, OMS['pm10']['anual'])}; {dp} días > {OMS['pm10']['24h']} µg/m³. Un valor de ~40 km no representa la exposición junto a "
        "las vías.")
    if sens_pm:
        out.append("Cambio de fórmula del PM en 49r1 (2024-11-12): " + sens_pm["conclusion"])
    otros = {c: sv for c, sv in saltos.items() if sv and c != "49r1"}
    if otros:
        out.append(
            "Los cambios de versión mueven los niveles: "
            + "; ".join(f"al pasar a {c}, " + ", ".join(f"{CORTO[k]} {_es_s(v)} %" for k, v in sv.items())
                        for c, sv in otros.items())
            + " en la media de 30 días, con indicio de salto. Por eso no se agrupan ciclos (p. ej., «antes» y «desde» 49r1) ni se leen las "
            "diferencias entre años como tendencias.")
    out.append(
        "Para decidir: CAMS sirve como evidencia de que el fondo regional de PM2,5 y de ozono supera las guías de la OMS en todas las versiones "
        "del modelo; no sirve para saber cuánto exactamente, si el aire mejora o empeora, ni para comparar barrios. Para eso hacen falta "
        "mediciones locales (estaciones del SVCA de la CVC o del SISAIRE, o campañas con sensores).")
    return out


def _cambios_mismas_fechas_otros_anios(x, ciclo_dia, fechas, f0, ventana):
    """Cambio log de la media de 30 días antes/después de la misma fecha en otros años, si esas 61 jornadas son de un solo ciclo."""
    out = []
    a0 = int(str(f0)[:4])
    for a in range(int(str(fechas[0])[:4]), int(str(fechas[-1])[:4]) + 1):
        if a == a0:
            continue
        fr = np.datetime64(f"{a}{str(f0)[4:]}")
        ic = int(np.searchsorted(fechas, fr))
        if ic - ventana < 0 or ic + ventana >= len(fechas) or fechas[ic] != fr:
            continue
        v = ciclo_dia[ic - ventana:ic + ventana + 1]
        if len(set(v)) != 1 or str(v[0]).startswith("cambio_"):
            continue
        pre, post = x[ic - ventana:ic], x[ic + 1:ic + ventana + 1]
        if np.isfinite(pre).sum() >= 25 and np.isfinite(post).sum() >= 25:
            out.append((a, math.log(np.nanmean(post) / np.nanmean(pre))))
    return out


def analizar_cambios(t, h, ciclo_hora, diario, ciclo_dia, fechas, ventana=30):
    """Para cada cambio de ciclo dentro de la serie: cociente PM10/PM2,5, salto horario y cambios de 30 días con su distribución nula."""
    r_h = h["pm10"] / h["pm2_5"]
    claves = list(CONTAM) + ["pm10_pm25"]
    n = len(fechas)
    # distribución nula: ventanas de 30 días antes/después de días centrales lejos de cualquier cambio (61 días de un mismo ciclo)
    nula = {k: [] for k in claves}
    for c in range(ventana, n - ventana):
        v = ciclo_dia[c - ventana:c + ventana + 1]
        if len(set(v)) != 1 or str(v[0]).startswith("cambio_"):
            continue
        for k in claves:
            pre, post = diario[k][c - ventana:c], diario[k][c + 1:c + ventana + 1]
            if np.isfinite(pre).sum() >= 25 and np.isfinite(post).sum() >= 25:
                nula[k].append(math.log(np.nanmean(post) / np.nanmean(pre)))
    nula = {k: np.array(v) for k, v in nula.items()}
    nula_resumen = {k: {"n_ventanas": int(v.size), "p2_5": _r(100 * (math.exp(np.percentile(v, 2.5)) - 1)),
                        "p50": _r(100 * (math.exp(np.percentile(v, 50)) - 1)), "p97_5": _r(100 * (math.exp(np.percentile(v, 97.5)) - 1))}
                    for k, v in nula.items() if v.size}
    cambios = []
    for i, c in enumerate(CICLOS_CAMS):
        f0 = np.datetime64(c["inicio"])
        if i == 0 or f0 <= fechas[0] or f0 > fechas[-1]:
            continue
        previo = CICLOS_CAMS[i - 1]["ciclo"]
        ic = int(np.searchsorted(fechas, f0))
        ent = {"ciclo": c["ciclo"], "fecha": c["inicio"], "ciclo_anterior": previo,
               "cociente_pm10_pm25_horario": {"antes": _pct(r_h[ciclo_hora == previo]), "despues": _pct(r_h[ciclo_hora == c["ciclo"]])}}
        # salto horario del cociente (±2 días)
        t0 = f0.astype("datetime64[h]")
        cand = np.where((t >= t0 - np.timedelta64(48, "h")) & (t < t0 + np.timedelta64(72, "h")))[0]
        mejor = None
        for k in cand:
            if k < 24 or k + 24 > len(r_h):
                continue
            a, b = np.nanmean(r_h[k - 24:k]), np.nanmean(r_h[k:k + 24])
            if mejor is None or abs(b - a) > mejor[0]:
                mejor = (abs(b - a), k, a, b)
        hl = t[mejor[1]]
        ent["salto_cociente_pm10_pm25"] = {
            "hora_local": str(hl), "hora_utc": str(hl + np.timedelta64(5, "h")),
            "media_24h_antes": _r(mejor[2], 3), "media_24h_despues": _r(mejor[3], 3), "diferencia": _r(mejor[0], 3),
            "detectado": bool(mejor[0] >= UMBRAL_SALTO_COCIENTE),
            "criterio": (f"hora que maximiza |media de las 24 h siguientes − media de las 24 h previas| del cociente horario, entre −48 h y +72 h "
                         f"del inicio del día del cambio; salto si esa diferencia ≥ {UMBRAL_SALTO_COCIENTE}"),
        }
        ent["cambio_30_dias"] = {}
        for k in claves:
            pre, post = diario[k][max(0, ic - ventana):ic], diario[k][ic + 1:ic + ventana + 1]
            if np.isfinite(pre).sum() < 25 or np.isfinite(post).sum() < 25:
                continue
            lc = math.log(np.nanmean(post) / np.nanmean(pre))
            pct = float(100 * np.mean(nula[k] <= lc)) if nula[k].size else float("nan")
            refs = _cambios_mismas_fechas_otros_anios(diario[k], ciclo_dia, fechas, f0, ventana)
            fuera = bool(pct < 2.5 or pct > 97.5)
            mas_extremo = bool(refs) and (lc < min(v for _, v in refs) or lc > max(v for _, v in refs))
            ent["cambio_30_dias"][k] = {"media_30d_antes": _r(np.nanmean(pre), 3 if k == "pm10_pm25" else 1),
                                        "media_30d_despues": _r(np.nanmean(post), 3 if k == "pm10_pm25" else 1),
                                        "cambio_pct": _r(100 * (math.exp(lc) - 1)),
                                        "percentil_en_distribucion_sin_cambio": _r(pct),
                                        "fuera_del_rango_p2_5_p97_5": fuera,
                                        "mismas_fechas_otros_anios_pct": {str(a): _r(100 * (math.exp(v) - 1)) for a, v in refs},
                                        "exceso_sobre_media_otros_anios_pct": _r(100 * (math.exp(lc - np.mean([v for _, v in refs])) - 1)) if refs else None,
                                        "indicio_de_salto": bool(fuera and mas_extremo)}
        cambios.append(ent)
    return cambios, nula_resumen


# ============================================================================ PARTE B: capa de tráfico

PESOS = {
    "motorway": 1.0, "trunk": 1.0, "primary": 0.8, "secondary": 0.6, "tertiary": 0.4,
    "unclassified": 0.2, "residential": 0.1, "living_street": 0.1, "service": 0.05,
    "track": 0.05,  # supuesto propio (no estaba en la especificación): vía agrícola/de finca, como service
}
CERO = {"pedestrian", "footway", "cycleway", "path", "steps", "bridleway", "corridor", "construction", "proposed", "platform", "elevator"}
MAYORES = {"motorway", "trunk", "primary", "secondary", "tertiary"}
ONEWAY_SI = {"yes", "1", "true", "-1"}
SIGMA_M = 50.0
CELDA_M = 10.0
MARGEN_M = 400.0
DIST_PAR_M = 40.0             # separación máxima entre calzadas de una vía dividida
SUMA_U_MAX = 0.5              # |u1 + u2| ≤ 0,5 ↔ sentidos a ≥ ~151°
FACTOR_CALZADA_DOBLE = 0.5
FACTOR_ENLACE_SENS = 0.5      # solo sensibilidad: enlaces *_link a la mitad del peso de su clase (la capa usa 1,0)
UMBRAL_CONSTRUIDO = 50.0      # % de la celda construido (ESA WorldCover, capa 'construido') para contarla como construida
SATURADO = 99.99
CONSULTA_OVERPASS = (f'[out:json][timeout:180];\nway["highway"]({comun.SUR},{comun.OESTE},{comun.NORTE},{comun.ESTE});\nout geom;')
PUNTOS_CONTROL = {"parque_bolivar": (4.7497, -75.9132), "centro_rejilla": (4.7464, -75.9117), "aeropuerto": (4.7601, -75.9545)}


def peso(tags):
    hw = tags.get("highway", "")
    base = hw[:-5] if hw.endswith("_link") else hw
    if hw in CERO or base in CERO:
        return 0.0, hw
    if tags.get("access") == "no" or tags.get("motor_vehicle") == "no":
        return 0.0, hw
    return PESOS.get(base, 0.0), hw


def descargar_osm():
    """Ejecuta la consulta Overpass equivalente (bloqueada desde la terminal de este proyecto; útil en otra red)."""
    import requests
    r = requests.post("https://overpass-api.de/api/interpreter", data={"data": CONSULTA_OVERPASS}, timeout=300)
    r.raise_for_status()
    ruta = os.path.join(DIR, "osm-vias-descarga.json")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(r.text)
    print(f"  → {ruta} (revisar y reemplazar a mano fuentes/osm-vias.json si corresponde)")


def verificar_osm(d):
    """Comprueba que fuentes/osm-vias.json es coherente con CONSULTA_OVERPASS."""
    S, W, N, E = comun.SUR, comun.OESTE, comun.NORTE, comun.ESTE
    el = d["elements"]
    fuera = sum(1 for e in el if e.get("bounds") and (e["bounds"]["maxlat"] < S or e["bounds"]["minlat"] > N
                                                       or e["bounds"]["maxlon"] < W or e["bounds"]["minlon"] > E))
    return {"elementos": len(el), "tipos": dict(Counter(e["type"] for e in el)),
            "sin_etiqueta_highway": sum("highway" not in e.get("tags", {}) for e in el),
            "sin_geometria": sum(len(e.get("geometry") or []) < 2 for e in el),
            "que_no_tocan_la_caja": fuera, "con_bounds": sum("bounds" in e for e in el)}


def muestrear_vias(elementos, transformer, paso=1.0):
    """Muestrea cada segmento de las vías con peso > 0 cada ≤ `paso` m (UTM).

    Devuelve (muestras, vias, longitudes): muestras = dict de arreglos x, y, l (longitud representada, m), w (peso),
    via (índice en `vias`), ux, uy (sentido de circulación unitario).
    """
    partes = {k: [] for k in ("x", "y", "l", "w", "via", "ux", "uy")}
    vias, longitudes = [], {}
    for e in elementos:
        tags = e.get("tags", {})
        w, hw = peso(tags)
        g = e.get("geometry") or []
        if len(g) < 2:
            continue
        x, y = transformer.transform(np.array([p["lon"] for p in g]), np.array([p["lat"] for p in g]))
        x, y = np.asarray(x), np.asarray(y)
        dx, dy = np.diff(x), np.diff(y)
        L = np.hypot(dx, dy)
        longitudes[hw] = longitudes.get(hw, 0.0) + float(L.sum())
        if w <= 0:
            continue
        sentido = -1.0 if tags.get("oneway") == "-1" else 1.0
        n = np.maximum(1, np.ceil(L / paso)).astype(int)
        seg = np.repeat(np.arange(len(L)), n)
        k = np.concatenate([(np.arange(m) + 0.5) / m for m in n])
        Ls = np.where(L > 0, L, 1.0)
        iv = len(vias)
        vias.append({"id": e.get("id"), "hw": hw, "base": hw[:-5] if hw.endswith("_link") else hw, "w": w,
                     "link": hw.endswith("_link"), "oneway": tags.get("oneway") in ONEWAY_SI,
                     "rotonda": tags.get("junction") in ("roundabout", "circular"), "nombre": tags.get("name"), "ref": tags.get("ref")})
        partes["x"].append(x[:-1][seg] + dx[seg] * k)
        partes["y"].append(y[:-1][seg] + dy[seg] * k)
        partes["l"].append((L / n)[seg])
        partes["w"].append(np.full(seg.size, w))
        partes["via"].append(np.full(seg.size, iv))
        partes["ux"].append((dx / Ls)[seg] * sentido)
        partes["uy"].append((dy / Ls)[seg] * sentido)
    return {k: np.concatenate(v) for k, v in partes.items()}, vias, longitudes


def pares_calzada_doble(m, vias, k_vecinos=8, dist_max=DIST_PAR_M, devolver_distancia=False):
    """Marca las muestras de calzadas de vías divididas (oneway, misma clase, sentido contrario, ≤ DIST_PAR_M).

    Búsqueda en un árbol 4D (x, y, S·ux, S·uy) consultado con el sentido invertido: el vecino más cercano es a la vez
    próximo en el espacio y de sentido opuesto. Devuelve (mascara, via_socia).
    """
    from scipy.spatial import cKDTree
    cand_via = np.array([v["oneway"] and v["base"] in MAYORES and not v["link"] and not v["rotonda"] for v in vias])
    clase_via = np.array([v["base"] for v in vias])
    idx = np.where(cand_via[m["via"]])[0]
    marca = np.zeros(m["x"].size, bool)
    socia = np.full(m["x"].size, -1)
    distancia = np.full(m["x"].size, np.nan)
    if idx.size == 0:
        return (marca, socia, distancia) if devolver_distancia else (marca, socia)
    S = 100.0
    P = np.column_stack([m["x"][idx], m["y"][idx], S * m["ux"][idx], S * m["uy"][idx]])
    Q = P.copy()
    Q[:, 2:] *= -1
    dist, nb = cKDTree(P).query(Q, k=k_vecinos, distance_upper_bound=math.hypot(dist_max, S * SUMA_U_MAX) + 1.0)
    par = np.zeros(idx.size, bool)
    soc = np.full(idx.size, -1)
    dsel = np.full(idx.size, np.nan)
    vi = m["via"][idx]
    for j in range(k_vecinos):
        ok = np.isfinite(dist[:, j])
        nbj = np.where(ok, nb[:, j], 0)
        vj = vi[nbj]
        dxy = np.hypot(P[:, 0] - P[nbj, 0], P[:, 1] - P[nbj, 1])
        su = np.hypot(m["ux"][idx] + m["ux"][idx[nbj]], m["uy"][idx] + m["uy"][idx[nbj]])
        cond = ok & ~par & (vi != vj) & (clase_via[vi] == clase_via[vj]) & (dxy <= dist_max) & (su <= SUMA_U_MAX)
        soc[cond] = vj[cond]
        dsel[cond] = dxy[cond]
        par |= cond
    marca[idx[par]] = True
    socia[idx[par]] = soc[par]
    distancia[idx[par]] = dsel[par]
    return (marca, socia, distancia) if devolver_distancia else (marca, socia)


def rasterizar(m, factor, x0, y1, nx, ny, celda=CELDA_M):
    lw = m["l"] * m["w"] * factor
    col = np.floor((m["x"] - x0) / celda).astype(int)
    fil = np.floor((y1 - m["y"]) / celda).astype(int)
    ok = (col >= 0) & (col < nx) & (fil >= 0) & (fil < ny)
    return np.bincount(fil[ok] * nx + col[ok], weights=lw[ok], minlength=ny * nx).reshape(ny, nx)


def rasterizar_vias(elementos, transformer, x0, y1, nx, ny, celda=CELDA_M, paso=1.0, regla_calzadas=True):
    """Longitud de vía ponderada (m) por celda; con la regla de calzadas dobles por defecto. Devuelve (acum, longitudes)."""
    m, vias, longitudes = muestrear_vias(elementos, transformer, paso)
    factor = np.where(pares_calzada_doble(m, vias)[0], FACTOR_CALZADA_DOBLE, 1.0) if regla_calzadas else np.ones(m["x"].size)
    return rasterizar(m, factor, x0, y1, nx, ny, celda), longitudes


def _muestrear_rejilla(arr, lon, lat):
    col = np.floor((np.asarray(lon) - comun.OESTE) / comun.RES).astype(int)
    fil = np.floor((comun.NORTE - np.asarray(lat)) / comun.RES).astype(int)
    ok = (col >= 0) & (col < comun.ANCHO) & (fil >= 0) & (fil < comun.ALTO)
    v = np.full(col.size, np.nan)
    v[ok] = arr[fil[ok], col[ok]]
    return v, fil, col, ok


def _resumen(x, nd=1):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return None
    return {"n": int(x.size), "media": _r(x.mean(), nd), "p10": _r(np.percentile(x, 10), nd), "mediana": _r(np.median(x), nd),
            "p90": _r(np.percentile(x, 90), nd), "max": _r(x.max(), nd)}


def diagnostico_calzadas(m, vias, par, socia):
    res = {}
    via = m["via"]
    for clase in ("motorway", "trunk", "primary", "secondary", "tertiary"):
        ow = np.array([v["base"] == clase and v["oneway"] and not v["link"] and not v["rotonda"] for v in vias])[via]
        if not ow.any():
            continue
        km_ow = m["l"][ow].sum() / 1000
        p = ow & par
        km_p = m["l"][p].sum() / 1000
        # ¿la calzada socia comparte nombre o ref?
        coincide = difiere = sin_dato = 0.0
        for i in np.where(p)[0][::10]:
            a, b = vias[via[i]], vias[socia[i]]
            if (a["nombre"] and a["nombre"] == b["nombre"]) or (a["ref"] and a["ref"] == b["ref"]):
                coincide += 1
            elif (a["nombre"] or a["ref"]) and (b["nombre"] or b["ref"]):
                difiere += 1
            else:
                sin_dato += 1
        tot = max(coincide + difiere + sin_dato, 1)
        nombres = Counter()
        for i in np.where(p)[0]:
            nombres[vias[via[i]]["nombre"] or "(sin nombre)"] += m["l"][i] / 1000
        res[clase] = {"km_oneway": round(km_ow, 2), "km_en_calzada_doble_x05": round(km_p, 2), "pct": round(100 * km_p / max(km_ow, 1e-9), 1),
                      "socia_mismo_nombre_o_ref_pct": round(100 * coincide / tot, 1), "socia_nombre_distinto_pct": round(100 * difiere / tot, 1),
                      "socia_sin_nombre_ni_ref_pct": round(100 * sin_dato / tot, 1),
                      "vias_principales_km": {k: round(v, 2) for k, v in nombres.most_common(8)}}
    return res


def _ordinal(n):
    return f"{n}.ª"


def _capa_auxiliar(nombre):
    """Capa de otro producto (fuentes/rejilla/<nombre>.npy) y su procedencia; (None, None) si no existe."""
    ruta = os.path.join(comun.REJILLA_NPY, f"{nombre}.npy")
    if not os.path.exists(ruta):
        return None, None
    ruta_meta = os.path.join(comun.CAPAS, f"{nombre}.json")
    mt = json.load(open(ruta_meta, encoding="utf-8")) if os.path.exists(ruta_meta) else {}
    return comun.cargar_capa(nombre), {"archivo": os.path.relpath(ruta, comun.RAIZ), "titulo": mt.get("titulo"), "unidad": mt.get("unidad"),
                                       "fecha_proceso": mt.get("fecha_proceso"),
                                       "modificado": datetime.fromtimestamp(os.path.getmtime(ruta)).isoformat(timespec="minutes")}


def estadisticas_zonas(indice, valido, urb):
    """Estadísticas del índice por zona con tres denominadores: área del polígono, población (capa 'poblacion') y celdas construidas
    (capa 'construido' ≥ UMBRAL_CONSTRUIDO %). Ordena por la media ponderada por población (exposición del residente promedio)."""
    zonas = comun.comunas()
    mz = comun.mascara_zonas(zonas)
    pop, dep_pop = _capa_auxiliar("poblacion")
    con, dep_con = _capa_auxiliar("construido")
    pop0 = np.where(np.isfinite(pop), pop, 0.0) if pop is not None else None
    construida = (np.nan_to_num(con, nan=0.0) >= UMBRAL_CONSTRUIDO) if con is not None else None

    def con_poblacion(q):
        P = float(pop0[q].sum())
        if P <= 0:
            return {"poblacion_hab": 0}
        return {"poblacion_hab": int(round(P)), "media_ponderada_poblacion": _r(np.sum(indice[q] * pop0[q]) / P),
                "pct_poblacion_indice_ge_25": _r(100 * pop0[q & (indice >= 25)].sum() / P),
                "pct_poblacion_indice_ge_50": _r(100 * pop0[q & (indice >= 50)].sum() / P)}

    def con_construido(q):
        b = q & construida
        return {"celdas_construidas": int(b.sum()), "pct_celdas_construidas": _r(100 * b.sum() / max(q.sum(), 1)),
                "construidas": _resumen(indice[b])}

    por_zona = []
    for z in zonas:
        q = (mz == z["indice"]) & valido
        r = _resumen(indice[q]) or {}
        tipo = ("huella construida (ESA WorldCover 2021), no un límite administrativo" if "WorldCover" in z["fuente"] else
                "círculo aproximado" if "círculo" in z["fuente"] else "polígono administrativo (OpenStreetMap)")
        r.update({"id": z["id"], "nombre": z["nombre"], "geometria_fuente": z["fuente"], "geometria_tipo": tipo,
                  "pct_celdas_ge_25": _r(100 * np.mean(indice[q] >= 25)) if q.any() else None})
        if pop0 is not None:
            r.update(con_poblacion(q))
        if construida is not None:
            r.update(con_construido(q))
        por_zona.append(r)

    metricas = {"media_ponderada_poblacion": lambda r: r.get("media_ponderada_poblacion"), "media_area": lambda r: r.get("media"),
                "media_celdas_construidas": lambda r: (r.get("construidas") or {}).get("media"),
                "mediana_celdas_construidas": lambda r: (r.get("construidas") or {}).get("mediana")}
    for nombre_m, f in metricas.items():
        vals = sorted((f(r) for r in por_zona if f(r) is not None), reverse=True)
        for r in por_zona:
            if f(r) is not None:
                r.setdefault("puesto", {})[nombre_m] = vals.index(f(r)) + 1
    for r in por_zona:
        p = list((r.get("puesto") or {}).values())
        r["rango_de_puesto_entre_metricas"] = [min(p), max(p)] if p else None
    clave = "media_ponderada_poblacion" if pop0 is not None else "media"
    por_zona.sort(key=lambda r: -(r.get(clave) or 0))

    q = urb & valido
    cab = {"media_area": _r(np.mean(indice[q]))}
    if pop0 is not None:
        cab.update(con_poblacion(q))
    if construida is not None:
        cc = con_construido(q)
        cab.update({"pct_celdas_construidas": cc["pct_celdas_construidas"], "media_celdas_construidas": (cc["construidas"] or {}).get("media")})

    nota = ("Tres denominadores: «media» (y n, p10, mediana, p90, pct_celdas_ge_25) = todas las celdas del polígono: mide la densidad vial del "
            "territorio, no la exposición de quienes viven en él, y baja en las comunas con mucho suelo no construido. "
            "«media_ponderada_poblacion» = índice del residente promedio (pesos = habitantes por celda de la capa 'poblacion'): es la métrica para "
            "comparar zonas y la que ordena esta lista. «construidas» = celdas con ≥ " + _es(UMBRAL_CONSTRUIDO, 0) + " % construido según la capa "
            "'construido' (ESA WorldCover 2021). «puesto» y «rango_de_puesto_entre_metricas» muestran qué tanto depende el orden de la métrica. "
            "Zaragoza no es comparable con las comunas en las métricas por área: su zona es la huella construida del centro poblado "
            "(datos/zaragoza.json), no un polígono administrativo, así que su media por área no se diluye con suelo rural.")
    hallazgo = ""
    if pop0 is not None and construida is not None:
        orden = [r for r in por_zona if r.get("media_ponderada_poblacion") is not None]
        castigada = max(orden, key=lambda r: r["puesto"]["media_area"] - r["puesto"]["media_ponderada_poblacion"])
        mas_poblada = max(orden, key=lambda r: r["poblacion_hab"])
        firmes = [r["nombre"] for r in orden if r["rango_de_puesto_entre_metricas"][0] == r["rango_de_puesto_entre_metricas"][1]]
        medio = orden[2:-2] if len(orden) > 5 else []
        hallazgo = (
            "Índice por zona: ordenadas por la media ponderada por población (índice del residente promedio), "
            + "; ".join(f"{r['nombre']} {_es(r['media_ponderada_poblacion'])}" for r in orden)
            + f". En la cabecera, {_es(cab.get('media_ponderada_poblacion'))} ponderada por población frente a {_es(cab['media_area'])} por área. "
            "La media sobre todo el polígono mide la densidad vial del territorio, no la exposición de los residentes, y castiga a las comunas "
            f"con mucho suelo no construido: {castigada['nombre']} tiene construido solo el {_es(castigada['pct_celdas_construidas'], 0)} % de "
            f"sus celdas y queda {_ordinal(castigada['puesto']['media_area'])} de {len(orden)} por área ({_es(castigada['media'])}), pero "
            f"{_ordinal(castigada['puesto']['media_ponderada_poblacion'])} por población"
            + (", es la más poblada ({} hab)".format(f"{castigada['poblacion_hab']:,}".replace(",", " ")) if castigada is mas_poblada else "")
            + f"; sobre sus celdas construidas, su mediana ({_es(castigada['construidas']['mediana'])}) es la "
            f"{_ordinal(castigada['puesto']['mediana_celdas_construidas'])} y su media ({_es(castigada['construidas']['media'])}) la "
            f"{_ordinal(castigada['puesto']['media_celdas_construidas'])}. Zaragoza no se compara por área: su zona es la huella construida, no un "
            "polígono administrativo. "
            + (f"Conserva el mismo puesto con las cuatro métricas: {', '.join(firmes)}. " if firmes else "")
            + (f"Entre los puestos 3 y {len(orden) - 2} ({', '.join(r['nombre'] for r in medio)}) la media ponderada solo varía "
               f"{_es(medio[0]['media_ponderada_poblacion'] - medio[-1]['media_ponderada_poblacion'])} puntos: ese tramo del orden no es firme "
               "en un índice relativo sin aforos." if medio else ""))
    return por_zona, {"nota": nota, "cabecera": cab, "hallazgo": hallazgo,
                      "dependencias": {"poblacion": dep_pop, "construido": dep_con,
                                       "nota": ("Estas estadísticas usan capas de otros productos (scripts/poblacion.py y scripts/worldcover.py): "
                                                "si se regeneran, reejecutar `scripts/aire.py --solo-trafico`.")}}


def diagnostico_enlaces(indice, indice_l, indice_sin_recorte, urb, m, vias, es_link, tr, tr_inv, radio_m=100.0):
    """Saturación del índice (≥ SATURADO) y su relación con los enlaces *_link; sensibilidad con enlaces a FACTOR_ENLACE_SENS."""
    from scipy.ndimage import label
    from scipy.spatial import cKDTree
    valido = np.isfinite(indice)
    sat = valido & (indice >= SATURADO)
    sat_l = np.isfinite(indice_l) & (indice_l >= SATURADO)
    rur = sat & ~urb
    latc, lonc = comun.centros_celdas()
    out = {"umbral_saturacion": SATURADO, "celdas_saturadas": int(sat.sum()), "urbanas": int((sat & urb).sum()), "rurales": int(rur.sum()),
           "indice_sin_recorte_en_saturadas": {"urbanas": _resumen(indice_sin_recorte[sat & urb]), "rurales": _resumen(indice_sin_recorte[rur]),
                                               "nota": "100 × densidad / p99 de la cabecera, antes de recortar a 100"}}
    if es_link.any() and rur.any():
        arbol = cKDTree(np.column_stack([m["x"][es_link], m["y"][es_link]]))
        xr, yr = tr.transform(lonc[rur], latc[rur])
        d = arbol.query(np.column_stack([xr, yr]))[0]
        out[f"pct_rurales_a_{int(radio_m)}m_o_menos_de_un_enlace"] = _r(100 * np.mean(d <= radio_m))
        xs, ys = tr.transform(lonc[sat & urb], latc[sat & urb])
        out[f"pct_urbanas_a_{int(radio_m)}m_o_menos_de_un_enlace"] = _r(100 * np.mean(arbol.query(np.column_stack([xs, ys]))[0] <= radio_m)) if (sat & urb).any() else None
        # grupos rurales mayores y nombres de las vías mayores o enlaces cercanos
        lab, n = label(rur, structure=np.ones((3, 3)))
        tam = np.bincount(lab.ravel())[1:]
        nombres_via = np.array([(v["nombre"] or v["ref"] or "(sin nombre)") for v in vias])
        mayor = np.array([v["base"] in ("motorway", "trunk", "primary") for v in vias])[m["via"]]
        arbol_m = cKDTree(np.column_stack([m["x"][mayor], m["y"][mayor]]))
        grupos = []
        for k in np.argsort(-tam)[:3]:
            q = lab == k + 1
            la, lo = float(latc[q].mean()), float(lonc[q].mean())
            x, y = tr.transform(lo, la)
            cerca = arbol_m.query_ball_point([x, y], r=150.0)
            nom = Counter(nombres_via[m["via"][mayor][cerca]]).most_common(3)
            grupos.append({"celdas": int(tam[k]), "lat": round(la, 4), "lon": round(lo, 4),
                           "enlace_a_100m_o_menos": bool(arbol.query([x, y])[0] <= radio_m), "vias_a_150m": [n_ for n_, _ in nom]})
        out["grupos_rurales_mayores"] = grupos
    lon_k, lat_k = tr_inv.transform(m["x"][es_link][::10], m["y"][es_link][::10])
    v1 = _muestrear_rejilla(indice, lon_k, lat_k)[0]
    v2 = _muestrear_rejilla(indice_l, lon_k, lat_k)[0]
    out["mediana_en_enlaces"] = {"peso_de_su_clase": _r(np.nanmedian(v1)), "enlaces_a_factor_sensibilidad": _r(np.nanmedian(v2)),
                                 "n": int(np.isfinite(v1).sum())}
    out["sensibilidad_enlaces"] = {"factor_sobre_peso_de_clase": FACTOR_ENLACE_SENS, "celdas_saturadas": int(sat_l.sum()),
                                   "urbanas": int((sat_l & urb).sum()), "rurales": int((sat_l & ~urb).sum()),
                                   "nota": "Solo sensibilidad: la capa publicada usa enlaces con el peso de su clase."}
    return out


def trafico():
    from pyproj import Transformer
    from rasterio.transform import from_origin
    from scipy.ndimage import gaussian_filter
    from scipy.spatial import cKDTree
    from scipy.stats import spearmanr
    from PIL import Image

    print("[B] Capa 'trafico' desde fuentes/osm-vias.json")
    ruta = os.path.join(comun.FUENTES, "osm-vias.json")
    d = json.load(open(ruta, encoding="utf-8"))
    ver_osm = verificar_osm(d)
    print(f"  verificación OSM: {ver_osm}")
    sello = d.get("osm3s", {}).get("timestamp_osm_base", "desconocido")
    try:
        from zoneinfo import ZoneInfo
        sello_local = datetime.fromisoformat(sello.replace("Z", "+00:00")).astimezone(ZoneInfo(TZ)).strftime("%Y-%m-%d %H:%M")
    except Exception:
        sello_local = "desconocido"
    tr = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True)
    tr_inv = Transformer.from_crs("EPSG:32618", "EPSG:4326", always_xy=True)
    bl = np.linspace(comun.OESTE, comun.ESTE, 50)
    bt = np.linspace(comun.SUR, comun.NORTE, 50)
    X, Y = tr.transform(np.concatenate([bl, bl, np.full(50, comun.OESTE), np.full(50, comun.ESTE)]),
                        np.concatenate([np.full(50, comun.SUR), np.full(50, comun.NORTE), bt, bt]))
    x0 = math.floor((min(X) - MARGEN_M) / CELDA_M) * CELDA_M
    x1 = math.ceil((max(X) + MARGEN_M) / CELDA_M) * CELDA_M
    y0 = math.floor((min(Y) - MARGEN_M) / CELDA_M) * CELDA_M
    y1 = math.ceil((max(Y) + MARGEN_M) / CELDA_M) * CELDA_M
    nx, ny = int((x1 - x0) / CELDA_M), int((y1 - y0) / CELDA_M)
    print(f"  rejilla UTM 18N {nx}×{ny} celdas de {CELDA_M:.0f} m")

    m, vias, longitudes = muestrear_vias(d["elements"], tr)
    par, socia, dist_par = pares_calzada_doble(m, vias, devolver_distancia=True)
    factor = np.where(par, FACTOR_CALZADA_DOBLE, 1.0)
    diag_cd = diagnostico_calzadas(m, vias, par, socia)
    # separación entre calzadas emparejadas y, para las oneway sin pareja, distancia a la vía antiparalela más cercana (≤ 150 m)
    par150, _, dist150 = pares_calzada_doble(m, vias, dist_max=150.0, devolver_distancia=True)
    base_m = np.array([v["base"] for v in vias])[m["via"]]
    for clase, dg in diag_cd.items():
        q = par & (base_m == clase)
        if q.sum() >= 50:
            dg["separacion_calzadas_m"] = {f"p{p}": round(float(np.percentile(dist_par[q], p)), 1) for p in (10, 50, 90)}
        q2 = (base_m == clase) & ~par & np.array([v["oneway"] and not v["link"] and not v["rotonda"] for v in vias])[m["via"]]
        if q2.sum() >= 50:
            d2 = dist150[q2]
            dg["oneway_sin_pareja"] = {"km": round(float(m["l"][q2].sum() / 1000), 2),
                                       "pct_con_antiparalela_40_150m": round(float(100 * np.isfinite(d2).mean()), 1),
                                       "distancia_antiparalela_m": ({f"p{p}": round(float(np.nanpercentile(d2, p)), 1) for p in (10, 50, 90)}
                                                                    if np.isfinite(d2).any() else None)}
    print("  calzadas dobles (× 0,5): " + "; ".join(f"{k} {v['km_en_calzada_doble_x05']}/{v['km_oneway']} km oneway "
                                                   f"(socia con mismo nombre/ref {v['socia_mismo_nombre_o_ref_pct']} %)" for k, v in diag_cd.items()))
    acum = rasterizar(m, factor, x0, y1, nx, ny)
    acum_sin = rasterizar(m, np.ones_like(factor), x0, y1, nx, ny)
    transform_utm = from_origin(x0, y1, CELDA_M, CELDA_M)

    def densidad(a, sigma_m):
        # longitud ponderada (m) / área de celda (m²) → m/m²; núcleo normalizado; ×1000 → km/km²
        return gaussian_filter(a / (CELDA_M ** 2), sigma=sigma_m / CELDA_M, mode="constant", cval=0.0, truncate=4.0) * 1000.0

    def a_rejilla(a):
        return comun.reproyectar(a, transform_utm, "EPSG:32618", remuestreo="average")

    dens_rej = a_rejilla(densidad(acum, SIGMA_M))
    urb = comun.mascara_urbana()
    p99 = float(np.nanpercentile(dens_rej[urb], 99))
    indice = np.clip(100.0 * dens_rej / p99, 0, 100).astype(np.float32)
    pico_linea = 1000.0 / (math.sqrt(2 * math.pi) * SIGMA_M) / p99 * 100   # índice en el eje de una línea aislada con w = 1

    # sensibilidad a σ y a la regla de calzadas dobles
    sens = {}
    for s in (25.0, 100.0, 150.0):
        sens[f"sigma_{int(s)}m"] = round(float(spearmanr(dens_rej[urb], a_rejilla(densidad(acum, s))[urb]).statistic), 3)
    dens_sin = a_rejilla(densidad(acum_sin, SIGMA_M))
    p99_sin = float(np.nanpercentile(dens_sin[urb], 99))
    indice_sin = np.clip(100.0 * dens_sin / p99_sin, 0, 100)
    sens_cd = {"spearman_cabecera_con_y_sin_regla": round(float(spearmanr(dens_rej[urb], dens_sin[urb]).statistic), 3),
               "p99_sin_regla_km_km2": round(p99_sin, 3)}
    print(f"  p99 cabecera = {p99:.3f} km/km² ponderados (sin regla de calzadas: {p99_sin:.3f}); pico de una línea aislada w=1: {pico_linea:.1f}; "
          f"Spearman σ: {sens}; con/sin regla: {sens_cd['spearman_cabecera_con_y_sin_regla']}")

    # enlaces *_link: pesan como su clase (supuesto); diagnóstico de saturación y sensibilidad con 0,5 × clase (solo informativo)
    es_link = np.array([v["link"] for v in vias])[m["via"]]
    acum_l = rasterizar(m, factor * np.where(es_link, FACTOR_ENLACE_SENS, 1.0), x0, y1, nx, ny)
    dens_l = a_rejilla(densidad(acum_l, SIGMA_M))
    indice_l = np.clip(100.0 * dens_l / float(np.nanpercentile(dens_l[urb], 99)), 0, 100)
    enlaces = diagnostico_enlaces(indice, indice_l, 100.0 * dens_rej / p99, urb, m, vias, es_link, tr, tr_inv)
    enlaces["spearman_cabecera_con_enlaces_1_y_0_5"] = round(float(spearmanr(dens_rej[urb], dens_l[urb]).statistic), 3)
    print(f"  enlaces *_link: {json.dumps(enlaces, ensure_ascii=False)}")

    # ---------------- verificaciones (se guardan en trafico.json)
    clase_via = np.array([v["hw"] for v in vias])
    ow_via = np.array([v["oneway"] for v in vias])
    sel = np.arange(0, m["x"].size, 10)                    # una muestra cada ~10 m
    lon_s, lat_s = tr_inv.transform(m["x"][sel], m["y"][sel])
    v_s, fil_s, col_s, ok_s = _muestrear_rejilla(indice, lon_s, lat_s)
    vsin_s = _muestrear_rejilla(indice_sin, lon_s, lat_s)[0]
    rural_s = np.zeros(sel.size, bool)
    rural_s[ok_s] = ~urb[fil_s[ok_s], col_s[ok_s]]
    hw_s = clase_via[m["via"][sel]]
    ow_s = ow_via[m["via"][sel]]
    par_s = par[sel]
    medianas = {}
    for hw in sorted(set(hw_s), key=lambda c: -PESOS.get(c.replace("_link", ""), 0)):
        q = (hw_s == hw) & ok_s
        if q.sum() < 20:
            continue
        medianas[hw] = {"peso": PESOS.get(hw.replace("_link", ""), 0.0), "todas": _r(np.nanmedian(v_s[q])), "n": int(q.sum()),
                        "rurales": _r(np.nanmedian(v_s[q & rural_s])) if (q & rural_s).sum() >= 20 else None}
    subtipos = {}
    for hw in ("trunk", "primary", "secondary"):
        for nombre, q in (("calzada_doble", par_s), ("oneway_sin_calzada_opuesta", ow_s & ~par_s), ("doble_sentido", ~ow_s)):
            qq = (hw_s == hw) & ok_s & rural_s & q
            if qq.sum() >= 20:
                subtipos[f"{hw}_{nombre}_rural"] = {"mediana": _r(np.nanmedian(v_s[qq])), "mediana_sin_regla": _r(np.nanmedian(vsin_s[qq])),
                                                     "n": int(qq.sum())}
    tr_cd, pr_ds = subtipos.get("trunk_calzada_doble_rural"), subtipos.get("primary_doble_sentido_rural")
    cociente_tp = None
    if tr_cd and pr_ds:
        cociente_tp = {"con_regla": _r(tr_cd["mediana"] / pr_ds["mediana"], 2), "sin_regla": _r(tr_cd["mediana_sin_regla"] / pr_ds["mediana_sin_regla"], 2),
                       "esperado_por_pesos": round(PESOS["trunk"] / PESOS["primary"], 2)}

    # perfil perpendicular a troncales rurales
    es_tr = np.where(np.isin(clase_via[m["via"]], ["trunk"]))[0][::50]
    lon_t, lat_t = tr_inv.transform(m["x"][es_tr], m["y"][es_tr])
    vt, ft, ct, okt = _muestrear_rejilla(indice, lon_t, lat_t)
    rur_t = np.zeros(es_tr.size, bool)
    rur_t[okt] = ~urb[ft[okt], ct[okt]]
    es_tr = es_tr[rur_t]
    perfil = {}
    for dist in (0, 30, 60, 100, 150, 250):
        vals = []
        for lado in ((1, -1) if dist else (1,)):
            px = m["x"][es_tr] - lado * dist * m["uy"][es_tr]
            py = m["y"][es_tr] + lado * dist * m["ux"][es_tr]
            lo, la = tr_inv.transform(px, py)
            vals.append(_muestrear_rejilla(indice, lo, la)[0])
        perfil[f"{dist}_m"] = {"mediana": _r(np.nanmedian(np.concatenate(vals))),
                               "gaussiana_linea_aislada_rel": round(math.exp(-dist ** 2 / (2 * SIGMA_M ** 2)), 3)}

    # puntos de control
    puntos = {k: _r(_muestrear_rejilla(indice, [lo], [la])[0][0]) for k, (la, lo) in PUNTOS_CONTROL.items()}
    # río La Vieja
    rio = comun.lineas_rio()
    npts = max(2, int(rio.length / 0.0002))
    pr = [rio.interpolate(f, normalized=True) for f in np.linspace(0, 1, npts)]
    v_rio = _muestrear_rejilla(indice, [p.x for p in pr], [p.y for p in pr])[0]
    # rural y norte/sur
    valido = np.isfinite(indice)
    rural = ~urb & valido
    q_tr = (hw_s == "trunk") & ok_s
    v_flip = indice[comun.ALTO - 1 - fil_s[q_tr], col_s[q_tr]]
    # índice por distancia a vías principales (centro de celda → eje de vía), cabecera
    q_may = np.isin(np.array([v["base"] for v in vias])[m["via"]], list(MAYORES))
    arbol = cKDTree(np.column_stack([m["x"][q_may][::5], m["y"][q_may][::5]]))
    latc, lonc = comun.centros_celdas()
    xc, yc = tr.transform(lonc.ravel(), latc.ravel())
    dist_may = arbol.query(np.column_stack([xc, yc]))[0].reshape(comun.ALTO, comun.ANCHO)
    bordes = [0, 25, 50, 100, 150, 250, 500, np.inf]
    por_dist = {}
    for a, b in zip(bordes[:-1], bordes[1:]):
        q = urb & valido & (dist_may >= a) & (dist_may < b)
        etq = f"{a}-{b}_m" if np.isfinite(b) else f">={a}_m"
        r = _resumen(indice[q])
        if r:
            r["pct_celdas_ge_10"] = _r(100 * np.mean(indice[q] >= 10))
            r["pct_celdas_ge_25"] = _r(100 * np.mean(indice[q] >= 25))
        por_dist[etq] = r
    lejos = urb & valido & (dist_may >= 150)
    pct_lejos_ge10 = _r(100 * np.mean(indice[lejos] >= 10))
    # zonas (geometría vigente de comun.comunas(): Zaragoza = datos/zaragoza.json si existe), con métricas comparables entre zonas
    por_zona, zonas_resumen = estadisticas_zonas(indice, valido, urb)
    print("  por zona (media ponderada por población / media por área / mediana en celdas construidas): "
          + "; ".join(f"{r['nombre']} {r.get('media_ponderada_poblacion')}/{r['media']}/{(r.get('construidas') or {}).get('mediana')}" for r in por_zona))
    print(f"  cabecera: {zonas_resumen['cabecera']}")
    print(f"  {zonas_resumen['hallazgo']}")

    verificacion = {
        "consulta_osm": ver_osm,
        "puntos_control": puntos,
        "rio_la_vieja_eje": _resumen(v_rio) | {"pct_ge_25": _r(100 * np.nanmean(v_rio >= 25))},
        "rural_fuera_cabecera": _resumen(indice[rural], 2) | {"pct_menor_0_5": _r(100 * np.mean(indice[rural] < 0.5))},
        "medianas_por_clase_en_muestras_cada_10m": medianas,
        "medianas_rurales_por_tipo_de_calzada": subtipos,
        "cociente_troncal_dividida_vs_primaria_doble_sentido_rural": cociente_tp,
        "perfil_perpendicular_troncales_rurales": perfil,
        "indice_por_distancia_a_vias_principales_cabecera": por_dist,
        "pct_celdas_cabecera_a_150m_o_mas_de_vias_principales_con_indice_ge_10": pct_lejos_ge10,
        "norte_sur": {"mediana_troncales": _r(np.nanmedian(v_s[q_tr])), "mediana_con_filas_invertidas": _r(np.nanmedian(v_flip))},
        "pico_teorico_linea_aislada_w1": round(pico_linea, 1),
        "pct_celdas_cabecera_saturadas_en_100": _r(100 * np.mean(indice[urb] >= 100), 2),
        "enlaces_y_saturacion": enlaces,
    }

    # interpretación derivada de la propia capa
    def _d(etq, campo="mediana"):
        r = por_dist.get(etq)
        return r[campo] if r else None
    med_100_500 = [_d(e) for e in ("100-150_m", "150-250_m", "250-500_m") if _d(e) is not None]
    interpretacion = (
        "No hay umbrales sanitarios para este índice: es relativo y las bandas son descriptivas, derivadas de la propia capa "
        "(verificacion.indice_por_distancia_a_vias_principales_cabecera). En la cabecera, la mediana del índice es "
        f"{_d('0-25_m')} a menos de 25 m del eje de una vía principal (trunk, primary, secondary o tertiary), {_d('25-50_m')} entre 25 y 50 m, "
        f"{_d('50-100_m')} entre 50 y 100 m, {min(med_100_500)}–{max(med_100_500)} entre 100 y 500 m y {_d('>=500_m')} a más de 500 m "
        f"(p90 {_d('>=500_m', 'p90')}); el {pct_lejos_ge10} % de las celdas urbanas a 150 m o más de una vía principal tiene índice ≥ 10 por la "
        f"densidad de calles residenciales. Una vía aislada de peso 1 (troncal) da ≈ {pico_linea:.0f} en su eje. Lectura sugerida: "
        "< 10 = baja densidad vial ponderada (zona rural, bordes urbanos o manzanas lejos de vías principales); "
        "10–25 = malla residencial o vías principales a 100–500 m; "
        "25–50 = 25–100 m de una vía principal, o malla residencial muy densa; "
        "≥ 50 = franja inmediata (menos de ~25–50 m) de vías principales o confluencia de varias. "
        "Un mismo valor puede venir de una arteria cercana o de muchas calles residenciales: el índice no distingue. Para comparar zonas use la "
        "media ponderada por población (estadisticas_por_zona), no la media sobre el área del polígono, que mide la densidad vial del territorio "
        "y no la exposición de los residentes. Para concentraciones reales se necesitan mediciones (estaciones o campañas con sensores) o un "
        "modelo de dispersión con aforos.")

    total_pond = {hw: round(L / 1000, 2) for hw, L in sorted(longitudes.items(), key=lambda kv: -kv[1])}
    paleta = ["#f7f4ea", "#f3d27a", "#e8913a", "#c2452d", "#6b1d2a"]
    meta = {
        "titulo": "Exposición relativa al tráfico vehicular",
        "descripcion": ("Índice de 0 a 100 que indica qué tan cerca está cada lugar de vías con más tráfico probable (según su categoría en "
                        "OpenStreetMap). No es una medición de contaminación: 100 marca las zonas urbanas más expuestas (1 % superior)."),
        "unidad": "índice relativo 0–100 (adimensional)",
        "fuente": {
            "nombre": "OpenStreetMap — red vial (highway=*) descargada con Overpass API",
            "url": "https://www.openstreetmap.org/copyright",
            "licencia": "ODbL 1.0 (© colaboradores de OpenStreetMap)",
            "cita": f"© colaboradores de OpenStreetMap, ODbL 1.0. Instantánea Overpass {sello} (UTC). Índice derivado por BioMap Cartago.",
            "consulta_overpass_equivalente": CONSULTA_OVERPASS,
        },
        "periodo": f"Red vial OSM, instantánea Overpass {sello} (UTC) = {sello_local} hora de Bogotá; sin dimensión temporal (no hay aforos)",
        "resolucion_original_m": CELDA_M,
        "procesamiento": [
            "Pesos por clase OSM: motorway/trunk 1,0; primary 0,8; secondary 0,6; tertiary 0,4; unclassified 0,2; residential/living_street 0,1; "
            "service 0,05; *_link = peso de su clase; peatonal, footway, cycleway, path, steps, construction = 0. Supuestos propios: track = 0,05; "
            "vías con access=no o motor_vehicle=no = 0.",
            f"Reproyección a UTM 18N (EPSG:32618) y muestreo de cada segmento cada ≤ 1 m.",
            f"Regla de calzadas dobles (supuesto): las muestras de una vía oneway de clase motorway–tertiary (sin *_link ni glorietas) que tienen a "
            f"≤ {DIST_PAR_M:.0f} m otra vía oneway de la misma clase en sentido contrario (≥ ~151°) pesan × {FACTOR_CALZADA_DOBLE}: una vía dividida "
            "cuenta una vez, como una de calzada sencilla de su clase. Las calles de un solo sentido sin calzada opuesta pesan completo.",
            f"Rasterización de la longitud ponderada en celdas de {CELDA_M:.0f} m con {MARGEN_M:.0f} m de margen.",
            f"Núcleo gaussiano isotrópico normalizado, σ = {SIGMA_M:.0f} m (truncado a 4σ) → densidad vial ponderada suavizada en km/km².",
            "Promedio a la rejilla común EPSG:4326 de 0,00025° (≈ 27,7 m).",
            f"Normalización: percentil 99 dentro de la cabecera urbana (OSM) = 100 (p99 = {p99:.3f} km/km² ponderados); recorte a [0, 100].",
        ],
        "parametros": {"pesos": PESOS, "peso_cero": sorted(CERO), "sigma_m": SIGMA_M, "celda_m": CELDA_M,
                       "p99_cabecera_km_km2_ponderados": round(p99, 4),
                       "calzadas_dobles": {"distancia_max_m": DIST_PAR_M, "suma_vectores_sentido_max": SUMA_U_MAX, "factor": FACTOR_CALZADA_DOBLE,
                                           "clases": sorted(MAYORES), "diagnostico_por_clase_en_la_descarga": diag_cd},
                       "longitud_osm_km_por_clase_vias_descargadas_incluye_tramos_fuera": total_pond},
        "fundamento_sigma": {
            "referencia": "Karner, A. A., Eisinger, D. S. y Niemeier, D. A. (2010). Near-roadway air quality: synthesizing the findings from real-world data. "
                          "Environmental Science & Technology, 44(14), 5334–5344. doi:10.1021/es100008x",
            "hallazgo": "Con normalización por el borde de la vía, casi todos los contaminantes decaen al fondo entre 115 y 570 m; CO y el número de partículas "
                        "ultrafinas bajan al menos 50 % hacia los 150 m; NO₂ y benceno decaen de forma sostenida en todo el rango; la masa de PM no muestra tendencia.",
            "consecuencia": "Con σ = 50 m el perfil a través de una vía cae al 50 % a ≈ 59 m, al 14 % a 100 m y al ≈ 1 % a 150 m: el índice describe la franja de "
                            "gradiente fuerte (0–150 m) y es más empinado que el decaimiento del NO₂ observado por Karner et al.",
            "sensibilidad_spearman_cabecera": sens,
        },
        "sensibilidad_regla_calzadas_dobles": sens_cd,
        "hallazgos": [zonas_resumen["hallazgo"]] if zonas_resumen["hallazgo"] else [],
        "estadisticas_por_zona": por_zona,
        "estadisticas_por_zona_nota": zonas_resumen["nota"],
        "estadisticas_cabecera": zonas_resumen["cabecera"],
        "estadisticas_por_zona_dependencias": zonas_resumen["dependencias"],
        "verificacion": verificacion,
        "limitaciones": [
            "Índice relativo de proximidad a vías ponderadas por su categoría en OSM; NO es una concentración ni una medición, y no usa aforos vehiculares (no hay aforos abiertos para Cartago).",
            "La categoría OSM es un sustituto grueso del volumen de tráfico; no considera velocidad, congestión, pendiente, flota (motos, buses, camiones cañeros) ni horario.",
            "Calzadas dobles: se cuentan una vez por una regla geométrica (oneway de la misma clase, sentido contrario, ≤ 40 m). Una vía dividida pesa "
            "como una de calzada sencilla de su clase aunque tenga más carriles; si una de las calzadas no está marcada como oneway en OSM, la vía "
            "cuenta doble. Dos calles de un solo sentido de la misma clase a menos de 40 m también se contarían como una. "
            + (f"En esta red, {diag_cd['trunk']['oneway_sin_pareja']['km']} km de troncal oneway quedan sin pareja y suman completo "
               f"(el {diag_cd['trunk']['oneway_sin_pareja']['pct_con_antiparalela_40_150m']} % tiene la calzada opuesta a "
               f"{diag_cd['trunk']['oneway_sin_pareja']['distancia_antiparalela_m']['p10']}–{diag_cd['trunk']['oneway_sin_pareja']['distancia_antiparalela_m']['p90']} m, "
               "tramos con separador más ancho que el umbral); las calles de un solo sentido del centro (p. ej., Carreras 4, 4A y 5, Calle 14) tienen su par "
               f"antiparalelo a {diag_cd['secondary']['oneway_sin_pareja']['distancia_antiparalela_m']['p10']}–"
               f"{diag_cd['secondary']['oneway_sin_pareja']['distancia_antiparalela_m']['p90']} m y no se emparejan."
               if diag_cd.get("trunk", {}).get("oneway_sin_pareja", {}).get("distancia_antiparalela_m")
               and diag_cd.get("secondary", {}).get("oneway_sin_pareja", {}).get("distancia_antiparalela_m") else ""),
            (f"Los enlaces (*_link) pesan como su clase (supuesto), aunque un ramal lleva solo una parte del tráfico de la vía. En los "
             f"intercambiadores confluyen en pocos metros la troncal, varios ramales y la vía que cruza, y el índice se recorta en 100: la mediana en "
             f"los enlaces es {_es(enlaces['mediana_en_enlaces']['peso_de_su_clase'])} (n = {enlaces['mediana_en_enlaces']['n']} muestras cada ~10 m). "
             f"De las {enlaces['celdas_saturadas']} celdas con índice ≥ {_es(SATURADO, 2)}, {enlaces['urbanas']} están en la cabecera y "
             f"{enlaces['rurales']} fuera"
             + (f"; el {_es(enlaces.get('pct_rurales_a_100m_o_menos_de_un_enlace'), 0)} % de las rurales está a ≤ 100 m de un enlace (grupos mayores: "
                + "; ".join(f"{g['lat']}, {g['lon']}, {g['celdas']} celdas, {' / '.join(g['vias_a_150m'])}" for g in enlaces.get("grupos_rurales_mayores", []))
                + ")" if enlaces.get("grupos_rurales_mayores") else "")
             + f". Sensibilidad (no aplicada a la capa): con los enlaces a {_es(FACTOR_ENLACE_SENS)} × su clase quedarían "
             f"{enlaces['sensibilidad_enlaces']['celdas_saturadas']} celdas saturadas ({enlaces['sensibilidad_enlaces']['urbanas']} urbanas, "
             f"{enlaces['sensibilidad_enlaces']['rurales']} rurales) y la mediana en los enlaces seguiría en "
             f"{_es(enlaces['mediana_en_enlaces']['enlaces_a_factor_sensibilidad'])}: la saturación viene de la confluencia de vías y del recorte, "
             "no solo del peso de los ramales (el orden de las celdas de la cabecera no cambia: Spearman "
             f"{_es(enlaces['spearman_cabecera_con_enlaces_1_y_0_5'], 3)}). Sin recortar, la mediana en las celdas saturadas es "
             f"{_es((enlaces['indice_sin_recorte_en_saturadas']['urbanas'] or {}).get('mediana'))} en la cabecera y "
             f"{_es((enlaces['indice_sin_recorte_en_saturadas']['rurales'] or {}).get('mediana'))} fuera. Lea 100 junto a intercambiadores y troncales "
             "sin calzada opuesta como «máximo de la escala», no como una exposición proporcionalmente mayor."),
            "El núcleo de σ = 50 m es más corto que el decaimiento de NO₂ medido (hasta ~500 m); los gradientes lejanos están subrepresentados.",
            "No incluye viento, topografía ni efecto cañón de las calles.",
            "La completitud de OSM es menor en zona rural (vías terciarias y caminos de finca pueden faltar o estar mal clasificados).",
            "La descarga Overpass usó la misma caja que la rejilla común: las vías que quedan enteramente fuera no se cuentan, por lo que en los "
            "~150 m junto al borde de la extensión el índice puede estar subestimado.",
            "La normalización con el percentil 99 de la cabecera hace que el índice solo sea comparable dentro de esta capa.",
        ],
        "rango_visual": [0, 100],
        "paleta": paleta,
        "interpretacion": interpretacion,
        "uso_en_aplicacion": ("Rotular como «Exposición relativa al tráfico (índice 0–100)», sin unidades de concentración. No sustituye ni debe "
                              "rotularse como NO₂ en µg/m³; para el aire regional use datos/series/aire.json (un solo valor para el municipio)."),
    }
    est = comun.guardar_capa("trafico", indice, escala=0.01, desplazamiento=0, meta=meta)

    # PNG decodificada frente al .npy
    rgba = np.asarray(Image.open(os.path.join(comun.CAPAS, "trafico.png")))
    v = rgba[..., 0].astype(np.int64) * 256 + rgba[..., 1]
    dec = np.where(v == 0, np.nan, (v - 1) * 0.01)
    npy = comun.cargar_capa("trafico")
    ruta_meta = os.path.join(comun.CAPAS, "trafico.json")
    mj = json.load(open(ruta_meta, encoding="utf-8"))
    mj["verificacion"]["png_vs_npy"] = {"max_abs_dif": round(float(np.nanmax(np.abs(dec - npy))), 4),
                                        "misma_mascara_nan": bool((np.isnan(dec) == np.isnan(npy)).all())}
    comun.guardar_json(ruta_meta, mj)
    print(f"  estadísticas: {est}")
    print(f"  verificación: {json.dumps({k: verificacion[k] for k in ('puntos_control', 'norte_sur', 'cociente_troncal_dividida_vs_primaria_doble_sentido_rural', 'pct_celdas_cabecera_a_150m_o_mas_de_vias_principales_con_indice_ge_10')}, ensure_ascii=False)}")
    print(f"  perfil: {json.dumps(perfil, ensure_ascii=False)}")
    print(f"  por distancia: {json.dumps(por_dist, ensure_ascii=False)}")
    print(f"  png vs npy: {mj['verificacion']['png_vs_npy']}")
    return indice, p99, sens


# ============================================================================ PARTE C: viabilidad S5P

HIJO_ORBITA = r"""
import json, logging, os, re, sys, time
os.environ["CPL_VSIL_CURL_ALLOWED_EXTENSIONS"] = ".nc"
os.environ["GDAL_DISABLE_READDIR_ON_OPEN"] = "EMPTY_DIR"
import numpy as np
url, ruta_log, lat0, lon0, caja = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
f = open(ruta_log, "w", buffering=1)
t0 = time.time()
cont = {"peticiones": 0, "bytes": 0}
class H(logging.Handler):
    def emit(self, r):
        m = r.getMessage()
        mm = re.search(r"Downloading (\d+)-(\d+)", m)
        if mm:
            cont["peticiones"] += 1
            cont["bytes"] += int(mm.group(2)) - int(mm.group(1)) + 1
def ev(txt, **extra):
    f.write(json.dumps({"s": round(time.time() - t0, 2), **cont, "evento": txt, **extra}) + "\n")
lg = logging.getLogger("rasterio"); lg.addHandler(H()); lg.setLevel(logging.DEBUG)
import rasterio
from rasterio.windows import Window
def sub(v):
    return 'HDF5:"/vsicurl/%s"://PRODUCT/%s' % (url, v)
with rasterio.Env(CPL_DEBUG=True):
    try:
        with rasterio.open(sub("latitude")) as s:
            ev("ABIERTO_latitude", forma=[s.height, s.width], bloques=[list(b) for b in s.block_shapes])
            col = s.read(1, window=Window(s.width // 2, 0, 1, s.height))[:, 0]
            filas = np.where(np.abs(col - lat0) < 0.6)[0]
            ev("columna_central", filas=[int(filas.min()), int(filas.max())] if filas.size else None)
            if not filas.size:
                ev("SIN_COBERTURA"); sys.exit(0)
            r0, r1 = max(int(filas.min()) - 20, 0), min(int(filas.max()) + 20, s.height)
            lat = s.read(1, window=Window(0, r0, s.width, r1 - r0))
        with rasterio.open(sub("longitude")) as s:
            lon = s.read(1, window=Window(0, r0, s.width, r1 - r0))
        q = (np.abs(lat - lat0) < caja) & (np.abs(lon - lon0) < caja)
        ev("geolocalizacion", pixeles=int(q.sum()))
        if q.any():
            ii, jj = np.where(q)
            a0, a1, b0, b1 = int(ii.min()), int(ii.max()) + 1, int(jj.min()), int(jj.max()) + 1
            w = Window(b0, r0 + a0, b1 - b0, a1 - a0)
            with rasterio.open(sub("nitrogendioxide_tropospheric_column")) as s:
                no2 = s.read(1, window=w).astype(float)
            with rasterio.open(sub("qa_value")) as s:
                qa = s.read(1, window=w).astype(float) * s.scales[0]
            m = q[a0:a1, b0:b1]
            ev("LEIDO", no2_mol_m2=[float(x) for x in no2[m]], qa=[round(float(x), 2) for x in qa[m]])
    except Exception as e:
        ev("ERROR", detalle=f"{type(e).__name__}: {str(e)[:200]}")
ev("FIN")
"""


def prueba_extraccion_orbita(href, limite_s=300, caja=0.05):
    """Extracción ACOTADA de una órbita por /vsicurl/ (driver HDF5 de GDAL): geolocaliza Cartago y lee NO₂ troposférico y qa_value
    solo en la ventana que lo cubre. Cuenta peticiones y bytes con el registro de depuración de GDAL."""
    ruta_log = os.path.join(DIR, "s5p_vsicurl.log")
    t0 = time.time()
    try:
        subprocess.run([sys.executable, "-c", HIJO_ORBITA, href, ruta_log, str(LAT), str(LON), str(caja)], timeout=limite_s, capture_output=True)
        agotado = False
    except subprocess.TimeoutExpired:
        agotado = True
    eventos = [json.loads(x) for x in open(ruta_log, encoding="utf-8")] if os.path.exists(ruta_log) else []
    ultimo = eventos[-1] if eventos else {}
    return {"objetivo": f"leer NO₂ troposférico y qa_value de los píxeles a ±{caja}° de Cartago en una órbita OFFL, sin descargar el archivo",
            "limite_s": limite_s, "agotado_el_tiempo": agotado, "duracion_s": round(time.time() - t0, 1),
            "peticiones_por_rango": ultimo.get("peticiones"), "bytes_pedidos": ultimo.get("bytes"),
            "eventos": eventos, "registro": os.path.relpath(ruta_log, comun.RAIZ)}


def versiones_s5p(cat, coleccion):
    """Versión del procesador (en el nombre del archivo) por fecha de muestra, y presencia del reprocesado RPRO en Planetary Computer.
    Cronología de versiones y del RPRO v2.4.0 (2018-05-01 a 2022-07-25): https://www.temis.nl/airpollution/no2col/tropomi_no2_data_versions.php"""
    out = {}
    for f in ("2018-09-01", "2019-09-01", "2020-09-01", "2021-03-01", "2021-09-01", "2022-03-01", "2022-09-01", "2023-09-01", "2024-09-01",
              "2025-09-01", "2026-09-01"):
        d0 = date.fromisoformat(f)
        try:
            its = list(cat.search(collections=[coleccion], intersects={"type": "Point", "coordinates": [LON, LAT]},
                                  datetime=f"{d0.isoformat()}/{(d0 + timedelta(days=3)).isoformat()}",
                                  query={"s5p:product_name": {"eq": "no2"}, "s5p:processing_mode": {"eq": "OFFL"}}, max_items=2).items())
            out[f] = sorted({i.assets["no2"].href.split("?")[0].rsplit("_", 2)[-2] for i in its if "no2" in i.assets}) or None
        except Exception as e:
            out[f] = f"error: {e}"
    try:
        n_rpro = len(list(cat.search(collections=[coleccion], datetime="2018-05-01/2022-07-25",
                                     query={"s5p:product_name": {"eq": "no2"}, "s5p:processing_mode": {"eq": "RPRO"}}, max_items=5).items()))
    except Exception as e:
        n_rpro = f"error: {e}"
    return {"version_procesador_OFFL_por_fecha": out, "items_RPRO_2018_2022": n_rpro,
            "fuente_cronologia": "https://www.temis.nl/airpollution/no2col/tropomi_no2_data_versions.php",
            "cronologia_temis": "v1.x hasta 2021-07-01; v2.2.0 hasta 2021-11-14; v2.3.1 hasta 2022-07-17; v2.4.0+ desde 2022-07-17; "
                                "RPRO v2.4.0 de 2018-05-01 a 2022-07-25 reemplaza las versiones anteriores."}


COLECCION_S5P = "sentinel-5p-l2-netcdf"
REGISTRO_RED = os.path.join(DIR, "s5p_red.jsonl")
ORBITAS_CACHE = os.path.join(DIR, "s5p_orbitas.json")
UMBRAL_HORAS_ANIO = 12.0   # criterio del script: un año de órbitas OFFL en menos de 12 h (≈ una noche de descarga)


def _catalogo_pc():
    import planetary_computer
    import pystac_client
    return pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=planetary_computer.sign_inplace)


def registrar_red(entrada):
    """Añade una medición de red al registro acumulativo fuentes/aire/s5p_red.jsonl (una línea JSON por medición)."""
    with open(REGISTRO_RED, "a", encoding="utf-8") as f:
        f.write(json.dumps(entrada, ensure_ascii=False) + "\n")


def leer_registro_red():
    """Registro de mediciones. Si no existe, lo inicia con la última evaluación guardada (s5p_evaluacion.json), que la respalda."""
    if not os.path.exists(REGISTRO_RED):
        ruta = os.path.join(DIR, "s5p_evaluacion.json")
        if os.path.exists(ruta):
            ev = json.load(open(ruta, encoding="utf-8"))
            red, pv = ev.get("red", {}), ev.get("prueba_extraccion_orbita", {})
            origen = f"importado de fuentes/aire/s5p_evaluacion.json (fecha_prueba {ev.get('fecha_prueba')})"
            if red.get("0-1048575", {}).get("bytes"):
                mb, kb = red["0-1048575"], red.get("0-16383", {})
                registrar_red({"fecha": ev.get("fecha_prueba"), "tipo": "rango_http", "origen": origen,
                               "kB_s": round(mb["bytes"] / max(mb["segundos"] - mb["primer_byte_s"], 0.1) / 1024, 1),
                               "latencia_s": kb.get("primer_byte_s"), "detalle": red})
            leido = next((e for e in pv.get("eventos", []) if e.get("evento") == "LEIDO"), None)
            if leido and not pv.get("agotado_el_tiempo"):
                registrar_red({"fecha": ev.get("fecha_prueba"), "tipo": "lectura_parcial_orbita", "origen": origen, "item": pv.get("item"),
                               "segundos": leido["s"], "bytes": leido["bytes"], "peticiones": leido["peticiones"],
                               "kB_s_efectivo": round(leido["bytes"] / leido["s"] / 1024, 1)})
    if not os.path.exists(REGISTRO_RED):
        return []
    return [json.loads(x) for x in open(REGISTRO_RED, encoding="utf-8") if x.strip()]


def medir_red(href, item_id, repeticiones=2, origen="medición directa"):
    """GET por rango de 16 KB (latencia = tiempo al primer byte) y de 1 MB (ancho de banda sin el primer byte), repetidos; cada
    medición se añade al registro. Devuelve la lista de entradas."""
    import requests
    out = []
    for k in range(repeticiones):
        red = {}
        for rango in ("0-16383", f"{1048576 * (k + 1)}-{1048576 * (k + 2) - 1}"):
            t0 = time.time()
            try:
                r = requests.get(href, headers={"Range": f"bytes={rango}"}, timeout=300, stream=True)
                ttfb = time.time() - t0
                n = sum(len(c) for c in r.iter_content(65536))
                red[rango] = {"bytes": n, "segundos": round(time.time() - t0, 2), "primer_byte_s": round(ttfb, 2)}
            except Exception as e:
                red[rango] = {"error": str(e)[:200]}
        mb = [v for kk, v in red.items() if kk != "0-16383"][0]
        if mb.get("bytes"):
            e = {"fecha": datetime.now().isoformat(timespec="seconds"), "tipo": "rango_http", "origen": origen, "item": item_id,
                 "kB_s": round(mb["bytes"] / max(mb["segundos"] - mb["primer_byte_s"], 0.1) / 1024, 1),
                 "latencia_s": red.get("0-16383", {}).get("primer_byte_s"), "detalle": red}
            registrar_red(e)
            out.append(e)
    return out


def contar_orbitas_offl(cat, anio):
    """Órbitas OFFL de NO₂ que tocan Cartago en un año calendario COMPLETO (sin el recorte por la latencia de OFFL). Caché en
    fuentes/aire/s5p_orbitas.json."""
    cache = json.load(open(ORBITAS_CACHE, encoding="utf-8")) if os.path.exists(ORBITAS_CACHE) else {}
    if str(anio) in cache:
        return cache[str(anio)]
    cat = cat or _catalogo_pc()
    its = list(cat.search(collections=[COLECCION_S5P], intersects={"type": "Point", "coordinates": [LON, LAT]},
                          datetime=f"{anio}-01-01/{anio}-12-31",
                          query={"s5p:product_name": {"eq": "no2"}, "s5p:processing_mode": {"eq": "OFFL"}}, limit=250).items())
    dias = Counter(i.datetime.date().isoformat() for i in its)
    meses = Counter(d[:7] for d in dias)
    ndias = 366 if calendar.isleap(anio) else 365
    r = {"anio": anio, "granulos_OFFL": len(its), "dias_con_al_menos_una_orbita": len(dias), "dias_del_anio": ndias,
         "dias_con_dos_o_mas": sum(v >= 2 for v in dias.values()), "orbitas_por_mes": dict(sorted(meses.items())),
         "consulta": f"STAC {COLECCION_S5P}, punto {LAT}, {LON}, s5p:product_name = no2, s5p:processing_mode = OFFL, {anio}-01-01/{anio}-12-31",
         "fecha_consulta": date.today().isoformat()}
    cache[str(anio)] = r
    comun.guardar_json(ORBITAS_CACHE, cache)
    return r


def estimar_viabilidad_s5p(res, registro, orbitas):
    """Horas por año (descarga completa y lectura parcial) con el número de órbitas de un año completo y el registro de red.
    Modelo conservador por órbita: bytes / ancho de banda + peticiones × latencia (GDAL agrupa rangos y reutiliza conexiones: el tiempo
    medido de la lectura parcial queda por debajo de este modelo)."""
    # órbitas por año: tasa diaria mediana de los meses del año completo × 365 (los huecos del archivo no reducen el costo de un año normal)
    tasas, huecos = [], {}
    for mes, n in orbitas["orbitas_por_mes"].items():
        dm = calendar.monthrange(int(mes[:4]), int(mes[5:7]))[1]
        tasas.append(n / dm)
        if n < 0.9 * dm:
            huecos[mes] = n
    tasa = float(np.median(tasas)) if tasas else 0.0
    n_orb = max(int(round(365 * tasa)), orbitas["granulos_OFFL"])
    orbitas = dict(orbitas) | {"orbitas_por_dia_mediana_mensual": round(tasa, 3), "orbitas_por_anio_nominal": n_orb,
                               "meses_con_huecos_en_el_archivo": huecos,
                               "nota": (f"{orbitas['anio']} tiene {orbitas['granulos_OFFL']} órbitas OFFL sobre Cartago, pero con huecos en el catálogo de "
                                        f"Planetary Computer ({', '.join(f'{k}: {v}' for k, v in huecos.items())}); no se investigó si son de la misión o "
                                        f"del archivo. Para el costo de un año normal se usa la tasa mediana mensual ({_es(tasa, 2)} órbitas/día) × 365 = "
                                        f"{n_orb}." if huecos else "Año sin huecos mensuales.")}
    rangos = [e for e in registro if e.get("tipo") == "rango_http" and e.get("kB_s")]
    lecturas = [e for e in registro if e.get("tipo") == "lectura_parcial_orbita"]
    tam = {m["modo"]: m["bytes"] for m in res.get("muestras", []) if m.get("bytes")}
    dias_med = sorted({e["fecha"][:10] for e in rangos})
    momentos = sorted({e["fecha"][:13] for e in rangos})
    est = {"orbitas_OFFL_por_anio_sobre_cartago": n_orb, "orbitas_fuente": orbitas, "umbral_horas_por_anio": UMBRAL_HORAS_ANIO,
           "registro_red": os.path.relpath(REGISTRO_RED, comun.RAIZ), "mediciones_de_red_en_registro": len(rangos),
           "momentos_distintos_de_medicion": len(momentos), "dias_distintos_de_medicion": len(dias_med),
           "registro_suficiente": bool(len(rangos) >= 5 and len(dias_med) >= 3)}
    if not rangos or not lecturas:
        res["estimacion"] = est
        res["viable_descarga_completa"] = res["viable_lectura_parcial"] = res["viable_con_esta_red"] = False
        res["veredicto_lectura_parcial"] = "sin_mediciones"
        res["conclusion"] = "Sin mediciones de red o de lectura parcial en el registro: no se puede estimar."
        return res
    ult = rangos[-1]
    peor_bw = min(rangos, key=lambda e: e["kB_s"])
    peor_lat = max((e for e in rangos if e.get("latencia_s") is not None), key=lambda e: e["latencia_s"])
    lec = lecturas[-1]
    B, P = lec["bytes"], lec["peticiones"]

    def horas(kB_s, lat):
        return n_orb * (B / (kB_s * 1024) + P * lat) / 3600

    h_hoy_medido = n_orb * lec["segundos"] / 3600
    h_ult = horas(ult["kB_s"], ult["latencia_s"])
    h_peor = horas(peor_bw["kB_s"], peor_lat["latencia_s"])
    resto = UMBRAL_HORAS_ANIO * 3600 - n_orb * P * peor_lat["latencia_s"]
    bw_min = n_orb * B / resto / 1024 if resto > 0 else None
    est.update({
        "ancho_banda_kB_s_ultima_medicion": ult["kB_s"], "latencia_s_ultima_medicion": ult["latencia_s"], "fecha_ultima_medicion": ult["fecha"],
        "ancho_banda_kB_s_peor_registrado": peor_bw["kB_s"], "fecha_peor_ancho_banda": peor_bw["fecha"],
        "latencia_s_peor_registrada": peor_lat["latencia_s"], "fecha_peor_latencia": peor_lat["fecha"],
        "horas_por_archivo": {k: round(v / (ult["kB_s"] * 1024) / 3600, 2) for k, v in tam.items()},
        "horas_por_anio_descarga_completa_ultima_medicion": round(n_orb * tam["OFFL"] / (ult["kB_s"] * 1024) / 3600, 1) if tam.get("OFFL") else None,
        "horas_por_anio_descarga_completa_peor_registrado": round(n_orb * tam["OFFL"] / (peor_bw["kB_s"] * 1024) / 3600, 1) if tam.get("OFFL") else None,
        "parcial_por_orbita_medido": {"segundos": lec["segundos"], "MB": round(B / 1e6, 2), "peticiones": P, "fecha": lec["fecha"], "item": lec.get("item")},
        "parcial_horas_por_anio_al_ritmo_medido_en_la_extraccion": round(h_hoy_medido, 1),
        "parcial_horas_por_anio_modelo_ultima_medicion": round(h_ult, 1),
        "parcial_horas_por_anio_modelo_peor_registrado": round(h_peor, 1),
        "parcial_ancho_banda_minimo_kB_s_para_el_umbral_con_la_peor_latencia": round(bw_min, 1) if bw_min else None,
        "parcial_horas_por_mes_de_actualizacion_peor_registrado": round(h_peor * 30.4 / 365, 1),
        "modelo": "horas = órbitas × (MB por órbita / ancho de banda + peticiones × latencia) / 3600; conservador frente al tiempo medido",
    })
    res["estimacion"] = est
    res["viable_descarga_completa"] = bool(est["horas_por_anio_descarga_completa_ultima_medicion"] is not None
                                           and est["horas_por_anio_descarga_completa_ultima_medicion"] < UMBRAL_HORAS_ANIO)
    res["viable_lectura_parcial"] = bool(h_peor < UMBRAL_HORAS_ANIO)
    res["viable_lectura_parcial_ancho_de_banda_actual"] = bool(h_ult < UMBRAL_HORAS_ANIO)
    res["viable_con_esta_red"] = res["viable_descarga_completa"] or res["viable_lectura_parcial"]
    # Sin un registro de red suficiente, el resultado no se da por viable: la red del proyecto es inestable
    # y hubo al menos una medición previa (no registrada) por debajo del mínimo.
    res["veredicto_lectura_parcial"] = ("indeterminado_registro_de_red_insuficiente" if not est["registro_suficiente"] else
                                        "viable" if res["viable_lectura_parcial"] else
                                        "viable_al_ancho_de_banda_actual_al_limite_con_el_peor" if res["viable_lectura_parcial_ancho_de_banda_actual"]
                                        else "no_viable")
    if not est["registro_suficiente"]:
        res["viable_con_esta_red"] = False
    res["criterio"] = (f"Viable si un año de órbitas OFFL sobre Cartago ({n_orb}, contadas en {orbitas['anio']} completo) se obtiene en menos de "
                       f"{_es(UMBRAL_HORAS_ANIO, 0)} h (≈ una noche) también con el peor ancho de banda y la peor latencia del registro "
                       f"({os.path.relpath(REGISTRO_RED, comun.RAIZ)}). El umbral es una convención del script: la actualización mensual "
                       "cuesta ≈ 1/12 de esa cifra.")
    ver = res.get("versiones", {})
    homog = ("Homogeneidad: en Planetary Computer el archivo mezcla versiones del procesador ("
             + ", ".join(f"{k[:7]}: {'/'.join(v)}" for k, v in ver.get("version_procesador_OFFL_por_fecha", {}).items() if isinstance(v, list))
             + f") y no hay ítems RPRO ({ver.get('items_RPRO_2018_2022')}); el reprocesado homogéneo RPRO v2.4.0 (2018-05-01 a 2022-07-25, TEMIS) "
             "habría que obtenerlo de otra fuente. Con Planetary Computer, usar solo órbitas OFFL desde 2022-07-17 (v2.4.0 o posterior) o tratar "
             "los cambios de versión como cortes de la serie. ") if ver else ""
    ruta = (homog + "Alternativa sin depender de la red local: agregación del lado del servidor (Google Earth Engine COPERNICUS/S5P/OFFL/L3_NO2; "
            "Copernicus Data Space Ecosystem / Sentinel Hub; o recorte OPeNDAP de S5P_L2__NO2____HiR en NASA GES DISC). En todos los casos: "
            "qa_value ≥ 0,75 y promedios mensuales; una celda nativa de 5,5 × 3,5 km sigue siendo escala de ciudad, no de calle; "
            "las órbitas con nubes sobre Cartago no aportan dato, así que las observaciones útiles serán menos que las órbitas.")
    base = (f"Lectura parcial: una órbita OFFL se geolocaliza y se lee para Cartago con {P} peticiones y {_es(B / 1e6, 2)} MB (no los "
            f"~{round(tam.get('OFFL', 0) / 1e6)} MB del archivo), en {_es(lec['segundos'], 1)} s el {lec['fecha'][:10]}. Con {n_orb} órbitas por año "
            f"(una por día: tasa mediana de los meses de {orbitas['anio']}"
            + (f", que tuvo {orbitas['granulos_OFFL']} por huecos del catálogo" if orbitas.get("meses_con_huecos_en_el_archivo") else "") + "): "
            f"≈ {_es(h_hoy_medido)} h/año al ritmo medido; con el modelo conservador, ≈ {_es(h_ult)} h/año con la última medición "
            f"({_es(ult['kB_s'], 0)} kB/s, {_es(ult['latencia_s'], 2)} s de latencia) y ≈ {_es(h_peor)} h/año con lo peor registrado "
            f"({_es(peor_bw['kB_s'], 0)} kB/s, {_es(peor_lat['latencia_s'], 2)} s; {len(rangos)} mediciones). "
            + (f"Hace falta ≥ {_es(bw_min, 0)} kB/s sostenidos para quedar bajo {_es(UMBRAL_HORAS_ANIO, 0)} h/año. " if bw_min else "")
            + f"La actualización mensual cuesta ≈ {_es(h_peor * 30.4 / 365)} h en el peor caso. ")
    if res["veredicto_lectura_parcial"].startswith("indeterminado"):
        cab = (f"Indeterminado: el registro de red es corto ({len(rangos)} mediciones en {len(momentos)} momentos de {len(dias_med)} días) y la red "
               f"del proyecto es inestable; con lo registrado la lectura parcial tomaría ≈ {_es(h_peor)} h/año, pero hace falta sostener ≥ "
               f"{_es(bw_min, 0) if bw_min else 's. d.'} kB/s y no hay evidencia suficiente de que la red lo haga. ")
    elif res["veredicto_lectura_parcial"] == "viable":
        cab = "Viable por lectura parcial, también con lo peor registrado"
        cab += (". " if est["registro_suficiente"] else
                f", pero el registro es corto ({len(rangos)} mediciones en {len(momentos)} momentos de {len(dias_med)} días, todas ≥ "
                f"{_es(peor_bw['kB_s'], 0)} kB/s) y la red del proyecto es inestable (CLAUDE.md): la condición que decide es sostener ≥ "
                f"{_es(bw_min, 0) if bw_min else 's. d.'} kB/s. ")
    elif res["veredicto_lectura_parcial"].startswith("viable_al"):
        cab = (f"Viable por lectura parcial al ancho de banda actual; al límite con lo peor registrado (≈ {_es(h_peor, 0)} h/año frente al umbral de "
               f"{_es(UMBRAL_HORAS_ANIO, 0)} h: el año inicial tomaría más de una noche). ")
    else:
        cab = "No viable por lectura parcial con esta red. "
    completa = (f"La descarga completa no es viable (≈ {_es(est['horas_por_anio_descarga_completa_ultima_medicion'], 0)} h/año con la última "
                f"medición). " if not res["viable_descarga_completa"] else "La descarga completa también sería factible. ")
    res["conclusion"] = cab + base + completa + ruta
    if bw_min:
        res["nota_medicion_anterior_sin_registro"] = (
            "La versión anterior del script usaba 119,1 kB/s y 0,9 s como peor caso (constantes en el código, de una ejecución del 2026-09-30 "
            "cuyo registro se sobrescribió). No se usan porque ningún archivo las respalda; desde entonces cada medición queda en "
            f"{os.path.relpath(REGISTRO_RED, comun.RAIZ)}. Como referencia: 119,1 kB/s está por debajo del mínimo calculado "
            f"({_es(bw_min, 0)} kB/s), así que con esa red el año inicial superaría {_es(UMBRAL_HORAS_ANIO, 0)} h "
            f"(≈ {_es(horas(119.1, max(0.9, peor_lat['latencia_s'])), 1)} h con el modelo).")
    return res


def evaluar_s5p(dias=30, recalcular=False, medir=True):
    """Viabilidad de NO₂ de Sentinel-5P: gránulos sobre Cartago, tamaño por archivo, red (registro acumulativo) y lectura parcial.

    recalcular=True: reutiliza fuentes/aire/s5p_evaluacion.json (muestras, extracción, versiones) y solo cuenta las órbitas de un año
    completo (metadatos STAC) y, si medir=True, añade una medición ligera de red (GET de 16 KB y 1 MB, ×2) al registro.
    """
    import requests
    print("[C] Viabilidad de Sentinel-5P NO₂ en Planetary Computer" + (" (recálculo con la evaluación guardada)" if recalcular else ""))
    ruta_ev = os.path.join(DIR, "s5p_evaluacion.json")
    registro = leer_registro_red()        # inicia el registro con la evaluación anterior si aún no existe
    cat = None if (recalcular and not medir) else _catalogo_pc()
    hoy = date.today()
    if recalcular:
        res = json.load(open(ruta_ev, encoding="utf-8"))
        res.pop("estimacion", None)
        res.setdefault("granulos_nota", ("Ventana reciente: OFFL llega con días de retraso, así que esta cuenta queda recortada; el número de órbitas "
                                         "por año se cuenta en un año calendario completo (estimacion.orbitas_fuente)."))
        if medir:
            item_id = res.get("prueba_extraccion_orbita", {}).get("item")
            its = list(cat.search(collections=[COLECCION_S5P], ids=[item_id]).items()) if item_id else []
            if its:
                href = (its[0].assets.get("no2") or next(iter(its[0].assets.values()))).href
                print("  medición de red (16 KB + 1 MB, ×2)…")
                for e in medir_red(href, item_id, origen="evaluar_s5p(recalcular=True)"):
                    print(f"    {e['fecha']}: {e['kB_s']} kB/s, latencia {e['latencia_s']} s")
        res["fecha_recalculo"] = datetime.now().isoformat(timespec="seconds")
    else:
        col = cat.get_collection(COLECCION_S5P)
        ventana = f"{(hoy - timedelta(days=dias)).isoformat()}/{(hoy - timedelta(days=1)).isoformat()}"
        items = list(cat.search(collections=[col.id], intersects={"type": "Point", "coordinates": [LON, LAT]},
                                datetime=ventana, query={"s5p:product_name": {"eq": "no2"}}, max_items=500).items())
        modos = Counter(i.properties.get("s5p:processing_mode") for i in items)
        res = {"coleccion": col.id, "extent_temporal": col.extent.to_dict()["temporal"]["interval"], "ventana_consulta": ventana,
               "granulos_no2_sobre_cartago": dict(modos),
               "granulos_nota": ("Ventana reciente: OFFL llega con días de retraso, así que esta cuenta queda recortada; el número de órbitas por "
                                 "año se cuenta en un año calendario completo (estimacion.orbitas_fuente)."),
               "muestras": [], "red": {}, "fecha_prueba": datetime.now().isoformat(timespec="seconds")}
        for modo in ("OFFL", "NRTI"):
            for it in [i for i in items if i.properties.get("s5p:processing_mode") == modo][:2]:
                a = it.assets.get("no2") or next(v for v in it.assets.values() if v.href.split("?")[0].endswith(".nc"))
                try:
                    hh = requests.head(a.href, timeout=120)
                    res["muestras"].append({"modo": modo, "item": it.id, "bytes": int(hh.headers.get("Content-Length", 0)), "bbox": it.bbox})
                except Exception as e:
                    res["muestras"].append({"modo": modo, "item": it.id, "error": str(e)})
        offl = [i for i in items if i.properties.get("s5p:processing_mode") == "OFFL"] or items
        if offl:
            href = (offl[0].assets.get("no2") or next(iter(offl[0].assets.values()))).href
            res["red"] = {"mediciones": medir_red(href, offl[0].id, origen="evaluar_s5p")}
            print("  prueba de extracción parcial de una órbita por /vsicurl/ (máx. 300 s)…")
            res["prueba_extraccion_orbita"] = prueba_extraccion_orbita(href) | {"item": offl[0].id}
            pv = res["prueba_extraccion_orbita"]
            leido = next((e for e in pv.get("eventos", []) if e.get("evento") == "LEIDO"), None)
            if leido and not pv.get("agotado_el_tiempo"):
                registrar_red({"fecha": res["fecha_prueba"], "tipo": "lectura_parcial_orbita", "origen": "evaluar_s5p", "item": offl[0].id,
                               "segundos": leido["s"], "bytes": leido["bytes"], "peticiones": leido["peticiones"],
                               "kB_s_efectivo": round(leido["bytes"] / leido["s"] / 1024, 1)})
        print("  versiones del procesador en Planetary Computer…")
        res["versiones"] = versiones_s5p(cat, col.id)
    anio = hoy.year - 1
    print(f"  órbitas OFFL sobre Cartago en {anio} (metadatos STAC; caché en {os.path.relpath(ORBITAS_CACHE, comun.RAIZ)})…")
    orbitas = contar_orbitas_offl(cat, anio)
    res = estimar_viabilidad_s5p(res, leer_registro_red(), orbitas)
    comun.guardar_json(ruta_ev, res)
    print(json.dumps({k: res[k] for k in ("estimacion", "viable_lectura_parcial", "veredicto_lectura_parcial", "viable_con_esta_red", "conclusion")
                      if k in res}, ensure_ascii=False, indent=1))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-serie", action="store_true")
    ap.add_argument("--solo-trafico", action="store_true")
    ap.add_argument("--evaluar-s5p", action="store_true")
    ap.add_argument("--recalcular-s5p", action="store_true",
                    help="recalcula la viabilidad de S5P con la evaluación guardada, las órbitas de un año completo y el registro de red")
    ap.add_argument("--descargar-osm", action="store_true")
    ap.add_argument("--sin-red", action="store_true", help="serie CAMS solo desde la caché de fuentes/aire/ (no consulta la API)")
    a = ap.parse_args()
    if a.evaluar_s5p or a.recalcular_s5p:
        evaluar_s5p(recalcular=a.recalcular_s5p, medir=not a.sin_red)
        sys.exit(0)
    if a.descargar_osm:
        descargar_osm()
        sys.exit(0)
    if not a.solo_trafico:
        serie(sin_red=a.sin_red)
    if not a.solo_serie:
        trafico()
