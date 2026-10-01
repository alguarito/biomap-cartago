"""Producto «indicadores»: indicadores por zona, exposición de equipamientos, series por zona,
calibración empírica para el simulador y componentes de priorización de BioMap Cartago.

No descarga nada: combina las capas ya construidas por los demás productos del proyecto
(fuentes/rejilla/*.npy, datos/capas/*.json, datos/vectores/*.geojson, datos/series/landsat.json)
y algunas cachés locales (fuentes/poblacion, fuentes/inundacion, fuentes/osm-vias.json).

FUENTES Y LICENCIAS (se heredan de las capas de entrada; la atribución completa va en cada salida)
  * LST 2022-2025 y rejillas anuales 2000-2025: USGS Landsat Collection 2 Level-2, vía Microsoft Planetary
    Computer. Dominio público USGS (se pide citar). doi:10.5066/P9OGBGM6 (L8-9), 10.5066/P9C7I13B (L7),
    10.5066/P9IAXOVV (L4-5).
  * NDVI 2024-2025: Copernicus Sentinel-2 L2A (Earth Search). Datos Copernicus: acceso libre; mención
    «Contiene datos modificados de Copernicus Sentinel [2024–2025]».
  * Arbolado, construido, agua, pasto: ESA WorldCover 10 m 2021 v200, CC BY 4.0. doi:10.5281/zenodo.7254221.
  * Población 2026: DANE (CNPV 2018 por manzana y sección rural, proyecciones PPED 2018-2042, MGN 2018);
    uso con cita «Fuente: Departamento Administrativo Nacional de Estadística: www.dane.gov.co».
  * Susceptibilidad a inundación y altitud: Copernicus DEM GLO-30 (licencia Copernicus WorldDEM-30, con aviso).
  * Tráfico, verde público, equipamientos, comunas, cabecera, ríos y vías: OpenStreetMap, ODbL 1.0.
  * Zaragoza (zona de trabajo): huella ESA WorldCover 2021 (datos/zaragoza.json), CC BY 4.0.
  * Inundación (registros oficiales): IDEAM, servicio Amenaza_Ambiental, capa 0 «Amenaza Creciente Súbita TR 50
    años» (atributos corriente «Río La Vieja» y cuenca «Directos Río La Vieja») y capas 6, 7, 8, 9, 22, 23, 24, 26 y
    27 «Áreas afectadas por inundación, La Niña» 1988–2022 (la 25 viene vacía), cachés del producto inundacion en
    fuentes/inundacion/ideam_*.geojson. Licencia: el servicio ArcGIS no declara licencia (copyrightText vacío). Las
    capas La Niña 1988, 2000, 2011 y 2012 las publica también el IDEAM en datos.gov.co con licencia CC BY-SA 4.0 y la
    advertencia «no han sido validados por el IDEAM» (conjuntos khg6-9h39, 5p6w-58v3, 6eu7-pzc5 y nufr-59j5; licencia
    verificada en el catálogo de datos.gov.co el 2026-10-01; 6eu7-pzc5 = «Áreas Afectadas Inundación Niña 2011»,
    verificado vía api/views, sin escala declarada). La creciente súbita TR 50 y La Niña 2016 y 2020–2022 no
    aparecieron en la búsqueda del catálogo. Por la regla del proyecto
    (CLAUDE.md) no se copian polígonos del IDEAM: solo se publican estadísticas derivadas con atribución.
  * Población: además del DANE, la capa poblacion usa Meta/CIESIN HRSL v1.5 (CC BY 4.0) para repartir dentro de
    las manzanas.

REFERENCIAS VERIFICADAS (WebFetch/WebSearch, 2026-10-01)
  * Decreto 1504 de 1998, arts. 12 y 14: espacio público efectivo = «espacio público de carácter permanente,
    conformado por zonas verdes, parques plazas y plazoletas»; índice mínimo de 15 m²/hab.
    https://normas.cra.gov.co/gestor/docs/decreto_1504_1998.htm
  * CONPES 3718 de 2012 (31-ene-2012), Política Nacional de Espacio Público: promedio nacional ajustado a 2010
    de 3,3 m²/hab y meta de 5–6 m²/hab a 2015 para ciudades de más de 100.000 hab (Gráfico 7). Copia local en
    fuentes/indicadores/referencias/conpes_3718_2012.pdf.
  * IDEAM en datos.gov.co: «Áreas Afectadas Inundación Niña 2011» (6eu7-pzc5), CC BY-SA 4.0, «no han sido validados por
    el IDEAM», sin escala declarada (api/views). Catálogo: 1988 khg6-9h39, 2000 5p6w-58v3, 2012 nufr-59j5, CC BY-SA 4.0.
  * Emergencias de la UNGRD en datos.gov.co: solo desde 2019 (wwkg-r6te y otros; catálogo Socrata). El «Consolidado reporte
    de emergencias 1998-2021» del repositorio de la UNGRD no respondió desde aquí (no verificado su contenido).
  * USGS, bandas de Landsat 8: TIRS se adquiere a 100 m y se remuestrea a 30 m.
    https://www.usgs.gov/faqs/what-are-band-designations-landsat-satellites
  * USGS (2-ene-2024): desde el 1-ene-2024 la temperatura de superficie de L7/L8/L9 usa GEOS-IT en lugar de
    GEOS FP-IT. https://www.usgs.gov/landsat-missions/news/changes-landsat-surface-temperature-atmospheric-auxiliary-data
  * Das, J. K., Kumari, B., Rahman, A. R., et al. (2025). Evaluation of community-based heat adaptation
    interventions: a systematic review. BMJ Public Health 3(2): e002332. doi:10.1136/bmjph-2024-002332
    (metaanálisis de temperatura de SUPERFICIE: techos verdes −10,88 °C frente a techo de concreto desnudo,
    IC 95 % −15,26 a −6,50, 17 estudios, I² 92 %; pavimentos modificados −5,45 °C frente a asfalto, IC −6,75 a
    −4,15, 8 estudios, I² 10 %; frente a concreto −1,14 °C, IC −2,91 a 0,63, 9 estudios; subgrupo de concretos
    porosos, retenedores de agua y permeables +1,74 °C, IC 0,81 a 2,68, 4 estudios; medias diarias).
    https://pmc.ncbi.nlm.nih.gov/articles/PMC12273142/
  * US EPA, Using Green Roofs to Reduce Heat Islands: la superficie de un techo verde «can be 56°F lower» que la
    de un techo convencional (cota superior). https://www.epa.gov/heatislands/using-green-roofs-reduce-heat-islands
  * Abhijith, K. V., Kumar, P., et al. (2017). Air pollution abatement performances of green infrastructure in
    open road and built-up street canyon environments – A review. Atmospheric Environment 162: 71–86.
    doi:10.1016/j.atmosenv.2017.05.014 (en cañones urbanos los árboles empeoraron la calidad del aire y los
    setos la mejoraron).
  * ESA WorldCover se clasificó con compuestos anuales de Sentinel-2 (RGBNIR, SWIR y percentiles 10/50/90 del NDVI)
    y Sentinel-1 (GAMMA0): https://registry.opendata.aws/esa-worldcover-vito-composites/ (de ahí la circularidad
    parcial del modelo de NDVI).
  * Intervalo de predicción de un metaanálisis de efectos aleatorios (Higgins, Thompson y Spiegelhalter 2009,
    J R Stat Soc A 172: 137–159): μ ± t(k−2)·√(τ² + SE²); fórmula verificada en Nagashima, Noma y Furukawa,
    arXiv:1804.01054. Das et al. no publican τ²: aquí se aproxima τ² ≈ I²·k·SE² suponiendo varianzas
    intraestudio iguales (supuesto propio, marcado como tal en calibracion.json).

PASOS
  1. Zonas: comun.comunas() (Comunas 1–7 de OSM y Zaragoza = huella WorldCover). «Cabecera» = unión de las
     8 zonas (≈ polígono OSM de la cabecera + Zaragoza; equivale al concepto DANE de cabecera, que incluye
     Zaragoza). Se comprueba la coherencia de la población con el DANE y con la serie de población.
  2. Indicadores por zona y cabecera: área, población, densidad, LST (media, p90, anomalía, calor extremo =
     LST ≥ p90 de la cabecera), NDVI, arbolado, construido, verde público OSM por habitante (intersección de
     polígonos en UTM 18N), acceso a verde a 300 m, inundación (susceptibilidad topográfica HAND por un lado y
     registros oficiales del IDEAM por otro: amenaza por creciente súbita TR 50 y áreas afectadas por La Niña,
     con sensibilidad del borde ± 2 celdas ≈ 55 m), tráfico, equipamientos y tendencia de la LST por zona (Sen,
     solo años confiables). Medias por área y ponderadas por población.
  2b. Coherencia topográfica de las manchas La Niña por periodo: HAND (fuentes/rejilla/hand.npy y
     hand_rio_mayor.npy del producto inundacion) dentro de cada mancha frente a las celdas del mismo ámbito fuera
     de toda mancha, en la cabecera y fuera de ella, con todas las celdas y solo con celdas abiertas (construido
     < 10 % y arbolado < 20 %, donde el DSM se acerca al terreno). Un periodo cuya parte urbana no está más baja que
     su entorno se marca como no coherente con el relieve; el componente de inundación se recalcula sin La Niña 2011
     (variante 'inundacion_ideam_sin_2011').
  3. Exposición de equipamientos: LST de la celda (y margen frente al umbral), NDVI y arbolado en 100 m (centros
     de celda a ≤ 100 m en UTM), clase de susceptibilidad, registros IDEAM, distancia a verde y tráfico.
  4. Series anuales por zona (2000-2025) con la marca de confiabilidad, en tres variantes (mediana y media de la
     zona, mediana del núcleo construido ≥ 80 %), con una marca de robustez de la tendencia entre variantes.
  5. Calibración: MCO en la cabecera. LST con unidades de 4×4 celdas (≈ 111 m, cercano a los 100 m de TIRS);
     NDVI por celda (más una sensibilidad con NDVI Landsat, otro sensor). IC 95 % por bootstrap espacial de
     bloques de 18 celdas (≈ 500 m) y sensibilidad con 1 km; diagnóstico de residuos (correlograma, sesgo por
     zona, no linealidad, VIF). Intervenciones del simulador con superficies disponibles por zona (vías OSM con
     ancho supuesto), restricción conjunta sobre lo construido y piso de LST en la mediana de las celdas de la
     cabecera con ≥ 80 % de arbolado (el bosque urbano observado; la referencia rural, más fría, se publica aparte).
     Topes y piso son reglas PROPUESTAS al simulador (calibracion.json no las aplica); 'verificacion_topes' calcula
     con los datos cuántas zonas bajarían del piso sin ellas.
  6. Prioridades: componentes 0–1 por zona con sus conteos absolutos, índice con pesos iguales, ranking y
     sensibilidad del ranking (variantes, entre ellas la evidencia IDEAM sin La Niña 2011, conteos absolutos, sin
     piso y quitando un componente).

SALIDAS
  datos/indicadores.json, datos/vectores/zonas.geojson, datos/vectores/equipamientos_exposicion.geojson,
  datos/series/zonas.json, datos/calibracion.json, datos/prioridades.json; registro en fuentes/indicadores/.
  Los problemas de ejecución (insumos ausentes, componentes que vuelven a HAND) se escriben en el registro y en
  'problemas' de indicadores.json y prioridades.json.

USO
  .venv/bin/python scripts/indicadores.py      (≈ 20 s; sin red; reejecutable con resultados idénticos)
"""
from __future__ import annotations

import json
import os
import sys
import warnings
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comun  # noqa: E402

import numpy as np  # noqa: E402

warnings.filterwarnings("ignore", category=RuntimeWarning)

DIR = os.path.join(comun.FUENTES, "indicadores")
LOG = os.path.join(DIR, "indicadores.log")
os.makedirs(DIR, exist_ok=True)
VECT = os.path.join(comun.DATOS, "vectores")
SERIES = os.path.join(comun.DATOS, "series")

# ------------------------------------------------------------------ parámetros (supuestos documentados)
P_CALOR = 90                 # calor extremo: LST ≥ percentil 90 de la cabecera (definición de la tarea)
DIST_VERDE_M = 300.0         # acceso a verde: ≤ 300 m (OMS 2016, verificado por el producto «verdes»)
TRAFICO_ALTO = 60.0          # tráfico alto: índice ≥ 60 (definición de la tarea; ver documentación)
TRAFICO_SENS = 50.0          # sensibilidad: banda «franja inmediata» (≥ 50) de trafico.json
RADIO_EQ_M = 100.0           # radio para NDVI y arbolado alrededor de cada equipamiento
AGREG = 4                    # unidades de 4×4 celdas (≈ 111 m) para el modelo de LST
FRAC_UNIDAD = 0.75           # una unidad entra si ≥ 75 % de sus celdas están en la cabecera
BLOQUE = 18                  # bloque de bootstrap: 18 celdas = 0,0045° ≈ 500 m
BLOQUE_SENS = 36             # sensibilidad: ≈ 1 km
N_BOOT = 1000
SEMILLA = 20261001
VENTANA_TERRENO = 19         # ≈ 525 m: percentil 10 del DSM como aproximación del terreno
MIN_FRAC_ZONA_ANIO = 0.5     # serie: valor de zona-año solo si ≥ 50 % de sus celdas tienen dato
PISO_RANGO = 0.05            # prioridades: diferencias < 5 pp de población no se amplían a toda la escala
MARGEN_UMBRAL_C = 0.5        # equipamientos: |LST − umbral| < 0,5 °C → «en el umbral» (supuesto)
BORDE_CELDAS = 2             # sensibilidad del borde de las manchas IDEAM (escala no declarada): ± 2 celdas (≈ 55 m)
PERIODO_SIN = "2011"         # variante 'inundacion_ideam_sin_2011': evidencia IDEAM sin las capas La Niña 2011 (8 y 22)
ABIERTA_CONSTRUIDO = 10.0    # coherencia topográfica: celda abierta = construido < 10 % y arbolado < 20 % (supuesto:
ABIERTA_ARBOLADO = 20.0      #   ahí el DSM se acerca al terreno)
COHERENCIA_PROB_MIN = 0.6    # coherente con el relieve si P(HAND dentro < HAND fuera) ≥ 0,6 (supuesto; 0,5 = sin diferencia)
MIN_CELDAS_COHERENCIA = 30   # mínimo de celdas de la mancha en un ámbito para evaluar su coherencia
DIST_TR50_RIO_M = 500.0      # mancha TR 50 ALTA «junto al La Vieja» si su mediana de distancia al eje es ≤ 500 m (supuesto)
NUCLEO_CONSTRUIDO = 80.0     # serie: núcleo construido = celdas con ≥ 80 % construido (como el producto landsat)
MIN_CELDAS_NUCLEO = 200      # serie: la variante de núcleo solo se calcula si la zona tiene ≥ 200 celdas de núcleo
ANCHO_CARRIL_M = 3.5         # simulador: ancho supuesto por carril para estimar la superficie vial OSM
CARRILES = {"trunk": 2, "trunk_link": 1, "primary": 2, "primary_link": 1, "secondary": 2, "secondary_link": 1,
            "tertiary": 2, "tertiary_link": 1, "unclassified": 2, "residential": 2, "living_street": 2, "service": 1}
UTM = "EPSG:32618"

# Capas IDEAM de áreas afectadas por inundación (La Niña) en la caché del producto inundacion: capa → periodo
IDEAM_NINA = {6: "1988", 7: "2000", 8: "2011", 9: "2012", 22: "2011", 23: "2016", 24: "2020–2022", 25: "1988",
              26: "2000", 27: "2012"}
LICENCIA_IDEAM = ("El servicio ArcGIS Amenaza_Ambiental no declara licencia (copyrightText vacío en el servicio y en sus capas). "
                  "Las áreas afectadas por La Niña 1988, 2000, 2011 y 2012 las publica también el IDEAM en datos.gov.co con licencia "
                  "CC BY-SA 4.0 (conjuntos khg6-9h39, 5p6w-58v3, 6eu7-pzc5 y nufr-59j5; licencia verificada en el catálogo de datos.gov.co "
                  "el 2026-10-01) y la advertencia, verificada en 6eu7-pzc5 (La Niña 2011), de que «no han sido validados por el IDEAM». "
                  "La amenaza por creciente súbita TR 50 y La Niña 2016 y 2020–2022 no aparecieron en la búsqueda del catálogo de "
                  "datos.gov.co (2026-10-01). No se copian polígonos del IDEAM: "
                  "solo se publican estadísticas derivadas, con atribución al IDEAM; las que derivan de las capas CC BY-SA "
                  "(ideam_nina_observada, ideam_evidencia_oficial y sus variantes) se comparten con la misma licencia CC BY-SA 4.0 "
                  "(criterio prudente del proyecto).")
CITA_IDEAM = "IDEAM – Instituto de Hidrología, Meteorología y Estudios Ambientales, servicio Amenaza_Ambiental (consulta 2026-09-30)"
CONTRASTE_REGISTROS = ("los registros municipales de gestión del riesgo (alcaldía de Cartago) o el consolidado anual de emergencias de la UNGRD "
                       "(serie desde 1998 en el repositorio institucional de la UNGRD, que no respondió desde aquí el 2026-10-01; en datos.gov.co "
                       "los conjuntos de emergencias de la UNGRD empiezan en 2019, p. ej. wwkg-r6te, así que no cubren 2010–2011)")

PUNTOS = {
    "Parque Bolívar": (4.7497, -75.9132),
    "Aeropuerto (punto de referencia)": (4.7601, -75.9545),
    "Rural suroccidente": (4.72, -75.97),
}

CATEGORIAS = ["educacion", "salud", "cuidado", "emergencia_gobierno"]
NOMBRE_CAT = {"educacion": "educación", "salud": "salud", "cuidado": "cuidado", "emergencia_gobierno": "emergencia o gobierno"}
NOMBRE_VAR = {"mediana": "mediana", "media": "media", "nucleo_construido": "núcleo construido"}


