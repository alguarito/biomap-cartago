"""Producto «clima» de BioMap Cartago: series climáticas 1950–2026 de la celda de reanálisis que cubre Cartago.

FUENTES Y LICENCIAS (verificadas el 2026-09-30)
  1. Temperatura del aire a 2 m y humedad relativa: ERA5-Land (ECMWF / Copernicus Climate Change Service, C3S) servido por la
     Open-Meteo Historical Weather API (https://archive-api.open-meteo.com/v1/archive, models=era5_land, timezone=America/Bogota).
       - Archivo de partida: fuentes/era5land-cartago-1950-2025.json (diario 1950-01-01 a 2025-12-31). No guarda su solicitud; si
         falta, el script lo vuelve a pedir con la solicitud equivalente (misma celda 4.70/−75.90 y elevación 919 m; se comprueba
         que la serie horaria pedida así reproduce sus Tmax y Tmin diarias).
       - 2026 (año parcial, marcado) con la misma API → fuentes/clima/era5land_2026.json.
       - Temperatura y humedad HORARIAS 1950→hoy (misma celda, bloques de 5 años, timeformat=unixtime) →
         fuentes/clima/era5_land_horario_*.json: necesarias para filtrar picos espurios de una hora (ver paso 2).
       - Celda devuelta: lat 4.70, lon −75.90 (rejilla de 0,1°; resolución nativa ≈ 9 km). Open-Meteo corrige la temperatura a la
         elevación de su MDT de 90 m («statistical downscaling», 919 m); con elevation=nan se obtiene la orografía del modelo.
       - Licencias: Open-Meteo, CC BY 4.0 (https://open-meteo.com/en/licence; atribución «Weather data by Open-Meteo.com» con
         enlace). ERA5-Land: CC-BY (Climate Data Store, doi:10.24381/cds.e2161bac; desde el 2 de julio de 2025 la CC-BY sustituye a
         la «Licence to use Copernicus Products»).
       - Cita: Muñoz-Sabater, J. et al. (2021). ERA5-Land: a state-of-the-art global reanalysis dataset for land applications.
         Earth System Science Data 13, 4349–4383. doi:10.5194/essd-13-4349-2021.
     DEFECTO DE LA FUENTE: en Open-Meteo, ERA5-Land NO trae precipitación ni radiación (el archivo de partida tiene null en las
     27 759 filas de precipitation_sum y shortwave_radiation_sum; la documentación de Open-Meteo lo indica). Por eso:
  2. Precipitación y radiación de onda corta diarias: ERA5 (0,25°, ≈ 31 km) vía la misma API (models=era5). ERA5-Land no calcula
     su propia lluvia ni su radiación: usa las de ERA5 interpoladas a 9 km sin corrección (Muñoz-Sabater et al. 2021). Licencia
     CC-BY (CDS). Cita: Hersbach, H. et al. (2020). Q. J. R. Meteorol. Soc. 146, 1999–2049. doi:10.1002/qj.3803; para 1950–1978,
     Bell, B. et al. (2021). Q. J. R. Meteorol. Soc. 147, 4186–4227. doi:10.1002/qj.4174. También se bajan la temperatura y la
     humedad diarias de ERA5 (contraste e índices de Tmax con sus propios umbrales) y su temperatura horaria 2015→hoy (referencia
     del filtro de picos y diagnóstico de la discontinuidad del ciclo diurno de ERA5 en Open-Meteo desde mayo de 2025).
     AVISO: la lluvia de ERA5 en esta celda es ≈ 3 veces la de los pluviómetros del IDEAM y su variabilidad tampoco se parece a la
     observada: precip_total, rx1day y rx5day se publican solo por trazabilidad y NO son aptos para decisiones.
  3. Lluvia mensual de referencia 1981→hoy: CHIRPS v3.0 (Climate Hazards Center, UCSB), 0,05°, COG mensuales globales
     (https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/global/cogs/), leídos por ventana (/vsicurl/, un bloque por archivo)
     y promediados sobre la huella urbana ponderando por la fracción de cada píxel dentro de ella. Licencia CC BY 4.0
     (https://www.chc.ucsb.edu/data/chirps3). Cita: Funk, C., Peterson, P., Harrison, L. et al. (2026). The Climate Hazards Center
     Infrared Precipitation with Stations, Version 3. Scientific Data 13, 718. doi:10.1038/s41597-026-07096-4; datos
     doi:10.15780/G2JQ0P. CHIRPS v3 incorpora estaciones del IDEAM: su comparación con el IDEAM no es independiente.
  4. Radiación solar mensual de referencia 1984→último año completo: NASA POWER, Monthly and Annual API
     (https://power.larc.nasa.gov/api/temporal/monthly/point, ALLSKY_SFC_SW_DWN, kWh/m²/día; GEWEX SRB 1984–2000 y CERES SYN1deg
     2001→, celdas de 1°; POWER corrige SRB hacia CERES por mapeo de cuantiles, pero el empalme de 2001 se nota frente a ERA5; la
     elevación que devuelve la API, 2267 m, es la media de su celda MERRA-2 de 0,5° × 0,625°). Licencia CC BY 4.0; referencia exigida: «The data was obtained from National Aeronautics and Space
     Administration (NASA) Langley Research Center's Prediction Of Worldwide Energy Resources (POWER) project funded through the
     NASA Earth Science Division» (https://power.larc.nasa.gov/docs/referencing/).
  5. Huella urbana (solo para pesos espaciales): Comunas 1–7 de OpenStreetMap (© colaboradores de OpenStreetMap, ODbL 1.0; vía
     comun.comunas() y js/datos-osm.js) y Zaragoza según datos/zaragoza.json (ESA WorldCover 10 m 2021 v200, CC BY 4.0,
     doi:10.5281/zenodo.7254221).
  6. IDEAM, datos abiertos en datos.gov.co, licencia CC BY-SA 4.0 (atribución: Instituto de Hidrología, Meteorología y Estudios
     Ambientales - IDEAM). Se usan para VALIDAR y, además, para calibrar el umbral de dias_tmax_ge_umbral_eq32 (ese campo de la
     serie anual es material derivado de datos IDEAM); por eso el archivo de salida se distribuye con CC BY-SA 4.0.
       - Normales climatológicas (nsz2-kzcq): 1961–1990, 1971–2000, 1981–2010 y 1991–2020 (Directriz OMM-N.° 1203).
       - Estación automática ZARAGOZA (código 0026105250, Cartago): temperatura máxima horaria (ccvq-rp9s), mínima horaria
         (afdg-3zpb), temperatura del aire (sbwg-7ju4) y precipitación cada 10 min (s54a-sgyg), agregadas a día en el servidor
         (SoQL), una consulta por año y variable (la del periodo completo no termina en tiempo razonable).
       - Radiación global MEDIDA (rv9s-8nv6, «Promedios Mensuales y Anual de la Radiación Global Acumulada Diaria para las Estaciones
         Meteorológicas del IDEAM», sensor calibrado, Wh/m²/día, publicado el 2026-09-17): climatología mensual y anual por estación,
         SIN periodo publicado. Se usa la de Zaragoza (Cartago, 943 m) para validar el valor absoluto de ERA5 y de NASA POWER.

PASOS
  1. Lee ERA5-Land 1950–2025 y descarga 2026 hasta el último día con dato (año parcial). Descarga ERA5 1950→hoy por bloques.
  2. Descarga la temperatura y la HR horarias de ERA5-Land, comprueba que sus agregados diarios reproducen el archivo de partida y
     filtra los PICOS ESPURIOS DE UNA HORA (T − media de sus dos vecinas > 2,5 °C con caída simultánea de la HR > 5 puntos; se
     reemplaza la hora por la media de sus vecinas, hasta 3 pasadas). Recalcula Tmax, Tmedia y HR media de los días afectados.
     El umbral se fija con la tasa de casos en ERA5 (sin el artefacto) y se informa la sensibilidad a otros criterios.
  3. Índices anuales: tmedia, tmax_media, tmin_media, txx, tnn, humedad_media (ERA5-Land filtrado); precip_total, rx1day, rx5day
     (ERA5, no aptos para decisiones); precip_chirps; radiacion_kwh_m2_dia (ERA5, MJ/m² ÷ 3,6) y radiacion_power_kwh_m2_dia
     (NASA POWER); completitud.
  4. TX90p y TN90p (ETCCDI, https://etccdi.pacificclimate.org/list_27_indices.shtml): percentil 90 por día del calendario con
     ventana centrada de 5 días, base 1961–1990, cuantil tipo 8 de Hyndman y Fan (numpy method='median_unbiased'), excedencia
     estricta y «bootstrap» para los años de la base (Zhang, Hegerl, Zwiers y Kenyon 2005, J. Climate 18, 1641–1651,
     doi:10.1175/JCLI3366.1). El 29 de febrero usa el umbral del 28. Lo mismo con la Tmax de ERA5 como contraste.
  5. Días con Tmax ≥ 32 °C: se calcula y se comprueba que no es informativo (ERA5-Land filtrado nunca llega a 32 °C; en el
     termómetro de Zaragoza 32 °C es un día corriente). Alternativas, ambas SUPUESTOS METODOLÓGICOS PROPIOS:
       a) dias_tmax_ge_umbral_eq32: umbral de ERA5-Land que se supera con la misma frecuencia con que la estación registra ≥ 32 °C.
       b) dias_tmax_gt_umbral_local (propuesta de índice climatológico de calor): Tmax > percentil 90 de todas las Tmax diarias
          de ERA5-Land en 1961–1990. Se mide su destreza día a día frente a la estación (POD, FAR): no sirve para alertas.
  6. Tendencias por década en 1950–2025, 1981–2025 y 1991–2025 (solo años completos; ERA5 también hasta 2024): MCO con IC 95 % y
     p; IC y p con tamaño efectivo de muestra por autocorrelación de orden 1 de los residuos (Santer et al. 2000, J. Geophys.
     Res. 105, 7337–7356, doi:10.1029/1999JD901105); pendiente de Sen (Sen 1968, JASA 63, 1379–1389) con IC 95 % y Mann-Kendall
     (Mann 1945, Econometrica 13, 245–259) con corrección por empates.
  7. Climatología mensual 1991–2020 (normal estándar de la OMM; la tarea decía «OMS») y del decenio 2016–2025, con anomalías;
     serie mensual completa con anomalías respecto de 1991–2020 (null en meses incompletos).
  8. Validación: estación Zaragoza (temperatura hasta 2023, por la falta de homogeneidad posterior; lluvia), normales IDEAM
     (sesgos y contraste de la tendencia entre normales sucesivas), consistencia de la lluvia de ERA5 con CHIRPS y radiación de
     ERA5 y NASA POWER frente a la climatología medida del IDEAM en Zaragoza (y entre sí, con el empalme SRB → CERES de POWER);
     TN90p con los dos reanálisis; sensibilidad a las cuatro celdas vecinas de ERA5-Land a la misma elevación.
  9. Escribe datos/series/clima.json.

Uso:
  .venv/bin/python scripts/clima.py               # usa caché; descarga lo que falte
  .venv/bin/python scripts/clima.py --actualizar  # vuelve a descargar el año en curso (ERA5-Land, ERA5, IDEAM) y POWER,
                                                  # y relee los 3 últimos meses de CHIRPS
  .venv/bin/python scripts/clima.py --sin-ideam   # omite la validación con el IDEAM (y el umbral eq32)
  .venv/bin/python scripts/clima.py --salida RUTA # escribe en otra ruta (pruebas)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comun  # noqa: E402

import numpy as np  # noqa: E402
import requests  # noqa: E402
from scipy import stats  # noqa: E402

DIR = os.path.join(comun.FUENTES, "clima")
DIR_IDEAM = os.path.join(DIR, "ideam")
os.makedirs(DIR_IDEAM, exist_ok=True)
ERA5L_HIST = os.path.join(comun.FUENTES, "era5land-cartago-1950-2025.json")
SALIDA = os.path.join(comun.DATOS, "series", "clima.json")
API = "https://archive-api.open-meteo.com/v1/archive"
LAT, LON = comun.CENTRO  # 4.7464, -75.9117 → misma celda ERA5-Land que el archivo de partida
TZ = "America/Bogota"
VARS_L = ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "relative_humidity_2m_mean"]
# variables diarias del archivo de partida, en su orden (para volver a pedirlo si falta)
VARS_PARTIDA = ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "precipitation_sum",
                "shortwave_radiation_sum", "relative_humidity_2m_mean"]
POWER_API = "https://power.larc.nasa.gov/api/temporal/monthly/point"
# Validación de temperatura con la estación Zaragoza hasta 2023: después de su hueco de 2023–2025 la estación cambia de nivel
# frente a los dos reanálisis (ver homogeneidad_estacion) y, además, ERA5 (Open-Meteo) cambia su ciclo diurno desde mayo de 2025
FIN_VALIDACION = np.datetime64("2023-12-31")
RADIO_NORMALES_TEND_KM, ALT_NORMALES_TEND_M = 40, 1400
VARS_E = ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "precipitation_sum",
          "shortwave_radiation_sum", "relative_humidity_2m_mean"]
SOCRATA = "https://www.datos.gov.co/resource"
EST_ZARAGOZA = {"codigo": "0026105250", "nombre": "ZARAGOZA (AUT)", "municipio": "Cartago",
                "lat": 4.689777778, "lon": -75.92519444}
IDEAM_DS = {"tx": ("ccvq-rp9s", "max"), "tn": ("afdg-3zpb", "min"), "t": ("sbwg-7ju4", "avg"), "p": ("s54a-sgyg", "sum")}
IDEAM_DESDE = 2000  # la estación tiene temperatura desde 2002 y lluvia desde finales de 2016
# Climatología medida de radiación global (Wh/m²/día) de las estaciones IDEAM con sensor calibrado (publicada el 2026-09-17)
IDEAM_RAD_DS = "rv9s-8nv6"
RADIO_RAD_ENTORNO_KM = 45
MIN_ANIOS_R_FRECUENCIA = 10  # años mínimos para publicar la correlación anual de frecuencias de días cálidos con la estación
PERIODOS_TEND = [(1950, 2025), (1981, 2025), (1991, 2025)]
BASE = (1961, 1990)
HILOS = 4
CHIRPS_DIR = "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/global/cogs/"
CHIRPS_CACHE = os.path.join(DIR, "chirps_v3_mensual.json")
CHIRPS_VENTANA = (-76.25, 4.45, -75.60, 5.05)  # oeste, sur, este, norte: ≈ 30 km alrededor de Cartago (un bloque del COG)


def un_mes(m):
    return m + np.timedelta64(1, "M")


def dias_mes(m):
    return int((un_mes(m).astype("datetime64[D]") - m.astype("datetime64[D]")).astype(int))


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ descargas

def _get(url, params, timeout=(30, 600), intentos=4):
    ultimo = None
    for i in range(intentos):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            if r.status_code == 200:
                return r
            ultimo = f"HTTP {r.status_code}: {r.text[:300]}"
            espera = 65 if r.status_code == 429 else 5 * (i + 1)  # 429: límite por minuto de Open-Meteo
        except requests.RequestException as e:  # red lenta: reintenta
            ultimo = repr(e)
            espera = 5 * (i + 1)
        log(f"   intento {i + 1}/{intentos} falló: {ultimo}")
        if i < intentos - 1:
            time.sleep(espera)
    raise RuntimeError(f"no se pudo descargar {url}: {ultimo}")


def hoy_bogota():
    return (datetime.now(timezone.utc) - timedelta(hours=5)).date()


def descargar_openmeteo(modelo, inicio, fin, variables, ruta, forzar=False, extra=None, lat=LAT, lon=LON, clave="daily"):
    """Descarga (o lee de la caché) una petición a la Historical Weather API y guarda la solicitud junto a la respuesta.

    clave: 'daily' o 'hourly' (agregación pedida)."""
    if os.path.exists(ruta) and not forzar:
        return json.load(open(ruta, encoding="utf-8"))
    log(f"  descargando {modelo} {clave} {inicio}→{fin} ({os.path.basename(ruta)})")
    p = {"latitude": lat, "longitude": lon, "start_date": inicio, "end_date": fin,
         clave: ",".join(variables), "models": modelo, "timezone": TZ} | (extra or {})
    d = _get(API, p).json()
    lista = d if isinstance(d, list) else [d]
    if any(clave not in x for x in lista):
        raise RuntimeError(f"respuesta sin '{clave}': {str(d)[:300]}")
    envoltura = {"respuestas": lista} if isinstance(d, list) else d
    envoltura["_solicitud"] = {"url": API, "parametros": p, "fecha_descarga": hoy_bogota().isoformat()}
    comun.guardar_json(ruta, envoltura)
    return envoltura


VARS_H = ["temperature_2m", "relative_humidity_2m"]
ANIO_FIN_BLOQUES = 2024  # 1950–2024 en bloques de 5 años; desde 2025, un archivo por año (el año en curso se renueva)


def bloques_horarios():
    hoy = hoy_bogota()
    ayer = (hoy - timedelta(days=1)).isoformat()
    b = [(f"{a}-01-01", f"{min(a + 4, ANIO_FIN_BLOQUES)}-12-31") for a in range(1950, ANIO_FIN_BLOQUES + 1, 5)]
    b += [(f"{a}-01-01", f"{a}-12-31" if a < hoy.year else ayer) for a in range(ANIO_FIN_BLOQUES + 1, hoy.year + 1)]
    return b


def descargar_horario(forzar_actual=False, modelo="era5_land", variables=VARS_H, desde=1950):
    """Temperatura y humedad relativa HORARIAS (hora local) de la misma celda, por bloques, en caché.

    Hace falta para filtrar los picos espurios de una hora de ERA5-Land antes de agregar a día (ver filtrar_picos)."""
    anio_hoy = hoy_bogota().year
    partes = []
    for ini, fin in bloques_horarios():
        if int(fin[:4]) < desde:
            continue
        nombre = f"{modelo}_horario_{ini[:4]}_{fin[:4]}.json"
        forzar = forzar_actual and int(fin[:4]) == anio_hoy
        ruta = os.path.join(DIR, nombre)
        nuevo = forzar or not os.path.exists(ruta)
        d = descargar_openmeteo(modelo, ini, fin, variables, ruta, forzar, extra={"timeformat": "unixtime"}, clave="hourly")
        if nuevo:
            time.sleep(5)  # Open-Meteo pondera las peticiones largas como varias llamadas: se espacian
        partes.append(d)
    return partes


def a_arreglos(d):
    t = np.array(d["daily"]["time"], dtype="datetime64[D]")
    v = {k: np.array([np.nan if x is None else x for x in vals], dtype=float)
         for k, vals in d["daily"].items() if k != "time"}
    return t, v


def recortar_cola(t, v, clave):
    """Quita los días finales sin dato (la API devuelve null después del último día disponible)."""
    ok = np.where(np.isfinite(v[clave]))[0]
    if ok.size == 0:
        return t[:0], {k: a[:0] for k, a in v.items()}
    n = ok[-1] + 1
    return t[:n], {k: a[:n] for k, a in v.items()}


def cargar_horario(partes, meta_ref=None):
    """Concatena bloques horarios (unixtime + desfase local) y recorta a días locales completos."""
    t, T, H = [], [], []
    for d in partes:
        if meta_ref is not None:
            assert abs(d["latitude"] - meta_ref["latitude"]) < 1e-3 and abs(d["longitude"] - meta_ref["longitude"]) < 1e-3, \
                "la celda horaria no coincide con la diaria"
            assert abs(d["elevation"] - meta_ref["elevation"]) < 1, "la elevación horaria no coincide con la diaria"
        t.append(np.array(d["hourly"]["time"], dtype=np.int64) + int(d["utc_offset_seconds"]))
        T.append(np.array([np.nan if x is None else x for x in d["hourly"]["temperature_2m"]], float))
        H.append(np.array([np.nan if x is None else x for x in d["hourly"]["relative_humidity_2m"]], float))
    t, T, H = np.concatenate(t), np.concatenate(T), np.concatenate(H)
    assert np.all(np.diff(t) == 3600), "la serie horaria tiene huecos o duplicados"
    assert t[0] % 86400 == 0, "la serie horaria no empieza a las 00 h locales"
    n = (np.nonzero(np.isfinite(T))[0][-1] + 1) // 24 * 24  # solo días locales completos
    t, T, H = t[:n], T[:n], H[:n]
    assert np.isfinite(T).all() and np.isfinite(H).all(), "faltan horas dentro de la serie horaria"
    dias = (t[::24] // 86400).astype("datetime64[D]")
    return dias, T.reshape(-1, 24), H.reshape(-1, 24)


PICO_CURV = 2.5   # °C: la hora supera en más de esto a la media de sus dos vecinas
PICO_HR = -5.0    # puntos de HR: y la humedad cae a la vez por debajo de la media de sus vecinas
PICO_PASADAS = 3


def curvatura(x):
    """x[h] − (x[h−1] + x[h+1]) / 2 sobre la serie continua (NaN en los extremos)."""
    c = np.full(x.size, np.nan)
    c[1:-1] = x[1:-1] - (x[:-2] + x[2:]) / 2
    return c


def filtrar_picos(T24, H24, umbral=PICO_CURV, umbral_hr=PICO_HR, pasadas=PICO_PASADAS, exigir_hr=True, criterio="curvatura"):
    """Detecta y repara picos espurios de una hora en la temperatura horaria de ERA5-Land.

    criterio='curvatura' (el del producto): T[h] − (T[h−1]+T[h+1])/2 > umbral y, si exigir_hr, HR[h] − (HR[h−1]+HR[h+1])/2
    < umbral_hr. criterio='vecina_max' (el del revisor, para sensibilidad): T[h] − max(T[h−1], T[h+1]) > umbral.
    La hora marcada (T y HR) se reemplaza por la media de sus vecinas; se repite hasta `pasadas` veces porque la hora
    siguiente al pico a veces conserva parte del exceso. Devuelve (T, H filtradas, lista de eventos)."""
    T = T24.ravel().copy()
    H = H24.ravel().copy()
    eventos = []
    for p in range(pasadas):
        if criterio == "curvatura":
            m = curvatura(T) > umbral
        else:
            m = np.zeros(T.size, bool)
            m[1:-1] = T[1:-1] - np.maximum(T[:-2], T[2:]) > umbral
        if exigir_hr:
            m &= curvatura(H) < umbral_hr
        idx = np.nonzero(m)[0]
        if idx.size == 0:
            break
        nT = (T[idx - 1] + T[idx + 1]) / 2
        nH = (H[idx - 1] + H[idx + 1]) / 2
        for i, a, b, ha, hb in zip(idx, T[idx], nT, H[idx], nH):
            eventos.append({"i": int(i), "pasada": p + 1, "t_original": float(a), "t_reparada": float(b),
                            "hr_original": float(ha), "hr_reparada": float(hb)})
        T[idx], H[idx] = nT, nH
    return T.reshape(-1, 24), H.reshape(-1, 24), eventos


def cargar_reanalisis(forzar):
    hoy = hoy_bogota()
    ayer = (hoy - timedelta(days=1)).isoformat()
    # ERA5-Land: archivo de partida (si falta, se vuelve a pedir con los mismos parámetros) + 2026
    if not os.path.exists(ERA5L_HIST):
        log("   AVISO: falta el archivo de partida; se descarga con la misma petición (Open-Meteo, models=era5_land)")
        descargar_openmeteo("era5_land", "1950-01-01", "2025-12-31", VARS_PARTIDA, ERA5L_HIST)
    dh = json.load(open(ERA5L_HIST, encoding="utf-8"))
    th, vh = a_arreglos(dh)
    meta_l = {k: dh[k] for k in ("latitude", "longitude", "elevation", "timezone")}
    nulos_hist = {k: int(np.isnan(a).sum()) for k, a in vh.items()}
    d26 = descargar_openmeteo("era5_land", "2026-01-01", ayer, VARS_L, os.path.join(DIR, "era5land_2026.json"), forzar)
    t26, v26 = recortar_cola(*a_arreglos(d26), "temperature_2m_mean")
    assert abs(d26["latitude"] - dh["latitude"]) < 1e-3 and abs(d26["longitude"] - dh["longitude"]) < 1e-3, \
        "la celda ERA5-Land de 2026 no coincide con la del archivo de partida"
    assert abs(d26["elevation"] - dh["elevation"]) < 1, "la elevación de downscaling de 2026 no coincide"
    tl = np.concatenate([th, t26])
    vl = {k: np.concatenate([vh[k], v26[k]]) for k in VARS_L}
    # ERA5 (precipitación, radiación y contraste de temperatura)
    bloques = [("1950-01-01", "1974-12-31"), ("1975-01-01", "1999-12-31"), ("2000-01-01", "2025-12-31"),
               ("2026-01-01", ayer)]
    partes = []
    meta_e = None
    for ini, fin in bloques:
        nombre = f"era5_{ini[:4]}_{fin[:4]}.json" if not ini.startswith("2026") else "era5_2026.json"
        de = descargar_openmeteo("era5", ini, fin, VARS_E, os.path.join(DIR, nombre),
                                 forzar and ini.startswith("2026"))
        meta_e = meta_e or {k: de[k] for k in ("latitude", "longitude", "elevation", "timezone")}
        assert abs(de["latitude"] - meta_e["latitude"]) < 1e-3 and abs(de["longitude"] - meta_e["longitude"]) < 1e-3
        partes.append(a_arreglos(de))
    te = np.concatenate([p[0] for p in partes])
    ve = {k: np.concatenate([p[1][k] for p in partes]) for k in VARS_E}
    te, ve = recortar_cola(te, ve, "precipitation_sum")
    for t in (tl, te):
        assert np.all(np.diff(t).astype(int) == 1), "la serie diaria tiene huecos o duplicados"
    return (tl, vl, meta_l, nulos_hist, t26), (te, ve, meta_e)


def elevacion_modelo(tl, vl, meta_l):
    """Pide 2020 sin downscaling (elevation=nan) para documentar la corrección de altitud de Open-Meteo."""
    d = descargar_openmeteo("era5_land", "2020-01-01", "2020-12-31", ["temperature_2m_mean"],
                            os.path.join(DIR, "era5land_2020_sin_downscaling.json"), extra={"elevation": "nan"})
    al = partes_fecha(tl)[0]
    t_corr = float(np.mean(vl["temperature_2m_mean"][al == 2020]))
    t_mod = float(np.nanmean([x for x in d["daily"]["temperature_2m_mean"] if x is not None]))
    el_mod = float(d["elevation"])
    grad = (t_corr - t_mod) / ((el_mod - meta_l["elevation"]) / 1000.0) if el_mod != meta_l["elevation"] else None
    return {"elevacion_modelo_m": el_mod, "tmedia_2020_corregida": r(t_corr), "tmedia_2020_sin_corregir": r(t_mod),
            "gradiente_aplicado_c_por_km": r(grad, 2), "celda_sin_downscaling": [d["latitude"], d["longitude"]]}


def celdas_vecinas(tl, tm_producto, elev):
    """ERA5-Land 1991–2020 en las 4 celdas de 0,1° que tocan la rejilla de BioMap, TODAS corregidas a la misma
    elevación que la serie del producto (elevation=919), para que la diferencia sea solo entre celdas.

    tm_producto: temperatura media diaria de la serie del producto SIN filtrar (para comprobar que la celda principal
    coincide con ella)."""
    lats, lons = [4.7, 4.7, 4.8, 4.8], [-76.0, -75.9, -76.0, -75.9]
    d = descargar_openmeteo("era5_land", "1991-01-01", "2020-12-31", ["temperature_2m_mean"],
                            os.path.join(DIR, f"era5land_celdas_vecinas_1991_2020_elev{int(elev)}.json"),
                            extra={"latitude": ",".join(map(str, lats)), "longitude": ",".join(map(str, lons)),
                                   "elevation": ",".join([str(int(elev))] * 4), "cell_selection": "nearest"})
    al = partes_fecha(tl)[0]
    s = (al >= 1991) & (al <= 2020)
    ref = float(np.mean(tm_producto[s]))
    filas = []
    for x in d["respuestas"]:
        t, v = a_arreglos(x)
        anio = partes_fecha(t)[0]
        tm = v["temperature_2m_mean"]
        tm_anual = np.array([np.mean(tm[anio == a]) for a in range(1991, 2021)])
        ts = stats.theilslopes(tm_anual, np.arange(1991, 2021))
        fila = {"lat": round(x["latitude"], 3), "lon": round(x["longitude"], 3), "elevacion_m": x["elevation"],
                "tmedia_1991_2020": r(np.mean(tm)), "diferencia_vs_serie_del_producto": r(np.mean(tm) - ref),
                "sen_tmedia_por_decada_1991_2020": r(ts[0] * 10, 3)}
        if abs(x["latitude"] - 4.7) < 0.01 and abs(x["longitude"] + 75.9) < 0.01:
            _, i, j = np.intersect1d(t, tl, return_indices=True)
            fila["celda_del_producto"] = True
            fila["max_dif_diaria_vs_serie_del_producto"] = r(np.max(np.abs(tm[i] - tm_producto[j])), 3)
        filas.append(fila)
    return {"elevacion_comun_m": elev, "tmedia_1991_2020_serie_del_producto_sin_filtrar": r(ref), "celdas": filas,
            "nota": ("Media diaria de ERA5-Land 1991–2020 (sin filtro de picos, que no altera la media de forma apreciable) en las cuatro "
                     "celdas, todas corregidas por Open-Meteo a la misma elevación que la serie del producto; así la diferencia refleja la "
                     "celda y no la altitud. La celda del producto reproduce su serie diaria.")}


def fraccion_urbana_en_celda(lat_c, lon_c, paso=0.1):
    """Fracción del área de las zonas urbanas (Comunas 1–7 y Zaragoza) dentro de la celda de 0,1° centrada en (lat_c, lon_c)."""
    from shapely.geometry import box
    from shapely.ops import unary_union
    u = unary_union([z["geom"] for z in comun.comunas()])
    celda = box(lon_c - paso / 2, lat_c - paso / 2, lon_c + paso / 2, lat_c + paso / 2)
    return u.intersection(celda).area / u.area


# ------------------------------------------------------------------ CHIRPS v3 (lluvia mensual de referencia)

def _chirps_listado():
    import re
    html = _get(CHIRPS_DIR, {}, timeout=(30, 120)).text
    return sorted(set(re.findall(r"chirps-v3\.0\.(\d{4})\.(\d{2})\.cog", html)))


def _chirps_leer(anio, mes):
    import rasterio
    from rasterio.windows import from_bounds
    url = f"/vsicurl/{CHIRPS_DIR}chirps-v3.0.{anio}.{mes}.cog"
    ultimo = None
    for i in range(4):
        try:
            # comun.py no incluye la extensión .cog entre las permitidas para /vsicurl/: se agrega aquí
            with rasterio.Env(CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".cog,.tif", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                              GDAL_HTTP_MAX_RETRY="4", GDAL_HTTP_RETRY_DELAY="2"):
                with rasterio.open(url) as s:
                    w = from_bounds(*CHIRPS_VENTANA, transform=s.transform).round_offsets().round_lengths()
                    a = s.read(1, window=w).astype(float)
                    t = s.window_transform(w)
            a[a < 0] = np.nan
            return a, t
        except Exception as e:  # red lenta: reintenta
            ultimo = e
            time.sleep(4 * (i + 1))
    raise RuntimeError(f"CHIRPS {anio}-{mes}: {ultimo}")


def chirps_mensual(actualizar=False):
    """Lee (o recupera de la caché) la ventana de CHIRPS v3 de cada mes disponible.

    Devuelve (meses 'AAAA-MM', cubo (n, filas, cols) en mm/mes, transform de la ventana, fallos)."""
    cache = json.load(open(CHIRPS_CACHE, encoding="utf-8")) if os.path.exists(CHIRPS_CACHE) else {"meses": {}}
    try:
        disponibles = _chirps_listado()
    except Exception as e:
        log(f"   AVISO: no se pudo listar CHIRPS ({e}); se usa la caché")
        disponibles = [tuple(k.split("-")) for k in cache["meses"]]
    claves = [f"{a}-{m}" for a, m in disponibles]
    faltan = [k for k in claves if k not in cache["meses"]]
    if actualizar:  # los últimos meses pueden revisarse
        faltan = sorted(set(faltan) | set(claves[-3:]))
    fallos = []
    if faltan:
        log(f"   CHIRPS: leyendo {len(faltan)} meses por ventana …")
        with ThreadPoolExecutor(6) as ex:
            fut = {ex.submit(_chirps_leer, *k.split("-")): k for k in faltan}
            for i, f in enumerate(as_completed(fut), 1):
                k = fut[f]
                try:
                    a, t = f.result()
                    tr = [t.a, t.b, t.c, t.d, t.e, t.f]
                    if "transform" in cache and not np.allclose(cache["transform"], tr, atol=1e-6):
                        raise RuntimeError(f"ventana distinta en {k}")
                    cache["transform"] = tr
                    cache["meses"][k] = [[None if not np.isfinite(x) else round(float(x), 2) for x in fila] for fila in a]
                except Exception as e:
                    fallos.append(f"{k}: {e}")
                if i % 50 == 0:
                    log(f"     {i}/{len(faltan)}")
                    comun.guardar_json(CHIRPS_CACHE, cache | {"fuente": CHIRPS_DIR, "ventana": CHIRPS_VENTANA})
        cache.update({"fuente": CHIRPS_DIR, "ventana": CHIRPS_VENTANA, "fecha_lectura": hoy_bogota().isoformat()})
        comun.guardar_json(CHIRPS_CACHE, cache)
    if not cache["meses"]:
        return None
    meses = sorted(cache["meses"])
    cubo = np.array([[[np.nan if x is None else x for x in fila] for fila in cache["meses"][k]] for k in meses], float)
    from affine import Affine
    return meses, cubo, Affine(*cache["transform"]), sorted(fallos)


def pesos_urbanos(transform, forma):
    """Fracción del área urbana (Comunas 1–7 y Zaragoza) en cada píxel de la ventana; suma 1."""
    from shapely.geometry import box
    from shapely.ops import unary_union
    u = unary_union([z["geom"] for z in comun.comunas()])
    w = np.zeros(forma)
    for i in range(forma[0]):
        for j in range(forma[1]):
            x0, y0 = transform * (j, i)
            x1, y1 = transform * (j + 1, i + 1)
            w[i, j] = u.intersection(box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))).area
    return w / w.sum()


def pixel(transform, lat, lon):
    col, fila = ~transform * (lon, lat)
    return int(math.floor(fila)), int(math.floor(col))


# ------------------------------------------------------------------ NASA POWER (radiación de referencia)

def power_mensual(actualizar=False):
    """Irradiancia solar global en superficie mensual de NASA POWER (ALLSKY_SFC_SW_DWN, kWh/m²/día), 1984 → último año completo.

    Devuelve (dict 'AAAA-MM' → valor, metadatos). Fuentes de POWER: GEWEX SRB (1984–2000) y CERES SYN1deg (2001→), 1°."""
    ruta = os.path.join(DIR, "nasa_power_mensual.json")
    fin = hoy_bogota().year - 1
    if os.path.exists(ruta) and not actualizar:
        d = json.load(open(ruta, encoding="utf-8"))
    else:
        p = {"parameters": "ALLSKY_SFC_SW_DWN,CLRSKY_SFC_SW_DWN", "community": "RE", "longitude": LON, "latitude": LAT,
             "start": 1984, "end": fin, "format": "JSON"}
        d = _get(POWER_API, p, timeout=(30, 300)).json()
        d["_solicitud"] = {"url": POWER_API, "parametros": p, "fecha_descarga": hoy_bogota().isoformat()}
        comun.guardar_json(ruta, d)
    fill = d["header"].get("fill_value", -999.0)
    par = d["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
    serie = {f"{k[:4]}-{k[4:]}": (None if v is None or v == fill else float(v)) for k, v in par.items() if k[4:] != "13"}
    coords = d["geometry"]["coordinates"]
    meta = {"api": d["header"]["api"], "fuentes": d["header"]["sources"], "unidades": d["parameters"]["ALLSKY_SFC_SW_DWN"]["units"],
            "punto": coords[:2], "solicitud": d.get("_solicitud"),
            # la cabecera CSV de la misma API dice «Elevation from MERRA-2: Average for 0.5 x 0.625 degree lat/lon region»
            "elevacion_media_celda_merra2_m": r(coords[2], 0) if len(coords) > 2 else None}
    return serie, meta


# ------------------------------------------------------------------ IDEAM (validación)

def socrata(dataset, params, ruta, forzar=False, timeout=(30, 300), intentos=4):
    if os.path.exists(ruta) and not forzar:
        return json.load(open(ruta, encoding="utf-8"))
    r = _get(f"{SOCRATA}/{dataset}.json", params, timeout=timeout, intentos=intentos)
    d = r.json()
    if not isinstance(d, list):
        raise RuntimeError(f"respuesta inesperada de {dataset}: {str(d)[:200]}")
    comun.guardar_json(ruta, d)
    return d


def _ideam_anio(var, anio, forzar):
    ds, f = IDEAM_DS[var]
    params = {
        "$select": f"date_trunc_ymd(fechaobservacion) as dia,{f}(valorobservado::number) as v,count(*) as n",
        "$where": (f"codigoestacion='{EST_ZARAGOZA['codigo']}' AND fechaobservacion between "
                   f"'{anio}-01-01T00:00:00' and '{anio}-12-31T23:59:59'"),
        "$group": "dia", "$order": "dia", "$limit": 1000,
    }
    return socrata(ds, params, os.path.join(DIR_IDEAM, f"zaragoza_{var}_{anio}.json"), forzar)


def ideam_estacion_diaria(forzar_anio_actual=False):
    """Agregados diarios de la estación IDEAM Zaragoza, un año por consulta y en hilos.

    Devuelve (dict var → (fechas, valor, n, dataset), lista de fallos)."""
    anio_hoy = hoy_bogota().year
    tareas = [(v, a) for v in IDEAM_DS for a in range(IDEAM_DESDE, anio_hoy + 1)]
    res, fallos = {}, []
    with ThreadPoolExecutor(HILOS) as ex:
        fut = {ex.submit(_ideam_anio, v, a, forzar_anio_actual and a == anio_hoy): (v, a) for v, a in tareas}
        for f in as_completed(fut):
            v, a = fut[f]
            try:
                res[(v, a)] = f.result()
            except Exception as e:  # la validación no es imprescindible: se registra y se sigue
                fallos.append(f"{v} {a}: {e}")
    out = {}
    for var, (ds, _) in IDEAM_DS.items():
        filas = [x for a in range(IDEAM_DESDE, anio_hoy + 1) for x in res.get((var, a), []) if x.get("v") is not None]
        if not filas:
            continue
        f_ = np.array([x["dia"][:10] for x in filas], dtype="datetime64[D]")
        v_ = np.array([float(x["v"]) for x in filas])
        n_ = np.array([int(x["n"]) for x in filas])
        out[var] = (f_, v_, n_, ds)
    return out, sorted(fallos)


def ideam_radiacion(forzar=False):
    """Climatología mensual y anual MEDIDA de la radiación global (Wh/m²/día) de las estaciones IDEAM con sensor calibrado
    (datos.gov.co rv9s-8nv6, CC BY-SA 4.0): tabla completa (≈ 170 filas) y metadatos del conjunto, en caché.

    El conjunto no publica el periodo de la climatología ni el código de las estaciones."""
    filas = socrata(IDEAM_RAD_DS, {"$limit": 5000}, os.path.join(DIR_IDEAM, f"radiacion_global_{IDEAM_RAD_DS}.json"), forzar)
    ruta_m = os.path.join(DIR_IDEAM, f"radiacion_global_{IDEAM_RAD_DS}_metadatos.json")
    meta = None
    if os.path.exists(ruta_m) and not forzar:
        meta = json.load(open(ruta_m, encoding="utf-8"))
    else:
        try:
            m = _get(f"https://www.datos.gov.co/api/views/{IDEAM_RAD_DS}.json", {}, timeout=(30, 120), intentos=2).json()
            iso = lambda t: datetime.fromtimestamp(t, timezone.utc).date().isoformat() if t else None  # noqa: E731
            meta = {"nombre": m.get("name"), "descripcion": m.get("description"), "atribucion": m.get("attribution"),
                    "licencia": (m.get("license") or {}).get("name"), "fecha_publicacion": iso(m.get("publicationDate")),
                    "fecha_actualizacion_filas": iso(m.get("rowsUpdatedAt")),
                    "frecuencia_actualizacion": (((m.get("metadata") or {}).get("custom_fields") or {}).get("Información de Datos") or {})
                    .get("Frecuencia de Actualización"),
                    "url": f"https://www.datos.gov.co/resource/{IDEAM_RAD_DS}", "fecha_consulta": hoy_bogota().isoformat()}
            comun.guardar_json(ruta_m, meta)
        except Exception as e:  # los metadatos no son imprescindibles
            log(f"   AVISO: sin metadatos de {IDEAM_RAD_DS}: {e}")
    return filas, meta


def ideam_normales(forzar=False):
    # caja de ≈ 45 km alrededor de Cartago: incluye Matecaña (Pereira) y El Edén (Armenia) para el contraste de tendencias
    params = {"$limit": 5000,
              "$where": "latitud::number between 4.40 and 5.10 AND longitud::number between -76.25 and -75.55"}
    return socrata("nsz2-kzcq", params, os.path.join(DIR, "ideam_normales_entorno_v2.json"), forzar)


def distancia_km(lat1, lon1, lat2, lon2):
    rt = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * rt * math.asin(math.sqrt(a))


# ------------------------------------------------------------------ utilidades

def partes_fecha(t):
    anio = t.astype("datetime64[Y]").astype(int) + 1970
    mes = t.astype("datetime64[M]").astype(int) % 12 + 1
    dia = (t - t.astype("datetime64[M]")).astype(int) + 1
    doy = (t - t.astype("datetime64[Y]")).astype(int)
    return anio, mes, dia, doy


def indice_365(t):
    """Índice de día del calendario 0..364 (29 de febrero → índice del 28) y máscara del 29 de febrero."""
    anio, mes, dia, doy = partes_fecha(t)
    bis = ((anio % 4 == 0) & (anio % 100 != 0)) | (anio % 400 == 0)
    idx = doy.copy()
    idx[bis & (doy >= 59)] -= 1
    return idx, (mes == 2) & (dia == 29)


def r(x, nd=2):
    if x is None:
        return None
    x = float(x)
    return None if not math.isfinite(x) else round(x, nd)


def sig(x, n=3):
    """Redondeo a n cifras significativas (para valores p muy pequeños)."""
    if x is None or not math.isfinite(float(x)):
        return None
    return float(f"{float(x):.{n}g}")


def rl(a, nd=2):
    return [r(x, nd) for x in a]


def fmt(x, nd=2, signo=True):
    if x is None:
        return "s. d."
    return f"{x:+.{nd}f}" if signo else f"{x:.{nd}f}"


def fmt_p(p):
    if p is None:
        return "s. d."
    return "< 0,001" if p < 0.001 else f"{p:.3f}"


# ------------------------------------------------------------------ percentiles ETCCDI

class Percentil90:
    """Umbral del percentil 90 por día del calendario (ventana de 5 días, base 1961–1990) con bootstrap."""

    def __init__(self, t, x, base=BASE, q=0.9):
        anio, _, _, _ = partes_fecha(t)
        idx, f29 = indice_365(t)
        self.q = q
        self.anios_base = list(range(base[0], base[1] + 1))
        sel = (anio >= base[0]) & (anio <= base[1]) & ~f29
        serie = x[sel]
        nb = len(self.anios_base)
        assert serie.size == nb * 365 and np.isfinite(serie).all(), "el periodo base no está completo"
        # ventana centrada de 5 días; solo datos del periodo base (los extremos de 1961 y 1990 quedan con 3–4 valores)
        pad = np.concatenate([[np.nan, np.nan], serie, [np.nan, np.nan]])
        w = np.lib.stride_tricks.sliding_window_view(pad, 5)
        self.W = w.reshape(nb, 365, 5)
        self.umbral = self._umbral(list(range(nb)))
        self.t, self.x, self.anio, self.idx = t, x, anio, idx

    def _umbral(self, filas):
        v = self.W[filas].transpose(1, 0, 2).reshape(365, -1)
        return np.nanquantile(v, self.q, axis=1, method="median_unbiased")

    def excedencias_anuales(self, anios):
        """dict año → (días que superan, días válidos, porcentaje)."""
        res = {}
        nb = len(self.anios_base)
        for a in anios:
            m = (self.anio == a) & np.isfinite(self.x)
            if not m.any():
                res[a] = (None, 0, None)
                continue
            xv, iv = self.x[m], self.idx[m]
            if a in self.anios_base:
                # Zhang et al. (2005): se quita el año a de la base, se reemplaza por cada uno de los otros 29
                # años, se cuenta con cada umbral y se promedia.
                j = self.anios_base.index(a)
                cuentas = []
                for k in range(nb):
                    if k == j:
                        continue
                    filas = list(range(nb))
                    filas[j] = k
                    cuentas.append(np.sum(xv > self._umbral(filas)[iv]))
                c = float(np.mean(cuentas))
            else:
                c = float(np.sum(xv > self.umbral[iv]))
            res[a] = (c, int(m.sum()), 100.0 * c / m.sum())
        return res


# ------------------------------------------------------------------ tendencias

def mann_kendall(y):
    n = len(y)
    s = 0.0
    for i in range(n - 1):
        s += np.sign(y[i + 1:] - y[i]).sum()
    _, cuentas = np.unique(y, return_counts=True)
    var = (n * (n - 1) * (2 * n + 5) - np.sum(cuentas * (cuentas - 1) * (2 * cuentas + 5))) / 18.0
    z = (s - 1) / math.sqrt(var) if s > 0 else ((s + 1) / math.sqrt(var) if s < 0 else 0.0)
    p = 2 * stats.norm.sf(abs(z))  # sf en lugar de 1 − cdf: evita que p muy pequeños se redondeen a 0
    return s, z, p, s / (n * (n - 1) / 2)


def tendencia(anios, valores, escala=10.0):
    x = np.asarray(anios, float)
    y = np.asarray(valores, float)
    m = np.isfinite(y)
    x, y = x[m], y[m]
    n = len(y)
    if n < 10:
        return None
    lr = stats.linregress(x, y)
    tc = stats.t.ppf(0.975, n - 2)
    res = y - (lr.intercept + lr.slope * x)
    r1 = float(np.corrcoef(res[:-1], res[1:])[0, 1])
    neff = n * (1 - r1) / (1 + r1) if r1 > 0 else float(n)
    if neff > 3:
        se_a = lr.stderr * math.sqrt((n - 2) / (neff - 2))
        tca = stats.t.ppf(0.975, neff - 2)
        ic_a = [(lr.slope - tca * se_a) * escala, (lr.slope + tca * se_a) * escala]
        p_a = float(2 * stats.t.sf(abs(lr.slope / se_a), neff - 2))
    else:
        ic_a, p_a = [None, None], None
    ts = stats.theilslopes(y, x, alpha=0.95)
    s, z, p_mk, tau = mann_kendall(y)
    return {
        "n_anios": n, "desde": int(x[0]), "hasta": int(x[-1]),
        "ols_por_decada": r(lr.slope * escala, 4),
        "ols_ic95": [r((lr.slope - tc * lr.stderr) * escala, 4), r((lr.slope + tc * lr.stderr) * escala, 4)],
        "ols_p": sig(lr.pvalue), "r2": r(lr.rvalue ** 2, 3),
        "ar1_residuos": r(r1, 3), "n_efectivo": r(neff, 1),
        "ols_ic95_ajustado_ar1": [r(ic_a[0], 4), r(ic_a[1], 4)], "ols_p_ajustado_ar1": sig(p_a),
        "sen_por_decada": r(ts[0] * escala, 4), "sen_ic95": [r(ts[2] * escala, 4), r(ts[3] * escala, 4)],
        "mk_s": int(s), "mk_z": r(z, 3), "mk_p": sig(p_mk), "kendall_tau": r(tau, 3),
        "significativa_5pct": bool(lr.pvalue < 0.05 and p_mk < 0.05),
        "significativa_5pct_ajustada_ar1": bool(p_a is not None and p_a < 0.05 and p_mk < 0.05),
    }


# ------------------------------------------------------------------ agregación

def anual(tl, vl, te, ve, p90x, p90n, umbrales, ch, pw=None):
    """Tabla anual. umbrales: {'eq32': float|None, 'local': float}; ch: dict 'AAAA-MM' → lluvia CHIRPS (mm) o None;
    pw: dict 'AAAA-MM' → radiación NASA POWER (kWh/m²/día) o None."""
    al, _, _, _ = partes_fecha(tl)
    ae, _, _, _ = partes_fecha(te)
    anios = list(range(int(al.min()), int(al.max()) + 1))
    exx = p90x.excedencias_anuales(anios)
    exn = p90n.excedencias_anuales(anios)
    P = ve["precipitation_sum"]
    # suma de 5 días que termina en cada día (ETCCDI); exige los 5 días con dato
    s5 = np.full(P.size, np.nan)
    c = np.convolve(np.nan_to_num(P), np.ones(5), "valid")
    ok = np.convolve(np.isfinite(P).astype(float), np.ones(5), "valid") == 5
    s5[4:] = np.where(ok, c, np.nan)
    col = {k: [] for k in ["anio", "parcial", "hasta", "tmedia", "tmax_media", "tmin_media", "txx", "tnn",
                           "precip_total", "precip_chirps", "rx1day", "rx5day", "dias_tx90p", "pct_tx90p", "noches_tn90p",
                           "pct_tn90p", "dias_tmax_ge_32", "dias_tmax_ge_umbral_eq32", "dias_tmax_gt_umbral_local",
                           "radiacion_kwh_m2_dia", "radiacion_power_kwh_m2_dia", "humedad_media", "completitud", "completitud_era5land",
                           "completitud_era5", "meses_chirps"]}
    for a in anios:
        ml = al == a
        me = ae == a
        ndias = 366 if (a % 4 == 0 and (a % 100 != 0 or a % 400 == 0)) else 365
        tm, tx, tn, hr = (vl[k][ml] for k in VARS_L)
        pr, rad = P[me], ve["shortwave_radiation_sum"][me]
        comp_l = np.isfinite(tm).sum() / ndias
        comp_e = np.isfinite(pr).sum() / ndias
        col["anio"].append(a)
        col["parcial"].append(bool(comp_l < 1 or comp_e < 1))
        col["hasta"].append(str(tl[ml][np.isfinite(tm)][-1]) if np.isfinite(tm).any() else None)
        col["tmedia"].append(r(np.nanmean(tm)))
        col["tmax_media"].append(r(np.nanmean(tx)))
        col["tmin_media"].append(r(np.nanmean(tn)))
        col["txx"].append(r(np.nanmax(tx), 1))
        col["tnn"].append(r(np.nanmin(tn), 1))
        hay_p = np.isfinite(pr).any()
        col["precip_total"].append(r(np.nansum(pr), 1) if hay_p else None)
        vals_ch = [ch.get(f"{a}-{m:02d}") for m in range(1, 13)] if ch else []
        vals_ch = [x for x in vals_ch if x is not None]
        col["meses_chirps"].append(len(vals_ch))
        col["precip_chirps"].append(r(sum(vals_ch), 1) if len(vals_ch) == 12 else None)  # solo años con los 12 meses
        col["rx1day"].append(r(np.nanmax(pr), 1) if hay_p else None)
        col["rx5day"].append(r(np.nanmax(s5[me]), 1) if np.isfinite(s5[me]).any() else None)
        col["dias_tx90p"].append(r(exx[a][0], 1))
        col["pct_tx90p"].append(r(exx[a][2], 2))
        col["noches_tn90p"].append(r(exn[a][0], 1))
        col["pct_tn90p"].append(r(exn[a][2], 2))
        col["dias_tmax_ge_32"].append(int(np.sum(tx >= 32.0)))
        col["dias_tmax_ge_umbral_eq32"].append(int(np.sum(tx >= umbrales["eq32"])) if umbrales.get("eq32") is not None else None)
        col["dias_tmax_gt_umbral_local"].append(int(np.sum(tx > umbrales["local"])))
        col["radiacion_kwh_m2_dia"].append(r(np.nanmean(rad) / 3.6, 3) if np.isfinite(rad).any() else None)
        vals_pw = [(pw or {}).get(f"{a}-{m:02d}") for m in range(1, 13)]
        if all(x is not None for x in vals_pw):  # media ponderada por días; solo años con los 12 meses
            dm = [dias_mes(np.datetime64(f"{a}-{m:02d}")) for m in range(1, 13)]
            col["radiacion_power_kwh_m2_dia"].append(r(np.dot(vals_pw, dm) / sum(dm), 3))
        else:
            col["radiacion_power_kwh_m2_dia"].append(None)
        col["humedad_media"].append(r(np.nanmean(hr), 1))
        col["completitud"].append(r(min(comp_l, comp_e), 4))
        col["completitud_era5land"].append(r(comp_l, 4))
        col["completitud_era5"].append(r(comp_e, 4))
    return col


def mensual(tl, vl, te, ve, ch, pw=None):
    """Serie mensual: ERA5-Land (temperatura, humedad), ERA5 (lluvia, radiación), CHIRPS v3 (lluvia de referencia) y
    NASA POWER (radiación de referencia). 'parcial' = el mes no tiene todos sus días en ERA5-Land."""
    ml = tl.astype("datetime64[M]")
    me = te.astype("datetime64[M]")
    meses = np.arange(ml.min(), un_mes(ml.max()))
    out = {k: [] for k in ["mes", "dias", "dias_validos", "dias_validos_era5", "parcial", "tmedia", "tmax_media", "tmin_media",
                           "humedad_media", "precip_total", "precip_chirps", "radiacion_kwh_m2_dia", "radiacion_power_kwh_m2_dia"]}
    for m in meses:
        a = ml == m
        b = me == m
        dias = dias_mes(m)
        tm = vl["temperature_2m_mean"][a]
        pr = ve["precipitation_sum"][b]
        rad = ve["shortwave_radiation_sum"][b]
        hay = np.isfinite(tm).any()
        out["mes"].append(str(m))
        out["dias"].append(dias)
        out["dias_validos"].append(int(np.isfinite(tm).sum()))
        out["dias_validos_era5"].append(int(np.isfinite(pr).sum()))
        out["parcial"].append(bool(int(np.isfinite(tm).sum()) < dias))
        out["tmedia"].append(r(np.nanmean(tm)) if hay else None)
        out["tmax_media"].append(r(np.nanmean(vl["temperature_2m_max"][a])) if hay else None)
        out["tmin_media"].append(r(np.nanmean(vl["temperature_2m_min"][a])) if hay else None)
        out["humedad_media"].append(r(np.nanmean(vl["relative_humidity_2m_mean"][a]), 1) if hay else None)
        # total mensual solo con el mes completo
        out["precip_total"].append(r(np.sum(pr), 1) if pr.size == dias and np.isfinite(pr).all() else None)
        out["precip_chirps"].append(ch.get(str(m)) if ch else None)
        out["radiacion_kwh_m2_dia"].append(r(np.nanmean(rad) / 3.6, 3) if np.isfinite(rad).any() else None)
        out["radiacion_power_kwh_m2_dia"].append(r((pw or {}).get(str(m)), 3))
    return out


VARS_CLIM = ["tmedia", "tmax_media", "tmin_media", "humedad_media", "precip_total", "precip_chirps", "radiacion_kwh_m2_dia",
             "radiacion_power_kwh_m2_dia"]
VARS_EXTERNAS = {"precip_chirps", "radiacion_power_kwh_m2_dia"}  # series mensuales ya agregadas (completas si hay dato)
VARS_ERA5_CLIM = {"precip_total", "radiacion_kwh_m2_dia"}
VARS_LLUVIA = {"precip_total", "precip_chirps"}


def clave_anual(v):
    return {"precip_total": "precip_anual", "precip_chirps": "precip_chirps_anual"}.get(v, f"{v}_anual")


def climatologia(mens, a0, a1):
    mes = np.array(mens["mes"], dtype="datetime64[M]")
    anio = mes.astype("datetime64[Y]").astype(int) + 1970
    mm = mes.astype(int) % 12 + 1
    dias = np.array(mens["dias"])
    out = {"periodo": f"{a0}-{a1}", "mes": list(range(1, 13))}
    for v in VARS_CLIM:
        arr = np.array([np.nan if x is None else x for x in mens[v]], float)
        if v in VARS_EXTERNAS:
            completo = np.isfinite(arr)
        else:
            completo = np.array(mens["dias_validos_era5" if v in VARS_ERA5_CLIM else "dias_validos"]) == dias
        vals, nanios = [], []
        for k in range(1, 13):
            s = (anio >= a0) & (anio <= a1) & (mm == k) & completo  # solo meses completos
            x = arr[s]
            vals.append(np.nanmean(x) if np.isfinite(x).any() else np.nan)
            nanios.append(int(np.isfinite(x).sum()))
        out[v] = rl(vals, 1 if v in VARS_LLUVIA | {"humedad_media"} else 3 if v.startswith("rad") else 2)
        out[f"n_anios_{v}"] = nanios
        if v in VARS_LLUVIA:
            out[clave_anual(v)] = r(np.sum(vals), 1)
        else:
            pesos = np.array([31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
            out[clave_anual(v)] = r(np.sum(np.array(vals) * pesos) / pesos.sum(), 3 if v.startswith("rad") else 2)
    return out


def anomalias(c1, c0):
    out = {"descripcion": f"{c1['periodo']} menos {c0['periodo']}", "mes": list(range(1, 13))}
    for v in VARS_CLIM:
        a, b = np.array(c1[v], float), np.array(c0[v], float)
        out[v] = rl(a - b, 3 if v.startswith("rad") else 1 if v in VARS_LLUVIA else 2)
        k = clave_anual(v)
        out[k] = r(c1[k] - c0[k], 3 if v.startswith("rad") else 1 if v in VARS_LLUVIA else 2) if None not in (c1[k], c0[k]) else None
    for v in VARS_LLUVIA:
        out[f"{v}_pct"] = rl(100 * (np.array(c1[v], float) / np.array(c0[v], float) - 1), 1)
        out[f"{clave_anual(v)}_pct"] = r(100 * (c1[clave_anual(v)] / c0[clave_anual(v)] - 1), 1)
    return out


def era5_clim(te, ve, a0, a1):
    """Climatología anual de ERA5 (temperaturas, humedad y lluvia) para comparar con normales."""
    ae = partes_fecha(te)[0]
    s = (ae >= a0) & (ae <= a1)
    out = {"periodo": f"{a0}-{a1}"}
    for v, k in (("tmedia", "temperature_2m_mean"), ("tmax_media", "temperature_2m_max"), ("tmin_media", "temperature_2m_min"),
                 ("humedad_media", "relative_humidity_2m_mean")):
        out[f"{v}_anual"] = r(np.mean(ve[k][s]), 2)
    out["precip_anual"] = r(np.sum(ve["precipitation_sum"][s]) / (a1 - a0 + 1), 1)
    return out


# ------------------------------------------------------------------ validación

def anomalias_mensuales(fechas, *series, min_dias=20):
    """Medias mensuales (meses con ≥ min_dias días comunes) menos la media de cada mes del calendario."""
    mf = fechas.astype("datetime64[M]")
    filas = []
    for m in np.unique(mf):
        s = mf == m
        if s.sum() >= min_dias:
            filas.append([int(str(m)[5:7])] + [float(x[s].mean()) for x in series])
    if len(filas) < 24:
        return None
    a = np.array(filas)
    mn = a[:, 0].astype(int)
    return [a[:, k] - np.array([a[mn == j, k].mean() for j in mn]) for k in range(1, a.shape[1])]


def destreza_eventos(obs, mod, umbral_obs, umbral_mod, mayor_igual_obs=True):
    """Tabla de contingencia de días cálidos: evento observado (estación) frente a evento del reanálisis."""
    eo = obs >= umbral_obs if mayor_igual_obs else obs > umbral_obs
    em = mod > umbral_mod
    a = int(np.sum(eo & em))       # aciertos
    b = int(np.sum(~eo & em))      # falsas alarmas
    c = int(np.sum(eo & ~em))      # sorpresas (fallos)
    return {"dias": int(obs.size), "eventos_estacion": a + c, "eventos_reanalisis": a + b, "aciertos": a,
            "falsas_alarmas": b, "fallos": c,
            "tasa_deteccion_pod": r(a / (a + c), 3) if a + c else None,
            "tasa_falsas_alarmas_far": r(b / (a + b), 3) if a + b else None,
            "sesgo_frecuencia": r((a + b) / (a + c), 3) if a + c else None}


def homogeneidad_estacion(est, tl, vl, te, ve):
    """Diferencia media estación − reanálisis por semestre (temperatura media, máxima y mínima): un salto que aparece frente a
    los DOS reanálisis a la vez apunta a la estación (traslado, sensor), no al reanálisis."""
    reglas = {"t": ("temperature_2m_mean", 10.0, 35.0), "tx": ("temperature_2m_max", 15.0, 42.0), "tn": ("temperature_2m_min", 8.0, 28.0)}
    out = {}
    for var, (k, lo, hi) in reglas.items():
        if var not in est:
            continue
        f, v, n, _ = est[var]
        ok = (n >= 18) & (n <= 24) & (v >= lo) & (v <= hi)
        f, v = f[ok], v[ok]
        com = np.intersect1d(np.intersect1d(tl, f), te)
        xs, xl, xe = v[np.searchsorted(f, com)], vl[k][np.searchsorted(tl, com)], ve[k][np.searchsorted(te, com)]
        an, ms = partes_fecha(com)[:2]
        sem = an * 10 + (ms > 6)
        filas = [{"semestre": f"{u // 10}-{'S1' if u % 10 == 0 else 'S2'}", "dias": int(np.sum(sem == u)),
                  "estacion_menos_era5land": r(np.mean(xs[sem == u] - xl[sem == u])),
                  "estacion_menos_era5": r(np.mean(xs[sem == u] - xe[sem == u]))} for u in np.unique(sem)]
        a = com <= FIN_VALIDACION
        b = com >= np.datetime64("2025-07-01")
        out[var] = {"por_semestre": filas,
                    "hasta_2023": {"dias": int(a.sum()), "estacion_menos_era5land": r(np.mean(xs[a] - xl[a])), "estacion_menos_era5": r(np.mean(xs[a] - xe[a]))},
                    "desde_2025_07": {"dias": int(b.sum()), "estacion_menos_era5land": r(np.mean(xs[b] - xl[b])) if b.any() else None,
                                      "estacion_menos_era5": r(np.mean(xs[b] - xe[b])) if b.any() else None}}
    return out


def tx_estacion_validada(est, tl, te):
    """Tmax diaria de la estación Zaragoza con el mismo control de calidad y los mismos días comunes que validar_estacion."""
    f, v, n, _ = est["tx"]
    ok = (n >= 18) & (n <= 24) & (v >= 15.0) & (v <= 42.0)
    f, v = f[ok], v[ok]
    sel = f <= FIN_VALIDACION
    f, v = f[sel], v[sel]
    comunes = np.intersect1d(np.intersect1d(tl, f), te)
    return comunes, v[np.searchsorted(f, comunes)]


def validar_estacion(est, tl, vl, te, ve, chirps_pixel=None, umbral_local=None, umbral_local_era5=None):
    """Compara la estación IDEAM Zaragoza con ERA5-Land/ERA5 (y CHIRPS en su píxel) en los días/meses comunes.

    La temperatura se compara hasta FIN_VALIDACION (la estación cambia de nivel tras su hueco de 2023–2025 y ERA5 cambia su
    ciclo diurno desde mayo de 2025) y con los MISMOS días para los dos reanálisis. Devuelve (bloque, umbral de ERA5-Land equivalente a 32 °C en la estación)."""
    out = {"estacion": EST_ZARAGOZA | {"distancia_al_centro_km": r(distancia_km(LAT, LON, EST_ZARAGOZA["lat"], EST_ZARAGOZA["lon"]), 1)},
           "periodo_temperatura": (f"días comunes hasta {FIN_VALIDACION} (los mismos para ERA5-Land y ERA5): la estación cambia de nivel "
                                   "después de su hueco de 2023–2025 (ver homogeneidad_estacion) y ERA5 cambia su ciclo diurno desde mayo de 2025"),
           "homogeneidad_estacion": homogeneidad_estacion(est, tl, vl, te, ve)}
    reglas = {"tx": (18, 15.0, 42.0), "tn": (18, 8.0, 28.0), "t": (18, 10.0, 35.0)}
    pares = {"tx": "temperature_2m_max", "tn": "temperature_2m_min", "t": "temperature_2m_mean"}
    umbral = None
    for var, (nmin, lo, hi) in reglas.items():
        if var not in est:
            continue
        f, v, n, ds = est[var]
        ok = (n >= nmin) & (n <= 24) & (v >= lo) & (v <= hi)
        f, v = f[ok], v[ok]
        anios_est = partes_fecha(f)[0]
        dias_validos = int(ok.sum())
        hasta_est = str(f.max())
        sel = f <= FIN_VALIDACION
        f, v = f[sel], v[sel]
        comunes = np.intersect1d(np.intersect1d(tl, f), te)
        if comunes.size < 30:
            out[var] = {"dataset": f"https://www.datos.gov.co/resource/{ds}", "nota": "menos de 30 días comunes válidos"}
            continue
        il = np.searchsorted(tl, comunes)
        ie_ = np.searchsorted(te, comunes)
        isx = np.searchsorted(f, comunes)
        xl, xe, xs = vl[pares[var]][il], ve[pares[var]][ie_], v[isx]
        bloque = {
            "dataset": f"https://www.datos.gov.co/resource/{ds}",
            "control_calidad": f"{nmin}–24 registros horarios en el día y valor en [{lo}, {hi}] °C",
            "dias_validos_estacion": dias_validos, "dias_descartados_cc": int((~ok).sum()),
            "desde": str(f.min()), "hasta": hasta_est,
            "dias_por_anio_estacion": {str(a): int(np.sum(anios_est == a)) for a in range(int(anios_est.min()), int(anios_est.max()) + 1)},
            "dias_comunes": int(comunes.size), "dias_comunes_era5land": int(comunes.size),
            "media_estacion": r(np.mean(xs)), "media_era5land": r(np.mean(xl)), "media_era5_mismos_dias": r(np.mean(xe)),
            "sesgo_era5land_menos_estacion": r(np.mean(xl - xs)), "sesgo_era5_menos_estacion": r(np.mean(xe - xs)),
            "r_diaria_era5land": r(np.corrcoef(xl, xs)[0, 1], 3), "r_diaria_era5": r(np.corrcoef(xe, xs)[0, 1], 3),
        }
        # correlación de anomalías mensuales (quita el ciclo anual): ¿sigue el reanálisis la variabilidad de la estación?
        an = anomalias_mensuales(comunes, xs, xl, xe)
        if an is not None:
            bloque["meses_con_20_dias"] = int(an[0].size)
            bloque["r_anomalias_mensuales_era5land"] = r(np.corrcoef(an[0], an[1])[0, 1], 3)
            bloque["r_anomalias_mensuales_era5"] = r(np.corrcoef(an[0], an[2])[0, 1], 3)
        if var == "tx":
            p32 = float(np.mean(xs >= 32.0))
            pct = (("p10", 10), ("p50", 50), ("p90", 90), ("p99", 99))
            bloque.update({
                "frecuencia_tx_ge_32_estacion_pct": r(100 * p32, 1),
                "frecuencia_tx_ge_32_era5land_pct": r(100 * np.mean(xl >= 32.0), 2),
                "percentiles_tx_estacion": {k: r(np.percentile(xs, q), 1) for k, q in pct} | {"max": r(xs.max(), 1)},
                "percentiles_tx_era5land": {k: r(np.percentile(xl, q), 1) for k, q in pct} | {"max": r(xl.max(), 1)},
                "percentiles_tx_era5": {k: r(np.percentile(xe, q), 1) for k, q in pct} | {"max": r(xe.max(), 1)},
            })
            if comunes.size >= 365 and 0 < p32 < 1:
                umbral = round(float(np.quantile(xl, 1 - p32, method="median_unbiased")), 1)
                bloque["umbral_equivalente_era5land"] = umbral
                bloque["frecuencia_umbral_equivalente_era5land_pct"] = r(100 * np.mean(xl >= umbral), 1)
            # destreza para días cálidos concretos (¿sirve el reanálisis para identificar días u avisar?)
            dz = {}
            q90s = float(np.quantile(xs, 0.9, method="median_unbiased"))
            dz["decil_superior"] = {
                "definicion": "evento = día en el 10 % más cálido de cada serie (umbral propio de cada una en los días comunes)",
                "umbral_estacion": r(q90s, 1),
                "era5land": destreza_eventos(xs, xl, q90s, float(np.quantile(xl, 0.9, method="median_unbiased")), False),
                "era5": destreza_eventos(xs, xe, q90s, float(np.quantile(xe, 0.9, method="median_unbiased")), False),
            }
            for nombre, x_r, u in (("umbral_local_era5land", xl, umbral_local), ("umbral_local_era5", xe, umbral_local_era5)):
                if u is None or comunes.size < 365:
                    continue
                q = float(np.mean(x_r > u))
                if not 0 < q < 1:
                    continue
                eq = float(np.quantile(xs, 1 - q, method="median_unbiased"))
                bloque_u = {"umbral_reanalisis": u, "frecuencia_reanalisis_en_dias_comunes_pct": r(100 * q, 1),
                            "equivalente_estacion_misma_frecuencia": r(eq, 1),
                            "contingencia": destreza_eventos(xs, x_r, round(eq, 1), u)}
                # frecuencia anual: años con ≥ 300 días comunes
                ac = partes_fecha(comunes)[0]
                filas_a = []
                for a in np.unique(ac):
                    s = ac == a
                    if s.sum() >= 300:
                        filas_a.append({"anio": int(a), "dias": int(s.sum()), "pct_estacion": r(100 * np.mean(xs[s] >= round(eq, 1)), 1),
                                        "pct_reanalisis": r(100 * np.mean(x_r[s] > u), 1)})
                bloque_u["frecuencia_anual"] = filas_a
                # correlación de la frecuencia anual: solo se publica con ≥ MIN_ANIOS_R_FRECUENCIA años; siempre con n e IC de Fisher
                bloque_u["r_frecuencia_anual"] = None
                if len(filas_a) >= 4:
                    n_a = len(filas_a)
                    rr = float(np.corrcoef([x["pct_estacion"] for x in filas_a], [x["pct_reanalisis"] for x in filas_a])[0, 1])
                    zf, se = math.atanh(max(min(rr, 0.999999), -0.999999)), 1 / math.sqrt(n_a - 3)
                    publicable = n_a >= MIN_ANIOS_R_FRECUENCIA
                    bloque_u["correlacion_frecuencia_anual"] = {
                        "n_anios": n_a, "r": r(rr, 3), "ic95_fisher": [r(math.tanh(zf - 1.96 * se), 2), r(math.tanh(zf + 1.96 * se), 2)],
                        "informativa": publicable,
                        "nota": (f"Años con ≥ 300 días comunes. Se exige n ≥ {MIN_ANIOS_R_FRECUENCIA} para usarla; con n = {n_a} el intervalo es "
                                 "demasiado ancho y la cifra no permite comparar reanálisis." if not publicable else
                                 f"Años con ≥ 300 días comunes (n ≥ {MIN_ANIOS_R_FRECUENCIA}).")}
                    if publicable:
                        bloque_u["r_frecuencia_anual"] = r(rr, 3)
                dz[nombre] = bloque_u
            dz["nota"] = ("POD = aciertos ÷ eventos de la estación; FAR = falsas alarmas ÷ eventos del reanálisis. Con POD ≈ 0,5 y FAR ≈ 0,5 "
                          "el índice no sirve para identificar días cálidos concretos ni para alertas: solo como índice climatológico "
                          "de frecuencia en periodos largos.")
            bloque["destreza_dias_calidos"] = dz
            if "umbral_local_era5land" in dz:
                bloque["umbral_local_era5land"] = umbral_local
                bloque["equivalente_estacion_umbral_local"] = dz["umbral_local_era5land"]["equivalente_estacion_misma_frecuencia"]
        out[var] = bloque
    # precipitación: días con 137–144 registros de 10 min (≥ 95 %; >144 indica duplicados)
    if "p" in est:
        f, v, n, ds = est["p"]
        ok = (n >= 137) & (n <= 144) & (v >= 0) & (v < 400)
        f, v = f[ok], v[ok]
        _, il, ie = np.intersect1d(te, f, return_indices=True)
        if il.size >= 30:
            pe = ve["precipitation_sum"][il]
            ps = v[ie]
            mf = f[ie].astype("datetime64[M]")
            filas = []
            for m in np.unique(mf):
                s = mf == m
                dias = dias_mes(m)
                if s.sum() >= 0.9 * dias:
                    filas.append((str(m), float(ps[s].sum() * dias / s.sum()), float(pe[s].sum() * dias / s.sum())))
            tot_s = np.array([x[1] for x in filas])
            tot_e = np.array([x[2] for x in filas])
            out["p"] = {
                "dataset": f"https://www.datos.gov.co/resource/{ds}",
                "control_calidad": "días con 137–144 registros de 10 min y total diario en [0, 400) mm",
                "dias_validos_estacion": int(ok.sum()), "dias_comunes_era5": int(il.size),
                "desde": str(f.min()), "hasta": str(f.max()),
                "media_diaria_estacion_mm": r(ps.mean()), "media_diaria_era5_mm": r(pe.mean()),
                "cociente_era5_estacion": r(pe.mean() / ps.mean(), 3) if ps.mean() > 0 else None,
                "r_diaria": r(np.corrcoef(pe, ps)[0, 1], 3),
                "meses_con_90pct_dias": len(filas),
                "r_mensual": r(np.corrcoef(tot_e, tot_s)[0, 1], 3) if len(filas) > 3 else None,
                "media_mensual_estacion_mm": r(tot_s.mean(), 1) if filas else None,
                "media_mensual_era5_mm": r(tot_e.mean(), 1) if filas else None,
                "p99_diaria_estacion_mm": r(np.percentile(ps, 99), 1), "p99_diaria_era5_mm": r(np.percentile(pe, 99), 1),
                "max_diaria_estacion_mm": r(ps.max(), 1), "max_diaria_era5_mm": r(pe.max(), 1),
                "dias_ge_20mm_estacion_pct": r(100 * np.mean(ps >= 20), 2), "dias_ge_20mm_era5_pct": r(100 * np.mean(pe >= 20), 2),
                "dias_ge_1mm_estacion_pct": r(100 * np.mean(ps >= 1), 1), "dias_ge_1mm_era5_pct": r(100 * np.mean(pe >= 1), 1),
                "nota": "Totales mensuales escalados a mes completo (suma × días del mes / días válidos) en meses con ≥ 90 % de días válidos.",
            }
            if chirps_pixel is not None:
                sp = chirps_pixel(EST_ZARAGOZA["lat"], EST_ZARAGOZA["lon"])
                par = [(x[1], sp[x[0]]) for x in filas if sp.get(x[0]) is not None]
                if len(par) > 3:
                    a_s, a_c = np.array([x[0] for x in par]), np.array([x[1] for x in par])
                    out["p"].update({
                        "meses_comunes_chirps": len(par), "r_mensual_chirps": r(np.corrcoef(a_c, a_s)[0, 1], 3),
                        "media_mensual_estacion_mm_meses_chirps": r(a_s.mean(), 1), "media_mensual_chirps_mm": r(a_c.mean(), 1),
                        "cociente_chirps_estacion": r(a_c.mean() / a_s.mean(), 3) if a_s.mean() > 0 else None,
                        "nota_chirps": "CHIRPS v3 en el píxel de 0,05° que contiene la estación; CHIRPS asimila estaciones del IDEAM (no es independiente).",
                    })
    return out, umbral


PARAM_NORMAL = {"TEMPERATURA MEDIA": "tmedia", "TEMPERATURA MÁXIMA": "tmax_media", "TEMPERATURA MÍNIMA": "tmin_media",
                "PRECIPITACIÓN": "precip_total", "HUMEDAD RELATIVA": "humedad_media"}
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
MESES_NOMBRE = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def validar_normales(norm, climas, chirps_clim=None):
    """Normales IDEAM de estaciones cercanas frente a la climatología del reanálisis (y de CHIRPS en el píxel de la
    estación) del mismo periodo."""
    filas = []
    vistos = set()
    for x in norm:
        par = PARAM_NORMAL.get(str(x.get("par_metro", "")).strip())
        if not par or x.get("periodo") not in climas:
            continue
        try:
            lat, lon, alt = float(x["latitud"]), float(x["longitud"]), float(x["altitud_m"])
            anual_ = float(x["anual"])
        except (KeyError, ValueError, TypeError):
            continue
        d = distancia_km(LAT, LON, lat, lon)
        if d > 30 or alt > 1250:
            continue
        clave = (x["c_digo"], x["periodo"], par)
        if clave in vistos:
            continue
        vistos.add(clave)
        cl = climas[x["periodo"]]
        rean = cl["era5land"] if par != "precip_total" else cl["era5"]
        rean_anual = rean["precip_anual"] if par == "precip_total" else rean[f"{par}_anual"]
        mensual_ideam = []
        for m in MESES:
            try:
                mensual_ideam.append(r(float(x[m]), 1))
            except (KeyError, ValueError, TypeError):
                mensual_ideam.append(None)
        fila = {
            "codigo": x["c_digo"], "estacion": str(x.get("estaci_n", "")).strip(), "municipio": x.get("municipio"),
            "categoria": x.get("categoria"), "altitud_m": alt, "lat": lat, "lon": lon, "distancia_km": r(d, 1),
            "periodo": x["periodo"], "variable": par,
            "mensual_ideam": mensual_ideam, "anual_ideam": r(anual_, 1), "anual_reanalisis": rean_anual,
            "reanalisis": "ERA5 (0,25°)" if par == "precip_total" else "ERA5-Land (0,1°)",
        }
        if par == "precip_total":
            fila["cociente_reanalisis_ideam"] = r(rean_anual / anual_, 3) if anual_ > 0 else None
            if chirps_clim is not None:
                a0, a1 = map(int, x["periodo"].split("-"))
                ch = chirps_clim(lat, lon, a0, a1)
                fila["anual_chirps_pixel"] = r(ch, 1)
                fila["cociente_chirps_ideam"] = r(ch / anual_, 3) if (ch is not None and anual_ > 0) else None
        else:
            fila["diferencia_reanalisis_menos_ideam"] = r(rean_anual - anual_, 2)
            fila["anual_era5"] = cl["era5"][f"{par}_anual"]
            fila["diferencia_era5_menos_ideam"] = r(cl["era5"][f"{par}_anual"] - anual_, 2)
        filas.append(fila)
    filas.sort(key=lambda f: (f["variable"], f["periodo"], f["distancia_km"]))
    return filas


def tendencia_normales(norm, climas):
    """Contraste observacional de la tendencia: cambio entre la primera y la última normal IDEAM disponible de cada estación
    del entorno (≤ 40 km, ≤ 1400 m) frente al cambio, entre los MISMOS periodos, de la climatología de ERA5-Land y de ERA5 en
    las celdas de Cartago. Para una tendencia lineal b, la diferencia entre dos medias de 30 años desplazadas k años es b·k;
    por eso la tasa equivalente es la diferencia ÷ k × 10 (°C/década)."""
    datos = {}
    for x in norm:
        par = PARAM_NORMAL.get(str(x.get("par_metro", "")).strip())
        if par not in ("tmedia", "tmax_media", "tmin_media") or x.get("periodo") not in climas:
            continue
        try:
            lat, lon, alt, val = float(x["latitud"]), float(x["longitud"]), float(x["altitud_m"]), float(x["anual"])
        except (KeyError, ValueError, TypeError):
            continue
        d = distancia_km(LAT, LON, lat, lon)
        if d > RADIO_NORMALES_TEND_KM or alt > ALT_NORMALES_TEND_M:
            continue
        clave = (x["c_digo"], par)
        datos.setdefault(clave, {"estacion": str(x.get("estaci_n", "")).strip(), "municipio": x.get("municipio"), "altitud_m": alt,
                                 "distancia_km": r(d, 1), "valores": {}})
        datos[clave]["valores"].setdefault(x["periodo"], val)
    filas = []
    for (cod, par), e in sorted(datos.items(), key=lambda z: (z[0][1], z[1]["distancia_km"])):
        per = sorted(e["valores"])
        if len(per) < 2:
            continue
        p0, p1 = per[0], per[-1]
        k = int(p1[:4]) - int(p0[:4])
        tasa = lambda a, b: r((b - a) / k * 10, 3)  # noqa: E731
        filas.append({
            "codigo": cod, "estacion": e["estacion"], "municipio": e["municipio"], "altitud_m": e["altitud_m"],
            "distancia_km": e["distancia_km"], "variable": par, "normales": {p: e["valores"][p] for p in per},
            "desde_periodo": p0, "hasta_periodo": p1, "desplazamiento_anios": k,
            "tasa_ideam_c_por_decada": tasa(e["valores"][p0], e["valores"][p1]),
            "tasa_era5land_c_por_decada": tasa(climas[p0]["era5land"][f"{par}_anual"], climas[p1]["era5land"][f"{par}_anual"]),
            "tasa_era5_c_por_decada": tasa(climas[p0]["era5"][f"{par}_anual"], climas[p1]["era5"][f"{par}_anual"]),
        })
    resumen = {}
    for par in ("tmedia", "tmax_media", "tmin_media"):
        f = [x for x in filas if x["variable"] == par]
        if f:
            resumen[par] = {"n_estaciones": len(f),
                            "tasa_ideam_min": min(x["tasa_ideam_c_por_decada"] for x in f),
                            "tasa_ideam_max": max(x["tasa_ideam_c_por_decada"] for x in f),
                            "tasa_ideam_mediana": r(np.median([x["tasa_ideam_c_por_decada"] for x in f]), 3),
                            "tasa_era5land_mediana_mismos_periodos": r(np.median([x["tasa_era5land_c_por_decada"] for x in f]), 3),
                            "tasa_era5_mediana_mismos_periodos": r(np.median([x["tasa_era5_c_por_decada"] for x in f]), 3)}
    return {"criterio": (f"estaciones IDEAM a ≤ {RADIO_NORMALES_TEND_KM} km del centro de Cartago y ≤ {ALT_NORMALES_TEND_M} m con al menos "
                         "dos normales (1961–1990, 1971–2000, 1981–2010, 1991–2020) de la variable; se usan la primera y la última"),
            "estaciones": filas, "resumen": resumen,
            "limitaciones": ("Las normales se publican redondeadas a 0,1 °C (con 10 años de desplazamiento, ±0,1 °C/década de resolución); "
                             "periodos solapados; el IDEAM no publica cuántos años válidos tiene cada normal ni si hubo traslados o "
                             "cambios de instrumento; el reanálisis se toma en las celdas de Cartago, no en cada estación. Es un "
                             "contraste, no una validación de la tendencia.")}


def resumen_normales(filas):
    """Diferencia media reanálisis − IDEAM por variable (todas las estaciones y periodos)."""
    out = {}
    for v in ("tmedia", "tmax_media", "tmin_media", "humedad_media"):
        sel = [f for f in filas if f["variable"] == v and f.get("diferencia_reanalisis_menos_ideam") is not None]
        if sel:
            d = [f["diferencia_reanalisis_menos_ideam"] for f in sel]
            e = [f["diferencia_era5_menos_ideam"] for f in sel if f.get("diferencia_era5_menos_ideam") is not None]
            out[v] = {"n_normales": len(d), "diferencia_media_era5land_menos_ideam": r(np.mean(d)),
                      "min": r(min(d)), "max": r(max(d)),
                      "diferencia_media_era5_menos_ideam": r(np.mean(e)) if e else None,
                      "min_era5": r(min(e)) if e else None, "max_era5": r(max(e)) if e else None}
    c = [f["cociente_reanalisis_ideam"] for f in filas if f["variable"] == "precip_total" and f.get("cociente_reanalisis_ideam")]
    if c:
        out["precip_total"] = {"n_normales": len(c), "cociente_medio_era5_ideam": r(np.mean(c), 3), "min": r(min(c), 3), "max": r(max(c), 3)}
    c = [f["cociente_chirps_ideam"] for f in filas if f["variable"] == "precip_total" and f.get("cociente_chirps_ideam")]
    if c:
        out["precip_chirps"] = {"n_normales": len(c), "cociente_medio_chirps_ideam": r(np.mean(c), 3), "min": r(min(c), 3),
                                "max": r(max(c), 3), "nota": "solo periodos 1981–2010 y 1991–2020 (CHIRPS empieza en 1981)"}
    return out


# ------------------------------------------------------------------ principal

# ------------------------------------------------------------------ diagnósticos

def frecuencia_picos(T24, H24, umbral=PICO_CURV, umbral_hr=PICO_HR):
    """Horas que cumplirían el criterio de pico (una sola pasada), hacia arriba y hacia abajo."""
    cT, cH = curvatura(T24.ravel()), curvatura(H24.ravel())
    return {"hacia_arriba": int(np.sum((cT > umbral) & (cH < umbral_hr))),
            "hacia_abajo": int(np.sum((cT < -umbral) & (cH > -umbral_hr)))}


def resumen_picos(tl, T24, H24, T24f, H24f, eventos, vl_orig, vl, ref_era5):
    anio = partes_fecha(tl)[0]
    idx = np.array([e["i"] for e in eventos], int)
    dia_i, hora = idx // 24, idx % 24
    dec = (anio[dia_i] // 10) * 10
    tx0, tx1 = vl_orig["temperature_2m_max"], vl["temperature_2m_max"]
    i0, i1 = int(np.argmax(tx0)), int(np.argmax(tx1))
    txx = {str(a): {"sin_filtro": r(tx0[anio == a].max(), 1), "filtrada": r(tx1[anio == a].max(), 1)}
           for a in range(2016, int(anio.max()) + 1)}
    mayores = sorted(eventos, key=lambda e: e["t_reparada"] - e["t_original"])[:12]
    # «picos hacia abajo»: se cuentan en la serie ya filtrada, porque antes de filtrar la hora previa a cada pico hacia arriba
    # también tiene curvatura negativa (es un efecto del propio pico)
    abajo = frecuencia_picos(T24f, H24f)["hacia_abajo"]
    return {
        "criterio": (f"hora con T − (T de la hora anterior + T de la siguiente)/2 > {PICO_CURV} °C y, a la vez, HR − (HR anterior + HR "
                     f"siguiente)/2 < {PICO_HR} puntos; T y HR de esa hora se reemplazan por la media de sus vecinas; hasta {PICO_PASADAS} "
                     "pasadas (la hora siguiente a veces conserva parte del exceso). Después se recalculan Tmax (máximo de las 24 horas), "
                     "la Tmedia y la HR media diarias (se les suma la corrección ÷ 24); la Tmin no cambia."),
        "justificacion_umbral": None if not ref_era5 else (
            f"En {ref_era5['periodo']}, en ERA5 (0,25°, el forzamiento atmosférico de ERA5-Land, sin este artefacto) el mismo criterio se "
            f"cumple {ref_era5['umbral_2.5']['era5']} veces con 2,5 °C, frente a {ref_era5['umbral_2.5']['era5land']} en ERA5-Land "
            f"(con 2,0 °C: {ref_era5['umbral_2.0']['era5']} frente a {ref_era5['umbral_2.0']['era5land']}; con 3,0 °C: "
            f"{ref_era5['umbral_3.0']['era5']} frente a {ref_era5['umbral_3.0']['era5land']}). Con 2,5 °C casi todo lo marcado es exceso "
            "de ERA5-Land sobre la tasa de ERA5. Es un supuesto metodológico propio; ver sensibilidad_filtro_picos."),
        "horas_corregidas": len(eventos),
        "por_pasada": {str(p): int(sum(e["pasada"] == p for e in eventos)) for p in range(1, PICO_PASADAS + 1)},
        "dias_afectados": int(np.unique(dia_i).size),
        "por_decenio": {f"{d}s": int(np.sum(dec == d)) for d in range(1950, int(anio.max()) // 10 * 10 + 10, 10)},
        "por_hora_local": {str(h): int(np.sum(hora == h)) for h in range(24) if np.any(hora == h)},
        "picos_hacia_abajo_mismo_criterio_en_serie_filtrada": abajo,
        "referencia_era5": ref_era5,
        "mayores": [{"fecha": str(tl[e["i"] // 24]), "hora_local": e["i"] % 24, "t_original": r(e["t_original"], 1),
                     "t_reparada": r(e["t_reparada"], 2), "hr_original": r(e["hr_original"], 0), "hr_reparada": r(e["hr_reparada"], 1)}
                    for e in mayores],
        "efecto": {
            "tmax_record_sin_filtro": {"valor": r(tx0[i0], 1), "fecha": str(tl[i0])},
            "tmax_record_filtrada": {"valor": r(tx1[i1], 1), "fecha": str(tl[i1])},
            "dias_tmax_ge_32_sin_filtro": int(np.sum(tx0 >= 32)), "dias_tmax_ge_32_filtrada": int(np.sum(tx1 >= 32)),
            "mayor_reduccion_tmax_diaria": r(np.max(tx0 - tx1), 1),
            "reduccion_media_tmax_todos_los_dias": r(np.mean(tx0 - tx1), 4),
            "mayor_reduccion_tmedia_diaria": r(np.max(vl_orig["temperature_2m_mean"] - vl["temperature_2m_mean"]), 2),
            "txx_por_anio": txx,
        },
        "documentacion": ("El artefacto no figura entre los problemas conocidos de ERA5-Land publicados por ECMWF (Copernicus Knowledge "
                          "Base, «ERA5-Land: data documentation», consultada el 2026-09-30). En los casos revisados a mano (2022-09-10, "
                          "2024-04-08, 2026-06-29) el salto aparece también en la temperatura del suelo de ERA5-Land y no en la "
                          "temperatura de ERA5: es un artefacto del modelo de superficie, no un evento meteorológico."),
    }


def sensibilidad_picos(tl, T24, H24):
    """Índices de Tmax según el criterio de filtrado (para mostrar cuánto depende el resultado de la elección)."""
    variantes = {
        "sin_filtro": None,
        "curvatura_2.0_con_HR": {"umbral": 2.0},
        "curvatura_2.5_con_HR (producto)": {"umbral": 2.5},
        "curvatura_3.0_con_HR": {"umbral": 3.0},
        "vecina_mayor_3.0_sin_HR_una_pasada (revisor)": {"umbral": 3.0, "criterio": "vecina_max", "exigir_hr": False, "pasadas": 1},
    }
    anio = partes_fecha(tl)[0]
    sb = (anio >= BASE[0]) & (anio <= BASE[1])
    a_rec = list(range(2016, 2026))
    out = {}
    for nombre, kw in variantes.items():
        if kw is None:
            tx, n = T24.max(1), 0
        else:
            Tf, _, ev = filtrar_picos(T24, H24, **kw)
            tx, n = Tf.max(1), len(ev)
        ul = round(float(np.quantile(tx[sb], 0.9, method="median_unbiased")), 1)
        ex = Percentil90(tl, tx).excedencias_anuales(a_rec)
        a81 = list(range(1981, 2026))
        out[nombre] = {
            "horas_corregidas": n, "tmax_record": r(tx.max(), 1), "dias_tmax_ge_32": int(np.sum(tx >= 32)),
            "txx_media_2016_2025": r(np.mean([tx[anio == a].max() for a in a_rec]), 2),
            "txx_ols_1981_2025_c_por_decada": tendencia(a81, [tx[anio == a].max() for a in a81])["ols_por_decada"],
            "tmax_media_ols_1981_2025_c_por_decada": tendencia(a81, [tx[anio == a].mean() for a in a81])["ols_por_decada"],
            "umbral_local_p90_1961_1990": ul,
            "dias_gt_umbral_local_media_2016_2025": r(np.mean([np.sum(tx[anio == a] > ul) for a in a_rec]), 1),
            "dias_tx90p_media_2016_2025": r(np.mean([ex[a][0] for a in a_rec]), 1),
        }
    return out


def discontinuidad_era5(dias_e, TE24, tl, vl):
    """Ciclo diurno de ERA5 (Open-Meteo) frente a ERA5-Land, por mes desde 2024, y resumen antes/después de mayo de 2025."""
    _, i, j = np.intersect1d(dias_e, tl, return_indices=True)
    X, d = TE24[i], dias_e[i]
    amp_e = X.max(1) - X.mean(1)
    amp_l = vl["temperature_2m_max"][j] - vl["temperature_2m_mean"][j]
    hmax = X.argmax(1)
    dtx = vl["temperature_2m_max"][j] - X.max(1)
    dtm = vl["temperature_2m_mean"][j] - X.mean(1)
    m = d.astype("datetime64[M]")
    filas = []
    for mm in np.unique(m):
        if mm < np.datetime64("2024-01"):
            continue
        s = m == mm
        filas.append({"mes": str(mm), "amplitud_era5": r(amp_e[s].mean()), "amplitud_era5land": r(amp_l[s].mean()),
                      "hora_media_del_maximo_era5": r(hmax[s].mean(), 1), "tmax_era5land_menos_era5": r(dtx[s].mean()),
                      "tmedia_era5land_menos_era5": r(dtm[s].mean())})
    a = d < np.datetime64("2025-01-01")
    b = d >= np.datetime64("2025-05-01")
    resumen = {
        "periodos": [f"{d[a].min()} a {d[a].max()}", f"{d[b].min()} a {d[b].max()}"],
        "amplitud_tmax_menos_tmedia_era5": [r(amp_e[a].mean()), r(amp_e[b].mean())],
        "amplitud_tmax_menos_tmedia_era5land": [r(amp_l[a].mean()), r(amp_l[b].mean())],
        "hora_media_del_maximo_era5": [r(hmax[a].mean(), 1), r(hmax[b].mean(), 1)],
        "tmax_era5land_menos_era5": [r(dtx[a].mean()), r(dtx[b].mean())],
        "tmedia_era5land_menos_era5": [r(dtm[a].mean()), r(dtm[b].mean())],
    }
    return {"descripcion": ("Desde mayo de 2025 la temperatura horaria de ERA5 que sirve Open-Meteo cambia de ciclo diurno: la hora media del "
                            f"máximo pasa de {resumen['hora_media_del_maximo_era5'][0]} a {resumen['hora_media_del_maximo_era5'][1]} h y la amplitud "
                            f"Tmax − Tmedia de {resumen['amplitud_tmax_menos_tmedia_era5'][0]} a {resumen['amplitud_tmax_menos_tmedia_era5'][1]} °C, "
                            f"mientras en ERA5-Land queda en {resumen['amplitud_tmax_menos_tmedia_era5land'][0]} → "
                            f"{resumen['amplitud_tmax_menos_tmedia_era5land'][1]} °C. No está documentado en Open-Meteo (consultado el 2026-09-30). "
                            "Afecta a Tmax y Tmin de ERA5 desde 2025; la media diaria cambia menos. Por eso la validación con la estación no "
                            "usa 2025 y las tendencias de ERA5 se dan también hasta 2024."),
            "resumen_2015_2024_vs_desde_2025_05": resumen, "mensual": filas}


def consistencia_lluvia(tab, mens, tend):
    """¿Sirve la lluvia de ERA5 al menos en términos relativos? Se compara con CHIRPS v3 en los años y meses comunes."""
    anios = np.array(tab["anio"])
    parcial = np.array(tab["parcial"])
    num = lambda x: np.array([np.nan if v is None else v for v in x], float)  # noqa: E731
    pe, pc = num(tab["precip_total"]), num(tab["precip_chirps"])
    s = ~parcial & np.isfinite(pe) & np.isfinite(pc)
    det = lambda y, x: y - np.polyval(np.polyfit(x, y, 1), x)  # noqa: E731
    me, mc = num(mens["precip_total"]), num(mens["precip_chirps"])
    mm = np.array([int(x[5:7]) for x in mens["mes"]])
    sm = np.isfinite(me) & np.isfinite(mc)
    an_e = me[sm] - np.array([me[sm][mm[sm] == k].mean() for k in mm[sm]])
    an_c = mc[sm] - np.array([mc[sm][mm[sm] == k].mean() for k in mm[sm]])
    rx = num(tab["rx1day"])
    t8 = tend["1981-2025"]
    return {
        "anios_comunes": f"{int(anios[s].min())}-{int(anios[s].max())}", "n_anios": int(s.sum()),
        "r_anual_era5_chirps": r(np.corrcoef(pe[s], pc[s])[0, 1], 3),
        "r_anual_sin_tendencia": r(np.corrcoef(det(pe[s], anios[s]), det(pc[s], anios[s]))[0, 1], 3),
        "meses_comunes": int(sm.sum()), "r_anomalias_mensuales_era5_chirps": r(np.corrcoef(an_e, an_c)[0, 1], 3),
        "tendencia_1981_2025_pct_por_decada": {
            "era5": {"valor": t8["precip_total"]["pct_por_decada_vs_1991_2020"], "ic95": t8["precip_total"]["pct_ic95_vs_1991_2020"]},
            "chirps": {"valor": t8["precip_chirps"]["pct_por_decada_vs_1991_2020"], "ic95": t8["precip_chirps"]["pct_ic95_vs_1991_2020"]}},
        "rx1day_era5_media_1950_1959_mm": r(np.nanmean(rx[(anios >= 1950) & (anios <= 1959)]), 1),
        "rx1day_era5_media_2016_2025_mm": r(np.nanmean(rx[(anios >= 2016) & (anios <= 2025)]), 1),
        "veredicto": ("La lluvia de ERA5 en esta celda no sirve ni en valores absolutos ni en términos relativos: su variabilidad anual y "
                      "mensual se parece poco a la de CHIRPS (y a la de la estación Zaragoza, ver validacion_ideam) y su tendencia de 1981–2025 "
                      "contradice la de CHIRPS. precip_total, rx1day y rx5day se publican solo por trazabilidad y NO son aptos para "
                      "decisiones (drenaje, inundación, gestión del agua)."),
    }


def _sin_tildes(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "")) if unicodedata.category(c) != "Mn").strip().lower()


def radiacion_ideam_estacion(rad_ideam, rad_meta, ce, cp, tab):
    """Climatología MEDIDA de la radiación global en la estación IDEAM Zaragoza (datos.gov.co rv9s-8nv6, sensor calibrado)
    frente a las climatologías mensuales 1991–2020 de ERA5 y NASA POWER. El IDEAM no publica el periodo de su climatología:
    se da la sensibilidad del cociente a cualquier ventana de 10 años entre 1984 y el último año completo."""
    filas = []
    for x in rad_ideam or []:
        try:
            lat, lon, alt = float(x["latitud"]), float(x["longitud"]), float(x["altitud"])
            meses = [float(x[m]) / 1000 for m in MESES]  # Wh/m²/día → kWh/m²/día
            anual_ = float(x["promedio_anual"]) / 1000
        except (KeyError, ValueError, TypeError):
            continue
        filas.append({"estacion": str(x.get("estacion", "")).strip(), "municipio": x.get("municipio"), "departamento": x.get("departamento"),
                      "tipo": x.get("tipo_de_estacion"), "lat": lat, "lon": lon, "altitud_m": alt,
                      "distancia_km": r(distancia_km(LAT, LON, lat, lon), 1), "mensual": rl(meses, 3), "anual": r(anual_, 3)})
    zs = [f for f in filas if _sin_tildes(f["estacion"]) == "zaragoza" and _sin_tildes(f["municipio"]) == "cartago"]
    if not zs:
        return None
    z = zs[0]
    d_est = distancia_km(z["lat"], z["lon"], EST_ZARAGOZA["lat"], EST_ZARAGOZA["lon"])
    zm, ce_, cp_ = np.array(z["mensual"]), np.array(ce, float), np.array(cp, float)
    num = lambda v: np.array([np.nan if y is None else y for y in v], float)  # noqa: E731
    anios, comp = np.array(tab["anio"]), ~np.array(tab["parcial"])
    series = {"era5": num(tab["radiacion_kwh_m2_dia"]), "nasa_power": num(tab["radiacion_power_kwh_m2_dia"])}
    ult = int(anios[comp].max())
    vent, maximos = {}, {}
    for k, x in series.items():
        q = []
        for a0 in range(1984, ult - 8):
            s = comp & (anios >= a0) & (anios <= a0 + 9)
            if np.isfinite(x[s]).sum() == 10:
                q.append(float(np.mean(x[s])) / z["anual"])
        vent[k] = {"min": r(min(q), 3), "max": r(max(q), 3), "ventanas": len(q)} if q else None
        s = comp & np.isfinite(x)
        i = int(np.argmax(np.where(s, x, -np.inf)))
        maximos[k] = {"anio": int(anios[i]), "valor": r(x[i], 3), "desde": int(anios[s].min()), "hasta": int(anios[s].max())}
    entorno = sorted([{k: f[k] for k in ("estacion", "municipio", "departamento", "tipo", "altitud_m", "distancia_km", "anual")}
                      for f in filas if f["distancia_km"] <= RADIO_RAD_ENTORNO_KM], key=lambda f: f["distancia_km"])
    c_e, c_p = float(ce_.mean()) / z["anual"], float(cp_.mean()) / z["anual"]
    return {
        "dataset": f"https://www.datos.gov.co/resource/{IDEAM_RAD_DS}",
        "metadatos": rad_meta,
        "licencia": "CC BY-SA 4.0 (Instituto de Hidrología, Meteorología y Estudios Ambientales - IDEAM)",
        "estacion": {k: z[k] for k in ("estacion", "municipio", "departamento", "tipo", "lat", "lon", "altitud_m", "distancia_km")}
        | {"distancia_a_la_estacion_0026105250_km": r(d_est, 1)},
        "identificacion": (f"El conjunto no publica el código de la estación; coincide en nombre, municipio, tipo y posición (a {d_est:.1f} km, "
                           "con coordenadas publicadas a 0,01°) con la estación ZARAGOZA (AUT) 0026105250 que se usa para la temperatura."),
        "periodo": ("no publicado: el conjunto da solo promedios multianuales («valor medio multianual»), sin años ni número de datos. "
                    "La comparación es entre climatologías, no entre meses simultáneos."),
        "mensual_kwh_m2_dia": z["mensual"], "anual_kwh_m2_dia": z["anual"],
        "control_anual_igual_a_media_simple_de_los_meses": r(float(zm.mean()), 3),
        "comparacion_climatologia_1991_2020": {
            "era5": r(ce_.mean(), 3), "nasa_power": r(cp_.mean(), 3),
            "cociente_era5_ideam": r(c_e, 3), "cociente_power_ideam": r(c_p, 3),
            "diferencia_era5_pct": r(100 * (c_e - 1), 1), "diferencia_power_pct": r(100 * (c_p - 1), 1),
            "mes": list(range(1, 13)), "cociente_mensual_era5_ideam": rl(ce_ / zm, 3), "cociente_mensual_power_ideam": rl(cp_ / zm, 3),
            "r_ciclo_anual_era5": r(np.corrcoef(ce_, zm)[0, 1], 3), "r_ciclo_anual_power": r(np.corrcoef(cp_, zm)[0, 1], 3),
            "nota_r": "correlación de las 12 medias mensuales (forma del ciclo anual); con 12 valores es solo descriptiva.",
        },
        "sensibilidad_al_periodo": {
            "descripcion": (f"cociente reanálisis ÷ IDEAM con la media de cada ventana de 10 años completos entre 1984 y {ult}, porque el "
                            "periodo de la climatología del IDEAM se desconoce"),
            "era5": vent["era5"], "nasa_power": vent["nasa_power"]},
        "maximo_anual": maximos,
        "estaciones_entorno": {"criterio": f"estaciones del conjunto a ≤ {RADIO_RAD_ENTORNO_KM} km del centro de Cartago", "estaciones": entorno},
    }


def validar_radiacion(mens, pw_meta, tab=None, rad_ideam=None, rad_meta=None):
    """Radiación de ERA5 frente a NASA POWER (GEWEX SRB 1984–2000, CERES SYN1deg 2001→; 1°) y frente a la climatología medida de la
    estación IDEAM Zaragoza (rv9s-8nv6)."""
    num = lambda x: np.array([np.nan if v is None else v for v in x], float)  # noqa: E731
    e, p = num(mens["radiacion_kwh_m2_dia"]), num(mens["radiacion_power_kwh_m2_dia"])
    parcial = np.array(mens["parcial"])
    anio = np.array([int(x[:4]) for x in mens["mes"]])
    mm = np.array([int(x[5:7]) for x in mens["mes"]])
    ok = np.isfinite(e) & np.isfinite(p) & ~parcial
    per = {}
    for a0, a1 in ((1984, 2000), (2001, 2020), (1991, 2020), (2016, 2025), (2025, 2025)):
        s = ok & (anio >= a0) & (anio <= a1)
        if s.sum() >= 12:
            per[f"{a0}-{a1}"] = {"era5": r(e[s].mean(), 3), "nasa_power": r(p[s].mean(), 3), "cociente_era5_power": r(e[s].mean() / p[s].mean(), 3)}
    s = ok & (anio >= 1991) & (anio <= 2020)
    ce = [float(e[s & (mm == k)].mean()) for k in range(1, 13)]
    cp = [float(p[s & (mm == k)].mean()) for k in range(1, 13)]
    an_e = e[ok] - np.array([e[ok][mm[ok] == k].mean() for k in mm[ok]])
    an_p = p[ok] - np.array([p[ok][mm[ok] == k].mean() for k in mm[ok]])
    elev_pw = (pw_meta or {}).get("elevacion_media_celda_merra2_m")
    emp = None
    if "1984-2000" in per and "2001-2020" in per:
        c0, c1 = per["1984-2000"]["cociente_era5_power"], per["2001-2020"]["cociente_era5_power"]
        emp = {"cociente_era5_power_1984_2000_srb": c0, "cociente_era5_power_2001_2020_ceres": c1,
               "cambio_relativo_pct": r(100 * (c1 / c0 - 1), 1),
               "documentacion": ("POWER une GEWEX SRB R4-IP (1984-01-01 a 2000-12-31) y CERES SYN1deg (2001-01-01→) y corrige el sesgo entre "
                                 "ambos ajustando SRB por mapeo de cuantiles entrenado con 2001–2009 "
                                 "(https://power.larc.nasa.gov/docs/methodology/energy-fluxes/srb-correction/, consultada el 2026-10-01)."),
               "nota": (f"Aun con esa corrección, el cociente ERA5 ÷ POWER pasa de {c0} a {c1} en el empalme: queda un salto relativo de "
                        f"≈ {abs(100 * (c1 / c0 - 1)):.0f} % entre las dos series (no se puede atribuir solo a POWER, porque ERA5 también cambia "
                        "sus observaciones asimiladas). Una tendencia de radiacion_power_kwh_m2_dia que cruce 2001 no debe leerse como cambio "
                        "físico sin más; véase tendencias.radiacion_power_solo_ceres_2001_2025.")}
    est = radiacion_ideam_estacion(rad_ideam, rad_meta, ce, cp, tab) if (rad_ideam and tab is not None) else None
    if est:
        cz = est["comparacion_climatologia_1991_2020"]
        nota = (f"Hay una medición abierta: la climatología de la estación automática IDEAM Zaragoza ({est['estacion']['distancia_km']} km del centro, "
                f"{est['estacion']['altitud_m']:.0f} m; datos.gov.co {IDEAM_RAD_DS}, «sensor de radiación global calibrado»), "
                f"{est['anual_kwh_m2_dia']:.2f} kWh/m²/día. Frente a ella ERA5 queda un {abs(cz['diferencia_era5_pct']):.0f} % por debajo y NASA POWER "
                f"un {abs(cz['diferencia_power_pct']):.0f} %; el IDEAM no publica el periodo, pero con cualquier decenio entre 1984 y "
                f"{est['maximo_anual']['era5']['hasta']} el cociente de ERA5 queda entre {est['sensibilidad_al_periodo']['era5']['min']} y "
                f"{est['sensibilidad_al_periodo']['era5']['max']} y el de POWER entre {est['sensibilidad_al_periodo']['nasa_power']['min']} y "
                f"{est['sensibilidad_al_periodo']['nasa_power']['max']}. ERA5 (0,25°) y POWER (1°) promedian celdas que incluyen laderas y "
                "cordillera"
                + (f" (POWER informa para su celda MERRA-2 de 0,5° × 0,625° una elevación media de {elev_pw:.0f} m, frente a "
                   f"{est['estacion']['altitud_m']:.0f} m de la estación)" if elev_pw else "")
                + ", donde las estaciones del IDEAM miden menos radiación que en el fondo del valle (estacion_ideam.estaciones_entorno). "
                "Para valores absolutos (p. ej., dimensionar sistemas solares) úsese la medición del "
                "IDEAM; ERA5 y POWER sirven para anomalías.")
    else:
        nota = ("ERA5 es un reanálisis de 0,25° y POWER un producto satelital de 1° (≈ 110 km); ninguno es una medición local. No se pudo "
                f"leer la climatología medida del IDEAM (datos.gov.co {IDEAM_RAD_DS}) para compararlas.")
    return {
        "referencia": "NASA POWER ALLSKY_SFC_SW_DWN mensual (kWh/m²/día) en el punto central de Cartago (celda de 1°)",
        "fuentes_power": (pw_meta or {}).get("fuentes"), "periodos": per,
        "climatologia_mensual_1991_2020": {"mes": list(range(1, 13)), "era5": rl(ce, 3), "nasa_power": rl(cp, 3),
                                           "cociente": rl(np.array(ce) / np.array(cp), 3)},
        "meses_comunes": int(ok.sum()), "r_anomalias_mensuales": r(np.corrcoef(an_e, an_p)[0, 1], 3),
        "elevacion_media_celda_power_merra2_m": elev_pw,
        "empalme_srb_ceres_power": emp,
        "estacion_ideam": est,
        "nota": nota,
    }


# ------------------------------------------------------------------ principal

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--actualizar", action="store_true", help="vuelve a descargar el año en curso")
    ap.add_argument("--sin-ideam", action="store_true", help="omite la validación IDEAM")
    ap.add_argument("--salida", default=SALIDA, help="ruta del JSON (para pruebas)")
    args = ap.parse_args()
    t_ini = time.time()

    log("1. Reanálisis")
    (tl, vl, meta_l, nulos_hist, t26), (te, ve, meta_e) = cargar_reanalisis(args.actualizar)
    log(f"   ERA5-Land {tl[0]} → {tl[-1]} ({tl.size} días); ERA5 {te[0]} → {te[-1]} ({te.size} días)")
    log(f"   nulos en el archivo de partida: {nulos_hist}")
    for k in VARS_L:
        assert np.isfinite(vl[k]).all(), f"ERA5-Land {k} tiene huecos"
    for k in ("precipitation_sum", "shortwave_radiation_sum"):
        assert np.isfinite(ve[k]).all(), f"ERA5 {k} tiene huecos"

    log("   ERA5-Land horario y filtro de picos espurios")
    dias_h, T24, H24 = cargar_horario(descargar_horario(args.actualizar), meta_l)
    n = min(dias_h.size, tl.size)
    assert np.array_equal(dias_h[:n], tl[:n]), "las fechas de la serie horaria y de la diaria no coinciden"
    if tl.size > n:
        log(f"   AVISO: se recortan {tl.size - n} días finales sin las 24 horas")
        tl, vl = tl[:n], {k: a[:n] for k, a in vl.items()}
    T24, H24 = T24[:n], H24[:n]
    repro = {
        "descripcion": ("Agregados diarios de la serie horaria SIN filtrar (hora local America/Bogota) frente al archivo de partida y a "
                        "2026: Tmax y Tmin idénticas; la media difiere solo por redondeo (Open-Meteo promedia valores sin redondear)."),
        "tmax_max_dif_abs": r(np.max(np.abs(T24.max(1) - vl["temperature_2m_max"])), 3),
        "tmin_max_dif_abs": r(np.max(np.abs(T24.min(1) - vl["temperature_2m_min"])), 3),
        "tmedia_max_dif_abs": r(np.max(np.abs(T24.mean(1) - vl["temperature_2m_mean"])), 3),
        "hr_media_max_dif_abs": r(np.max(np.abs(H24.mean(1) - vl["relative_humidity_2m_mean"])), 3),
    }
    assert repro["tmax_max_dif_abs"] == 0 and repro["tmin_max_dif_abs"] == 0, "la serie horaria no reproduce Tmax/Tmin diarias"
    assert repro["tmedia_max_dif_abs"] < 0.1 and repro["hr_media_max_dif_abs"] < 1
    T24f, H24f, eventos = filtrar_picos(T24, H24)
    vl_orig = {k: a.copy() for k, a in vl.items()}
    vl["temperature_2m_max"] = T24f.max(1)
    vl["temperature_2m_mean"] = vl_orig["temperature_2m_mean"] + (T24f - T24).sum(1) / 24
    vl["relative_humidity_2m_mean"] = vl_orig["relative_humidity_2m_mean"] + (H24f - H24).sum(1) / 24
    assert np.allclose(T24f.min(1), vl_orig["temperature_2m_min"]), "el filtro no debe tocar la mínima"
    log(f"   {len(eventos)} horas corregidas en {len(set(e['i'] // 24 for e in eventos))} días")
    ref_era5, disc_era5 = None, None
    try:
        dias_e, TE24, HE24 = cargar_horario(descargar_horario(args.actualizar, modelo="era5", desde=2015), meta_e)
        _, ie_, il_ = np.intersect1d(dias_e, tl, return_indices=True)
        ae_ = partes_fecha(dias_e)[0][ie_]
        s_ = (ae_ >= 2015) & (ae_ <= 2024)
        ref_era5 = {"periodo": "2015-2024"}
        for u in (2.0, 2.5, 3.0):
            ref_era5[f"umbral_{u}"] = {"era5": frecuencia_picos(TE24[ie_[s_]], HE24[ie_[s_]], u)["hacia_arriba"],
                                       "era5land": frecuencia_picos(T24[il_[s_]], H24[il_[s_]], u)["hacia_arriba"]}
        ref_era5["hacia_abajo_2.5"] = {"era5": frecuencia_picos(TE24[ie_[s_]], HE24[ie_[s_]])["hacia_abajo"],
                                       "era5land_filtrada": frecuencia_picos(T24f[il_[s_]], H24f[il_[s_]])["hacia_abajo"]}
        disc_era5 = discontinuidad_era5(dias_e, TE24, tl, vl)
        _, a_, b_ = np.intersect1d(dias_e, te, return_indices=True)
        repro["era5_tmax_horario_vs_diario_max_dif_abs"] = r(np.max(np.abs(TE24[a_].max(1) - ve["temperature_2m_max"][b_])), 3)
    except Exception as e:  # el diagnóstico de ERA5 no es imprescindible
        log(f"   AVISO: sin ERA5 horario: {e}")
    picos = resumen_picos(tl, T24, H24, T24f, H24f, eventos, vl_orig, vl, ref_era5)
    sens_picos = sensibilidad_picos(tl, T24, H24)

    elev = elevacion_modelo(tl, vl_orig, meta_l)
    log(f"   orografía del modelo {elev['elevacion_modelo_m']} m; downscaling a {meta_l['elevation']} m")
    try:
        vecinas = celdas_vecinas(tl, vl_orig["temperature_2m_mean"], meta_l["elevation"])
    except Exception as e:
        log(f"   AVISO: sin celdas vecinas: {e}")
        vecinas = None
    frac_urb = fraccion_urbana_en_celda(round(meta_l["latitude"], 2), round(meta_l["longitude"], 2))

    log("   CHIRPS v3 mensual (lluvia de referencia)")
    ch, chirps_info, chirps_pixel, chirps_clim, fallos_ch = None, None, None, None, []
    try:
        res_ch = chirps_mensual(args.actualizar)
    except Exception as e:
        log(f"   AVISO: CHIRPS no disponible: {e}")
        res_ch = None
    if res_ch:
        meses_ch, cubo, tr_ch, fallos_ch = res_ch
        w_urb = pesos_urbanos(tr_ch, cubo.shape[1:])
        validos = np.isfinite(cubo)
        serie_ch = np.nansum(cubo * w_urb, axis=(1, 2)) / np.sum(w_urb * validos, axis=(1, 2))
        cubre = np.sum(w_urb * validos, axis=(1, 2))
        ch = {k: r(v, 1) for k, v, c_ in zip(meses_ch, serie_ch, cubre) if np.isfinite(v) and c_ > 0.99}
        anios_ch = np.array([int(k[:4]) for k in meses_ch])
        meses_n = np.array([int(k[5:]) for k in meses_ch])

        def chirps_pixel(lat, lon):
            i, j = pixel(tr_ch, lat, lon)
            if not (0 <= i < cubo.shape[1] and 0 <= j < cubo.shape[2]):
                return {}
            return {k: (float(cubo[n_, i, j]) if np.isfinite(cubo[n_, i, j]) else None) for n_, k in enumerate(meses_ch)}

        def chirps_clim(lat, lon, a0, a1):
            i, j = pixel(tr_ch, lat, lon)
            if a0 < int(meses_ch[0][:4]) or not (0 <= i < cubo.shape[1] and 0 <= j < cubo.shape[2]):
                return None
            tot = 0.0
            for k in range(1, 13):
                x = cubo[(anios_ch >= a0) & (anios_ch <= a1) & (meses_n == k), i, j]
                if np.isfinite(x).sum() < 0.9 * (a1 - a0 + 1):
                    return None
                tot += float(np.nanmean(x))
            return tot

        filas_w, cols_w = np.nonzero(w_urb)
        chirps_info = {
            "producto": "CHIRPS v3.0 mensual global (COG)", "url": CHIRPS_DIR, "resolucion_grados": 0.05,
            "primer_mes": meses_ch[0], "ultimo_mes": meses_ch[-1], "meses": len(meses_ch), "meses_fallidos": fallos_ch,
            "agregacion": ("media ponderada por la fracción de cada píxel dentro de la huella urbana: Comunas 1–7 (polígonos de "
                           "OpenStreetMap, ODbL) y Zaragoza (huella de ESA WorldCover 2021, CC BY 4.0; datos/zaragoza.json)"),
            "pixeles_urbanos": [{"lat_centro": r(tr_ch.f + (i + 0.5) * tr_ch.e, 3), "lon_centro": r(tr_ch.c + (j + 0.5) * tr_ch.a, 3),
                                 "peso": r(w_urb[i, j], 3)} for i, j in zip(filas_w, cols_w)],
        }
        log(f"   CHIRPS {meses_ch[0]} → {meses_ch[-1]} ({len(meses_ch)} meses; {len(fallos_ch)} fallidos); {len(filas_w)} píxeles urbanos")

    log("   NASA POWER mensual (radiación de referencia)")
    pw, pw_meta = None, None
    try:
        pw, pw_meta = power_mensual(args.actualizar)
        log(f"   POWER {min(pw)} → {max(pw)}")
    except Exception as e:
        log(f"   AVISO: NASA POWER no disponible: {e}")

    # umbrales locales de calor (propuesta): percentil 90 de todas las Tmax diarias de 1961–1990
    al = partes_fecha(tl)[0]
    sb = (al >= BASE[0]) & (al <= BASE[1])
    umbral_local = round(float(np.quantile(vl["temperature_2m_max"][sb], 0.9, method="median_unbiased")), 1)
    ae = partes_fecha(te)[0]
    sbe = (ae >= BASE[0]) & (ae <= BASE[1])
    umbral_local_era5 = round(float(np.quantile(ve["temperature_2m_max"][sbe], 0.9, method="median_unbiased")), 1)

    log("2. Validación IDEAM")
    est, umbral_eq, val_est, val_norm, tend_norm, fallos_ideam = {}, None, None, None, None, []
    if not args.sin_ideam:
        est, fallos_ideam = ideam_estacion_diaria(args.actualizar)
        if fallos_ideam:
            log(f"   AVISO: {len(fallos_ideam)} consultas IDEAM fallidas: {fallos_ideam[:4]}")
        if est:
            val_est, umbral_eq = validar_estacion(est, tl, vl, te, ve, chirps_pixel, umbral_local, umbral_local_era5)
            log(f"   umbral equivalente a 32 °C en ERA5-Land: {umbral_eq} °C")
    rad_ideam, rad_meta = None, None
    if not args.sin_ideam:
        try:
            rad_ideam, rad_meta = ideam_radiacion(args.actualizar)
            log(f"   radiación global IDEAM ({IDEAM_RAD_DS}): {len(rad_ideam)} estaciones")
        except Exception as e:  # la validación no es imprescindible
            log(f"   AVISO: sin la climatología de radiación del IDEAM: {e}")

    log("3. Percentiles ETCCDI (bootstrap 1961–1990)")
    t0 = time.time()
    p90x = Percentil90(tl, vl["temperature_2m_max"])
    p90n = Percentil90(tl, vl["temperature_2m_min"])
    tab = anual(tl, vl, te, ve, p90x, p90n, {"eq32": umbral_eq, "local": umbral_local}, ch, pw)
    p90x_e = Percentil90(te, ve["temperature_2m_max"])
    p90n_e = Percentil90(te, ve["temperature_2m_min"])  # contraste de TN90p (la Tmin es la variable peor validada)
    log(f"   {time.time() - t0:.1f} s")
    anios = np.array(tab["anio"])
    completos = ~np.array(tab["parcial"])

    def media_periodo(v, a0, a1, t=tab):
        x = np.array([np.nan if y is None else y for y in t[v]], float)[completos & (anios >= a0) & (anios <= a1)]
        return float(np.nanmean(x)) if np.isfinite(x).any() else None

    tx90_base = media_periodo("pct_tx90p", *BASE)
    tn90_base = media_periodo("pct_tn90p", *BASE)

    log("4. Tendencias")
    variables_t = {"tmedia": "°C/década", "tmax_media": "°C/década", "tmin_media": "°C/década", "txx": "°C/década",
                   "precip_total": "mm/década", "precip_chirps": "mm/década", "pct_tx90p": "puntos porcentuales/década",
                   "dias_tx90p": "días/década", "pct_tn90p": "puntos porcentuales/década",
                   "noches_tn90p": "noches/década", "dias_tmax_gt_umbral_local": "días/década",
                   "radiacion_power_kwh_m2_dia": "kWh/m²/día por década"}

    def tendencias(t, variables, periodos):
        res = {}
        for a0, a1 in periodos:
            s = completos & (anios >= a0) & (anios <= a1)
            res[f"{a0}-{a1}"] = {}
            for v in variables:
                y = np.array([np.nan if x is None else x for x in t[v]], float)[s]
                # una serie que no cubre el periodo completo (CHIRPS desde 1981, POWER desde 1984) no se ajusta en ese periodo
                res[f"{a0}-{a1}"][v] = tendencia(anios[s], y) if np.isfinite(y).sum() == s.sum() else None
        return res

    tend = tendencias(tab, variables_t, PERIODOS_TEND)
    # contraste: ERA5 (0,25°), con los mismos índices de Tmax
    exx_e = p90x_e.excedencias_anuales(list(anios))
    exn_e = p90n_e.excedencias_anuales(list(anios))
    era5_anual = {"anio": tab["anio"], "tmedia": [], "tmax_media": [], "tmin_media": [], "humedad_media": [], "dias_tx90p": [],
                  "pct_tx90p": [], "noches_tn90p": [], "pct_tn90p": [], "dias_tmax_gt_umbral_local": [], "afectado_discontinuidad_2025": []}
    for a in tab["anio"]:
        m = ae == a
        for v, k in (("tmedia", "temperature_2m_mean"), ("tmax_media", "temperature_2m_max"),
                     ("tmin_media", "temperature_2m_min"), ("humedad_media", "relative_humidity_2m_mean")):
            era5_anual[v].append(r(np.nanmean(ve[k][m]), 2) if m.any() else None)
        era5_anual["dias_tx90p"].append(r(exx_e[a][0], 1))
        era5_anual["pct_tx90p"].append(r(exx_e[a][2], 2))
        era5_anual["noches_tn90p"].append(r(exn_e[a][0], 1))
        era5_anual["pct_tn90p"].append(r(exn_e[a][2], 2))
        era5_anual["dias_tmax_gt_umbral_local"].append(int(np.sum(ve["temperature_2m_max"][m] > umbral_local_era5)) if m.any() else None)
        era5_anual["afectado_discontinuidad_2025"].append(bool(a >= 2025))
    per_e = PERIODOS_TEND + [(1950, 2024), (1981, 2024), (1991, 2024)]
    tend_e = tendencias(era5_anual, ("tmedia", "tmax_media", "tmin_media", "pct_tx90p", "pct_tn90p", "noches_tn90p",
                                     "dias_tmax_gt_umbral_local"), per_e)
    # radiación de POWER solo con CERES SYN1deg (sin el empalme SRB → CERES de 2001)
    tend_pw_ceres = tendencias(tab, ("radiacion_power_kwh_m2_dia",), [(2001, 2025)])["2001-2025"]["radiacion_power_kwh_m2_dia"]
    if tend.get("1991-2025", {}).get("radiacion_power_kwh_m2_dia"):
        tend["1991-2025"]["radiacion_power_kwh_m2_dia"]["nota"] = (
            "Cruza el empalme de fuentes de NASA POWER (GEWEX SRB hasta 2000, CERES SYN1deg desde 2001; ver "
            "validacion_radiacion.empalme_srb_ceres_power): no debe leerse como cambio físico sin más. Sin el empalme: "
            "tendencias.radiacion_power_solo_ceres_2001_2025.")

    log("5. Climatologías")
    mens = mensual(tl, vl, te, ve, ch, pw)
    c9120 = climatologia(mens, 1991, 2020)
    c1625 = climatologia(mens, 2016, 2025)
    anom = anomalias(c1625, c9120)
    mm = np.array([int(m[5:7]) for m in mens["mes"]])
    parc = np.array(mens["parcial"])
    for v in ("tmedia", "tmax_media", "tmin_media", "precip_total", "precip_chirps"):
        base_m = np.array(c9120[v], float)[mm - 1]
        x = np.array([np.nan if y is None else y for y in mens[v]], float)
        a_ = x - base_m
        a_[parc] = np.nan  # un mes incompleto no tiene anomalía
        mens[f"anomalia_{v}"] = rl(a_, 1 if v in VARS_LLUVIA else 2)
    for per in tend.values():
        for v in VARS_LLUVIA:
            if per.get(v) and c9120.get(clave_anual(v)):
                m0 = c9120[clave_anual(v)]
                per[v]["pct_por_decada_vs_1991_2020"] = r(100 * per[v]["ols_por_decada"] / m0, 2)
                per[v]["pct_ic95_vs_1991_2020"] = [r(100 * x / m0, 2) for x in per[v]["ols_ic95"]]
    tab["anomalia_tmedia_vs_1991_2020"] = [r(x - c9120["tmedia_anual"]) if (x is not None and not p) else None
                                           for x, p in zip(tab["tmedia"], tab["parcial"])]

    climas = {}
    for p0, p1 in ((1961, 1990), (1971, 2000), (1981, 2010), (1991, 2020)):
        climas[f"{p0}-{p1}"] = {"era5land": climatologia(mens, p0, p1), "era5": era5_clim(te, ve, p0, p1)}
    if not args.sin_ideam:
        try:
            norm = ideam_normales()
            val_norm = validar_normales(norm, climas, chirps_clim)
            tend_norm = tendencia_normales(norm, climas)
        except Exception as e:
            log(f"   AVISO: normales IDEAM no disponibles: {e}")

    contraste_est = None
    if val_est and isinstance(val_est.get("tx"), dict) and val_norm:
        nx = [f for f in val_norm if f["variable"] == "tmax_media" and f["periodo"] in ("1981-2010", "1991-2020")]
        if nx and "media_estacion" in val_est["tx"]:
            m_n = float(np.mean([f["anual_ideam"] for f in nx]))
            contraste_est = {
                "media_tx_estacion_zaragoza": val_est["tx"]["media_estacion"],
                "media_normales_tmax_ideam_1981_2020": r(m_n),
                "normales_usadas": [f"{f['estacion']} ({f['municipio']}, {f['periodo']}): {f['anual_ideam']} °C" for f in nx],
                "diferencia_estacion_menos_normales": r(val_est["tx"]["media_estacion"] - m_n),
                "nota": ("La máxima de la estación automática Zaragoza queda por encima de la máxima media de las normales convencionales "
                         "cercanas; parte puede ser calentamiento reciente y parte el instrumento o el sitio. Por eso los umbrales "
                         "«equivalentes en la estación» son orientativos."),
            }
            if "tx" in est:
                _, xs_ = tx_estacion_validada(est, tl, te)
                assert abs(100 * np.mean(xs_ >= 32.0) - val_est["tx"]["frecuencia_tx_ge_32_estacion_pct"]) < 0.06, "serie Tmax de la estación distinta"
                dif_ = val_est["tx"]["media_estacion"] - m_n
                contraste_est.update({
                    "frecuencia_tx_ge_32_estacion_pct": val_est["tx"]["frecuencia_tx_ge_32_estacion_pct"],
                    "frecuencia_aprox_tx_ge_32_al_nivel_de_las_normales_pct": r(100 * np.mean(xs_ - dif_ >= 32.0), 1),
                    "nota_frecuencia_aprox": (f"Aproximación: se rebaja toda la distribución diaria de la estación en {dif_:.2f} °C (la diferencia con las "
                                              "normales) y se cuenta cuántos días llegarían a 32 °C. Supone un desplazamiento uniforme y mezcla periodos "
                                              f"distintos (estación {val_est['tx']['desde'][:4]}–{str(FIN_VALIDACION)[:4]}, normales 1981–2020): "
                                              "es orientativa."),
                })

    consist_lluvia = consistencia_lluvia(tab, mens, tend) if ch else None
    val_rad = validar_radiacion(mens, pw_meta, tab, rad_ideam, rad_meta) if pw else None

    # ---- distribución de Tmax para juzgar el umbral de 32 °C (serie filtrada)
    tx = vl["temperature_2m_max"]
    s9120 = (al >= 1991) & (al <= 2020)
    dist_tx = {
        "periodo": "1991-2020", **{f"p{q}": r(np.percentile(tx[s9120], q), 1) for q in (50, 90, 95, 99)},
        "max_1950_hoy": r(tx.max(), 1), "fecha_max": str(tl[int(np.argmax(tx))]),
        "dias_ge_32_total": int(np.sum(tx >= 32)), "anios_con_algun_dia_ge_32": int(len(np.unique(al[tx >= 32]))),
        "dias_ge_30_total": int(np.sum(tx >= 30)),
        "sin_filtro_de_picos": {"max_1950_hoy": r(vl_orig["temperature_2m_max"].max(), 1),
                                "fecha_max": str(tl[int(np.argmax(vl_orig["temperature_2m_max"]))]),
                                "dias_ge_32_total": int(np.sum(vl_orig["temperature_2m_max"] >= 32))},
        "umbral_local_p90_1961_1990": umbral_local,
        "frecuencia_gt_umbral_local_1961_1990_pct": r(100 * np.mean(tx[sb] > umbral_local), 2),
    }

    # ---- hallazgos (todas las cifras salen de los datos)
    T, TE = tend, tend_e
    t5, t8, t9 = T["1950-2025"]["tmedia"], T["1981-2025"]["tmedia"], T["1991-2025"]["tmedia"]
    e5, e8, e9 = TE["1950-2025"]["tmedia"], TE["1981-2025"]["tmedia"], TE["1991-2025"]["tmedia"]
    e8_24 = TE["1981-2024"]["tmedia"]
    x8, n8 = T["1981-2025"]["tmax_media"], T["1981-2025"]["tmin_media"]
    ex8, en8 = TE["1981-2024"]["tmax_media"], TE["1981-2024"]["tmin_media"]  # ERA5 hasta 2024: su Tmax/Tmin de 2025 no es comparable
    ic = lambda d, nd=2: f"IC 95 % {fmt(d['ols_ic95'][0], nd)} a {fmt(d['ols_ic95'][1], nd)}"  # noqa: E731
    tm_c = np.array([np.nan if x is None else x for x in tab["tmedia"]], float)
    tm_c[~completos] = np.nan
    i_max = int(np.nanargmax(tm_c))
    orden = np.argsort(-np.nan_to_num(tm_c, nan=-99))[:5]
    tme = np.array([np.nan if x is None else x for x in era5_anual["tmedia"]], float)
    tme[~completos] = np.nan
    i_max_e = int(np.nanargmax(tme))
    tx_b, tx_9120, tx_1625 = media_periodo("dias_tx90p", *BASE), media_periodo("dias_tx90p", 1991, 2020), media_periodo("dias_tx90p", 2016, 2025)
    tn_b, tn_1625 = media_periodo("noches_tn90p", *BASE), media_periodo("noches_tn90p", 2016, 2025)
    # TN90p: rango entre reanálisis (ERA5 desde 2025 no es comparable por la discontinuidad de su ciclo diurno)
    tn_per = [("1961-1990", *BASE), ("1991-2020", 1991, 2020), ("2016-2024", 2016, 2024), ("2016-2025", 2016, 2025)]
    p50n_l = Percentil90(tl, vl["temperature_2m_min"], q=0.5).umbral
    p50n_e = Percentil90(te, ve["temperature_2m_min"], q=0.5).umbral
    resumen_tn90p = {
        "noches_por_anio": {k: {"era5land": r(media_periodo("noches_tn90p", a0, a1), 1),
                                "era5": r(media_periodo("noches_tn90p", a0, a1, t=era5_anual), 1)} for k, a0, a1 in tn_per}
        | {"2024": {"era5land": tab["noches_tn90p"][tab["anio"].index(2024)], "era5": era5_anual["noches_tn90p"][era5_anual["anio"].index(2024)]}},
        "margen_p90_sobre_mediana_tmin_base_c": {"era5land": r(np.mean(p90n.umbral - p50n_l), 2), "era5": r(np.mean(p90n_e.umbral - p50n_e), 2)},
        "nota": ("Mismo método en los dos reanálisis (percentil 90 por día del calendario, ventana de 5 días, base 1961–1990, bootstrap en la "
                 "base). El valor de ERA5 en 2016–2025 incluye 2025, afectado por la discontinuidad de su ciclo diurno (Tmin no comparable): "
                 "compárese 2016–2024. margen_p90_sobre_mediana: cuántos °C separan en promedio el umbral de la mediana de la Tmin del mismo "
                 "día en la base; cuanto menor, menos calentamiento hace falta para que casi todas las noches superen el umbral."),
    }
    vtn = (val_est or {}).get("tn") if val_est else None
    vtm = (val_est or {}).get("t") if val_est else None
    tx90t = T["1981-2025"]["pct_tx90p"]
    tx90d = T["1981-2025"]["dias_tx90p"]
    q8, q9 = T["1981-2025"].get("precip_chirps"), T["1991-2025"].get("precip_chirps")
    ul_b, ul_1625 = media_periodo("dias_tmax_gt_umbral_local", *BASE), media_periodo("dias_tmax_gt_umbral_local", 2016, 2025)
    ul_t = T["1981-2025"]["dias_tmax_gt_umbral_local"]
    idx_2024 = tab["anio"].index(2024)

    hallazgos = [
        f"Calentamiento de la temperatura media del aire en la celda de Cartago: en 1981–2025, entre {fmt(t8['ols_por_decada'])} °C/década "
        f"(ERA5-Land; {ic(t8)}) y {fmt(e8['ols_por_decada'])} °C/década (ERA5; {ic(e8)}); en 1950–2025, entre {fmt(t5['ols_por_decada'])} "
        f"({ic(t5)}) y {fmt(e5['ols_por_decada'])} ({ic(e5)}). La diferencia entre los dos reanálisis es mayor que la incertidumbre "
        "estadística de cada uno: la tendencia depende del producto, y el valor de ERA5-Land no es el más fiable solo por ser el más bajo "
        "(ver validación).",
    ]
    def compara(a, b):  # a = ERA5, b = ERA5-Land (correlaciones)
        return "parecida" if abs(a - b) < 0.03 else ("mejor con ERA5" if a > b else "mejor con ERA5-Land")

    if val_est and isinstance(val_est.get("t"), dict) and "r_anomalias_mensuales_era5" in val_est["t"]:
        vt, vx = val_est["t"], val_est.get("tx", {})
        hz = val_est.get("homogeneidad_estacion", {}).get("t", {})
        txt_h = ""
        if hz.get("desde_2025_07", {}).get("dias"):
            dl_ = hz["desde_2025_07"]["estacion_menos_era5land"] - hz["hasta_2023"]["estacion_menos_era5land"]
            de_ = hz["desde_2025_07"]["estacion_menos_era5"] - hz["hasta_2023"]["estacion_menos_era5"]
            txt_h = (f" Se usa hasta {str(FIN_VALIDACION)[:4]}: desde julio de 2025 la estación cambia de nivel frente a los dos reanálisis a la vez "
                     f"({fmt(dl_, 1)} °C frente a ERA5-Land y {fmt(de_, 1)} °C frente a ERA5 en la media), señal de un cambio en la estación; "
                     "incluir esos meses rebaja artificialmente la correlación de ERA5-Land.")
        hallazgos.append(
            f"Frente a la estación IDEAM Zaragoza ({vt['dias_comunes']} días comunes, {vt['desde'][:4]}–{str(FIN_VALIDACION)[:4]}), ERA5 tiene menos "
            f"sesgo (media {fmt(vt['sesgo_era5_menos_estacion'], 1)} °C frente a {fmt(vt['sesgo_era5land_menos_estacion'], 1)} °C de ERA5-Land; máxima "
            f"{fmt(vx.get('sesgo_era5_menos_estacion'), 1)} frente a {fmt(vx.get('sesgo_era5land_menos_estacion'), 1)} °C). La variabilidad mensual de "
            f"la media se sigue de forma {compara(vt['r_anomalias_mensuales_era5'], vt['r_anomalias_mensuales_era5land'])} (r de anomalías "
            f"{vt['r_anomalias_mensuales_era5']} frente a {vt['r_anomalias_mensuales_era5land']}) y la de la máxima, "
            f"{compara(vx.get('r_anomalias_mensuales_era5', 0), vx.get('r_anomalias_mensuales_era5land', 0))} ({vx.get('r_anomalias_mensuales_era5')} "
            f"frente a {vx.get('r_anomalias_mensuales_era5land')}; r diaria {vx.get('r_diaria_era5')} frente a {vx.get('r_diaria_era5land')})."
            + txt_h + " ERA5-Land sigue como serie principal porque es la fuente pedida, tiene 0,1° y no sufre la discontinuidad de ERA5 "
            "desde mayo de 2025; ERA5 se publica completo como contraste.")
    if tend_norm and tend_norm["resumen"].get("tmedia"):
        rt = tend_norm["resumen"]["tmedia"]
        lista = "; ".join(f"{x['estacion'].split('  ')[0]} {fmt(x['tasa_ideam_c_por_decada'])} ({x['desde_periodo']} → {x['hasta_periodo']})"
                          for x in tend_norm["estaciones"] if x["variable"] == "tmedia")
        med, ml_, me_ = rt["tasa_ideam_mediana"], rt["tasa_era5land_mediana_mismos_periodos"], rt["tasa_era5_mediana_mismos_periodos"]
        cerca = "ERA5-Land" if abs(med - ml_) < abs(med - me_) else ("ERA5" if abs(med - me_) < abs(med - ml_) else "los dos por igual")
        hallazgos.append(
            f"Contraste con observaciones: las normales IDEAM sucesivas de {rt['n_estaciones']} estaciones del entorno (≤ {RADIO_NORMALES_TEND_KM} km, "
            f"≤ {ALT_NORMALES_TEND_M} m) implican para la temperatura media entre {fmt(rt['tasa_ideam_min'])} y {fmt(rt['tasa_ideam_max'])} °C/década "
            f"({lista}; mediana {fmt(med)}); entre los mismos periodos ERA5-Land da {fmt(ml_)} y ERA5 {fmt(me_)} °C/década (medianas). La mediana "
            f"observada queda más cerca de {cerca}, pero son pocas estaciones, con normales redondeadas a 0,1 °C, periodos solapados y "
            "posibles cambios de sitio: no basta para elegir entre los reanálisis.")
    hallazgos += [
        f"La tasa de ERA5-Land es mayor en los periodos recientes, {fmt(t5['ols_por_decada'])} (1950–2025), {fmt(t8['ols_por_decada'])} "
        f"(1981–2025) y {fmt(t9['ols_por_decada'])} °C/década (1991–2025; ajustado por autocorrelación "
        f"{fmt(t9['ols_ic95_ajustado_ar1'][0])} a {fmt(t9['ols_ic95_ajustado_ar1'][1])}), pero sin prueba formal de aceleración: "
        f"los intervalos se solapan. Con ERA5: {fmt(e5['ols_por_decada'])}, {fmt(e8['ols_por_decada'])} y {fmt(e9['ols_por_decada'])} "
        f"°C/década ({fmt(e8_24['ols_por_decada'])} en 1981–2024, sin el año afectado por su discontinuidad).",
        f"En 1981–2025 la máxima diaria sube {fmt(x8['ols_por_decada'])} °C/década según ERA5-Land ({ic(x8)}) y la mínima "
        f"{fmt(n8['ols_por_decada'])} ({ic(n8)}); con ERA5 en 1981–2024 (su Tmax y Tmin de 2025 no son comparables), "
        f"{fmt(ex8['ols_por_decada'])} ({ic(ex8)}) y {fmt(en8['ols_por_decada'])} ({ic(en8)}).",
        f"Año más cálido (años completos 1950–2025): {tab['anio'][i_max]} en ERA5-Land, con {tm_c[i_max]:.2f} °C de media en la celda "
        f"({fmt(tab['anomalia_tmedia_vs_1991_2020'][i_max])} °C sobre 1991–2020); le siguen "
        + ", ".join(f"{tab['anio'][i]} ({tm_c[i]:.2f})" for i in orden[1:]) + f". En ERA5 también es {tab['anio'][i_max_e]}.",
        f"El decenio 2016–2025 es {fmt(anom['tmedia_anual'])} °C más cálido que la normal 1991–2020 en la media, "
        f"{fmt(anom['tmax_media_anual'])} °C en la máxima y {fmt(anom['tmin_media_anual'])} °C en la mínima (ERA5-Land).",
        f"Días cálidos TX90p (ERA5-Land): {fmt(tx_b, 1, False)} días/año en la base 1961–1990 ({fmt(tx90_base, 1, False)} % de los días; 10 % por "
        f"construcción), {fmt(tx_9120, 1, False)} en 1991–2020 y {fmt(tx_1625, 1, False)} en 2016–2025, con {fmt(tab['dias_tx90p'][idx_2024], 0, False)} "
        f"en 2024; tendencia 1981–2025 {fmt(tx90t['ols_por_decada'], 1)} puntos porcentuales/década ({ic(tx90t, 1)}), o "
        f"{fmt(tx90d['ols_por_decada'], 1)} días/década.",
    ]
    tnr = resumen_tn90p["noches_por_anio"]
    txt_val_tn = ""
    if isinstance(vtn, dict) and "r_anomalias_mensuales_era5land" in vtn:
        txt_val_tn = (f" Úsese con cautela: la Tmin es la variable peor validada; frente a la estación Zaragoza, la r de anomalías mensuales es "
                      f"{vtn['r_anomalias_mensuales_era5land']} con ERA5-Land y {vtn['r_anomalias_mensuales_era5']} con ERA5"
                      + (f" (frente a {vtm['r_anomalias_mensuales_era5land']} de la media)" if isinstance(vtm, dict) and vtm.get('r_anomalias_mensuales_era5land') else "")
                      + f" y la r diaria {vtn['r_diaria_era5land']} y {vtn['r_diaria_era5']}.")
    mg = resumen_tn90p["margen_p90_sobre_mediana_tmin_base_c"]
    hallazgos.append(
        f"Noches cálidas TN90p (Tmin sobre el percentil 90 de 1961–1990): el valor depende mucho del reanálisis. En 2016–2024, entre "
        f"{fmt(tnr['2016-2024']['era5land'], 0, False)} (ERA5-Land) y {fmt(tnr['2016-2024']['era5'], 0, False)} (ERA5) noches/año, frente a "
        f"{fmt(tnr['1961-1990']['era5land'], 1, False)} y {fmt(tnr['1961-1990']['era5'], 1, False)} en la base y {fmt(tnr['1991-2020']['era5land'], 0, False)}–"
        f"{fmt(tnr['1991-2020']['era5'], 0, False)} en 1991–2020; en 2016–2025 ERA5-Land da {fmt(tnr['2016-2025']['era5land'], 0, False)} (ERA5 "
        f"{fmt(tnr['2016-2025']['era5'], 0, False)}, con 2025 no comparable) y en 2024 entre {fmt(tnr['2024']['era5land'], 0, False)} y "
        f"{fmt(tnr['2024']['era5'], 0, False)} noches; tendencia {fmt(T['1981-2025']['pct_tn90p']['ols_por_decada'], 1)} puntos porcentuales/década "
        f"en 1981–2025 con ERA5-Land y {fmt(TE['1981-2024']['pct_tn90p']['ols_por_decada'], 1)} con ERA5 en 1981–2024." + txt_val_tn +
        f" Además, la Tmin varía poco de un día a otro: el umbral queda solo {fmt(mg['era5land'], 1, False)} °C (ERA5-Land) y "
        f"{fmt(mg['era5'], 1, False)} °C (ERA5) sobre la mediana de la base, así que un calentamiento moderado basta para que la mayoría de las "
        "noches lo superen. Sirve como índice de frecuencia de largo plazo (más noches cálidas que en 1961–1990), no para noches concretas "
        "ni como cifra exacta.")
    if val_est and isinstance(val_est.get("tx"), dict) and "destreza_dias_calidos" in val_est["tx"]:
        dz = val_est["tx"]["destreza_dias_calidos"]
        ul_l = dz.get("umbral_local_era5land", {})
        ul_e = dz.get("umbral_local_era5", {})
        cl, ce = ul_l.get("contingencia", {}), ul_e.get("contingencia", {})
        hallazgos.append(
            f"Días cálidos con umbral local (Tmax de ERA5-Land > {umbral_local} °C, el percentil 90 de 1961–1990): {fmt(ul_b, 1, False)} días/año "
            f"en 1961–1990 y {fmt(ul_1625, 1, False)} en 2016–2025; tendencia 1981–2025 {fmt(ul_t['ols_por_decada'], 1)} días/década ({ic(ul_t, 1)}). "
            "Sirve como índice climatológico de frecuencia, NO para identificar días cálidos concretos ni para alertas: frente a la estación "
            f"Zaragoza (días con ≥ {ul_l.get('equivalente_estacion_misma_frecuencia')} °C, la misma frecuencia) detecta el "
            f"{fmt(100 * cl['tasa_deteccion_pod'], 0, False)} % de sus días cálidos y el {fmt(100 * cl['tasa_falsas_alarmas_far'], 0, False)} % "
            f"de sus avisos son falsos (ERA5 con su propio umbral de {umbral_local_era5} °C: {fmt(100 * ce['tasa_deteccion_pod'], 0, False)} % y "
            f"{fmt(100 * ce['tasa_falsas_alarmas_far'], 0, False)} %); en el 10 % más cálido de cada serie, ERA5-Land acierta el "
            f"{fmt(100 * dz['decil_superior']['era5land']['tasa_deteccion_pod'], 0, False)} % de los días de la estación y ERA5 el "
            f"{fmt(100 * dz['decil_superior']['era5']['tasa_deteccion_pod'], 0, False)} %."
            + (f" No se puede evaluar si sigue la frecuencia anual de la estación: solo hay "
               f"{ul_l['correlacion_frecuencia_anual']['n_anios']} años con ≥ 300 días comunes (se exigen {MIN_ANIOS_R_FRECUENCIA})."
               if ul_l.get("correlacion_frecuencia_anual") and not ul_l["correlacion_frecuencia_anual"]["informativa"] else
               (f" La correlación de su frecuencia anual con la de la estación es {ul_l['r_frecuencia_anual']} "
                f"(n = {ul_l['correlacion_frecuencia_anual']['n_anios']} años; ERA5: {ul_e.get('r_frecuencia_anual')})."
                if ul_l.get("r_frecuencia_anual") is not None else "")))
    if val_est and isinstance(val_est.get("tx"), dict) and "frecuencia_tx_ge_32_estacion_pct" in val_est["tx"]:
        v = val_est["tx"]
        hallazgos.append(
            f"32 °C no es un umbral útil aquí. En ERA5-Land, quitados los picos espurios, ningún día llega a 32 °C entre 1950 y "
            f"{str(tl[-1])[:4]} ({dist_tx['dias_ge_32_total']} días; máximo {dist_tx['max_1950_hoy']} °C el {dist_tx['fecha_max']}; sin el filtro "
            f"eran {dist_tx['sin_filtro_de_picos']['dias_ge_32_total']} días y {dist_tx['sin_filtro_de_picos']['max_1950_hoy']} °C, todos "
            f"artefactos). En la estación automática Zaragoza 32 °C es un día corriente: lo alcanza el {v['frecuencia_tx_ge_32_estacion_pct']} % de "
            f"los días y la mediana de la máxima es {v['percentiles_tx_estacion']['p50']} °C"
            + (f"; pero esa estación no representa por sí sola el clima de Cartago: su máxima media supera en ≈ "
               f"{contraste_est['diferencia_estacion_menos_normales']:.1f} °C la de las normales convencionales cercanas "
               f"({contraste_est['media_tx_estacion_zaragoza']:.1f} frente a {contraste_est['media_normales_tmax_ideam_1981_2020']:.1f} °C) y no es "
               "homogénea en el tiempo. Rebajada a ese nivel (aproximación con un desplazamiento uniforme), llegaría a 32 °C ≈ "
               f"{contraste_est['frecuencia_aprox_tx_ge_32_al_nivel_de_las_normales_pct']:.0f} % de los días: aun así no es un umbral de calor extremo"
               if contraste_est and contraste_est.get("frecuencia_aprox_tx_ge_32_al_nivel_de_las_normales_pct") is not None else "")
            + ". Se propone en su lugar el umbral local o TX90p.")
    hallazgos.append(
        f"Control de calidad: la temperatura horaria de ERA5-Land tiene picos espurios de una hora (hasta "
        f"{fmt(picos['mayores'][0]['t_original'] - picos['mayores'][0]['t_reparada'], 1, False)} °C sobre la media de sus vecinas, con caída "
        f"simultánea de la humedad, solo de día, entre las {min(map(int, picos['por_hora_local']))} y las {max(map(int, picos['por_hora_local']))} h, "
        f"y ausentes en ERA5: {(ref_era5 or {}).get('umbral_2.5', {}).get('era5', 's. d.')} frente a "
        f"{(ref_era5 or {}).get('umbral_2.5', {}).get('era5land', 's. d.')} en 2015–2024): {picos['horas_corregidas']} horas en {picos['dias_afectados']} días, "
        f"{picos['por_decenio'].get('2020s', 0)} de ellas en 2020–{str(tl[-1])[:4]}. Se filtraron antes de agregar a día. Cambian el récord y "
        f"TXx (2024: {picos['efecto']['txx_por_anio']['2024']['sin_filtro']} → {picos['efecto']['txx_por_anio']['2024']['filtrada']} °C) "
        f"pero apenas la media de la máxima (tendencia 1981–2025 "
        f"{fmt(sens_picos['sin_filtro']['tmax_media_ols_1981_2025_c_por_decada'], 3)} sin filtro, "
        f"{fmt(sens_picos['curvatura_2.5_con_HR (producto)']['tmax_media_ols_1981_2025_c_por_decada'], 3)} con filtro). La tendencia de TXx no "
        f"es robusta: {fmt(sens_picos['sin_filtro']['txx_ols_1981_2025_c_por_decada'])} °C/década sin filtro y entre "
        f"{fmt(min(v_['txx_ols_1981_2025_c_por_decada'] for k_, v_ in sens_picos.items() if k_ != 'sin_filtro'))} y "
        f"{fmt(max(v_['txx_ols_1981_2025_c_por_decada'] for k_, v_ in sens_picos.items() if k_ != 'sin_filtro'))} según el criterio de filtrado.")
    if q8 and val_norm is not None:
        cn = [f for f in val_norm if f["variable"] == "precip_total" and f.get("municipio") == "Cartago" and f["periodo"] == "1991-2020"
              and f.get("cociente_chirps_ideam")]
        pz = (val_est or {}).get("p", {}) if val_est else {}
        txt_cn = ("; en su píxel, CHIRPS da entre " + f"{min(f['cociente_chirps_ideam'] for f in cn):.2f} y "
                  f"{max(f['cociente_chirps_ideam'] for f in cn):.2f} veces las normales IDEAM 1991–2020 de las estaciones de Cartago ("
                  + ", ".join(f"{f['estacion']} {f['anual_ideam']:.0f} mm" for f in cn) + ")") if cn else ""
        txt_z = (f" y {pz['cociente_chirps_estacion']:.2f} veces la estación automática Zaragoza en {pz['meses_comunes_chirps']} meses "
                 f"(r = {pz['r_mensual_chirps']})") if pz.get("cociente_chirps_estacion") else ""
        hallazgos.append(
            f"Lluvia de referencia (CHIRPS v3 sobre la huella urbana): normal 1991–2020 de {c9120['precip_chirps_anual']:.0f} mm/año"
            + (f", con una incertidumbre de al menos ±{100 * max(abs(f['cociente_chirps_ideam'] - 1) for f in cn):.0f} %" if cn else "")
            + f"{txt_cn}{txt_z}. Régimen bimodal. Sin tendencia: {fmt(q8['ols_por_decada'], 1)} mm/década por MCO "
            f"y {fmt(q8['sen_por_decada'], 1)} por Sen en 1981–2025 ({ic(q8, 1)}; Mann-Kendall p {fmt_p(q8['mk_p'])}); 2016–2025 frente a "
            f"1991–2020: {fmt(anom['precip_chirps_anual_pct'], 1)} %.")
    if consist_lluvia:
        cl_ = consist_lluvia
        pz = (val_est or {}).get("p", {}) if val_est else {}
        rn = resumen_normales(val_norm).get("precip_total", {}) if val_norm else {}
        hallazgos.append(
            f"La lluvia de ERA5 no es apta para decisiones: su normal 1991–2020 es {c9120['precip_anual']:.0f} mm/año"
            + (f" (≈ {rn['cociente_medio_era5_ideam']:.1f} veces las normales IDEAM)" if rn else "")
            + f" y tampoco sigue la variabilidad (r anual con CHIRPS {cl_['r_anual_era5_chirps']}, r de anomalías mensuales "
            f"{cl_['r_anomalias_mensuales_era5_chirps']}"
            + (f"; r diaria con la estación Zaragoza {pz['r_diaria']}, que llueve ≥ 1 mm el {pz['dias_ge_1mm_estacion_pct']} % de los días "
               f"frente al {pz['dias_ge_1mm_era5_pct']} % de ERA5" if pz.get("r_diaria") is not None else "")
            + f"). Su secado de {fmt(cl_['tendencia_1981_2025_pct_por_decada']['era5']['valor'], 1)} %/década en 1981–2025 lo contradice CHIRPS "
            f"({fmt(cl_['tendencia_1981_2025_pct_por_decada']['chirps']['valor'], 1)} %/década). precip_total, rx1day y rx5day quedan solo por "
            "trazabilidad.")
    if val_rad and "1991-2020" in val_rad["periodos"]:
        pr_ = val_rad["periodos"]["1991-2020"]
        cq = val_rad["climatologia_mensual_1991_2020"]["cociente"]
        ri = val_rad.get("estacion_ideam")
        if ri:
            cz, sp_, ent = ri["comparacion_climatologia_1991_2020"], ri["sensibilidad_al_periodo"], ri["estaciones_entorno"]["estaciones"]
            otras = [x for x in ent if _sin_tildes(x["estacion"]) != "zaragoza"]
            mz = ri["mensual_kwh_m2_dia"]
            hallazgos.append(
                f"Radiación solar: la medición abierta más cercana, la climatología de la estación automática IDEAM Zaragoza "
                f"({ri['estacion']['distancia_km']:.1f} km del centro, {ri['estacion']['altitud_m']:.0f} m; sensor calibrado, datos.gov.co {IDEAM_RAD_DS}), "
                f"da {ri['anual_kwh_m2_dia']:.2f} kWh/m²/día de media anual (de {min(mz):.2f} en {MESES_NOMBRE[int(np.argmin(mz))]} a {max(mz):.2f} en "
                f"{MESES_NOMBRE[int(np.argmax(mz))]}). ERA5 la subestima un {abs(cz['diferencia_era5_pct']):.0f} % ({cz['era5']:.2f} en 1991–2020) y NASA "
                f"POWER un {abs(cz['diferencia_power_pct']):.0f} % ({cz['nasa_power']:.2f})"
                + (f"; ningún año de ERA5 ({ri['maximo_anual']['era5']['desde']}–{ri['maximo_anual']['era5']['hasta']}, máximo "
                   f"{ri['maximo_anual']['era5']['valor']:.2f}) ni de POWER ({ri['maximo_anual']['nasa_power']['desde']}–"
                   f"{ri['maximo_anual']['nasa_power']['hasta']}, máximo {ri['maximo_anual']['nasa_power']['valor']:.2f}) llega a esa media"
                   if max(ri['maximo_anual']['era5']['valor'], ri['maximo_anual']['nasa_power']['valor']) < ri['anual_kwh_m2_dia'] else "")
                + ". El IDEAM no publica el "
                f"periodo de su climatología, pero con cualquier decenio de 1984–{ri['maximo_anual']['era5']['hasta']} el cociente de ERA5 queda entre "
                f"{sp_['era5']['min']:.2f} y {sp_['era5']['max']:.2f} y el de POWER entre {sp_['nasa_power']['min']:.2f} y {sp_['nasa_power']['max']:.2f}. "
                "Las celdas de ERA5 (0,25°) y POWER (1°"
                + (f"; elevación media {val_rad['elevacion_media_celda_power_merra2_m']:.0f} m en su celda MERRA-2" if val_rad.get("elevacion_media_celda_power_merra2_m") else "")
                + ") promedian el fondo del valle con laderas y cordillera"
                + (f", donde el IDEAM mide menos: las otras {len(otras)} estaciones a ≤ {RADIO_RAD_ENTORNO_KM} km, todas más altas "
                   f"({min(x['altitud_m'] for x in otras):.0f}–{max(x['altitud_m'] for x in otras):.0f} m), dan entre {min(x['anual'] for x in otras):.2f} y "
                   f"{max(x['anual'] for x in otras):.2f}"
                   if otras and all(x['altitud_m'] > ri['estacion']['altitud_m'] and x['anual'] < ri['anual_kwh_m2_dia'] for x in otras) else
                   (f"; las otras estaciones del IDEAM a ≤ {RADIO_RAD_ENTORNO_KM} km miden entre {min(x['anual'] for x in otras):.2f} y "
                    f"{max(x['anual'] for x in otras):.2f}" if otras else ""))
                + ". Para valores absolutos (p. ej., dimensionar sistemas solares) úsese la medición del IDEAM; ERA5 y POWER, solo para anomalías.")
        else:
            hallazgos.append(
                f"Radiación solar: la normal 1991–2020 está entre {pr_['era5']:.2f} kWh/m²/día (ERA5) y {pr_['nasa_power']:.2f} (NASA POWER, "
                f"satelital); ERA5 queda {100 * (1 - pr_['cociente_era5_power']):.0f} % por debajo, con cocientes mensuales entre {min(cq):.2f} y "
                f"{max(cq):.2f}. No se pudo leer la climatología medida del IDEAM ({IDEAM_RAD_DS}) en esta ejecución: el valor absoluto es "
                "incierto y no debe usarse sin más para dimensionar sistemas solares.")
    if val_norm:
        rn = resumen_normales(val_norm)
        if rn.get("tmedia") and rn.get("tmax_media"):
            hallazgos.append(
                f"Sesgos frente a las normales IDEAM cercanas (≤ 30 km, ≤ 1250 m): media {fmt(rn['tmedia']['diferencia_media_era5land_menos_ideam'], 1)} °C "
                f"en ERA5-Land y {fmt(rn['tmedia']['diferencia_media_era5_menos_ideam'], 1)} °C en ERA5; máxima "
                f"{fmt(rn['tmax_media']['diferencia_media_era5land_menos_ideam'], 1)} y {fmt(rn['tmax_media']['diferencia_media_era5_menos_ideam'], 1)} °C; "
                + (f"humedad relativa {fmt(rn['humedad_media']['diferencia_media_era5land_menos_ideam'], 1)} puntos en ERA5-Land. " if rn.get("humedad_media") else "")
                + "Los dos reanálisis sirven para anomalías e índices por percentil, no para umbrales absolutos; la tasa de tendencia depende "
                "del reanálisis (úsese el rango de tendencias.rango_entre_reanalisis_tmedia_c_por_decada).")
    if vecinas:
        cv = vecinas["celdas"]
        hallazgos.append(
            f"La celda de ERA5-Land (4,65–4,75 N; −75,95 a −75,85) contiene el {100 * frac_urb:.0f} % del área urbana; el norte y el aeropuerto "
            f"caen en la celda vecina. Con las cuatro celdas corregidas a la misma elevación ({vecinas['elevacion_comun_m']:.0f} m), la media "
            f"1991–2020 varía entre {min(x['tmedia_1991_2020'] for x in cv):.2f} y {max(x['tmedia_1991_2020'] for x in cv):.2f} °C (la del "
            f"producto, {vecinas['tmedia_1991_2020_serie_del_producto_sin_filtrar']:.2f} °C) y la tendencia de Sen 1991–2020 entre "
            f"{fmt(min(x['sen_tmedia_por_decada_1991_2020'] for x in cv))} y {fmt(max(x['sen_tmedia_por_decada_1991_2020'] for x in cv))} °C/década.")

    # ---- cifras para los textos de limitaciones y definiciones (todas salen de los datos)
    tm_l_ = np.array([np.nan if x is None else x for x in tab["tmedia"]], float)
    tm_e_ = np.array([np.nan if x is None else x for x in era5_anual["tmedia"]], float)
    quinq = [float(np.nanmean((tm_l_ - tm_e_)[completos & (anios >= a) & (anios <= a + 4)])) for a in range(1950, 2026, 5)]
    rn_ = resumen_normales(val_norm) if val_norm else {}
    dz_ = ((val_est or {}).get("tx") or {}).get("destreza_dias_calidos", {}) if val_est else {}
    c_l_ = (dz_.get("umbral_local_era5land") or {}).get("contingencia")
    cn_ = [f["cociente_chirps_ideam"] for f in (val_norm or []) if f["variable"] == "precip_total" and f.get("municipio") == "Cartago"
           and f["periodo"] == "1991-2020" and f.get("cociente_chirps_ideam")]
    rad_ = (val_rad or {}).get("periodos", {}).get("1991-2020")
    disc_ = (disc_era5 or {}).get("resumen_2015_2024_vs_desde_2025_05")
    txt_lluvia_x = (f"≈ {rn_['precip_total']['cociente_medio_era5_ideam']:.1f} veces la de los pluviómetros del IDEAM"
                    if rn_.get("precip_total") else "muy superior a la de los pluviómetros del IDEAM")
    txt_rad_pct = (f"{100 * (1 - rad_['cociente_era5_power']):.0f} % por debajo de NASA POWER en 1991–2020" if rad_ else "sin contraste disponible")
    ri_ = (val_rad or {}).get("estacion_ideam")
    if ri_:
        cz_ = ri_["comparacion_climatologia_1991_2020"]
        txt_rad_ideam = (f"{abs(cz_['diferencia_era5_pct']):.0f} % por debajo de la climatología medida de la estación IDEAM Zaragoza, "
                         f"{ri_['anual_kwh_m2_dia']:.2f} kWh/m²/día con periodo no publicado, y {txt_rad_pct}")
        lim_rad = (f"La radiación solar absoluta de los productos en rejilla no sirve para dimensionar: frente a la climatología medida de la estación "
                   f"automática IDEAM Zaragoza ({ri_['anual_kwh_m2_dia']:.2f} kWh/m²/día, sensor calibrado; datos.gov.co {IDEAM_RAD_DS}), ERA5 queda "
                   f"{abs(cz_['diferencia_era5_pct']):.0f} % por debajo y NASA POWER {abs(cz_['diferencia_power_pct']):.0f} % (validacion_radiacion."
                   "estacion_ideam). El IDEAM no publica el periodo de esa climatología ni su serie mensual, así que no sirve para validar la "
                   "variabilidad ni la tendencia. La tendencia de POWER que cruza 2001 mezcla dos fuentes (GEWEX SRB → CERES SYN1deg; "
                   "validacion_radiacion.empalme_srb_ceres_power). Las anomalías son más robustas que el valor absoluto.")
    else:
        txt_rad_ideam = txt_rad_pct
        lim_rad = (f"La radiación solar absoluta es incierta: ERA5 queda {txt_rad_pct} (satelital, celda de 1°); en esta ejecución no se pudo "
                   f"leer la climatología medida del IDEAM (datos.gov.co {IDEAM_RAD_DS}). Las anomalías son más robustas que el valor absoluto.")
    txt_chirps_err = (f"va de {100 * (min(cn_) - 1):+.0f} % a {100 * (max(cn_) - 1):+.0f} % frente a las normales IDEAM 1991–2020 de las estaciones "
                      "de Cartago (en el píxel de cada una)" if cn_ else "desconocida: no hay normales de Cartago para contrastar")
    lim_tend = (f"La tendencia depende del reanálisis: en 1981–2025 ERA5 calienta {e8['ols_por_decada'] / t8['ols_por_decada']:.1f} veces lo que "
                f"ERA5-Land ({fmt(e8['ols_por_decada'])} frente a {fmt(t8['ols_por_decada'])} °C/década), y la diferencia ERA5-Land − ERA5 de la "
                f"media anual va de {min(quinq):+.2f} a {max(quinq):+.2f} °C según el quinquenio "
                "(contraste_era5.diferencia_era5land_menos_era5_tmedia_por_quinquenio). ERA5 tiene menos sesgo frente a la estación Zaragoza y a "
                "las normales IDEAM, pero las tendencias implícitas en las normales sucesivas quedan más cerca de ERA5-Land "
                "(validacion_ideam.tendencia_observada_normales). Con estos datos no se puede decidir cuál tendencia es la correcta: úsese el rango.")
    vtn_ = ((val_est or {}).get("tn") or {}) if val_est else {}
    lim_destreza = ("Los índices de calor (TX90p, TN90p, días sobre el umbral local) tienen poca destreza día a día" +
                    (f": frente a la estación Zaragoza, el umbral local de ERA5-Land detecta el {100 * c_l_['tasa_deteccion_pod']:.0f} % de sus "
                     f"días cálidos y el {100 * c_l_['tasa_falsas_alarmas_far']:.0f} % de sus avisos son falsos" if c_l_ else "") +
                    (f". TN90p es el más incierto: la Tmin es la variable peor validada (r de anomalías mensuales con la estación "
                     f"{vtn_['r_anomalias_mensuales_era5land']} en ERA5-Land y {vtn_['r_anomalias_mensuales_era5']} en ERA5; r diaria "
                     f"{vtn_['r_diaria_era5land']}) y su valor cambia mucho entre reanálisis (contraste_era5.resumen_tn90p)"
                     if vtn_.get("r_anomalias_mensuales_era5land") is not None else
                     ". TN90p cambia mucho entre reanálisis (contraste_era5.resumen_tn90p)") +
                    ". Son índices climatológicos de frecuencia para periodos largos, no herramientas de alerta.")
    lim_disc = ("Desde mayo de 2025 la temperatura horaria de ERA5 en Open-Meteo cambia de ciclo diurno" +
                (f" (hora media del máximo {disc_['hora_media_del_maximo_era5'][0]} → {disc_['hora_media_del_maximo_era5'][1]} h; amplitud "
                 f"Tmax − Tmedia {disc_['amplitud_tmax_menos_tmedia_era5'][0]} → {disc_['amplitud_tmax_menos_tmedia_era5'][1]} °C)" if disc_ else "") +
                ", sin cambio en ERA5-Land y sin documentación de Open-Meteo: la Tmax y la Tmin de ERA5 de 2025–2026 no son comparables con las "
                "anteriores (contraste_era5.discontinuidad_2025). Podría afectar también la lluvia y la radiación diarias de ERA5 de esos años (no verificado).")

    txt_desc_rad = ""
    if ri_:
        _cz = ri_["comparacion_climatologia_1991_2020"]
        _d = sorted([abs(_cz["diferencia_power_pct"]), abs(_cz["diferencia_era5_pct"])])
        txt_desc_rad = f" y la radiación solar, entre un {_d[0]:.0f} y un {_d[1]:.0f} % por debajo de la medida en la estación IDEAM Zaragoza"

    # ---- salida
    ult = str(tl[-1])
    anio_parcial = int(ult[:4]) if tab["parcial"][-1] else None
    hoy = hoy_bogota().isoformat()
    attr_power = ("The data was obtained from National Aeronautics and Space Administration (NASA) Langley Research Center's Prediction "
                  f"Of Worldwide Energy Resources (POWER) project funded through the NASA Earth Science Division. POWER Monthly and Annual "
                  f"API {((pw_meta or {}).get('api') or {}).get('version', '')}, consultada el {hoy}.")
    salida = {
        "titulo": "Clima de Cartago 1950–2026 (reanálisis ERA5-Land y ERA5; lluvia CHIRPS v3; radiación NASA POWER)",
        "descripcion": ("Temperatura, lluvia, radiación solar y humedad de la celda de reanálisis que cubre Cartago, resumidas por año y por mes, "
                        "con tendencias e índices de calor. Un reanálisis combina un modelo meteorológico con observaciones: describe mejor la "
                        "variabilidad y los cambios en el tiempo que los valores absolutos, que no son los de un termómetro en la ciudad (aquí la "
                        f"temperatura queda varios grados por debajo de la que mide el IDEAM{txt_desc_rad}), y la tasa de "
                        "calentamiento cambia según el reanálisis, así que se da como rango. La cantidad de lluvia sale de CHIRPS, que combina "
                        "satélite y pluviómetros."),
        "licencia_producto": ("CC BY-SA 4.0. El archivo incorpora material derivado de datos del IDEAM publicados con CC BY-SA 4.0: el bloque "
                              "validacion_ideam, validacion_radiacion.estacion_ideam y el umbral de dias_tmax_ge_umbral_eq32, calibrado con la "
                              "estación Zaragoza. Las demás fuentes "
                              "(Open-Meteo, Copernicus, CHIRPS, NASA POWER y ESA WorldCover, todas CC BY 4.0) admiten esa licencia. La geometría de "
                              "OpenStreetMap (ODbL) solo se usa para calcular pesos espaciales (obra producida), lo que exige atribuirla. Es "
                              "una interpretación de las licencias, no asesoría jurídica."),
        "campos_no_aptos_para_decisiones": {
            ("anual.precip_total, anual.rx1day, anual.rx5day, mensual.precip_total, mensual.anomalia_precip_total, "
             "climatologia_mensual.*.precip_total, climatologia_mensual.*.precip_anual, climatologia_mensual.anomalia_2016_2025_vs_1991_2020."
             "precip_total_pct / precip_anual_pct, tendencias.periodos.*.precip_total (con su pct_por_decada_vs_1991_2020)"):
                f"lluvia de ERA5: {txt_lluvia_x} y con una variabilidad que no se parece a la observada (ver consistencia_lluvia_era5); "
                "úsese precip_chirps",
            ("anual.radiacion_kwh_m2_dia, mensual.radiacion_kwh_m2_dia, climatologia_mensual.*.radiacion_kwh_m2_dia (valores absolutos)"):
                (f"radiación de ERA5: {txt_rad_ideam}; sirve para anomalías, no para dimensionar sistemas solares"),
            ("anual.radiacion_power_kwh_m2_dia, mensual.radiacion_power_kwh_m2_dia, climatologia_mensual.*.radiacion_power_kwh_m2_dia "
             "(valores absolutos)"):
                ((f"radiación de NASA POWER: {abs(ri_['comparacion_climatologia_1991_2020']['diferencia_power_pct']):.0f} % por debajo de la "
                  "climatología medida de la estación IDEAM Zaragoza; para dimensionar úsese esa medición (validacion_radiacion.estacion_ideam)")
                 if ri_ else "radiación satelital de 1°, sin contraste con una medición local en esta ejecución"),
            "anual.dias_tmax_ge_32": "siempre 0 con ERA5-Land filtrado: no informa",
            "anual.txx": ("valor de reanálisis sesgado en frío y sensible al filtro de picos horarios: su tendencia no es robusta "
                          "(control_calidad.sensibilidad_filtro_picos)"),
        },
        "fuente": {
            "nombre": ("ERA5-Land (temperatura y humedad) y ERA5 (lluvia y radiación), ECMWF / Copernicus Climate Change Service, vía Open-Meteo "
                       "Historical Weather API; lluvia de referencia CHIRPS v3 (Climate Hazards Center, UCSB); radiación de referencia NASA POWER"),
            "url": "https://open-meteo.com/en/docs/historical-weather-api",
            "licencia": ("CC BY 4.0 (Open-Meteo); CC-BY (Copernicus Climate Data Store); CC BY 4.0 (CHIRPS v3, NASA POWER, ESA WorldCover); "
                         "ODbL (OpenStreetMap, solo pesos espaciales); IDEAM CC BY-SA 4.0 (validación y umbral eq32). Producto: CC BY-SA 4.0"),
            "cita": ("Muñoz-Sabater, J. et al. (2021). ERA5-Land: a state-of-the-art global reanalysis dataset for land applications. "
                     "Earth Syst. Sci. Data 13, 4349–4383. doi:10.5194/essd-13-4349-2021. Hersbach, H. et al. (2020). The ERA5 global "
                     "reanalysis. Q. J. R. Meteorol. Soc. 146, 1999–2049. doi:10.1002/qj.3803. Funk, C. et al. (2026). The Climate Hazards Center "
                     "Infrared Precipitation with Stations, Version 3. Sci. Data 13, 718. doi:10.1038/s41597-026-07096-4. Datos: Open-Meteo.com (CC BY 4.0)."),
            "atribucion": ("Weather data by Open-Meteo.com (https://open-meteo.com/). Contains modified Copernicus Climate Change Service "
                           f"information {hoy_bogota().year}. Neither the European Commission nor ECMWF is responsible for any use that may be "
                           "made of the Copernicus information or data it contains. Lluvia: CHIRPS v3, Climate Hazards Center, UC Santa Barbara "
                           f"(CC BY 4.0). Radiación de referencia: {attr_power} Huella urbana: © colaboradores de OpenStreetMap (ODbL); © ESA "
                           "WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium. "
                           "Validación: IDEAM, datos abiertos de datos.gov.co (CC BY-SA 4.0)."),
            "nota_atribucion": ("La frase «Contains modified Copernicus Climate Change Service information» y la exención de responsabilidad "
                                "provienen de la licencia Copernicus anterior a la CC-BY (vigente hasta el 2 de julio de 2025); se mantienen como "
                                "buena práctica. Open-Meteo exige «Weather data by Open-Meteo.com» con enlace. NASA POWER pide además avisar a "
                                "larc-power-project@mail.nasa.gov al publicar o redistribuir sus datos."),
        },
        "fuentes": [
            {"nombre": "ERA5-Land hourly data from 1950 to present (C3S/ECMWF)", "url": "https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land",
             "doi": "10.24381/cds.e2161bac", "licencia": "CC-BY",
             "variables": "temperatura a 2 m (horaria y diaria: media, máxima, mínima), humedad relativa",
             "cita": "Muñoz-Sabater et al. (2021), Earth Syst. Sci. Data 13, 4349–4383, doi:10.5194/essd-13-4349-2021"},
            {"nombre": "ERA5 hourly data on single levels from 1940 to present (C3S/ECMWF)", "url": "https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels",
             "doi": "10.24381/cds.adbb2d47", "licencia": "CC-BY", "variables": "precipitación diaria, radiación de onda corta diaria; temperatura y humedad como contraste",
             "cita": ("Hersbach et al. (2020), Q. J. R. Meteorol. Soc. 146, 1999–2049, doi:10.1002/qj.3803; "
                      "Bell et al. (2021), Q. J. R. Meteorol. Soc. 147, 4186–4227, doi:10.1002/qj.4174 (extensión 1950–1978)")},
            {"nombre": "Open-Meteo Historical Weather API", "url": "https://archive-api.open-meteo.com/v1/archive", "licencia": "CC BY 4.0",
             "cita": "Weather data by Open-Meteo.com", "licencia_url": "https://open-meteo.com/en/licence"},
            {"nombre": "CHIRPS v3.0 (Climate Hazards Center InfraRed Precipitation with Stations), mensual global", "url": CHIRPS_DIR,
             "doi": "10.15780/G2JQ0P", "licencia": "CC BY 4.0", "licencia_url": "https://www.chc.ucsb.edu/data/chirps3",
             "variables": "precipitación mensual (precip_chirps)",
             "cita": ("Funk, C., Peterson, P., Harrison, L. et al. (2026). The Climate Hazards Center Infrared Precipitation with Stations, "
                      "Version 3. Scientific Data 13, 718. doi:10.1038/s41597-026-07096-4")},
            {"nombre": "NASA POWER (Prediction Of Worldwide Energy Resources), Monthly and Annual API, ALLSKY_SFC_SW_DWN",
             "url": "https://power.larc.nasa.gov/", "licencia": "CC BY 4.0", "licencia_url": "https://power.larc.nasa.gov/docs/referencing/",
             "variables": "radiación solar global en superficie mensual (radiacion_power_kwh_m2_dia), 1984→; GEWEX SRB 1984–2000 y CERES SYN1deg 2001→, 1°",
             "cita": attr_power},
            {"nombre": "OpenStreetMap: polígonos de las Comunas 1–7 de Cartago (js/datos-osm.js)", "url": "https://www.openstreetmap.org/copyright",
             "licencia": "ODbL 1.0", "uso": "solo pesos espaciales (fracción urbana de la celda ERA5-Land y pesos de los píxeles CHIRPS)",
             "cita": "© colaboradores de OpenStreetMap"},
            {"nombre": "ESA WorldCover 10 m 2021 v200: huella construida de Zaragoza (datos/zaragoza.json)", "url": "https://esa-worldcover.org/",
             "doi": "10.5281/zenodo.7254221", "licencia": "CC BY 4.0", "uso": "solo pesos espaciales (igual que OSM)",
             "cita": "Zanaga, D. et al. (2022). ESA WorldCover 10 m 2021 v200. doi:10.5281/zenodo.7254221"},
            {"nombre": "IDEAM: Normales Climatológicas de Colombia y datos horarios/10 min de la estación Zaragoza (datos.gov.co)",
             "url": "https://www.datos.gov.co/resource/nsz2-kzcq", "licencia": "CC BY-SA 4.0",
             "uso": "validación (bloque validacion_ideam) y calibración del umbral de dias_tmax_ge_umbral_eq32",
             "cita": "Instituto de Hidrología, Meteorología y Estudios Ambientales (IDEAM), datos abiertos en datos.gov.co"},
            {"nombre": ("IDEAM: Promedios Mensuales y Anual de la Radiación Global Acumulada Diaria para las Estaciones Meteorológicas del IDEAM "
                        f"(datos.gov.co {IDEAM_RAD_DS})"),
             "url": f"https://www.datos.gov.co/resource/{IDEAM_RAD_DS}", "licencia": "CC BY-SA 4.0",
             "fecha_publicacion": (rad_meta or {}).get("fecha_publicacion"),
             "uso": ("validación del valor absoluto de la radiación de ERA5 y NASA POWER con la climatología medida de la estación Zaragoza "
                     "(validacion_radiacion.estacion_ideam); el IDEAM no publica el periodo de la climatología"),
             "cita": "Instituto de Hidrología, Meteorología y Estudios Ambientales (IDEAM), datos abiertos en datos.gov.co"},
        ],
        "celda": {
            "solicitud": {"lat": LAT, "lon": LON, "cell_selection": "land (predeterminado de Open-Meteo: celda de tierra con elevación parecida)"},
            "era5land": {"lat": meta_l["latitude"], "lon": meta_l["longitude"], "rejilla_grados": 0.1, "resolucion_nativa_km": 9,
                         "cubre_aprox": {"sur": 4.65, "norte": 4.75, "oeste": -75.95, "este": -75.85},
                         "fraccion_area_urbana_dentro": r(frac_urb, 3),
                         "elevacion_downscaling_m": meta_l["elevation"], **elev,
                         "nota": ("Open-Meteo corrige la temperatura a la elevación de su MDT de 90 m desde la orografía del modelo; "
                                  "la celda de 0,1° es una caja aproximada (ERA5-Land se calcula en una rejilla gaussiana de ≈ 9 km y se "
                                  "interpola a 0,1°). El norte de la ciudad (lat > 4,75, incluido el aeropuerto) cae en la celda vecina.")},
            "era5": {"lat": meta_e["latitude"], "lon": meta_e["longitude"], "rejilla_grados": 0.25, "resolucion_nativa_km": 31,
                     "elevacion_downscaling_m": meta_e["elevation"]},
            "sensibilidad_celdas_vecinas_1991_2020": vecinas,
            "chirps": chirps_info,
            "nasa_power": ({"punto": pw_meta["punto"], "rejilla_grados": 1.0, "fuentes": pw_meta["fuentes"], "solicitud": pw_meta["solicitud"]}
                           if pw_meta else None),
            "zona_horaria": TZ,
        },
        "periodo": {"inicio": str(tl[0]), "fin": ult, "anio_parcial": anio_parcial, "fin_era5": str(te[-1]),
                    "nota_parcial": (f"{anio_parcial} es un año parcial (ERA5-Land hasta {ult}, ERA5 hasta {te[-1]}); sus valores anuales no son "
                                     "comparables con años completos y se excluyen de tendencias, rankings y climatologías." if anio_parcial else None)},
        "unidades": {"tmedia": "°C", "tmax_media": "°C", "tmin_media": "°C", "txx": "°C", "tnn": "°C", "precip_total": "mm", "rx1day": "mm",
                     "rx5day": "mm", "dias_tx90p": "días", "pct_tx90p": "% de días", "noches_tn90p": "noches", "pct_tn90p": "% de días",
                     "dias_tmax_ge_32": "días", "dias_tmax_ge_umbral_eq32": "días", "radiacion_kwh_m2_dia": "kWh/m²/día",
                     "radiacion_power_kwh_m2_dia": "kWh/m²/día", "humedad_media": "%", "completitud": "fracción de días del año",
                     "anomalia_tmedia_vs_1991_2020": "°C", "precip_chirps": "mm", "meses_chirps": "meses", "dias_tmax_gt_umbral_local": "días"},
        "definiciones": {
            "tmedia / tmax_media / tmin_media": ("media anual de la temperatura del aire a 2 m media, máxima y mínima diaria (ERA5-Land, con el "
                                                 "filtro de picos horarios de control_calidad.picos_horarios_era5land)."),
            "txx / tnn": "máxima absoluta de Tmax y mínima absoluta de Tmin del año (ETCCDI TXx, TNn), con la serie filtrada.",
            "precip_total": "suma anual de la precipitación diaria de ERA5. NO APTA PARA DECISIONES (ver campos_no_aptos_para_decisiones).",
            "precip_chirps": "suma de los 12 totales mensuales de CHIRPS v3 sobre la huella urbana; null si falta algún mes (año en curso).",
            "meses_chirps": "meses del año con dato CHIRPS.",
            "dias_tmax_gt_umbral_local": ("días con Tmax de ERA5-Land por encima del umbral local fijo (percentil 90 de todas las Tmax diarias de "
                                          "1961–1990; ver distribucion_tmax_era5land). PROPUESTA de índice climatológico de calor; no sirve para "
                                          "identificar días concretos ni para alertas (ver validacion_ideam.estacion_zaragoza.tx.destreza_dias_calidos)."),
            "rx1day": "máxima precipitación en un día del año según ERA5 (ETCCDI Rx1day). NO APTA PARA DECISIONES.",
            "rx5day": "máximo de la precipitación de ERA5 acumulada en 5 días consecutivos que terminan en un día del año (ETCCDI Rx5day). NO APTA PARA DECISIONES.",
            "dias_tx90p / pct_tx90p": ("días (y % de días) con Tmax > percentil 90 del día del calendario, calculado con ventana centrada de 5 días en el "
                                       "periodo base 1961–1990 (ETCCDI TX90p); en 1961–1990 se usa el bootstrap de Zhang et al. (2005), por eso hay decimales."),
            "noches_tn90p / pct_tn90p": ("ídem con Tmin (ETCCDI TN90p, «noches cálidas»). La Tmin es la variable peor validada frente a la "
                                         "estación y el índice cambia mucho entre reanálisis (contraste_era5.resumen_tn90p): úsese como índice de "
                                         "frecuencia de largo plazo, con el rango, no como cifra exacta ni para noches concretas."),
            "dias_tmax_ge_32": "días con Tmax ≥ 32 °C en ERA5-Land (umbral absoluto; ver interpretacion: no es informativo con este reanálisis).",
            "dias_tmax_ge_umbral_eq32": ("días con Tmax de ERA5-Land ≥ el umbral equivalente a 32 °C en la estación IDEAM Zaragoza (ver "
                                         "interpretacion). El umbral sale de datos del IDEAM (CC BY-SA 4.0), así que este campo es material derivado de ellos."),
            "radiacion_kwh_m2_dia": (f"media anual de la radiación solar global diaria en superficie de ERA5, MJ/m² ÷ 3,6 ({txt_rad_ideam}). "
                                     "Valor absoluto NO APTO para dimensionar (ver campos_no_aptos_para_decisiones); úsese para anomalías."),
            "radiacion_power_kwh_m2_dia": ("media anual (ponderada por días) de la radiación solar global mensual de NASA POWER; solo años con los 12 "
                                           "meses. GEWEX SRB hasta 2000 y CERES SYN1deg desde 2001: su tendencia cruza ese empalme."),
            "humedad_media": "media anual de la humedad relativa media diaria (ERA5-Land, filtrada).",
            "completitud": "fracción de los días del año con dato en ambos reanálisis (1 = año completo); también por reanálisis.",
            "anomalia_tmedia_vs_1991_2020": "tmedia del año menos la media anual 1991–2020 (solo años completos).",
            "mensual.parcial": "true si el mes no tiene todos sus días; sus anomalías quedan en null.",
        },
        "anual": tab,
        "umbrales_percentil_90": {
            "base": "1961-1990", "ventana_dias": 5, "cuantil": "tipo 8 de Hyndman y Fan (como climdex.pcic)", "excedencia": "estricta (>)",
            "dia_calendario": list(range(1, 366)), "tx90": rl(p90x.umbral, 2), "tn90": rl(p90n.umbral, 2),
            "pct_tx90p_medio_en_base": r(tx90_base, 2), "pct_tn90p_medio_en_base": r(tn90_base, 2),
            "nota": ("Open-Meteo entrega ERA5-Land con 0,1 °C de resolución; los empates con el umbral no cuentan como excedencia y el promedio "
                     "en el periodo base puede quedar algo por debajo del 10 % teórico."),
        },
        "distribucion_tmax_era5land": dist_tx,
        "tendencias": {
            "metodo": ("Pendiente por década con mínimos cuadrados ordinarios (IC 95 % con t de Student, p bilateral) y con tamaño efectivo de muestra por "
                       "autocorrelación de orden 1 de los residuos (Santer et al. 2000); pendiente de Sen con IC 95 % y prueba de Mann-Kendall con corrección "
                       "por empates. Solo años completos. 'significativa_5pct' exige p < 0,05 en MCO y en Mann-Kendall. Que la pendiente sea mayor en "
                       "un periodo más corto no prueba aceleración: los periodos se solapan y los intervalos también."),
            "unidades": variables_t,
            "periodos": tend,
            "fuente_por_variable": {"tmedia": "ERA5-Land", "tmax_media": "ERA5-Land", "tmin_media": "ERA5-Land", "txx": "ERA5-Land",
                                    "precip_total": "ERA5 (no apta para decisiones)", "precip_chirps": "CHIRPS v3 (desde 1981)",
                                    "pct_tx90p": "ERA5-Land", "dias_tx90p": "ERA5-Land", "pct_tn90p": "ERA5-Land",
                                    "dias_tmax_gt_umbral_local": "ERA5-Land", "radiacion_power_kwh_m2_dia": "NASA POWER (desde 1984)"},
            "rango_entre_reanalisis_tmedia_c_por_decada": {
                p: {"era5land": T[p]["tmedia"]["ols_por_decada"], "era5": TE[p]["tmedia"]["ols_por_decada"]} for p in T},
            "radiacion_power_solo_ceres_2001_2025": tend_pw_ceres,
        },
        "climatologia_mensual": {
            "normal_1991_2020": c9120, "decenio_2016_2025": c1625, "anomalia_2016_2025_vs_1991_2020": anom,
            "nota": ("1991–2020 es la normal climatológica estándar vigente de la Organización Meteorológica Mundial (OMM; la «OMS» de la solicitud "
                     "se interpreta como OMM). Temperatura y humedad: ERA5-Land; lluvia y radiación: ERA5; precip_chirps: CHIRPS v3; "
                     "radiacion_power_kwh_m2_dia: NASA POWER. precip_total y precip_chirps son totales mensuales medios (mm/mes). Solo meses completos."),
        },
        "mensual": mens,
        "contraste_era5": {
            "descripcion": ("Temperatura y humedad anuales de ERA5 (0,25°) e índices de Tmax y Tmin con sus propios umbrales (TX90p y TN90p con base 1961–1990; "
                            f"umbral local {umbral_local_era5} °C = percentil 90 de las Tmax de ERA5 en 1961–1990), para medir cuánto depende el "
                            "resultado del reanálisis. ERA5-Land se fuerza con ERA5, así que no son estimaciones independientes. Los años desde 2025 "
                            "están afectados por la discontinuidad del ciclo diurno de ERA5 (ver discontinuidad_2025): por eso hay tendencias hasta 2024."),
            "umbral_local_era5": umbral_local_era5,
            "anual": era5_anual, "tendencias": tend_e,
            "resumen_tn90p": resumen_tn90p,
            "diferencia_era5land_menos_era5_tmedia_por_quinquenio": {
                f"{a}-{a + 4}": r(np.nanmean(np.array([np.nan if x is None else x for x in tab["tmedia"]], float)[completos & (anios >= a) & (anios <= a + 4)]
                                             - np.array([np.nan if x is None else x for x in era5_anual["tmedia"]], float)[completos & (anios >= a) & (anios <= a + 4)]))
                for a in range(1950, 2026, 5)},
            "discontinuidad_2025": disc_era5,
        },
        "consistencia_lluvia_era5": consist_lluvia,
        "validacion_radiacion": val_rad,
        "validacion_ideam": {
            "licencia": "CC BY-SA 4.0 (IDEAM, datos.gov.co): este bloque contiene valores derivados de datos del IDEAM",
            "estacion_zaragoza": val_est, "normales_estaciones_cercanas": val_norm,
            "resumen_normales": resumen_normales(val_norm) if val_norm else None,
            "tendencia_observada_normales": tend_norm,
            "contraste_estacion_vs_normales_tmax": contraste_est,
            "consultas_fallidas": fallos_ideam,
            "criterio_normales": ("estaciones a ≤ 30 km del centro de Cartago y ≤ 1250 m de altitud; se compara con la climatología del "
                                  "reanálisis del mismo periodo de 30 años (1961–1990, 1971–2000, 1981–2010, 1991–2020)"),
        },
        "control_calidad": {
            "dias_era5land": int(tl.size), "dias_era5": int(te.size),
            "nulos_archivo_partida": nulos_hist,
            "dias_2026_era5land": int(t26.size),
            "reproducibilidad_archivo_de_partida": repro | {
                "solicitud_equivalente": {"url": API, "latitude": LAT, "longitude": LON, "start_date": "1950-01-01", "end_date": "2025-12-31",
                                          "daily": ",".join(VARS_PARTIDA), "models": "era5_land", "timezone": TZ},
                "nota": ("El archivo de partida no guarda su solicitud. La de arriba devuelve la misma celda (4.70, −75.90) y elevación (919 m) "
                         "y la serie horaria pedida con ella reproduce sus Tmax y Tmin diarias; el script la usa para volver a descargarlo si falta.")},
            "picos_horarios_era5land": picos,
            "sensibilidad_filtro_picos": sens_picos,
            "rango_tmedia_diaria": [r(np.min(vl["temperature_2m_mean"]), 1), r(np.max(vl["temperature_2m_mean"]), 1)],
            "rango_tmax_diaria": [r(np.min(vl["temperature_2m_max"]), 1), r(np.max(vl["temperature_2m_max"]), 1)],
            "rango_tmin_diaria": [r(np.min(vl["temperature_2m_min"]), 1), r(np.max(vl["temperature_2m_min"]), 1)],
            "rango_humedad_diaria": [r(np.min(vl["relative_humidity_2m_mean"]), 1), r(np.max(vl["relative_humidity_2m_mean"]), 1)],
            "precip_diaria_max_mm": r(np.max(ve["precipitation_sum"]), 1),
            "precip_diaria_min_mm": r(np.min(ve["precipitation_sum"]), 1),
            "radiacion_diaria_mj_m2": [r(np.min(ve["shortwave_radiation_sum"]), 2), r(np.max(ve["shortwave_radiation_sum"]), 2)],
            "tmin_le_tmedia_le_tmax": bool(np.all((vl["temperature_2m_min"] <= vl["temperature_2m_mean"] + 1e-6) & (vl["temperature_2m_mean"] <= vl["temperature_2m_max"] + 1e-6))),
        },
        "procesamiento": [
            "Lectura de fuentes/era5land-cartago-1950-2025.json (Open-Meteo, models=era5_land, diario, America/Bogota; si falta, se vuelve a pedir con la solicitud equivalente) y descarga de 2026 con la misma petición; se comprueba que la celda y la elevación coinciden y que la serie no tiene huecos.",
            "Descarga de la temperatura y la humedad HORARIAS de ERA5-Land (misma celda, 1950→hoy, bloques de 5 años) y comprobación de que sus agregados reproducen el archivo diario.",
            f"Filtro de picos espurios de una hora (curvatura > {PICO_CURV} °C con caída simultánea de la HR > {-PICO_HR:.0f} puntos; reemplazo por la media de las vecinas; hasta {PICO_PASADAS} pasadas) y recálculo de Tmax, Tmedia y HR media de los días afectados.",
            "precipitation_sum y shortwave_radiation_sum de ERA5-Land vienen vacías en Open-Meteo: se descargan de ERA5 (models=era5), el forzamiento del que ERA5-Land toma la lluvia y la radiación (interpoladas a 9 km sin corrección).",
            "Índices anuales a partir de los valores diarios; Rx5day con sumas de 5 días que terminan en cada día (incluye los últimos días del año anterior).",
            "TX90p/TN90p: umbral por día del calendario (365; el 29 de febrero usa el del 28) con ventana centrada de 5 días sobre 1961–1990, cuantil tipo 8, excedencia estricta; bootstrap de Zhang et al. (2005) para los años 1961–1990 (29 réplicas por año). Lo mismo con la Tmax de ERA5 como contraste.",
            "Tendencias: MCO (scipy.stats.linregress), ajuste por autocorrelación AR(1) de residuos (Santer et al. 2000), Sen (scipy.stats.theilslopes) y Mann-Kendall propio con corrección por empates.",
            "Climatologías mensuales con meses completos; anomalías como diferencia (°C, mm, kWh/m²/día, puntos de humedad) y, para la lluvia, también en %; los meses incompletos no tienen anomalía.",
            "Lluvia de referencia CHIRPS v3 (COG mensuales por ventana, media ponderada sobre la huella urbana) y radiación de referencia NASA POWER (API mensual, punto central).",
            (f"Validación: agregación diaria en el servidor (SoQL, una consulta por año y variable) de la estación IDEAM Zaragoza (temperatura hasta "
             f"{FIN_VALIDACION}, por la falta de homogeneidad posterior de la estación; lluvia completa); normales IDEAM 1961–1990, 1971–2000, 1981–2010 y "
             "1991–2020 de estaciones cercanas, también como contraste de la tendencia; destreza para días cálidos (POD, FAR); climatología medida "
             f"de radiación global de las estaciones IDEAM (datos.gov.co {IDEAM_RAD_DS}) frente a ERA5 y NASA POWER."),
            "Sensibilidad espacial: ERA5-Land 1991–2020 en las cuatro celdas de 0,1° que tocan la rejilla de BioMap, todas a la elevación de la serie del producto (cell_selection=nearest, elevation=919).",
        ],
        "limitaciones": [
            "Es un REANÁLISIS, no una estación: ERA5-Land representa el promedio de una celda de ≈ 9–11 km (0,1°) que mezcla la ciudad, el valle del río La Vieja y las primeras laderas; ver celda.era5land.elevacion_modelo_m. La lluvia y la radiación vienen de ERA5, con celdas de ≈ 28 km (0,25°).",
            lim_tend,
            "Los valores absolutos están sesgados: frente a la estación IDEAM Zaragoza y a las normales IDEAM del valle, ERA5-Land es varios grados más frío (sobre todo la máxima) y más húmedo; ERA5 menos, pero también (ver validacion_ideam). Úsese para anomalías y tendencias (estas, con el rango entre reanálisis), no para comparar con umbrales absolutos ni con mediciones locales.",
            "ERA5-Land tiene picos espurios de una hora en la temperatura (y la humedad) horaria, más frecuentes desde 2020; se filtraron con un criterio propio (control_calidad.picos_horarios_era5land). Un pico menor que el umbral, o el exceso que queda en la hora siguiente, puede seguir en Tmax; TXx es el índice más sensible (ver control_calidad.sensibilidad_filtro_picos).",
            lim_destreza,
            "La temperatura del aire a 2 m NO es la temperatura de superficie (LST) de Landsat: de día la superficie (techos, asfalto) se calienta mucho más que el aire y la isla de calor superficial es más intensa que la del aire (p. ej., Azevedo, Chapman y Muller 2016, Remote Sensing 8(2):153, doi:10.3390/rs8020153); no se comparan directamente.",
            "El reanálisis no ve la isla de calor urbana ni diferencias entre barrios: es un solo valor para toda la ciudad, y el norte de la cabecera (incluido el aeropuerto) cae en otra celda.",
            (f"La lluvia de ERA5 en esta celda no sirve: es {txt_lluvia_x} y su variabilidad anual, mensual y diaria se parece poco a la "
             "observada (consistencia_lluvia_era5); precip_total, rx1day y rx5day se publican solo por trazabilidad y no son aptos para decisiones. "
             "Para la cantidad de lluvia úsese precip_chirps. No hay extremos diarios de lluvia fiables (Rx1day, Rx5day): CHIRPS v3 se usa "
             "aquí en su versión mensual, y la diaria (≈ 16 000 archivos) no es viable con la red disponible."),
            lim_rad,
            ("CHIRPS v3 incorpora estaciones del IDEAM y corrige la subcaptación de los pluviómetros (por eso puede quedar por encima de las "
             f"normales IDEAM), así que su comparación con el IDEAM no es una validación independiente; su diferencia {txt_chirps_err}. Empieza en 1981."),
            lim_disc,
            ("La estación IDEAM Zaragoza, la única con datos diarios abiertos en Cartago, tiene huecos largos y cambia de nivel tras el de "
             "2023–2025 (validacion_ideam.estacion_zaragoza.homogeneidad_estacion); la validación de temperatura usa solo hasta 2023 y no "
             "permite evaluar tendencias. Las normales IDEAM no dicen cuántos años válidos tienen."),
            "Las tendencias de un reanálisis pueden verse afectadas por cambios en las observaciones asimiladas; antes de 1979 ERA5 asimila menos datos (Bell et al. 2021), así que la incertidumbre de 1950–1980 es mayor que la que expresan los intervalos estadísticos.",
            "Los intervalos de confianza suponen errores independientes (MCO) o AR(1) (ajustado); no incluyen la incertidumbre estructural del reanálisis (ver contraste_era5 y celda.sensibilidad_celdas_vecinas_1991_2020).",
            "El año en curso es parcial y se excluye de tendencias, climatologías y rankings; los meses incompletos no tienen anomalía.",
            "El umbral equivalente a 32 °C y el umbral local son supuestos metodológicos propios (emparejamiento de frecuencias con una sola estación, con huecos); úsense como orientación, no como norma.",
        ],
        "interpretacion": {
            "umbral_32C": None,
            "tx90p": "Por construcción, en 1961–1990 alrededor del 10 % de los días superan el percentil 90 (≈ 36 días/año). Valores claramente mayores indican más días cálidos para el clima local de referencia, sin depender del sesgo absoluto del reanálisis. Es un índice de frecuencia en periodos largos; no identifica días concretos.",
            "umbral_local": None,
            "tendencia_significativa": "Se considera significativa al 5 % cuando MCO y Mann-Kendall dan p < 0,05; la versión ajustada por autocorrelación es la más conservadora.",
            "normal_oms_nota": "La «normal» de referencia es la de la OMM (Organización Meteorológica Mundial), no de la OMS.",
        },
        "hallazgos": hallazgos,
        "fecha_proceso": date.today().isoformat(),
    }
    n32 = dist_tx["dias_ge_32_total"]
    base_txt = (f"32 °C no es informativo con ERA5-Land: en {tl.size} días (1950–{ult[:4]}) {n32} alcanzan 32 °C una vez quitados los picos "
                f"espurios de una hora (sin el filtro eran {dist_tx['sin_filtro_de_picos']['dias_ge_32_total']}, todos artefactos); la máxima del "
                f"registro es {dist_tx['max_1950_hoy']} °C ({dist_tx['fecha_max']}) y en 1991–2020 el percentil 99 de Tmax es {dist_tx['p99']} °C. ")
    if umbral_eq is not None:
        v = val_est["tx"]
        salida["interpretacion"]["umbral_32C"] = base_txt + (
            f"Tampoco marca calor extremo en el termómetro: en la estación automática IDEAM Zaragoza la mediana de la máxima diaria es "
            f"{v['percentiles_tx_estacion']['p50']} °C y se registra ≥ 32 °C el {v['frecuencia_tx_ge_32_estacion_pct']} % de los días"
            + (f" (esa estación tiene una máxima media ≈ {contraste_est['diferencia_estacion_menos_normales']:.1f} °C por encima de la de las normales "
               "convencionales cercanas y no es homogénea; al nivel de las normales, con un desplazamiento uniforme, serían ≈ "
               f"{contraste_est['frecuencia_aprox_tx_ge_32_al_nivel_de_las_normales_pct']:.0f} % de los días: "
               "validacion_ideam.contraste_estacion_vs_normales_tmax)"
               if contraste_est and contraste_est.get("frecuencia_aprox_tx_ge_32_al_nivel_de_las_normales_pct") is not None else "")
            + ". "
            f"dias_tmax_ge_umbral_eq32 usa {umbral_eq} °C en ERA5-Land, el valor que en los {v['dias_comunes']} días comunes se supera con la "
            "misma frecuencia con que la estación alcanza 32 °C (emparejamiento de cuantiles): describe días que llegan a 32 °C, no días extremos, "
            "y deriva de datos IDEAM (CC BY-SA 4.0). Para días cálidos se propone dias_tmax_gt_umbral_local (ver umbral_local) o TX90p. "
            "Supuestos metodológicos propios, no normas.")
    else:
        salida["interpretacion"]["umbral_32C"] = base_txt + "Sin la estación IDEAM no se pudo calcular el umbral equivalente; úsese dias_tmax_gt_umbral_local o TX90p."
    eq_txt = ""
    if val_est and isinstance(val_est.get("tx"), dict) and val_est["tx"].get("destreza_dias_calidos", {}).get("umbral_local_era5land"):
        u = val_est["tx"]["destreza_dias_calidos"]["umbral_local_era5land"]
        c_ = u["contingencia"]
        eq_txt = (f" Con la misma frecuencia de excedencia, equivale a ≈ {u['equivalente_estacion_misma_frecuencia']} °C en el termómetro de la "
                  f"estación IDEAM Zaragoza, pero solo como frecuencia: día a día coinciden {c_['aciertos']} de {c_['eventos_estacion']} días cálidos "
                  f"de la estación (POD {c_['tasa_deteccion_pod']}) y {c_['falsas_alarmas']} de los {c_['eventos_reanalisis']} días marcados por "
                  f"ERA5-Land son falsas alarmas (FAR {c_['tasa_falsas_alarmas_far']}).")
    amp_tx = max(c9120["tmax_media"]) - min(c9120["tmax_media"])
    salida["interpretacion"]["umbral_local"] = (
        f"Propuesta de índice climatológico de calor: Tmax de ERA5-Land > {umbral_local} °C, el percentil 90 de todas las Tmax diarias de "
        f"1961–1990 (en esa base lo supera el {dist_tx['frecuencia_gt_umbral_local_1961_1990_pct']} % de los días; la discretización de 0,1 °C "
        "puede dejar la cifra algo por debajo del 10 %). Sigue el principio de TX90p (umbral relativo al clima local, inmune al sesgo absoluto "
        f"del reanálisis) pero con un solo número en °C, sin ventana estacional (en la normal 1991–2020 la máxima media mensual varía solo "
        f"{amp_tx:.1f} °C entre el mes más fresco y el más cálido).{eq_txt} Sirve para contar días cálidos por año o por decenio; no para "
        "identificar un día concreto ni para emitir alertas. Supuesto metodológico propio.")
    comun.guardar_json(args.salida, salida)
    log(f"\nEscrito {args.salida} ({os.path.getsize(args.salida) / 1024:.0f} KB) en {time.time() - t_ini:.0f} s")
    log("\nRESUMEN")
    for h in hallazgos:
        log(" - " + h)
    log(f" - TX90p medio en la base: {tx90_base:.2f} %; TN90p: {tn90_base:.2f} %")
    log(f" - interpretación 32 °C: {salida['interpretacion']['umbral_32C']}")




if __name__ == "__main__":
    main()
