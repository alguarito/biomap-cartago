"""Espacio verde público, equipamientos sensibles y distancia al verde en Cartago (OpenStreetMap).

FUENTES
  OpenStreetMap — fuentes/osm-verdes-equipamientos.json: respuesta Overpass 'out geom'
    (relaciones con miembros que traen geometry, ways con geometry, nodos con lat/lon).
    Marca temporal osm3s.timestamp_osm_base = 2026-10-01T01:50:59Z, en UTC (2026-09-30 20:50 hora de
    Colombia, UTC−5: por eso es "posterior" a la fecha de proceso local 2026-09-30).
    Consulta (registrada en la sesión que hizo la descarga y copiada en CONSULTA_OVERPASS; el script la
    escribe en fuentes/verdes/osm-verdes-equipamientos.overpassql y comprueba que el archivo la cumple):
      [out:json][timeout:170];(
        nwr["leisure"~"^(park|garden|pitch|playground|nature_reserve|recreation_ground)$"](4.688,-75.985,4.795,-75.855);
        nwr["landuse"~"^(grass|recreation_ground|forest|meadow|village_green|cemetery)$"](...);
        nwr["natural"~"^(wood|wetland|water|scrub|tree_row)$"](...);
        nwr["amenity"~"^(school|kindergarten|college|university|hospital|clinic|doctors|nursing_home|
                        social_facility|fire_station|police|townhall)$"](...);
      );out geom;
    POST a https://overpass-api.de/api/interpreter (Overpass API 0.7.62.11). No pidió healthcare=*.
    Licencia: Open Database License (ODbL) 1.0. Atribución: «© colaboradores de OpenStreetMap».
    https://www.openstreetmap.org/copyright
  Geometría auxiliar (ODbL) vía comun.osm(): cabecera, límite municipal, comunas, río La Vieja.
  fuentes/osm-vias.json (Overpass, misma descarga, way["highway"] en la misma caja, ODbL): vías
    principales (separadores viales) y nombres de vías de servicio que mencionan instituciones.
  Zona urbana del Marco Geoestadístico Nacional 2018 del DANE (clase 1 = cabecera), caché de
    scripts/poblacion.py en fuentes/poblacion/mgn2018_zona_urbana_76147.geojson. OJO: el polígono
    clase 1 de Cartago es uno solo y llega hasta el área urbana de Zaragoza. Términos DANE: uso y
    transformación autorizados citando «Fuente: Departamento Administrativo Nacional de Estadística:
    www.dane.gov.co». Si falta, se usa la cabecera de OSM.
  Población de la cabecera 2026: DANE, PPED serie municipal por área 2018-2042 (actualizada el
    30-jul-2025), leída de datos/series/poblacion.json (139.614 hab).
  Capa 'poblacion' (scripts/poblacion.py) para el indicador ponderado por población; capas
    'arbolado', 'cob_pasto' y 'construido' (ESA WorldCover 2021, scripts/worldcover.py, CC BY 4.0)
    solo para señalar vegetación sin mapear y para el escenario de sensibilidad (a).
  Referencias oficiales para estimar la cobertura de OSM (solo conteos agregados; caché en
    fuentes/verdes/referencias/, se consultan una vez y luego se reutilizan):
    - MEN, MEN_ESTABLECIMIENTOS_EDUCATIVOS_PREESCOLAR_BÁSICA_Y_MEDIA (datos.gov.co cfw5-qzt5,
      CC BY-SA 4.0): establecimientos y sedes de Cartago (76147) por año y sector.
    - MinSalud, Registro Especial de Prestadores y Sedes de Servicios de Salud (datos.gov.co
      c36g-9fc2, CC BY-SA 4.0): sedes en Cartago por clase de prestador.
    - Secretaría de Educación Municipal de Cartago, Boletín Estadístico Sector Educación – Año 2023
      (marzo de 2024, MMDS.600.18.F.125), pp. 16, 18, 19 y 27 (cifras copiadas en REF_BOLETIN).
    - Findeter (2022), Cartago Ciudad Emblemática, documento de diagnóstico, pp. 58 y 60: inventario
      del diagnóstico del POT (224.800 m² de espacio público efectivo urbano; 1,68 m²/hab en 2021).

REFERENCIAS VERIFICADAS (2026-09-30)
  WHO Regional Office for Europe (2016). Urban green spaces and health. A review of evidence.
    Copenhague: WHO Regional Office for Europe. https://www.who.int/europe/publications/i/item/WHO-EURO-2016-3352-43111-60341
    Sección 3.6.2 (p. 30-31): verde según Urban Atlas 1.4.1 «Green Urban Areas» con 0,5 ha
    (indicador principal) o 1,0 ha (adicional); 300 m lineales ≈ 5 min a pie. Sección 4.1 (p. 32):
    «currently there is no consensus» sobre la distancia; los casos de estudio de esa misma sección
    probaron tamaños mínimos de 0,25 a 5 ha y distancias de 100 a 500 m. Recuadro 4.1 (p. 33):
    Urban Atlas 14100, unidad mínima 0,25 ha y ancho mínimo 10 m; incluye bosques que entran en la
    ciudad si al menos dos lados lindan con zona urbana y hay huellas de uso recreativo; excluye
    jardines privados, cementerios y «patches of natural vegetation ... enclosed by built-up areas
    without being managed as green urban areas». Sección 4.3.2, paso 2 (p. 36): otras distancias
    (p. ej. 200 y 500 m). Sección 4.4 (p. 39): verde ≥ 0,5 ha (adicional 1,0 ha), 300 m al borde en
    línea recta; el indicador es la proporción de la población con «recommended access».
    Copia local: fuentes/verdes/who2016_iris.pdf (IRIS).
  Decreto 1504 de 1998, art. 12 y 14 (Decreto 1077 de 2015, arts. 2.2.3.2.5 y 2.2.3.2.7): espacio
    público efectivo = zonas verdes, parques, plazas y plazoletas; mínimo 15 m²/hab.
    https://normas.cra.gov.co/gestor/docs/decreto_1504_1998.htm — solo como referencia orientativa.

PASOS
  1. Ensambla geometrías: ways cerrados → polígonos; relaciones multipolygon → anillos 'outer'
     unidos con linemerge (los tramos abiertos se cosen), menos anillos 'inner'; relaciones
     type=building → miembro 'outline'. Se reparan con make_valid.
  2. Espacio verde candidato: leisure = park, playground, recreation_ground, nature_reserve,
     garden; landuse = recreation_ground, village_green. Acceso: access=private/no o garden:type
     privado → privado; ≥ 50 % dentro de un equipamiento o cementerio → institucional; tarifa
     verificada externamente (EXCLUSIONES) → fuera; access=yes/public → público; sin etiqueta → se
     asume público. Separadores viales (≥ 90 % del borde a ≤ 10 m de una vía principal y ancho medio
     2·A/P < 10 m; Urban Atlas 14100 exige 10 m de ancho) → fuera. Canchas (leisure=pitch) fuera,
     contadas aparte.
  3. En UTM 18N (EPSG:32618): unión del verde público, cierre morfológico de 1,5 m y componentes
     conexos; área del componente = unión de los polígonos originales.
  4. Capa 'distancia_verde': distancia euclidiana exacta (STRtree.query_nearest) desde el centro de
     cada celda al borde del componente público ≥ 0,5 ha más cercano; 0 dentro; escala 1 m.
     .npy adicionales: 'distancia_verde_todos' (cualquier tamaño, incluye jardineras de decenas de m²)
     y 'distancia_verde_025ha' (unidad mínima de Urban Atlas).
     Paleta divergente centrada en 300 m (rango_visual 0–600 m): el paso de verde a amarillo y naranja
     cae en el criterio de la OMS en el visor, que interpola linealmente (js/datos.js).
  5. Sensibilidad (OMS 300 m, población de la cabecera DANE y por zona): umbrales 0,25 / 0,5 / 1 ha
     y sin umbral; (a) + manchas de vegetación intraurbana de WorldCover sin mapear; (b) + bosques y
     matorrales de OSM (natural=wood/scrub, landuse=forest) ≥ 0,5 ha que tocan la cabecera; (c) +
     centros recreativos con tarifa; (a+b+c) juntos. Se publica el rango y el orden de las zonas.
  6. Equipamientos sensibles (amenity o healthcare): educación, salud, cuidado, emergencia y
     gobierno. Áreas → centroide (o punto representativo). Duplicados: punto dentro de un área del
     mismo subtipo; mismo nombre normalizado y categoría a < 50 m. Cobertura frente a MEN, Boletín
     municipal y REPS.
  7. Hallazgos en datos/series/verdes.json (con 'limitaciones'), vacíos de OSM y verificaciones
     (rangos, puntos de control, norte/sur, PNG vs .npy, colores del visor en 299/301 m, consulta
     Overpass vs contenido del archivo).

Uso: .venv/bin/python scripts/verdes.py   (sin red si existen las cachés de fuentes/verdes/referencias)
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comun  # noqa: E402

import shapely  # noqa: E402
from pyproj import Transformer  # noqa: E402
from shapely.geometry import LineString, MultiLineString, Point, Polygon, box, mapping, shape  # noqa: E402
from shapely.ops import linemerge, unary_union  # noqa: E402
from shapely.strtree import STRtree  # noqa: E402

OSM_JSON = os.path.join(comun.FUENTES, "osm-verdes-equipamientos.json")
VIAS_JSON = os.path.join(comun.FUENTES, "osm-vias.json")
MGN_URBANA = os.path.join(comun.FUENTES, "poblacion", "mgn2018_zona_urbana_76147.geojson")
SERIE_POB = os.path.join(comun.DATOS, "series", "poblacion.json")
VECTORES = os.path.join(comun.DATOS, "vectores")
SERIES = os.path.join(comun.DATOS, "series")
DIR = os.path.join(comun.FUENTES, "verdes")
DIR_REF = os.path.join(DIR, "referencias")
for d in (VECTORES, SERIES, DIR, DIR_REF):
    os.makedirs(d, exist_ok=True)

BBOX = (4.688, -75.985, 4.795, -75.855)   # sur, oeste, norte, este (orden Overpass)
_bb = "({},{},{},{})".format(*BBOX)
FILTROS_OVERPASS = {
    "leisure": ("park", "garden", "pitch", "playground", "nature_reserve", "recreation_ground"),
    "landuse": ("grass", "recreation_ground", "forest", "meadow", "village_green", "cemetery"),
    "natural": ("wood", "wetland", "water", "scrub", "tree_row"),
    "amenity": ("school", "kindergarten", "college", "university", "hospital", "clinic", "doctors", "nursing_home",
                "social_facility", "fire_station", "police", "townhall"),
}
CONSULTA_OVERPASS = "[out:json][timeout:170];(" + "".join(
    f'nwr["{k}"~"^({"|".join(v)})$"]{_bb};' for k, v in FILTROS_OVERPASS.items()) + ");out geom;"

A_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True)
UMBRAL_HA = 0.5          # OMS 2016, indicador principal
UMBRAL_HA_ALT = 1.0      # OMS 2016, indicador adicional
UMBRAL_HA_UA = 0.25      # unidad mínima de Urban Atlas (OMS 2016, recuadro 4.1)
DIST_OMS = 300           # m, línea recta
CIERRE_M = 1.5           # m
DUP_M = 50               # m
SEP_BORDE = 0.90
SEP_DIST_M = 10          # m
SEP_ANCHO_M = 10         # m; ancho mínimo de Urban Atlas 14100 (OMS 2016, recuadro 4.1)
VIAS_MAYORES = {"motorway", "trunk", "primary", "secondary", "tertiary",
                "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link"}

# Paleta del visor: 5 colores interpolados linealmente entre 0 y 600 m (paradas cada 150 m); la parada
# central (#ffffbf) cae en 300 m, el criterio OMS: verdes por debajo, amarillo-naranja-rojo por encima.
RANGO_VISUAL = [0, 600]
PALETA = ["#1a9850", "#a6d96a", "#ffffbf", "#fdae61", "#d73027"]
CLASES_LEYENDA = [(0, 200, "≤ 200 m"), (200, 300, "200–300 m (cumple el criterio OMS)"),
                  (300, 500, "300–500 m (no cumple)"), (500, None, "> 500 m (color saturado desde 600 m)")]

VERDE_LEISURE = {"park": "parque", "playground": "zona de juegos", "recreation_ground": "zona recreativa",
                 "nature_reserve": "reserva natural", "garden": "jardín"}
VERDE_LANDUSE = {"recreation_ground": "zona recreativa", "village_green": "zona verde comunal"}
BOSQUES = (("natural", "wood"), ("natural", "scrub"), ("landuse", "forest"))

# Reclasificaciones con evidencia externa (consultada el 2026-09-30).
EXCLUSIONES = {
    "way/1305319659": {
        "acceso": "con tarifa (centro recreacional de caja de compensación)",
        "evidencia": "Hotel y Centro Recreacional Villasol, operado por Comfenalco Valle Delagente; los no afiliados pagan "
                     "entrada según categoría D.",
        "url": "https://www.comfenalcovalle.com.co/en/personas/recreacion-y-deportes/nuestros-centros-recreacionales/villasol/",
    },
    "way/1318891866": {
        "acceso": "con tarifa (establecimiento comercial)",
        "evidencia": "Centro Turístico Míster Mojarra (Calle 55B # 3N-51, Santa Ana): establecimiento comercial con "
                     "piscinas, lagos de pesca, restaurante y cabañas; según reseñas de visitantes se paga entrada.",
        "url": "https://co.fitfit.fitness/es/i/3593-mister-mojarra/",
    },
}
# Escenarios deportivos de acceso restringido verificados (no son verde; solo para no listarlos como públicos)
CLUBES = {
    "way/712320807": {"nota": "Club Campestre de Cartago: club social (S.A.) con planes de socios y pasadía pagado para no "
                              "socios", "url": "https://co.fitfit.fitness/es/i/3586-club-campestre-cartago/"},
}

EQUIP = {
    "school": "educacion", "kindergarten": "educacion", "college": "educacion", "university": "educacion",
    "hospital": "salud", "clinic": "salud", "doctors": "salud", "doctor": "salud",
    "nursing_home": "cuidado", "social_facility": "cuidado",
    "fire_station": "emergencia_gobierno", "police": "emergencia_gobierno", "townhall": "emergencia_gobierno",
}
CATEGORIA_ES = {"educacion": "Educación", "salud": "Salud", "cuidado": "Cuidado",
                "emergencia_gobierno": "Emergencia y gobierno"}
SUBTIPO_ES = {"school": "colegio o escuela", "kindergarten": "jardín infantil", "college": "institución técnica o tecnológica",
              "university": "universidad", "hospital": "hospital", "clinic": "clínica o IPS", "doctors": "consultorio",
              "doctor": "consultorio", "nursing_home": "hogar geriátrico", "social_facility": "servicio social",
              "fire_station": "estación de bomberos", "police": "policía", "townhall": "alcaldía"}

# Boletín Estadístico Sector Educación – Año 2023 (Secretaría de Educación Municipal de Cartago, marzo de 2024).
# Cifras leídas por este agente en el PDF (copia en fuentes/verdes/referencias/boletin_estadistico_sem_cartago_2024.pdf).
REF_BOLETIN = {
    "fuente": "Secretaría de Educación Municipal de Cartago, Boletín Estadístico Sector Educación – Año 2023 "
              "(marzo de 2024, código MMDS.600.18.F.125)",
    "url": "https://municipio.cartago.gov.co/wp-content/uploads/2024/04/BOLETIN_ESTADISTICO-SEM_2024-FINAL.pdf",
    "sedes_oficiales_total": 41, "sedes_oficiales_urbanas": 29, "sedes_oficiales_rurales": 12,
    "no_oficiales_total": 25, "no_oficiales_urbanos": 24, "no_oficiales_en_tabla_p16": 26,
    "centros_desarrollo_infantil": 5, "universidades": 6, "sena": 1, "instituciones_etdh": 29,
    "paginas": "p. 16 (tabla: 12 IE oficiales con 29 sedes + 12 principales, 26 no oficiales, 5 CDI, 6 universidades, "
               "1 SENA, 29 ETDH); p. 18 (41 sedes oficiales); p. 19 (29 sedes oficiales urbanas y 12 rurales); p. 27 "
               "(25 no oficiales, 24 urbanos). El propio boletín da 26 no oficiales en la tabla y 25 en el texto.",
}
REF_FINDETER = {
    "fuente": "Findeter (2022). Cartago, ciudad emblemática. Documento de diagnóstico, versión final, diciembre de 2022",
    "url": "https://www.findeter.gov.co/system/files/internas/Diagnostico-PDA-Cartago.pdf",
    "epe_urbano_m2": 224800, "epe_m2_hab_2021": 1.68, "poblacion_urbana_2021": 133400,
    "paginas": "p. 58 (según el diagnóstico del POT, 224.800 m² de espacio público efectivo en la zona urbana, con la "
               "plaza Simón Bolívar, el parque de la Isleta y el Parque Lineal Los Samanes); p. 60 (1,68 m²/hab al cierre "
               "de 2021 con 133.400 habitantes urbanos proyectados por el DANE)",
}

PUNTOS_CONTROL = {
    "Parque Bolívar (centro)": (4.7497, -75.9132),
    "Aeropuerto Santa Ana": (4.7601, -75.9545),
    "Rural suroccidente": (4.700, -75.975),
    "Rural nororiente (otra orilla del La Vieja)": (4.790, -75.870),
}


# ------------------------------------------------------------------ utilidades

def a_utm(g):
    return shapely.transform(g, lambda c: np.column_stack(A_UTM.transform(c[:, 0], c[:, 1])))


def de_utm(g):
    inv = Transformer.from_crs("EPSG:32618", "EPSG:4326", always_xy=True)
    return shapely.transform(g, lambda c: np.column_stack(inv.transform(c[:, 0], c[:, 1])))


def poligonal(g):
    """Solo las partes poligonales de una geometría (make_valid puede devolver colecciones)."""
    if g is None or g.is_empty:
        return None
    g = shapely.make_valid(g)
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    partes = [p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")]
    return unary_union(partes) if partes else None


def partes(g):
    return list(g.geoms) if g.geom_type == "MultiPolygon" else [g]


def normalizar(nombre):
    if not nombre:
        return ""
    s = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode().lower()
    return " ".join("".join(ch if ch.isalnum() else " " for ch in s).split())


def redondear(obj, nd=6):
    if isinstance(obj, (list, tuple)):
        return [redondear(x, nd) for x in obj]
    if isinstance(obj, float):
        return round(obj, nd)
    return obj


def feature(geom, props):
    m = mapping(geom)
    return {"type": "Feature", "geometry": {"type": m["type"], "coordinates": redondear(m["coordinates"])},
            "properties": props}


def escribir_geojson(ruta, features, meta):
    obj = {"type": "FeatureCollection", "name": os.path.splitext(os.path.basename(ruta))[0],
           "metadatos": meta, "features": features}
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"), default=comun._json_default)


def color_visor(v, paleta=PALETA, rango=RANGO_VISUAL):
    """Mismo cálculo que BM.colorearCapa (js/datos.js): interpolación lineal entre paradas uniformes."""
    rgb = [[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in paleta]
    m = len(rgb) - 1
    t = max(0.0, min(1.0, (v - rango[0]) / (rango[1] - rango[0]))) * m
    i = min(int(np.floor(t)), m - 1)
    f = t - i
    c = [round(rgb[i][k] + (rgb[i + 1][k] - rgb[i][k]) * f) for k in range(3)]
    return "#{:02x}{:02x}{:02x}".format(*c)


def coma(x):
    """Decimal con coma para los textos en español."""
    return str(x).replace(".", ",")


def corte_txt(s):
    """'Fecha corte REPS: Mar 12 2026  3:11PM' → '12-mar-2026'."""
    m = re.search(r"([A-Z][a-z]{2}) +(\d{1,2}) +(\d{4})", s or "")
    if not m:
        return s
    meses = dict(zip(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
                     ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")))
    return f"{int(m.group(2))}-{meses.get(m.group(1), m.group(1))}-{m.group(3)}"


def mediana_ponderada(vals, pesos):
    o = np.argsort(vals)
    c = np.cumsum(pesos[o])
    if c[-1] <= 0:
        return None
    return float(vals[o][np.searchsorted(c, c[-1] / 2)])


def socrata(nombre, dataset, params):
    """Consulta agregada a datos.gov.co (Socrata) con caché local; None si no hay red ni caché."""
    ruta = os.path.join(DIR_REF, f"{nombre}.json")
    if os.path.exists(ruta):
        return json.load(open(ruta, encoding="utf-8"))
    import requests
    url = f"https://www.datos.gov.co/resource/{dataset}.json"
    err = None
    for _ in range(3):
        try:
            r = requests.get(url, params=params, timeout=90)
            r.raise_for_status()
            obj = {"dataset": dataset, "consulta": r.url, "fecha_consulta": date.today().isoformat(),
                   "licencia": "CC BY-SA 4.0 (según la ficha del conjunto en datos.gov.co)", "filas": r.json()}
            comun.guardar_json(ruta, obj)
            return obj
        except Exception as ex:  # red lenta o caída: se reintenta y, si no, se omite la comparación
            err = ex
            time.sleep(3)
    PROBLEMAS.append(f"No se pudo consultar datos.gov.co/{dataset} ({err}); se omite esa comparación de cobertura")
    return None


# ------------------------------------------------------------------ geometría OSM

PROBLEMAS = []


def anillos(miembros, rol, eid):
    segs = [LineString([(p["lon"], p["lat"]) for p in m["geometry"]])
            for m in miembros if m["type"] == "way" and m.get("role") == rol and len(m.get("geometry", [])) >= 2]
    if not segs:
        return []
    unido = linemerge(MultiLineString(segs)) if len(segs) > 1 else segs[0]
    ps = list(unido.geoms) if unido.geom_type == "MultiLineString" else [unido]
    polis, abiertos = [], 0
    for p in ps:
        c = list(p.coords)
        if len(c) >= 4 and c[0] == c[-1]:
            polis.append(Polygon(c))
        else:
            abiertos += 1
    if abiertos:
        PROBLEMAS.append(f"relation/{eid}: {abiertos} tramo(s) '{rol}' no cierran anillo; se ignoran")
    return polis


def geometria(e):
    """Polygon/MultiPolygon (lon/lat) para ways y relaciones; Point para nodos."""
    if e["type"] == "node":
        return Point(e["lon"], e["lat"])
    if e["type"] == "way":
        c = [(p["lon"], p["lat"]) for p in e.get("geometry", [])]
        if len(c) >= 4 and c[0] == c[-1]:
            return poligonal(Polygon(c))
        return None
    tipo = e.get("tags", {}).get("type")
    if tipo == "building":
        out = anillos(e["members"], "outline", e["id"]) or anillos(e["members"], "outer", e["id"])
        return poligonal(unary_union([poligonal(p) for p in out])) if out else None
    out = anillos(e["members"], "outer", e["id"]) + anillos(e["members"], "", e["id"])
    inn = anillos(e["members"], "inner", e["id"])
    if not out:
        return None
    g = unary_union([poligonal(p) for p in out if poligonal(p) is not None])
    if inn:
        g = g.difference(unary_union([poligonal(p) for p in inn if poligonal(p) is not None]))
    return poligonal(g)


def oid(e):
    return f"{e['type']}/{e['id']}"


def componentes_de(polis):
    """Componentes conexos (cierre de CIERRE_M) de una lista de polígonos UTM; geometría = unión de los originales."""
    if not polis:
        return []
    u = unary_union(polis)
    cerr = u.buffer(CIERRE_M, join_style="mitre").buffer(-CIERRE_M, join_style="mitre")
    cs = partes(cerr)
    arbol = STRtree(cs)
    grupos = defaultdict(list)
    for p in partes(u):
        idx = arbol.query(p.representative_point(), predicate="intersects")
        k = int(idx[0]) if len(idx) else int(arbol.query_nearest(p.representative_point())[0])
        grupos[k].append(p)
    return [unary_union(g) for _, g in sorted(grupos.items())]


# ------------------------------------------------------------------ programa

def main():
    t0 = time.time()
    datos = json.load(open(OSM_JSON, encoding="utf-8"))
    marca = datos.get("osm3s", {}).get("timestamp_osm_base", "desconocida")
    try:
        t_utc = datetime.strptime(marca, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        t_col = t_utc.astimezone(timezone(timedelta(hours=-5)))
        marca_txt = f"{marca} en UTC ({t_col:%Y-%m-%d %H:%M} hora de Colombia, UTC−5)"
    except ValueError:
        marca_txt = marca
    elementos = datos["elements"]
    print(f"OSM: {len(elementos)} elementos, marca temporal {marca_txt}")

    # consulta Overpass: se deja escrita junto a la descarga y se comprueba que el archivo la cumple
    ruta_q = os.path.join(DIR, "osm-verdes-equipamientos.overpassql")
    with open(ruta_q, "w", encoding="utf-8") as f:
        f.write("/* Consulta Overpass que produjo fuentes/osm-verdes-equipamientos.json.\n"
                "   Enviada por POST a https://overpass-api.de/api/interpreter el 2026-09-30 hacia las 20:52 hora de\n"
                f"   Colombia (marca de la base: {marca}, UTC). Respuesta: Overpass API 0.7.62.11, 'out geom'.\n"
                "   Copiada del registro de la sesión que hizo la descarga; las mismas reglas están en\n"
                "   scripts/verdes.py (CONSULTA_OVERPASS). Caja: (sur, oeste, norte, este) = rejilla común.\n"
                "   Datos © colaboradores de OpenStreetMap, ODbL 1.0. */\n")
        f.write(CONSULTA_OVERPASS.replace(";(", ";(\n  ").replace(");out", "\n);out").replace(f"{_bb};", f"{_bb};\n  ")
                .replace("\n  \n);", "\n);") + "\n")
    caja = box(BBOX[1], BBOX[0], BBOX[3], BBOX[2])
    fuera_filtro, fuera_caja = [], []
    for e in elementos:
        t = e.get("tags", {})
        if not any(t.get(k) in v for k, v in FILTROS_OVERPASS.items()):
            fuera_filtro.append(oid(e))
        if e["type"] == "node":
            dentro = caja.contains(Point(e["lon"], e["lat"]))
        elif e["type"] == "way":
            dentro = caja.intersects(LineString([(p["lon"], p["lat"]) for p in e["geometry"]])) if len(e.get("geometry", [])) > 1 else True
        else:
            dentro = any(caja.intersects(LineString([(p["lon"], p["lat"]) for p in m["geometry"]]))
                         for m in e.get("members", []) if len(m.get("geometry", [])) > 1) or not e.get("members")
        if not dentro:
            fuera_caja.append(oid(e))

    # zonas de referencia ---------------------------------------------------------
    osm = comun.osm()
    cab_osm = comun._poligono(osm["cabecera"])
    municipio = comun._poligono(osm["municipio"])
    zonas = comun.comunas()
    cab_dane, fuente_cab = None, None
    if os.path.exists(MGN_URBANA):
        fs = json.load(open(MGN_URBANA, encoding="utf-8"))["features"]
        cl1 = [shape(f["geometry"]) for f in fs if str(f["properties"].get("COD_CLAS")) == "1"]
        if cl1:
            cab_dane = poligonal(unary_union(cl1))
            fuente_cab = ("DANE, Marco Geoestadístico Nacional 2018, zona urbana clase 1 (cabecera de Cartago). Es un solo "
                          "polígono que llega hasta el área urbana de Zaragoza, así que los totales de la cabecera incluyen "
                          "a Zaragoza")
    if cab_dane is None:
        cab_dane, fuente_cab = cab_osm, "OpenStreetMap (relación 13305920), porque falta el MGN del DANE"
        PROBLEMAS.append("No se encontró el MGN 2018 del DANE; la cabecera del indicador es la de OSM")
    cab_dane_u, cab_osm_u = a_utm(cab_dane), a_utm(cab_osm)

    def comuna_de(pt):
        for z in zonas:
            if z["geom"].contains(pt):
                return z["nombre"]
        return None

    # geometrías ------------------------------------------------------------------
    geoms = {}
    for e in elementos:
        try:
            geoms[oid(e)] = geometria(e)
        except Exception as ex:  # geometría irreparable: se informa y se sigue
            PROBLEMAS.append(f"{oid(e)}: geometría no construida ({ex})")
            geoms[oid(e)] = None

    institucionales = []
    for e in elementos:
        t = e.get("tags", {})
        v = t.get("amenity") if t.get("amenity") in EQUIP else (t.get("healthcare") if t.get("healthcare") in EQUIP else None)
        g = geoms[oid(e)]
        if g is None or g.geom_type == "Point":
            continue
        if v or t.get("landuse") == "cemetery":
            institucionales.append((oid(e), t.get("name") or ("cementerio" if t.get("landuse") == "cemetery" else v), a_utm(g)))

    vias_mayores, arbol_vias = [], None
    if os.path.exists(VIAS_JSON):
        for w in json.load(open(VIAS_JSON, encoding="utf-8"))["elements"]:
            tw = w.get("tags", {})
            if w["type"] == "way" and tw.get("highway") in VIAS_MAYORES and len(w.get("geometry", [])) >= 2:
                vias_mayores.append((tw.get("name") or tw.get("ref"),
                                     a_utm(LineString([(p["lon"], p["lat"]) for p in w["geometry"]]))))
        arbol_vias = STRtree([l for _, l in vias_mayores]) if vias_mayores else None
    else:
        PROBLEMAS.append("Sin fuentes/osm-vias.json: no se pudieron reconocer separadores viales etiquetados como verde")

    # 1. espacio verde ------------------------------------------------------------
    verdes, puntos_verdes, canchas, otras = [], [], [], defaultdict(list)
    for e in elementos:
        t = e.get("tags", {})
        g = geoms[oid(e)]
        tipo = None
        if t.get("leisure") in VERDE_LEISURE:
            tipo = ("leisure", t["leisure"], VERDE_LEISURE[t["leisure"]])
        elif t.get("landuse") in VERDE_LANDUSE:
            tipo = ("landuse", t["landuse"], VERDE_LANDUSE[t["landuse"]])
        if t.get("leisure") == "pitch":
            if g is not None and g.geom_type != "Point":
                canchas.append((e, g))
            continue
        if tipo is None:
            for k, vals in (("landuse", ("grass", "cemetery", "forest", "meadow")), ("natural", ("wood", "scrub", "wetland"))):
                if t.get(k) in vals and g is not None and g.geom_type != "Point":
                    otras[f"{k}={t[k]}"].append((e, g))
            continue
        if g is None:
            PROBLEMAS.append(f"{oid(e)} ({tipo[0]}={tipo[1]}): sin geometría de área")
            continue
        if g.geom_type == "Point":
            puntos_verdes.append({"osm_id": oid(e), "tipo": f"{tipo[0]}={tipo[1]}", "nombre": t.get("name"),
                                  "lat": round(g.y, 6), "lon": round(g.x, 6),
                                  "etiquetas": {k: v for k, v in t.items() if k not in ("name",)}})
            continue
        gu = a_utm(g)
        acc = (t.get("access") or "").lower()
        gtype = (t.get("garden:type") or "").lower()
        nota = []
        tarifa = False
        if oid(e) in EXCLUSIONES:
            ex = EXCLUSIONES[oid(e)]
            acceso, publico, tarifa = ex["acceso"], False, True
            nota.append(f"{ex['evidencia']} Fuente: {ex['url']}")
        elif acc in ("private", "no") or gtype in ("private", "residential"):
            acceso, publico = "privado (access=private)" if acc else f"privado (garden:type={gtype})", False
        else:
            dentro = None
            for iid, inom, ig in institucionales:
                if ig.intersects(gu) and ig.intersection(gu).area >= 0.5 * gu.area:
                    dentro = (iid, inom)
                    break
            if dentro:
                acceso, publico = f"institucional (dentro de {dentro[1]}, {dentro[0]})", False
            elif acc in ("customers", "members", "permit", "destination", "permissive"):
                acceso, publico = f"restringido (access={acc})", False
            elif acc in ("yes", "public"):
                acceso, publico = f"público (access={acc})", True
            else:
                acceso, publico = "no declarado en OSM (se asume público)", True
        separador = None
        if publico and arbol_vias is not None:
            idx = arbol_vias.query(gu.buffer(SEP_DIST_M + 5))
            if len(idx):
                zona = unary_union([vias_mayores[i][1] for i in idx]).buffer(SEP_DIST_M)
                borde = gu.boundary
                f_borde = borde.intersection(zona).length / borde.length
                ancho = 2 * gu.area / gu.length
                if f_borde >= SEP_BORDE and ancho < SEP_ANCHO_M:
                    nombres_v = sorted({vias_mayores[i][0] for i in idx
                                        if vias_mayores[i][0] and vias_mayores[i][1].distance(gu) <= SEP_DIST_M})
                    separador = {"borde_junto_a_via_pct": round(100 * f_borde), "ancho_medio_m": round(ancho, 1),
                                 "vias": nombres_v}
                    acceso, publico = (f"separador o franja vial (ancho medio ≈ {ancho:.1f} m; {round(100 * f_borde)} % del "
                                       f"borde a ≤ {SEP_DIST_M} m de vías principales); no es espacio recreativo"), False
                    nota.append("vías contiguas: " + (", ".join(nombres_v) if nombres_v else "sin nombre en OSM"))
        if gtype == "community":
            nota.append("huerta comunitaria (garden:type=community)")
        if t.get("place") == "square":
            nota.append("también etiquetada place=square: plaza, probablemente con superficie dura")
        rp = g.representative_point()
        verdes.append({
            "e": e, "g": g, "gu": gu, "publico": publico, "separador": separador, "tarifa": tarifa,
            "props": {
                "osm_id": oid(e), "osm_url": f"https://www.openstreetmap.org/{oid(e)}",
                "nombre": t.get("name") or t.get("loc_name"),
                "tipo": f"{tipo[0]}={tipo[1]}", "tipo_es": tipo[2],
                "area_m2": round(gu.area, 1), "acceso": acceso, "access_osm": t.get("access"),
                "publico": publico,
                "en_cabecera": bool(cab_dane.contains(rp)),
                "comuna": comuna_de(rp),
                "municipio": "Cartago" if municipio.contains(rp) else "otro municipio",
                "nota": "; ".join(nota) or None,
            }})

    # 2. componentes del verde público --------------------------------------------
    pub = [v for v in verdes if v["publico"]]
    union_pub = unary_union([v["gu"] for v in pub])
    comps_g = componentes_de([v["gu"] for v in pub])
    arbol_c = STRtree(comps_g)
    componentes = []
    for k, g in enumerate(comps_g):
        componentes.append({"id": k + 1, "gu": g, "area_m2": g.area, "miembros": []})
    for v in pub:
        idx = arbol_c.query(v["gu"].representative_point(), predicate="intersects")
        k = int(idx[0]) if len(idx) else int(arbol_c.query_nearest(v["gu"].representative_point())[0])
        componentes[k]["miembros"].append(v)
    for c in componentes:
        c["nombres"] = sorted({v["props"]["nombre"] for v in c["miembros"] if v["props"]["nombre"]})
        c["n_poligonos"] = len(c["miembros"])
        for v in c["miembros"]:
            v["props"].update({"componente": c["id"], "componente_area_m2": round(c["area_m2"], 1),
                               "componente_ge_05ha": c["area_m2"] >= UMBRAL_HA * 1e4,
                               "componente_ge_1ha": c["area_m2"] >= UMBRAL_HA_ALT * 1e4})
    for v in verdes:
        if not v["publico"]:
            v["props"].update({"componente": None, "componente_area_m2": None,
                               "componente_ge_05ha": False, "componente_ge_1ha": False})

    def mayores(comps, ha):
        return [c for c in comps if c.area >= ha * 1e4]

    grandes = [c for c in componentes if c["area_m2"] >= UMBRAL_HA * 1e4]
    grandes1 = [c for c in componentes if c["area_m2"] >= UMBRAL_HA_ALT * 1e4]
    print(f"Verde: {len(verdes)} polígonos candidatos, {len(pub)} públicos, {len(componentes)} componentes, "
          f"{len(grandes)} ≥ {UMBRAL_HA} ha, {len(grandes1)} ≥ {UMBRAL_HA_ALT} ha")

    # 3. distancias -----------------------------------------------------------------
    lat, lon = comun.centros_celdas()
    x, y = A_UTM.transform(lon.ravel(), lat.ravel())
    pts = shapely.points(np.asarray(x), np.asarray(y))

    def distancia(polis):
        if not polis:
            return np.full((comun.ALTO, comun.ANCHO), np.nan, dtype=np.float32)
        arbol = STRtree(polis)
        _, dist = arbol.query_nearest(pts, return_distance=True, all_matches=False)
        return dist.reshape(comun.ALTO, comun.ANCHO).astype(np.float32)

    d05 = distancia([c["gu"] for c in grandes])
    d1 = distancia([c["gu"] for c in grandes1])
    d025 = distancia(mayores(comps_g, UMBRAL_HA_UA))
    dtodos = distancia(comps_g)
    assert np.isfinite(d05).all(), "distancia con NaN"

    # 4. equipamientos ----------------------------------------------------------------
    candidatos = []
    for e in elementos:
        t = e.get("tags", {})
        v = t.get("amenity") if t.get("amenity") in EQUIP else (t.get("healthcare") if t.get("healthcare") in EQUIP else None)
        if v is None:
            continue
        sub = v
        if v == "social_facility" and t.get("social_facility") in ("nursing_home",):
            sub = "nursing_home"
        g = geoms[oid(e)]
        if g is None:
            PROBLEMAS.append(f"{oid(e)} ({v}): sin geometría; no se incluye")
            continue
        if g.geom_type == "Point":
            pt, area, origen = g, 0.0, "nodo"
        else:
            pt = g.centroid if g.contains(g.centroid) else g.representative_point()
            area, origen = a_utm(g).area, "área"
        candidatos.append({"e": e, "g": g, "pt": pt, "ptu": a_utm(pt), "area": area, "origen": origen,
                           "categoria": EQUIP[sub], "subtipo": sub, "nombre": t.get("name"),
                           "operador": t.get("operator"), "fusionados": [], "motivos": []})
    candidatos.sort(key=lambda c: -c["area"])
    vivos = []
    for c in candidatos:
        madre = None
        for m in vivos:
            if m["origen"] == "área" and m["subtipo"] == c["subtipo"] and m["area"] > c["area"] and m["g"].contains(c["pt"]):
                madre = m
                break
        if madre:
            madre["fusionados"].append(oid(c["e"]))
            madre["motivos"].append(f"{oid(c['e'])} dentro del área")
            if not madre["nombre"] and c["nombre"]:
                madre["nombre"] = c["nombre"]
            continue
        vivos.append(c)
    finales = []
    for c in vivos:
        dup = None
        n = normalizar(c["nombre"])
        if n:
            for m in finales:
                if m["categoria"] == c["categoria"] and normalizar(m["nombre"]) == n and m["ptu"].distance(c["ptu"]) < DUP_M:
                    dup = m
                    break
        if dup:
            dup["fusionados"].append(oid(c["e"]))
            dup["motivos"].append(f"{oid(c['e'])} mismo nombre a {dup['ptu'].distance(c['ptu']):.0f} m")
            continue
        finales.append(c)
    arbol05 = STRtree([c["gu"] for c in grandes])
    for c in finales:
        _, dd = arbol05.query_nearest(c["ptu"], return_distance=True)
        c["dist_verde"] = float(dd[0])
        c["municipio"] = "Cartago" if municipio.contains(c["pt"]) else "otro municipio"
        c["en_cabecera"] = bool(cab_dane.contains(c["pt"]))
    feats_eq = []
    for c in sorted(finales, key=lambda c: (c["categoria"], c["subtipo"], normalizar(c["nombre"]) or "~")):
        feats_eq.append(feature(c["pt"], {
            "categoria": c["categoria"], "categoria_es": CATEGORIA_ES[c["categoria"]],
            "subtipo": c["subtipo"], "subtipo_es": SUBTIPO_ES[c["subtipo"]],
            "nombre": c["nombre"], "osm_id": oid(c["e"]), "osm_url": f"https://www.openstreetmap.org/{oid(c['e'])}",
            "geometria_origen": c["origen"], "area_m2": round(c["area"], 1) if c["area"] else None,
            "operador": c["operador"], "municipio": c["municipio"],
            "comuna": comuna_de(c["pt"]), "en_cabecera": c["en_cabecera"],
            "dist_verde_publico_05ha_m": round(c["dist_verde"]),
            "fusionados": c["fusionados"] or None, "motivo_fusion": "; ".join(c["motivos"]) or None,
        }))
    print(f"Equipamientos: {len(candidatos)} elementos OSM → {len(finales)} tras eliminar duplicados")

    # cobertura de OSM frente a fuentes oficiales (solo conteos agregados) ----------------
    men = socrata("men_establecimientos_cartago", "cfw5-qzt5", {
        "$select": "a_o,sector,count(*) AS establecimientos,sum(cantidad_sedes) AS sedes",
        "$where": "cod_dane_municipio='76147'", "$group": "a_o,sector", "$order": "a_o"})
    reps = socrata("reps_sedes_cartago", "c36g-9fc2", {
        "$select": "claseprestador,naturalezajuridica,fecha_corte_reps,count(*) AS sedes",
        "$where": "municipiosede='76147'", "$group": "claseprestador,naturalezajuridica,fecha_corte_reps"})
    fin_cart = [c for c in finales if c["municipio"] == "Cartago"]
    n_esc_cart = sum(c["subtipo"] in ("school", "kindergarten") for c in fin_cart)
    n_esc_cab = sum(c["subtipo"] in ("school", "kindergarten") for c in fin_cart if c["en_cabecera"])
    n_sup_cart = sum(c["subtipo"] in ("university", "college") for c in fin_cart)
    n_sal_cart = sum(c["categoria"] == "salud" for c in fin_cart)
    n_doc_cart = sum(c["subtipo"] in ("doctors", "doctor") for c in fin_cart)
    cobertura_eq = {"nota": "Conteos de OSM (municipio de Cartago, tras deduplicar) frente a registros oficiales. Un punto de "
                            "OSM no equivale siempre a una sede: la razón es una estimación gruesa de cobertura, no un cruce "
                            "uno a uno."}
    if men:
        filas = men["filas"]
        ult = max(int(f["a_o"]) for f in filas)
        sedes_men = sum(int(f["sedes"]) for f in filas if int(f["a_o"]) == ult)
        cobertura_eq["educacion_men"] = {
            "fuente": "MEN, MEN_ESTABLECIMIENTOS_EDUCATIVOS_PREESCOLAR_BÁSICA_Y_MEDIA (datos.gov.co cfw5-qzt5, CC BY-SA 4.0)",
            "consulta": men["consulta"], "fecha_consulta": men["fecha_consulta"], "anio": ult,
            "por_sector": {f["sector"]: {"establecimientos": int(f["establecimientos"]), "sedes": int(f["sedes"])}
                           for f in filas if int(f["a_o"]) == ult},
            "sedes_total_municipio": sedes_men,
            "osm_colegios_y_jardines_municipio": n_esc_cart,
            "cobertura_osm_pct": round(100 * n_esc_cart / sedes_men) if sedes_men else None}
    urb_bol = REF_BOLETIN["sedes_oficiales_urbanas"] + REF_BOLETIN["no_oficiales_urbanos"]
    cobertura_eq["educacion_boletin_municipal"] = {
        "fuente": REF_BOLETIN["fuente"], "url": REF_BOLETIN["url"], "paginas": REF_BOLETIN["paginas"],
        "sedes_urbanas_oficiales": REF_BOLETIN["sedes_oficiales_urbanas"],
        "establecimientos_urbanos_no_oficiales": REF_BOLETIN["no_oficiales_urbanos"],
        "total_urbano": urb_bol, "osm_colegios_y_jardines_en_cabecera": n_esc_cab,
        "cobertura_osm_pct": round(100 * n_esc_cab / urb_bol),
        "educacion_superior": {"boletin_universidades": REF_BOLETIN["universidades"], "boletin_sena": REF_BOLETIN["sena"],
                               "osm_university_y_college": n_sup_cart},
        "centros_desarrollo_infantil_boletin": REF_BOLETIN["centros_desarrollo_infantil"]}
    if reps:
        filas = reps["filas"]
        por_clase = defaultdict(int)
        for f in filas:
            por_clase[f["claseprestador"]] += int(f["sedes"])
        ips = por_clase.get("Instituciones Prestadoras de Servicios de Salud - IPS", 0)
        prof = por_clase.get("Profesional Independiente", 0)
        cobertura_eq["salud_reps"] = {
            "fuente": "MinSalud, Registro Especial de Prestadores y Sedes de Servicios de Salud (datos.gov.co c36g-9fc2, "
                      "CC BY-SA 4.0)", "consulta": reps["consulta"], "fecha_consulta": reps["fecha_consulta"],
            "corte": sorted({f["fecha_corte_reps"] for f in filas}),
            "sedes_por_clase": dict(sorted(por_clase.items())),
            "sedes_ips_publicas_ese": sum(int(f["sedes"]) for f in filas if f["claseprestador"].endswith("IPS")
                                          and f["naturalezajuridica"] == "Pública"),
            "osm_salud_municipio": n_sal_cart, "osm_consultorios_municipio": n_doc_cart,
            "cobertura_osm_ips_pct": round(100 * n_sal_cart / ips) if ips else None,
            "profesionales_independientes": prof}

    # 5. vegetación intraurbana sin ningún polígono OSM (WorldCover 2021) ------------------
    from rasterio.features import rasterize, shapes
    from scipy import ndimage
    tr = comun.transformacion()
    m_dane = rasterize([(cab_dane, 1)], out_shape=(comun.ALTO, comun.ANCHO), transform=tr, fill=0, dtype="uint8").astype(bool)
    m_zonas = comun.mascara_zonas(zonas)
    area_celda = comun.area_celda_m2()
    aerodromo = comun._poligono(osm["aerodromo"])
    manchas, manchas_u = [], []
    try:
        arb = np.load(os.path.join(comun.REJILLA_NPY, "arbolado.npy"))
        pas = np.load(os.path.join(comun.REJILLA_NPY, "cob_pasto.npy"))
        con = np.load(os.path.join(comun.REJILLA_NPY, "construido.npy"))
        todos_polis = [g for g in geoms.values() if g is not None and g.geom_type != "Point"] + [aerodromo]
        mapeado = rasterize([(g, 1) for g in todos_polis], out_shape=(comun.ALTO, comun.ANCHO), transform=tr,
                            fill=0, dtype="uint8", all_touched=True).astype(bool)
        mapeado = ndimage.binary_dilation(mapeado, iterations=1)
        veg = (np.nan_to_num(arb) + np.nan_to_num(pas)) >= 50
        cand = veg & m_dane & ~mapeado
        lab, n = ndimage.label(cand, structure=np.ones((3, 3)))
        conservar = np.zeros_like(lab)
        for i in range(1, n + 1):
            mk = lab == i
            a = float(area_celda[mk].sum())
            if not (UMBRAL_HA * 1e4 <= a <= 5e4):
                continue
            anillo = ndimage.binary_dilation(mk, iterations=3) & ~mk
            if m_dane[anillo].mean() < 0.95 or np.nanmean(con[anillo]) < 70:
                continue
            conservar[mk] = i
            la, lo = float(lat[mk].mean()), float(lon[mk].mean())
            manchas.append({"etiqueta": i, "lat": round(la, 5), "lon": round(lo, 5), "area_ha": round(a / 1e4, 2),
                            "construido_alrededor_pct": round(float(np.nanmean(con[anillo]))),
                            "comuna": comuna_de(Point(lo, la)),
                            "dist_verde_publico_05ha_m": round(float(d05[mk].min()))})
        if manchas:
            pol_m = defaultdict(list)
            for gj, val in shapes(conservar.astype(np.int32), mask=conservar > 0, transform=tr, connectivity=8):
                pol_m[int(val)].append(shape(gj))
            manchas_u = [a_utm(unary_union(ps)) for _, ps in sorted(pol_m.items())]
        manchas.sort(key=lambda m: -m["area_ha"])
        for m in manchas:
            m.pop("etiqueta")
    except FileNotFoundError as ex:
        PROBLEMAS.append(f"Sin capas WorldCover para la pista de vegetación sin mapear ({ex}); se omite el escenario (a)")

    # 6. población ---------------------------------------------------------------------
    pob_cab, anio_pob = None, None
    if os.path.exists(SERIE_POB):
        sp = json.load(open(SERIE_POB, encoding="utf-8"))
        anios = sp.get("dane_serie_cartago", {}).get("anios", {})
        if "2026" in anios:
            pob_cab, anio_pob = anios["2026"]["cabecera"], 2026
    if pob_cab is None:
        PROBLEMAS.append("Sin población DANE de la cabecera: no se calcula m²/hab")
    pob = None
    try:
        pob = np.nan_to_num(comun.cargar_capa("poblacion").astype(np.float64))
    except Exception as ex:
        PROBLEMAS.append(f"Capa 'poblacion' no disponible ({ex}): no se calcula el indicador ponderado por población")

    def cobertura(mask, dist, umbral):
        r = {"celdas_pct": round(100 * float((dist[mask] <= umbral).mean()), 1)}
        if pob is not None:
            p = pob[mask]
            tot = p.sum()
            if tot > 0:
                r["poblacion_pct"] = round(100 * float(p[dist[mask] <= umbral].sum() / tot), 1)
                r["poblacion_hab"] = int(round(float(p[dist[mask] <= umbral].sum())))
                r["poblacion_total_hab"] = int(round(float(tot)))
        return r

    acceso = {"cabecera_dane": {f"{u}m_{h}ha": cobertura(m_dane, dd, u)
                                for (h, dd) in (("0.25", d025), ("0.5", d05), ("1", d1), ("cualquiera", dtodos))
                                for u in (200, 300, 500)}}

    # 7. sensibilidad -----------------------------------------------------------------
    tarifa_u = [v["gu"] for v in verdes if v["tarifa"]]
    bosques = [(e, a_utm(g)) for k in ("natural=wood", "natural=scrub", "landuse=forest") for e, g in otras.get(k, [])]
    bosques_sel = [(e, gu) for e, gu in bosques if gu.area >= UMBRAL_HA * 1e4 and gu.intersects(cab_dane_u)]
    g05 = [c["gu"] for c in grandes]
    comps_c = componentes_de([v["gu"] for v in pub] + tarifa_u)
    escenarios = {
        "base_05ha": ("Verde público de OSM, componentes ≥ 0,5 ha (capa publicada)", d05),
        "umbral_025ha": ("Componentes ≥ 0,25 ha (unidad mínima de Urban Atlas)", d025),
        "umbral_1ha": ("Componentes ≥ 1 ha (indicador adicional de la OMS)", d1),
        "sin_umbral": ("Cualquier tamaño (incluye jardineras de decenas de m²)", dtodos),
    }
    for m2 in (500, 1000):
        escenarios[f"minimo_{m2}m2"] = (f"Componentes ≥ {m2} m²", distancia(mayores(comps_g, m2 / 1e4)))
    if manchas_u:
        escenarios["a_manchas_worldcover"] = (
            f"(a) Base + {len(manchas_u)} manchas de vegetación intraurbana de WorldCover sin mapear, como si fueran parques "
            "públicos (cota superior: la OMS excluye vegetación sin manejo como área verde urbana)", distancia(g05 + manchas_u))
    if bosques_sel:
        escenarios["b_bosques_osm"] = (
            f"(b) Base + {len(bosques_sel)} polígonos OSM natural=wood/scrub o landuse=forest ≥ 0,5 ha que tocan la cabecera "
            "(la OMS los incluye solo si lindan con ciudad por dos lados y tienen uso recreativo; no verificado)",
            distancia(g05 + [gu for _, gu in bosques_sel]))
    if tarifa_u:
        escenarios["c_con_tarifa"] = ("(c) Verde público + centros recreativos con tarifa (Villasol y Mister Mojarra), ≥ 0,5 ha",
                                      distancia(mayores(comps_c, UMBRAL_HA)))
    if manchas_u and bosques_sel and tarifa_u:
        escenarios["abc_juntos"] = ("(a+b+c) Los tres escenarios juntos (cota superior)",
                                    distancia(mayores(comps_c, UMBRAL_HA) + manchas_u + [gu for _, gu in bosques_sel]))
    sens_cab = {k: {"descripcion": d, **cobertura(m_dane, dd, DIST_OMS)} for k, (d, dd) in escenarios.items()}
    ESC_RANGO = [k for k in escenarios if k not in ("sin_umbral", "minimo_500m2", "minimo_1000m2")]
    vals_r = [sens_cab[k].get("poblacion_pct", sens_cab[k]["celdas_pct"]) for k in ESC_RANGO]
    rango_cab = [min(vals_r), max(vals_r)]

    # 8. por zona ---------------------------------------------------------------------
    por_zona = []
    for z in zonas:
        mk = m_zonas == z["indice"]
        zu = a_utm(z["geom"])
        a = union_pub.intersection(zu).area
        r = {"id": z["id"], "nombre": z["nombre"], "area_verde_publica_m2": round(a),
             "parques_ge_05ha_que_tocan": sum(1 for c in grandes if c["gu"].intersects(zu)),
             "distancia_mediana_celdas_m": round(float(np.median(d05[mk]))) if mk.any() else None,
             "distancia_p90_celdas_m": round(float(np.percentile(d05[mk], 90))) if mk.any() else None}
        if pob is not None and mk.any():
            md = mediana_ponderada(d05[mk], pob[mk])
            r["distancia_mediana_poblacion_m"] = round(md) if md is not None else None
        r.update({"acceso_300m_05ha": cobertura(mk, d05, DIST_OMS),
                  "canchas": sum(1 for _, g in canchas if z["geom"].contains(g.representative_point())),
                  "equipamientos_osm": dict(Counter(c["categoria"] for c in finales if z["geom"].contains(c["pt"])))})
        if pob is not None and mk.any():
            ph = float(pob[mk].sum())
            r["poblacion_capa_hab"] = int(round(ph))
            r["m2_verde_publico_por_hab"] = round(a / ph, 2) if ph > 0 else None
        sz = {k: cobertura(mk, dd, DIST_OMS).get("poblacion_pct") for k, (_, dd) in escenarios.items()}
        r["sensibilidad_300m_poblacion_pct"] = sz
        vz = [sz[k] for k in ESC_RANGO if sz.get(k) is not None]
        r["sensibilidad_rango_pct"] = [min(vz), max(vz)] if vz else None
        por_zona.append(r)

    def orden(clave):
        vals = [(z["sensibilidad_300m_poblacion_pct"].get(clave), z["nombre"]) for z in por_zona]
        vals = [v for v in vals if v[0] is not None]
        return [n for _, n in sorted(vals, key=lambda v: (-v[0], v[1]))]

    ordenes = {k: orden(k) for k in escenarios}
    posiciones = {z["nombre"]: [ordenes[k].index(z["nombre"]) + 1 for k in ESC_RANGO if z["nombre"] in ordenes[k]]
                  for z in por_zona}
    for z in por_zona:
        p = posiciones[z["nombre"]]
        z["posicion_base"] = ordenes["base_05ha"].index(z["nombre"]) + 1 if z["nombre"] in ordenes["base_05ha"] else None
        z["posicion_min_max_escenarios"] = [min(p), max(p)] if p else None
    cambios_orden = {k: ordenes[k] != ordenes["base_05ha"] for k in ESC_RANGO}

    # 9. salidas vectoriales ------------------------------------------------------------
    atrib = "© colaboradores de OpenStreetMap, ODbL 1.0 (https://www.openstreetmap.org/copyright)"
    fuente_osm = {"nombre": "OpenStreetMap (Overpass, out geom)", "url": "https://www.openstreetmap.org/copyright",
                  "licencia": "ODbL 1.0", "cita": atrib,
                  "consulta_overpass": CONSULTA_OVERPASS, "consulta_archivo": "fuentes/verdes/osm-verdes-equipamientos.overpassql"}
    periodo_osm = f"Estado de OpenStreetMap en la marca {marca_txt}"
    pub_cab = [v for v in pub if v["props"]["en_cabecera"]]
    sin_nom = [v for v in pub_cab if not v["props"]["nombre"]]
    sin_acc = [v for v in pub if v["props"]["access_osm"] is None]
    mini = sorted(c.area for c in comps_g)
    lim_verde = [
        "Inventario parcial: solo cuenta lo mapeado en OpenStreetMap. WorldCover 2021 muestra "
        f"{len(manchas)} manchas de vegetación de 0,5–5 ha rodeadas de ciudad sin ningún polígono OSM (ver "
        "datos/series/verdes.json, vacios_osm); un parque sin mapear no aparece.",
        f"Acceso supuesto: {len(sin_acc)} de {len(pub)} polígonos públicos no tienen etiqueta 'access' en OSM y se asumieron "
        "públicos; zonas verdes internas de conjuntos cerrados mal etiquetadas se contarían como públicas.",
        "Las exclusiones (institucionales, con tarifa y separadores viales) siguen reglas propias documentadas en 'criterios' "
        "y en 'nota'; no son una clasificación oficial.",
        "El área es la del polígono OSM: puede incluir senderos, plazoletas duras y canchas internas no separadas.",
        "No equivale al espacio público efectivo del Decreto 1504 de 1998 ni al inventario municipal (que incluye plazas).",
        f"Hay polígonos muy pequeños (jardineras de {round(mini[0])}–{round(mini[3])} m²) que cuentan como verde de cualquier "
        "tamaño, pero no en los indicadores con umbral.",
        "Incluye polígonos fuera del municipio de Cartago (municipio='otro municipio', p. ej. Puerto Caldas, Pereira).",
        "No mide calidad, sombra, seguridad ni dotación de los parques.",
    ]
    feats_v = [feature(v["g"], v["props"]) for v in sorted(verdes, key=lambda v: -v["props"]["area_m2"])]
    escribir_geojson(os.path.join(VECTORES, "espacio_verde.geojson"), feats_v, {
        "titulo": "Espacio verde de uso público (OpenStreetMap)",
        "descripcion": "Parques, zonas de juego, zonas recreativas y jardines mapeados en OpenStreetMap, con su área y "
                       "acceso. 'publico' indica si entra en el indicador de acceso al verde.",
        "fuente": fuente_osm, "periodo": periodo_osm,
        "crs": "EPSG:4326", "area_calculada_en": "EPSG:32618 (UTM 18N)",
        "criterios": ["leisure=park|playground|recreation_ground|nature_reserve|garden; landuse=recreation_ground|village_green",
                      "canchas (leisure=pitch) excluidas; se cuentan en datos/series/verdes.json",
                      "publico=false: access=private/no, garden:type privado, ≥50 % dentro de un equipamiento o cementerio, "
                      "o tarifa verificada externamente (ver 'nota')",
                      "publico=false también para separadores viales: ≥ 90 % del borde a ≤ 10 m de vías principales y ancho "
                      "medio 2·A/P < 10 m (Urban Atlas 14100: ancho mínimo 10 m, uso recreativo; OMS 2016, recuadro 4.1)"],
        "limitaciones": lim_verde})

    cob_txt = []
    if "educacion_men" in cobertura_eq:
        em = cobertura_eq["educacion_men"]
        cob_txt.append(f"Educación: OSM tiene {n_esc_cart} colegios o jardines en el municipio de Cartago frente a "
                       f"{em['sedes_total_municipio']} sedes de preescolar, básica y media del MEN ({em['anio']}), una "
                       f"cobertura de ≈ {em['cobertura_osm_pct']} %. En la cabecera, {n_esc_cab} frente a {urb_bol} sedes urbanas "
                       f"(29 oficiales y 24 no oficiales, Boletín Estadístico municipal 2023): ≈ "
                       f"{cobertura_eq['educacion_boletin_municipal']['cobertura_osm_pct']} %.")
    if "salud_reps" in cobertura_eq:
        sr = cobertura_eq["salud_reps"]
        cob_txt.append(f"Salud: OSM tiene {n_sal_cart} puntos de salud en Cartago frente a "
                       f"{sr['sedes_por_clase'].get('Instituciones Prestadoras de Servicios de Salud - IPS', 0)} sedes de IPS "
                       f"habilitadas en el REPS (corte {corte_txt(sr['corte'][0])}), ≈ "
                       f"{sr['cobertura_osm_ips_pct']} %, más {sr['profesionales_independientes']} profesionales independientes "
                       f"(OSM: {n_doc_cart} consultorios).")
    lim_eq = [
        "Cobertura parcial: los conteos son 'mapeados en OSM', no un inventario. " + " ".join(cob_txt),
        "Un punto por equipamiento (centroide o punto representativo del área): no representa linderos, accesos ni la "
        "población atendida; un área OSM puede agrupar varias sedes y una sede puede faltar.",
        "La consulta Overpass no pidió healthcare=*: los consultorios etiquetados solo con healthcare quedan fuera.",
        "La categoría sale de las etiquetas OSM, que a veces son dudosas (p. ej. un puesto de salud etiquetado hospital, una "
        "escuela de aviación etiquetada school) y los nombres pueden estar desactualizados (ver vacios_osm en "
        "datos/series/verdes.json).",
        "Incluye equipamientos fuera del municipio de Cartago (municipio='otro municipio', p. ej. Puerto Caldas, Pereira).",
        "dist_verde_publico_05ha_m depende de los mismos supuestos de la capa distancia_verde (verde mapeado, acceso supuesto).",
    ]
    escribir_geojson(os.path.join(VECTORES, "equipamientos.geojson"), feats_eq, {
        "titulo": "Equipamientos sensibles mapeados en OpenStreetMap",
        "descripcion": "Colegios, universidades, centros de salud, hogares de cuidado, bomberos, policía y alcaldía "
                       "mapeados en OpenStreetMap; un punto por equipamiento. Es un inventario incompleto.",
        "fuente": fuente_osm, "periodo": periodo_osm, "crs": "EPSG:4326",
        "criterios": ["áreas → centroide (punto representativo si el centroide cae fuera)",
                      "duplicados: punto dentro de un área del mismo subtipo; mismo nombre y categoría a < 50 m",
                      "dist_verde_publico_05ha_m: distancia en línea recta (UTM 18N) al borde del verde público ≥ 0,5 ha"],
        "cobertura_frente_a_registros_oficiales": cobertura_eq,
        "limitaciones": lim_eq})

    # 10. capa raster ----------------------------------------------------------------------
    nombres_esc = {"base_05ha": "base (≥ 0,5 ha)", "umbral_025ha": "≥ 0,25 ha", "umbral_1ha": "≥ 1 ha",
                   "sin_umbral": "cualquier tamaño", "a_manchas_worldcover": "(a) + vegetación sin mapear",
                   "b_bosques_osm": "(b) + bosques OSM", "c_con_tarifa": "(c) + centros con tarifa",
                   "abc_juntos": "(a+b+c)"}
    sens_txt = "; ".join(f"{nombres_esc.get(k, k)} {coma(sens_cab[k].get('poblacion_pct'))} %" for k in sens_cab
                         if k in nombres_esc)
    leyenda = [{"desde": a, "hasta": b, "etiqueta": et,
                "color": color_visor((a + (b if b is not None else 700)) / 2 if b is not None else 650)}
               for a, b, et in CLASES_LEYENDA]
    meta = {
        "titulo": "Distancia al espacio verde público (≥ 0,5 ha)",
        "descripcion": "Metros en línea recta desde cada punto hasta el borde del parque o zona verde pública de al menos "
                       "media hectárea más cercano, según lo mapeado en OpenStreetMap. La OMS (2016) propone como indicador "
                       "la proporción de la población que vive a 300 m o menos de uno (unos 5 minutos a pie).",
        "unidad": "m",
        "fuente": {"nombre": "OpenStreetMap: parques, zonas de juego, zonas recreativas y jardines públicos",
                   "url": "https://www.openstreetmap.org/copyright", "licencia": "ODbL 1.0", "cita": atrib,
                   "consulta_overpass": CONSULTA_OVERPASS},
        "referencias": [
            {"cita": "WHO Regional Office for Europe (2016). Urban green spaces and health. A review of evidence. "
                     "Copenhague: WHO Regional Office for Europe. Secciones 3.6.2 (p. 30-31), 4.1 (p. 32), 4.3.2 "
                     "(p. 36) y 4.4 (p. 39); recuadro 4.1 (p. 33).",
             "url": "https://www.who.int/europe/publications/i/item/WHO-EURO-2016-3352-43111-60341"},
        ],
        "periodo": periodo_osm,
        "resolucion_original_m": None,
        "resolucion_nota": "Datos vectoriales: sin resolución de píxel. La distancia se calcula de forma exacta desde el centro "
                           "de cada celda de la rejilla (≈27,7 m).",
        "procesamiento": [
            "Descarga Overpass (consulta en fuente.consulta_overpass y en fuentes/verdes/osm-verdes-equipamientos.overpassql).",
            "Ensamblaje de polígonos OSM: ways cerrados y relaciones multipolygon (anillos outer cosidos con linemerge, menos inner).",
            "Selección de verde: leisure=park, playground, recreation_ground, nature_reserve, garden; landuse=recreation_ground, "
            "village_green. Se excluyen canchas (leisure=pitch), cementerios, landuse=grass y coberturas naturales.",
            "Acceso: fuera del indicador access=private/no, jardines con ≥ 50 % de su área dentro de un equipamiento "
            "(colegio, hogar, clínica…), dos centros recreativos con tarifa verificada (Villasol de Comfenalco y Mister Mojarra) "
            "y los separadores viales etiquetados como jardín (franjas de ancho medio < 10 m con ≥ 90 % del borde junto a vías "
            "principales; Urban Atlas 14100 exige 10 m de ancho mínimo, OMS 2016, recuadro 4.1).",
            f"Unión en UTM 18N (EPSG:32618) con cierre morfológico de {CIERRE_M} m; componentes conexos; se conservan los de "
            f"área ≥ {UMBRAL_HA} ha (umbral principal de la OMS 2016).",
            "Distancia euclidiana exacta desde el centro de cada celda al borde del componente más cercano (0 dentro del parque), "
            "con shapely STRtree.query_nearest; redondeo a 1 m.",
            "Sensibilidad: el mismo cálculo con umbrales de 0,25 y 1 ha y con verde sin mapear o no incluido (ver 'sensibilidad').",
        ],
        "limitaciones": [
            "Depende de lo mapeado en OpenStreetMap: un parque que no está en el mapa no cuenta y aumenta la distancia. "
            f"La proporción de la cabecera a ≤ 300 m va de {coma(rango_cab[0])} % a {coma(rango_cab[1])} % según el umbral de tamaño y el "
            "verde sin mapear o no incluido (ver 'sensibilidad').",
            "El orden de las comunas es 'según lo mapeado en OSM' y puede invertirse con otros supuestos: comunas sin parques "
            "mapeados de ≥ 0,5 ha (1, 2 y 3) suben mucho si se cuenta la vegetación sin mapear o los bosques. Antes de usarlo "
            "para priorizar inversión, contrastarlo con el inventario municipal de espacio público (diagnóstico del POT).",
            "Distancia en línea recta, como propone la OMS: no considera calles, puentes ni barreras. Al otro lado del río La Vieja "
            "(Puerto Caldas, Pereira) o del Cauca la distancia real a pie puede ser mucho mayor.",
            "Se asume público todo parque sin etiqueta de acceso; parques internos de conjuntos cerrados mal etiquetados "
            "se contarían como públicos.",
            "No mide calidad, sombra, seguridad ni equipamiento de los parques; una plazoleta etiquetada como parque cuenta igual.",
            "En la zona rural el valor es grande por definición y no indica falta de naturaleza: el indicador de la OMS es urbano.",
            "Solo se usaron elementos dentro del área descargada de OSM: en los bordes de la rejilla puede haber parques "
            "cercanos fuera de la descarga.",
            "Colores: el visor interpola entre 0 y 600 m; desde 600 m todo se ve del mismo rojo. El valor exacto está en la capa.",
        ],
        "rango_visual": RANGO_VISUAL,
        "paleta": PALETA,
        "paleta_nota": "Paleta divergente con el centro (#ffffbf) en 300 m, el criterio de la OMS: verdes por debajo; amarillo, "
                       "naranja y rojo por encima. Paradas cada 150 m.",
        "leyenda_clases": leyenda,
        "interpretacion": "≤ 300 m (verdes): cumple el criterio de acceso de la OMS (Oficina Regional para Europa, 2016): estar "
                          "a 300 m en línea recta o menos del borde de un espacio verde público de al menos 0,5 ha (unos 5 min "
                          "a pie). 300–500 m (amarillo a naranja): fuera del criterio; la OMS sugiere analizar también 200 y "
                          "500 m y reconoce que no hay consenso sobre la distancia ligada a beneficios en salud. > 500 m "
                          "(naranja rojizo a rojo): sin verde público de ≥ 0,5 ha mapeado a menos de 500 m; puede haber parques "
                          "más pequeños o verde sin mapear cerca. Es un umbral de planificación urbana, no un umbral clínico.",
        "umbrales": [{"valor": 200, "etiqueta": "200 m (análisis adicional, OMS 2016)"},
                     {"valor": DIST_OMS, "etiqueta": "criterio OMS 2016 (300 m, ≥ 0,5 ha)"},
                     {"valor": 500, "etiqueta": "500 m (análisis adicional, OMS 2016)"}],
        "sensibilidad": {
            "indicador": "población de la cabecera DANE (incluye Zaragoza) a ≤ 300 m, %",
            "resumen": sens_txt,
            "rango_pct": rango_cab,
            "escenarios": {k: {"descripcion": v["descripcion"], "poblacion_pct": v.get("poblacion_pct"),
                               "celdas_pct": v["celdas_pct"]} for k, v in sens_cab.items()},
            "detalle_por_comuna": "datos/series/verdes.json → sensibilidad",
        },
        "variantes": {
            "distancia_verde_todos": "fuentes/rejilla/distancia_verde_todos.npy: a cualquier componente de verde público, sin "
                                     f"umbral de tamaño; incluye jardineras de {round(mini[0])}–{round(mini[3])} m² que no son "
                                     "espacio verde utilizable. Para comparar, preferir distancia_verde_025ha.",
            "distancia_verde_025ha": "fuentes/rejilla/distancia_verde_025ha.npy: a componentes ≥ 0,25 ha (unidad mínima de "
                                     "Urban Atlas, OMS 2016, recuadro 4.1).",
        },
    }
    est = comun.guardar_capa("distancia_verde", d05.astype(np.float64), 1, 0, meta)
    np.save(os.path.join(comun.REJILLA_NPY, "distancia_verde_todos.npy"), dtodos.astype(np.float32))
    np.save(os.path.join(comun.REJILLA_NPY, "distancia_verde_025ha.npy"), d025.astype(np.float32))

    # 11. hallazgos -----------------------------------------------------------------------
    area_pub_dane = union_pub.intersection(cab_dane_u).area
    area_pub_osm = union_pub.intersection(cab_osm_u).area
    area_05_dane = unary_union(g05).intersection(cab_dane_u).area if grandes else 0.0
    canchas_u = unary_union([a_utm(g) for _, g in canchas]) if canchas else None
    cancha_en_parque = canchas_u.intersection(union_pub).intersection(cab_dane_u).area if canchas_u is not None else 0.0
    seps = [v for v in verdes if v["separador"]]
    area_sep_dane = unary_union([v["gu"] for v in seps]).intersection(cab_dane_u).area if seps else 0.0
    z_zar = [z for z in zonas if z["id"] == "zaragoza"]
    nota_zaragoza = None
    if z_zar:
        mz = m_zonas == z_zar[0]["indice"]
        nota_zaragoza = {
            "nota": "Según el MGN 2018 del DANE, la cabecera (clase 1) es un solo polígono que incluye el área urbana de "
                    "Zaragoza. Los totales de 'cabecera DANE' (área verde, población 139.614 hab, m²/hab y acceso) incluyen a "
                    "Zaragoza; en 'por_zona' Zaragoza aparece aparte.",
            "celdas_zaragoza": int(mz.sum()), "celdas_zaragoza_dentro_de_la_cabecera_dane": int((mz & m_dane).sum()),
            "poblacion_capa_zaragoza_dentro_de_la_cabecera_dane": int(round(float(pob[mz & m_dane].sum()))) if pob is not None else None,
            "area_verde_publica_zaragoza_dentro_de_la_cabecera_dane_m2": round(
                union_pub.intersection(a_utm(z_zar[0]["geom"])).intersection(cab_dane_u).area)}

    cancha_info = []
    for e, g in canchas:
        t = e.get("tags", {})
        gu = a_utm(g)
        cancha_info.append({"osm_id": oid(e), "nombre": t.get("name"), "deporte": t.get("sport"), "access": t.get("access"),
                            "area_m2": round(gu.area), "en_cabecera": bool(cab_dane.contains(g.representative_point())),
                            "dentro_de_verde_publico": bool(union_pub.intersection(gu).area >= 0.5 * gu.area),
                            "municipio": "Cartago" if municipio.contains(g.representative_point()) else "otro municipio",
                            "nota": CLUBES[oid(e)]["nota"] + " (" + CLUBES[oid(e)]["url"] + ")" if oid(e) in CLUBES else None})

    otras_res = {}
    for k, lst in sorted(otras.items()):
        polis = [a_utm(g) for _, g in lst]
        otras_res[k] = {"n": len(lst), "area_total_m2": round(sum(p.area for p in polis)),
                        "area_en_cabecera_m2": round(unary_union(polis).intersection(cab_dane_u).area)}

    cnt_cat = Counter(c["categoria"] for c in finales)
    cnt_sub = Counter(f"{c['categoria']}/{c['subtipo']}" for c in finales)
    cnt_cat_cartago = Counter(c["categoria"] for c in fin_cart)
    cnt_sub_cab = Counter(f"{c['categoria']}/{c['subtipo']}" for c in fin_cart if c["en_cabecera"])
    sin_nombre = [oid(c["e"]) for c in finales if not c["nombre"]]
    edu = [c for c in finales if c["categoria"] == "educacion"]
    edu_c = [c for c in edu if c["municipio"] == "Cartago"]
    cuid = [c for c in finales if c["categoria"] == "cuidado"]
    eq_res = {
        "nota": "Conteos de equipamientos MAPEADOS EN OSM; OSM está muy incompleto (ver cobertura_frente_a_registros_oficiales).",
        "elementos_osm": len(candidatos), "tras_deduplicar": len(finales),
        "por_categoria_extension": dict(cnt_cat), "por_categoria_municipio_cartago": dict(cnt_cat_cartago),
        "por_subtipo_extension": dict(sorted(cnt_sub.items())), "por_subtipo_cabecera_dane": dict(sorted(cnt_sub_cab.items())),
        "cobertura_frente_a_registros_oficiales": cobertura_eq,
        "duplicados_fusionados": [{"conserva": oid(c["e"]), "nombre": c["nombre"], "fusiona": c["fusionados"],
                                   "motivo": "; ".join(c["motivos"])} for c in finales if c["fusionados"]],
        "sin_nombre": sin_nombre,
        "educacion_a_300m_de_verde_05ha": {
            "municipio_cartago": f"{sum(c['dist_verde'] <= DIST_OMS for c in edu_c)} de {len(edu_c)}",
            "extension_de_la_rejilla": f"{sum(c['dist_verde'] <= DIST_OMS for c in edu)} de {len(edu)}",
            "nota": "La extensión incluye sedes de Puerto Caldas (Pereira) y la escuela de aviación del aeropuerto."},
        "cuidado_a_300m_de_verde_05ha": f"{sum(c['dist_verde'] <= DIST_OMS for c in cuid)} de {len(cuid)}",
    }

    vacios = []
    vacios.append({"tema": "Verde público sin nombre",
                   "evidencia": f"{len(sin_nom)} de {len(pub_cab)} polígonos de verde público de la cabecera no tienen 'name'",
                   "ids": [v["props"]["osm_id"] for v in sin_nom]})
    if seps:
        vacios.append({"tema": "Separadores viales etiquetados como verde (leisure=garden/park)",
                       "evidencia": f"{len(seps)} polígonos, {round(sum(v['gu'].area for v in seps))} m² en total "
                                    f"({round(area_sep_dane)} m² en la cabecera): " + "; ".join(
                                        f"{v['props']['osm_id']} ({round(v['gu'].area)} m², ancho medio "
                                        f"{v['separador']['ancho_medio_m']} m, junto a {', '.join(v['separador']['vias']) or 'vías sin nombre'})"
                                        for v in sorted(seps, key=lambda v: -v['gu'].area)),
                       "nota": "Se excluyen del indicador y del área verde pública; en OSM convendría etiquetarlos como "
                               "landuse=grass o area:highway, no como jardín."})
    vacios.append({"tema": "Acceso no declarado",
                   "evidencia": f"{len(sin_acc)} de {len(pub)} polígonos públicos no tienen etiqueta 'access' "
                                "(se asumieron públicos)"})
    vacios.append({"tema": "Verde solo como punto",
                   "evidencia": f"{len(puntos_verdes)} elemento(s) de verde mapeado(s) como nodo, sin área",
                   "detalle": puntos_verdes})
    sinz = [z["nombre"] for z in por_zona if z["parques_ge_05ha_que_tocan"] == 0]
    vacios.append({"tema": "Zonas sin ningún verde público ≥ 0,5 ha mapeado",
                   "evidencia": ", ".join(sinz) if sinz else "ninguna",
                   "nota": "Puede ser un déficit real o parques sin mapear; requiere verificación en campo o con el inventario "
                           "municipal de espacio público (ver 'sensibilidad')."})
    nombradas = [c for c in cancha_info if c["nombre"] and not c["dentro_de_verde_publico"] and c["access"] != "private"]
    pub_cart = [c for c in nombradas if c["municipio"] == "Cartago" and c["osm_id"] not in CLUBES]
    club = [c for c in nombradas if c["osm_id"] in CLUBES]
    otro_m = [c for c in nombradas if c["municipio"] != "Cartago"]
    vacios.append({"tema": "Escenarios deportivos con nombre fuera de cualquier parque mapeado",
                   "evidencia": f"En Cartago, {len(pub_cart)} escenarios públicos: "
                                + "; ".join(f"{c['nombre']} ({c['osm_id']})" for c in pub_cart)
                                + (f". Además, {len(club)} club con entrada paga: " + "; ".join(
                                    f"{c['nombre']} ({c['osm_id']})" for c in club) if club else "")
                                + (f". Fuera del municipio, {len(otro_m)}: " + "; ".join(
                                    f"{c['nombre']} ({c['osm_id']})" for c in otro_m) if otro_m else "")})
    edu_sin = [oid(c["e"]) for c in edu_c if not c["nombre"]]
    vacios.append({"tema": "Colegios sin nombre",
                   "evidencia": f"{len(edu_sin)} de {len(edu_c)} sedes educativas mapeadas en Cartago sin 'name' "
                                f"({sum(1 for c in edu if not c['nombre'])} de {len(edu)} en toda la extensión)",
                   "ids": edu_sin})
    vacios.append({"tema": "Equipamientos sin mapear (cobertura frente a registros oficiales)",
                   "evidencia": " ".join(cob_txt) or "sin comparación (no hubo acceso a los registros oficiales)",
                   "detalle": cobertura_eq})
    gr = otras.get("landuse=grass", [])
    gr_aer = [(e, g) for e, g in gr if aerodromo.intersection(g).area >= 0.5 * g.area]
    gr_urb = [(e, g) for e, g in gr if aerodromo.intersection(g).area < 0.5 * g.area]
    vacios.append({"tema": "Zonas verdes sin uso declarado (landuse=grass)",
                   "evidencia": f"{len(gr)} polígonos landuse=grass: {len(gr_aer)} dentro del aeródromo "
                                f"({round(sum(a_utm(g).area for _, g in gr_aer) / 1e4, 1)} ha, no son espacio público) y "
                                f"{len(gr_urb)} en el resto ({round(sum(a_utm(g).area for _, g in gr_urb))} m²). Estos últimos "
                                "pueden ser separadores, lotes o zonas verdes públicas no etiquetadas como parque.",
                   "ids_fuera_del_aerodromo": [{"osm_id": oid(e), "area_m2": round(a_utm(g).area),
                                                "comuna": comuna_de(g.representative_point())} for e, g in gr_urb]})
    rarezas = []
    for p in puntos_verdes:
        if p["etiquetas"].get("sport") == "9pin":
            rarezas.append(f"{p['osm_id']} '{p['nombre']}' etiquetado leisure=playground con sport=9pin (parece una cancha de bolo)")
    for c in finales:
        nm = (c["nombre"] or "").lower()
        if c["subtipo"] == "school" and ("flying" in nm or "cockpit" in nm):
            rarezas.append(f"{oid(c['e'])} '{c['nombre']}' etiquetado amenity=school: parece una escuela de aviación")
        if c["subtipo"] == "hospital" and "puesto de salud" in nm:
            rarezas.append(f"{oid(c['e'])} '{c['nombre']}' etiquetado como hospital: por su nombre es un puesto de salud")
    for v in verdes:
        if v["props"]["nombre"] and "parqure" in v["props"]["nombre"].lower():
            rarezas.append(f"{v['props']['osm_id']} nombre con errata: '{v['props']['nombre']}'")
    vacios.append({"tema": "Etiquetado dudoso", "evidencia": rarezas})

    if os.path.exists(VIAS_JSON):
        patron = re.compile(r"(hospital|cl[ií]nica|colegio|escuela|instituci[oó]n educativa|universidad)\s+(.+)", re.I)
        refs = []
        for e in json.load(open(VIAS_JSON, encoding="utf-8"))["elements"]:
            nm = e.get("tags", {}).get("name") or ""
            m = patron.search(nm)
            if e["type"] != "way" or not m or len(e.get("geometry", [])) < 2:
                continue
            lu = a_utm(LineString([(p["lon"], p["lat"]) for p in e["geometry"]]))
            inst = normalizar(m.group(2))
            if [c for c in finales if inst and inst in normalizar(c["nombre"])]:
                continue
            cerca = min(finales, key=lambda c: (c["ptu"] if c["origen"] == "nodo" else a_utm(c["g"])).distance(lu))
            dcer = (cerca["ptu"] if cerca["origen"] == "nodo" else a_utm(cerca["g"])).distance(lu)
            refs.append({"via": f"way/{e['id']}", "nombre_via": nm, "institucion_nombrada": m.group(0),
                         "equipamiento_mas_cercano": {"osm_id": oid(cerca["e"]), "nombre": cerca["nombre"],
                                                      "subtipo": cerca["subtipo"], "distancia_m": round(dcer)}})
        if refs:
            ev = "; ".join(f"la vía {r['via']} '{r['nombre_via']}' nombra una institución que no existe con ese nombre en la "
                           f"descarga; el equipamiento más cercano es {r['equipamiento_mas_cercano']['osm_id']} "
                           f"'{r['equipamiento_mas_cercano']['nombre']}' ({r['equipamiento_mas_cercano']['subtipo']}) a "
                           f"{r['equipamiento_mas_cercano']['distancia_m']} m" for r in refs)
            vacios.append({
                "tema": "Equipamiento nombrado en las vías pero ausente o con otro nombre",
                "evidencia": ev, "detalle": refs,
                "nota": "Para el caso del hospital: un directorio web (Waze) ubica el 'Hospital de San Juan de Dios' en la "
                        "Carrera 3ª B # 1-80, junto a la dirección OSM de la IPS Municipal (Carrera 3 Bis # 1-40); "
                        "'Sagrado Corazón de Jesús' es el nombre con que El Tiempo (26-dic-1996) reseña la conversión del "
                        "hospital de Cartago en empresa del Estado. Probable nombre desactualizado en OSM; no verificado en "
                        "campo. Fuentes: https://www.waze.com/live-map/directions/hospital-de-san-juan-de-dios-carrera-3a-b-1-80-"
                        "cartago?to=place.w.186187824.1861878235.1454888 ; https://www.eltiempo.com/archivo/documento/MAM-667482"})
    if manchas:
        vacios.append({"tema": "Vegetación intraurbana sin ningún polígono OSM (pista de zonas verdes sin mapear)",
                       "evidencia": f"{len(manchas)} manchas de 0,5–5 ha dentro de la cabecera, rodeadas de construcción "
                                    f"(≥ 70 % construido en un anillo de ≈ 80 m) y con ≥ 50 % de árboles + pasto según "
                                    f"ESA WorldCover 2021, que no tocan ningún polígono de la descarga OSM; suman "
                                    f"{round(sum(m['area_ha'] for m in manchas), 1)} ha",
                       "nota": "No prueba que sean parques: pueden ser lotes, patios o predios privados (la OMS excluye la "
                               "vegetación sin manejo rodeada de ciudad). Sirve para priorizar la revisión en campo o en el "
                               "inventario municipal de espacio público. Su efecto en el indicador está en 'sensibilidad' (a).",
                       "manchas": manchas})

    # 12. verificaciones ------------------------------------------------------------------
    verif = []

    def celda(la, lo):
        return int((comun.NORTE - la) / comun.RES), int((lo - comun.OESTE) / comun.RES)
    verif.append(f"Consulta Overpass vs archivo: {len(elementos) - len(fuera_filtro)} de {len(elementos)} elementos cumplen "
                 f"algún filtro de la consulta y {len(elementos) - len(fuera_caja)} tocan la caja {BBOX} → "
                 f"{'OK' if not fuera_filtro and not fuera_caja else 'REVISAR: ' + ', '.join((fuera_filtro + fuera_caja)[:5])}")
    control = {}
    for nom, (la, lo) in PUNTOS_CONTROL.items():
        i, j = celda(la, lo)
        control[nom] = {"lat": la, "lon": lo, "distancia_verde_m": float(d05[i, j]),
                        "distancia_verde_025ha_m": float(d025[i, j]), "distancia_verde_todos_m": float(dtodos[i, j])}
    rio_ll = comun.lineas_rio()
    vals_rio = []
    for f in np.linspace(0.05, 0.95, 10):
        p = rio_ll.interpolate(f, normalized=True)
        if comun.SUR < p.y < comun.NORTE and comun.OESTE < p.x < comun.ESTE:
            i, j = celda(p.y, p.x)
            vals_rio.append(float(d05[i, j]))
    control["Río La Vieja (10 puntos del eje)"] = {"min_m": min(vals_rio), "mediana_m": float(np.median(vals_rio)),
                                                    "max_m": max(vals_rio)}
    isl = [c for c in grandes if "Parque de la Isleta" in c["nombres"]]
    if isl:
        rio_u = a_utm(rio_ll)
        p_rio = de_utm(rio_u.interpolate(rio_u.project(isl[0]["gu"].centroid)))
        i, j = celda(p_rio.y, p_rio.x)
        control["Río La Vieja frente al Parque de la Isleta"] = {
            "lat": round(p_rio.y, 5), "lon": round(p_rio.x, 5), "distancia_verde_m": float(d05[i, j]),
            "distancia_eje_rio_a_parque_m": round(isl[0]["gu"].distance(rio_u))}
    ok, ok_esp = 0, 0
    for c in grandes:
        p = de_utm(c["gu"].representative_point())
        i, j = celda(p.y, p.x)
        ok += d05[i, j] <= 20
        ok_esp += d05[comun.ALTO - 1 - i, j] <= 20
    cent = sorted(grandes, key=lambda c: de_utm(c["gu"].representative_point()).y)
    s_pt, n_pt = de_utm(cent[0]["gu"].representative_point()), de_utm(cent[-1]["gu"].representative_point())
    verif.append(f"Orientación: {ok} de {len(grandes)} componentes ≥0,5 ha caen en celdas con distancia ≤ 20 m; con las filas "
                 f"invertidas, {ok_esp}. Más al sur: {', '.join(cent[0]['nombres']) or 'sin nombre'} ({s_pt.y:.4f}, fila "
                 f"{celda(s_pt.y, s_pt.x)[0]}); más al norte: {', '.join(cent[-1]['nombres']) or 'sin nombre'} "
                 f"({n_pt.y:.4f}, fila {celda(n_pt.y, n_pt.x)[0]}) → {'OK' if ok == len(grandes) and ok_esp < len(grandes) / 2 else 'ERROR'}")
    fuera = [c for c in grandes if not municipio.contains(de_utm(c["gu"].representative_point()))]
    if fuera:
        d_solo = distancia([c["gu"] for c in grandes if c not in fuera])
        n_dif = int(((d05 <= DIST_OMS) & (d_solo > DIST_OMS) & m_dane).sum())
        verif.append(f"{len(fuera)} componente(s) ≥0,5 ha fuera del municipio; celdas de la cabecera que pasan a ≤300 m "
                     f"solo por ellos: {n_dif}")
    from PIL import Image
    png = np.asarray(Image.open(os.path.join(comun.CAPAS, "distancia_verde.png")).convert("RGBA")).astype(np.int64)
    v = png[..., 0] * 256 + png[..., 1]
    dec = np.where(v == 0, np.nan, (v - 1) * 1.0 + 0.0)
    npy = comun.cargar_capa("distancia_verde")
    dif = np.nanmax(np.abs(dec - npy))
    dif_r = np.nanmax(np.abs(dec - np.round(npy)))
    verif.append(f"PNG decodificada (v=R*256+G; valor=(v-1)*1+0) vs .npy: diferencia máxima {dif:.3f} m frente al valor "
                 f"continuo y {dif_r:.0f} m frente a round(.npy) → {'OK' if dif <= 0.5 and dif_r == 0 else 'ERROR'}; celdas sin "
                 f"dato {int(np.isnan(dec).sum())}; B única {sorted(set(np.unique(png[..., 2]).tolist()))}, "
                 f"A única {sorted(set(np.unique(png[..., 3]).tolist()))}")
    verif.append(f"Rango distancia_verde: {float(d05.min()):.0f}–{float(d05.max()):.0f} m; 0,25 ha "
                 f"{float(d025.min()):.0f}–{float(d025.max()):.0f} m; todos {float(dtodos.min()):.0f}–{float(dtodos.max()):.0f} m; "
                 f"todos ≤ 0,25 ha ≤ 0,5 ha ≤ 1 ha en todas las celdas: "
                 f"{bool((dtodos <= d025 + 1e-3).all() and (d025 <= d05 + 1e-3).all() and (d05 <= d1 + 1e-3).all())}")
    verif.append(f"Celdas con distancia 0 (dentro de parques ≥0,5 ha): {int((d05 == 0).sum())}, "
                 f"≈ {float(area_celda[d05 == 0].sum()) / 1e4:.1f} ha; área vectorial de esos componentes "
                 f"{sum(c['area_m2'] for c in grandes) / 1e4:.1f} ha")
    verif.append(f"Colores del visor (misma interpolación que js/datos.js): 100 m {color_visor(100)}, 250 m {color_visor(250)}, "
                 f"299 m {color_visor(299)}, 300 m {color_visor(300)}, 301 m {color_visor(301)}, 400 m {color_visor(400)}, "
                 f"450 m {color_visor(450)}, 600 m {color_visor(600)}: el centro neutro cae en 300 m")
    rng = np.random.default_rng(0)
    for _ in range(3):
        i, j = int(rng.integers(0, comun.ALTO)), int(rng.integers(0, comun.ANCHO))
        p = a_utm(Point(lon[i, j], lat[i, j]))
        ref = min(c["gu"].distance(p) for c in grandes)
        verif.append(f"Celda ({i},{j}) lat {lat[i, j]:.5f} lon {lon[i, j]:.5f}: capa {d05[i, j]:.1f} m, cálculo directo {ref:.1f} m")
    if pob is not None:
        verif.append(f"Población de la capa 'poblacion' en las celdas de la cabecera DANE: {pob[m_dane].sum():,.0f} hab "
                     f"(DANE 2026: {pob_cab:,} hab; la diferencia viene de celdas del borde, ver anclaje en datos/series/poblacion.json)")

    limitaciones_serie = [
        "Todas las cifras de verde y equipamientos son 'mapeadas en OpenStreetMap' a la fecha de la descarga, no un inventario "
        "oficial; ver cobertura_frente_a_registros_oficiales y vacios_osm.",
        f"El acceso a ≤ 300 m de la cabecera va de {coma(rango_cab[0])} % a {coma(rango_cab[1])} % de la población según el umbral de "
        "tamaño (0,25–1 ha) y el verde sin mapear o no incluido (escenarios a, b y c); el orden de las comunas puede "
        "invertirse (ver 'sensibilidad').",
        "Antes de usar estas cifras para priorizar inversión, contrastarlas con el inventario municipal de espacio público "
        "(diagnóstico del POT; Findeter 2022 reporta 224.800 m² de espacio público efectivo urbano).",
        "La cabecera DANE (MGN 2018, clase 1) incluye el área urbana de Zaragoza; sus totales también.",
        "El indicador ponderado por población usa la capa 'poblacion' de BioMap (modelada a partir del censo 2018 y anclada a "
        "DANE 2026), no un conteo por vivienda.",
        "Se asume público el verde sin etiqueta 'access'; las exclusiones (institucionales, con tarifa, separadores viales) son "
        "reglas propias documentadas.",
        "Distancia en línea recta, sin barreras; no mide calidad ni seguridad del verde.",
        "m²/hab del verde de OSM no es comparable directamente con el índice de espacio público efectivo (15 m²/hab, Decreto "
        "1504 de 1998), que incluye plazas y plazoletas.",
        "Los equipamientos son puntos (centroide), no linderos; la consulta no incluyó healthcare=*.",
        "Las cifras por zona dependen de las capas 'poblacion' y WorldCover de otros scripts; si se regeneran, conviene volver "
        "a ejecutar este script.",
    ]

    resumen = {
        "titulo": "Espacio verde público y equipamientos sensibles mapeados en OpenStreetMap (Cartago)",
        "descripcion": "Área de verde público, acceso a menos de 300 m según la OMS con su sensibilidad, canchas, "
                       "equipamientos sensibles mapeados y vacíos de datos detectados en OpenStreetMap.",
        "fuente_osm": {"nombre": "OpenStreetMap", "licencia": "ODbL 1.0", "cita": atrib, "extraccion": marca_txt,
                       "consulta_overpass": CONSULTA_OVERPASS,
                       "consulta_archivo": "fuentes/verdes/osm-verdes-equipamientos.overpassql"},
        "referencias": [
            {"cita": "WHO Regional Office for Europe (2016). Urban green spaces and health. A review of evidence. Copenhague.",
             "url": "https://www.who.int/europe/publications/i/item/WHO-EURO-2016-3352-43111-60341",
             "uso": "Criterio de 300 m en línea recta al borde de verde público ≥ 0,5 ha (secciones 3.6.2 y 4.4); 1 ha como "
                    "indicador adicional; 200 y 500 m como análisis complementarios (sección 4.3.2, p. 36); tamaños de 0,25 a "
                    "5 ha probados en los casos de estudio (sección 4.1, p. 32); unidad mínima de 0,25 ha y definición de "
                    "Urban Atlas 14100 (recuadro 4.1, p. 33)."},
            {"cita": "Decreto 1504 de 1998, arts. 12 y 14 (Decreto 1077 de 2015, arts. 2.2.3.2.5 y 2.2.3.2.7)",
             "url": "https://normas.cra.gov.co/gestor/docs/decreto_1504_1998.htm",
             "uso": "Índice mínimo de espacio público efectivo de 15 m²/hab (parques, plazas, plazoletas y zonas verdes). "
                    "Solo como referencia: el verde de OSM no equivale al espacio público efectivo."},
            {"cita": REF_FINDETER["fuente"], "url": REF_FINDETER["url"], "uso": REF_FINDETER["paginas"]},
            {"cita": REF_BOLETIN["fuente"], "url": REF_BOLETIN["url"], "uso": REF_BOLETIN["paginas"]},
        ],
        "cabecera_usada": fuente_cab,
        "cabecera_incluye_zaragoza": nota_zaragoza,
        "limitaciones": limitaciones_serie,
        "espacio_verde": {
            "poligonos_candidatos": len(verdes), "poligonos_publicos": len(pub),
            "poligonos_excluidos": [{"osm_id": v["props"]["osm_id"], "nombre": v["props"]["nombre"],
                                     "area_m2": v["props"]["area_m2"], "acceso": v["props"]["acceso"]}
                                    for v in verdes if not v["publico"]],
            "componentes_publicos": len(componentes), "componentes_ge_025ha": len(mayores(comps_g, UMBRAL_HA_UA)),
            "componentes_ge_05ha": len(grandes), "componentes_ge_1ha": len(grandes1),
            "componentes_menores_de_100m2": sum(1 for a in mini if a < 100),
            "areas_de_los_5_componentes_mas_pequenos_m2": [round(a) for a in mini[:5]],
            "componentes_ge_05ha_detalle": [{"id": c["id"], "nombres": c["nombres"], "area_ha": round(c["area_m2"] / 1e4, 2),
                                             "n_poligonos": c["n_poligonos"]}
                                            for c in sorted(grandes, key=lambda c: -c["area_m2"])],
            "area_verde_publica_cabecera_dane_m2": round(area_pub_dane),
            "area_verde_publica_cabecera_osm_m2": round(area_pub_osm),
            "area_en_componentes_ge_05ha_cabecera_dane_m2": round(area_05_dane),
            "area_de_canchas_dentro_del_verde_publico_cabecera_m2": round(cancha_en_parque),
            "area_separadores_viales_excluidos_cabecera_m2": round(area_sep_dane),
            "poblacion_cabecera_dane": {"anio": anio_pob, "hab": pob_cab,
                                        "fuente": "DANE, PPED serie municipal por área 2018-2042 (actualizada 30-jul-2025)",
                                        "nota": "la cabecera DANE incluye Zaragoza"},
            "m2_verde_publico_por_hab_cabecera": round(area_pub_dane / pob_cab, 2) if pob_cab else None,
            "contraste_inventario_municipal": {
                "fuente": REF_FINDETER["fuente"], "url": REF_FINDETER["url"], "paginas": REF_FINDETER["paginas"],
                "espacio_publico_efectivo_urbano_m2": REF_FINDETER["epe_urbano_m2"],
                "m2_hab_2021": REF_FINDETER["epe_m2_hab_2021"],
                "nota": "Concepto distinto (el espacio público efectivo incluye plazas y plazoletas; el verde de OSM incluye "
                        "zonas de juego y jardines) y sin geometría disponible aquí: solo sirve para ver que el orden de "
                        "magnitud del total coincide. No permite validar la distribución por comuna."},
            "referencia_15m2_hab_espacio_publico_efectivo": "no comparable directamente (ver referencias)",
            "puntos_sin_area": puntos_verdes,
        },
        "acceso_oms": acceso,
        "sensibilidad": {
            "indicador": "población a ≤ 300 m en línea recta, % (capa 'poblacion')",
            "cabecera_dane": sens_cab,
            "rango_cabecera_pct": rango_cab,
            "escenarios_en_el_rango": ESC_RANGO,
            "orden_de_las_zonas": {k: ordenes[k] for k in escenarios},
            "orden_cambia_respecto_a_la_base": cambios_orden,
            "bosques_osm_usados_en_b": [{"osm_id": oid(e), "etiqueta": next(f"{k}={e['tags'][k]}" for k in ("natural", "landuse")
                                                                           if (k, e["tags"].get(k)) in BOSQUES),
                                         "nombre": e["tags"].get("name"), "area_ha": round(gu.area / 1e4, 2)}
                                        for e, gu in sorted(bosques_sel, key=lambda x: -x[1].area)],
            "nota": "Los escenarios (a) y (b) son cotas superiores: suponen que esa vegetación es verde público utilizable, lo "
                    "que no está verificado. 'sin_umbral' y los mínimos en m² no entran en el rango porque cuentan jardineras.",
        },
        "por_zona": por_zona,
        "canchas": {"n": len(cancha_info), "n_en_cabecera": sum(c["en_cabecera"] for c in cancha_info),
                    "n_municipio_cartago": sum(c["municipio"] == "Cartago" for c in cancha_info),
                    "area_total_m2": round(sum(c["area_m2"] for c in cancha_info)),
                    "n_privadas": sum(c["access"] == "private" for c in cancha_info),
                    "n_dentro_de_verde_publico": sum(c["dentro_de_verde_publico"] for c in cancha_info),
                    "por_deporte": dict(Counter(c["deporte"] or "sin dato" for c in cancha_info)),
                    "detalle": cancha_info},
        "otras_coberturas_no_incluidas": otras_res,
        "equipamientos": eq_res,
        "vacios_osm": vacios,
        "verificacion": {"puntos_control": control, "comprobaciones": verif, "estadisticas_capa": est},
        "problemas": PROBLEMAS,
        "fecha_proceso": date.today().isoformat(),
    }
    comun.guardar_json(os.path.join(SERIES, "verdes.json"), resumen)

    # 13. impresión ----------------------------------------------------------------------
    print(f"\nCabecera usada: {fuente_cab}")
    print(f"Área verde pública en la cabecera (DANE): {area_pub_dane / 1e4:.2f} ha (OSM: {area_pub_osm / 1e4:.2f} ha); "
          f"en componentes ≥0,5 ha: {area_05_dane / 1e4:.2f} ha; canchas dentro de parques: {cancha_en_parque:.0f} m²; "
          f"separadores viales excluidos: {area_sep_dane:.0f} m²")
    if pob_cab:
        print(f"m² de verde público por habitante (DANE {anio_pob}: {pob_cab:,} hab): {area_pub_dane / pob_cab:.2f}")
    print(f"Zaragoza en la cabecera DANE: {nota_zaragoza}")
    print("Acceso OMS en la cabecera:")
    for k, r in acceso["cabecera_dane"].items():
        print(f"  {k:>18}: {r}")
    print(f"Sensibilidad (cabecera, población a ≤300 m): rango {rango_cab}")
    for k, r in sens_cab.items():
        print(f"  {k:>22}: {r.get('poblacion_pct')} % pob, {r['celdas_pct']} % celdas")
    print("Orden de las zonas:")
    for k, o in ordenes.items():
        print(f"  {k:>22}: {' > '.join(o)}")
    print("Por zona:")
    for z in por_zona:
        print(f"  {z['nombre']:<26} verde {z['area_verde_publica_m2']:>7} m²  ≥0,5ha {z['parques_ge_05ha_que_tocan']}  "
              f"med celdas {z['distancia_mediana_celdas_m']} m  med pob {z.get('distancia_mediana_poblacion_m')} m  "
              f"{z['acceso_300m_05ha'].get('poblacion_pct')} % pob  rango {z['sensibilidad_rango_pct']}  "
              f"m²/hab {z.get('m2_verde_publico_por_hab')}  pos {z['posicion_base']} {z['posicion_min_max_escenarios']}")
    print(f"Canchas: {resumen['canchas']['n']} ({resumen['canchas']['n_en_cabecera']} en la cabecera), "
          f"{resumen['canchas']['area_total_m2']} m²")
    print(f"Equipamientos: {dict(cnt_cat)}; en Cartago {dict(cnt_cat_cartago)}; cabecera {dict(cnt_sub_cab)}")
    print(f"Cobertura: {' '.join(cob_txt)}")
    print(f"Educación a ≤300 m: {eq_res['educacion_a_300m_de_verde_05ha']}")
    print("Puntos de control:")
    for k, r in control.items():
        print(f"  {k}: {r}")
    print("Vacíos de OSM:")
    for vv in vacios:
        print(f"  {vv['tema']}: {str(vv['evidencia'])[:400]}")
    print("Verificaciones:")
    for vv in verif:
        print("  " + vv)
    if PROBLEMAS:
        print("Problemas:")
        for p in PROBLEMAS:
            print("  " + p)
    print(f"Tiempo: {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