def log(*a):
    txt = " ".join(str(x) for x in a)
    linea = f"[{datetime.now().strftime('%H:%M:%S')}] {txt}"
    print(linea, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def es(x, nd=1, signo=False):
    """Número con coma decimal (texto en español); el cero redondeado se escribe sin signo negativo."""
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "s. d."
    x = float(x)
    if round(x, nd) == 0:
        x = 0.0
    s = f"{x:+.{nd}f}" if signo and x != 0 else f"{x:.{nd}f}"
    return s.replace(".", ",")


def es_int(x):
    return f"{int(round(x)):,}".replace(",", ".")


def r(x, nd=2):
    if x is None:
        return None
    x = float(x)
    return round(x, nd) if np.isfinite(x) else None


def limpio(o):
    """Convierte numpy y NaN/inf a tipos JSON estrictos."""
    if isinstance(o, dict):
        return {str(k): limpio(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [limpio(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return float(o) + 0.0 if np.isfinite(o) else None      # + 0.0 convierte −0.0 en 0.0
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return limpio(o.tolist())
    return o


def guardar(ruta, obj):
    comun.guardar_json(ruta, limpio(obj))


def wmedia(x, w):
    ok = np.isfinite(x) & np.isfinite(w) & (w > 0)
    return float(np.sum(x[ok] * w[ok]) / np.sum(w[ok])) if ok.any() and np.sum(w[ok]) > 0 else None


def wmediana(x, w):
    ok = np.isfinite(x) & np.isfinite(w) & (w > 0)
    if not ok.any():
        return None
    o = np.argsort(x[ok])
    xs, ws = x[ok][o], w[ok][o]
    c = np.cumsum(ws)
    return float(xs[np.searchsorted(c, 0.5 * c[-1])])


# ------------------------------------------------------------------ insumos

CAPAS_REQ = ["lst", "ndvi", "arbolado", "construido", "agua", "poblacion", "trafico",
             "susceptibilidad_inundacion", "distancia_verde", "distancia_verde_025ha", "altitud"]
CAPAS_OPC = ["cob_pasto", "cob_cultivo", "cob_suelo", "hand", "hand_rio_mayor"]


def cargar_insumos():
    capas, faltan = {}, []
    for n in CAPAS_REQ + CAPAS_OPC:
        ruta = os.path.join(comun.REJILLA_NPY, f"{n}.npy")
        if os.path.exists(ruta):
            capas[n] = comun.cargar_capa(n).astype(np.float64)
        else:
            faltan.append(n)
    meta = {}
    for n in CAPAS_REQ:
        ruta = os.path.join(comun.CAPAS, f"{n}.json")
        if os.path.exists(ruta):
            meta[n] = json.load(open(ruta, encoding="utf-8"))
    return capas, meta, faltan


def transformador():
    from pyproj import Transformer
    return Transformer.from_crs("EPSG:4326", UTM, always_xy=True)


def a_utm(geom, tr):
    from shapely.ops import transform
    return transform(tr.transform, geom)


def centros_utm(tr):
    lat, lon = comun.centros_celdas()
    x, y = tr.transform(lon, lat)
    return np.asarray(x), np.asarray(y)


def celda(lat, lon):
    f = int(np.floor((comun.NORTE - lat) / comun.RES))
    c = int(np.floor((lon - comun.OESTE) / comun.RES))
    if 0 <= f < comun.ALTO and 0 <= c < comun.ANCHO:
        return f, c
    return None


def rasterizar(geoms_vals, all_touched=False):
    from rasterio.features import rasterize
    if not geoms_vals:
        return np.zeros((comun.ALTO, comun.ANCHO), dtype=np.uint8)
    return rasterize(geoms_vals, out_shape=(comun.ALTO, comun.ANCHO), transform=comun.transformacion(),
                     fill=0, dtype="uint8", all_touched=all_touched)


def ideam_amenaza():
    """Rejilla 0–3 (0 sin mancha, 1 baja, 2 media, 3 alta) de la amenaza por creciente súbita TR 50 del IDEAM."""
    from shapely.geometry import shape
    ruta = os.path.join(comun.FUENTES, "inundacion", "ideam_0_creciente_subita_tr50.geojson")
    if not os.path.exists(ruta):
        return None, "falta fuentes/inundacion/ideam_0_creciente_subita_tr50.geojson"
    g = json.load(open(ruta, encoding="utf-8"))
    cod = {"BAJA": 1, "MEDIA": 2, "ALTA": 3}
    out = np.zeros((comun.ALTO, comun.ANCHO), dtype=np.uint8)
    for nivel in ("BAJA", "MEDIA", "ALTA"):            # el más alto se escribe al final
        geoms = [(shape(f["geometry"]), 1) for f in g["features"] if f["properties"].get("ame") == nivel]
        msk = rasterizar(geoms) > 0
        out[msk] = cod[nivel]
    return out, None


def tr50_alta_poligonos(tr, rio_utm):
    """Polígonos de amenaza ALTA de la capa 0 del IDEAM con sus atributos y su distancia al eje OSM del La Vieja (UTM)."""
    from shapely.geometry import shape
    ruta = os.path.join(comun.FUENTES, "inundacion", "ideam_0_creciente_subita_tr50.geojson")
    if not os.path.exists(ruta):
        return None
    out = []
    for f in json.load(open(ruta, encoding="utf-8"))["features"]:
        p = f["properties"]
        if p.get("ame") != "ALTA":
            continue
        g = a_utm(shape(f["geometry"]), tr)
        out.append({"objectid": p.get("objectid"), "corriente_ideam": p.get("corriente"), "cuenca_ideam": p.get("cuenca"),
                    "area_ha": r(p.get("area_tot_ha"), 2), "distancia_minima_al_eje_la_vieja_km": r(g.distance(rio_utm) / 1000, 2),
                    "distancia_centroide_al_eje_la_vieja_km": r(g.centroid.distance(rio_utm) / 1000, 2)})
    return sorted(out, key=lambda d: d["distancia_minima_al_eje_la_vieja_km"])


def tr50_alta_tipo(tr50_alta):
    """Rejilla de la amenaza ALTA TR 50 según el polígono: 1 = junto al eje del La Vieja (≤ DIST_TR50_RIO_M), 2 = corrientes menores."""
    from shapely.geometry import shape
    ruta = os.path.join(comun.FUENTES, "inundacion", "ideam_0_creciente_subita_tr50.geojson")
    tipo = {p_["objectid"]: (1 if p_["distancia_minima_al_eje_la_vieja_km"] * 1000 <= DIST_TR50_RIO_M else 2) for p_ in tr50_alta}
    feats = [f for f in json.load(open(ruta, encoding="utf-8"))["features"] if f["properties"].get("ame") == "ALTA"]
    return rasterizar([(shape(f["geometry"]), tipo[f["properties"]["objectid"]]) for f in feats])


def estado_coherencia(coh, periodo):
    """Estado de la parte urbana de un periodo La Niña según el diagnóstico: no_coherente, dudosa, coherente, sin_evaluar o None."""
    return ((coh or {}).get("estado_por_periodo") or {}).get(periodo, {}).get("parte_urbana")


def frase_coherencia(estado):
    """Predicado (tras «cuya parte urbana» o «la parte urbana de La Niña X») generado del diagnóstico, no escrito a mano."""
    return {"no_coherente": "no es coherente con el relieve",
            "dudosa": "tiene una coherencia dudosa con el relieve",
            "coherente": "resultó coherente con el relieve en esta ejecución",
            "sin_evaluar": "no se pudo evaluar frente al relieve (pocas celdas)"}.get(
        estado, "no se evaluó frente al relieve en esta ejecución (falta el diagnóstico)")


def resumen_coherencia(coh, periodo):
    """Frase con el diagnóstico de coherencia topográfica de un periodo (dentro frente a fuera de la mancha)."""
    if not coh:
        return None
    def par(amb, tipo, p_):
        b = coh[amb][tipo]
        f = b["periodos"].get(p_, {})
        if f.get("hand_mediana_m") is None:
            return None
        return (f"{es(f['hand_mediana_m'], 1)} m dentro frente a {es(b['referencia_fuera_de_toda_mancha']['hand_mediana_m'], 1)} m fuera "
                f"(P = {es(f['prob_hand_menor_que_referencia'], 2)})")
    u_t, u_a = par("cabecera", "todas_las_celdas", periodo), par("cabecera", "celdas_abiertas", periodo)
    rur = par("fuera_de_la_cabecera", "todas_las_celdas", periodo)
    # el periodo coherente con más población urbana sirve de contraste
    otros = [(p_, f) for p_, f in coh["cabecera"]["todas_las_celdas"]["periodos"].items()
             if p_ != periodo and f.get("coherente_con_el_relieve")]
    otro = max(otros, key=lambda kv: kv[1]["poblacion"] or 0) if otros else None
    txt = (f"HAND mediano de la parte urbana de La Niña {periodo}: {u_t or 's. d.'}"
           + (f"; en celdas abiertas, {u_a}" if u_a else "")
           + (f". En el campo, la misma mancha sí está en el fondo del valle: {rur}" if rur else "")
           + (f"; la de {otro[0]} en la ciudad, {par('cabecera', 'todas_las_celdas', otro[0])}" if otro else "")
           + ". P = probabilidad de que una celda de la mancha esté más baja que una de fuera (0,5 = sin diferencia).")
    return txt


def ideam_nina():
    """Áreas afectadas por inundación en eventos La Niña (IDEAM), rasterizadas por centro de celda.

    Devuelve (por_periodo {periodo: máscara}, unión, n_periodos por celda, unión reducida y ampliada ±BORDE_CELDAS,
    lista de capas usadas, error). Las versiones v1 y v2 de un mismo año se unen en un solo periodo.
    """
    import glob
    from scipy import ndimage
    from shapely.geometry import shape
    por_periodo, usadas, vacias, faltan = {}, [], [], []
    for capa, periodo in IDEAM_NINA.items():
        rutas = glob.glob(os.path.join(comun.FUENTES, "inundacion", f"ideam_{capa}_*.geojson"))
        if not rutas:
            faltan.append(capa)
            continue
        g = json.load(open(rutas[0], encoding="utf-8"))
        if not g.get("features"):
            vacias.append(capa)
            continue
        msk = rasterizar([(shape(f["geometry"]), 1) for f in g["features"]]) > 0
        por_periodo[periodo] = por_periodo.get(periodo, np.zeros_like(msk)) | msk
        usadas.append({"capa": capa, "periodo": periodo, "nombre_archivo": os.path.basename(rutas[0]),
                       "poligonos": len(g["features"]),
                       "generalizacion_grados": g.get("consulta", {}).get("generalizacion_grados")})
    if not por_periodo:
        return None, f"faltan las capas La Niña del IDEAM en fuentes/inundacion (capas {faltan})"
    union = np.zeros((comun.ALTO, comun.ANCHO), dtype=bool)
    n = np.zeros((comun.ALTO, comun.ANCHO), dtype=np.int16)
    for msk in por_periodo.values():
        union |= msk
        n += msk
    yy, xx = np.mgrid[-BORDE_CELDAS:BORDE_CELDAS + 1, -BORDE_CELDAS:BORDE_CELDAS + 1]
    disco = (yy ** 2 + xx ** 2) <= BORDE_CELDAS ** 2
    return {"por_periodo": dict(sorted(por_periodo.items())), "union": union, "n_periodos": n,
            "reducida": ndimage.binary_erosion(union, disco), "ampliada": ndimage.binary_dilation(union, disco),
            "capas_usadas": usadas, "capas_vacias": vacias, "capas_faltantes": faltan}, None


def coherencia_topografica_nina(nina, C, cab, pop, area, tr50a=None):
    """Diagnóstico por periodo La Niña: ¿la mancha está más baja sobre el drenaje (HAND) que su entorno no inundado?

    Para cada periodo y ámbito (cabecera / fuera de la cabecera) compara el HAND de las celdas de la mancha con el de las
    celdas del mismo ámbito fuera de TODA mancha La Niña, con todas las celdas y solo con celdas abiertas (construido
    < ABIERTA_CONSTRUIDO % y arbolado < ABIERTA_ARBOLADO %: allí el DSM se acerca al terreno). El estadístico es la
    probabilidad de superioridad P(HAND dentro < HAND fuera) = 1 − U/(n1·n2) de Mann-Whitney (0,5 = sin diferencia);
    no se da valor p porque las celdas vecinas no son independientes.
    """
    from scipy.stats import mannwhitneyu
    if "hand" not in C:
        return None, "Falta fuentes/rejilla/hand.npy (producto inundacion): no se calcula la coherencia topográfica de las manchas La Niña."
    H = C["hand"]
    HR = C.get("hand_rio_mayor")
    abierta = (C["construido"] < ABIERTA_CONSTRUIDO) & (C["arbolado"] < ABIERTA_ARBOLADO)
    u = nina["union"]
    out = {}
    for amb, sel_amb in (("cabecera", cab), ("fuera_de_la_cabecera", ~cab)):
        out[amb] = {}
        for tipo, t in (("todas_las_celdas", np.ones_like(cab)), ("celdas_abiertas", abierta)):
            ref = sel_amb & t & ~u & np.isfinite(H)
            bloque = {"referencia_fuera_de_toda_mancha": {
                "celdas": int(ref.sum()), "hand_mediana_m": r(np.median(H[ref]), 2) if ref.any() else None,
                "hand_rio_mayor_mediana_m": r(np.nanmedian(HR[ref]), 2) if (HR is not None and ref.any()) else None,
                "pct_celdas_hand_le_6m": r(100 * np.mean(H[ref] <= 6), 1) if ref.any() else None}, "periodos": {}}
            for p_, mk in nina["por_periodo"].items():
                sp = sel_amb & t & mk & np.isfinite(H)
                n = int(sp.sum())
                fila = {"celdas": n, "area_ha": r(area[sp].sum() / 1e4, 1), "poblacion": r(pop[sp].sum(), 0)}
                if n >= MIN_CELDAS_COHERENCIA and ref.sum() >= MIN_CELDAS_COHERENCIA:
                    U = mannwhitneyu(H[sp], H[ref], alternative="two-sided").statistic
                    prob = 1.0 - U / (n * ref.sum())
                    fila.update({
                        "hand_mediana_m": r(np.median(H[sp]), 2),
                        "hand_p25_p75_m": [r(np.percentile(H[sp], 25), 2), r(np.percentile(H[sp], 75), 2)],
                        "hand_rio_mayor_mediana_m": r(np.nanmedian(HR[sp]), 2) if HR is not None else None,
                        "pct_celdas_hand_le_6m": r(100 * np.mean(H[sp] <= 6), 1),
                        "diferencia_mediana_con_referencia_m": r(np.median(H[sp]) - np.median(H[ref]), 2),
                        "prob_hand_menor_que_referencia": r(prob, 3),
                        "coherente_con_el_relieve": bool(prob >= COHERENCIA_PROB_MIN),
                    })
                else:
                    fila["nota"] = f"menos de {MIN_CELDAS_COHERENCIA} celdas: no se evalúa"
                bloque["periodos"][p_] = fila
            out[amb][tipo] = bloque
    # estado de la parte urbana de cada periodo: no coherente (falla con todas las celdas y con las abiertas), dudosa (falla en una)
    # o coherente; con la población de la cabecera que solo está en esa mancha (fuera de las demás y de la amenaza ALTA TR 50)
    tr50a = np.zeros_like(u) if tr50a is None else tr50a
    marcados, estado = [], {}
    for p_, mk in nina["por_periodo"].items():
        otras = np.zeros_like(u)
        for q_, mq in nina["por_periodo"].items():
            if q_ != p_:
                otras |= mq
        solo = cab & mk & ~otras & ~tr50a
        urb = [out["cabecera"][t]["periodos"][p_].get("coherente_con_el_relieve") for t in ("todas_las_celdas", "celdas_abiertas")]
        rur = out["fuera_de_la_cabecera"]["todas_las_celdas"]["periodos"][p_].get("coherente_con_el_relieve")
        ev = [v for v in urb if v is not None]
        est_ = "sin_evaluar" if not ev else ("no_coherente" if all(v is False for v in ev) else ("dudosa" if False in ev else "coherente"))
        estado[p_] = {"parte_urbana": est_, "parte_rural_coherente": rur,
                      "poblacion_cabecera_en_la_mancha": r(pop[cab & mk].sum(), 0),
                      "poblacion_cabecera_solo_en_esta_mancha": r(pop[solo].sum(), 0)}
        if est_ in ("no_coherente", "dudosa"):
            marcados.append({"periodo": p_, "parte_urbana": est_, "parte_rural_coherente": rur,
                             "incoherente_en": [t for t, v in zip(("todas_las_celdas", "celdas_abiertas"), urb) if v is False],
                             "poblacion_cabecera_solo_en_esta_mancha": estado[p_]["poblacion_cabecera_solo_en_esta_mancha"]})
    out["estado_por_periodo"] = estado
    out["periodos_con_parte_urbana_no_coherente"] = marcados
    out["metodo"] = (f"HAND = altura sobre el cauce más cercano (capa hand del producto inundacion, DSM Copernicus con corrección parcial del dosel); "
                     f"hand_rio_mayor = altura sobre La Vieja o Cauca. Referencia: celdas del mismo ámbito fuera de toda mancha La Niña. Celdas "
                     f"abiertas: construido < {es(ABIERTA_CONSTRUIDO, 0)} % y arbolado < {es(ABIERTA_ARBOLADO, 0)} % (WorldCover 2021; supuesto: ahí el "
                     "DSM se acerca al terreno). prob_hand_menor_que_referencia = P(HAND de una celda de la mancha < HAND de una celda de "
                     "referencia), de la U de Mann-Whitney; 0,5 = sin diferencia. Coherente con el relieve si es ≥ "
                     f"{es(COHERENCIA_PROB_MIN, 2)} (supuesto). Sin valor p: las celdas vecinas no son independientes. Rasterizado por centro de celda.")
    out["interpretacion"] = ("Una mancha de inundación fluvial debería estar más baja sobre el drenaje que el terreno no inundado del mismo "
                             "ámbito. Si no lo está, puede ser un error de comisión o de generalización de la mancha, un encharcamiento no "
                             "fluvial (lluvia o alcantarillado) o un error del HAND (edificios en el DSM, cauces no representados); estos datos "
                             "no permiten distinguirlos. Un periodo no coherente no se descarta: se publica la cifra con y sin él.")
    return out, None


def superficie_vial_por_zona(zonas_utm, tr):
    """% del área de cada zona ocupado por calzadas OSM (ejes con un ancho supuesto por carril)."""
    from shapely.geometry import LineString
    from shapely.ops import unary_union
    ruta = os.path.join(comun.FUENTES, "osm-vias.json")
    if not os.path.exists(ruta):
        return None, None
    d = json.load(open(ruta, encoding="utf-8"))
    pols, sup = [], {}
    for e in d["elements"]:
        t = e.get("tags", {})
        hw = t.get("highway")
        if hw not in CARRILES or len(e.get("geometry", [])) < 2:
            continue
        try:
            n = int(str(t.get("lanes", "")).split(";")[0])
        except ValueError:
            n = CARRILES[hw]
        xs, ys = tr.transform([p["lon"] for p in e["geometry"]], [p["lat"] for p in e["geometry"]])
        ln = LineString(list(zip(xs, ys)))
        pols.append(ln.buffer(n * ANCHO_CARRIL_M / 2, cap_style=2))
        s = t.get("surface", "sin etiqueta")
        sup[s] = sup.get(s, 0.0) + ln.length
    red = unary_union(pols)
    out = {zid: 100 * float(red.intersection(g).area) / float(g.area) for zid, g in zonas_utm.items()}
    tot = sum(sup.values())
    return out, {k: r(100 * v / tot, 1) for k, v in sorted(sup.items(), key=lambda kv: -kv[1])}


def mgn_cabecera():
    from shapely.geometry import shape
    from shapely.ops import unary_union
    ruta = os.path.join(comun.FUENTES, "poblacion", "mgn2018_zona_urbana_76147.geojson")
    if not os.path.exists(ruta):
        return None
    g = json.load(open(ruta, encoding="utf-8"))
    geoms = [shape(f["geometry"]) for f in g["features"] if str(f["properties"].get("COD_CLAS")) == "1"]
    if not geoms:
        return None
    return rasterizar([(unary_union(geoms), 1)]) > 0


def vias_principales_utm(tr):
    """Ejes OSM trunk/primary/secondary/tertiary en UTM (para documentar el umbral de tráfico)."""
    from shapely.geometry import LineString
    ruta = os.path.join(comun.FUENTES, "osm-vias.json")
    if not os.path.exists(ruta):
        return None
    d = json.load(open(ruta, encoding="utf-8"))
    lineas = []
    for e in d["elements"]:
        if e.get("tags", {}).get("highway") in ("trunk", "primary", "secondary", "tertiary") and len(e.get("geometry", [])) >= 2:
            xs, ys = tr.transform([p["lon"] for p in e["geometry"]], [p["lat"] for p in e["geometry"]])
            lineas.append(LineString(list(zip(xs, ys))))
    return lineas


# ------------------------------------------------------------------ tendencias

def sen_mk(anios, vals):
    from scipy import stats
    a = np.asarray(anios, dtype=float)
    v = np.asarray(vals, dtype=float)
    ok = np.isfinite(v)
    a, v = a[ok], v[ok]
    if len(a) < 6:
        return None
    s = stats.theilslopes(v, a, alpha=0.95)
    t = stats.kendalltau(a, v)
    lo, hi = s[2] * 10, s[3] * 10
    sig = bool(t.pvalue < 0.05 and (lo > 0 or hi < 0))
    return {"sen_por_decada": r(s[0] * 10, 3), "ic95_sen": [r(lo, 3), r(hi, 3)], "mann_kendall_p": r(t.pvalue, 4),
            "n_anios": int(len(a)), "anios": [int(x) for x in a], "significativa": sig}


TRAMOS = {
    "2013_2025_landsat_8_9": (2013, 2025, "Principal: un solo tipo de sensor (TIRS), tramo preferente según datos/series/landsat.json."),
    "2013_2023_sin_cambio_geos_it": (2013, 2023, "Sensibilidad: excluye 2024-2025, cuando el USGS pasó de GEOS FP-IT a GEOS-IT como dato atmosférico del producto ST (desde el 1-ene-2024)."),
    "2000_2012_landsat_5_7": (2000, 2012, "Landsat 5 TM y 7 ETM+ (SLC-off desde mayo de 2003)."),
    "2000_2025_sin_armonizar": (2000, 2025, "Solo referencia, NO robusta: mezcla sensores; el salto de 2012-2013 (cambio de sensor y salto de causa no determinada) domina la pendiente."),
}


VARIANTES_SERIE = {
    "mediana": "Mediana espacial de las celdas de la zona (serie principal).",
    "media": "Media espacial de las celdas de la zona: menos sensible al salto entre los dos modos de una zona heterogénea.",
    "nucleo_construido": f"Mediana de las celdas de la zona con ≥ {NUCLEO_CONSTRUIDO:g} % construido (WorldCover 2021); solo si hay ≥ {MIN_CELDAS_NUCLEO} celdas.",
}


def resumen_variantes(tv, unidad):
    """Marca de robustez de una tendencia entre variantes (como en datos/series/landsat.json)."""
    vals = {k: v for k, v in tv.items() if v is not None}
    if not vals:
        return None
    sens = [v["sen_por_decada"] for v in vals.values()]
    sig = [k for k, v in vals.items() if v["significativa"]]
    signos = {np.sign(vals[k]["sen_por_decada"]) for k in sig}
    rango = f"Sen entre {es(min(sens), 3 if unidad == 'NDVI' else 2, True)} y {es(max(sens), 3 if unidad == 'NDVI' else 2, True)} {unidad}/década"
    if len(sig) == len(vals) and len(signos) == 1:
        lect = f"{'Aumento' if signos == {1.0} else 'Disminución'} consistente: las {len(vals)} variantes son significativas ({rango})."
        robusta = True
    elif not sig:
        lect = f"Sin tendencia detectable: ninguna de las {len(vals)} variantes es significativa ({rango})."
        robusta = True
    else:
        lect = (f"Depende del método: {len(sig)} de {len(vals)} variantes significativas ({', '.join(sig)}); {rango}. "
                "No es una conclusión robusta.")
        robusta = False
    return {"sen_min": r(min(sens), 4), "sen_max": r(max(sens), 4), "variantes_significativas": sig,
            "n_variantes": len(vals), "robusta": robusta, "lectura": lect}


def serie_y_tendencias(zonas, m, landsat_json, faltan, construido):
    """Series anuales por zona de las rejillas Landsat (mediana, media y núcleo construido), isla respecto a la
    referencia rural y tendencias por variante."""
    anios_meta = {a["anio"]: a for a in landsat_json["anios"]}
    conf = {a: bool(v.get("confiable")) for a, v in anios_meta.items()}
    rural, err_rural = None, None
    try:
        import landsat  # noqa: WPS433  (solo se usa landsat.mascaras(), sin red)
        rural = landsat.mascaras()["rural"]
    except Exception as e:  # pragma: no cover
        err_rural = f"No se pudo construir la referencia rural con landsat.mascaras(): {e}"
    ids = [z["id"] for z in zonas] + ["cabecera"]
    sel = {z["id"]: (m == z["indice"]) for z in zonas}
    sel["cabecera"] = m > 0
    nucleo = {i: sel[i] & (construido >= NUCLEO_CONSTRUIDO) for i in ids}
    n_nucleo = {i: int(nucleo[i].sum()) for i in ids}
    filas = []
    por_zona = {i: {"lst": [], "ndvi": [], "isla": [], "pct_celdas_lst": [], "pct_celdas_ndvi": [],
                    "lst_media": [], "ndvi_media": [], "lst_nucleo_construido": [], "ndvi_nucleo_construido": []} for i in ids}
    rural_lst, rural_ndvi, anios = [], [], []
    for anio in range(2000, 2026):
        rl = os.path.join(comun.REJILLA_NPY, f"lst_{anio}.npy")
        rn = os.path.join(comun.REJILLA_NPY, f"ndvi_{anio}.npy")
        if not (os.path.exists(rl) and os.path.exists(rn)):
            faltan.append(f"lst_{anio}/ndvi_{anio}")
            continue
        L, N = np.load(rl).astype(np.float64), np.load(rn).astype(np.float64)
        anios.append(anio)
        rmed = float(np.nanmedian(L[rural])) if rural is not None else None
        rnd = float(np.nanmedian(N[rural])) if rural is not None else None
        rural_lst.append(r(rmed, 3))
        rural_ndvi.append(r(rnd, 4))
        for i in ids:
            s = sel[i]
            fl, fn = np.isfinite(L[s]).mean(), np.isfinite(N[s]).mean()
            vl = float(np.nanmedian(L[s])) if fl >= MIN_FRAC_ZONA_ANIO else None
            vn = float(np.nanmedian(N[s])) if fn >= MIN_FRAC_ZONA_ANIO else None
            por_zona[i]["lst"].append(r(vl, 3))
            por_zona[i]["ndvi"].append(r(vn, 4))
            por_zona[i]["isla"].append(r(vl - rmed, 3) if (vl is not None and rmed is not None) else None)
            por_zona[i]["pct_celdas_lst"].append(r(100 * fl, 1))
            por_zona[i]["pct_celdas_ndvi"].append(r(100 * fn, 1))
            por_zona[i]["lst_media"].append(r(np.nanmean(L[s]), 3) if fl >= MIN_FRAC_ZONA_ANIO else None)
            por_zona[i]["ndvi_media"].append(r(np.nanmean(N[s]), 4) if fn >= MIN_FRAC_ZONA_ANIO else None)
            nc = nucleo[i]
            ok_n = n_nucleo[i] >= MIN_CELDAS_NUCLEO
            fln = np.isfinite(L[nc]).mean() if ok_n else 0
            fnn = np.isfinite(N[nc]).mean() if ok_n else 0
            por_zona[i]["lst_nucleo_construido"].append(r(np.nanmedian(L[nc]), 3) if ok_n and fln >= MIN_FRAC_ZONA_ANIO else None)
            por_zona[i]["ndvi_nucleo_construido"].append(r(np.nanmedian(N[nc]), 4) if ok_n and fnn >= MIN_FRAC_ZONA_ANIO else None)
        meta = anios_meta.get(anio, {})
        filas.append({"anio": anio, "confiable": conf.get(anio, False),
                      "motivo_no_confiable": landsat_json.get("anios_no_confiables", {}).get(str(anio)),
                      "sensores": meta.get("sensores"), "n_escenas": meta.get("n_escenas"),
                      "trimestres": meta.get("trimestres"), "hora_local_media": meta.get("hora_local_media"),
                      "celdas_frias_residuales": meta.get("celdas_frias_residuales")})
    def tendencia(serie, a0, a1):
        ys = [a for a in anios if a0 <= a <= a1 and conf.get(a)]
        vs = [serie[anios.index(a)] for a in ys]
        return sen_mk(ys, [np.nan if v is None else v for v in vs])

    tend, tend_var = {}, {}
    for i in ids:
        tend[i] = {}
        for var in ("lst", "isla", "ndvi"):
            tend[i][var] = {}
            for t, (a0, a1, _) in TRAMOS.items():
                if var == "ndvi" and t == "2000_2025_sin_armonizar":
                    continue
                tend[i][var][t] = tendencia(por_zona[i][var], a0, a1)
        # variantes (mediana, media, núcleo construido) para LST y NDVI, tramos de un solo tipo de sensor
        tend_var[i] = {}
        for var, unidad in (("lst", "°C"), ("ndvi", "NDVI")):
            tend_var[i][var] = {}
            for t in ("2013_2025_landsat_8_9", "2013_2023_sin_cambio_geos_it", "2000_2012_landsat_5_7"):
                a0, a1, _ = TRAMOS[t]
                tv = {"mediana": tend[i][var][t], "media": tendencia(por_zona[i][f"{var}_media"], a0, a1),
                      "nucleo_construido": tendencia(por_zona[i][f"{var}_nucleo_construido"], a0, a1)}
                tend_var[i][var][t] = {"variantes": tv, "resumen": resumen_variantes(tv, unidad)}
    tend_rural = {}
    for var, serie in (("lst", rural_lst), ("ndvi", rural_ndvi)):
        tend_rural[var] = {}
        for t, (a0, a1, _) in TRAMOS.items():
            ys = [a for a in anios if a0 <= a <= a1 and conf.get(a)]
            vs = [np.nan if serie[anios.index(a)] is None else serie[anios.index(a)] for a in ys]
            tend_rural[var][t] = sen_mk(ys, vs)
    return {"anios": anios, "filas": filas, "por_zona": por_zona, "rural_lst": rural_lst, "rural_ndvi": rural_ndvi,
            "tendencias": tend, "tendencias_variantes": tend_var, "celdas_nucleo": n_nucleo,
            "tendencias_rural": tend_rural, "err_rural": err_rural, "confiables": [a for a in anios if conf.get(a)],
            "mascara_rural": rural}


def lectura_tendencia(t, tv=None):
    p = t["lst"]["2013_2025_landsat_8_9"]
    s = t["isla"]["2013_2025_landsat_8_9"]
    g = t["lst"]["2000_2025_sin_armonizar"]
    if p is None:
        return "Sin datos suficientes."
    txt = (f"LST 2013-2025 (Landsat 8/9): Sen {es(p['sen_por_decada'], 2, True)} °C/década "
           f"(IC 95 % {es(p['ic95_sen'][0], 2, True)} a {es(p['ic95_sen'][1], 2, True)}; Mann-Kendall p = {es(p['mann_kendall_p'], 2)}): ")
    txt += "tendencia significativa. " if p["significativa"] else "sin tendencia detectable. "
    if s is not None:
        txt += (f"Diferencia con el campo: {es(s['sen_por_decada'], 2, True)} °C/década "
                f"({'significativa' if s['significativa'] else 'no significativa'}). ")
    if g is not None:
        txt += (f"El tramo 2000-2025 sin armonizar da {es(g['sen_por_decada'], 2, True)} °C/década, pero mezcla sensores y lo "
                "domina el salto de 2012-2013; no se usa para decidir.")
    if tv is not None:
        for var, et in (("lst", "LST"), ("ndvi", "NDVI Landsat")):
            res = (tv.get(var, {}).get("2013_2025_landsat_8_9") or {}).get("resumen")
            if res:
                txt += f" {et} 2013-2025 entre variantes (mediana, media, núcleo construido): {res['lectura']}"
    return txt


# ------------------------------------------------------------------ estadísticas por zona

def stats_zona(s, C, ctx):
    """Indicadores de una selección booleana s (zona o cabecera)."""
    A = ctx["area"]
    pop = ctx["pop"]
    P = float(pop[s].sum())
    area_km2 = float(A[s].sum() / 1e6)
    lst, ndvi = C["lst"], C["ndvi"]
    arb, con, agua = C["arbolado"], C["construido"], C["agua"]
    cal = s & (lst >= ctx["umbral_calor"])
    sv = s & (C["distancia_verde"] > DIST_VERDE_M)
    sv25 = s & (C["distancia_verde_025ha"] > DIST_VERDE_M)
    sus = C["susceptibilidad_inundacion"]
    tra = C["trafico"]
    d = {
        "celdas": int(s.sum()),
        "area_km2": r(area_km2, 3),
        "poblacion": r(P, 0),
        "densidad_hab_km2": r(P / area_km2, 0) if area_km2 > 0 else None,
        "densidad_sobre_area_construida_hab_km2": r(P / (np.sum(con[s] / 100 * A[s]) / 1e6), 0),
        "lst_media": r(np.nanmean(lst[s]), 2),
        "lst_p90": r(np.nanpercentile(lst[s], 90), 2),
        "lst_media_pob": r(wmedia(lst[s], pop[s]), 2),
        "pct_area_calor_extremo": r(100 * np.sum(A[cal]) / np.sum(A[s]), 1),
        "poblacion_calor_extremo": r(pop[cal].sum(), 0),
        "pct_poblacion_calor_extremo": r(100 * pop[cal].sum() / P, 1) if P > 0 else None,
        "ndvi_medio": r(np.nanmean(ndvi[s]), 3),
        "ndvi_medio_pob": r(wmedia(ndvi[s], pop[s]), 3),
        "arbolado_pct": r(np.mean(arb[s]), 1),
        "arbolado_pct_pob": r(wmedia(arb[s], pop[s]), 1),
        "construido_pct": r(np.mean(con[s]), 1),
        "construido_pct_pob": r(wmedia(con[s], pop[s]), 1),
        "agua_pct": r(np.mean(agua[s]), 2),
        "m2_arbolado_por_hab": r(np.sum(arb[s] / 100 * A[s]) / P, 1) if P > 0 else None,
        "pct_poblacion_sin_verde_300m": r(100 * pop[sv].sum() / P, 1) if P > 0 else None,
        "poblacion_sin_verde_300m": r(pop[sv].sum(), 0),
        "pct_poblacion_sin_verde_300m_umbral_025ha": r(100 * pop[sv25].sum() / P, 1) if P > 0 else None,
        "distancia_verde_mediana_pob_m": r(wmediana(C["distancia_verde"][s], pop[s]), 0),
        "poblacion_susceptibilidad_alta": r(pop[s & (sus == 3)].sum(), 0),
        "poblacion_susceptibilidad_media": r(pop[s & (sus == 2)].sum(), 0),
        "pct_poblacion_susceptibilidad_alta": r(100 * pop[s & (sus == 3)].sum() / P, 2) if P > 0 else None,
        "pct_poblacion_susceptibilidad_media": r(100 * pop[s & (sus == 2)].sum() / P, 1) if P > 0 else None,
        "pct_area_susceptibilidad_alta": r(100 * np.sum(A[s & (sus == 3)]) / np.sum(A[s]), 2),
        "pct_area_susceptibilidad_media": r(100 * np.sum(A[s & (sus == 2)]) / np.sum(A[s]), 1),
        "trafico_medio": r(np.mean(tra[s]), 1),
        "trafico_medio_pob": r(wmedia(tra[s], pop[s]), 1),
        "poblacion_trafico_alto": r(pop[s & (tra >= TRAFICO_ALTO)].sum(), 0),
        "pct_poblacion_trafico_alto": r(100 * pop[s & (tra >= TRAFICO_ALTO)].sum() / P, 1) if P > 0 else None,
        "pct_poblacion_trafico_ge_50": r(100 * pop[s & (tra >= TRAFICO_SENS)].sum() / P, 1) if P > 0 else None,
    }
    rios = ctx.get("rios_utm") or {}

    def dist_med(sel, rio, pesos=None):
        """Mediana de la distancia (km) de los centros de celda de sel al eje del río (por celda o ponderada)."""
        from shapely import distance as sdist, points
        if rio is None or not sel.any():
            return None
        dd = np.asarray(sdist(points(ctx["xutm"][sel], ctx["yutm"][sel]), rio)) / 1000.0
        return r(np.median(dd) if pesos is None else wmediana(dd, pesos[sel]), 2)

    if ctx.get("ideam") is not None:
        ide = ctx["ideam"]
        a3 = s & (ide == 3)
        d["contraste_ideam_creciente_subita_tr50"] = {
            "poblacion_amenaza_alta": r(pop[a3].sum(), 0),
            "poblacion_amenaza_media": r(pop[s & (ide == 2)].sum(), 0),
            "pct_poblacion_amenaza_alta": r(100 * pop[a3].sum() / P, 2) if P > 0 else None,
            "area_amenaza_alta_ha": r(np.sum(A[a3]) / 1e4, 2),
            "poblacion_amenaza_alta_en_clase_hand_0_o_1": r(pop[a3 & (sus <= 1)].sum(), 0),
            "distancia_mediana_amenaza_alta_al_eje_la_vieja_km": dist_med(a3, rios.get("la_vieja")),
        }
    nina = ctx.get("nina")
    if nina is not None:
        u = nina["union"]
        pp = nina["por_periodo"]
        otros = np.zeros_like(u)
        for p_, mk in pp.items():
            if p_ != PERIODO_SIN:
                otros |= mk
        tr50a = (ctx["ideam"] == 3) if ctx.get("ideam") is not None else np.zeros_like(u)
        solo = pp.get(PERIODO_SIN, np.zeros_like(u)) & ~otros & ~tr50a
        d["ideam_nina_observada"] = {
            "poblacion": r(pop[s & u].sum(), 0),
            "pct_poblacion": r(100 * pop[s & u].sum() / P, 2) if P > 0 else None,
            "area_ha": r(np.sum(A[s & u]) / 1e4, 2),
            "pct_area": r(100 * np.sum(A[s & u]) / np.sum(A[s]), 2),
            "poblacion_por_periodo": {p_: r(pop[s & mk].sum(), 0) for p_, mk in pp.items()},
            "poblacion_afectada_en_2_o_mas_periodos": r(pop[s & (nina["n_periodos"] >= 2)].sum(), 0),
            f"poblacion_solo_en_la_mancha_{PERIODO_SIN}": r(pop[s & solo].sum(), 0),
            "sensibilidad_borde_55m": {"mancha_reducida": r(pop[s & nina["reducida"]].sum(), 0),
                                       "mancha_ampliada": r(pop[s & nina["ampliada"]].sum(), 0)},
            "poblacion_por_clase_hand": {str(k): r(pop[s & u & (sus == k)].sum(), 0) for k in (3, 2, 1, 0)},
            "distancia_mediana_a_los_rios_km": {
                "la_vieja": {"por_celda": dist_med(s & u, rios.get("la_vieja")),
                             "ponderada_por_poblacion": dist_med(s & u, rios.get("la_vieja"), pop)},
                "cauca": {"por_celda": dist_med(s & u, rios.get("cauca")),
                          "ponderada_por_poblacion": dist_med(s & u, rios.get("cauca"), pop)},
            },
        }
        if ctx.get("ideam") is not None:
            ev = u | tr50a
            ev_sin = otros | tr50a
            d["ideam_evidencia_oficial"] = {
                "definicion": ("amenaza ALTA por creciente súbita TR 50 (IDEAM; corrientes de la cuenca directa del río La Vieja) ∪ área "
                               "afectada por La Niña 1988–2022 (IDEAM)"),
                "poblacion": r(pop[s & ev].sum(), 0),
                "pct_poblacion": r(100 * pop[s & ev].sum() / P, 2) if P > 0 else None,
                "area_ha": r(np.sum(A[s & ev]) / 1e4, 2),
                "sensibilidad_borde_55m": {
                    "con_nina_reducida": r(pop[s & (nina["reducida"] | tr50a)].sum(), 0),
                    "con_nina_ampliada": r(pop[s & (nina["ampliada"] | tr50a)].sum(), 0)},
                f"sin_{PERIODO_SIN}": {
                    "definicion": (f"igual, pero sin las capas La Niña {PERIODO_SIN} (8 y 22), cuya parte urbana "
                                   f"{frase_coherencia(ctx.get('estado_coherencia_sin'))} "
                                   "(ver indicadores.json → coherencia_topografica_nina)"),
                    "poblacion": r(pop[s & ev_sin].sum(), 0),
                    "pct_poblacion": r(100 * pop[s & ev_sin].sum() / P, 2) if P > 0 else None,
                    "area_ha": r(np.sum(A[s & ev_sin]) / 1e4, 2),
                },
            }
            # campos de primer nivel (los lee el frontend; se mantienen también los anidados)
            d["poblacion_evidencia_inundacion_ideam"] = d["ideam_evidencia_oficial"]["poblacion"]
            d["pct_poblacion_evidencia_inundacion_ideam"] = d["ideam_evidencia_oficial"]["pct_poblacion"]
            d[f"poblacion_evidencia_inundacion_ideam_sin_{PERIODO_SIN}"] = d["ideam_evidencia_oficial"][f"sin_{PERIODO_SIN}"]["poblacion"]
            d[f"pct_poblacion_evidencia_inundacion_ideam_sin_{PERIODO_SIN}"] = d["ideam_evidencia_oficial"][f"sin_{PERIODO_SIN}"]["pct_poblacion"]
    return d


def verde_publico_por_zona(zonas_utm, cab_utm, tr):
    """m² de verde público OSM (espacio_verde.geojson, publico=true) dentro de cada zona (UTM 18N)."""
    from shapely.geometry import shape
    from shapely.ops import unary_union
    ruta = os.path.join(VECT, "espacio_verde.geojson")
    if not os.path.exists(ruta):
        return None, None
    g = json.load(open(ruta, encoding="utf-8"))
    pols = [a_utm(shape(f["geometry"]), tr) for f in g["features"] if f["properties"].get("publico")]
    verde = unary_union([p.buffer(0) for p in pols])
    out = {zid: float(verde.intersection(geo).area) for zid, geo in zonas_utm.items()}
    out["cabecera"] = float(verde.intersection(cab_utm).area)
    return out, len(pols)


# ------------------------------------------------------------------ equipamientos

def equipamientos(C, ctx, zonas, zonas_ll, tr):
    from shapely.geometry import Point
    ruta = os.path.join(VECT, "equipamientos.geojson")
    if not os.path.exists(ruta):
        return None, None
    g = json.load(open(ruta, encoding="utf-8"))
    X, Y = ctx["xutm"], ctx["yutm"]
    feats = []
    for f in g["features"]:
        lon, lat = f["geometry"]["coordinates"]
        p = f["properties"]
        rc = celda(lat, lon)
        zona = None
        for z in zonas:
            if zonas_ll[z["id"]].contains(Point(lon, lat)):
                zona = z
                break
        prop = {"osm_id": p.get("osm_id"), "osm_url": p.get("osm_url"), "nombre": p.get("nombre"),
                "nombre_mostrar": p.get("nombre") or f"{(p.get('subtipo_es') or 'equipamiento').capitalize()} sin nombre en OSM",
                "categoria": p.get("categoria"), "categoria_es": p.get("categoria_es"),
                "subtipo": p.get("subtipo"), "subtipo_es": p.get("subtipo_es"), "municipio": p.get("municipio"),
                "zona_id": zona["id"] if zona else None, "zona": zona["nombre"] if zona else None}
        if rc is None:
            prop["nota"] = "fuera de la rejilla"
            feats.append({"type": "Feature", "geometry": f["geometry"], "properties": prop})
            continue
        fi, co = rc
        x0, y0 = tr.transform(lon, lat)
        f0, f1 = max(0, fi - 6), min(comun.ALTO, fi + 7)
        c0, c1 = max(0, co - 6), min(comun.ANCHO, co + 7)
        dd = np.hypot(X[f0:f1, c0:c1] - x0, Y[f0:f1, c0:c1] - y0)
        en = dd <= RADIO_EQ_M
        lst = float(C["lst"][fi, co])
        sus = int(C["susceptibilidad_inundacion"][fi, co])
        dvec = p.get("dist_verde_publico_05ha_m")
        dgrid = float(C["distancia_verde"][fi, co])
        dist = float(dvec) if dvec is not None else dgrid
        tra = float(C["trafico"][fi, co])
        margen = lst - ctx["umbral_calor"]
        nina = ctx.get("nina")
        prop.update({
            "lst_c": r(lst, 2),
            "calor_extremo": bool(lst >= ctx["umbral_calor"]),
            "lst_margen_umbral_c": r(margen, 2),
            "en_umbral_calor": bool(abs(margen) < MARGEN_UMBRAL_C),
            "ndvi_100m": r(np.nanmean(C["ndvi"][f0:f1, c0:c1][en]), 3),
            "arbolado_100m_pct": r(np.nanmean(C["arbolado"][f0:f1, c0:c1][en]), 1),
            "construido_100m_pct": r(np.nanmean(C["construido"][f0:f1, c0:c1][en]), 1),
            "celdas_en_100m": int(en.sum()),
            "susceptibilidad_inundacion_clase": sus,
            "susceptibilidad_inundacion": ctx["etiquetas_sus"].get(sus),
            "susceptibilidad_inundacion_detalle": ctx["etiquetas_sus_largas"].get(sus),
            "susceptibilidad_alta": bool(sus == 3),
            "amenaza_ideam_creciente_subita_tr50": (None if ctx.get("ideam") is None else
                                                    {0: "fuera de la mancha", 1: "baja", 2: "media", 3: "alta"}[int(ctx["ideam"][fi, co])]),
            "area_afectada_nina_ideam": None if nina is None else bool(nina["union"][fi, co]),
            "periodos_nina_ideam": None if nina is None else [p for p, mk in nina["por_periodo"].items() if mk[fi, co]],
            "dist_verde_publico_05ha_m": r(dist, 0),
            "dist_verde_fuente": "vector (producto verdes)" if dvec is not None else "rejilla distancia_verde",
            "dist_verde_rejilla_m": r(dgrid, 0),
            "a_mas_de_300m_de_verde": bool(dist > DIST_VERDE_M),
            "trafico_indice": r(tra, 1),
            "trafico_alto": bool(tra >= TRAFICO_ALTO),
        })
        if p.get("osm_id") in ("node/8474141918",):
            prop["etiquetado_dudoso"] = "Escuela de aviación etiquetada amenity=school en OSM; no es preescolar, básica ni media."
        if p.get("osm_id") in ("node/1447545029",):
            prop["etiquetado_dudoso"] = ("Etiquetada amenity=college en OSM; el Boletín estadístico municipal (según la revisión del "
                                         "producto verdes) la lista como Institución Educativa oficial.")
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
                      "properties": prop})
    return feats, g.get("metadatos", {})


def resumen_equipamientos(feats, zid):
    sel = [f["properties"] for f in feats if (zid == "cabecera" and f["properties"].get("zona_id")) or f["properties"].get("zona_id") == zid]
    def cuenta(lst):
        d = {c: 0 for c in CATEGORIAS}
        for p in lst:
            d[p["categoria"]] = d.get(p["categoria"], 0) + 1
        d["total"] = len(lst)
        return d
    exp = {
        "calor_extremo": cuenta([p for p in sel if p.get("calor_extremo")]),
        "susceptibilidad_alta": cuenta([p for p in sel if p.get("susceptibilidad_alta")]),
        "a_mas_de_300m_de_verde": cuenta([p for p in sel if p.get("a_mas_de_300m_de_verde")]),
        "trafico_alto": cuenta([p for p in sel if p.get("trafico_alto")]),
        "amenaza_alta_ideam_contraste": cuenta([p for p in sel if p.get("amenaza_ideam_creciente_subita_tr50") == "alta"]),
        "area_afectada_nina_ideam": cuenta([p for p in sel if p.get("area_afectada_nina_ideam")]),
        "calor_extremo_en_umbral": cuenta([p for p in sel if p.get("calor_extremo") and p.get("en_umbral_calor")]),
    }
    return {"por_categoria": cuenta(sel), "expuestos": exp}


# ------------------------------------------------------------------ calibración

def agregar(a, k, cab):
    H, W = a.shape
    h, w = H // k, W // k
    x = np.where(cab, a, np.nan)[:h * k, :w * k].reshape(h, k, w, k)
    return np.nanmean(x, axis=(1, 3))


def ols(y, X):
    X1 = np.column_stack([np.ones(len(y)), X])
    b, *_ = np.linalg.lstsq(X1, y, rcond=None)
    res = y - X1 @ b
    return b, res


def ols_completo(y, X, nombres):
    from scipy import stats
    n, k = X.shape
    X1 = np.column_stack([np.ones(n), X])
    b, *_ = np.linalg.lstsq(X1, y, rcond=None)
    res = y - X1 @ b
    s2 = res @ res / (n - k - 1)
    cov = s2 * np.linalg.inv(X1.T @ X1)
    se = np.sqrt(np.diag(cov))
    tcrit = stats.t.ppf(0.975, n - k - 1)
    r2 = 1 - res.var() / y.var()
    r2a = 1 - (1 - r2) * (n - 1) / (n - k - 1)
    return {"b": b, "se": se, "tcrit": tcrit, "res": res, "r2": r2, "r2_ajustado": r2a,
            "rmse": float(np.sqrt(np.mean(res ** 2))), "mae": float(np.mean(np.abs(res))), "n": n, "nombres": nombres}


def bootstrap_bloques(y, X, bloques, n_boot, rng):
    ub = np.unique(bloques)
    idx_por_bloque = {b: np.flatnonzero(bloques == b) for b in ub}
    out = np.empty((n_boot, X.shape[1] + 1))
    for i in range(n_boot):
        elegidos = rng.choice(ub, size=len(ub), replace=True)
        idx = np.concatenate([idx_por_bloque[b] for b in elegidos])
        out[i], _ = ols(y[idx], X[idx])
    return out, len(ub)


def correlograma(R, lags, paso_m):
    out = []
    for k in lags:
        pares = []
        a, b = R[:, :-k], R[:, k:]
        ok = np.isfinite(a) & np.isfinite(b)
        pares.append((a[ok], b[ok]))
        a, b = R[:-k, :], R[k:, :]
        ok = np.isfinite(a) & np.isfinite(b)
        pares.append((a[ok], b[ok]))
        u = np.concatenate([p[0] for p in pares])
        v = np.concatenate([p[1] for p in pares])
        out.append({"distancia_m": int(round(k * paso_m)), "correlacion_residuos": r(np.corrcoef(u, v)[0, 1], 3),
                    "pares": int(len(u))})
    return out


def vif(X, nombres):
    out = {}
    for j, n in enumerate(nombres):
        otros = np.delete(X, j, axis=1)
        _, res = ols(X[:, j], otros)
        r2 = 1 - res.var() / X[:, j].var()
        out[n] = r(1 / (1 - r2), 2) if r2 < 1 else None
    return out


def residuo_por_bins(res, x, cortes):
    out = []
    for a, b in zip(cortes[:-1], cortes[1:]):
        s = (x >= a) & (x < b) if b < cortes[-1] else (x >= a) & (x <= b)
        if s.sum() >= 5:
            out.append({"rango": f"{a}–{b}", "n": int(s.sum()), "residuo_medio": r(res[s].mean(), 3)})
    return out


def ajustar_modelo(nombre_y, y, X, nombres, bloques, bloques_sens, rng, escala_coef):
    """MCO + bootstrap espacial. escala_coef: dict nombre → factor (10 para pp de cobertura)."""
    m = ols_completo(y, X, nombres)
    boot, nb = bootstrap_bloques(y, X, bloques, N_BOOT, rng)
    boot_s, nbs = bootstrap_bloques(y, X, bloques_sens, N_BOOT, rng)
    coef = {}
    for j, n in enumerate(["intercepto"] + nombres):
        f = 1.0 if n == "intercepto" else escala_coef.get(n, 1.0)
        b = m["b"][j]
        coef[n] = {
            "valor": r(b * f, 4),
            "unidad": None,
            "ic95_bootstrap_bloques_500m": [r(np.percentile(boot[:, j], 2.5) * f, 4), r(np.percentile(boot[:, j], 97.5) * f, 4)],
            "ic95_bootstrap_bloques_1km": [r(np.percentile(boot_s[:, j], 2.5) * f, 4), r(np.percentile(boot_s[:, j], 97.5) * f, 4)],
            "ic95_ingenuo_iid": [r((b - m["tcrit"] * m["se"][j]) * f, 4), r((b + m["tcrit"] * m["se"][j]) * f, 4)],
        }
    return m, coef, boot, {"bloques_500m": nb, "bloques_1km": nbs}


def calibracion(C, ctx, zonas, m, rng, ndvi_landsat=None):
    from scipy import ndimage, stats
    cab = m > 0
    terreno = ndimage.percentile_filter(C["altitud"], 10, size=VENTANA_TERRENO)
    ctx["terreno"] = terreno
    k = AGREG
    frac = cab[: (comun.ALTO // k) * k, : (comun.ANCHO // k) * k].reshape(comun.ALTO // k, k, comun.ANCHO // k, k).mean(axis=(1, 3))
    okA = frac >= FRAC_UNIDAD
    A = {n: agregar(C[n], k, cab) for n in ("lst", "arbolado", "construido", "agua", "ndvi", "cob_suelo") if n in C}
    A["terreno"] = agregar(terreno, k, cab)
    # centro de cada unidad en filas/columnas de celda → bloque de bootstrap
    fu, cu = np.meshgrid(np.arange(okA.shape[0]) * k + k / 2, np.arange(okA.shape[1]) * k + k / 2, indexing="ij")
    def bloques_de(fil, col, tam):
        return (fil // tam).astype(int) * 10000 + (col // tam).astype(int)
    ok = okA & np.isfinite(A["lst"])
    y = A["lst"][ok]
    nombres = ["arbolado_pct", "construido_pct", "agua_pct", "altitud_terreno_m"]
    X = np.column_stack([A["arbolado"][ok], A["construido"][ok], A["agua"][ok], A["terreno"][ok]])
    esc = {"arbolado_pct": 10, "construido_pct": 10, "agua_pct": 10, "altitud_terreno_m": 10}
    bl, bl2 = bloques_de(fu[ok], cu[ok], BLOQUE), bloques_de(fu[ok], cu[ok], BLOQUE_SENS)
    mL, coefL, bootL, nbL = ajustar_modelo("lst", y, X, nombres, bl, bl2, rng, esc)
    for n in nombres:
        coefL[n]["unidad"] = "°C por +10 m" if n == "altitud_terreno_m" else "°C por +10 puntos porcentuales"
    coefL["intercepto"]["unidad"] = "°C"
    # residuos en la rejilla agregada
    Rgrid = np.full(okA.shape, np.nan)
    Rgrid[ok] = mL["res"]
    paso = k * comun.RES * 110574.0
    diag_L = {
        "r2": r(mL["r2"], 3), "r2_ajustado": r(mL["r2_ajustado"], 3), "rmse_c": r(mL["rmse"], 3), "mae_c": r(mL["mae"], 3),
        "asimetria_residuos": r(stats.skew(mL["res"]), 3), "curtosis_exceso_residuos": r(stats.kurtosis(mL["res"]), 3),
        "correlograma_residuos": correlograma(Rgrid, [1, 2, 4, 9], paso),
        "residuo_por_construido_pct": residuo_por_bins(mL["res"], X[:, 1], [0, 20, 40, 60, 80, 100]),
        "residuo_por_arbolado_pct": residuo_por_bins(mL["res"], X[:, 0], [0, 10, 20, 40, 60, 100]),
        "sd_residuo_por_tercil_de_ajustado": [],
        "vif": vif(X, nombres),
        "correlacion_arbolado_construido": r(np.corrcoef(X[:, 0], X[:, 1])[0, 1], 3),
        "unidades_con_agua_mayor_que_0": int((X[:, 2] > 0).sum()),
    }
    ajust = y - mL["res"]
    for a, b in zip(np.percentile(ajust, [0, 33.3, 66.7]), np.percentile(ajust, [33.3, 66.7, 100])):
        s = (ajust >= a) & (ajust <= b)
        diag_L["sd_residuo_por_tercil_de_ajustado"].append({"ajustado_c": f"{es(a, 1)}–{es(b, 1)}", "sd_residuo_c": r(mL["res"][s].std(), 3)})
    # sensibilidades del modelo de LST
    sens = {}
    def coef_rapido(yv, Xv, nom):
        """Coeficientes por +10 pp (coberturas), por +10 m (altitud) y por unidad de log(m) (distancia al río)."""
        b, res = ols(yv, Xv)
        return {n: r(b[j + 1] * (1 if n == "log_dist_rio_m" else 10), 4) for j, n in enumerate(nom)} | {"r2": r(1 - res.var() / yv.var(), 3), "n": int(len(yv))}
    sens["sin_altitud"] = coef_rapido(y, X[:, :3], nombres[:3])
    if "cob_suelo" in A:
        Xs = np.column_stack([X, A["cob_suelo"][ok]])
        sens["con_suelo_desnudo_separado"] = coef_rapido(y, Xs, nombres + ["suelo_desnudo_pct"])
    # distancia al río (La Vieja y Cauca) como posible confusor
    try:
        from shapely.geometry import Point  # noqa: F401
        from shapely.ops import unary_union
        tr = ctx["tr"]
        rios = unary_union([a_utm(comun.lineas_rio("rio_la_vieja"), tr)] +
                           [a_utm(comun.lineas_rio("rio_cauca"), tr)])
        from shapely import distance as sdist, points
        xs = agregar(ctx["xutm"], k, cab)[ok]
        ys = agregar(ctx["yutm"], k, cab)[ok]
        dr = np.asarray(sdist(points(xs, ys), rios))
        Xr = np.column_stack([X, np.log(np.maximum(dr, 30.0))])
        sens["con_log_distancia_a_rios"] = coef_rapido(y, Xr, nombres + ["log_dist_rio_m"])
    except Exception as e:  # pragma: no cover
        sens["con_log_distancia_a_rios"] = {"error": str(e)}
    # nivel de celda (sin agregar): atenuación esperada por los 100 m de TIRS
    okc = cab & np.isfinite(C["lst"])
    Xc = np.column_stack([C["arbolado"][okc], C["construido"][okc], C["agua"][okc], terreno[okc]])
    sens["nivel_celda_27m"] = coef_rapido(C["lst"][okc], Xc, nombres)
    # agregación 2×2
    A2 = {n: agregar(C[n], 2, cab) for n in ("lst", "arbolado", "construido", "agua")}
    t2 = agregar(terreno, 2, cab)
    f2 = cab[: (comun.ALTO // 2) * 2, : (comun.ANCHO // 2) * 2].reshape(comun.ALTO // 2, 2, comun.ANCHO // 2, 2).mean(axis=(1, 3))
    ok2 = (f2 >= FRAC_UNIDAD) & np.isfinite(A2["lst"])
    sens["unidades_2x2_55m"] = coef_rapido(A2["lst"][ok2], np.column_stack([A2["arbolado"][ok2], A2["construido"][ok2], A2["agua"][ok2], t2[ok2]]), nombres)
    for kk, et in ((6, "unidades_6x6_166m"), (8, "unidades_8x8_222m")):
        Ak = {n: agregar(C[n], kk, cab) for n in ("lst", "arbolado", "construido", "agua")}
        tk = agregar(terreno, kk, cab)
        fk = cab[: (comun.ALTO // kk) * kk, : (comun.ANCHO // kk) * kk].reshape(comun.ALTO // kk, kk, comun.ANCHO // kk, kk).mean(axis=(1, 3))
        okk = (fk >= FRAC_UNIDAD) & np.isfinite(Ak["lst"])
        sens[et] = coef_rapido(Ak["lst"][okk], np.column_stack([Ak["arbolado"][okk], Ak["construido"][okk], Ak["agua"][okk], tk[okk]]), nombres)
    # sesgo del modelo por zona (aplicado a las medias de zona, como lo usará el simulador)
    sesgo = {}
    b = mL["b"]
    for z in zonas:
        s = m == z["indice"]
        pred = b[0] + b[1] * C["arbolado"][s].mean() + b[2] * C["construido"][s].mean() + b[3] * C["agua"][s].mean() + b[4] * terreno[s].mean()
        obs = np.nanmean(C["lst"][s])
        sesgo[z["id"]] = {"lst_observada_media": r(obs, 2), "lst_predicha_con_medias_de_zona": r(pred, 2), "residuo_c": r(obs - pred, 2)}
    diag_L["residuo_por_zona"] = sesgo
    coefL["agua_pct"]["identificado"] = False
    escalas = [("nivel_celda_27m", "28 m"), ("unidades_2x2_55m", "55 m"), (None, "111 m"), ("unidades_6x6_166m", "166 m"), ("unidades_8x8_222m", "222 m")]
    serie_esc = [(et, coefL["arbolado_pct"]["valor"] if k is None else sens[k]["arbolado_pct"]) for k, et in escalas]
    diag_L["nota_escala"] = ("El coeficiente del arbolado crece con la escala de agregación: " +
                             "; ".join(f"{et} {es(v, 2, True)}" for et, v in serie_esc) +
                             " °C por 10 pp. Por debajo de 100 m lo atenúa la resolución térmica; el valor de 111 m es conservador para intervenciones que abarcan una zona.")
    peor = max(diag_L["residuo_por_construido_pct"], key=lambda d: abs(d["residuo_medio"]))
    diag_L["nota_no_linealidad"] = (f"No linealidad moderada: el residuo medio llega a {es(peor['residuo_medio'], 2, True)} °C en unidades con {peor['rango']} % "
                                    "construido (n = " + str(peor["n"]) + "); la relación con lo construido no es exactamente lineal.")
    zmax = max(sesgo, key=lambda i: abs(sesgo[i]["residuo_c"]))
    diag_L["nota_sesgo_zona"] = (f"Aplicado a las medias de zona, el modelo se desvía hasta {es(sesgo[zmax]['residuo_c'], 2, True)} °C ({zmax}); el simulador debe "
                                 "sumar el cambio predicho a la LST observada de la zona, no usar la LST predicha.")

    # ---------------- NDVI ~ arbolado + construido (por celda; Sentinel-2 10 m agregado ≈ resolución de WorldCover)
    okn = cab & np.isfinite(C["ndvi"])
    fc, cc = np.meshgrid(np.arange(comun.ALTO) + 0.5, np.arange(comun.ANCHO) + 0.5, indexing="ij")
    yN = C["ndvi"][okn]
    XN = np.column_stack([C["arbolado"][okn], C["construido"][okn]])
    nomN = ["arbolado_pct", "construido_pct"]
    blN, blN2 = bloques_de(fc[okn], cc[okn], BLOQUE), bloques_de(fc[okn], cc[okn], BLOQUE_SENS)
    mN, coefN, bootN, nbN = ajustar_modelo("ndvi", yN, XN, nomN, blN, blN2, rng, {"arbolado_pct": 10, "construido_pct": 10})
    for n in nomN:
        coefN[n]["unidad"] = "NDVI por +10 puntos porcentuales"
    coefN["intercepto"]["unidad"] = "NDVI"
    RgN = np.full(C["ndvi"].shape, np.nan)
    RgN[okn] = mN["res"]
    diag_N = {
        "r2": r(mN["r2"], 3), "r2_ajustado": r(mN["r2_ajustado"], 3), "rmse": r(mN["rmse"], 4), "mae": r(mN["mae"], 4),
        "asimetria_residuos": r(stats.skew(mN["res"]), 3), "curtosis_exceso_residuos": r(stats.kurtosis(mN["res"]), 3),
        "correlograma_residuos": correlograma(RgN, [1, 2, 4, 9, 18, 36], comun.RES * 110574.0),
        "residuo_por_construido_pct": residuo_por_bins(mN["res"], XN[:, 1], [0, 20, 40, 60, 80, 100]),
        "residuo_por_arbolado_pct": residuo_por_bins(mN["res"], XN[:, 0], [0, 10, 20, 40, 60, 100]),
        "vif": vif(XN, nomN),
    }
    sesgoN = {}
    bN = mN["b"]
    for z in zonas:
        s = m == z["indice"]
        pred = bN[0] + bN[1] * C["arbolado"][s].mean() + bN[2] * C["construido"][s].mean()
        obs = np.nanmean(C["ndvi"][s])
        sesgoN[z["id"]] = {"ndvi_observado_medio": r(obs, 3), "ndvi_predicho_con_medias_de_zona": r(pred, 3), "residuo": r(obs - pred, 3)}
    diag_N["residuo_por_zona"] = sesgoN
    okA2 = okA & np.isfinite(A["ndvi"])
    sensN = {"unidades_4x4_111m": coef_rapido(A["ndvi"][okA2], np.column_stack([A["arbolado"][okA2], A["construido"][okA2]]), nomN)}
    # Sensibilidad con otro sensor: NDVI Landsat 8/9 (mediana de los años confiables 2021–2023, alrededor de WorldCover 2021)
    if ndvi_landsat is not None:
        NL = ndvi_landsat["rejilla"]
        okl = cab & np.isfinite(NL) & np.isfinite(C["ndvi"])
        sensN["ndvi_landsat_por_celda"] = coef_rapido(NL[okl], np.column_stack([C["arbolado"][okl], C["construido"][okl]]), nomN)
        sensN["ndvi_landsat_por_celda"]["anios"] = ndvi_landsat["anios"]
        sensN["ndvi_landsat_por_celda"]["correlacion_con_ndvi_sentinel2"] = r(np.corrcoef(NL[okl], C["ndvi"][okl])[0, 1], 3)
        AL = agregar(NL, k, cab)
        okl4 = okA & np.isfinite(AL)
        sensN["ndvi_landsat_unidades_4x4_111m"] = coef_rapido(AL[okl4], np.column_stack([A["arbolado"][okl4], A["construido"][okl4]]), nomN)
    return {"lst": (mL, coefL, bootL, nbL, diag_L, sens, X), "ndvi": (mN, coefN, bootN, nbN, diag_N, sensN, XN)}


def ic_boot(v):
    return [r(np.percentile(v, 2.5), 4), r(np.percentile(v, 97.5), 4)]


# ------------------------------------------------------------------ prioridades

def normalizar(vals, direccion, piso):
    v = np.array([np.nan if x is None else x for x in vals], dtype=float)
    lo, hi = np.nanmin(v), np.nanmax(v)
    rango = hi - lo
    den = max(rango, piso) if piso else rango
    if not np.isfinite(den) or den <= 0:
        return [0.0 for _ in v], [0.0 for _ in v]
    if direccion == "+":
        n, nm = (v - lo) / den, (v - lo) / (rango if rango > 0 else 1)
    else:
        n, nm = (hi - v) / den, (hi - v) / (rango if rango > 0 else 1)
    return [r(np.clip(x, 0, 1), 4) for x in n], [r(np.clip(x, 0, 1), 4) for x in nm]


def ranking(indice, ids):
    orden = sorted(ids, key=lambda i: (-indice[i], i))
    return orden, {i: orden.index(i) + 1 for i in ids}


# ------------------------------------------------------------------ principal

def main():
    t0 = datetime.now()
    open(LOG, "w").close()
    log("Producto «indicadores»: inicio")
    problemas = []
    C, meta, faltan = cargar_insumos()
    falt_req = [f for f in faltan if f in CAPAS_REQ]
    if falt_req:
        raise SystemExit(f"Faltan capas requeridas: {falt_req}. No se construye el producto (no se sustituyen por valores sintéticos).")
    if faltan:
        problemas.append(f"Capas opcionales ausentes (solo afectan sensibilidades): {faltan}")
    landsat_json = json.load(open(os.path.join(SERIES, "landsat.json"), encoding="utf-8"))
    tr = transformador()
    xutm, yutm = centros_utm(tr)
    zonas = comun.comunas()
    m = comun.mascara_zonas(zonas)
    cab = m > 0
    area = comun.area_celda_m2()
    pop = np.nan_to_num(C["poblacion"], nan=0.0)
    ideam, err = ideam_amenaza()
    if err:
        problemas.append(err)
    nina, err = ideam_nina()
    if err:
        problemas.append(err)
    coherencia = None
    if nina is not None:
        coherencia, err = coherencia_topografica_nina(nina, C, cab, pop, area, None if ideam is None else (ideam == 3))
        if err:
            problemas.append(err)
    sus_meta = meta["susceptibilidad_inundacion"].get("clases", [])
    etiquetas_sus = {int(c["valor"]): c.get("etiqueta_corta") or c["etiqueta"] for c in sus_meta}
    etiquetas_sus_largas = {int(c["valor"]): c["etiqueta"] for c in sus_meta}
    umbral = float(np.nanpercentile(C["lst"][cab], P_CALOR))
    rios_utm = {"la_vieja": a_utm(comun.lineas_rio("rio_la_vieja"), tr), "cauca": a_utm(comun.lineas_rio("rio_cauca"), tr)}
    tr50_alta = tr50_alta_poligonos(tr, rios_utm["la_vieja"]) if ideam is not None else None
    tipo_tr50 = tr50_alta_tipo(tr50_alta) if tr50_alta else None
    # estado de la parte urbana de La Niña PERIODO_SIN según el diagnóstico: todos los textos sobre su coherencia salen de aquí
    est_sin = estado_coherencia(coherencia, PERIODO_SIN)
    coh_sin = frase_coherencia(est_sin)
    sobreestima_sin = est_sin in ("no_coherente", "dudosa")
    ctx = {"area": area, "pop": pop, "umbral_calor": umbral, "ideam": ideam, "nina": nina, "etiquetas_sus": etiquetas_sus,
           "etiquetas_sus_largas": etiquetas_sus_largas, "xutm": xutm, "yutm": yutm, "tr": tr, "rios_utm": rios_utm,
           "estado_coherencia_sin": est_sin}
    meta_lst = meta["lst"]
    n_esc = meta_lst.get("escenas_usadas")
    HORA = meta_lst.get("hora_local_media_paso") or "media mañana"
    log(f"Zonas: {len(zonas)}; celdas en la cabecera (unión de zonas): {int(cab.sum())}; umbral de calor extremo (p{P_CALOR}) = {umbral:.2f} °C")
    if coherencia:
        for mk in coherencia["periodos_con_parte_urbana_no_coherente"]:
            log(f"Coherencia topográfica: La Niña {mk['periodo']} parte urbana {mk['parte_urbana']} (falla en {', '.join(mk['incoherente_en'])}); "
                f"parte rural coherente: {mk['parte_rural_coherente']}; hab solo en esa mancha: {mk['poblacion_cabecera_solo_en_esta_mancha']}")

    # ---------------- geometrías
    from shapely.ops import unary_union
    zonas_ll = {z["id"]: z["geom"] for z in zonas}
    zonas_utm = {z["id"]: a_utm(z["geom"], tr) for z in zonas}
    cab_utm = unary_union(list(zonas_utm.values()))
    solape_m2 = sum(zonas_utm[a].intersection(zonas_utm[b]).area for i, a in enumerate(zonas_utm) for b in list(zonas_utm)[i + 1:])

    # ---------------- indicadores por zona
    ids = [z["id"] for z in zonas]
    nombres_z = {z["id"]: z["nombre"] for z in zonas} | {"cabecera": "Cabecera (Comunas 1–7 + Zaragoza)"}
    est = {}
    for z in zonas:
        est[z["id"]] = stats_zona(m == z["indice"], C, ctx)
    est["cabecera"] = stats_zona(cab, C, ctx)
    lst_cab, lst_cab_pob = est["cabecera"]["lst_media"], est["cabecera"]["lst_media_pob"]
    for k, d in est.items():
        d["lst_anomalia"] = r(d["lst_media"] - lst_cab, 2)
        d["lst_anomalia_pob"] = r(d["lst_media_pob"] - lst_cab_pob, 2)
    verde, n_pol = verde_publico_por_zona(zonas_utm, cab_utm, tr)
    for k, d in est.items():
        d["area_poligono_km2"] = r((cab_utm.area if k == "cabecera" else zonas_utm[k].area) / 1e6, 3)
        if verde is not None:
            d["verde_publico_osm_m2"] = r(verde[k], 0)
            d["m2_verde_publico_por_hab"] = r(verde[k] / d["poblacion"], 2) if d["poblacion"] else None
    # equipamientos
    feats, meta_eq = equipamientos(C, ctx, zonas, zonas_ll, tr)
    if feats is None:
        problemas.append("Falta datos/vectores/equipamientos.geojson: no se calculan los indicadores de equipamientos.")
    else:
        for k in est:
            est[k]["equipamientos"] = resumen_equipamientos(feats, k)
    # tendencias y serie
    faltan_series = []
    S = serie_y_tendencias(zonas, m, landsat_json, faltan_series, C["construido"])
    if S["err_rural"]:
        problemas.append(S["err_rural"])
    if faltan_series:
        problemas.append(f"Rejillas anuales ausentes: {faltan_series}")
    for k in est:
        t = S["tendencias"][k]
        tv = S["tendencias_variantes"][k]
        p = t["lst"]["2013_2025_landsat_8_9"]
        est[k]["tendencia_lst_c_decada"] = p["sen_por_decada"] if p else None
        est[k]["tendencia_lst_significativa"] = bool(p["significativa"]) if p else None
        est[k]["tendencia_lst_ic95"] = p["ic95_sen"] if p else None
        est[k]["tendencia_lst"] = {"tramo_principal": "2013_2025_landsat_8_9", "por_tramo": t["lst"], "isla_por_tramo": t["isla"],
                                   "variantes_2013_2025": tv["lst"]["2013_2025_landsat_8_9"]}
        est[k]["lectura_tendencia_lst"] = lectura_tendencia(t, tv)
        pn = t["ndvi"]["2013_2025_landsat_8_9"]
        est[k]["tendencia_ndvi_landsat_por_decada"] = pn["sen_por_decada"] if pn else None
        est[k]["tendencia_ndvi_landsat"] = pn
        est[k]["tendencia_ndvi_landsat_variantes_2013_2025"] = tv["ndvi"]["2013_2025_landsat_8_9"]

    # ---------------- inundación: HAND frente a los registros del IDEAM (rejilla completa y cabecera)
    hand_vs_ideam = {}
    if ideam is not None:
        sus = C["susceptibilidad_inundacion"]
        for nom, selc in (("rejilla_completa", np.ones_like(cab)), ("cabecera", cab)):
            a3 = selc & (ideam == 3)
            ta = float(area[a3].sum())
            hand_vs_ideam[nom] = {
                "celdas_amenaza_alta_ideam": int(a3.sum()),
                "pct_area_amenaza_alta_ideam_por_clase_hand": {str(k): r(100 * area[a3 & (sus == k)].sum() / ta, 1) if ta else None for k in (3, 2, 1, 0)},
                "pct_area_amenaza_alta_ideam_en_clases_hand_0_o_1": r(100 * area[a3 & (sus <= 1)].sum() / ta, 1) if ta else None,
            }
            if tipo_tr50 is not None:
                hand_vs_ideam[nom]["por_tipo_de_corriente"] = {}
                for et, v in (("junto_al_la_vieja", 1), ("corrientes_menores_de_la_cuenca_directa", 2)):
                    at = a3 & (tipo_tr50 == v)
                    tt = float(area[at].sum())
                    hand_vs_ideam[nom]["por_tipo_de_corriente"][et] = {
                        "celdas": int(at.sum()), "area_ha": r(tt / 1e4, 1),
                        "pct_area_por_clase_hand": {str(k): r(100 * area[at & (sus == k)].sum() / tt, 1) if tt else None for k in (3, 2, 1, 0)},
                        "pct_area_en_clases_hand_0_o_1": r(100 * area[at & (sus <= 1)].sum() / tt, 1) if tt else None}
                hand_vs_ideam[nom]["por_tipo_de_corriente"]["criterio"] = (
                    f"Polígono ALTA a ≤ {es(DIST_TR50_RIO_M, 0)} m del eje OSM del La Vieja = junto al La Vieja; si no, corriente menor (supuesto).")
            if nina is not None:
                un = selc & nina["union"]
                tn = float(area[un].sum())
                hand_vs_ideam[nom]["pct_area_nina_observada_por_clase_hand"] = {str(k): r(100 * area[un & (sus == k)].sum() / tn, 1) if tn else None for k in (3, 2, 1, 0)}
                hand_vs_ideam[nom]["pct_poblacion_nina_observada_por_clase_hand"] = {
                    str(k): r(100 * pop[un & (sus == k)].sum() / max(pop[un].sum(), 1e-9), 1) for k in (3, 2, 1, 0)}
    # NDVI Sentinel-2 por año (cabecera, por adquisición) desde la serie del producto sentinel2: cifra rastreable
    ndvi_s2_anual = None
    ruta_s2 = os.path.join(SERIES, "sentinel2.json")
    if os.path.exists(ruta_s2):
        s2 = json.load(open(ruta_s2, encoding="utf-8"))
        ndvi_s2_anual = {}
        for anio in ("2024", "2025"):
            v = [x["ndvi_mediana_cabecera"] for x in s2.get("serie", []) if str(x.get("fecha", "")).startswith(anio)
                 and x.get("ndvi_mediana_cabecera") is not None]
            ndvi_s2_anual[anio] = {"mediana_de_las_fechas": r(np.median(v), 3) if v else None, "fechas": len(v)}

    # ---------------- coherencia de población
    mgn = mgn_cabecera()
    pc = meta["poblacion"]
    ser_pob = json.load(open(os.path.join(SERIES, "poblacion.json"), encoding="utf-8")) if os.path.exists(os.path.join(SERIES, "poblacion.json")) else {}
    pz_ser = {d["id"]: d["poblacion_hab"] for d in ser_pob.get("por_zona", [])}
    pob_cruda = {z["id"]: float(pop[m == z["indice"]].sum()) for z in zonas}
    suma_zonas = sum(pob_cruda.values())
    pob_cab_cruda = float(pop[cab].sum())
    coh = {
        "suma_poblacion_zonas": r(suma_zonas, 0),
        "poblacion_cabecera_union_de_zonas": est["cabecera"]["poblacion"],
        "diferencia_suma_zonas_menos_cabecera": r(suma_zonas - pob_cab_cruda, 3),
        "solape_entre_poligonos_de_zonas_m2": r(solape_m2, 0),
        "poblacion_cabecera_osm_mascara_urbana": r(pop[comun.mascara_urbana()].sum(), 0),
        "poblacion_cabecera_dane_mgn2018_celdas": r(pop[mgn].sum(), 0) if mgn is not None else None,
        "proyeccion_dane_2026_cabecera": pc.get("anclaje_dane", {}).get("dane_cabecera"),
        "pct_de_la_proyeccion_dane_cabecera": r(100 * est["cabecera"]["poblacion"] / pc["anclaje_dane"]["dane_cabecera"], 2) if pc.get("anclaje_dane") else None,
        "poblacion_zona_vs_serie_poblacion": {i: {"indicadores": est[i]["poblacion"], "series_poblacion": pz_ser.get(i)} for i in ids},
        "nota": ("La cabecera de este producto es la unión de las 8 zonas (Comunas 1–7 de OSM y la huella WorldCover de Zaragoza); "
                 "las zonas no se solapan en la rejilla, así que la suma de zonas es exactamente la cabecera. El polígono OSM de "
                 "comun.mascara_urbana() excluye Zaragoza; la cabecera DANE (MGN 2018) incluye Zaragoza y una franja periurbana "
                 "mayor. La proyección DANE 2026 de la cabecera es la cifra de referencia."),
    }
    ok_coh = abs(suma_zonas - pob_cab_cruda) < 1 and all(
        pz_ser.get(i) is None or abs(pob_cruda[i] - pz_ser[i]) <= 1 for i in ids)
    coh["coherente"] = bool(ok_coh)
    log(f"Población: zonas {suma_zonas:.0f}; OSM {coh['poblacion_cabecera_osm_mascara_urbana']}; MGN {coh['poblacion_cabecera_dane_mgn2018_celdas']}; DANE 2026 {coh['proyeccion_dane_2026_cabecera']}")

    # ---------------- documentación del umbral de tráfico
    doc_trafico = {}
    vias = vias_principales_utm(tr)
    if vias:
        from shapely import distance as sdist, points
        from shapely.ops import unary_union as uu
        red = uu(vias)
        alto = cab & (C["trafico"] >= TRAFICO_ALTO)
        dd = np.asarray(sdist(points(xutm[alto], yutm[alto]), red))
        doc_trafico = {
            "celdas_cabecera_indice_ge_60": int(alto.sum()),
            "pct_celdas_cabecera": r(100 * alto.sum() / cab.sum(), 1),
            "distancia_a_via_principal_m_p50_p90": [r(np.percentile(dd, 50), 0), r(np.percentile(dd, 90), 0)],
            "pct_a_menos_de_50m_de_via_principal": r(100 * np.mean(dd < 50), 1),
            "nota": ("Vías principales = highway trunk, primary, secondary o tertiary de fuentes/osm-vias.json (OSM, ODbL). "
                     "Según trafico.json la mediana del índice es 56,2 a menos de 25 m del eje de una vía principal: el umbral 60 "
                     "selecciona la parte más expuesta de esa franja inmediata. Es un umbral de la tarea, no sanitario."),
        }

    # ---------------- puntos de control
    puntos = {}
    for n, (la, lo) in PUNTOS.items():
        rc = celda(la, lo)
        f, c = rc
        puntos[n] = {"lat": la, "lon": lo, "zona": next((z["nombre"] for z in zonas if z["indice"] == m[f, c]), None),
                     "lst_c": r(C["lst"][f, c], 2), "calor_extremo": bool(C["lst"][f, c] >= umbral),
                     "trafico": r(C["trafico"][f, c], 1), "distancia_verde_m": r(C["distancia_verde"][f, c], 0),
                     "susceptibilidad_clase": int(C["susceptibilidad_inundacion"][f, c]), "poblacion_celda": r(pop[f, c], 2)}
    # río La Vieja: celdas de la cabecera a ≤ 100 m del eje
    from shapely import distance as sdist, points
    rio = a_utm(comun.lineas_rio("rio_la_vieja"), tr)
    drio = np.full(cab.shape, np.nan)
    drio[cab] = np.asarray(sdist(points(xutm[cab], yutm[cab]), rio))
    cerca = cab & (drio <= 100)
    calor_cab = cab & (C["lst"] >= umbral)
    verif_rio = {
        "celdas_cabecera_a_100m_del_la_vieja": int(cerca.sum()),
        "lst_media_a_100m_del_rio_c": r(np.nanmean(C["lst"][cerca]), 2),
        "lst_media_cabecera_a_mas_de_500m_del_rio_c": r(np.nanmean(C["lst"][cab & (drio > 500)]), 2),
        "pct_celdas_calor_extremo_a_100m_del_rio": r(100 * np.sum(calor_cab & cerca) / max(1, calor_cab.sum()), 2),
        "distancia_mediana_al_rio_celdas_calor_extremo_m": r(np.nanmedian(drio[calor_cab]), 0),
        "distancia_mediana_al_rio_resto_cabecera_m": r(np.nanmedian(drio[cab & ~calor_cab]), 0),
    }
    # norte/sur: Zaragoza (sur) frente a Comuna 1 (norte, junto al La Vieja)
    lat_c, _ = comun.centros_celdas()
    ns = {z["nombre"]: r(lat_c[m == z["indice"]].mean(), 4) for z in zonas}
    ns_ok = ns["Zaragoza (corregimiento)"] < min(v for k, v in ns.items() if k != "Zaragoza (corregimiento)")

    # ---------------- calibración
    log("Calibración: ajuste de modelos y bootstrap espacial…")
    rng = np.random.default_rng(SEMILLA)
    anios_nl = [a for a in (2021, 2022, 2023) if a in S["confiables"]
                and os.path.exists(os.path.join(comun.REJILLA_NPY, f"ndvi_{a}.npy"))]
    ndvi_landsat = None
    if anios_nl:
        pila = np.stack([np.load(os.path.join(comun.REJILLA_NPY, f"ndvi_{a}.npy")).astype(np.float64) for a in anios_nl])
        ndvi_landsat = {"rejilla": np.nanmedian(pila, axis=0), "anios": anios_nl}
    else:
        problemas.append("Sin rejillas NDVI Landsat confiables 2021–2023: no se calcula la sensibilidad del modelo de NDVI con otro sensor.")
    cal = calibracion(C, ctx, zonas, m, rng, ndvi_landsat)
    mL, coefL, bootL, nbL, diagL, sensL, XL = cal["lst"]
    mN, coefN, bootN, nbN, diagN, sensN, XN = cal["ndvi"]
    log(f"  LST: N={mL['n']} R²={mL['r2']:.3f} arbolado {coefL['arbolado_pct']['valor']} construido {coefL['construido_pct']['valor']} °C/10 pp")
    log(f"  NDVI: N={mN['n']} R²={mN['r2']:.3f} arbolado {coefN['arbolado_pct']['valor']} construido {coefN['construido_pct']['valor']} /10 pp")

    # =====================================================================================
    # SALIDA 1: indicadores.json
    fuentes = []
    for n in ["lst", "ndvi", "arbolado", "poblacion", "susceptibilidad_inundacion", "trafico", "distancia_verde"]:
        f = meta[n].get("fuente", {})
        fuentes.append({"capa": n, "nombre": f.get("nombre"), "url": f.get("url"), "licencia": f.get("licencia"), "cita": f.get("cita")})
    fuentes += [
        {"capa": "zonas", "nombre": "OpenStreetMap (Comunas 1–7) y ESA WorldCover 2021 (huella de Zaragoza, datos/zaragoza.json)",
         "url": "https://www.openstreetmap.org/copyright", "licencia": "ODbL 1.0 / CC BY 4.0",
         "cita": "© colaboradores de OpenStreetMap; © ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium"},
        {"capa": "verde público y equipamientos", "nombre": "OpenStreetMap (datos/vectores/espacio_verde.geojson y equipamientos.geojson del producto verdes)",
         "url": "https://www.openstreetmap.org/copyright", "licencia": "ODbL 1.0", "cita": "© colaboradores de OpenStreetMap"},
        {"capa": "inundación: registros oficiales", "nombre": ("IDEAM, servicio Amenaza_Ambiental: capa 0 «Amenaza Creciente Súbita TR 50 años, 8 cabeceras "
                                                               "municipales 2K» y capas 6, 7, 8, 9, 22, 23, 24, 26 y 27 «Áreas afectadas por inundación, La Niña» "
                                                               "(1988, 2000, 2011, 2012, 2016, 2020–2022; escala no declarada); en datos.gov.co, La Niña 1988, 2000, 2011 y 2012: "
                                                               "khg6-9h39, 5p6w-58v3, 6eu7-pzc5 y nufr-59j5"),
         "url": "https://visualizador.ideam.gov.co/gisserver/rest/services/Amenaza_Ambiental/MapServer",
         "licencia": LICENCIA_IDEAM, "cita": CITA_IDEAM},
        {"capa": "serie y tendencia", "nombre": "Rejillas anuales Landsat 2000–2025 (producto landsat)", "url": "https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2",
         "licencia": "Dominio público USGS", "cita": "Landsat Collection 2 Level-2 Science Products courtesy of the U.S. Geological Survey"},
    ]
    referencias = [
        {"nombre": "Decreto 1504 de 1998, arts. 12 y 14", "url": "https://normas.cra.gov.co/gestor/docs/decreto_1504_1998.htm",
         "uso": "Espacio público efectivo (zonas verdes, parques, plazas y plazoletas de carácter permanente); índice mínimo 15 m²/hab.", "verificado": True},
        {"nombre": "CONPES 3718 de 2012, Política Nacional de Espacio Público (31-ene-2012), Gráfico 7",
         "url": "https://www.minambiente.gov.co/wp-content/uploads/2021/10/Conpes-3718-de-2012.pdf",
         "uso": "Promedio nacional ajustado a 2010: 3,3 m²/hab; meta 5–6 m²/hab a 2015 para ciudades de más de 100.000 hab.", "verificado": True},
        {"nombre": "IDEAM, «Áreas Afectadas Inundación Niña 2011», datos.gov.co 6eu7-pzc5", "url": "https://www.datos.gov.co/api/views/6eu7-pzc5.json",
         "uso": "Licencia CC BY-SA 4.0; advertencia «Los datos a visualizar o descargar a continuación no han sido validados por el IDEAM»; sin escala declarada.",
         "verificado": True},
        {"nombre": "Catálogo de datos.gov.co: conjuntos «Emergencias UNGRD» (wwkg-r6te, 2019–2022; otros desde 2019)",
         "url": "https://api.us.socrata.com/api/catalog/v1?domains=www.datos.gov.co&q=emergencias%20UNGRD",
         "uso": "Los registros abiertos de emergencias de la UNGRD en datos.gov.co no cubren 2010–2011.", "verificado": True},
        {"nombre": "UNGRD, «Consolidado reporte de emergencias 1998-2021» (repositorio institucional)",
         "url": "https://repositorio.gestiondelriesgo.gov.co:8443/handle/20.500.11762/20782",
         "uso": "Fuente sugerida para contrastar La Niña 2010–2011 en Cartago (registros por municipio, no por barrio).", "verificado": False,
         "nota": "Encontrado con un buscador web; el servidor no respondió desde aquí el 2026-10-01, así que su contenido no se comprobó."},
    ]
    cab_d = est["cabecera"]
    ref_verde = {
        "indicador_local": "m2_verde_publico_por_hab = verde público mapeado en OSM (parques, jardines, zonas de juego y recreativas de acceso supuesto público) / población 2026",
        "decreto_1504_1998_minimo_espacio_publico_efectivo_m2_hab": 15,
        "conpes_3718_promedio_nacional_2010_m2_hab": 3.3,
        "conpes_3718_meta_2015_m2_hab": [5, 6],
        "cabecera_m2_verde_publico_por_hab": cab_d.get("m2_verde_publico_por_hab"),
        "pct_del_minimo_decreto_1504": r(100 * cab_d["m2_verde_publico_por_hab"] / 15, 1) if cab_d.get("m2_verde_publico_por_hab") is not None else None,
        "advertencia": ("No son conceptos idénticos: el espacio público efectivo incluye plazas y plazoletas duras y se mide con el inventario "
                        "municipal; el verde OSM es un inventario parcial (ver limitaciones de espacio_verde.geojson). La comparación es de "
                        "orden de magnitud. El diagnóstico del POT citado por Findeter (2022) da 1,68 m²/hab de espacio público efectivo "
                        "urbano en 2021 (verificado por el producto verdes)."),
    }
    zonas_out = []
    for z in zonas:
        d = {"id": z["id"], "nombre": z["nombre"], "fuente_geometria": z["fuente"]}
        d.update(est[z["id"]])
        zonas_out.append(d)
    cab_out = {"id": "cabecera", "nombre": "Cabecera (Comunas 1–7 + Zaragoza)", "fuente_geometria": "unión de las 8 zonas"}
    cab_out.update(est["cabecera"])
    # ---- textos de inundación generados de los datos
    ts_osm = None
    try:
        ts_osm = json.load(open(os.path.join(comun.FUENTES, "osm-vias.json"), encoding="utf-8")).get("osm3s", {}).get("timestamp_osm_base")
    except (OSError, ValueError):
        pass
    txt_tr50 = ""
    if tr50_alta:
        dmin = [p_["distancia_minima_al_eje_la_vieja_km"] for p_ in tr50_alta]
        lejos = [p_ for p_ in tr50_alta if p_["distancia_minima_al_eje_la_vieja_km"] * 1000 > DIST_TR50_RIO_M]
        txt_tr50 = (f"la capa del IDEAM atribuye sus {len(tr50_alta)} polígonos de amenaza ALTA a la corriente "
                    f"«{tr50_alta[0]['corriente_ideam']}» (cuenca «{tr50_alta[0]['cuenca_ideam']}»), pero "
                    + (f"{len(lejos)} de ellos están a {es(min(p_['distancia_minima_al_eje_la_vieja_km'] for p_ in lejos), 1)}–"
                       f"{es(max(p_['distancia_minima_al_eje_la_vieja_km'] for p_ in lejos), 1)} km del eje del río: corresponden a corrientes "
                       "menores de su cuenca directa" if lejos else f"todos están a ≤ {es(max(dmin), 1)} km del eje del río"))
    sin_ = f"sin_{PERIODO_SIN}"
    ev_ok = "ideam_evidencia_oficial" in est["cabecera"]
    if coherencia and est_sin != "no_coherente":
        problemas.append(f"La parte urbana de La Niña {PERIODO_SIN} {coh_sin} (estado '{est_sin}'): los textos se generan de ese diagnóstico; "
                         f"revisar si la variante 'inundacion_ideam_{sin_}' sigue siendo necesaria.")
    txt_coh = resumen_coherencia(coherencia, PERIODO_SIN) if coherencia else None
    txt_sin = ""
    if ev_ok:
        ec_ = est["cabecera"]["ideam_evidencia_oficial"]
        cambios = sorted(ids, key=lambda i: -(est[i]["ideam_evidencia_oficial"]["pct_poblacion"] - est[i]["ideam_evidencia_oficial"][sin_]["pct_poblacion"]))
        txt_sin = (f"con La Niña {PERIODO_SIN}, {es_int(ec_['poblacion'])} hab de la cabecera ({es(ec_['pct_poblacion'], 1)} %); sin ella, "
                   f"{es_int(ec_[sin_]['poblacion'])} hab ({es(ec_[sin_]['pct_poblacion'], 1)} %); por zona: "
                   + "; ".join(f"{nombres_z[i]} {es(est[i]['ideam_evidencia_oficial']['pct_poblacion'], 1)} → "
                               f"{es(est[i]['ideam_evidencia_oficial'][sin_]['pct_poblacion'], 1)} %"
                               for i in cambios if est[i]["ideam_evidencia_oficial"]["pct_poblacion"] != est[i]["ideam_evidencia_oficial"][sin_]["pct_poblacion"]))
    zonas_c = [i for i in sorted(ids, key=lambda i: -(est[i].get("ideam_nina_observada", {}).get(f"poblacion_solo_en_la_mancha_{PERIODO_SIN}") or 0))
               if (est[i].get("ideam_nina_observada", {}).get(f"poblacion_solo_en_la_mancha_{PERIODO_SIN}") or 0) > 0]
    lim_2011 = None
    if ev_ok and coherencia:
        sol = est["cabecera"]["ideam_nina_observada"][f"poblacion_solo_en_la_mancha_{PERIODO_SIN}"]
        ev_cab = est["cabecera"]["ideam_evidencia_oficial"]["poblacion"]
        lim_2011 = (f"La parte urbana de la mancha La Niña {PERIODO_SIN} del IDEAM {coh_sin}"
                    + (" y puede sobrestimar el área inundada. " if sobreestima_sin else "; se conserva la variante sin ella como sensibilidad. ")
                    + (txt_coh + " " if txt_coh else "")
                    + ("Puede ser un error de comisión o de generalización, un encharcamiento no fluvial o un error del HAND. " if sobreestima_sin else "")
                    + "El IDEAM advierte en datos.gov.co que estas capas no han sido validadas. "
                    + (f"De ella depende el {es(100 * sol / ev_cab, 0)} % de la cifra por defecto de la cabecera: " if ev_cab else "")
                    + f"{es_int(sol)} hab de la cabecera solo están en la mancha de {PERIODO_SIN}"
                    + (" (" + ", ".join(f"{nombres_z[i]} {es_int(est[i]['ideam_nina_observada'][f'poblacion_solo_en_la_mancha_{PERIODO_SIN}'])}" for i in zonas_c) + ")" if zonas_c else "")
                    + f". Registros oficiales {txt_sin} (variante 'inundacion_ideam_{sin_}'). Antes de usar las cifras de "
                    f"{', '.join(nombres_z[i] for i in zonas_c) or 'esas zonas'}, contrastar con {CONTRASTE_REGISTROS} sobre los barrios afectados en 2010–2011."
                    + "".join((" La parte urbana de La Niña " + mk['periodo'] + (" también" if sobreestima_sin else "") + " es ") + f"{'dudosa' if mk['parte_urbana'] == 'dudosa' else 'no coherente'} "
                              f"(falla con {' y '.join(t.replace('_', ' ') for t in mk['incoherente_en'])}), pero "
                              + (f"solo {es_int(mk['poblacion_cabecera_solo_en_esta_mancha'])} hab dependen únicamente de ella."
                                 if mk['poblacion_cabecera_solo_en_esta_mancha'] else "ningún habitante depende únicamente de ella.")
                              for mk in coherencia["periodos_con_parte_urbana_no_coherente"] if mk["periodo"] != PERIODO_SIN))
    lst_sig_z = [i for i in ids + ["cabecera"] if (est[i]["tendencia_lst"]["por_tramo"].get("2013_2025_landsat_8_9") or {}).get("significativa")]
    hv_cab = hand_vs_ideam.get("cabecera", {})
    hv_pob = hv_cab.get("pct_poblacion_nina_observada_por_clase_hand") or {}
    hv_tipo = hv_cab.get("por_tipo_de_corriente")
    z_menores = ([z["nombre"] for z in zonas if ((m == z["indice"]) & (ideam == 3) & (tipo_tr50 == 2)).any()]
                 if tipo_tr50 is not None else [])
    L = {
        "lst": f"La LST es temperatura de SUPERFICIE a media mañana ({HORA} hora local) en días despejados, no temperatura del aire ni la máxima del día.",
        "umbral_calor": "El umbral de calor extremo es relativo (p90 de la propia cabecera): por construcción ≈ 10 % del área de la cabecera queda en calor extremo; no indica riesgo sanitario.",
        "arbolado": "Arbolado = área que ESA WorldCover 2021 clasifica como árboles (≥ 10 % de cobertura por píxel de 10 m), no fracción de copa; subestima el arbolado de calle absorbido por la clase construida.",
        "ndvi": ("El NDVI 2024–2025 mezcla dos años distintos" + (
            f": la mediana por fecha del NDVI Sentinel-2 de la cabecera fue {es(ndvi_s2_anual['2024']['mediana_de_las_fechas'], 3)} en 2024 "
            f"({ndvi_s2_anual['2024']['fechas']} fechas) y {es(ndvi_s2_anual['2025']['mediana_de_las_fechas'], 3)} en 2025 ({ndvi_s2_anual['2025']['fechas']} fechas) "
            "(datos/series/sentinel2.json); las fechas no se reparten igual entre meses. No hay NDVI por año y zona."
            if ndvi_s2_anual and all(ndvi_s2_anual[a]["mediana_de_las_fechas"] is not None for a in ("2024", "2025")) else
            "; no hay NDVI por año y zona para cuantificar la diferencia.")),
        "osm": ("Verde público y equipamientos dependen de la completitud de OpenStreetMap: OSM tiene ≈ 26 % de las sedes educativas del MEN y ≈ 11 % "
                f"de las sedes de IPS del REPS (producto verdes); el acceso al verde se supone público en los {n_pol if n_pol is not None else 's. d.'} "
                "polígonos y el orden de las comunas por acceso no es robusto (ver datos/series/verdes.json → sensibilidad)."),
        "hand_ideam": (
            "Inundación: la susceptibilidad topográfica (HAND) y los registros oficiales del IDEAM no coinciden del todo dentro de la ciudad. De la amenaza "
            "ALTA por creciente súbita del IDEAM, la clase alta HAND cubre el "
            f"{es(hand_vs_ideam.get('rejilla_completa', {}).get('pct_area_amenaza_alta_ideam_por_clase_hand', {}).get('3'), 1)} % del área en toda la rejilla y el "
            f"{es(hv_cab.get('pct_area_amenaza_alta_ideam_por_clase_hand', {}).get('3'), 1)} % dentro de la cabecera "
            f"({hv_cab.get('celdas_amenaza_alta_ideam')} celdas IDEAM ALTA), donde el "
            f"{es(hv_cab.get('pct_area_amenaza_alta_ideam_en_clases_hand_0_o_1'), 1)} % cae en las clases HAND baja o > 15 m, que no descartan amenaza"
            + (f" (junto al La Vieja, el {es(hv_tipo['junto_al_la_vieja']['pct_area_en_clases_hand_0_o_1'], 1)} % de {es(hv_tipo['junto_al_la_vieja']['area_ha'], 1)} ha; "
               f"en las corrientes menores de {' y '.join(z_menores) or 's. d.'}, el {es(hv_tipo['corrientes_menores_de_la_cuenca_directa']['pct_area_en_clases_hand_0_o_1'], 1)} % "
               f"de {es(hv_tipo['corrientes_menores_de_la_cuenca_directa']['area_ha'], 1)} ha)" if hv_tipo else "") + ". "
            + (f"De la población de la cabecera en áreas afectadas por La Niña, el {es(hv_pob.get('3'), 1)} % está en clase alta HAND y el "
               f"{es(hv_pob.get('2'), 1)} % en media. " if hv_pob else "")
            + "El desacuerdo puede venir de los dos lados: del HAND (DSM con edificios, red de drenaje) y de los registros (bordes gruesos, escala no declarada"
            + (f"; la parte urbana de La Niña {PERIODO_SIN} {coh_sin}" + (f", ver la limitación sobre La Niña {PERIODO_SIN}" if lim_2011 else "") if nina is not None else "")
            + "). Poca población en clase alta HAND NO significa ausencia de amenaza: "
            + ("por eso el componente de inundación por defecto usa los registros del IDEAM. " if ev_ok else
               "en esta ejecución faltan registros del IDEAM y el componente de inundación usa la clase alta HAND (ver 'problemas'). ")
            + "Consúltense además el POT y la CVC.") if hand_vs_ideam else None,
        "registros_ideam": (
            "Registros del IDEAM: la amenaza por creciente súbita (TR 50 años) solo cubre las corrientes de la cuenca directa del río La Vieja junto a "
            "la cabecera" + (f" ({txt_tr50})" if txt_tr50 else "") + ", no la inundación lenta del Cauca; las áreas afectadas por La Niña son "
            "manchas de escala no declarada (bordes gruesos, eventos posiblemente incompletos, sin profundidad ni duración), el IDEAM advierte en "
            "datos.gov.co que no las ha validado y no son una zonificación de amenaza. Con la mancha reducida o ampliada ≈ 55 m la población expuesta "
            "cambia mucho (ver 'sensibilidad_borde_55m'). La población dentro de cada mancha es la de 2026, no la afectada en el evento: la "
            "inundación de 1988 se registró sobre una ciudad distinta de la actual."
            + ("" if ev_ok else
               " En esta ejecución faltan " + ("todos esos registros" if (ideam is None and nina is None) else "parte de esos registros")
               + " (ver 'problemas'): el componente de inundación usa la susceptibilidad topográfica HAND alta, que no es amenaza oficial; poca "
               "población en clase alta no significa ausencia de amenaza (consultar la zonificación oficial del IDEAM, la CVC y el POT).")),
        "nina_2011": lim_2011,
        "trafico": "Tráfico: índice relativo de proximidad a vías ponderadas por categoría OSM; no es concentración de NO₂ ni aforo.",
        "zaragoza": (f"Zaragoza es la huella construida de WorldCover ({es(est['zaragoza']['area_poligono_km2'], 2) if 'zaragoza' in est else 's. d.'} km²) y las "
                     "comunas son polígonos administrativos con suelo no construido (la Comuna 7 incluye el aeródromo): las densidades y los promedios "
                     "por área no son del todo comparables entre ambos tipos de zona."),
        "poblacion": "Población: proyección DANE 2026 repartida con el censo 2018 por manzana; las urbanizaciones habitadas después de 2018 no aparecen.",
        "tendencia_lst": ("Tendencias de LST por zona: el tramo 2000–2025 sin armonizar está dominado por el salto de 2012–2013 y no debe usarse para "
                          "decidir. En 2024–2025 cambió el dato atmosférico auxiliar del producto ST del USGS (GEOS-IT). Tramo 2013–2025 (mediana): "
                          + (f"pendiente significativa solo en {', '.join(nombres_z[i] for i in lst_sig_z)}" if lst_sig_z else
                             "ninguna pendiente por zona es significativa")
                          + "; ver 'tendencia_lst_significativa' y 'tendencia_lst_ic95' en cada zona."),
        "tendencia_ndvi": ("Tendencias de NDVI Landsat por zona: la magnitud depende del estadístico (la mediana de una zona bimodal exagera la caída; ver "
                           "'tendencia_ndvi_landsat_variantes_2013_2025' y la advertencia de datos/series/landsat.json). Que la caída sea casi uniforme en los núcleos "
                           "construidos mientras el campo no cambia no está explicado (podría ser pérdida real de vegetación residual o un artefacto no identificado) y no "
                           "se ha contrastado con una fuente independiente (Sentinel-2 desde 2017 o fotointerpretación): no usar para decidir sin ese contraste."),
    }
    ORDEN_LIM = ["lst", "umbral_calor", "arbolado", "ndvi", "osm", "hand_ideam", "registros_ideam", "nina_2011", "trafico", "zaragoza",
                 "poblacion", "tendencia_lst", "tendencia_ndvi"]
    unidades = {
        "area_km2": "km² (suma de áreas de celda)", "area_poligono_km2": "km² (polígono en UTM 18N)", "poblacion": "hab (2026)",
        "densidad_hab_km2": "hab/km² de la zona", "densidad_sobre_area_construida_hab_km2": "hab por km² de superficie clasificada como construida",
        "lst_*": f"°C (temperatura de SUPERFICIE, {HORA} hora local, días despejados 2022–2025)", "lst_anomalia": "°C (media de la zona − media de la cabecera)",
        "pct_*": "%", "ndvi_*": "adimensional (−1 a 1)", "arbolado_pct, construido_pct, agua_pct": "% del área (WorldCover 2021)",
        "m2_*_por_hab": "m²/hab", "trafico_*": "índice relativo 0–100", "poblacion_*": "hab", "tendencia_lst_c_decada": "°C/década",
        "sufijo _pob": "ponderado por población (promedio de las celdas pesado por sus habitantes)",
        "ideam_nina_observada.poblacion_por_periodo": ("hab de 2026 que viven hoy dentro de la mancha de cada evento La Niña; NO son las personas "
                                                       "afectadas en ese evento (la ciudad de 1988 o de 2011 era distinta)"),
        "distancia_mediana_*_km": "km, mediana de la distancia en línea recta (UTM 18N) de los centros de celda al eje OSM del río",
    }
    indicadores = {
        "titulo": "Indicadores ambientales y de exposición por zona de Cartago",
        "descripcion": ("Cifras por comuna, Zaragoza y la cabecera sobre calor de superficie, vegetación, acceso a verde, "
                        "inundación, tráfico y equipamientos, calculadas con datos abiertos reales. Se presentan por área "
                        "(cómo es el territorio) y ponderadas por población (a qué está expuesta la gente)."),
        "unidades": unidades,
        "periodo": {"poblacion": "proyección DANE 2026 repartida con el CNPV 2018", "lst": f"Landsat 8/9, 2022–2025 ({n_esc} escenas, {HORA} hora local)",
                    "ndvi": "Sentinel-2, 2024–2025", "coberturas": "ESA WorldCover 2021", "osm": f"instantánea {ts_osm or 's. d.'} (fuentes/osm-vias.json)",
                    "serie": "Landsat 2000–2025 (solo años confiables)"},
        "definiciones": {
            "cabecera": "Unión de las 8 zonas: Comunas 1–7 (OpenStreetMap) y Zaragoza (huella WorldCover 2021, zona de trabajo, no límite oficial).",
            "calor_extremo": f"Celdas con LST ≥ percentil {P_CALOR} de las celdas de la cabecera (umbral {es(umbral, 2)} °C). Es un umbral relativo de la ciudad, no sanitario.",
            "umbral_calor_extremo_c": r(umbral, 2),
            "sin_verde_300m": "Población en celdas a más de 300 m (línea recta) del borde del verde público OSM de ≥ 0,5 ha (capa distancia_verde, criterio OMS 2016).",
            "susceptibilidad": "Clases de la capa susceptibilidad_inundacion (HAND): 3 alta, 2 media. Es susceptibilidad topográfica, no la amenaza oficial.",
            "ideam_nina_observada": ("Población de 2026 y área dentro de la unión de las áreas afectadas por inundación que el IDEAM registró en los "
                                     "eventos La Niña 1988, 2000, 2011, 2012, 2016 y 2020–2022 (escala no declarada; versiones v1 y v2 de un mismo año "
                                     "unidas). Es un registro histórico de áreas afectadas, no una zonificación de amenaza, y la población es la actual, "
                                     "no la afectada en cada evento. Rasterizado por centro de celda; "
                                     f"'sensibilidad_borde_55m' reduce o amplía la mancha {BORDE_CELDAS} celdas (≈ 55 m) porque los bordes son gruesos. "
                                     f"'poblacion_solo_en_la_mancha_{PERIODO_SIN}': hab dentro de la mancha de {PERIODO_SIN} y fuera de las demás y de la "
                                     "amenaza ALTA TR 50."),
            "ideam_evidencia_oficial": ("Unión de la amenaza ALTA por creciente súbita TR 50 años del IDEAM (corrientes de la cuenca directa del río La Vieja, "
                                        "según sus atributos) y de las áreas afectadas por La Niña (IDEAM): componente de inundación por defecto de "
                                        "prioridades.json. Se copia en el primer nivel de cada zona como poblacion_evidencia_inundacion_ideam y "
                                        f"pct_poblacion_evidencia_inundacion_ideam. '{sin_}' (y los campos *_sin_{PERIODO_SIN}): la misma unión sin "
                                        f"las capas La Niña {PERIODO_SIN} (8 y 22), cuya parte urbana {coh_sin}."),
            "coherencia_topografica_nina": ("Por periodo La Niña, HAND dentro de la mancha frente a fuera de toda mancha, en la ciudad y en el campo "
                                            "(ver coherencia_topografica_nina.metodo)."),
            "trafico_alto": f"Índice de tráfico ≥ {es(TRAFICO_ALTO, 0)} (definición de la tarea). Documentación: ver 'documentacion_umbral_trafico'.",
            "tendencia_lst_c_decada": "Pendiente de Sen de la mediana anual de LST de la zona, tramo 2013–2025 (Landsat 8/9), solo años confiables; ver tendencia_lst para los demás tramos.",
            "equipamientos_expuestos": ("Puntos OSM (centroide) en celda con calor extremo, con clase de susceptibilidad alta, a más de 300 m de verde ≥ 0,5 ha "
                                        "(distancia vectorial del producto verdes), con tráfico ≥ 60, en la mancha de amenaza alta del IDEAM o en un área "
                                        f"afectada por La Niña según el IDEAM. 'calor_extremo_en_umbral': en calor extremo pero a menos de {es(MARGEN_UMBRAL_C, 1)} °C del umbral."),
        },
        "inundacion_hand_frente_a_ideam": hand_vs_ideam,
        "coherencia_topografica_nina": coherencia,
        "creciente_subita_tr50_poligonos_alta": {"poligonos": tr50_alta, "lectura": (txt_tr50[0].upper() + txt_tr50[1:] + ".") if txt_tr50 else None,
                                                 "nota": "Distancias al eje OSM del La Vieja (comun.lineas_rio) en UTM 18N; atributos copiados del IDEAM."},
        "registros_ideam_usados": {"creciente_subita_tr50": "capa 0" if ideam is not None else None,
                                   "nina": None if nina is None else {"capas": nina["capas_usadas"], "capas_vacias": nina["capas_vacias"],
                                                                      "capas_faltantes": nina["capas_faltantes"]},
                                   "licencia": LICENCIA_IDEAM},
        "ndvi_sentinel2_cabecera_por_anio": {"valores": ndvi_s2_anual,
                                             "fuente": "datos/series/sentinel2.json → serie (ndvi_mediana_cabecera por adquisición; cabecera según el producto sentinel2)",
                                             "nota": "Mediana de las medianas por fecha de cada año; las fechas no se reparten igual entre meses, así que es indicativo."},
        "cabecera": cab_out,
        "zonas": zonas_out,
        "referencia_espacio_publico": ref_verde,
        "coherencia_poblacion": coh,
        "documentacion_umbral_trafico": doc_trafico,
        "verificacion": {"puntos_control": puntos, "rio_la_vieja": verif_rio, "latitud_media_zonas": ns, "norte_sur_ok": bool(ns_ok)},
        "procesamiento": [
            "Zonas rasterizadas con comun.mascara_zonas() (centro de celda); medias por área con el área real de cada celda (comun.area_celda_m2()).",
            "Ponderación por población con la capa poblacion (hab/celda, 2026).",
            f"Calor extremo: LST ≥ p{P_CALOR} de la cabecera = {es(umbral, 2)} °C.",
            "Verde público por habitante: intersección en UTM 18N de los polígonos públicos de espacio_verde.geojson con cada zona.",
            "Arbolado por habitante: Σ(fracción arbolada × área de celda) / población.",
            "Inundación: clases de susceptibilidad_inundacion (HAND) por un lado; por otro, registros del IDEAM rasterizados por centro de celda: amenaza por "
            "creciente súbita TR 50 años y unión de las áreas afectadas por La Niña (con la mancha reducida y ampliada ≈ 55 m como sensibilidad)."
            + ("" if ev_ok else " En esta ejecución faltan registros del IDEAM (ver 'problemas')."),
            ("Coherencia topográfica de las manchas La Niña: por periodo, HAND dentro de la mancha frente a las celdas del mismo ámbito fuera de toda "
             "mancha (cabecera y fuera de ella; todas las celdas y celdas abiertas), con la probabilidad de superioridad de Mann-Whitney; la evidencia "
             f"oficial se recalcula sin La Niña {PERIODO_SIN} como variante."
             + ("" if coherencia else " No se calculó en esta ejecución: faltan las capas La Niña del IDEAM (ver 'problemas').")),
            "Distancias a los ríos: centros de celda al eje OSM del La Vieja y del Cauca (comun.lineas_rio) en UTM 18N.",
            "Equipamientos: punto en polígono de zona; exposición con la celda del punto y la distancia vectorial a verde del producto verdes.",
            "Tendencia: medianas anuales de las rejillas Landsat por zona (valor de zona-año solo si ≥ 50 % de sus celdas tiene dato), pendiente de Sen (scipy.stats.theilslopes, IC 95 %) y Mann-Kendall (τ de Kendall) por tramo; solo años confiables de datos/series/landsat.json.",
        ],
        "limitaciones": [L[k] for k in ORDEN_LIM if L.get(k)],
        "fuentes": fuentes,
        "referencias": referencias,
        "script": "scripts/indicadores.py",
        "fecha_proceso": date.today().isoformat(),
    }
    # definiciones de bloques que no existen en esta ejecución (insumos del IDEAM ausentes) no se publican
    for k_, presente in (("ideam_evidencia_oficial", ev_ok), ("ideam_nina_observada", nina is not None),
                         ("coherencia_topografica_nina", bool(coherencia))):
        if not presente:
            indicadores["definiciones"].pop(k_, None)
    guardar(os.path.join(comun.DATOS, "indicadores.json"), indicadores)
    log("Escrito datos/indicadores.json")

    # =====================================================================================
    # SALIDA 1b: zonas.geojson
    from shapely.geometry import mapping
    from shapely import set_precision
    claves_flat = ["area_km2", "poblacion", "densidad_hab_km2", "lst_media", "lst_p90", "lst_anomalia", "lst_media_pob",
                   "pct_area_calor_extremo", "poblacion_calor_extremo", "pct_poblacion_calor_extremo", "ndvi_medio", "arbolado_pct",
                   "construido_pct", "m2_arbolado_por_hab", "m2_verde_publico_por_hab", "pct_poblacion_sin_verde_300m",
                   "poblacion_susceptibilidad_alta", "poblacion_susceptibilidad_media", "pct_area_susceptibilidad_alta",
                   "pct_poblacion_susceptibilidad_media", "trafico_medio", "trafico_medio_pob", "poblacion_trafico_alto", "pct_poblacion_trafico_alto",
                   "tendencia_lst_c_decada", "tendencia_lst_significativa", "tendencia_lst_ic95",
                   "poblacion_evidencia_inundacion_ideam", "pct_poblacion_evidencia_inundacion_ideam",
                   f"poblacion_evidencia_inundacion_ideam_sin_{PERIODO_SIN}", f"pct_poblacion_evidencia_inundacion_ideam_sin_{PERIODO_SIN}"]
    feats_z = []
    for z in zonas:
        d = est[z["id"]]
        prop = {"id": z["id"], "nombre": z["nombre"], "fuente_geometria": z["fuente"]}
        prop.update({k: d.get(k) for k in claves_flat})
        if "contraste_ideam_creciente_subita_tr50" in d:
            prop["poblacion_amenaza_alta_ideam"] = d["contraste_ideam_creciente_subita_tr50"]["poblacion_amenaza_alta"]
        if "ideam_nina_observada" in d:
            prop["poblacion_area_afectada_nina_ideam"] = d["ideam_nina_observada"]["poblacion"]
            prop["pct_poblacion_area_afectada_nina_ideam"] = d["ideam_nina_observada"]["pct_poblacion"]
        if "ideam_evidencia_oficial" in d:
            prop["pct_poblacion_evidencia_inundacion_ideam"] = d["ideam_evidencia_oficial"]["pct_poblacion"]
        if "equipamientos" in d:
            prop["equipamientos_total"] = d["equipamientos"]["por_categoria"]["total"]
        feats_z.append({"type": "Feature", "geometry": mapping(set_precision(z["geom"], 1e-6)), "properties": prop})
    gz = {"type": "FeatureCollection", "name": "zonas",
          "metadatos": {"titulo": "Zonas de análisis de Cartago con sus indicadores",
                        "descripcion": "Comunas 1–7 (OpenStreetMap) y Zaragoza (huella ESA WorldCover 2021) con los indicadores principales; el detalle está en datos/indicadores.json.",
                        "crs": "EPSG:4326", "umbral_calor_extremo_c": r(umbral, 2),
                        "campos": {
                            "poblacion_evidencia_inundacion_ideam, pct_poblacion_evidencia_inundacion_ideam": (
                                "hab y % de la zona con registro oficial del IDEAM (amenaza ALTA TR 50 ∪ La Niña 1988–2022); componente de inundación por defecto"
                                if ev_ok else "null en esta ejecución: faltan registros del IDEAM (ver datos/indicadores.json → problemas)"),
                            f"*_sin_{PERIODO_SIN}": (f"lo mismo sin las capas La Niña {PERIODO_SIN}, cuya parte urbana {coh_sin}" if ev_ok else
                                                     "null en esta ejecución: faltan registros del IDEAM"),
                            "pct_poblacion_susceptibilidad_media": "% de la población en la clase media de susceptibilidad topográfica (HAND); no es amenaza oficial",
                            "tendencia_lst_c_decada": "°C/década, Sen 2013–2025 de la mediana anual de LST (Landsat 8/9)",
                            "tendencia_lst_significativa": "true si Mann-Kendall p < 0,05 y el IC 95 % de Sen excluye 0",
                            "tendencia_lst_ic95": "IC 95 % de la pendiente de Sen (°C/década)",
                        },
                        "fuente": {"nombre": "Geometría: OpenStreetMap (comunas) y ESA WorldCover 2021 (Zaragoza). Atributos: DANE y Meta/CIESIN HRSL (población), "
                                             "USGS Landsat (LST), Copernicus Sentinel-2 (NDVI), ESA WorldCover (coberturas), Copernicus DEM GLO-30 (susceptibilidad "
                                             "HAND), OpenStreetMap (verde, tráfico, equipamientos) e IDEAM (registros de inundación); indicadores de BioMap Cartago",
                                   "licencia": ("Geometría: ODbL 1.0 (OSM) y CC BY 4.0 (WorldCover). Atributos: DANE (uso citando la fuente), HRSL CC BY 4.0, "
                                                "USGS dominio público, Copernicus Sentinel acceso libre y abierto, Copernicus WorldDEM-30 (libre con atribución y "
                                                "exención), ODbL 1.0 (OSM). IDEAM: " + LICENCIA_IDEAM),
                                   "cita": list(dict.fromkeys(f["cita"] for f in fuentes if f.get("cita")))},
                        "limitaciones": [L[k] for k in ("lst", "umbral_calor", "arbolado", "hand_ideam", "registros_ideam", "nina_2011",
                                                                  "trafico", "zaragoza", "poblacion", "tendencia_lst") if L.get(k)],
                        "fecha_proceso": date.today().isoformat()},
          "features": feats_z}
    guardar(os.path.join(VECT, "zonas.geojson"), gz)
    log("Escrito datos/vectores/zonas.geojson")

    # =====================================================================================
    # SALIDA 2: equipamientos_exposicion.geojson
    if feats is not None:
        ge = {"type": "FeatureCollection", "name": "equipamientos_exposicion",
              "metadatos": {
                  "titulo": "Exposición ambiental de los equipamientos mapeados en OpenStreetMap",
                  "descripcion": ("Para cada colegio, centro de salud, hogar de cuidado, estación de bomberos o policía y alcaldía mapeado en OSM: "
                                  "temperatura de superficie de su celda, verdor y arbolado en 100 m, susceptibilidad a inundación, distancia a "
                                  "verde público y exposición al tráfico."),
                  "crs": "EPSG:4326",
                  "campos": {
                      "lst_c": "°C, LST 2022–2025 de la celda (≈ 28 m; resolución térmica nativa 100 m)",
                      "calor_extremo": f"LST ≥ {es(umbral, 2)} °C (p{P_CALOR} de la cabecera)",
                      "ndvi_100m": "NDVI Sentinel-2 2024–2025, media de las celdas con centro a ≤ 100 m",
                      "arbolado_100m_pct": "% de área arbolada (WorldCover 2021) en las celdas con centro a ≤ 100 m",
                      "susceptibilidad_inundacion_clase": "0–3 de la capa susceptibilidad_inundacion (HAND)",
                      "amenaza_ideam_creciente_subita_tr50": "clase de la mancha de amenaza por creciente súbita TR 50 años del IDEAM en el punto (registro oficial; solo corrientes de la cuenca directa del río La Vieja)",
                      "area_afectada_nina_ideam": "el punto cae en un área afectada por inundación en algún evento La Niña registrado por el IDEAM (escala no declarada; bordes gruesos)",
                      "susceptibilidad_inundacion": "etiqueta corta de la clase HAND (etiqueta_corta de datos/capas/susceptibilidad_inundacion.json); las clases baja y HAND > 15 m no descartan amenaza",
                      "susceptibilidad_inundacion_detalle": "etiqueta completa de la clase HAND",
                      "periodos_nina_ideam": "eventos La Niña (IDEAM) en que el punto quedó dentro del área afectada",
                      "lst_margen_umbral_c": "°C, LST de la celda − umbral de calor extremo",
                      "en_umbral_calor": f"|lst_margen_umbral_c| < {es(MARGEN_UMBRAL_C, 1)} °C (supuesto): la clasificación en calor extremo es frágil",
                      "nombre_mostrar": "nombre OSM o, si falta, el tipo seguido de «sin nombre en OSM»",
                      "dist_verde_publico_05ha_m": "m, distancia en línea recta al borde del verde público ≥ 0,5 ha (vector del producto verdes)",
                      "trafico_indice": "índice relativo 0–100 de la celda",
                      "trafico_alto": f"índice ≥ {es(TRAFICO_ALTO, 0)}",
                  },
                  "fuente": {"nombre": ("OpenStreetMap (equipamientos, verde, vías) + capas BioMap: USGS Landsat (LST), Copernicus Sentinel-2 (NDVI), "
                                        "ESA WorldCover 2021 (arbolado, construido), Copernicus DEM GLO-30 (susceptibilidad HAND) e IDEAM (registros de inundación)"),
                             "licencia": ("ODbL 1.0 para la geometría y atributos OSM; USGS dominio público; Copernicus Sentinel acceso libre y abierto; "
                                          "WorldCover CC BY 4.0; Copernicus WorldDEM-30 libre con atribución y exención de responsabilidad. IDEAM: " + LICENCIA_IDEAM),
                             "cita": ["© colaboradores de OpenStreetMap, ODbL 1.0",
                                      meta["lst"]["fuente"].get("cita"), meta["ndvi"]["fuente"].get("cita"),
                                      "© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium",
                                      meta["susceptibilidad_inundacion"]["fuente"].get("cita"), CITA_IDEAM]},
                  "limitaciones": [
                      "Inventario incompleto: OSM tiene ≈ 26 % de las sedes educativas del MEN y ≈ 11 % de las sedes de IPS del REPS (producto verdes).",
                      "Un punto por equipamiento (centroide): no representa linderos ni la población atendida.",
                      "La LST de una celda de 28 m hereda la resolución térmica de 100 m: es el ambiente de superficie del entorno, no el techo del edificio.",
                      "Las clases de susceptibilidad baja y HAND > 15 m no descartan amenaza por inundación (ver limitaciones de susceptibilidad_inundacion); las áreas afectadas por La Niña del IDEAM son de escala no declarada (bordes gruesos) y la creciente súbita TR 50 solo cubre las corrientes de la cuenca directa del río La Vieja.",
                  ] + ([f"La parte urbana de la mancha La Niña {PERIODO_SIN} {coh_sin} (ver indicadores.json → coherencia_topografica_nina)"
                        + (f": un equipamiento que solo cae en ella ('periodos_nina_ideam' = ['{PERIODO_SIN}']) debe contrastarse con registros municipales o de la UNGRD."
                           if sobreestima_sin else ".")] if nina is not None else []) + [
                      f"Un equipamiento a menos de {es(MARGEN_UMBRAL_C, 1)} °C del umbral de calor extremo ('en_umbral_calor') puede cambiar de grupo con otra escena o resolución: la LST tiene incertidumbre de medición y la del PNG publicado se redondea a 0,01 °C.",
                      "Incluye equipamientos fuera de Cartago (Puerto Caldas, Pereira) con zona = null.",
                      "Dos etiquetas dudosas de OSM se marcan en 'etiquetado_dudoso'; no se reclasifican aquí.",
                  ],
                  "fecha_proceso": date.today().isoformat()},
              "features": feats}
        guardar(os.path.join(VECT, "equipamientos_exposicion.geojson"), ge)
        log(f"Escrito datos/vectores/equipamientos_exposicion.geojson ({len(feats)} equipamientos)")

    # =====================================================================================
    # SALIDA 3: series/zonas.json
    series = {
        "titulo": "Serie anual Landsat por zona: temperatura de superficie y NDVI (2000–2025)",
        "descripcion": ("Mediana anual por zona de la temperatura de superficie (LST) y del NDVI de Landsat, con la marca de confiabilidad "
                        "de cada año y la diferencia con el campo a la misma altitud. Las cifras de distintos sensores no son directamente comparables."),
        "unidades": {"lst": "°C", "ndvi": "adimensional", "isla": "°C (zona − referencia rural)", "pct_celdas_*": "%", "sen_por_decada": "°C/década o NDVI/década"},
        "fuente": {"nombre": "Rejillas anuales del producto landsat (fuentes/rejilla/lst_<año>.npy, ndvi_<año>.npy), USGS Landsat C2 L2 vía Planetary Computer",
                   "url": "https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2", "licencia": "Dominio público USGS",
                   "cita": "Landsat Collection 2 Level-2 Science Products courtesy of the U.S. Geological Survey"},
        "metodo": {
            "valor_zona_anio": "Mediana de las celdas de la zona con dato; nulo si menos del 50 % de las celdas de la zona tiene dato ese año (supuesto).",
            "referencia_rural": "landsat.mascaras()['rural']: fuera de la cabecera, a más de 500 m, sin agua, construido < 10 % y altitud ± 30 m de la mediana de la cabecera (definición del producto landsat).",
            "confiable": landsat_json.get("metodo", {}).get("confiable"),
            "tendencias": "Pendiente de Sen con IC 95 % (scipy.stats.theilslopes) y Mann-Kendall (τ de Kendall, scipy.stats.kendalltau); significativa si p < 0,05 y el IC de Sen excluye 0. Solo años confiables.",
            "tramos": {k: v[2] for k, v in TRAMOS.items()},
            "variantes": VARIANTES_SERIE,
            "robustez": ("'tendencias_variantes' compara mediana, media y núcleo construido en los tramos de un solo tipo de sensor: robusta = las tres "
                         "variantes significativas con el mismo signo, o ninguna significativa; si solo algunas lo son, el resultado depende del método."),
        },
        "anios": S["anios"],
        "metadatos_anio": S["filas"],
        "rural_referencia": {"lst": S["rural_lst"], "ndvi": S["rural_ndvi"], "tendencias": S["tendencias_rural"],
                             "nota": "Control: si la zona y el campo cambian igual, el cambio no es urbano (clima, hora de paso, sensor o procesamiento)."},
        "zonas": [{"id": i, "nombre": nombres_z[i], **S["por_zona"][i], "celdas_nucleo_construido": S["celdas_nucleo"][i],
                   "tendencias": S["tendencias"][i], "tendencias_variantes": S["tendencias_variantes"][i],
                   "lectura": lectura_tendencia(S["tendencias"][i], S["tendencias_variantes"][i])} for i in ids + ["cabecera"]],
        "advertencias": [
            "Cambio de sensor en 2013 (Landsat 5/7 → 8/9): los niveles antes y después no son comparables sin armonizar; el salto de 2012–2013 de la isla de calor no está explicado (ver datos/series/landsat.json).",
            "Con 3 a 6 escenas por año, la mediana anual depende de los meses que quedaron despejados y de la hora de paso: la variación entre años no es solo climática.",
            "Desde el 1-ene-2024 el producto ST del USGS usa GEOS-IT como dato atmosférico auxiliar (antes GEOS FP-IT): 2024–2025 pueden no ser homogéneos con los años anteriores; se publica la sensibilidad 2013–2023.",
            "Las zonas son fijas en el tiempo (polígonos actuales): mezclan expansión urbana con cambios dentro del área ya construida.",
            "El NDVI de esta serie es Landsat (no Sentinel-2) y cambia de sensor en 2013 (Roy et al. 2016).",
            "Las zonas son heterogéneas (mezclan núcleo construido y suelo verde): su mediana espacial puede caer entre los dos modos y exagerar los cambios; por eso se publican la media y el núcleo construido (tendencias_variantes).",
            "La caída del NDVI Landsat en los núcleos construidos, con el campo sin cambio, no está explicada ni contrastada con una fuente independiente (Sentinel-2 desde 2017 o fotointerpretación): no usar para decidir sin ese contraste.",
            "2003 no es confiable (3 escenas en un trimestre) y queda fuera de las tendencias.",
        ],
        "fecha_proceso": date.today().isoformat(),
    }
    guardar(os.path.join(SERIES, "zonas.json"), series)
    log("Escrito datos/series/zonas.json")

    # =====================================================================================
    # SALIDA 4: calibracion.json
    bA = {n: bootL[:, j + 1] * 10 for j, n in enumerate(["arbolado_pct", "construido_pct", "agua_pct", "altitud_terreno_m"])}
    bNd = {n: bootN[:, j + 1] * 10 for j, n in enumerate(["arbolado_pct", "construido_pct"])}
    dif_lst = bA["arbolado_pct"] - bA["construido_pct"]
    dif_ndvi = bNd["arbolado_pct"] - bNd["construido_pct"]
    # superficies disponibles, piso de LST y techo de NDVI para el simulador
    vias_pct, superficie_osm = superficie_vial_por_zona(zonas_utm, tr)
    if vias_pct is None:
        problemas.append("Falta fuentes/osm-vias.json: no se estima la superficie vial por zona (topes de pavimento y techos sin separar).")
    rural_m = S.get("mascara_rural")
    lst_rural = float(np.nanmedian(C["lst"][rural_m])) if rural_m is not None else None
    arb80 = cab & (C["arbolado"] >= 80)
    lst_arb80 = float(np.nanmedian(C["lst"][arb80])) if arb80.any() else None
    ndvi_techo = float(np.nanmedian(C["ndvi"][arb80])) if arb80.any() else None
    # Piso de LST del simulador: la LST mediana del bosque urbano observado (celdas de la cabecera con ≥ 80 % de arbolado), que es
    # más alta que la referencia rural; una zona urbana arborizada al máximo no debería quedar más fría que ese bosque urbano.
    piso_lst = max([v for v in (lst_rural, lst_arb80) if v is not None], default=None)
    piso_criterio = ("lst_celdas_cabecera_arbolado_ge_80_c" if (lst_arb80 is not None and piso_lst == lst_arb80) else "lst_referencia_rural_c")
    cob_ref = {n: r(np.mean(C[n][cab]), 1) for n in ("cob_pasto", "cob_cultivo", "cob_suelo") if n in C}
    disp = {}
    for z in zonas:
        s = m == z["indice"]
        a, c, w = C["arbolado"][s].mean(), C["construido"][s].mean(), C["agua"][s].mean()
        lz, nz = float(np.nanmean(C["lst"][s])), float(np.nanmean(C["ndvi"][s]))
        v = None if vias_pct is None else min(vias_pct[z["id"]], c)
        disp[z["id"]] = {"arbolado_pct": r(a, 1), "construido_pct": r(c, 1), "agua_pct": r(w, 2),
                         "pasto_cultivo_suelo_y_otros_pct": r(100 - a - c - w, 1),
                         "max_pp_arbolado_sustituyendo_pasto": r(100 - a - c - w, 1), "max_pp_sobre_construido": r(c, 1),
                         "calzadas_osm_pct": r(vias_pct[z["id"]], 1) if vias_pct is not None else None,
                         "max_pp_pavimento_frio": r(v, 1) if v is not None else r(c, 1),
                         "max_pp_techos_verdes": r(max(c - v, 0.0), 1) if v is not None else r(c, 1),
                         "lst_observada_media_c": r(lz, 2), "ndvi_observado_medio": r(nz, 3),
                         "delta_lst_minimo_c": r(min(piso_lst - lz, 0.0), 2) if piso_lst is not None else None,
                         "delta_ndvi_maximo": r(max(ndvi_techo - nz, 0.0), 3) if ndvi_techo is not None else None}
    from scipy import stats as _st

    def pi_aprox(mu, lo, hi, i2, k):
        """Intervalo de predicción HTS (2009) con τ² aproximado = I²·k·SE² (supuesto de varianzas intraestudio iguales)."""
        se = (hi - lo) / (2 * 1.959964)
        tau2 = i2 * k * se ** 2
        h = _st.t.ppf(0.975, k - 2) * np.sqrt(tau2 + se ** 2)
        return {"intervalo_prediccion_95_elemento_c": [r(mu - h, 2), r(mu + h, 2)],
                "intervalo_prediccion_95_lst_por_10pp": [r((mu - h) / 10, 3), r((mu + h) / 10, 3)],
                "se_media_c": r(se, 3), "tau2_aproximado_c2": r(tau2, 2), "k_estudios": k, "i2": i2,
                "metodo": ("Aproximación propia, no publicada por Das et al.: SE de la media desde su IC 95 %, τ² ≈ I²·k·SE² (supone varianzas "
                           "intraestudio iguales) e intervalo de predicción de Higgins, Thompson y Spiegelhalter (2009): μ ± t(k−2)·√(τ² + SE²). "
                           "Indica el rango en que caería el efecto en un sitio nuevo parecido a los estudiados; es orientativo.")}
    pi_techo = pi_aprox(-10.88, -15.26, -6.50, 0.92, 17)
    pi_pav = pi_aprox(-5.45, -6.75, -4.15, 0.10, 8)
    # ¿hace falta el piso de LST? ΔLST de cada intervención en su tope de superficie y de la combinación máxima, frente a delta_lst_minimo_c
    ef_pp = {"arbolado_sustituye_pasto": coefL["arbolado_pct"]["valor"] / 10,
             "arbolado_sustituye_construido": (coefL["arbolado_pct"]["valor"] - coefL["construido_pct"]["valor"]) / 10,
             "techos_verdes": -10.88 / 100, "pavimento_frio": -5.45 / 100}
    tope_de = {"arbolado_sustituye_pasto": "max_pp_arbolado_sustituyendo_pasto", "arbolado_sustituye_construido": "max_pp_sobre_construido",
               "techos_verdes": "max_pp_techos_verdes", "pavimento_frio": "max_pp_pavimento_frio"}
    sobre_constr = sorted(("arbolado_sustituye_construido", "techos_verdes", "pavimento_frio"), key=lambda k: ef_pp[k])
    ver_topes = {}
    for z in zonas:
        dz = disp[z["id"]]
        piso_z = dz["delta_lst_minimo_c"]
        sola = {k: r(ef_pp[k] * dz[tope_de[k]], 2) for k in ef_pp}
        # combinación de mayor enfriamiento: arbolado sobre pasto al tope y reparto voraz de lo construido (restricción conjunta; óptimo
        # para un programa lineal con topes por intervención y una sola restricción conjunta)
        comb, resto, reparto = ef_pp["arbolado_sustituye_pasto"] * dz["max_pp_arbolado_sustituyendo_pasto"], dz["max_pp_sobre_construido"], {}
        for k in sobre_constr:
            x = min(dz[tope_de[k]], resto) if ef_pp[k] < 0 else 0.0
            reparto[k] = r(x, 1)
            comb += ef_pp[k] * x
            resto -= x
        ver_topes[z["id"]] = {
            "delta_lst_minimo_c": piso_z,
            "una_intervencion_en_su_tope_c": sola,
            "intervenciones_que_bajan_del_piso": [k for k, v in sola.items() if piso_z is not None and v < piso_z],
            "combinacion_maxima_c": r(comb, 2),
            "combinacion_maxima_pp": {"arbolado_sustituye_pasto": dz["max_pp_arbolado_sustituyendo_pasto"], **reparto},
            "combinacion_baja_del_piso": bool(piso_z is not None and comb < piso_z),
            "exceso_sobre_el_piso_c": r(min(comb - piso_z, 0.0), 2) if piso_z is not None else None,
        }
    n_sola = sum(1 for v in ver_topes.values() if v["intervenciones_que_bajan_del_piso"])
    n_comb = sum(1 for v in ver_topes.values() if v["combinacion_baja_del_piso"])
    z_peor = min(ver_topes, key=lambda i: ver_topes[i]["exceso_sobre_el_piso_c"] if ver_topes[i]["exceso_sobre_el_piso_c"] is not None else 0.0)
    calib = {
        "titulo": "Modelos empíricos locales para el simulador de intervenciones",
        "descripcion": ("Relaciones estadísticas medidas en la cabecera de Cartago entre la cobertura del suelo y la temperatura de "
                        "superficie o el verdor, y coeficientes de literatura para techos verdes y pavimentos. Sirven para estimar el "
                        "orden de magnitud del efecto de una intervención, no para predecirlo con exactitud."),
        "advertencia_principal": ("Asociación transversal, no causalidad: el coeficiente compara lugares distintos de la ciudad en 2021–2025, no el "
                                  "antes y después de una intervención. La temperatura de superficie no es la del aire."),
        "datos": {
            "respuesta_lst": f"Capa lst (Landsat 8/9, mediana 2022–2025, {n_esc} escenas, {HORA} hora local, °C)",
            "respuesta_ndvi": "Capa ndvi (Sentinel-2, mediana 2024–2025)",
            "covariables": "arbolado, construido y agua (% del área, ESA WorldCover 2021); altitud del terreno aproximada = percentil 10 del DSM Copernicus en una ventana de 19 celdas (≈ 525 m), para no confundir edificios y copas con terreno",
            "categoria_de_referencia": ("Lo que no es arbolado, construido ni agua: en la cabecera, "
                                        + ", ".join(f"{et} {es(cob_ref[n], 1)} %" for n, et in (("cob_pasto", "pasto"), ("cob_cultivo", "cultivo"), ("cob_suelo", "suelo desnudo")) if n in cob_ref)
                                        + " (medias por celda, WorldCover 2021). Cada coeficiente compara con esa categoría (sobre todo pasto)."),
            "ambito": "Celdas de la cabecera (unión de las 8 zonas)",
            "unidad_lst": f"Unidades de {AGREG}×{AGREG} celdas (≈ 111 m) con ≥ {int(FRAC_UNIDAD * 100)} % de celdas en la cabecera: la banda térmica TIRS se adquiere a 100 m y se remuestrea a 30 m (USGS), así que a nivel de celda el efecto del arbolado se atenúa (ver sensibilidad nivel_celda_27m).",
            "unidad_ndvi": "Celda de 0,00025° (≈ 28 m): el NDVI de Sentinel-2 (10 m) y WorldCover (10 m) tienen resolución comparable.",
        },
        "modelos": {
            "lst": {
                "formula": "LST = b0 + b1·arbolado_pct + b2·construido_pct + b3·agua_pct + b4·altitud_terreno_m",
                "n": mL["n"], "r2": r(mL["r2"], 3), "r2_ajustado": r(mL["r2_ajustado"], 3), "rmse_c": r(mL["rmse"], 3),
                "coeficientes": coefL,
                "bootstrap": {"replicas": N_BOOT, "semilla": SEMILLA, "bloques": nbL,
                              "metodo": "Remuestreo con reemplazo de bloques espaciales cuadrados de 18 celdas (≈ 500 m) y, como sensibilidad, de 36 celdas (≈ 1 km); IC percentil 2,5–97,5. El tamaño de bloque es un supuesto apoyado en el correlograma de residuos."},
                "diagnostico_residuos": diagL,
                "sensibilidad": sensL,
                "nota_agua": (f"En la cabecera casi no hay agua (media {es(np.mean(C['agua'][cab]), 2)} %; {diagL['unidades_con_agua_mayor_que_0']} de "
                              f"{mL['n']} unidades con agua > 0): su coeficiente no está identificado y no debe usarse."),
            },
            "ndvi": {
                "formula": "NDVI = g0 + g1·arbolado_pct + g2·construido_pct",
                "n": mN["n"], "r2": r(mN["r2"], 3), "r2_ajustado": r(mN["r2_ajustado"], 3), "rmse": r(mN["rmse"], 4),
                "coeficientes": coefN,
                "bootstrap": {"replicas": N_BOOT, "semilla": SEMILLA, "bloques": nbN, "metodo": "Igual que en LST, por celda."},
                "diagnostico_residuos": diagN,
                "sensibilidad": sensN,
                "tipo_de_relacion": "equivalencia_de_cobertura",
                "advertencia_circularidad": (
                    "Relación en parte circular: ESA WorldCover 2021 (arbolado, construido) es una clasificación hecha con compuestos anuales de "
                    "Sentinel-2 (reflectancias y percentiles 10, 50 y 90 del NDVI) y de radar Sentinel-1, y la respuesta es el NDVI del mismo sensor "
                    "(2024–2025). El R² y los coeficientes describen sobre todo qué "
                    "NDVI corresponde a cada cobertura de la clasificación, no un efecto medido de forma independiente. "
                    + (f"Con NDVI Landsat 8/9 {'–'.join(str(a_) for a_ in (sensN['ndvi_landsat_por_celda']['anios'][0], sensN['ndvi_landsat_por_celda']['anios'][-1]))} "
                       f"(otro sensor y otros años; 'ndvi_landsat_por_celda') los coeficientes conservan signo y orden de magnitud (arbolado "
                       f"{es(sensN['ndvi_landsat_por_celda']['arbolado_pct'], 4, True)} frente a {es(coefN['arbolado_pct']['valor'], 4, True)}; construido "
                       f"{es(sensN['ndvi_landsat_por_celda']['construido_pct'], 4, True)} frente a {es(coefN['construido_pct']['valor'], 4, True)} por 10 pp; R² "
                       f"{es(sensN['ndvi_landsat_por_celda']['r2'], 2)}): la relación no depende de las mismas imágenes, pero el coeficiente del arbolado es "
                       "menor con Landsat y la dependencia conceptual se mantiene, porque todo NDVI óptico se parece a la señal con la que se clasificó. "
                       if "ndvi_landsat_por_celda" in sensN else "")
                    + "No se dispone en el proyecto de una cobertura arbórea independiente (OSM no mapea copas) para validarlo. El ΔNDVI del simulador "
                      "es una equivalencia de cobertura, no un efecto medido."),
            },
        },
        "intervenciones": {
            "arbolado": {
                "descripcion": "+X puntos porcentuales de área arbolada en la zona (en la unidad de WorldCover: área clasificada como árboles).",
                "supuesto_por_defecto": "sustituye_pasto",
                "justificacion_supuesto": ("Por defecto el árbol se planta sobre pasto, suelo o lote (la categoría de referencia): es el efecto más "
                                           "conservador y no exige retirar pavimento. La variante 'sustituye_construido' (despavimentar y arborizar, "
                                           "o copa que cubre pavimento) da un efecto mayor. El simulador debe limitar X a lo disponible en la zona "
                                           "(ver disponibilidad_por_zona)."),
                "variantes": {
                    "sustituye_pasto": {
                        "origen": "local",
                        "delta_lst_c_por_10pp": coefL["arbolado_pct"]["valor"], "ic95_lst": coefL["arbolado_pct"]["ic95_bootstrap_bloques_500m"],
                        "delta_ndvi_por_10pp": coefN["arbolado_pct"]["valor"], "ic95_ndvi": coefN["arbolado_pct"]["ic95_bootstrap_bloques_500m"],
                        "formula": "ΔLST = (X/10)·b1 ; ΔNDVI = (X/10)·g1",
                        "limite_x": "X ≤ max_pp_arbolado_sustituyendo_pasto de la zona (pasto, cultivo, suelo y otros)",
                        "interpretacion_ndvi": "equivalencia de cobertura (ver modelos.ndvi.advertencia_circularidad), no efecto medido",
                    },
                    "sustituye_construido": {
                        "origen": "local",
                        "delta_lst_c_por_10pp": r(coefL["arbolado_pct"]["valor"] - coefL["construido_pct"]["valor"], 4),
                        "ic95_lst": ic_boot(dif_lst),
                        "delta_ndvi_por_10pp": r(coefN["arbolado_pct"]["valor"] - coefN["construido_pct"]["valor"], 4),
                        "ic95_ndvi": ic_boot(dif_ndvi),
                        "formula": "ΔLST = (X/10)·(b1 − b2) ; ΔNDVI = (X/10)·(g1 − g2)",
                        "limite_x": "X ≤ max_pp_sobre_construido de la zona y, junto con techos verdes y pavimento frío, dentro de la restricción conjunta (regla_combinacion)",
                        "interpretacion_ndvi": "equivalencia de cobertura (ver modelos.ndvi.advertencia_circularidad), no efecto medido",
                    },
                },
            },
            "techos_verdes": {
                "descripcion": "X puntos porcentuales del área de la zona pasan de techo convencional a techo verde.",
                "origen": "literatura",
                "delta_temperatura_superficie_elemento_c": -10.88, "ic95_elemento_c": [-15.26, -6.50],
                "delta_lst_c_por_10pp": r(-10.88 / 10, 3), "ic95_lst_por_10pp": [r(-15.26 / 10, 3), r(-6.50 / 10, 3)],
                "formula": "ΔLST_zona ≈ (X/100)·ΔT_elemento (mezcla lineal por área; supuesto)",
                "limite_x": ("X ≤ max_pp_techos_verdes de la zona = construido − calzadas OSM (cota superior: incluye patios, parqueaderos y andenes, y no "
                             "considera la capacidad estructural ni la pendiente de los techos; supuesto), y dentro de la restricción conjunta (regla_combinacion)"),
                "heterogeneidad": pi_techo,
                "advertencia_ic": ("El IC 95 % de la media (−15,26 a −6,50 °C) no recoge la heterogeneidad entre estudios (I² 92 %): el efecto en un sitio "
                                   "concreto puede quedar muy lejos de la media. Ver 'heterogeneidad' (intervalo de predicción aproximado)."),
                "cita": ("Das, J. K., Kumari, B., Rahman, A. R., et al. (2025). Evaluation of community-based heat adaptation interventions: "
                         "a systematic review. BMJ Public Health 3(2): e002332. doi:10.1136/bmjph-2024-002332. Metaanálisis: «green roofs "
                         "significantly decrease the surface temperature by 10.88°C compared with bare concrete roofs (95% CI: −15.26°C to –6.50°C; 17 studies)», I² = 92 %."),
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12273142/",
                "cota_superior_contexto": "US EPA: la superficie de un techo verde «can be 56°F lower» (≈ 31 °C) que la de un techo convencional (https://www.epa.gov/heatislands/using-green-roofs-reduce-heat-islands).",
                "contraste_local": {
                    "analogia": "Sustituir construido por pasto en el modelo local: −b2 por 10 pp",
                    "delta_lst_c_por_10pp": r(-coefL["construido_pct"]["valor"], 4),
                    "ic95": [r(-coefL["construido_pct"]["ic95_bootstrap_bloques_500m"][1], 4), r(-coefL["construido_pct"]["ic95_bootstrap_bloques_500m"][0], 4)],
                },
                "delta_ndvi": {"origen": "analogia_local", "delta_ndvi_por_10pp": r(-coefN["construido_pct"]["valor"], 4),
                               "nota": "Supuesto: un techo verde se ve desde el satélite como cobertura herbácea; −g2 por 10 pp. No hay medición local."},
                "advertencias": [
                    "Efecto sobre la temperatura del ELEMENTO (techo) en medias diarias, con heterogeneidad muy alta entre estudios (I² 92 %) y comparado con concreto desnudo; los techos de Cartago (fibrocemento, teja de barro, lámina) pueden diferir.",
                    f"La LST del simulador es a las {HORA} hora local; la diferencia a esa hora puede ser distinta de la media diaria.",
                    "El valor de literatura por 10 pp es mayor que la analogía local (construido → pasto); la diferencia indica la incertidumbre de trasladar resultados de techo a la escala de 100 m.",
                ],
            },
            "pavimento_frio": {
                "descripcion": "X puntos porcentuales del área de la zona pasan de asfalto convencional a pavimento modificado (reflectivo o de otros materiales).",
                "origen": "literatura",
                "delta_temperatura_superficie_elemento_c": {"frente_a_asfalto": -5.45, "frente_a_concreto": -1.14},
                "ic95_elemento_c": {"frente_a_asfalto": [-6.75, -4.15], "frente_a_concreto": [-2.91, 0.63]},
                "delta_lst_c_por_10pp": r(-5.45 / 10, 3), "ic95_lst_por_10pp": [r(-6.75 / 10, 3), r(-4.15 / 10, 3)],
                "formula": "ΔLST_zona ≈ (X/100)·ΔT_elemento (mezcla lineal por área; supuesto). Solo para superficies de asfalto; sobre concreto el efecto no es significativo.",
                "limite_x": ("X ≤ max_pp_pavimento_frio de la zona = calzadas OSM con ancho supuesto (ver superficie_vial), y dentro de la restricción "
                             "conjunta (regla_combinacion). La fracción de asfalto es desconocida: en OSM la superficie solo está etiquetada en una parte de la red (ver superficie_vial)."),
                "heterogeneidad": pi_pav,
                "cita": ("Das et al. (2025), BMJ Public Health 3(2): e002332, doi:10.1136/bmjph-2024-002332: «Modified pavements significantly decrease "
                         "the surface temperature by 5.45°C when compared with conventional asphalt (95% CI: −6.75 to –4.15; 8 studies)», I² = 10 %; frente a "
                         "concreto: −1,14 °C (IC −2,91 a 0,63; 9 estudios), no significativo."),
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12273142/",
                "delta_ndvi": {"origen": "supuesto", "delta_ndvi_por_10pp": 0.0, "nota": "Un pavimento no cambia la vegetación."},
            },
            "pavimento_permeable": {
                "descripcion": "Pavimento poroso, permeable o retenedor de agua.",
                "origen": "literatura",
                "delta_temperatura_superficie_elemento_c": 1.74, "ic95_elemento_c": [0.81, 2.68],
                "delta_lst_c_por_10pp": r(1.74 / 10, 3), "ic95_lst_por_10pp": [r(0.81 / 10, 3), r(2.68 / 10, 3)],
                "cita": ("Das et al. (2025), subgrupo frente a concreto convencional: «porous, water-retaining, and permeable concrete, pavers, and "
                         "interlocking porous blocks (MD: 1.74°C; 95% CI: 0.81°C to 2.68°C; 4 studies)»: en promedio estuvieron MÁS calientes."),
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12273142/",
                "recomendacion_simulador": "No presentarlo como medida de enfriamiento. Este producto no evalúa su efecto sobre la escorrentía.",
                "delta_ndvi": {"origen": "supuesto", "delta_ndvi_por_10pp": 0.0},
            },
        },
        "efecto_no2_trafico": {
            "cuantificable": False,
            "texto": ("No hay base local ni de literatura verificada para cuantificar el efecto de estas intervenciones sobre el NO₂ o el índice de tráfico "
                      "en Cartago: el proyecto no tiene mediciones de NO₂ por calle y el índice de tráfico depende solo de la red vial. El simulador debe "
                      "mostrarlo de forma cualitativa."),
            "cualitativo": ("Revisión de Abhijith et al. (2017): en cañones urbanos, las copas altas de árboles empeoraron la calidad del aire y los setos "
                            "bajos la mejoraron; techos y muros verdes pueden ayudar a reducir contaminantes. Plantar árboles en calles estrechas y "
                            "cerradas no debe presentarse como medida contra el NO₂."),
            "cita": ("Abhijith, K. V., Kumar, P., Gallagher, J., McNabola, A., Baldauf, R., Pilla, F., Broderick, B., Di Sabatino, S., Pulvirenti, B. (2017). "
                     "Air pollution abatement performances of green infrastructure in open road and built-up street canyon environments – A review. "
                     "Atmospheric Environment 162: 71–86. doi:10.1016/j.atmosenv.2017.05.014"),
            "pavimentos": "Ni el pavimento frío ni el permeable cambian las emisiones del tráfico: efecto sobre NO₂ = no cuantificado (sin base).",
        },
        "regla_combinacion": {
            "restricciones": [
                "X_arbolado_sobre_pasto ≤ max_pp_arbolado_sustituyendo_pasto",
                "X_techos_verdes ≤ max_pp_techos_verdes",
                "X_pavimento_frio ≤ max_pp_pavimento_frio",
                "X_arbolado_sobre_construido + X_techos_verdes + X_pavimento_frio ≤ max_pp_sobre_construido (una misma superficie construida no puede recibir dos intervenciones)",
            ],
            "suma": "ΔLST_total = Σ ΔLST_i y ΔNDVI_total = Σ ΔNDVI_i (mezcla lineal por área: cada intervención actúa sobre una fracción distinta de la zona; supuesto).",
            "pisos": ("ΔLST_total ≥ delta_lst_minimo_c = piso_lst_c − LST observada de la zona, con piso_lst_c = la mayor de la LST mediana de las "
                      "celdas de la cabecera con ≥ 80 % de arbolado (el bosque urbano observado) y la LST de referencia rural: una zona urbana arborizada "
                      "al máximo no debería quedar más fría que el bosque urbano que ya existe, que recibe el calor de la ciudad vecina. "
                      f"Con estos datos el piso es {es(piso_lst, 2)} °C ({'bosque urbano' if piso_criterio != 'lst_referencia_rural_c' else 'referencia rural'}; "
                      f"la referencia rural es {es(lst_rural, 2)} °C). ΔNDVI_total ≤ delta_ndvi_maximo = NDVI mediano de las celdas de la cabecera con "
                      "≥ 80 % de arbolado − NDVI observado de la zona. Supuestos de diseño para no extrapolar fuera de lo observado."),
            "piso_lst_c": r(piso_lst, 2),
            "piso_lst_criterio": piso_criterio,
            "piso_lst_nota": ("Hasta la versión anterior el piso era la LST de referencia rural (más fría); se cambió al bosque urbano observado por "
                              "ser más conservador y estar dentro de lo medido en la ciudad."),
            "lst_referencia_rural_c": r(lst_rural, 2),
            "lst_celdas_cabecera_arbolado_ge_80_c": r(lst_arb80, 2),
            "ndvi_celdas_cabecera_arbolado_ge_80": r(ndvi_techo, 3),
            "referencia_rural": "landsat.mascaras()['rural'] (fuera de la cabecera, a más de 500 m, sin agua, construido < 10 %, ± 30 m de la altitud de la cabecera), mediana de la capa lst 2022–2025",
            "aplicacion": ("Regla propuesta para el simulador: sumar el ΔLST acotado a la LST observada de la zona (no a la predicha por el modelo). "
                           "Este archivo no la aplica por sí mismo: una cifra del simulador solo respeta los topes y el piso si los implementa "
                           "(ver verificacion_topes)."),
        },
        "superficie_vial": {
            "metodo": (f"Ejes OSM highway = {', '.join(CARRILES)} con búfer de (carriles × {es(ANCHO_CARRIL_M, 1)} m)/2; carriles = etiqueta lanes de OSM o, si "
                       "falta, 2 (1 en enlaces y service). Unión de los búferes intersecada con cada zona en UTM 18N. Ancho por carril y carriles por defecto: supuestos. "
                       "No incluye andenes, separadores ni parqueaderos."),
            "superficie_etiquetada_pct_de_la_longitud": superficie_osm,
            "fuente": "fuentes/osm-vias.json, © colaboradores de OpenStreetMap, ODbL 1.0",
        },
        "disponibilidad_por_zona": disp,
        "verificacion_topes": {
            "por_zona": ver_topes,
            "zonas_con_alguna_intervencion_bajo_el_piso": n_sola,
            "zonas_con_la_combinacion_maxima_bajo_el_piso": n_comb,
            "metodo": ("ΔLST de cada intervención con X en su tope de superficie (max_pp_arbolado_sustituyendo_pasto, max_pp_sobre_construido para el "
                       "arbolado sobre construido, max_pp_techos_verdes, max_pp_pavimento_frio) y de la combinación de mayor enfriamiento que respeta "
                       "la restricción conjunta sobre lo construido, con los coeficientes centrales; se compara con delta_lst_minimo_c."),
            "lectura": (f"Aun dentro de las superficies disponibles, una sola intervención en su tope bajaría del piso de LST en {n_sola} de "
                        f"{len(zonas)} zonas y la combinación máxima en {n_comb}"
                        + (": el piso (regla_combinacion.pisos) es una restricción necesaria, no redundante. " if (n_sola or n_comb) else
                           ": con estos datos el piso no se alcanza dentro de las superficies disponibles. ")
                        + "max_pp_techos_verdes y max_pp_pavimento_frio son los topes de esas intervenciones; max_pp_sobre_construido es "
                        "el tope conjunto de lo que se hace sobre lo construido, no el de cada una."),
        },
        "ejemplo_por_zona_10pp": {
            z["id"]: {
                "arbolado_sustituye_pasto_delta_lst_c": coefL["arbolado_pct"]["valor"] if disp[z["id"]]["max_pp_arbolado_sustituyendo_pasto"] >= 10 else None,
                "arbolado_sustituye_construido_delta_lst_c": r(coefL["arbolado_pct"]["valor"] - coefL["construido_pct"]["valor"], 3),
                "nota": None if disp[z["id"]]["max_pp_arbolado_sustituyendo_pasto"] >= 10 else "La zona tiene menos de 10 pp de pasto u otras coberturas disponibles.",
            } for z in zonas},
        "limitaciones": [
            "Asociación transversal, no causalidad: otros factores ligados a la cobertura (riego, humedad del suelo, cercanía al río, materiales, sombra de edificios) pueden explicar parte del coeficiente.",
            f"La LST es temperatura de superficie a las {HORA} hora local en días despejados; no es la temperatura del aire que siente la gente ni la máxima de la tarde.",
            "WorldCover es de 2021 y la LST de 2022–2025: los cambios de cobertura entre esos años no se reflejan.",
            "Arbolado = área clasificada como árboles por WorldCover, no fracción de copa: el X del simulador está en esa unidad.",
            "Modelo lineal y aditivo: fuera del rango observado es una extrapolación; " + diagL["nota_no_linealidad"],
            diagL["nota_sesgo_zona"],
            diagL["nota_escala"],
            "El coeficiente del agua no está identificado (casi no hay agua en la cabecera).",
            "Los coeficientes de literatura (techos verdes, pavimentos) son de temperatura de superficie del elemento, de otros climas y materiales, en medias diarias; trasladarlos a la LST de 100 m con una mezcla lineal por área es un supuesto.",
            "El IC del bootstrap por bloques recoge la autocorrelación espacial a la escala del bloque, no la incertidumbre del modelo ni la de los datos de entrada.",
            "Los IC de literatura son de la media del metaanálisis y no recogen la heterogeneidad entre estudios (techos verdes I² 92 %); el intervalo de predicción publicado es una aproximación propia.",
            "El modelo de NDVI es en parte circular (WorldCover se clasificó con Sentinel-2): su ΔNDVI es una equivalencia de cobertura, no un efecto medido.",
            "Superficie vial estimada con ejes OSM y un ancho supuesto por carril: los topes de techos verdes y pavimento frío son aproximados.",
        ],
        "referencias": [
            {"nombre": "USGS, What are the band designations for the Landsat satellites? (TIRS 100 m, remuestreado a 30 m)", "url": "https://www.usgs.gov/faqs/what-are-band-designations-landsat-satellites", "verificado": True},
            {"nombre": "Das et al. (2025), BMJ Public Health 3(2): e002332", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12273142/", "verificado": True},
            {"nombre": "US EPA, Using Green Roofs to Reduce Heat Islands", "url": "https://www.epa.gov/heatislands/using-green-roofs-reduce-heat-islands", "verificado": True},
            {"nombre": "Abhijith et al. (2017), Atmospheric Environment 162: 71–86", "url": "https://doi.org/10.1016/j.atmosenv.2017.05.014", "verificado": True},
            {"nombre": "ESA WorldCover Sentinel-1 and Sentinel-2 10m Annual Composites (insumos de la clasificación WorldCover: compuestos S2 RGBNIR y SWIR, percentiles del NDVI S2 y S1 GAMMA0)",
             "url": "https://registry.opendata.aws/esa-worldcover-vito-composites/", "verificado": True},
            {"nombre": "Higgins, J. P. T., Thompson, S. G., Spiegelhalter, D. J. (2009). A re-evaluation of random-effects meta-analysis. J R Stat Soc A 172(1): 137–159 "
                       "(fórmula del intervalo de predicción μ ± t(k−2)·√(τ² + SE²), verificada en Nagashima, Noma y Furukawa, arXiv:1804.01054)",
             "url": "https://arxiv.org/abs/1804.01054", "verificado": True},
        ],
        "fuentes": fuentes[:3] + [{"capa": "altitud", **{k: meta["altitud"]["fuente"].get(k) for k in ("nombre", "url", "licencia", "cita")}},
                                  {"capa": "superficie vial", "nombre": "OpenStreetMap, red vial (fuentes/osm-vias.json)", "url": "https://www.openstreetmap.org/copyright",
                                   "licencia": "ODbL 1.0", "cita": "© colaboradores de OpenStreetMap"},
                                  {"capa": "serie y tendencia (NDVI Landsat de la sensibilidad)", "nombre": "USGS Landsat Collection 2 Level-2 (producto landsat)",
                                   "url": "https://planetarycomputer.microsoft.com/dataset/landsat-c2-l2", "licencia": "Dominio público USGS",
                                   "cita": "Landsat Collection 2 Level-2 Science Products courtesy of the U.S. Geological Survey"}],
        "script": "scripts/indicadores.py",
        "fecha_proceso": date.today().isoformat(),
    }
    guardar(os.path.join(comun.DATOS, "calibracion.json"), calib)
    log("Escrito datos/calibracion.json")

    # =====================================================================================
    # SALIDA 5: prioridades.json
    def frac(k):
        return [None if est[i].get(k) is None else r(est[i][k] / 100, 5) for i in ids]

    def anid(clave, k):
        return [None if est[i].get(clave) is None else est[i][clave].get(k) for i in ids]

    def conteos(k):
        return {i: est[i].get(k) for i in ids}

    hay_ev = all("ideam_evidencia_oficial" in est[i] for i in ids)
    if hay_ev:
        inund = {"id": "inundacion", "nombre": "Inundación: registros oficiales del IDEAM",
                 "valores_origen": [r(x / 100, 5) for x in anid("ideam_evidencia_oficial", "pct_poblacion")], "direccion": "+",
                 "unidad_origen": "fracción de la población (0–1)", "piso": PISO_RANGO,
                 "conteos_absolutos": dict(zip(ids, anid("ideam_evidencia_oficial", "poblacion"))),
                 "conteo_cabecera": est["cabecera"]["ideam_evidencia_oficial"]["poblacion"],
                 "formula": ("habitantes en (amenaza ALTA por creciente súbita TR 50 años del IDEAM ∪ áreas afectadas por inundación en eventos La Niña "
                             "1988–2022 del IDEAM) / habitantes de la zona")}
    else:
        inund = {"id": "inundacion", "nombre": "Susceptibilidad topográfica a inundación (HAND), clase alta",
                 "valores_origen": frac("pct_poblacion_susceptibilidad_alta"), "direccion": "+",
                 "unidad_origen": "fracción de la población (0–1)", "piso": PISO_RANGO,
                 "conteos_absolutos": conteos("poblacion_susceptibilidad_alta"),
                 "conteo_cabecera": est["cabecera"]["poblacion_susceptibilidad_alta"],
                 "formula": "habitantes en clase 3 (alta) de susceptibilidad_inundacion / habitantes de la zona"}
        problemas.append("Faltan registros del IDEAM (creciente súbita TR 50 o áreas afectadas por La Niña): el componente de inundación usa la "
                         f"susceptibilidad topográfica HAND alta ({es_int(est['cabecera']['poblacion_susceptibilidad_alta'])} hab en la cabecera), "
                         "que no es amenaza oficial.")
    comp_defs = [
        {"id": "calor", "nombre": "Calor extremo", "valores_origen": frac("pct_poblacion_calor_extremo"), "direccion": "+",
         "unidad_origen": "fracción de la población (0–1)", "piso": PISO_RANGO,
         "conteos_absolutos": conteos("poblacion_calor_extremo"), "conteo_cabecera": est["cabecera"]["poblacion_calor_extremo"],
         "formula": f"habitantes en celdas con LST ≥ {es(umbral, 2)} °C (p{P_CALOR} de la cabecera) / habitantes de la zona"},
        {"id": "deficit_verde", "nombre": "Déficit de verde", "valores_origen": None, "direccion": "+",
         "unidad_origen": "índice 0–1 (promedio de dos subcomponentes normalizados)", "piso": None,
         "conteos_absolutos": conteos("poblacion_sin_verde_300m"), "conteo_cabecera": est["cabecera"]["poblacion_sin_verde_300m"],
         "conteo_descripcion": "habitantes a más de 300 m de verde público ≥ 0,5 ha",
         "formula": "0,5·n(fracción de población a > 300 m de verde público ≥ 0,5 ha) + 0,5·n(−arbolado ponderado por población)"},
        inund,
        {"id": "trafico", "nombre": "Tráfico", "valores_origen": frac("pct_poblacion_trafico_alto"), "direccion": "+",
         "unidad_origen": "fracción de la población (0–1)", "piso": PISO_RANGO,
         "conteos_absolutos": conteos("poblacion_trafico_alto"), "conteo_cabecera": est["cabecera"]["poblacion_trafico_alto"],
         "formula": f"habitantes en celdas con índice de tráfico ≥ {es(TRAFICO_ALTO, 0)} / habitantes de la zona"},
        {"id": "densidad", "nombre": "Densidad de población", "valores_origen": [est[i]["densidad_hab_km2"] for i in ids], "direccion": "+",
         "unidad_origen": "hab/km²", "piso": None, "conteos_absolutos": conteos("poblacion"), "conteo_cabecera": est["cabecera"]["poblacion"],
         "conteo_descripcion": "habitantes de la zona", "formula": "habitantes / área de la zona (km²)"},
    ]
    sub_sv = frac("pct_poblacion_sin_verde_300m")
    sub_arb = [r(est[i]["arbolado_pct_pob"] / 100, 5) for i in ids]
    n_sv, nm_sv = normalizar(sub_sv, "+", PISO_RANGO)
    n_ab, nm_ab = normalizar(sub_arb, "-", PISO_RANGO)
    comps = {}
    for cdef in comp_defs:
        if cdef["id"] == "deficit_verde":
            n = [r((a + b) / 2, 4) for a, b in zip(n_sv, n_ab)]
            nm = [r((a + b) / 2, 4) for a, b in zip(nm_sv, nm_ab)]
            cdef["subcomponentes"] = {
                "sin_verde_300m": {"valores_origen": dict(zip(ids, sub_sv)), "unidad": "fracción de la población", "direccion": "+", "normalizado": dict(zip(ids, n_sv))},
                "arbolado_pob": {"valores_origen": dict(zip(ids, sub_arb)), "unidad": "fracción del área arbolada, ponderada por población", "direccion": "−", "normalizado": dict(zip(ids, n_ab))},
            }
        else:
            n, nm = normalizar(cdef["valores_origen"], cdef["direccion"], cdef["piso"])
        comps[cdef["id"]] = {"n": dict(zip(ids, n)), "n_minmax": dict(zip(ids, nm))}
        cdef["normalizado"] = dict(zip(ids, n))
        cdef["normalizado_minmax_puro"] = dict(zip(ids, nm))
        if cdef["valores_origen"] is not None:
            cdef["valores_origen"] = dict(zip(ids, cdef["valores_origen"]))
    pesos = {c["id"]: 0.2 for c in comp_defs}

    def indice(compn, pesos_, clave="n"):
        return {i: r(sum(pesos_[c] * compn[c][clave][i] for c in pesos_) / sum(pesos_.values()), 4) for i in ids}
    idx = indice(comps, pesos)
    orden, puesto = ranking(idx, ids)

    # ---- variantes de componentes
    variantes = {}

    def variante_fraccion(nombre, formula, fr, cnt, advert=None):
        nn, _ = normalizar(fr, "+", PISO_RANGO)
        v = {"nombre": nombre, "formula": formula, "valores_origen": dict(zip(ids, [r(x, 5) for x in fr])),
             "conteos_absolutos": dict(zip(ids, cnt)), "normalizado": dict(zip(ids, nn))}
        if advert:
            v["advertencia"] = advert
        return v
    P_ = [est[i]["poblacion"] for i in ids]
    z_hand = [nombres_z[i] for i in ids if est[i]["poblacion_susceptibilidad_alta"] > 0]
    variantes["inundacion_hand_alta"] = variante_fraccion(
        "Susceptibilidad topográfica a inundación (HAND), clase alta",
        "habitantes en clase 3 (alta) de susceptibilidad_inundacion / habitantes (componente literal de la tarea)",
        [est[i]["poblacion_susceptibilidad_alta"] / est[i]["poblacion"] for i in ids], [est[i]["poblacion_susceptibilidad_alta"] for i in ids],
        f"Casi nulo: solo {' y '.join(z_hand) or 'ninguna zona'} {'tienen' if len(z_hand) > 1 else 'tiene'} población en clase alta "
        f"({es_int(sum(est[i]['poblacion_susceptibilidad_alta'] for i in ids))} hab). Susceptibilidad topográfica, no amenaza oficial.")
    variantes["inundacion_alta_o_media"] = variante_fraccion(
        "Susceptibilidad topográfica a inundación (HAND), clases alta o media", "habitantes en clases 2 o 3 / habitantes",
        [(est[i]["poblacion_susceptibilidad_alta"] + est[i]["poblacion_susceptibilidad_media"]) / est[i]["poblacion"] for i in ids],
        [est[i]["poblacion_susceptibilidad_alta"] + est[i]["poblacion_susceptibilidad_media"] for i in ids],
        "Susceptibilidad topográfica, no amenaza oficial. Clase media: " + (etiquetas_sus_largas.get(2) or "s. d.").removeprefix("Media: ")
        + ". Mezcla poca altura sobre cauces menores, la franja junto a los ríos mayores y depresiones del modelo de superficie.")
    if ideam is not None:
        variantes["inundacion_ideam_alta"] = variante_fraccion(
            "Amenaza ALTA por creciente súbita TR 50 años (IDEAM)",
            "habitantes en la mancha de amenaza ALTA por creciente súbita TR 50 años del IDEAM (corrientes de la cuenca directa del río La Vieja) / habitantes",
            [est[i]["contraste_ideam_creciente_subita_tr50"]["poblacion_amenaza_alta"] / est[i]["poblacion"] for i in ids],
            [est[i]["contraste_ideam_creciente_subita_tr50"]["poblacion_amenaza_alta"] for i in ids],
            "Solo cubre la creciente súbita (TR 50 años) de las corrientes de la cuenca directa del río La Vieja"
            + (f": {txt_tr50}" if txt_tr50 else "") + ". No cubre la inundación lenta del Cauca ni las áreas afectadas por La Niña.")
    if nina is not None:
        variantes["inundacion_ideam_nina_observada"] = variante_fraccion(
            "Áreas afectadas por inundación en eventos La Niña 1988–2022 (IDEAM)",
            "habitantes en la unión de las áreas afectadas por La Niña (IDEAM) / habitantes",
            [est[i]["ideam_nina_observada"]["poblacion"] / est[i]["poblacion"] for i in ids], [est[i]["ideam_nina_observada"]["poblacion"] for i in ids],
            "Manchas de escala no declarada (bordes gruesos, eventos posiblemente incompletos, no validadas por el IDEAM según datos.gov.co); registro "
            f"histórico, no zonificación de amenaza. La parte urbana de La Niña {PERIODO_SIN} {coh_sin}"
            + (f" (ver 'inundacion_ideam_{sin_}')." if hay_ev else "."))
        if hay_ev:
            for clave, et in (("con_nina_reducida", "reducida"), ("con_nina_ampliada", "ampliada")):
                cnt = [est[i]["ideam_evidencia_oficial"]["sensibilidad_borde_55m"][clave] for i in ids]
                variantes[f"inundacion_ideam_borde_{et}_55m"] = variante_fraccion(
                    f"Registros IDEAM con la mancha La Niña {et} ≈ 55 m", f"como el componente por defecto, con la mancha La Niña {et} {BORDE_CELDAS} celdas",
                    [c / p for c, p in zip(cnt, P_)], cnt, "Sensibilidad a los bordes gruesos de las manchas La Niña (escala no declarada).")
            cnt = [est[i]["ideam_evidencia_oficial"][sin_]["poblacion"] for i in ids]
            variantes[f"inundacion_ideam_{sin_}"] = variante_fraccion(
                f"Registros IDEAM sin La Niña {PERIODO_SIN}",
                (f"habitantes en (amenaza ALTA por creciente súbita TR 50 ∪ áreas afectadas por La Niña {', '.join(p_ for p_ in nina['por_periodo'] if p_ != PERIODO_SIN)}"
                 f") / habitantes: el componente por defecto sin las capas La Niña {PERIODO_SIN} (8 y 22)"),
                [c / p for c, p in zip(cnt, P_)], cnt,
                (f"La parte urbana de la mancha de {PERIODO_SIN} "
                 + ("no está más baja sobre el drenaje que la ciudad no inundada" if est_sin == "no_coherente" else coh_sin)
                 + " (indicadores.json → coherencia_topografica_nina)"
                 + ("; puede sobrestimar y esta variante la excluye. Tampoco es definitiva: el área de "
                    f"{PERIODO_SIN} pudo inundarse por lluvia o alcantarillado. " if sobreestima_sin else "; esta variante, que la excluye, queda como sensibilidad. ")
                 + f"Contrastar con {CONTRASTE_REGISTROS}."))
    dc = [est[i]["densidad_sobre_area_construida_hab_km2"] for i in ids]
    n3, _ = normalizar(dc, "+", None)
    variantes["densidad_sobre_area_construida"] = {"nombre": "Densidad sobre el área construida", "formula": "habitantes / km² clasificados como construidos (WorldCover)",
                                                   "valores_origen": dict(zip(ids, dc)), "normalizado": dict(zip(ids, n3))}
    sv25 = frac("pct_poblacion_sin_verde_300m_umbral_025ha")
    n4, _ = normalizar(sv25, "+", PISO_RANGO)
    variantes["deficit_verde_umbral_025ha"] = {"nombre": "Déficit de verde con verde ≥ 0,25 ha", "formula": "como deficit_verde pero con verde ≥ 0,25 ha",
                                               "normalizado": dict(zip(ids, [r((a + b) / 2, 4) for a, b in zip(n4, n_ab)]))}
    # variante por conteos absolutos (personas expuestas en lugar de fracción de la zona)
    conteo_n = {}
    for cdef in comp_defs:
        if cdef["id"] == "densidad":
            continue
        vals = [cdef["conteos_absolutos"][i] for i in ids]
        conteo_n[cdef["id"]] = dict(zip(ids, normalizar(vals, "+", None)[0]))
    variantes["conteos_absolutos"] = {
        "nombre": "Personas expuestas (conteos absolutos)",
        "formula": ("calor, déficit de verde (solo personas a > 300 m de verde ≥ 0,5 ha), inundación y tráfico normalizados min–max con el número de "
                    "habitantes expuestos de cada zona, no con su fracción; densidad sin cambio"),
        "normalizado_por_componente": conteo_n,
        "advertencia": "Favorece a las zonas grandes (Comunas 6 y 7): responde a «dónde hay más personas expuestas», no a «dónde es más frecuente la exposición».",
    }

    # ---- sensibilidad del ranking
    def con_reemplazo(reemplazos):
        cc = {k: dict(v) for k, v in comps.items()}
        for cid, nuevos in reemplazos.items():
            cc[cid] = {"n": nuevos, "n_minmax": nuevos}
        return ranking(indice(cc, pesos), ids)[1]
    sens_rank = {"por_defecto": puesto}
    sens_rank["minmax_puro_sin_piso"] = ranking(indice(comps, pesos, "n_minmax"), ids)[1]
    for k in ("inundacion_hand_alta", "inundacion_alta_o_media", "inundacion_ideam_alta", "inundacion_ideam_nina_observada",
              "inundacion_ideam_borde_reducida_55m", "inundacion_ideam_borde_ampliada_55m", f"inundacion_ideam_{sin_}"):
        if k in variantes:
            sens_rank[k] = con_reemplazo({"inundacion": variantes[k]["normalizado"]})
    sens_rank["densidad_sobre_area_construida"] = con_reemplazo({"densidad": variantes["densidad_sobre_area_construida"]["normalizado"]})
    sens_rank["deficit_verde_umbral_025ha"] = con_reemplazo({"deficit_verde": variantes["deficit_verde_umbral_025ha"]["normalizado"]})
    sens_rank["conteos_absolutos"] = con_reemplazo(conteo_n)
    for c in pesos:
        p2 = {k: (0.0 if k == c else 0.25) for k in pesos}
        sens_rank[f"sin_{c}"] = ranking(indice(comps, p2), ids)[1]
    rango_puesto = {i: [min(v[i] for v in sens_rank.values()), max(v[i] for v in sens_rank.values())] for i in ids}
    hand_igual_sin = sens_rank.get("inundacion_hand_alta") == sens_rank["sin_inundacion"]
    idx_hand = indice({**comps, "inundacion": {"n": variantes["inundacion_hand_alta"]["normalizado"], "n_minmax": variantes["inundacion_hand_alta"]["normalizado"]}}, pesos)

    n_hand_alta = es_int(sum(est[i]['poblacion_susceptibilidad_alta'] for i in ids))
    if hay_ev:
        comp_defs[2]["advertencia"] = (
            "Registros oficiales del IDEAM, no susceptibilidad topográfica: la amenaza por creciente súbita (TR 50 años) solo cubre las corrientes de la cuenca "
            "directa del río La Vieja y las áreas afectadas por La Niña son manchas de escala no declarada (bordes gruesos; ver variantes "
            f"'inundacion_ideam_borde_*'). La parte urbana de La Niña {PERIODO_SIN} {coh_sin}"
            + (f" y puede sobrestimar: ver la variante 'inundacion_ideam_{sin_}' antes de usar las cifras de las zonas que dependen de ella. "
               if sobreestima_sin else f" (variante 'inundacion_ideam_{sin_}'). ")
            + "Decisión de diseño de este producto: la tarea pedía la población en susceptibilidad alta (HAND), pero esa clase solo tiene "
            f"{n_hand_alta} hab en la cabecera y con ella el ranking "
            f"{'es idéntico al que se obtiene quitando la inundación' if hand_igual_sin else 'cambia poco frente a quitar la inundación'}; se conserva como variante "
            "'inundacion_hand_alta' (y 'inundacion_alta_o_media').")
    else:
        comp_defs[2]["advertencia"] = (
            "Susceptibilidad topográfica (HAND), no amenaza oficial: en esta ejecución faltan registros del IDEAM (ver 'problemas') y el componente "
            f"vuelve a la clase alta HAND, que tiene {n_hand_alta} hab en la cabecera; con ella el ranking "
            f"{'es idéntico al que se obtiene quitando la inundación' if hand_igual_sin else 'cambia poco frente a quitar la inundación'}. Poca población en "
            "clase alta no significa ausencia de amenaza: consultar la zonificación oficial del IDEAM, la CVC y el POT.")
    comp_defs[1]["advertencia"] = ("El acceso a verde depende del verde mapeado en OSM y de suponer público todo polígono sin etiqueta de acceso; "
                                   "su orden entre comunas no es robusto (datos/series/verdes.json → sensibilidad).")
    comp_defs[4]["advertencia"] = ("Zaragoza es una huella construida y las comunas son polígonos administrativos con suelo no construido: la densidad bruta "
                                   "favorece a Zaragoza frente a la Comuna 7. Variante: 'densidad_sobre_area_construida'.")
    prior = {
        "titulo": "Componentes de priorización por zona",
        "descripcion": ("Cinco componentes de 0 (menor prioridad relativa) a 1 (mayor) para comparar las zonas de Cartago, y un índice por defecto "
                        "con pesos iguales. Es una herramienta para ordenar la discusión, no un diagnóstico: los pesos los decide quien usa la plataforma."),
        "zonas": [{"id": z["id"], "nombre": z["nombre"], "poblacion": est[z["id"]]["poblacion"]} for z in zonas],
        "metodo": {
            "normalizacion": ("Min–max entre las 8 zonas en la dirección indicada (1 = zona más prioritaria). Para los componentes que son fracciones de "
                              f"población, el denominador es max(rango, {es(PISO_RANGO, 2)}): diferencias menores de {int(PISO_RANGO * 100)} puntos porcentuales "
                              "de población no se amplían a toda la escala (supuesto de diseño, para no convertir decenas de personas en una prioridad máxima). "
                              "'normalizado_minmax_puro' da la versión sin piso."),
            "indice": "Promedio ponderado de los componentes normalizados; pesos por defecto iguales (0,2 cada uno).",
            "relativo": "Los valores son relativos a estas 8 zonas: un 0 no significa ausencia del problema.",
            "fracciones_y_conteos": ("Los componentes usan la fracción de la población de cada zona (qué tan frecuente es la exposición). Cada componente "
                                     "publica también 'conteos_absolutos' (cuántas personas), y la variante 'conteos_absolutos' recalcula el índice con ellos."),
            "inundacion": (("Por defecto, registros oficiales del IDEAM (amenaza alta por creciente súbita ∪ áreas afectadas por La Niña). La susceptibilidad "
                            "topográfica HAND se publica aparte como variante y nunca se mezcla con la amenaza oficial. La variante "
                            f"'inundacion_ideam_{sin_}' excluye La Niña {PERIODO_SIN}, cuya parte urbana {coh_sin} "
                            "(datos/indicadores.json → coherencia_topografica_nina).") if hay_ev else
                           ("Por diseño, el componente usa los registros oficiales del IDEAM (amenaza alta por creciente súbita ∪ áreas afectadas por La "
                            "Niña), pero en esta ejecución faltan (ver 'problemas'): usa la susceptibilidad topográfica HAND alta, que no es amenaza "
                            "oficial. Regenerar con la caché del IDEAM del producto inundacion antes de publicar.")),
        },
        "componentes": comp_defs,
        "variantes_componentes": variantes,
        "indice_por_defecto": {"pesos": pesos, "valores": idx, "ranking": orden, "puesto": puesto,
                               "ranking_nombres": [nombres_z[i] for i in orden]},
        "indice_con_inundacion_hand_alta": {"valores": idx_hand, "ranking": ranking(idx_hand, ids)[0],
                                            "nota": "Índice con el componente literal de la tarea (susceptibilidad HAND alta), solo como referencia."},
        "sensibilidad_ranking": {"puestos": sens_rank, "rango_de_puesto_por_zona": rango_puesto, "escenarios": len(sens_rank),
                                 "nota": ("Puesto de cada zona (1 = más prioritaria) con variantes de componentes, conteos absolutos, sin piso de rango y "
                                          "quitando un componente a la vez (los otros cuatro con peso 0,25).")},
        "limitaciones": [
            "Índice compuesto con pesos iguales: el resultado depende de los pesos, de la normalización y de qué componentes se incluyen (ver sensibilidad_ranking).",
            "Los componentes heredan las limitaciones de sus capas (ver datos/indicadores.json → limitaciones), en especial: "
            + ("registros de inundación del IDEAM de escala no declarada o limitados a la cuenca directa del La Vieja, susceptibilidad HAND que no coincide con ellos"
               if hay_ev else "susceptibilidad HAND en lugar de los registros del IDEAM (faltan en esta ejecución; no es amenaza oficial)")
            + ", verde OSM incompleto y tráfico como índice relativo (no NO₂).",
            "La normalización min–max es relativa a estas 8 zonas: al añadir o quitar zonas cambian todos los valores.",
            "Fracciones frente a conteos: con fracciones una zona pequeña con exposición frecuente sube por encima de zonas con más personas expuestas; ver 'conteos_absolutos'.",
            "Densidad bruta: las comunas incluyen suelo no construido y Zaragoza es una huella construida.",
        ] + ([L["nina_2011"]] if L.get("nina_2011") else []),
        "fuentes": "Las de datos/indicadores.json",
        "script": "scripts/indicadores.py",
        "fecha_proceso": date.today().isoformat(),
    }
    # ---------------- hallazgos (generados de los datos)
    def top3(vals, rev=True):
        return sorted(ids, key=lambda i: (-(vals[i] or 0) if rev else (vals[i] or 0), i))[:3]
    hall = []
    pc = {i: est[i]["pct_poblacion_calor_extremo"] for i in ids}
    nc = {i: est[i]["poblacion_calor_extremo"] for i in ids}
    hall.append(f"Calor (población en celdas con LST ≥ {es(umbral, 2)} °C, p90 de la cabecera). Mayor proporción: " + "; ".join(
        f"{nombres_z[i]} {es(pc[i], 1)} % ({es_int(nc[i])} hab)" for i in top3(pc)) + ". Más personas: " + "; ".join(
        f"{nombres_z[i]} {es_int(nc[i])} hab ({es(pc[i], 1)} %)" for i in top3(nc)) +
        f". En la cabecera, el 10 % del área más caliente aloja al {es(est['cabecera']['pct_poblacion_calor_extremo'], 1)} % de la población "
        f"({es_int(est['cabecera']['poblacion_calor_extremo'])} hab); la LST media ponderada por población es {es(est['cabecera']['lst_media_pob'], 2)} °C "
        f"frente a {es(est['cabecera']['lst_media'], 2)} °C por área.")
    dv = {i: comps["deficit_verde"]["n"][i] for i in ids}
    nsv = {i: est[i]["poblacion_sin_verde_300m"] for i in ids}
    hall.append("Déficit de verde (índice 0–1): " + "; ".join(
        f"{nombres_z[i]} {es(dv[i], 2)} ({es(est[i]['pct_poblacion_sin_verde_300m'], 1)} % de la población a más de 300 m de verde ≥ 0,5 ha; "
        f"arbolado ponderado por población {es(est[i]['arbolado_pct_pob'], 1)} %; {es(est[i]['m2_verde_publico_por_hab'], 2)} m² de verde público/hab)" for i in top3(dv)) +
        ". Más personas a más de 300 m: " + "; ".join(f"{nombres_z[i]} {es_int(nsv[i])} hab" for i in top3(nsv)) +
        f". Cabecera: {es(est['cabecera']['m2_verde_publico_por_hab'], 2)} m²/hab de verde público OSM frente al mínimo de 15 m²/hab de espacio público "
        "efectivo del Decreto 1504 de 1998 (conceptos no idénticos) y al promedio nacional de 3,3 m²/hab del CONPES 3718.")
    if hay_ev and nina is not None:
        ev = {i: est[i]["ideam_evidencia_oficial"]["pct_poblacion"] for i in ids}
        nev = {i: est[i]["ideam_evidencia_oficial"]["poblacion"] for i in ids}
        nn_ = {i: est[i]["ideam_nina_observada"] for i in ids}
        tsu = {i: est[i]["contraste_ideam_creciente_subita_tr50"]["poblacion_amenaza_alta"] for i in ids}
        ec = est["cabecera"]
        top_n = top3({i: nn_[i]["poblacion"] for i in ids})
        hv = hand_vs_ideam.get("cabecera", {}).get("pct_poblacion_nina_observada_por_clase_hand") or {}
        # zonas con amenaza ALTA TR 50: junto al eje del La Vieja o en corrientes menores de su cuenca directa (de los datos)
        z_tr = [i for i in sorted(ids, key=lambda i: -(tsu[i] or 0)) if (tsu[i] or 0) > 0]
        def donde_tr(i):
            dk = est[i]["contraste_ideam_creciente_subita_tr50"].get("distancia_mediana_amenaza_alta_al_eje_la_vieja_km")
            if dk is None:
                return ""
            return (f" (junto al La Vieja, mediana {es(dk * 1000, 0)} m del eje)" if dk * 1000 <= DIST_TR50_RIO_M else
                    f" (a {es(dk, 1)} km del eje del La Vieja: corrientes menores de su cuenca directa)")
        ord_sin = ranking(indice({**comps, "inundacion": {"n": variantes[f"inundacion_ideam_{sin_}"]["normalizado"],
                                                          "n_minmax": variantes[f"inundacion_ideam_{sin_}"]["normalizado"]}}, pesos), ids)[0]
        hall.append(
            "Inundación según los registros oficiales del IDEAM (amenaza ALTA por creciente súbita TR 50 en las corrientes de la cuenca directa del La Vieja ∪ "
            "áreas afectadas por La Niña 1988–2022): " + "; ".join(f"{nombres_z[i]} {es(ev[i], 1)} % ({es_int(nev[i])} hab)" for i in top3(ev)) +
            f"; cabecera {es_int(ec['ideam_evidencia_oficial']['poblacion'])} hab ({es(ec['ideam_evidencia_oficial']['pct_poblacion'], 1)} %). "
            f"La parte urbana de la mancha de La Niña {PERIODO_SIN} "
            + ("no está más baja sobre el drenaje que la ciudad no inundada y puede sobrestimar" if est_sin == "no_coherente" else
               coh_sin + (" y puede sobrestimar" if sobreestima_sin else ""))
            + ": sin "
            f"ella, la cabecera queda en {es_int(ec['ideam_evidencia_oficial'][sin_]['poblacion'])} hab ({es(ec['ideam_evidencia_oficial'][sin_]['pct_poblacion'], 1)} %) y "
            + "; ".join(f"{nombres_z[i]} pasa de {es(ev[i], 1)} % a {es(est[i]['ideam_evidencia_oficial'][sin_]['pct_poblacion'], 1)} %" for i in zonas_c) +
            (f"; el orden del índice {'no cambia' if ord_sin == orden else 'pasa a ' + ', '.join(nombres_z[i] for i in ord_sin)}. ")
            + f"Contrastar con registros municipales o de la UNGRD de 2010–2011 antes de usar las cifras de {', '.join(nombres_z[i] for i in zonas_c) or 'esas zonas'}. "
            "Habitantes actuales (2026) dentro de las manchas La Niña (no son los afectados de cada evento): " + "; ".join(
                f"{nombres_z[i]} {es_int(nn_[i]['poblacion'])} hab ({es(nn_[i]['pct_poblacion'], 1)} %; dentro de la mancha de "
                + ", ".join(f"{p_}: {es_int(v)}" for p_, v in nn_[i]["poblacion_por_periodo"].items() if v and v > 0)
                + f"; con el borde ± 55 m entre {es_int(nn_[i]['sensibilidad_borde_55m']['mancha_reducida'])} y {es_int(nn_[i]['sensibilidad_borde_55m']['mancha_ampliada'])})"
                for i in top_n) +
            ". Creciente súbita TR 50, amenaza ALTA: " + ("; ".join(f"{nombres_z[i]} {es_int(tsu[i])} hab{donde_tr(i)}" for i in z_tr) or "ninguna zona") +
            f". La susceptibilidad topográfica HAND alta suma {es_int(ec['poblacion_susceptibilidad_alta'])} hab en la cabecera y no coincide con esos registros: de la "
            f"población de la cabecera en áreas afectadas por La Niña, el {es(hv.get('3'), 1)} % está en clase alta HAND, el {es(hv.get('2'), 1)} % en media y el "
            f"{es((hv.get('1') or 0) + (hv.get('0') or 0), 1)} % en baja o HAND > 15 m (que no descartan amenaza). La mayor población con registro de inundación está en "
            f"la {nombres_z[top_n[0]]}" + (" (áreas afectadas por La Niña, que la capa de creciente súbita no cubre)" if (tsu[top_n[0]] or 0) == 0 else "")
            + ". Las manchas La Niña no dicen qué cauce desbordó.")
    pt = {i: est[i]["pct_poblacion_trafico_alto"] for i in ids}
    nt = {i: est[i]["poblacion_trafico_alto"] for i in ids}
    hall.append(f"Tráfico (población con índice ≥ {es(TRAFICO_ALTO, 0)}). Mayor proporción: " + "; ".join(
        f"{nombres_z[i]} {es(pt[i], 1)} % ({es_int(nt[i])} hab)" for i in top3(pt)) + ". Más personas: " + "; ".join(
        f"{nombres_z[i]} {es_int(nt[i])} hab" for i in top3(nt)) +
        f". En la cabecera, {es(est['cabecera']['pct_poblacion_trafico_alto'], 1)} %; el índice medio ponderado por población es "
        f"{es(est['cabecera']['trafico_medio_pob'], 1)} frente a {es(est['cabecera']['trafico_medio'], 1)} por área. Es un índice de proximidad a vías, no NO₂.")
    de = {i: est[i]["densidad_hab_km2"] for i in ids}
    hall.append("Densidad bruta: " + "; ".join(f"{nombres_z[i]} {es_int(de[i])} hab/km²" for i in top3(de)) +
                f". Cabecera {es_int(est['cabecera']['densidad_hab_km2'])} hab/km².")
    empates = [(a_, b_) for a_, b_ in zip(orden[:-1], orden[1:]) if abs(idx[a_] - idx[b_]) < 0.01]
    hall.append(f"Índice por defecto (pesos iguales; inundación con {'registros del IDEAM' if hay_ev else 'susceptibilidad HAND alta, porque faltan los registros del IDEAM'}): " +
                ", ".join(f"{k + 1}.º {nombres_z[i]} ({es(idx[i], 3)})" for k, i in enumerate(orden)) +
                ("; empate práctico (diferencia < 0,01) entre " + ", ".join(f"{nombres_z[a_]} y {nombres_z[b_]}" for a_, b_ in empates) if empates else "") +
                f". Rango de puesto en {len(sens_rank)} escenarios: " + "; ".join(f"{nombres_z[i]} {rango_puesto[i][0]}–{rango_puesto[i][1]}" for i in orden) +
                ". Con el componente literal de la tarea (HAND alta) el orden es " + ", ".join(nombres_z[i] for i in ranking(idx_hand, ids)[0]) +
                ("; ese orden es idéntico al de quitar la inundación" if hand_igual_sin else "") +
                ". Con conteos absolutos: " + ", ".join(nombres_z[i] for i in sorted(ids, key=lambda i: sens_rank["conteos_absolutos"][i])) +
                (f". Sin La Niña {PERIODO_SIN} en el componente de inundación: " + ", ".join(nombres_z[i] for i in sorted(ids, key=lambda i: sens_rank[f"inundacion_ideam_{sin_}"][i]))
                 if f"inundacion_ideam_{sin_}" in sens_rank else "") + ".")
    bl, bc = coefL["arbolado_pct"], coefL["construido_pct"]
    hall.append(f"Calibración (cabecera, unidades de ≈ 111 m, N = {mL['n']}, R² = {es(mL['r2'], 2)}): +10 pp de arbolado en lugar de pasto se asocia con "
                f"{es(bl['valor'], 2, True)} °C de LST (IC 95 % bloques {es(bl['ic95_bootstrap_bloques_500m'][0], 2, True)} a {es(bl['ic95_bootstrap_bloques_500m'][1], 2, True)}); "
                f"+10 pp de construido en lugar de pasto, {es(bc['valor'], 2, True)} °C ({es(bc['ic95_bootstrap_bloques_500m'][0], 2, True)} a {es(bc['ic95_bootstrap_bloques_500m'][1], 2, True)}); "
                f"arbolado en lugar de construido, {es(bl['valor'] - bc['valor'], 2, True)} °C por 10 pp. NDVI: {es(coefN['arbolado_pct']['valor'], 3, True)} y "
                f"{es(coefN['construido_pct']['valor'], 3, True)} por 10 pp (R² = {es(mN['r2'], 2)}; equivalencia de cobertura, en parte circular). "
                f"Topes que calibracion.json propone para el simulador (regla_combinacion): cada intervención hasta su superficie disponible "
                f"(max_pp_techos_verdes, max_pp_pavimento_frio…; max_pp_sobre_construido es el tope conjunto) y ΔLST total ≥ delta_lst_minimo_c, para que "
                f"ninguna zona baje de la LST del bosque urbano observado ({es(piso_lst, 2)} °C; la rural es {es(lst_rural, 2)} °C). "
                + ("El piso hace falta: aun " if (n_sola or n_comb) else "Con estos datos el piso no llega a actuar: ")
                + "dentro de esas superficies, una sola intervención en su tope bajaría de él en "
                + (f"las {n_sola} zonas" if n_sola == len(zonas) else f"{n_sola} de {len(zonas)} zonas")
                + f" y la combinación máxima en {'todas' if n_comb == len(zonas) else n_comb}"
                + (f"; el mayor exceso es de {es(-ver_topes[z_peor]['exceso_sobre_el_piso_c'], 2)} °C, en {nombres_z[z_peor]}" if n_comb else "")
                + ". Son restricciones propuestas en el archivo: una cifra del simulador solo las respeta si las aplica. Asociación transversal, no causalidad.")
    tl = est["cabecera"]["tendencia_lst"]["por_tramo"]["2013_2025_landsat_8_9"]
    rl = {i: est[i]["tendencia_lst"]["variantes_2013_2025"]["resumen"] for i in ids}
    rn = {i: est[i]["tendencia_ndvi_landsat_variantes_2013_2025"]["resumen"] for i in ids}
    lst_sig = [nombres_z[i] for i in ids if rl[i] and rl[i]["variantes_significativas"]]
    ndvi_rob = [i for i in ids if rn[i] and rn[i]["robusta"] and len(rn[i]["variantes_significativas"]) == rn[i]["n_variantes"]]
    ndvi_dep = [i for i in ids if rn[i] and not rn[i]["robusta"]]
    ndvi_nada = [i for i in ids if rn[i] and rn[i]["robusta"] and not rn[i]["variantes_significativas"]]
    sens_rob = [v for i in ndvi_rob for v in (rn[i]["sen_min"], rn[i]["sen_max"])]
    tn_r = S["tendencias_rural"]["ndvi"]["2013_2025_landsat_8_9"]
    txt = ("Tendencias 2013–2025 (Landsat 8/9): LST " + ("sin tendencia detectable en ninguna zona con ninguna de las 3 variantes" if not lst_sig else
                                                      f"con alguna variante significativa en {', '.join(lst_sig)}") +
           f" (cabecera, mediana: Sen {es(tl['sen_por_decada'], 2, True)} °C/década, IC {es(tl['ic95_sen'][0], 2, True)} a {es(tl['ic95_sen'][1], 2, True)}). "
           f"NDVI Landsat: disminución consistente en las 3 variantes (mediana, media, núcleo construido) en {len(ndvi_rob)} zonas"
           + (f" ({', '.join(nombres_z[i] for i in ndvi_rob)})" if ndvi_rob else "") +
           (f"; depende del método en {', '.join(nombres_z[i] for i in ndvi_dep)}" if ndvi_dep else "") +
           (f"; sin tendencia en {', '.join(nombres_z[i] for i in ndvi_nada)}" if ndvi_nada else "") +
           (f". En esas zonas, Sen entre {es(min(sens_rob), 3, True)} y {es(max(sens_rob), 3, True)} NDVI/década según la zona y la variante "
            f"(la mediana da la caída mayor en {sum(1 for i in ndvi_rob if est[i]['tendencia_ndvi_landsat_variantes_2013_2025']['variantes']['mediana']['sen_por_decada'] <= min(v['sen_por_decada'] for v in est[i]['tendencia_ndvi_landsat_variantes_2013_2025']['variantes'].values() if v))} de {len(ndvi_rob)})"
            if sens_rob else "") +
           f"; el campo de referencia {'no tiene tendencia' if not tn_r['significativa'] else 'también cambia'} (Sen {es(tn_r['sen_por_decada'], 3, True)}/década). ")
    for i in ndvi_dep:
        vv = est[i]["tendencia_ndvi_landsat_variantes_2013_2025"]["variantes"]
        txt += (f"{nombres_z[i]}: " + ", ".join(f"{NOMBRE_VAR[k]} {es(v['sen_por_decada'], 3, True)} (p {'< 0,001' if v['mann_kendall_p'] < 0.001 else '= ' + es(v['mann_kendall_p'], 3)})" for k, v in vv.items() if v) + ". ")
    txt += "La caída no está contrastada con una fuente independiente: no usar para decidir sin ese contraste."
    hall.append(txt)
    if feats is not None:
        eqc = est["cabecera"]["equipamientos"]
        en_z = [f["properties"] for f in feats if f["properties"].get("zona_id")]
        cal_l = [p for p in en_z if p.get("calor_extremo")]
        hall.append(
            f"Equipamientos OSM dentro de las zonas: {eqc['por_categoria']['total']} (" +
            ", ".join(f"{eqc['por_categoria'][c]} de {NOMBRE_CAT[c]}" for c in CATEGORIAS) + "). En calor extremo: " +
            "; ".join(f"{p['nombre_mostrar']} ({es(p['lst_c'], 2)} °C, margen {es(p['lst_margen_umbral_c'], 2, True)} °C"
                      + (", en el umbral" if p.get("en_umbral_calor") else "") + ")" for p in sorted(cal_l, key=lambda p: -p["lst_c"])) +
            f". A más de 300 m de verde ≥ 0,5 ha: {eqc['expuestos']['a_mas_de_300m_de_verde']['total']}; susceptibilidad alta HAND: "
            f"{eqc['expuestos']['susceptibilidad_alta']['total']}; tráfico alto: {eqc['expuestos']['trafico_alto']['total']}; amenaza alta IDEAM por creciente súbita: "
            f"{eqc['expuestos']['amenaza_alta_ideam_contraste']['total']}; en áreas afectadas por La Niña (IDEAM): {eqc['expuestos']['area_afectada_nina_ideam']['total']}"
            + (" (" + "; ".join(f"{p['nombre_mostrar']}: {', '.join(p['periodos_nina_ideam'])}" for p in en_z if p.get("area_afectada_nina_ideam")) + ")"
               if eqc['expuestos']['area_afectada_nina_ideam']['total'] else "") + ". OSM solo tiene una parte de las sedes reales.")
    prior["hallazgos"] = hall[:6]
    prior["problemas"] = list(problemas)
    guardar(os.path.join(comun.DATOS, "prioridades.json"), prior)
    log("Escrito datos/prioridades.json")
    indicadores["hallazgos"] = hall
    indicadores["problemas"] = list(problemas)
    guardar(os.path.join(comun.DATOS, "indicadores.json"), indicadores)
    for pr in problemas:
        log("PROBLEMA:", pr)
    if not problemas:
        log("Sin problemas de ejecución (todas las capas y cachés presentes).")
    for h in hall:
        log("HALLAZGO:", h)

    # =====================================================================================
    # resumen en consola
    log("— Resumen por zona —")
    for i in ids + ["cabecera"]:
        d = est[i]
        log(f"{nombres_z[i]:<36} pob {d['poblacion']:>8.0f} dens {d['densidad_hab_km2']:>7.0f} LST {d['lst_media']:.2f} "
            f"anom {d['lst_anomalia']:+.2f} calor %pob {d['pct_poblacion_calor_extremo']:>5.1f} arb {d['arbolado_pct']:>5.1f} "
            f"verde m²/hab {d.get('m2_verde_publico_por_hab')} sinverde {d['pct_poblacion_sin_verde_300m']:>5.1f} "
            f"sus3 {d['poblacion_susceptibilidad_alta']:.0f} sus2 {d['poblacion_susceptibilidad_media']:.0f} traf≥60 {d['pct_poblacion_trafico_alto']:.1f} % "
            f"tend {d['tendencia_lst_c_decada']}")
    log(f"Índice por defecto: {[(nombres_z[i], idx[i]) for i in orden]}")
    log(f"Rango de puesto: {rango_puesto}")
    log(f"Coherencia de población: {coh['coherente']}; norte/sur: {ns_ok}")
    log(f"Duración: {(datetime.now() - t0).total_seconds():.1f} s")
    return {"est": est, "umbral": umbral, "idx": idx, "orden": orden, "problemas": problemas}


if __name__ == "__main__":
    main()
