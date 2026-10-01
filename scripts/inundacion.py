"""Susceptibilidad TOPOGRÁFICA a inundación de Cartago (HAND) y agua superficial histórica.

ADVERTENCIA: este producto describe la posición del terreno respecto a los cauces. NO es la
amenaza oficial por inundación: esa está en el POT de Cartago, en los estudios de la CVC
(Corporación Autónoma Regional del Valle del Cauca) y en la zonificación del IDEAM, que modelan
caudales, periodos de retorno, diques y obras. Aquí no hay hidráulica, ni lluvia, ni caudales.

FUENTES Y LICENCIAS
  1. Copernicus DEM GLO-30 (WorldDEM-30), teselas COG públicas en AWS (Open Data):
       https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N04_00_W076_00_DEM/Copernicus_DSM_COG_10_N04_00_W076_00_DEM.tif
       https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N04_00_W077_00_DEM/Copernicus_DSM_COG_10_N04_00_W077_00_DEM.tif
         (la segunda solo para el margen occidental: la rejilla termina 1,6 km al este del meridiano 76° O)
     Licencia: "Licence for the use of the Copernicus WorldDEM-30" (libre y gratuita; reproducción,
     distribución y modificación permitidas). Verificada en
       https://docs.sentinel-hub.com/api/latest/static/files/data/dem/resources/license/License-COPDEM-30.pdf
     Aviso obligatorio para datos modificados (art. 6 b):
       "produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH
        2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved"
     Exención obligatoria (art. 6 c), en todo aviso de distribución: "The organisations in charge of the
       Copernicus programme by law or by delegation do not incur any liability for any use of the
       Copernicus WorldDEM-30".
     DOI pedido para citar: https://doi.org/10.5270/ESA-c5d3d65
     Producto: modelo DIGITAL DE SUPERFICIE (incluye edificios y árboles); alturas sobre el geoide
     EGM2008; cuerpos de agua aplanados y ríos editados para flujo consistente (Product Handbook,
     https://dataspace.copernicus.eu/sites/default/files/media/files/2024-06/geo1988-copernicusdem-spe-002_producthandbook_i5.0.pdf).
  2. JRC Global Surface Water v1.5 (1984–2024), capas 'occurrence' y 'extent', tesela 80W_10N, COG
     servidos por el JRC (listado enlazado desde https://global-surface-water.appspot.com/download):
       https://s3.waw4-1.cloudferro.com/swift/v1/global-surface-water/download2024/Aggregated/VER1-5/occurrence/occurrence_80W_10N_v1_5_2024.tif
       https://s3.waw4-1.cloudferro.com/swift/v1/global-surface-water/download2024/Aggregated/VER1-5/extent/extent_80W_10N_v1_5_2024.tif
     Si fallan, se usa la v1.3 (1984–2020) de Microsoft Planetary Computer (colección 'jrc-gsw').
     Licencia: "All data here is produced under the Copernicus Programme and is provided free of
     charge, without restriction of use" (https://global-surface-water.appspot.com/download).
     Cita obligatoria: Pekel, J.-F., Cottam, A., Gorelick, N., Belward, A. S. (2016). High-resolution
     mapping of global surface water and its long-term changes. Nature 540, 418–422.
     doi:10.1038/nature20584. Atribución en mapas: "Source: EC JRC/Google".
     Codificación: occurrence 0 = no agua, 1–100 = % de observaciones con agua, 255 = sin dato;
     extent 0 = nunca agua, 1 = agua detectada alguna vez, 255 = sin dato (se comprueba en los datos).
  3. Ejes y áreas de los ríos: OpenStreetMap (© colaboradores de OpenStreetMap, ODbL 1.0):
     comun.osm() ('rio_la_vieja', 'rio_cauca'), fuentes/osm-base.json (vías fluviales completas
     del río La Vieja y del Cauca) y fuentes/osm-verdes-equipamientos.json (polígonos natural=water,
     water=river del Cauca, La Vieja y Consota). Arroyos, canales y demás ríos (waterway=river, stream,
     canal, drain, ditch) del dominio: API pública de Overpass (https://overpass-api.de/api/interpreter,
     con espejos de respaldo), caché en fuentes/inundacion/osm_cauces_dominio.json.
  4. SOLO PARA VALIDACIÓN (no se publican como capas): IDEAM, servicio ArcGIS 'Amenaza_Ambiental'
       https://visualizador.ideam.gov.co/gisserver/rest/services/Amenaza_Ambiental/MapServer
     capa 0 "Amenaza Creciente Subita TR 50 Años 8 cabeceras municipales 2K" (polígonos de Cartago,
     río La Vieja, clases ALTA/MEDIA/BAJA) y capas de áreas afectadas por inundación de La Niña
     (1988, 2000, 2011, 2012, 2016, 2020–2022). El servicio no declara licencia (copyrightText vacío);
     la página de datos abiertos del IDEAM solo trae la definición genérica de dato abierto. Las capas
     La Niña 1988, 2000, 2011 y 2012 están además en datos.gov.co, publicadas por el IDEAM con licencia
     CC BY-SA 4.0 (khg6-9h39, 5p6w-58v3, 6eu7-pzc5, nufr-59j5; verificado vía api/views el 2026-10-01).
     No se encontró en datos.gov.co la creciente súbita TR 50. Escala de las manchas: no declarada.
     Se publican solo estadísticas derivadas, con atribución al IDEAM.
  5. Altura del dosel: Meta y World Resources Institute (WRI), High Resolution Canopy Height Maps v1
     (1 m), teselas COG en AWS Open Data (s3://dataforgood-fb-data/forests/v1/alsgedi_global_v6_float/chm/,
     quadkeys 032232013 y 032232102). Licencia CC BY 4.0 según el Registry of Open Data on AWS
     (https://registry.opendata.aws/dataforgood-fb-forests/). Cita: Tolan et al. (2024), Remote Sensing
     of Environment 300, 113888, doi:10.1016/j.rse.2023.113888. Las teselas son tiras de una fila sin
     resúmenes: se leen por ventanas solo las filas del dominio (≈ 26.000 filas por tesela) y se promedian
     a 8×8 px (≈ 9,6 m). Se descartó la v2 (2026; Brandt et al., arXiv:2603.06382) porque su licencia es
     ambigua: el registro de AWS y Zenodo dicen CC BY 4.0, pero el artículo la publica "under the DINOv3
     license" (licencia propia de Meta con restricciones de uso).

UMBRALES (fundamento)
  - Nobre, A.D., Cuartas, L.A., Hodnett, M., Rennó, C.D., Rodrigues, G., Silveira, A., Waterloo, M.,
    Saleska, S. (2011). Height Above the Nearest Drainage – a hydrologically relevant new terrain
    model. Journal of Hydrology 404, 13–29. doi:10.1016/j.jhydrol.2011.03.051. Calibraron en campo
    (Amazonia central, SRTM 90 m) los umbrales 5,3 m (suelos encharcados / ecotono) y 15 m
    (ecotono / tierra alta) (verificado en el manuscrito aceptado, sección 3.3.1).
  - Rennó, C.D., Nobre, A.D., Cuartas, L.A., Soares, J.V., Hodnett, M.G., Tomasella, J., Waterloo,
    M.J. (2008). HAND, a new terrain descriptor using SRTM-DEM: Mapping terra-firme rainforest
    environments in Amazonia. Remote Sensing of Environment 112, 3469–3481 (algoritmo HAND).
  - Santos, E.D.S., Pinheiro, H.S.K., Gallo Junior, H. (2021). Height Above the Nearest Drainage to
    Predict Flooding Areas in São Luiz do Paraitinga, São Paulo. Floresta e Ambiente 28(2).
    doi:10.1590/2179-8087-FLORAM-2020-0070. Clases muy alta 0–3 m, alta 3–7, media 7–12, baja 12–15,
    muy baja > 15 m, calibradas con crecientes históricas locales (1996, 2000, 2006, 2010), sobre un
    DEM TOPODATA de 30 m interpolado con Topo to Raster y una red de 100 celdas (≈ 0,09 km²).
    Esa red es unas 55 veces más fina que la de aquí y el DEM no es el mismo: los cortes de HAND no
    se trasladan entre redes ni DEM distintos, así que su 0–3 m NO respalda directamente el corte de
    3 m de este producto; es solo un antecedente.
  - Alabbad, Y. (2026). Terrain-Based Flood Susceptibility and Exposure Mapping Using a HAND-GIS
    Framework: A Case Study from the Aseer Region, Saudi Arabia. Water 18(13), 1598
    (https://www.mdpi.com/2073-4441/18/13/1598): ejemplo de sensibilidad del HAND a umbrales de
    iniciación de cauces de 1, 5, 10 y 20 km² con DEM de 30 m.
  Los cortes de este producto (3 / 6 / 15 m, 1,5 km y la franja de 100 m) son CRITERIO TÉCNICO: 15 m
  coincide con el límite superior de las tierras bajas de Nobre et al. (2011); 3 m, 6 m, 1,5 km y
  100 m no están calibrados para Cartago. El script publica la sensibilidad a cada uno (datos/series/inundacion.json)
  y una comparación con la amenaza del IDEAM y con manchas de inundación observadas.

CLASES (rejilla común). Las clases baja y 0 NO descartan amenaza: la referencia oficial es IDEAM/CVC/POT.
  3 alta  = HAND respecto a los ríos La Vieja o Cauca (hand_rio_mayor) ≤ 3 m y distancia euclidiana
            al cauce mayor ≤ 1,5 km. Es decir: la celda está a ≤ 3 m por encima del nivel del río
            mayor en el punto donde su drenaje lo alcanza. No depende de la red menor.
  2 media = HAND respecto al cauce más cercano (mayor, arroyo/canal OSM o derivado) ≤ 6 m, o celda a
            ≤ DIST_PISO_M = 100 m del cauce mayor (REGLA DE PISO de la franja de ribera: allí el dosel
            residual del DSM y el desfase de los ejes OSM elevan el HAND), y no clase 3.
  1 baja  = 6 < HAND ≤ 15 m.  0 = HAND > 15 m (etiqueta 'HAND > 15 m', no 'sin susceptibilidad').

PASOS
  1. Lee del COG remoto solo la ventana DOM (−76,08 a −75,76 E; 4,60 a 4,88 N: ≈ 10 km de margen
     alrededor de la rejilla común para no cortar cuencas), en trozos alineados con los bloques de
     1024 px, con 4 hilos y reintentos. Caché en fuentes/inundacion/ (no se publica). Igual con el
     CHM (filas del dominio, promedio 8×8 px) y con los cauces OSM (una consulta Overpass).
  2. 'altitud': DSM a la rejilla común con remuestreo bilineal (comun.reproyectar), SIN corregir.
  3. DSM a UTM 18N (EPSG:32618) a 30 m, bilineal, sobre el rectángulo UTM inscrito en DOM.
  3b. Corrección del dosel (calibrar_dosel): CHM promediado a 30 m; en terreno llano fuera de la
     ciudad se mide el exceso del DSM sobre la media de las celdas sin dosel de una ventana de
     330 m, se toma la mediana por intervalos de CHM y se resta esa curva (interpolada) al DSM. El
     control (celdas sin dosel) da ≈ 0 m. La lámina de agua de los ríos sigue saliendo del DSM.
  4. Quema de cauces: La Vieja y Cauca (ejes OSM con all_touched y polígonos de agua fluvial), el
     Consota (polígono) y los demás ríos OSM se bajan PROFUNDIDAD_QUEMA m; los arroyos OSM (con sus
     alcantarillas) y los canales OSM que pasan la prueba topográfica de drenaje (evaluar_canales:
     corren por lo bajo, no a media ladera ni en terraplén) se bajan PROFUNDIDAD_QUEMA_MENOR m. Solo
     dirige el flujo; las alturas del HAND NO usan el DEM quemado.
  5. Relleno de depresiones Priority-Flood + ε (Barnes et al. 2014, implementado aquí en Python
     puro con heapq): no deja planos ni pozos; el orden de extracción da un orden topológico.
  6. Dirección de flujo D8 (máxima pendiente, diagonales a 30·√2 m) sobre el DEM rellenado.
  7. Acumulación de flujo (celdas aguas arriba) recorriendo el orden topológico.
  8. Red de drenaje = cauces OSM quemados ∪ cauces derivados (área drenada ≥ UMBRAL_KM2 = 5 km²)
     solo FUERA de la red mapeada: los derivados a ≤ CERCA_OSM_M = 90 m de un cauce OSM se
     sustituyen por él. Los tramos derivados que pasan por celdas que el relleno elevó más de
     UMBRAL_RELLENO_M (0,5 m) se EXCLUYEN: allí el D8 cruza depresiones rellenadas del DSM con
     trayectos rectos que no son cauces observados ('trayecto_sobre_relleno' en el GeoJSON).
  9. Cota del cauce: ríos OSM, mínimo 5×5 (±60 m) del DSM sin corregir (lámina de agua); arroyos y
     canales OSM, mínimo 3×3 del DEM corregido; derivados, la propia celda del DEM corregido. Perfil
     no creciente aguas abajo SOLO dentro de cada tipo de cauce (río mayor, otros ríos, arroyo/canal
     OSM, derivado). Con la exclusión del paso 8, el rebaje de un cauce derivado queda acotado por
     UMBRAL_RELLENO_M. Piso: la cota de un cauce menor no baja de la del río mayor (La Vieja o
     Cauca) al que entrega; así hand ≤ hand_rio_mayor en toda celda.
 10. HAND = altura de la celda (DEM corregido del dosel) − cota del cauce al que drena por D8 (salto
     de punteros vectorizado). Dos versiones: 'hand' respecto a toda la red y 'hand_rio_mayor'
     respecto solo a La Vieja y Cauca. Negativos (depresiones del DSM) → 0 (el HAND bruto se usa para
     separar esas depresiones en el resumen por zona). Celdas que salen del dominio sin tocar la red →
     sin dato.
 11. Distancia euclidiana al cauce mayor (La Vieja + Cauca, ejes y polígonos) en UTM.
 12. HAND y distancia a la rejilla común (bilineal); 'hand' y 'hand_rio_mayor' se recortan a 0–60 m.
 13. 'susceptibilidad_inundacion': clases de arriba (con la regla de piso).
 14. 'agua_ocurrencia': JRC GSW v1.5 occurrence; su malla de 0,00025° coincide exactamente con la
     rejilla común (origen −80°, 10°), así que se copia sin remuestreo. 255 → sin dato. Se mide (no se
     corrige) el posible desfase de ± 1 celda frente al DEM.
 15. Sensibilidad (área de drenaje 1/2/5/10 km² o sin red derivada × exclusión de relleno 0,5 m /
     2 m / sin exclusión; corte de HAND 2/3/4 m × distancia 1,0–2,0 km), validación frente al IDEAM
     (amenaza por creciente súbita TR 50 años por polígono y por zona, y manchas de La Niña), efecto de
     cada corrección (versión anterior, solo dosel, solo red OSM, sin regla de piso, publicada) y
     coherencia interna. Todo en datos/series/inundacion.json, con 'hallazgos' generados de los datos.
 16. Red de drenaje como GeoJSON (datos/vectores/inundacion_drenaje.geojson) y verificaciones
     (rangos, puntos de control, norte/sur, PNG decodificada vs .npy).

Dependencias: numpy, scipy, rasterio, pyproj, shapely, pystac-client, planetary-computer, pillow,
requests. pysheds se intentó instalar (uv pip install pysheds) pero la descarga de numba/llvmlite no
terminó en > 20 min con la red lenta; por eso D8 está implementado aquí con numpy/scipy/heapq.

Uso: .venv/bin/python scripts/inundacion.py
"""
from __future__ import annotations

import heapq
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comun  # noqa: E402

CACHE = os.path.join(comun.FUENTES, "inundacion")
os.makedirs(CACHE, exist_ok=True)
SERIES = os.path.join(comun.DATOS, "series")
VECTORES = os.path.join(comun.DATOS, "vectores")
UA = {"User-Agent": "BioMapCartago/1.0 (plataforma geoambiental abierta)"}

# Dominio de cálculo (≈ 10 km de margen alrededor de la rejilla común)
DOM_OESTE, DOM_ESTE, DOM_SUR, DOM_NORTE = -76.08, -75.76, 4.60, 4.88
URL_DEM = ("https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_{t}_00_DEM/"
           "Copernicus_DSM_COG_10_{t}_00_DEM.tif")
TESELAS = ["N04_00_W077", "N04_00_W076"]
RUTA_DEM = os.path.join(CACHE, "copdem_glo30_ventana.tif")
URL_GSW15 = ("https://s3.waw4-1.cloudferro.com/swift/v1/global-surface-water/download2024/Aggregated/VER1-5/"
             "{c}/{c}_80W_10N_v1_5_2024.tif")
RUTA_GSW15 = {c: os.path.join(CACHE, f"jrc_gsw_v1_5_{c}_rejilla.tif") for c in ("occurrence", "extent")}
RUTA_GSW13 = os.path.join(CACHE, "jrc_gsw_occurrence_rejilla.tif")   # v1.3 (Planetary Computer), respaldo
URL_CHM = "https://dataforgood-fb-data.s3.amazonaws.com/forests/v1/alsgedi_global_v6_float/chm/{q}.tif"
TESELAS_CHM = ["032232013", "032232102"]      # quadkeys de nivel 9 que cubren el dominio
CHM_FACTOR = 8                                 # 8×8 px de 1,19 m → bloques de ≈ 9,6 m
RUTA_CHM = os.path.join(CACHE, "meta_wri_chm_v1_media_8px.tif")
URL_CHM_FECHA = "https://dataforgood-fb-data.s3.amazonaws.com/forests/v1/alsgedi_global_v6_float/CHM_acquisition_date.tif"
RUTA_CHM_FECHA = os.path.join(CACHE, "meta_wri_chm_v1_fecha_dominio.tif")
RUTA_OSM_CAUCES = os.path.join(CACHE, "osm_cauces_dominio.json")
OVERPASS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.private.coffee/api/interpreter"]
IDEAM_SERVICIO = "https://visualizador.ideam.gov.co/gisserver/rest/services/Amenaza_Ambiental/MapServer"
# capa → (clave, nombre exacto en el servicio, año o periodo)
IDEAM_CAPAS = {
    0: ("creciente_subita_tr50", "Amenaza Creciente Subita TR 50 Años 8 cabeceras municipales 2K", None),
    6: ("nina_1988", "Areas Afectadas Inundacion Niña 1988", "1988"),
    7: ("nina_2000", "Areas Afectadas Inundacion Niña 2000", "2000"),
    8: ("nina_2011", "Areas Afectadas Inundacion Niña 2011", "2011"),
    9: ("nina_2012", "Areas Afectadas Inundacion Niña 2012", "2012"),
    22: ("nina_2011_v2", "Areas afectadas inundacion Nina 2011 V2", "2011"),
    23: ("nina_2016", "Areas afectadas por inundacion Nina 2016", "2016"),
    24: ("nina_2020_2022", "Areas afectadas por inundacion Nina 2020 - 2022", "2020–2022"),
    25: ("nina_1988_v2", "Areas afectadas por Inundacion niña 1988 V2", "1988"),
    26: ("nina_2000_v2", "Areas afectadas por  Inundacion niña 2000 V2", "2000"),
    27: ("nina_2012_v2", "Areas afectadas por Inundacion niña 2012 V2", "2012"),
}

CRS_UTM = "EPSG:32618"
PASO = 30.0                # m
PROFUNDIDAD_QUEMA = 20.0   # m (solo para dirigir el flujo; criterio técnico)
UMBRAL_KM2 = 5.0           # área drenada mínima para iniciar un cauce derivado (criterio técnico; ver sensibilidad)
UMBRAL_RELLENO_M = 0.5     # tramos derivados sobre celdas elevadas por el relleno más que esto → fuera de la red
HAND_ALTA, HAND_MEDIA, HAND_BAJA = 3.0, 6.0, 15.0
DIST_MAYOR_M = 1500.0
DIST_PISO_M = 100.0        # regla de piso: a ≤ 100 m del cauce mayor (La Vieja o Cauca) la clase no baja de 'media'
CERCA_CAUCE_M = 60.0       # para separar celdas "sobre el cauce quemado" en la validación
PROFUNDIDAD_QUEMA_MENOR = 10.0   # m: arroyos y canales de drenaje OSM (solo dirige el flujo; criterio técnico)
CORREDOR_VIEJA_M = 300.0   # polígono IDEAM a ≤ 300 m del eje de La Vieja = corredor del río; si no, cauce menor
CERCA_OSM_M = 90.0         # cauces derivados a ≤ 90 m de un cauce OSM menor se sustituyen por el cauce mapeado
# calibración del exceso del DSM bajo dosel (ver calibrar_dosel)
CAL_VENTANA = 11           # celdas UTM (330 m)
CAL_SD_MAX = 1.5           # m
CAL_BORDES = [2, 4, 6, 8, 10, 12, 15, 18, 22, 30]   # m de CHM medio en la celda de 30 m

ATRIB_DEM = ("produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH "
             "2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved")
EXENCION_DEM = ("The organisations in charge of the Copernicus programme by law or by delegation do not incur any "
                "liability for any use of the Copernicus WorldDEM-30")
FUENTE_DEM = {
    "nombre": "Copernicus DEM GLO-30 (WorldDEM-30), ESA / Unión Europea",
    "url": "https://copernicus-dem-30m.s3.amazonaws.com/",
    "licencia": "Licence for the use of the Copernicus WorldDEM-30 (libre y gratuita, con atribución y exención de responsabilidad)",
    "cita": ATRIB_DEM + ". " + EXENCION_DEM + ". DOI: 10.5270/ESA-c5d3d65",
}
FUENTE_OSM = "Ríos, arroyos y canales: © colaboradores de OpenStreetMap, ODbL 1.0"
CITA_CHM = ("Tolan, J., Yang, H.-I., Nosarzewski, B., Couairon, G., Vo, H. V., Brandt, J., Spore, J., Majumdar, S., Haziza, D., Vamaraju, J., "
            "et al. (2024). Very high resolution canopy height maps from RGB imagery using self-supervised vision transformer and convolutional "
            "decoder trained on aerial lidar. Remote Sensing of Environment 300, 113888. doi:10.1016/j.rse.2023.113888")
ATRIB_CHM = ("Meta and World Resources Institute (WRI) - 2024. High Resolution Canopy Height Maps (CHM). Source imagery © 2016 Maxar. "
             "Licencia CC BY 4.0 (https://registry.opendata.aws/dataforgood-fb-forests/)")
CITA_GSW = ("Pekel, J.-F., Cottam, A., Gorelick, N., Belward, A. S. (2016). High-resolution mapping of global surface "
            "water and its long-term changes. Nature 540, 418–422. doi:10.1038/nature20584. Source: EC JRC/Google")
FUENTE_IDEAM = ("IDEAM, servicio Amenaza_Ambiental (" + IDEAM_SERVICIO + "). El servicio no declara licencia (copyrightText y descripciones "
                "vacíos); la sección de datos abiertos del IDEAM solo da la definición genérica de dato abierto. Las capas de áreas afectadas "
                "por La Niña 1988, 2000, 2011 y 2012 también las publica el IDEAM en datos.gov.co con licencia CC BY-SA 4.0 (conjuntos "
                "khg6-9h39, 5p6w-58v3, 6eu7-pzc5 y nufr-59j5, con la advertencia de que no han sido validadas por el IDEAM); para la amenaza por "
                "creciente súbita TR 50 no se encontró conjunto en datos.gov.co. Aquí se publican solo estadísticas derivadas, con atribución al "
                "IDEAM; no se copian sus polígonos")

PUNTOS = {
    "Parque Bolívar (centro)": (4.7497, -75.9132),
    "Aeropuerto Santa Ana": (4.7601, -75.9545),
    "Río La Vieja frente al oriente de la ciudad": (4.7528, -75.9095),
    "Lomas al suroriente (4,70; −75,87)": (4.70, -75.87),
    "Lomas al suroriente (4,71; −75,88)": (4.71, -75.88),
    "Zaragoza (nodo OSM)": (4.6968, -75.9264),
}


# ============================================================== utilidades
def _reintentar(f, *a, intentos=6, espera=4):
    for k in range(intentos):
        try:
            return f(*a)
        except Exception as e:  # noqa: BLE001
            print(f"  reintento {k + 1}/{intentos}: {e}", flush=True)
            time.sleep(espera * (k + 1))
    raise RuntimeError("lectura remota fallida tras reintentos")


def _leer_trozo(url, ventana):
    import rasterio
    with rasterio.open("/vsicurl/" + url) as s:
        return s.read(1, window=ventana)


def celda(lat, lon):
    """Fila y columna de la rejilla común para un punto (lat, lon)."""
    return int((comun.NORTE - lat) / comun.RES), int((lon - comun.OESTE) / comun.RES)


def es(x, fmt="g"):
    """Número con coma decimal para los textos en español."""
    return format(x, fmt).replace(".", ",")


def ha(mask, area):
    return round(float(area[mask].sum()) / 1e4, 2)


# ============================================================== 1. descargas
def descargar_dem():
    import rasterio
    from rasterio.windows import Window, from_bounds
    if os.path.exists(RUTA_DEM):
        print("DEM en caché:", RUTA_DEM)
        return
    partes, tareas = [], []
    for t in TESELAS:
        url = URL_DEM.format(t=t)
        with rasterio.open("/vsicurl/" + url) as s:
            l, b, r, tp = s.bounds
            o, e = max(DOM_OESTE, l), min(DOM_ESTE, r)
            if o >= e:
                continue
            w = from_bounds(o, DOM_SUR, e, DOM_NORTE, transform=s.transform).round_offsets().round_lengths()
            c0 = max(0, int(w.col_off))
            w = Window(c0, int(w.row_off), min(int(w.width), s.width - c0), int(w.height))
            partes.append((t, w, s.window_transform(w)))
            r0, r1 = int(w.row_off), int(w.row_off + w.height)
            cortes = sorted({r0, r1, *[k for k in range(0, s.height, 1024) if r0 < k < r1]})
            for a, z in zip(cortes[:-1], cortes[1:]):
                tareas.append((t, url, Window(w.col_off, a, w.width, z - a)))
    print(f"leyendo {len(tareas)} trozos de {len(partes)} teselas del DEM…", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        res = list(ex.map(lambda x: (x[0], x[2], _reintentar(_leer_trozo, x[1], x[2])), tareas))
    print(f"  descargado en {time.time() - t0:.0f} s", flush=True)
    bloques = []
    for t, w, tr in partes:
        filas = [a for (tt, ww, a) in sorted(res, key=lambda q: q[1].row_off) if tt == t]
        bloques.append(np.vstack(filas))
    assert len({b.shape[0] for b in bloques}) == 1
    # las teselas comparten la malla de 1": la columna final de W077 es contigua a la inicial de W076
    assert abs(partes[0][2].c + bloques[0].shape[1] * partes[0][2].a - partes[-1][2].c) < 1e-9
    mosaico = np.hstack(bloques).astype(np.float32)
    perfil = dict(driver="GTiff", dtype="float32", width=mosaico.shape[1], height=mosaico.shape[0], count=1,
                  crs="EPSG:4326", transform=partes[0][2], compress="deflate", predictor=3, tiled=True)
    with rasterio.open(RUTA_DEM, "w", **perfil) as d:
        d.write(mosaico, 1)
    print("DEM guardado:", RUTA_DEM, mosaico.shape)


def _ventana_gsw(s):
    """Ventana de la rejilla común dentro de un ráster GSW (mallas coincidentes, se comprueba)."""
    from rasterio.windows import Window
    col = (comun.OESTE - s.transform.c) / s.transform.a
    fil = (s.transform.f - comun.NORTE) / -s.transform.e
    assert abs(col - round(col)) < 1e-6 and abs(fil - round(fil)) < 1e-6, (col, fil)
    assert abs(s.transform.a - comun.RES) < 1e-12 and abs(-s.transform.e - comun.RES) < 1e-12
    return Window(int(round(col)), int(round(fil)), comun.ANCHO, comun.ALTO)


def _guardar_tif(ruta, arr, tr, crs, etiquetas):
    import rasterio
    perfil = dict(driver="GTiff", dtype="uint8", width=arr.shape[1], height=arr.shape[0], count=1,
                  crs=crs, transform=tr, compress="deflate", tiled=False)
    with rasterio.open(ruta, "w", **perfil) as d:
        d.write(arr, 1)
        d.update_tags(**etiquetas)


def descargar_gsw():
    """JRC GSW v1.5 (occurrence y extent) desde el servidor del JRC; si falla, occurrence v1.3 de Planetary Computer.

    Devuelve {'occurrence': ruta, 'extent': ruta o None, 'version': '1.5'|'1.3'}.
    """
    import rasterio
    try:
        for c, ruta in RUTA_GSW15.items():
            if os.path.exists(ruta):
                print("GSW v1.5 en caché:", ruta)
                continue
            url = URL_GSW15.format(c=c)

            def leer(url=url):
                with rasterio.open("/vsicurl/" + url) as s:
                    w = _ventana_gsw(s)
                    return s.read(1, window=w), s.window_transform(w), s.crs
            arr, tr, crs = _reintentar(leer, intentos=4)
            _guardar_tif(ruta, arr, tr, crs, {"url": url, "version": "1.5", "periodo": "1984/2024"})
            print("GSW v1.5 guardado:", ruta, arr.shape, np.unique(arr)[:12])
        return {"occurrence": RUTA_GSW15["occurrence"], "extent": RUTA_GSW15["extent"], "version": "1.5"}
    except Exception as e:  # noqa: BLE001
        print("AVISO: GSW v1.5 no disponible, se usa la v1.3 de Planetary Computer:", e)
    if not os.path.exists(RUTA_GSW13):
        import planetary_computer
        import pystac_client
        cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1",
                                        modifier=planetary_computer.sign_inplace)
        items = list(cat.search(collections=["jrc-gsw"], bbox=[comun.OESTE, comun.SUR, comun.ESTE, comun.NORTE]).items())
        assert len(items) == 1, [i.id for i in items]
        it = items[0]
        href = it.assets["occurrence"].href

        def leer():
            with rasterio.open(href) as s:
                w = _ventana_gsw(s)
                return s.read(1, window=w), s.window_transform(w), s.crs
        arr, tr, crs = _reintentar(leer)
        _guardar_tif(RUTA_GSW13, arr, tr, crs, {"item": it.id, "version": "1.3",
                     "periodo": f"{it.properties.get('start_datetime')}/{it.properties.get('end_datetime')}"})
    return {"occurrence": RUTA_GSW13, "extent": None, "version": "1.3"}


def _merc(lon, lat):
    r = 6378137.0
    return r * math.radians(lon), r * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def _leer_chm_bloque(url, ventana, f):
    """Lee filas de una tesela CHM (tiras de 1 fila) y promedia bloques f×f. Devuelve (suma, n) por bloque."""
    import rasterio
    with rasterio.open("/vsicurl/" + url) as s:
        a = s.read(1, window=ventana).astype(np.float32)
    h, w = a.shape
    a = a.reshape(h // f, f, w // f, f)
    return a.mean(axis=(1, 3))


def descargar_chm():
    """Altura del dosel de Meta/WRI CHM v1 (1 m) agregada a bloques de 8×8 px (≈ 9,6 m) sobre el dominio DOM.

    Las teselas v1 son GeoTIFF de 65.536 × 65.536 px en EPSG:3857, en tiras de UNA fila y sin resúmenes: no hay forma
    de leer solo las columnas del dominio, así que se leen (por ventanas de filas, en paralelo) solo las filas que
    cruzan el dominio y se promedia en bloques alineados con la malla de la tesela. Caché en fuentes/inundacion/.
    Devuelve (arreglo float32 en m, transform EPSG:3857).
    """
    import rasterio
    from rasterio.transform import Affine
    from rasterio.windows import Window
    if os.path.exists(RUTA_CHM):
        with rasterio.open(RUTA_CHM) as s:
            print("CHM en caché:", RUTA_CHM)
            return s.read(1), s.transform
    xo, ys = _merc(DOM_OESTE, DOM_SUR)
    xe, yn = _merc(DOM_ESTE, DOM_NORTE)
    f = CHM_FACTOR
    partes = []
    for q in TESELAS_CHM:
        url = URL_CHM.format(q=q)
        with rasterio.open("/vsicurl/" + url) as s:
            assert s.crs.to_epsg() == 3857 and s.count == 1 and s.dtypes[0] == "uint8"
            tr = s.transform
            c0 = max(0, int(math.floor((xo - tr.c) / tr.a / f)) * f)
            c1 = min(s.width, int(math.ceil((xe - tr.c) / tr.a / f)) * f)
            r0 = max(0, int(math.floor((tr.f - yn) / -tr.e / f)) * f)
            r1 = min(s.height, int(math.ceil((tr.f - ys) / -tr.e / f)) * f)
            if c1 <= c0:
                continue
            paso_f = 128
            vent = [Window(c0, r, c1 - c0, min(paso_f, r1 - r)) for r in range(r0, r1, paso_f)]
            partes.append((q, url, c0, r0, tr, vent))
    print(f"CHM: {sum(len(p[5]) for p in partes)} ventanas de filas en {len(partes)} teselas…", flush=True)
    t0 = time.time()
    bloques = []
    for q, url, c0, r0, tr, vent in partes:
        with ThreadPoolExecutor(max_workers=6) as ex:
            res = list(ex.map(lambda w: _reintentar(_leer_chm_bloque, url, w, f), vent))
        bloques.append(np.vstack(res))
        print(f"  tesela {q}: {bloques[-1].shape} en {time.time() - t0:.0f} s", flush=True)
    assert len({(p[3]) for p in partes}) == 1 and len({b.shape[0] for b in bloques}) == 1
    # contigüidad de las teselas en la malla de 1,19 m
    for (qa, _, ca, _, ta, va), (qb, _, cb, _, tb, _) in zip(partes, partes[1:]):
        assert abs((ta.c + (ca + va[0].width) * ta.a) - (tb.c + cb * tb.a)) < 1e-3, (qa, qb)
    mosaico = np.hstack(bloques).astype(np.float32)
    q0, _, c0, r0, tr0, _ = partes[0]
    trm = Affine(tr0.a * f, 0, tr0.c + c0 * tr0.a, 0, tr0.e * f, tr0.f + r0 * tr0.e)
    perfil = dict(driver="GTiff", dtype="float32", width=mosaico.shape[1], height=mosaico.shape[0], count=1,
                  crs="EPSG:3857", transform=trm, compress="deflate", predictor=3, tiled=True)
    with rasterio.open(RUTA_CHM, "w", **perfil) as d:
        d.write(mosaico, 1)
        d.update_tags(fuente=URL_CHM, teselas=",".join(TESELAS_CHM), factor=str(f), fecha=time.strftime("%Y-%m-%d"))
    print("CHM guardado:", RUTA_CHM, mosaico.shape, f"{time.time() - t0:.0f} s")
    return mosaico, trm


def fechas_chm():
    """Fecha de las imágenes del CHM v1 (ráster global de 0,01°) en la rejilla común: {valor: celdas}.

    Valores interpretados como año − 2000 (p. ej. 18,25 = abril de 2018): es la codificación documentada para la v2
    (Brandt et al. 2026); para la v1 se SUPONE la misma por el rango de valores (14–19).
    """
    import rasterio
    from rasterio.windows import from_bounds
    if not os.path.exists(RUTA_CHM_FECHA):
        def leer():
            with rasterio.open("/vsicurl/" + URL_CHM_FECHA) as s:
                w = from_bounds(DOM_OESTE, DOM_SUR, DOM_ESTE, DOM_NORTE, transform=s.transform).round_offsets().round_lengths()
                return s.read(1, window=w), s.window_transform(w), s.crs
        a, tr, crs = _reintentar(leer, intentos=3)
        perfil = dict(driver="GTiff", dtype="float32", width=a.shape[1], height=a.shape[0], count=1, crs=crs, transform=tr)
        with rasterio.open(RUTA_CHM_FECHA, "w", **perfil) as d:
            d.write(a.astype(np.float32), 1)
    with rasterio.open(RUTA_CHM_FECHA) as s:
        a, tr = s.read(1), s.transform
    filas, cols = np.indices(a.shape)
    lon, lat = tr * (cols + 0.5, filas + 0.5)
    en = (lon >= comun.OESTE) & (lon <= comun.ESTE) & (lat >= comun.SUR) & (lat <= comun.NORTE) & (a > 0)
    v = a[en]
    return {"anios_rejilla": sorted({round(2000 + float(x), 2) for x in v}),
            "min": round(2000 + float(v.min()), 2), "max": round(2000 + float(v.max()), 2),
            "mediana": round(2000 + float(np.median(v)), 2), "celdas_0_01_grados": int(v.size)} if v.size else None


def descargar_ideam():
    """Polígonos del IDEAM que tocan la rejilla común (solo para validación). Devuelve {capa: FeatureCollection}.

    Si el servidor falla con la geometría completa (le pasa a la mancha 2020–2022, que cubre todo el valle), se pide
    generalizada a 0,00005° (≈ 5,5 m; irrelevante para manchas de borde grueso y escala no declarada). Una capa que falla se omite.
    """
    import requests
    out = {}
    for capa, (clave, nombre, _) in IDEAM_CAPAS.items():
        ruta = os.path.join(CACHE, f"ideam_{capa}_{clave}.geojson")
        if not os.path.exists(ruta):
            base = dict(where="1=1", geometry=f"{comun.OESTE},{comun.SUR},{comun.ESTE},{comun.NORTE}",
                        geometryType="esriGeometryEnvelope", inSR=4326, spatialRel="esriSpatialRelIntersects",
                        outFields="*", returnGeometry="true", outSR=4326, f="geojson")

            def pedir(params):
                r = requests.get(f"{IDEAM_SERVICIO}/{capa}/query", params=params, headers=UA, timeout=300)
                r.raise_for_status()
                d = r.json()
                assert d.get("type") == "FeatureCollection", str(d)[:300]
                assert not d.get("exceededTransferLimit"), "respuesta truncada"
                return d
            variantes = [base] + ([base | {"maxAllowableOffset": 0.00005}] if capa != 0 else [])
            d = None
            for params in variantes:
                try:
                    d = _reintentar(pedir, params, intentos=3)
                    break
                except Exception as e:  # noqa: BLE001
                    print(f"  IDEAM capa {capa}: falla con {params.get('maxAllowableOffset', 'geometría completa')}: {e}", flush=True)
            if d is None:
                print(f"AVISO: IDEAM capa {capa} ({nombre}) no disponible; se omite", flush=True)
                continue
            d["consulta"] = {"servicio": IDEAM_SERVICIO, "capa": capa, "nombre": nombre, "fecha": time.strftime("%Y-%m-%d"),
                             "generalizacion_grados": params.get("maxAllowableOffset")}
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False)
            print(f"IDEAM capa {capa} ({nombre}): {len(d['features'])} polígonos", flush=True)
        out[capa] = json.load(open(ruta, encoding="utf-8"))
    return out


# ============================================================== 2. geometría de los ríos (OSM)
def _anillos_relacion(e):
    from shapely.geometry import LineString
    from shapely.ops import polygonize, unary_union
    ext, inn = [], []
    for m in e["members"]:
        if m["type"] != "way" or "geometry" not in m:
            continue
        ls = LineString([(p["lon"], p["lat"]) for p in m["geometry"]])
        (inn if m.get("role") == "inner" else ext).append(ls)
    pe = unary_union(list(polygonize(unary_union(ext)))) if ext else None
    pi = unary_union(list(polygonize(unary_union(inn)))) if inn else None
    if pe is None:
        return None
    return pe.difference(pi) if pi is not None and not pi.is_empty else pe


def rios_osm():
    """Geometrías lon/lat recortadas al dominio: {'La Vieja': (lineas, poligonos), 'Cauca': (...)}, otros_poligonos."""
    from shapely.geometry import LineString, Polygon, box
    from shapely.ops import unary_union
    caja = box(DOM_OESTE, DOM_SUR, DOM_ESTE, DOM_NORTE)
    d = comun.osm()
    lineas = {"La Vieja": [LineString([(lon, lat) for lat, lon in d["rio_la_vieja"]])],
              "Cauca": [LineString([(lon, lat) for lat, lon in d["rio_cauca"]])]}
    nombres = {"Río La Vieja": "La Vieja", "Río Cauca": "Cauca"}
    base = json.load(open(os.path.join(comun.FUENTES, "osm-base.json"), encoding="utf-8"))
    for e in base["elements"]:
        t = e.get("tags", {})
        if e["type"] == "way" and t.get("waterway") == "river" and t.get("name") in nombres:
            lineas[nombres[t["name"]]].append(LineString([(p["lon"], p["lat"]) for p in e["geometry"]]))
    verdes = json.load(open(os.path.join(comun.FUENTES, "osm-verdes-equipamientos.json"), encoding="utf-8"))
    pols = {"La Vieja": [], "Cauca": []}
    otros_pol = []
    for e in verdes["elements"]:
        t = e.get("tags", {})
        if t.get("natural") != "water" or t.get("water") != "river":
            continue
        nombre = t.get("name") or ""
        if e["type"] == "way":
            g = e["geometry"]
            if len(g) < 4 or (g[0]["lat"], g[0]["lon"]) != (g[-1]["lat"], g[-1]["lon"]):
                continue
            pol = Polygon([(p["lon"], p["lat"]) for p in g]).buffer(0)
        else:
            pol = _anillos_relacion(e)
        if pol is None or pol.is_empty:
            continue
        pol = pol.intersection(caja)
        if pol.is_empty:
            continue
        if nombre in nombres:
            pols[nombres[nombre]].append(pol)
        elif nombre in ("Rio Consota",):
            otros_pol.append(pol)
    rios = {k: (unary_union([l.intersection(caja) for l in lineas[k]]), unary_union(pols[k]) if pols[k] else None)
            for k in lineas}
    return rios, unary_union(otros_pol) if otros_pol else None


def descargar_cauces_osm():
    """Vías fluviales de OSM (river, stream, canal, drain, ditch) en el dominio DOM, con geometría. Caché en fuentes/.

    La API pública de Overpass responde con requests y un User-Agent identificable; si falla, se prueban espejos.
    Devuelve el JSON de Overpass o None si no se pudo obtener.
    """
    import requests
    if os.path.exists(RUTA_OSM_CAUCES):
        print("cauces OSM en caché:", RUTA_OSM_CAUCES)
        return json.load(open(RUTA_OSM_CAUCES, encoding="utf-8"))
    q = (f'[out:json][timeout:120];way["waterway"~"^(river|stream|canal|drain|ditch)$"]'
         f"({DOM_SUR},{DOM_OESTE},{DOM_NORTE},{DOM_ESTE});out tags geom;")
    for url in OVERPASS:
        try:
            r = requests.post(url, data={"data": q}, headers=UA, timeout=180)
            r.raise_for_status()
            d = r.json()
            assert "elements" in d
        except Exception as e:  # noqa: BLE001
            print(f"  Overpass {url}: {e}", flush=True)
            continue
        d["consulta"] = {"servidor": url, "consulta": q, "fecha": time.strftime("%Y-%m-%d")}
        with open(RUTA_OSM_CAUCES, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
        print(f"cauces OSM: {len(d['elements'])} vías desde {url}", flush=True)
        return d
    print("AVISO: no se pudieron descargar los cauces menores de OSM; la red menor sale solo del DEM", flush=True)
    return None


def cauces_osm(d):
    """Clasifica las vías fluviales OSM (sin La Vieja ni Cauca, que ya son el cauce mayor).

    Devuelve lista de dicts {id, tipo ('rio'|'arroyo'|'canal'), nombre, alcantarilla, geom (LineString lon/lat)}.
    Las alcantarillas (tunnel=culvert) se conservan como tramos de la red: el agua sigue pasando por ellas.
    """
    from shapely.geometry import LineString
    out = []
    if not d:
        return out
    for e in d["elements"]:
        t = e.get("tags", {})
        ww, nombre = t.get("waterway"), t.get("name") or ""
        if e.get("type") != "way" or len(e.get("geometry", [])) < 2 or nombre in ("Río La Vieja", "Río Cauca"):
            continue
        tipo = {"river": "rio", "stream": "arroyo", "canal": "canal", "drain": "canal", "ditch": "canal"}.get(ww)
        if tipo is None:
            continue
        out.append({"id": e["id"], "tipo": tipo, "waterway": ww, "nombre": nombre,
                    "alcantarilla": t.get("tunnel") in ("culvert", "yes"),
                    "geom": LineString([(p["lon"], p["lat"]) for p in e["geometry"]])})
    return out


# ============================================================== 3. hidrología D8
VECINOS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
GRUPO_MAYOR, GRUPO_OTRO, GRUPO_DERIVADO, GRUPO_OSM_MENOR = 1, 2, 3, 4


def priority_flood_eps(z):
    """Relleno Priority-Flood + ε (Barnes, Lehman y Mulla 2014). Devuelve (dem_relleno, orden).

    Cada celda no semilla queda estrictamente por encima de la celda desde la que se alcanzó, de modo
    que el D8 posterior siempre encuentra un vecino más bajo. 'orden' es el orden de extracción
    (no decreciente en la cota rellenada): orden topológico de aguas abajo hacia aguas arriba.
    """
    from scipy.ndimage import binary_dilation
    H, W = z.shape
    invalido = ~np.isfinite(z)
    borde = np.zeros((H, W), bool)
    borde[0, :] = borde[-1, :] = borde[:, 0] = borde[:, -1] = True
    semillas = np.flatnonzero(((borde | binary_dilation(invalido, np.ones((3, 3), bool))) & ~invalido).ravel())
    zf = np.where(invalido, np.inf, z).astype(np.float64).ravel().tolist()
    cerrado = bytearray(invalido.ravel().astype(np.uint8).tobytes())
    heap = []
    for k, i in enumerate(semillas.tolist()):
        heap.append((zf[i], k, i))
        cerrado[i] = 1
    heapq.heapify(heap)
    cont = len(heap)
    orden = []
    nextafter, inf = math.nextafter, math.inf
    pop, push, add = heapq.heappop, heapq.heappush, orden.append
    desp = [(dr, dc, dr * W + dc) for dr, dc in VECINOS]
    while heap:
        h, _, i = pop(heap)
        add(i)
        r, c = divmod(i, W)
        for dr, dc, di in desp:
            rr, cc = r + dr, c + dc
            if rr < 0 or rr >= H or cc < 0 or cc >= W:
                continue
            j = i + di
            if cerrado[j]:
                continue
            cerrado[j] = 1
            zj = zf[j]
            if zj <= h:
                zj = nextafter(h, inf)
                zf[j] = zj
            push(heap, (zj, cont, j))
            cont += 1
    zf = np.array(zf, dtype=np.float64).reshape(H, W)
    zf[invalido] = np.nan
    return zf, np.array(orden, dtype=np.int64)


def d8(zf):
    """Índice lineal de la celda aguas abajo (−1 = salida del dominio)."""
    H, W = zf.shape
    pad = np.pad(zf, 1, constant_values=np.nan)
    mejor = np.zeros((H, W))
    abajo = np.full((H, W), -1, np.int64)
    filas, cols = np.indices((H, W))
    for dr, dc in VECINOS:
        dist = PASO * (math.sqrt(2) if dr and dc else 1.0)
        zn = pad[1 + dr:1 + dr + H, 1 + dc:1 + dc + W]
        with np.errstate(invalid="ignore"):
            p = (zf - zn) / dist
        m = np.isfinite(p) & (p > mejor)
        mejor[m] = p[m]
        abajo[m] = ((filas + dr) * W + (cols + dc))[m]
    abajo[~np.isfinite(zf)] = -1
    return abajo.ravel()


def acumulacion(abajo, orden, valido):
    acc = valido.ravel().astype(np.float64).tolist()
    ab = abajo.tolist()
    for i in orden[::-1].tolist():          # de aguas arriba hacia aguas abajo
        d = ab[i]
        if d >= 0:
            acc[d] += acc[i]
    return np.array(acc)


def destino_drenaje(abajo, drenaje):
    """Para cada celda, índice de la celda de la red a la que llega por D8 (−1 si sale sin tocarla)."""
    n = abajo.size
    idx = np.arange(n)
    t = np.where(drenaje, idx, abajo)
    for _ in range(64):
        tt = np.where(t >= 0, t[np.maximum(t, 0)], -1)
        tt = np.where(drenaje, idx, tt)
        if np.array_equal(tt, t):
            break
        t = tt
    return t


def perfil_minimo(z, abajo, orden, grupo):
    """Mínimo acumulado aguas abajo, solo por enlaces D8 cuyos dos extremos son del mismo grupo (≠ 0)."""
    zl = np.asarray(z, dtype=np.float64).ravel().tolist()
    ab = abajo.tolist()
    g = grupo.ravel().tolist()
    for i in orden[::-1].tolist():          # de aguas arriba hacia aguas abajo
        gi = g[i]
        if gi:
            d = ab[i]
            if d >= 0 and g[d] == gi and zl[d] > zl[i]:
                zl[d] = zl[i]
    return np.array(zl)


def aplicar_piso(zc, menor, destino_mayor, zc_mayor):
    """La cota de un cauce menor no baja de la del río mayor (La Vieja o Cauca) al que acaba entregando.

    Garantiza hand (toda la red) ≤ hand_rio_mayor en cada celda, sin propagar aguas arriba los
    resaltos del DSM dentro de los cauces menores.
    """
    zc = zc.copy()
    i = np.flatnonzero(menor & (destino_mayor >= 0))
    piso = zc_mayor[destino_mayor[i]]
    zc[i] = np.maximum(zc[i], piso)
    return zc


def calibrar_dosel(z, ch, excluir):
    """Exceso del DSM sobre el suelo en función de la altura media del dosel (CHM), calibrado en Cartago.

    En terreno llano (desviación típica ≤ CAL_SD_MAX m de las celdas sin dosel en una ventana de CAL_VENTANA celdas) y fuera de
    la cabecera, exceso = altura de la celda − media de las celdas sin dosel (CHM < 0,5 m) de la ventana. Se toma la mediana del
    exceso por intervalos de CHM; la corrección es la interpolación lineal de esas medianas (0 en CHM = 0), monótona y nunca mayor
    que la propia altura del dosel; por encima del último intervalo se extrapola con la razón exceso/CHM de ese intervalo.
    """
    from scipy.ndimage import uniform_filter
    zz = np.asarray(z, np.float64)
    c = np.asarray(ch, np.float64)
    ok = np.isfinite(zz) & np.isfinite(c)
    abierto = ok & (c < 0.5) & ~excluir
    k = CAL_VENTANA
    n = uniform_filter(abierto.astype(float), k)
    s1 = uniform_filter(np.where(abierto, zz, 0.0), k)
    s2 = uniform_filter(np.where(abierto, zz * zz, 0.0), k)
    with np.errstate(invalid="ignore", divide="ignore"):
        m = s1 / n
        sd = np.sqrt(np.maximum(s2 / n - m * m, 0))
    llano = (n >= 0.3) & (sd <= CAL_SD_MAX) & ok & ~excluir
    exceso = zz - m
    tabla = []
    for a, b2 in zip(CAL_BORDES[:-1], CAL_BORDES[1:]):
        mm = llano & (c >= a) & (c < b2)
        if mm.sum() >= 30:
            tabla.append({"chm_desde_m": a, "chm_hasta_m": b2, "celdas": int(mm.sum()), "chm_mediana_m": round(float(np.median(c[mm])), 2),
                          "exceso_dsm_mediana_m": round(float(np.median(exceso[mm])), 2),
                          "exceso_dsm_p25_m": round(float(np.percentile(exceso[mm], 25)), 2),
                          "exceso_dsm_p75_m": round(float(np.percentile(exceso[mm], 75)), 2)})
    control = llano & (c < 0.5)
    xs = np.array([0.0] + [t["chm_mediana_m"] for t in tabla])
    ys = np.maximum.accumulate(np.maximum(np.array([0.0] + [t["exceso_dsm_mediana_m"] for t in tabla]), 0))
    ys = np.minimum(ys, xs)
    razon_final = float(ys[-1] / xs[-1])
    corr = np.where(c <= xs[-1], np.interp(c, xs, ys), c * razon_final)
    corr = np.where(ok, np.clip(corr, 0, c), 0.0)
    info = {"tabla": tabla, "curva_chm_m": [round(float(x), 2) for x in xs], "curva_correccion_m": [round(float(y), 2) for y in ys],
            "razon_extrapolacion": round(razon_final, 3),
            "control_celdas_sin_dosel_exceso_mediana_m": round(float(np.median(exceso[control])), 3), "control_celdas": int(control.sum()),
            "ventana_celdas": k, "desviacion_max_m": CAL_SD_MAX}
    return corr, info


def evaluar_canales(z, canales, f_utm, tr_utm, H, W):
    """Prueba topográfica de cada canal OSM: ¿corre por lo bajo (drenaje) o a media ladera / en terraplén (riego)?

    Cada 30 m del eje se compara el mínimo 3×3 del DEM corregido con la mediana de los flancos a 60–150 m a cada lado
    (perpendicular). Se acepta como cauce de drenaje si en ≥ 60 % de los puntos el eje está a ≤ 0,5 m del flanco más bajo o
    por debajo. Las alcantarillas de canal heredan la decisión de los canales con los que comparten extremo.
    """
    from scipy.ndimage import minimum_filter
    from shapely.ops import transform as stransform
    zmin3 = minimum_filter(np.where(np.isfinite(z), z, np.inf), size=3)
    inv = ~tr_utm

    def zen(x, y, arr):
        cc, ff = inv * (x, y)
        ff, cc = int(ff), int(cc)
        return float(arr[ff, cc]) if 0 <= ff < H and 0 <= cc < W and np.isfinite(arr[ff, cc]) else np.nan
    res = {}
    for cn in canales:
        if cn["alcantarilla"]:
            continue
        g = stransform(f_utm, cn["geom"])
        if g.length < 90:
            continue
        pts_ok = pts = 0
        for dd in np.arange(15, g.length, 30.0):
            p0, p1 = g.interpolate(max(dd - 15, 0)), g.interpolate(min(dd + 15, g.length))
            dx, dy = p1.x - p0.x, p1.y - p0.y
            nn = math.hypot(dx, dy)
            if nn == 0:
                continue
            nx, ny = -dy / nn, dx / nn
            p = g.interpolate(dd)
            zl = zen(p.x, p.y, zmin3)
            lados = [[zen(p.x + s * o * nx, p.y + s * o * ny, z) for o in (60, 90, 120, 150)] for s in (1, -1)]
            if not np.isfinite(zl) or not all(np.isfinite(x).any() for x in lados):
                continue
            fl = [float(np.nanmedian(x)) for x in lados]
            pts += 1
            pts_ok += zl <= min(fl) + 0.5
        res[cn["id"]] = {"puntos": pts, "pct_en_lo_bajo": round(100.0 * pts_ok / pts, 1) if pts else None,
                         "drenaje": bool(pts and pts_ok / pts >= 0.6)}
    # alcantarillas: heredan de los canales que tocan
    extremos = {}
    for cn in canales:
        if not cn["alcantarilla"] and cn["id"] in res:
            for q in (cn["geom"].coords[0], cn["geom"].coords[-1]):
                extremos.setdefault(q, []).append(res[cn["id"]]["drenaje"])
    for cn in canales:
        if cn["alcantarilla"]:
            v = [x for q in (cn["geom"].coords[0], cn["geom"].coords[-1]) for x in extremos.get(q, [])]
            res[cn["id"]] = {"puntos": 0, "pct_en_lo_bajo": None, "drenaje": bool(v) and all(v), "alcantarilla": True}
    return res


def hidrologia(dem_geo, tr_geo, crs_geo, chm=None, cauces=None):
    """Pasos 3–9 comunes a todas las variantes: DEM en UTM, corrección del dosel, quema, Priority-Flood, D8, acumulación.

    chm = (arreglo, transform EPSG:3857) de la altura del dosel; None → sin corrección (DSM tal cual).
    cauces = lista de cauces_osm(); None o [] → la red menor sale solo del DEM.
    """
    from pyproj import Transformer
    from rasterio.features import rasterize
    from rasterio.transform import from_origin
    from rasterio.warp import Resampling, reproject
    from scipy.ndimage import binary_dilation, distance_transform_edt, minimum_filter
    from shapely.ops import transform as stransform

    # ---- rejilla UTM inscrita en el dominio
    a_utm = Transformer.from_crs("EPSG:4326", CRS_UTM, always_xy=True)
    lons = np.linspace(DOM_OESTE, DOM_ESTE, 200)
    lats = np.linspace(DOM_SUR, DOM_NORTE, 200)
    xo, _ = a_utm.transform(np.full_like(lats, DOM_OESTE), lats)
    xe, _ = a_utm.transform(np.full_like(lats, DOM_ESTE), lats)
    _, ys = a_utm.transform(lons, np.full_like(lons, DOM_SUR))
    _, yn = a_utm.transform(lons, np.full_like(lons, DOM_NORTE))
    x0 = math.ceil((xo.max() + PASO) / PASO) * PASO
    x1 = math.floor((xe.min() - PASO) / PASO) * PASO
    y0 = math.ceil((ys.max() + PASO) / PASO) * PASO
    y1 = math.floor((yn.min() - PASO) / PASO) * PASO
    W, H = int((x1 - x0) / PASO), int((y1 - y0) / PASO)
    tr_utm = from_origin(x0, y1, PASO, PASO)
    z_dsm = np.full((H, W), np.nan, np.float32)
    reproject(dem_geo, z_dsm, src_transform=tr_geo, src_crs=crs_geo, src_nodata=np.nan,
              dst_transform=tr_utm, dst_crs=CRS_UTM, dst_nodata=np.nan, resampling=Resampling.bilinear)
    print(f"UTM 18N {W}×{H} celdas de {PASO:.0f} m ({W * PASO / 1000:.1f} × {H * PASO / 1000:.1f} km); "
          f"sin dato: {int((~np.isfinite(z_dsm)).sum())}")
    f_utm = a_utm.transform

    def ras(geom, todo):
        if geom is None or geom.is_empty:
            return np.zeros((H, W), bool)
        return rasterize([(stransform(f_utm, geom), 1)], out_shape=(H, W), transform=tr_utm, fill=0,
                         all_touched=todo, dtype="uint8").astype(bool)

    # ---- corrección del dosel (DSM → aproximación al terreno bajo los árboles)
    ch_u = None
    cal = None
    z0 = z_dsm
    if chm is not None:
        ch_u = np.full((H, W), np.nan, np.float32)
        reproject(chm[0], ch_u, src_transform=chm[1], src_crs="EPSG:3857", src_nodata=np.nan,
                  dst_transform=tr_utm, dst_crs=CRS_UTM, dst_nodata=np.nan, resampling=Resampling.average)
        cab = comun._poligono(comun.osm()["cabecera"]).buffer(0.003)      # ≈ 330 m de margen: fuera de la ciudad
        corr, cal = calibrar_dosel(z_dsm, ch_u, ras(cab, False))
        z0 = (z_dsm - corr).astype(np.float32)
        print(f"corrección del dosel: curva CHM {cal['curva_chm_m']} → {cal['curva_correccion_m']} m; control sin dosel "
              f"{cal['control_celdas_sin_dosel_exceso_mediana_m']} m; corrección p50/p90/p99/máx "
              f"{np.percentile(corr, 50):.2f}/{np.percentile(corr, 90):.2f}/{np.percentile(corr, 99):.2f}/{corr.max():.2f} m")
        cal["correccion_m"] = {"p50": round(float(np.percentile(corr, 50)), 2), "p90": round(float(np.percentile(corr, 90)), 2),
                               "p99": round(float(np.percentile(corr, 99)), 2), "max": round(float(corr.max()), 2)}

    # ---- ríos (etiqueta 1 = La Vieja, 2 = Cauca)
    rios, pol_otros = rios_osm()
    rio_id = np.zeros((H, W), np.uint8)
    n_lin = n_pol = 0
    for k, nombre in ((2, "Cauca"), (1, "La Vieja")):     # La Vieja se escribe al final (prevalece en la confluencia)
        lin, pol = rios[nombre]
        ml, mp = ras(lin, True), ras(pol, False)
        n_lin += int(ml.sum())
        n_pol += int(mp.sum())
        rio_id[ml | mp] = k
    mayor = rio_id > 0
    otros = ras(pol_otros, False) & ~mayor
    # ---- cauces menores de OSM: otros ríos (como el Consota) y arroyos/canales de drenaje (red menor mapeada)
    canales_eval = {}
    menor_osm = np.zeros((H, W), bool)
    n_tipo = {}
    if cauces:
        from shapely.ops import unary_union
        canales = [c for c in cauces if c["tipo"] == "canal"]
        canales_eval = evaluar_canales(z0, canales, f_utm, tr_utm, H, W)
        rios_m = [c["geom"] for c in cauces if c["tipo"] == "rio"]
        menores = [c["geom"] for c in cauces if c["tipo"] == "arroyo"
                   or (c["tipo"] == "canal" and canales_eval.get(c["id"], {}).get("drenaje"))]
        if rios_m:
            otros |= ras(unary_union(rios_m), True) & ~mayor
        if menores:
            menor_osm = ras(unary_union(menores), True) & ~mayor & ~otros
        for t in ("rio", "arroyo", "canal"):
            n_tipo[t] = sum(1 for c in cauces if c["tipo"] == t)
    quemado = mayor | otros | menor_osm
    print(f"cauce mayor: {int(mayor.sum())} celdas (La Vieja {int((rio_id == 1).sum())}, Cauca {int((rio_id == 2).sum())}; "
          f"ejes {n_lin}, polígonos {n_pol}); otros ríos OSM: {int(otros.sum())}; arroyos y canales de drenaje OSM: "
          f"{int(menor_osm.sum())}; vías OSM por tipo {n_tipo}; canales aceptados como drenaje "
          f"{[k for k, v in canales_eval.items() if v['drenaje']]}")

    # ---- D8
    t0 = time.time()
    zq = np.where(mayor | otros, z0 - PROFUNDIDAD_QUEMA, np.where(menor_osm, z0 - PROFUNDIDAD_QUEMA_MENOR, z0)).astype(np.float64)
    zf, orden = priority_flood_eps(zq)
    relleno = zf - zq
    print(f"Priority-Flood: {time.time() - t0:.1f} s; celdas elevadas por el relleno: "
          f"{int((relleno > 0.01).sum())} (> 1 cm), {int((relleno > UMBRAL_RELLENO_M).sum())} (> {UMBRAL_RELLENO_M} m), "
          f"máx {np.nanmax(relleno):.1f} m")
    abajo = d8(zf)
    valido = np.isfinite(z0)
    pos = np.empty(abajo.size, np.int64)
    pos[orden] = np.arange(orden.size)
    tiene = abajo >= 0
    assert (pos[abajo[tiene]] < pos[np.flatnonzero(tiene)]).all(), "D8 no es coherente con el orden topológico"
    acc = acumulacion(abajo, orden, valido)
    print(f"acumulación máx {acc.max() * PASO * PASO / 1e6:.0f} km² (cuencas truncadas por el dominio en los ríos mayores)")
    z0d = z0.astype(np.float64)
    # Lámina de agua de los ríos OSM: mínimo 5×5 del DSM SIN corregir (el agua abierta se ve en el DSM; la corrección del
    # dosel, calibrada en tierra, podría bajar las orillas por debajo del agua). Arroyos y canales OSM: mínimo 3×3 del DEM
    # corregido (absorbe el desfase del eje OSM). Cauces derivados: la propia celda del DEM corregido.
    zmin5 = minimum_filter(np.where(valido, z_dsm.astype(np.float64), np.inf), size=5)
    zmin3 = minimum_filter(np.where(valido, z0d, np.inf), size=3)
    zraw = z0d.copy()
    zraw[mayor | otros] = zmin5[mayor | otros]
    zraw[menor_osm] = zmin3[menor_osm]
    # perfil de los ríos mayores: mínimo acumulado solo entre celdas de río mayor (no recibe pozos de otros cauces)
    zc_mayor = perfil_minimo(zraw, abajo, orden, mayor.astype(np.uint8))
    rebaje_mayor = (zraw.ravel() - zc_mayor)[mayor.ravel()]
    print(f"perfil río mayor: rebaje respecto al mínimo 5×5 p50 {np.median(rebaje_mayor):.2f} m, p99 "
          f"{np.percentile(rebaje_mayor, 99):.2f} m, máx {rebaje_mayor.max():.2f} m; > 2 m: {int((rebaje_mayor > 2).sum())} celdas")
    dist_u = distance_transform_edt(~mayor) * PASO
    cerca_osm = binary_dilation(menor_osm | otros, iterations=int(round(CERCA_OSM_M / PASO))) if (menor_osm | otros).any() \
        else np.zeros((H, W), bool)
    destino_mayor = destino_drenaje(abajo, (mayor & valido).ravel())
    a_geo = Transformer.from_crs(CRS_UTM, "EPSG:4326", always_xy=True)
    ff, cc = np.indices((H, W))
    lo_u, la_u = a_geo.transform(*(tr_utm * (cc + 0.5, ff + 0.5)))
    en_rejilla = (lo_u >= comun.OESTE) & (lo_u <= comun.ESTE) & (la_u >= comun.SUR) & (la_u <= comun.NORTE)
    return dict(z0=z0, z_dsm=z_dsm, ch_u=ch_u, calibracion_dosel=cal, zf=zf, relleno=relleno, orden=orden, abajo=abajo, acc=acc,
                valido=valido, mayor=mayor, rio_id=rio_id, otros=otros, menor_osm=menor_osm, cerca_osm=cerca_osm,
                canales_evaluados=canales_eval, quemado=quemado, zraw=zraw, zc_mayor=zc_mayor, dist_u=dist_u,
                destino_mayor=destino_mayor, en_rejilla=en_rejilla,
                tr_utm=tr_utm, H=H, W=W,
                rebaje_mayor={"p50_m": round(float(np.median(rebaje_mayor)), 2),
                              "p99_m": round(float(np.percentile(rebaje_mayor, 99)), 2),
                              "max_m": round(float(rebaje_mayor.max()), 2),
                              "celdas_mas_de_2m": int((rebaje_mayor > 2).sum()), "celdas": int(rebaje_mayor.size)})


def calcular_hand(b, umbral_km2=UMBRAL_KM2, umbral_relleno=UMBRAL_RELLENO_M, solo_mayor=False, informar=False):
    """Pasos 8–10: red de drenaje, cota del cauce y HAND (m) en la malla UTM.

    umbral_km2 = None → sin cauces derivados (solo ríos OSM quemados).
    umbral_relleno = None → no se excluyen los tramos derivados sobre relleno.
    solo_mayor = True → la red es solo La Vieja + Cauca (HAND respecto a los ríos mayores).
    """
    H, W, valido, quemado, mayor, otros = b["H"], b["W"], b["valido"], b["quemado"], b["mayor"], b["otros"]
    vacio = np.zeros((H, W), bool)
    sustituidos = vacio
    if solo_mayor:
        derivados_todos, excluidos = vacio, vacio
        red = mayor & valido
    else:
        if umbral_km2 is None:
            derivados_todos = vacio
        else:
            derivados_todos = (b["acc"] * PASO * PASO / 1e6 >= umbral_km2).reshape(H, W) & valido & ~quemado
        sustituidos = derivados_todos & b["cerca_osm"]          # el cauce OSM mapeado sustituye al derivado paralelo
        derivados_todos = derivados_todos & ~b["cerca_osm"]
        excluidos = derivados_todos & (b["relleno"] > umbral_relleno) if umbral_relleno is not None else vacio
        red = (quemado | (derivados_todos & ~excluidos)) & valido
    derivados = red & ~quemado
    grupo = np.zeros((H, W), np.uint8)
    grupo[red & mayor] = GRUPO_MAYOR
    grupo[red & otros] = GRUPO_OTRO
    grupo[red & b["menor_osm"]] = GRUPO_OSM_MENOR
    grupo[derivados] = GRUPO_DERIVADO
    menor = (red & ~mayor).ravel()
    dren = red.ravel()
    zc0 = b["zraw"].ravel().copy()
    zc0[mayor.ravel()] = b["zc_mayor"][mayor.ravel()]
    g_menor = np.where(grupo == GRUPO_MAYOR, 0, grupo)           # el perfil mayor ya está hecho
    zc1 = perfil_minimo(zc0, b["abajo"], b["orden"], g_menor)
    destino = destino_drenaje(b["abajo"], dren)
    zc = aplicar_piso(zc1, menor, b["destino_mayor"], b["zc_mayor"])
    rebaje = (zc0 - zc1)[derivados.ravel()]
    piso = (zc - zc1)[menor]
    z0d = b["z0"].astype(np.float64).ravel()
    hand_u = np.full(dren.size, np.nan)
    ok = (destino >= 0) & valido.ravel()
    hand_u[ok] = z0d[ok] - zc[destino[ok]]
    neg = int((hand_u < 0).sum())
    sin_destino = int((~ok & valido.ravel()).sum())
    negr = (hand_u < 0) & b["en_rejilla"].ravel()
    prof = -hand_u[negr]
    est_neg = {"celdas_utm_en_rejilla": int(negr.sum()), "celdas_utm_rejilla_total": int(b["en_rejilla"].sum()),
               "en_depresiones_rellenadas_mas_de_0_5m": int((negr & (b["relleno"].ravel() > UMBRAL_RELLENO_M)).sum()),
               "profundidad_bajo_la_referencia_m": ({"p50": round(float(np.median(prof)), 2), "p90": round(float(np.percentile(prof, 90)), 2),
                                                     "p99": round(float(np.percentile(prof, 99)), 2), "max": round(float(prof.max()), 2)}
                                                    if prof.size else None)}
    hand_bruto_u = hand_u.reshape(H, W).copy()                 # sin recortar: < 0 = celda bajo la cota de su cauce (depresión del DSM)
    hand_u = np.maximum(hand_u, 0).reshape(H, W)
    ref_u = np.full(dren.size, np.nan, np.float32)               # grupo del cauce de referencia
    ref_u[ok] = grupo.ravel()[destino[ok]]
    est = {
        "umbral_km2": umbral_km2, "umbral_relleno_m": umbral_relleno, "solo_mayor": solo_mayor,
        "celdas_red": int(red.sum()), "celdas_derivadas_usadas": int(derivados.sum()),
        "celdas_derivadas_excluidas_por_relleno": int(excluidos.sum()),
        "celdas_derivadas_sustituidas_por_cauce_osm": int(sustituidos.sum()),
        "celdas_red_osm_menor": int((red & b["menor_osm"]).sum()), "celdas_red_otros_rios_osm": int((red & otros).sum()),
        "rebaje_derivados_m": ({"p50": round(float(np.median(rebaje)), 3), "p90": round(float(np.percentile(rebaje, 90)), 3),
                                "p99": round(float(np.percentile(rebaje, 99)), 3), "max": round(float(rebaje.max()), 3),
                                "celdas_mas_de_2m": int((rebaje > 2).sum()), "celdas_mas_de_5m": int((rebaje > 5).sum())}
                               if rebaje.size else None),
        "piso_cauces_menores_m": ({"celdas_elevadas": int((piso > 1e-9).sum()), "max": round(float(piso.max()), 3),
                                   "p99": round(float(np.percentile(piso, 99)), 3)} if piso.size else None),
        "hand_negativo_llevado_a_0": neg, "hand_negativo_dentro_de_la_rejilla": est_neg, "celdas_sin_destino": sin_destino,
    }
    if informar:
        print(f"red ({'solo ríos mayores' if solo_mayor else f'umbral {umbral_km2} km², relleno {umbral_relleno} m'}): "
              f"{est['celdas_red']} celdas, {est['celdas_derivadas_usadas']} derivadas usadas, "
              f"{est['celdas_derivadas_excluidas_por_relleno']} excluidas por relleno; rebaje derivados {est['rebaje_derivados_m']}; "
              f"piso {est['piso_cauces_menores_m']}; HAND UTM {np.nanmin(hand_u):.1f}–{np.nanmax(hand_u):.1f} m; "
              f"negativos → 0: {neg}; sin destino: {sin_destino}", flush=True)
    return dict(red=red, derivados=derivados, excluidos=excluidos, zc=zc, destino=destino, hand_u=hand_u, hand_bruto_u=hand_bruto_u,
                ref_u=ref_u.reshape(H, W), est=est)


def a_rejilla(b, arr, remuestreo="bilinear"):
    return comun.reproyectar(np.asarray(arr, dtype=np.float32), b["tr_utm"], CRS_UTM, remuestreo=remuestreo)


def clasificar(hand, hand_m, dist, h_alta=HAND_ALTA, d_max=DIST_MAYOR_M, piso=True):
    """Clases 0–3. piso=True aplica la regla de piso de la franja de ribera: a ≤ DIST_PISO_M del cauce mayor, al menos media."""
    clase = np.full(hand.shape, np.nan, np.float32)
    v = np.isfinite(hand) & np.isfinite(dist)
    clase[v] = 0
    clase[v & (hand <= HAND_BAJA)] = 1
    clase[v & (hand <= HAND_MEDIA)] = 2
    if piso:
        clase[v & (dist <= DIST_PISO_M) & (clase < 2)] = 2
    clase[v & np.isfinite(hand_m) & (hand_m <= h_alta) & (dist <= d_max)] = 3
    return clase


# ============================================================== 4. sensibilidad
def sensibilidad(b, hand_m, dist):
    zonas = comun.comunas()
    mz = comun.mascara_zonas(zonas)
    urb = comun.mascara_urbana()
    area = comun.area_celda_m2()
    nombres = {z["indice"]: z["nombre"] for z in zonas}
    fb, cb = celda(*PUNTOS["Parque Bolívar (centro)"])

    # A. clase alta (no depende de la red menor): corte de HAND × distancia al cauce mayor
    tabla_a = []
    for h in (2.0, 3.0, 4.0):
        for dmax in (1000.0, 1250.0, 1500.0, 1750.0, 2000.0):
            c3 = np.isfinite(hand_m) & (hand_m <= h) & (dist <= dmax)
            tabla_a.append({"hand_max_m": h, "distancia_max_m": dmax,
                            "area_alta_rejilla_ha": ha(c3, area), "area_alta_cabecera_ha": ha(c3 & urb, area),
                            "celdas_alta_cabecera": int((c3 & urb).sum()),
                            "zonas_con_alta": [nombres[k] for k in sorted(set(mz[c3].tolist()) - {0})]})
    # B. red menor: umbral de área × exclusión por relleno (afecta 'hand', media, baja y HAND > 15 m)
    tabla_b = []
    for u in (1.0, 2.0, 5.0, 10.0, None):
        for rl in (UMBRAL_RELLENO_M, 2.0, None):
            if u is None and rl != UMBRAL_RELLENO_M:
                continue
            r = calcular_hand(b, u, rl)
            hr = a_rejilla(b, r["hand_u"])
            cl = clasificar(hr, hand_m, dist)
            vieja = urb & (hr <= HAND_ALTA) & (dist <= DIST_MAYOR_M)        # regla de la versión anterior
            tabla_b.append({
                "umbral_km2": u if u is not None else "sin red derivada (solo ríos OSM)",
                "exclusion_relleno_m": rl if rl is not None else "sin exclusión",
                "celdas_derivadas_usadas": r["est"]["celdas_derivadas_usadas"],
                "hand_mediana_cabecera_m": round(float(np.nanmedian(hr[urb])), 2),
                "hand_parque_bolivar_m": round(float(hr[fb, cb]), 2),
                "area_alta_cabecera_ha": ha(urb & (cl == 3), area),
                "area_media_cabecera_ha": ha(urb & (cl == 2), area),
                "area_baja_cabecera_ha": ha(urb & (cl == 1), area),
                "area_sin_cabecera_ha": ha(urb & (cl == 0), area),
                "area_media_rejilla_ha": ha(cl == 2, area),
                "regla_anterior_area_alta_cabecera_ha": ha(vieja, area),
                "rebaje_derivados_max_m": (r["est"]["rebaje_derivados_m"] or {}).get("max"),
            })
            print("  sensibilidad red menor:", tabla_b[-1], flush=True)
    return tabla_a, tabla_b


# ============================================================== 5. validación
def validar(clase, hand, hand_m, occ, ext, dist, ideam, acc_km2=None, cauces=(), red_r=None):
    """Comparación con datos independientes. Devuelve un dict para la serie."""
    from rasterio.features import rasterize
    area = comun.area_celda_m2()
    urb = comun.mascara_urbana()
    lejos = dist > CERCA_CAUCE_M
    v = np.isfinite(clase)
    out = {"nota": ("Validación parcial. El IDEAM y GSW son independientes del DEM, pero ninguno es un inventario completo de "
                    "inundaciones de Cartago. Se separan las celdas a más de "
                    f"{CERCA_CAUCE_M:g} m del cauce mayor quemado, donde el HAND no es ~0 por construcción.")}

    def por_clase(m):
        tot = float(area[m & v].sum())
        return {f"clase_{k}_pct": round(100.0 * float(area[m & v & (clase == k)].sum()) / tot, 1) if tot else None
                for k in (3, 2, 1, 0)}

    def tasa_por_clase(obs):
        """% del área de cada clase cubierta por la observación (todo / lejos del cauce)."""
        r = {}
        for k in (3, 2, 1, 0):
            mk = v & (clase == k)
            r[f"clase_{k}"] = {
                "pct_area_observada": round(100.0 * float(area[mk & obs].sum()) / max(float(area[mk].sum()), 1), 2),
                "pct_area_observada_lejos_del_cauce": round(100.0 * float(area[mk & obs & lejos].sum()) / max(float(area[mk & lejos].sum()), 1), 2)}
        return r

    def ras(feats, valor=lambda f: 1):
        if not feats:
            return np.zeros((comun.ALTO, comun.ANCHO), np.uint8)
        return rasterize([(f["geometry"], valor(f)) for f in feats], out_shape=(comun.ALTO, comun.ANCHO),
                         transform=comun.transformacion(), fill=0, all_touched=False, dtype="uint8")

    # ---- IDEAM: amenaza por creciente súbita TR 50 años (Cartago, río La Vieja)
    if ideam is not None and 0 in ideam:
        feats = ideam[0]["features"]
        orden = {"BAJA": 1, "MEDIA": 2, "ALTA": 3}
        feats = sorted([f for f in feats if f["properties"].get("ame") in orden], key=lambda f: orden[f["properties"]["ame"]])
        am = ras(feats, lambda f: orden[f["properties"]["ame"]])
        filas = []
        for nom, k in (("ALTA", 3), ("MEDIA", 2), ("BAJA", 1)):
            m = am == k
            filas.append({"amenaza_ideam": nom, "celdas": int(m.sum()), "area_ha": ha(m, area),
                          "area_ha_segun_atributo": round(sum(f["properties"]["area_tot_ha"] for f in feats if f["properties"]["ame"] == nom), 2),
                          "en_nuestras_clases": por_clase(m),
                          "hand_rio_mayor_mediana_m": round(float(np.nanmedian(hand_m[m])), 2) if m.any() else None,
                          "hand_mediana_m": round(float(np.nanmedian(hand[m])), 2) if m.any() else None,
                          "pct_lejos_del_cauce": round(100.0 * float((m & lejos).sum()) / max(int(m.sum()), 1), 1)})
        cualquiera = am > 0
        c3u = urb & (clase == 3)
        zonas = comun.comunas()
        mz = comun.mascara_zonas(zonas)
        por_zona = []
        for z in zonas:
            m = mz == z["indice"]
            fila = {"nombre": z["nombre"]}
            for nom, k in (("alta", 3), ("media", 2), ("baja", 1)):
                fila[f"ideam_{nom}_ha"] = ha(m & (am == k), area)
            for k in (3, 2, 1, 0):
                fila[f"ideam_alta_en_nuestra_clase_{k}_ha"] = ha(m & (am == 3) & (clase == k), area)
            fila["ideam_alta_en_clases_baja_o_0_pct"] = (round(100.0 * float(area[m & (am == 3) & (clase <= 1)].sum())
                                                               / float(area[m & (am == 3)].sum()), 1) if (m & (am == 3)).any() else None)
            fila["nuestra_clase_3_ha"] = ha(m & (clase == 3), area)
            fila["nuestra_clase_2_ha"] = ha(m & (clase == 2), area)
            fila["nuestra_clase_2_fuera_de_mancha_ideam_ha"] = ha(m & (clase == 2) & (am == 0), area)
            por_zona.append(fila)
        cobertura_corte = {}
        for nom, k in (("ALTA", 3), ("MEDIA", 2)):
            m = am == k
            cobertura_corte[nom] = {f"hand_rio_mayor_le_{h:g}m": round(100.0 * float(area[m & (hand_m <= h) & (dist <= DIST_MAYOR_M)].sum())
                                                                     / max(float(area[m].sum()), 1), 1) for h in (2, 3, 4, 5, 6, 8, 10)}
        # por polígono ALTA: corredor del río La Vieja frente a cauces menores (todos llevan corriente = 'Río La Vieja')
        from pyproj import Transformer
        from shapely.geometry import shape
        from shapely.ops import transform as stransform
        a_utm = Transformer.from_crs("EPSG:4326", CRS_UTM, always_xy=True).transform
        vieja_u = stransform(a_utm, comun.lineas_rio("rio_la_vieja"))
        from shapely.ops import unary_union
        menores_osm = [c["geom"] for c in cauces if c["tipo"] in ("arroyo", "canal")]
        osm_u = stransform(a_utm, unary_union(menores_osm)) if menores_osm else None
        nom_z = {z["indice"]: z["nombre"] for z in zonas}
        por_pol = []
        for f in feats:
            if f["properties"]["ame"] != "ALTA":
                continue
            m = ras([f]) > 0
            if not m.any():
                continue
            g = shape(f["geometry"])
            d_v = stransform(a_utm, g).distance(vieja_u)
            zs = mz[m]
            zona = nom_z.get(int(np.bincount(zs).argmax()), "fuera de las zonas") if zs.size else None
            tot = float(area[m & v].sum())
            por_pol.append({
                "objectid_ideam": f["properties"].get("objectid"), "area_ha": ha(m, area),
                "centroide_lat_lon": [round(g.centroid.y, 3), round(g.centroid.x, 3)],
                "distancia_al_eje_la_vieja_m": round(d_v), "zona": zona,
                "distancia_al_arroyo_o_canal_osm_m": round(stransform(a_utm, g).distance(osm_u)) if osm_u is not None else None,
                "area_drenada_max_dsm_km2": round(float(np.nanmax(acc_km2[m])), 2) if acc_km2 is not None else None,
                "celdas_con_red_de_drenaje": int(np.nansum(red_r[m] > 0)) if red_r is not None else None,
                "celdas": int(m.sum()),
                "tipo": "corredor del río La Vieja" if d_v <= CORREDOR_VIEJA_M else "cauce menor",
                "en_nuestras_clases": por_clase(m),
                "en_clases_baja_o_0_ha": ha(m & v & (clase <= 1), area),
                "hand_mediana_m": round(float(np.nanmedian(hand[m])), 2), "hand_rio_mayor_mediana_m": round(float(np.nanmedian(hand_m[m])), 2),
                "pct_en_cabecera": round(100.0 * float(area[m & urb].sum()) / tot, 1) if tot else None})
        grupos = {}
        for tipo in ("corredor del río La Vieja", "cauce menor"):
            ms = [ras([f]) > 0 for f in feats if f["properties"]["ame"] == "ALTA"
                  and any(p["objectid_ideam"] == f["properties"].get("objectid") and p["tipo"] == tipo for p in por_pol)]
            if ms:
                mm = np.any(ms, axis=0)
                fuera = mm & v & (clase <= 1)
                grupos[tipo] = {"area_ha": ha(mm, area), "en_nuestras_clases": por_clase(mm),
                                "en_clases_baja_o_0_ha": ha(fuera, area),
                                "en_clases_baja_o_0_distancia_mediana_al_cauce_mayor_m": round(float(np.nanmedian(dist[fuera]))) if fuera.any() else None,
                                "en_clases_baja_o_0_hand_mediana_m": round(float(np.nanmedian(hand[fuera])), 2) if fuera.any() else None,
                                "cabecera": por_clase(mm & urb) if (mm & urb).any() else None}
        a3u = urb & (am == 3)
        out["ideam_creciente_subita_tr50"] = {
            "fuente": IDEAM_CAPAS[0][1] + " — " + FUENTE_IDEAM,
            "municipios": sorted({f["properties"].get("nom_mpio") for f in feats}),
            "corrientes": sorted({f["properties"].get("corriente") for f in feats}),
            "por_clase_ideam": filas,
            "recall_alta_ideam_en_clase_3_pct": filas[0]["en_nuestras_clases"]["clase_3_pct"],
            "recall_cualquier_amenaza_ideam_en_clases_2_o_3_pct": round(
                100.0 * float(area[cualquiera & ((clase == 3) | (clase == 2))].sum()) / max(float(area[cualquiera].sum()), 1), 1),
            "pct_area_ideam_con_hand_rio_mayor_le_corte_y_1_5km": cobertura_corte,
            "cabecera_alta_ideam": {"area_ha": ha(a3u, area), "en_nuestras_clases": por_clase(a3u) if a3u.any() else None,
                                    "en_clases_baja_o_0_ha": ha(a3u & v & (clase <= 1), area)},
            "por_poligono_alta": por_pol,
            "corredor_la_vieja_frente_a_cauces_menores": grupos,
            "por_zona": por_zona,
            "clase_3_cabecera_dentro_de_mancha_ideam_pct": round(100.0 * float(area[c3u & cualquiera].sum()) / max(float(area[c3u].sum()), 1), 1) if c3u.any() else None,
            "advertencia": ("El IDEAM solo zonificó el corredor del río La Vieja junto a la cabecera; fuera de sus polígonos no se sabe si "
                            "hay amenaza o si no se estudió, así que solo se calcula la cobertura (recall), no la precisión. "
                            "Creciente súbita TR 50 años: no incluye el desbordamiento lento del Cauca."),
        }
    # ---- IDEAM: áreas afectadas por inundación (La Niña)
    if ideam is not None:
        eventos, union = [], np.zeros((comun.ALTO, comun.ANCHO), bool)
        for capa, (clave, nombre, periodo) in IDEAM_CAPAS.items():
            if capa == 0 or capa not in ideam:
                continue
            m = ras(ideam[capa]["features"]) > 0
            union |= m
            eventos.append({"capa": capa, "nombre": nombre, "periodo": periodo, "poligonos": len(ideam[capa]["features"]),
                            "generalizacion_grados": ideam[capa].get("consulta", {}).get("generalizacion_grados"),
                            "area_en_rejilla_ha": ha(m, area), "area_lejos_del_cauce_ha": ha(m & lejos, area),
                            "en_nuestras_clases": por_clase(m) if m.any() else None,
                            "en_nuestras_clases_lejos_del_cauce": por_clase(m & lejos) if (m & lejos).any() else None})
        out["ideam_areas_afectadas_nina"] = {
            "fuente": FUENTE_IDEAM,
            "eventos": eventos,
            "union_area_ha": ha(union, area), "union_area_lejos_del_cauce_ha": ha(union & lejos, area),
            "union_en_nuestras_clases": por_clase(union) if union.any() else None,
            "union_en_nuestras_clases_lejos_del_cauce": por_clase(union & lejos) if (union & lejos).any() else None,
            "union_hand_rio_mayor_mediana_m": round(float(np.nanmedian(hand_m[union])), 2) if union.any() else None,
            "tasa_por_clase": tasa_por_clase(union),
            "advertencia": ("Manchas de áreas afectadas cartografiadas por el IDEAM (escala no declarada en el servicio ni en datos.gov.co): "
                            "bordes gruesos y eventos posiblemente incompletos; el IDEAM advierte en datos.gov.co que no las ha validado."),
        }
        out["_union_nina"] = union
    # ---- GSW: extensión máxima de agua (alguna vez agua 1984–2024)
    if ext is not None:
        alguna = ext == 1
        out["gsw_extension_maxima"] = {
            "descripcion": "Celdas en que Landsat detectó agua alguna vez (JRC GSW v1.5 'extent', 1984–2024).",
            "celdas": int(alguna.sum()), "celdas_lejos_del_cauce": int((alguna & lejos).sum()),
            "en_nuestras_clases": por_clase(alguna), "en_nuestras_clases_lejos_del_cauce": por_clase(alguna & lejos),
            "tasa_por_clase": tasa_por_clase(alguna),
        }
    # ---- coherencia interna (no es validación)
    if occ is not None:
        w = occ >= 50
        out["coherencia_gsw_ocurrencia_50"] = {
            "descripcion": ("Coherencia interna, NO validación: casi todas las celdas con agua frecuente están sobre el cauce "
                            "quemado, donde el HAND vale ~0 por construcción."),
            "celdas": int(w.sum()),
            "a_30m_o_menos_del_cauce_mayor": int((w & (dist <= 30)).sum()),
            "a_60m_o_menos_del_cauce_mayor": int((w & (dist <= 60)).sum()),
            "pct_hand_rio_mayor_le_3": round(100.0 * float(np.mean(hand_m[w] <= HAND_ALTA)), 1),
            "lejos_del_cauce": int((w & lejos).sum()),
            "lejos_del_cauce_hand_rio_mayor_le_3": int((w & lejos & (hand_m <= HAND_ALTA)).sum()),
            "ocurrencia_10_50_lejos_del_cauce": int(((occ >= 10) & (occ < 50) & lejos).sum()),
            "ocurrencia_10_50_lejos_del_cauce_hand_rio_mayor_le_3": int(((occ >= 10) & (occ < 50) & lejos & (hand_m <= HAND_ALTA)).sum()),
        }
    return out


def ideam_rejilla(ideam):
    """Amenaza por creciente súbita TR 50 del IDEAM en la rejilla común (0 fuera, 1 baja, 2 media, 3 alta)."""
    from rasterio.features import rasterize
    if ideam is None or 0 not in ideam:
        return None
    orden = {"BAJA": 1, "MEDIA": 2, "ALTA": 3}
    feats = sorted([f for f in ideam[0]["features"] if f["properties"].get("ame") in orden], key=lambda f: orden[f["properties"]["ame"]])
    return rasterize([(f["geometry"], orden[f["properties"]["ame"]]) for f in feats], out_shape=(comun.ALTO, comun.ANCHO),
                     transform=comun.transformacion(), fill=0, all_touched=False, dtype="uint8")


def resumen_variante(clase, am, area, urb):
    """Área por clase y reparto de la amenaza ALTA del IDEAM entre las clases (rejilla y cabecera)."""
    out = {}
    for nom, m in (("rejilla", np.ones_like(urb)), ("cabecera", urb)):
        v = m & np.isfinite(clase)
        fila = {f"area_clase_{k}_ha": ha(v & (clase == k), area) for k in (3, 2, 1, 0)}
        if am is not None:
            a3 = v & (am == 3)
            t = float(area[a3].sum())
            fila["ideam_alta_ha"] = ha(a3, area)
            fila["ideam_alta_en_clase_pct"] = {str(k): round(100.0 * float(area[a3 & (clase == k)].sum()) / t, 1) if t else None
                                               for k in (3, 2, 1, 0)}
            fila["ideam_alta_en_clases_baja_o_0_pct"] = round(100.0 * float(area[a3 & (clase <= 1)].sum()) / t, 1) if t else None
            fila["ideam_alta_en_clases_baja_o_0_ha"] = ha(a3 & (clase <= 1), area)
        out[nom] = fila
    return out


def comparar_versiones(dem_geo, tr_geo, crs_geo, chm, cauces, am, publicada):
    """Efecto de cada corrección (dosel, red OSM, regla de piso) frente a la versión anterior (DSM tal cual, red solo del DEM)."""
    area = comun.area_celda_m2()
    urb = comun.mascara_urbana()
    out, extra = {}, {}
    variantes = [("version_anterior_dsm_sin_correcciones", None, None), ("solo_correccion_dosel", chm, None),
                 ("solo_red_osm", None, cauces)]
    for nom, c1, c2 in variantes:
        if (c1 is None and nom == "solo_correccion_dosel") or (not c2 and nom == "solo_red_osm"):
            continue
        print(f"variante {nom}…", flush=True)
        bv = hidrologia(dem_geo, tr_geo, crs_geo, chm=c1, cauces=c2)
        rv, rmv = calcular_hand(bv), calcular_hand(bv, solo_mayor=True)
        hv, hmv, dv = a_rejilla(bv, rv["hand_u"]), a_rejilla(bv, rmv["hand_u"]), a_rejilla(bv, bv["dist_u"])
        out[nom] = resumen_variante(clasificar(hv, hmv, dv, piso=False), am, area, urb)
        if nom.startswith("version_anterior"):
            extra["hand_rio_mayor_anterior"] = hmv
            extra["hand_bruto_anterior"] = a_rejilla(bv, rv["hand_bruto_u"])
            extra["clase_anterior"] = clasificar(hv, hmv, dv, piso=False)
    clase, clase_sin_piso = publicada
    out["dosel_y_red_osm_sin_regla_de_piso"] = resumen_variante(clase_sin_piso, am, area, urb)
    out["publicada_dosel_red_osm_y_regla_de_piso"] = resumen_variante(clase, am, area, urb)
    return out, extra


def desplazamiento_gsw(occ, altitud):
    """¿Está el agua frecuente de GSW desplazada respecto al DEM? Altura relativa (altitud − media 9×9) en celdas con
    ocurrencia ≥ 50 % para desplazamientos de −1 a +1 celda. Un mínimo fuera de (0, 0) sugiere desfase."""
    from scipy.ndimage import uniform_filter
    rel = altitud - uniform_filter(np.nan_to_num(altitud, nan=float(np.nanmean(altitud))), 9)
    w = np.nan_to_num(occ) >= 50
    res = {}
    for df in (-1, 0, 1):
        for dc in (-1, 0, 1):
            ww = np.roll(np.roll(w, df, axis=0), dc, axis=1)
            res[f"{df},{dc}"] = round(float(np.nanmean(rel[ww])), 2)
    mejor = min(res, key=res.get)
    df, dc = (int(x) for x in mejor.split(","))
    hacia = " y ".join(t for t in ({-1: "una celda al norte", 1: "una celda al sur"}.get(df), {-1: "una celda al oeste", 1: "una celda al este"}.get(dc)) if t)
    desfase = {-1: "sur", 1: "norte"}.get(df, "") + {-1: "este", 1: "oeste"}.get(dc, "")
    return {"altura_relativa_media_m_por_desplazamiento_fila_columna": res, "desplazamiento_con_menor_altura": mejor,
            "convencion": "fila −1 = mover la máscara de agua una celda al norte; columna +1 = una celda al este",
            "mover_hacia": hacia, "desfase_gsw": desfase or "ninguno"}


# ============================================================== 6. principal
def main():
    import rasterio

    t_ini = time.time()
    descargar_dem()
    try:
        gsw = descargar_gsw()
    except Exception as e:  # noqa: BLE001
        print("AVISO: JRC GSW no disponible, no se construye 'agua_ocurrencia':", e)
        gsw = None
    try:
        ideam = descargar_ideam()
    except Exception as e:  # noqa: BLE001
        print("AVISO: IDEAM no disponible, se omite esa validación:", e)
        ideam = None
    try:
        chm = descargar_chm()
        fch = fechas_chm()
        print("fechas de las imágenes del CHM en la rejilla:", fch)
    except Exception as e:  # noqa: BLE001
        print("AVISO: CHM de Meta/WRI no disponible, el HAND se calcula sobre el DSM sin corregir:", e)
        chm, fch = None, None
    try:
        osm_cauces = descargar_cauces_osm()
    except Exception as e:  # noqa: BLE001
        print("AVISO: cauces OSM no disponibles:", e)
        osm_cauces = None
    cauces = cauces_osm(osm_cauces)

    with rasterio.open(RUTA_DEM) as s:
        dem_geo = s.read(1).astype(np.float32)
        tr_geo, crs_geo = s.transform, s.crs
    print(f"DEM ventana {dem_geo.shape}, {np.nanmin(dem_geo):.1f}–{np.nanmax(dem_geo):.1f} m")
    assert np.isfinite(dem_geo).all() and dem_geo.min() > -50, "DEM con huecos o valores anómalos"

    # ---- altitud en la rejilla común
    altitud = comun.reproyectar(dem_geo, tr_geo, crs_geo, remuestreo="bilinear")
    t3 = [[round(float(np.nanmedian(altitud[i * comun.ALTO // 3:(i + 1) * comun.ALTO // 3, j * comun.ANCHO // 3:(j + 1) * comun.ANCHO // 3])), 1)
           for j in range(3)] for i in range(3)]
    print("altitud mediana por tercios (filas N→S, columnas O→E):", t3)
    assert all(t3[i][2] > t3[i][0] for i in range(3)), "se esperaba el oriente más alto que el occidente"

    b = hidrologia(dem_geo, tr_geo, crs_geo, chm=chm, cauces=cauces)
    H, W, tr_utm = b["H"], b["W"], b["tr_utm"]
    r = calcular_hand(b, UMBRAL_KM2, UMBRAL_RELLENO_M, informar=True)
    rm = calcular_hand(b, solo_mayor=True, informar=True)
    hm_u, h_u = rm["hand_u"], r["hand_u"]
    ambos = np.isfinite(hm_u) & np.isfinite(h_u)
    viol = int((h_u[ambos] > hm_u[ambos] + 1e-6).sum())
    print(f"comprobación HAND (toda la red) ≤ HAND (ríos mayores): {viol} celdas lo incumplen de {int(ambos.sum())}")
    assert viol == 0
    if r["est"]["rebaje_derivados_m"]:
        assert r["est"]["rebaje_derivados_m"]["max"] <= UMBRAL_RELLENO_M + 1e-6, "rebaje mayor que el acotado por la exclusión"

    # ---- a la rejilla común
    hand = a_rejilla(b, h_u)
    hand_m = a_rejilla(b, hm_u)
    hand_bruto = a_rejilla(b, r["hand_bruto_u"])
    dist = a_rejilla(b, b["dist_u"])
    ref = a_rejilla(b, r["ref_u"], "nearest")
    chm_r = a_rejilla(b, b["ch_u"]) if b["ch_u"] is not None else None
    # río mayor al que llega cada celda (1 La Vieja, 2 Cauca)
    rio_u = np.full(H * W, np.nan, np.float32)
    okm = rm["destino"] >= 0
    rio_u[okm] = b["rio_id"].ravel()[rm["destino"][okm]]
    rio = a_rejilla(b, rio_u.reshape(H, W), "nearest")
    hand_pub = np.where(np.isfinite(hand), np.clip(hand, 0, 60), np.nan)
    hand_m_pub = np.where(np.isfinite(hand_m), np.clip(hand_m, 0, 60), np.nan)
    clase = clasificar(hand, hand_m, dist)
    clase_sin_piso = clasificar(hand, hand_m, dist, piso=False)
    area = comun.area_celda_m2()
    urb = comun.mascara_urbana()
    promovidas = np.isfinite(clase) & (clase != clase_sin_piso)
    piso_est = {"rejilla_ha": ha(promovidas, area), "cabecera_ha": ha(promovidas & urb, area),
                "desde_baja_ha": ha(promovidas & (clase_sin_piso == 1), area), "desde_hand_mayor_15_ha": ha(promovidas & (clase_sin_piso == 0), area)}
    print("regla de piso (≤ 100 m del cauce mayor → al menos media):", piso_est)

    am = ideam_rejilla(ideam)
    efecto, extra = comparar_versiones(dem_geo, tr_geo, crs_geo, chm, cauces, am, (clase, clase_sin_piso))
    print("efecto de las correcciones:", json.dumps(efecto, ensure_ascii=False)[:3000], flush=True)

    # sesgo residual del dosel junto a los ríos mayores: hand_rio_mayor a 30–90 m del cauce según el dosel
    ribera = None
    if chm_r is not None:
        franja = (dist > 30) & (dist <= 90) & np.isfinite(hand_m)
        hm_ant = extra.get("hand_rio_mayor_anterior")
        ribera = []
        for a_, b_ in ((0, 2), (2, 6), (6, 10), (10, 60)):
            mm = franja & (chm_r >= a_) & (chm_r < b_)
            if mm.sum() >= 20:
                ribera.append({"chm_desde_m": a_, "chm_hasta_m": b_, "celdas": int(mm.sum()),
                               "hand_rio_mayor_mediana_m_antes": round(float(np.nanmedian(hm_ant[mm])), 2) if hm_ant is not None else None,
                               "hand_rio_mayor_mediana_m_despues": round(float(np.nanmedian(hand_m[mm])), 2)})
        print("franja 30–90 m del cauce mayor por dosel:", ribera)

    print("sensibilidad…", flush=True)
    tabla_a, tabla_b = sensibilidad(b, hand_m, dist)

    # ---- agua histórica
    occ = ext = None
    if gsw is not None:
        with rasterio.open(gsw["occurrence"]) as s:
            g = s.read(1)
            assert s.transform.almost_equals(comun.transformacion()), (s.transform, comun.transformacion())
            etiquetas = s.tags()
        assert set(np.unique(g).tolist()) <= set(range(101)) | {255}, np.unique(g)
        occ = np.where(g == 255, np.nan, g.astype(np.float32))
        periodo_gsw = etiquetas.get("periodo", "")
        if gsw["extent"]:
            with rasterio.open(gsw["extent"]) as s:
                e = s.read(1)
                assert s.transform.almost_equals(comun.transformacion())
            assert set(np.unique(e).tolist()) <= {0, 1, 255}, np.unique(e)
            ext = np.where(e == 255, 255, e)
            # coherencia entre capas: donde occurrence > 0 la extensión máxima debe ser 1
            assert np.all(ext[np.nan_to_num(occ) > 0] == 1)

    acc_r = comun.reproyectar((b["acc"] * PASO * PASO / 1e6).reshape(H, W).astype(np.float32), tr_utm, CRS_UTM, remuestreo="max")
    red_r = comun.reproyectar(r["red"].astype(np.float32), tr_utm, CRS_UTM, remuestreo="max")
    val = validar(clase, hand, hand_m, occ, ext, dist, ideam, acc_r, cauces, red_r)
    val.pop("_union_nina", None)
    val["efecto_correcciones"] = {
        "descripcion": ("Reparto de la amenaza ALTA por creciente súbita del IDEAM entre nuestras clases antes y después de cada corrección. "
                        "'version_anterior' = DSM sin corregir y red menor solo del DEM (lo publicado antes); la versión publicada añade la "
                        "corrección del dosel, la red de arroyos y canales de drenaje de OSM y la regla de piso de la franja de ribera."),
        "variantes": efecto, "regla_de_piso": piso_est, "franja_30_90m_cauce_mayor_por_dosel": ribera}
    vi = val.get("ideam_creciente_subita_tr50")
    vn = val.get("ideam_areas_afectadas_nina")

    # ---- textos de validación (todas las cifras salen de los datos)
    lim_nina, aviso_bajas, resumen_val = [], None, None
    if vi:
        cab = vi["cabecera_alta_ideam"]
        a_rej = vi["por_clase_ideam"][0]
        c_rej = a_rej["en_nuestras_clases"]
        cc = cab["en_nuestras_clases"]
        ant = efecto["version_anterior_dsm_sin_correcciones"]
        pub = efecto["publicada_dosel_red_osm_y_regla_de_piso"]
        grupos = vi["corredor_la_vieja_frente_a_cauces_menores"]
        menores = [p for p in vi["por_poligono_alta"] if p["tipo"] == "cauce menor"]
        cor = grupos.get("corredor del río La Vieja")
        men = grupos.get("cauce menor")
        aviso_bajas = (
            "Las clases 'baja' y 'HAND > 15 m' NO descartan amenaza de inundación: la referencia oficial es la zonificación de amenaza del "
            "IDEAM, de la CVC y del POT de Cartago. Frente a la amenaza ALTA por creciente súbita del IDEAM (TR 50 años), en la cabecera el "
            f"{es(pub['cabecera']['ideam_alta_en_clases_baja_o_0_pct'])} % de su área ({es(cab['en_clases_baja_o_0_ha'])} de {es(cab['area_ha'])} ha) "
            f"queda en esas clases, y en toda la rejilla el {es(pub['rejilla']['ideam_alta_en_clases_baja_o_0_pct'])} % "
            f"({es(pub['rejilla']['ideam_alta_en_clases_baja_o_0_ha'])} ha), sobre todo en cauces menores al sur de la cabecera y en Zaragoza.")
        resumen_val = (
            f"Amenaza ALTA del IDEAM en la rejilla ({es(a_rej['area_ha'])} ha): {es(c_rej['clase_3_pct'])} % en nuestra clase alta, "
            f"{es(c_rej['clase_2_pct'])} % en media, {es(c_rej['clase_1_pct'])} % en baja y {es(c_rej['clase_0_pct'])} % en HAND > 15 m. "
            + (f"En el corredor del río La Vieja ({es(cor['area_ha'])} ha) queda en baja o HAND > 15 m el "
               f"{es(round(cor['en_nuestras_clases']['clase_1_pct'] + cor['en_nuestras_clases']['clase_0_pct'], 1))} % "
               f"({es(cor['en_clases_baja_o_0_ha'])} ha; a {es(cor['en_clases_baja_o_0_distancia_mediana_al_cauce_mayor_m'])} m del cauce mayor y HAND "
               f"{es(cor['en_clases_baja_o_0_hand_mediana_m'])} m en mediana). " if cor and cor['en_clases_baja_o_0_ha'] else "")
            + (f"En los cauces menores (polígonos {', '.join(str(p['objectid_ideam']) for p in menores)} del IDEAM: sur de la cabecera y Zaragoza, "
               f"a {es(min(p['distancia_al_eje_la_vieja_m'] for p in menores) / 1000, '.1f')}–{es(max(p['distancia_al_eje_la_vieja_m'] for p in menores) / 1000, '.1f')} km "
               f"de La Vieja; {es(men['area_ha'])} ha) queda en baja o HAND > 15 m el "
               f"{es(round(men['en_nuestras_clases']['clase_1_pct'] + men['en_nuestras_clases']['clase_0_pct'], 1))} % ({es(men['en_clases_baja_o_0_ha'])} ha): "
               f"esos polígonos están a {es(min(p['distancia_al_arroyo_o_canal_osm_m'] for p in menores))}–"
               f"{es(max(p['distancia_al_arroyo_o_canal_osm_m'] for p in menores))} m del arroyo o canal OSM más cercano y el área drenada máxima del DSM "
               "dentro de ellos es de " + ", ".join(f"{es(p['area_drenada_max_dsm_km2'])} km² (polígono {p['objectid_ideam']})" for p in menores)
               + f"; la red de drenaje usada toca " + ", ".join(f"{p['celdas_con_red_de_drenaje']} de {p['celdas']} celdas" for p in menores)
               + ", así que casi todo su HAND se mide respecto a cauces lejanos. "
               if men and menores and all(p.get("distancia_al_arroyo_o_canal_osm_m") is not None for p in menores) else "")
            + f"Antes de estas correcciones (DSM sin corregir, sin red OSM ni regla de piso) el reparto en la cabecera era "
              f"{es(ant['cabecera']['ideam_alta_en_clase_pct']['3'])} / {es(ant['cabecera']['ideam_alta_en_clase_pct']['2'])} / "
              f"{es(ant['cabecera']['ideam_alta_en_clase_pct']['1'])} / {es(ant['cabecera']['ideam_alta_en_clase_pct']['0'])} % (alta / media / baja / "
              f"HAND > 15 m); ahora es {es(pub['cabecera']['ideam_alta_en_clase_pct']['3'])} / {es(pub['cabecera']['ideam_alta_en_clase_pct']['2'])} / "
              f"{es(pub['cabecera']['ideam_alta_en_clase_pct']['1'])} / {es(pub['cabecera']['ideam_alta_en_clase_pct']['0'])} %.")
    if vn:
        t = vn["tasa_por_clase"]
        lim_nina.append(
            "Frente a las áreas afectadas por inundación de La Niña del IDEAM (1988–2022, escala no declarada; unión de "
            f"{es(vn['union_area_ha'])} ha en la rejilla): quedó inundado el {es(t['clase_3']['pct_area_observada'])} % del área de clase alta, el "
            f"{es(t['clase_2']['pct_area_observada'])} % de la media, el {es(t['clase_1']['pct_area_observada'])} % de la baja y el "
            f"{es(t['clase_0']['pct_area_observada'])} % de la clase HAND > 15 m. Las clases ordenan el riesgo observado, pero el "
            f"{es(vn['union_en_nuestras_clases']['clase_2_pct'])} % del área inundada observada está en clase media y el "
            f"{es(round(vn['union_en_nuestras_clases']['clase_1_pct'] + vn['union_en_nuestras_clases']['clase_0_pct'], 1))} % en baja o HAND > 15 m.")

    # ================================================= metadatos y escritura
    cal = b["calibracion_dosel"]
    proc_comun = [
        "Lectura por ventanas de las teselas COG N04W076 y N04W077 del Copernicus DEM GLO-30 (dominio −76,08/−75,76 E, 4,60/4,88 N).",
    ]
    if cal:
        par = "; ".join(f"{es(x)} m → {es(y)} m" for x, y in zip(cal["curva_chm_m"][1:], cal["curva_correccion_m"][1:]))
        txt_cal = (f"Corrección del dosel: altura del dosel de Meta/WRI CHM v1 (1 m; imágenes de {int(fch['min'])}–{int(fch['max'])} en la rejilla) "
                   f"promediada a 30 m y convertida en exceso del DSM con una curva calibrada en Cartago: en terreno llano fuera de la ciudad, mediana de "
                   f"(altura de la celda − media de las celdas sin dosel en {CAL_VENTANA}×{CAL_VENTANA} celdas) por intervalos de CHM ({par}; por encima, "
                   f"{es(cal['razon_extrapolacion'])} × CHM; control en celdas sin dosel: {es(cal['control_celdas_sin_dosel_exceso_mediana_m'])} m). "
                   "El HAND usa este DEM corregido; la capa 'altitud' sigue siendo el DSM.") if fch else None
    else:
        txt_cal = None
    lim_dsm = ("El Copernicus DEM es un modelo de SUPERFICIE: incluye edificios y copas de árboles. "
               + ("Para el HAND se resta una estimación del exceso del dosel (Meta/WRI CHM v1, curva calibrada en Cartago); la corrección es "
                  "parcial: "
                  + (f"a 30–90 m de La Vieja o del Cauca, el HAND respecto al río pasa de {es(ribera[-1]['hand_rio_mayor_mediana_m_antes'])} a "
                     f"{es(ribera[-1]['hand_rio_mayor_mediana_m_despues'])} m bajo dosel alto (CHM ≥ {es(ribera[-1]['chm_desde_m'])} m), frente a "
                     f"{es(ribera[0]['hand_rio_mayor_mediana_m_despues'])} m sin dosel, " if ribera else "")
                  + "y los edificios no se corrigen (en la ciudad las alturas siguen por encima del suelo y el HAND tiende a quedar alto). "
                  if cal else "En la ciudad las alturas quedan por encima del suelo, lo que tiende a SUBESTIMAR la susceptibilidad (HAND más alto). ")
               + "La lámina de agua de los ríos se toma del mínimo local del DSM (±60 m).")
    interp_alt = (f"Sin umbrales: es la base topográfica del HAND. Valores bajos al occidente y al norte (llanura del Cauca y confluencia "
                  f"con La Vieja); altos al oriente (piedemonte). Medianas por tercios de la rejilla, de norte a sur y de oeste a este: "
                  + "; ".join("[" + ", ".join(es(x) for x in fila) + "]" for fila in t3) + " m.")
    meta_alt = {
        "titulo": "Altitud de la superficie (DSM)",
        "descripcion": "Altura sobre el nivel del mar de la superficie visible desde el satélite (incluye edificios y árboles), a unos 30 m de detalle.",
        "unidad": "m s.n.m.",
        "fuente": FUENTE_DEM,
        "periodo": "Adquisiciones TanDEM-X 2011–2015 (Copernicus DEM GLO-30)",
        "resolucion_original_m": 30,
        "procesamiento": proc_comun + [
            "Remuestreo bilineal a la rejilla común (0,00025°) con comun.reproyectar.",
            "Alturas sobre el geoide EGM2008 (≈ metros sobre el nivel del mar), sin ajuste al datum vertical colombiano.",
        ],
        "limitaciones": [
            "El Copernicus DEM es un modelo de SUPERFICIE: incluye edificios y copas de árboles; esta capa NO está corregida (el HAND sí usa una "
            "corrección del dosel; ver su ficha).",
            "Exactitud absoluta del producto global: del orden de pocos metros; en pendientes fuertes y bajo vegetación densa el error crece.",
            "Las fechas de adquisición (2011–2015) no reflejan construcciones posteriores.",
        ],
        "rango_visual": [895, 1100],
        "paleta": ["#2c6e49", "#86a873", "#e9d8a6", "#bb9457", "#7f5539"],
        "interpretacion": interp_alt,
        "avisos_legales": [ATRIB_DEM, EXENCION_DEM],
    }
    est_r = r["est"]
    neg_r = est_r["hand_negativo_dentro_de_la_rejilla"]
    n_ar = sum(1 for c in cauces if c["tipo"] == "arroyo")
    canales_ok = sorted(k for k, v in b["canales_evaluados"].items() if v["drenaje"])
    canales_no = sorted(k for k, v in b["canales_evaluados"].items() if not v["drenaje"])
    proc_hand = proc_comun + [
        f"DEM a UTM 18N (EPSG:32618) a {PASO:.0f} m con remuestreo bilineal; dominio {W}×{H} celdas ({es(W * PASO / 1000, '.1f')} × {es(H * PASO / 1000, '.1f')} km).",
    ] + ([txt_cal] if txt_cal else []) + [
        f"Quema de cauces: ejes OSM de los ríos La Vieja y Cauca (rasterizados tocando celdas), polígonos de agua fluvial OSM de La Vieja, Cauca y Consota "
        f"y ejes de los demás ríos OSM bajados {PROFUNDIDAD_QUEMA:.0f} m; arroyos OSM ({n_ar} vías, incluidas las alcantarillas) y canales OSM que pasan la prueba "
        f"de drenaje bajados {PROFUNDIDAD_QUEMA_MENOR:.0f} m. Solo dirige el flujo; las alturas del HAND no usan el DEM quemado.",
        "Prueba de drenaje de cada canal OSM: cada 30 m, el mínimo 3×3 del eje frente a la mediana de los flancos a 60–150 m a cada lado; se acepta si en "
        f"≥ 60 % de los puntos el eje queda a ≤ 0,5 m del flanco más bajo o por debajo (corre por lo bajo). Aceptados: {len(canales_ok)} vías; rechazados "
        f"(a media ladera o en terraplén, como un canal de riego): {len(canales_no)} vías ({', '.join(str(k) for k in canales_no)}).",
        "Relleno de depresiones Priority-Flood + ε (Barnes et al. 2014) y dirección de flujo D8 por máxima pendiente.",
        f"Red de drenaje = ríos OSM ∪ arroyos y canales de drenaje OSM ∪ celdas con área drenada ≥ {es(UMBRAL_KM2)} km² ({int(round(UMBRAL_KM2 * 1e6 / PASO ** 2))} "
        f"celdas de 30 m; criterio técnico) fuera de la red mapeada: los cauces derivados a ≤ {CERCA_OSM_M:g} m de un cauce OSM se sustituyen por él "
        f"({est_r['celdas_derivadas_sustituidas_por_cauce_osm']} celdas) y los tramos derivados sobre celdas que el relleno elevó más de "
        f"{es(UMBRAL_RELLENO_M)} m se excluyen ({est_r['celdas_derivadas_excluidas_por_relleno']} celdas); quedan {est_r['celdas_derivadas_usadas']} celdas derivadas.",
        "Cota del cauce: en los ríos OSM, mínimo 5×5 (±60 m) del DSM sin corregir, para tomar la lámina de agua y no la orilla arbolada; en arroyos y "
        "canales OSM, mínimo 3×3 del DEM corregido (absorbe el desfase del eje); en los derivados, la propia celda del DEM corregido. Perfil no creciente "
        "aguas abajo solo dentro de cada tipo de cauce; un cauce menor no queda por debajo del nivel del río mayor al que entrega.",
        "HAND = altura de la celda (DEM corregido, sin quemar ni rellenar) − cota del cauce al que drena siguiendo el D8. Valores negativos (depresiones del DSM) → 0.",
        "Remuestreo bilineal de UTM a la rejilla común; recorte a 0–60 m para la publicación.",
    ]
    filas_u = [f for f in tabla_b if f["exclusion_relleno_m"] == UMBRAL_RELLENO_M]
    lim_red = [
        f"La red menor combina los arroyos y canales de drenaje de OpenStreetMap ({n_ar} arroyos y {len(canales_ok)} tramos de canal aceptados) con cauces "
        f"derivados del DEM (área drenada ≥ {es(UMBRAL_KM2)} km², criterio técnico) donde OSM no mapea nada. OSM no es exhaustivo: los cauces menores "
        "que la amenaza ALTA del IDEAM señala al sur de la cabecera y en Zaragoza no están en OSM, y allí el HAND se mide respecto a cauces lejanos "
        "(susceptibilidad subestimada). Algunos cauces derivados pueden no corresponder a cauces reales. La función de los canales OSM (drenaje "
        "o riego) no está etiquetada: se decide con una prueba topográfica que puede equivocarse en terreno llano.",
        "Resultado sensible al umbral de área drenada (como se ha documentado en otros estudios, p. ej. Alabbad 2026, Water 18(13):1598). HAND mediano "
        "de la cabecera: " + "; ".join(
            (f"{es(f['hand_mediana_cabecera_m'])} m con {es(f['umbral_km2'])} km²" if not isinstance(f['umbral_km2'], str)
             else f"{es(f['hand_mediana_cabecera_m'])} m sin red derivada (solo cauces OSM)")
            for f in filas_u) + ". Detalle en datos/series/inundacion.json (clave 'sensibilidad_red_menor').",
        f"Los tramos derivados que cruzan depresiones rellenadas del DSM (relleno > {es(UMBRAL_RELLENO_M)} m) se excluyen de la red: allí el D8 "
        "traza rectas sin cauce real. Las celdas que drenaban a ellos miden su HAND respecto al siguiente cauce aguas abajo; las que quedan "
        f"por debajo de él (depresiones del DSM) toman HAND 0: {neg_r['celdas_utm_en_rejilla']} de {neg_r['celdas_utm_rejilla_total']} celdas UTM "
        f"de la rejilla ({es(100 * neg_r['celdas_utm_en_rejilla'] / neg_r['celdas_utm_rejilla_total'], '.1f')} %), con profundidad mediana "
        f"{es(neg_r['profundidad_bajo_la_referencia_m']['p50'])} m (p90 {es(neg_r['profundidad_bajo_la_referencia_m']['p90'])} m). En un modelo de "
        "superficie muchas de esas depresiones son artefactos (campos rodeados de árboles o edificios) y allí el HAND 0 puede exagerar la susceptibilidad; "
        "el área por zona está en 'resumen.zonas[].area_depresion_dsm_ha' de datos/series/inundacion.json.",
    ]
    lim_hand = [
        lim_dsm,
        "No es la amenaza oficial por inundación: esa está en el POT de Cartago, en los estudios de la CVC y en la zonificación del IDEAM, "
        "que modelan caudales, periodos de retorno, diques y obras. Un HAND alto NO descarta amenaza.",
        "HAND solo mide posición del terreno respecto al cauce; no considera caudales, lluvias, diques, jarillones, alcantarillado ni remanso del Cauca sobre La Vieja.",
    ] + lim_red + [
        "Los ejes de OSM pueden estar desplazados decenas de metros del cauce actual; los ríos migran.",
        "Resolución de 30 m: no resuelve bordillos, muros ni diferencias de 1–2 m entre calles vecinas.",
    ] + ([f"El CHM v1 de Meta/WRI se infiere de imágenes ópticas ({int(fch['min'])}–{int(fch['max'])} en la rejilla; fecha codificada como "
          "año − 2000, supuesto por el rango de valores) y el DSM es de 2011–2015: los árboles talados o plantados entre ambas fechas quedan mal corregidos. "
          "El CHM subestima doseles altos y densos; la curva de corrección se calibró con doseles de 2–15 m de altura media."] if cal and fch else [])
    meta_hand = {
        "titulo": "Altura sobre el drenaje más cercano (HAND)",
        "descripcion": "Cuántos metros está cada lugar por encima del río o cauce al que escurre su agua. Cuanto más bajo, más fácil que el agua lo alcance en una creciente; un valor alto no descarta inundación.",
        "unidad": "m",
        "fuente": FUENTE_DEM | {"cita": FUENTE_DEM["cita"] + ". " + FUENTE_OSM + (". " + CITA_CHM if cal else "")},
        "periodo": "Topografía 2011–2015 (TanDEM-X); dosel Meta/WRI CHM v1 (imágenes 2014–2018); cauces OSM descargados en 2026",
        "resolucion_original_m": 30,
        "procesamiento": proc_hand,
        "limitaciones": lim_hand + ["Valores > 60 m se guardan como 60 m (recorte de la capa publicada)."],
        "rango_visual": [0, 30],
        "paleta": ["#08306b", "#2171b5", "#6baed6", "#c6dbef", "#f7fbff"],
        "interpretacion": (
            "Referencias: Nobre et al. (2011, J. Hydrology 404:13–29) calibraron en Amazonia 5,3 m (suelos encharcados/ecotono) y 15 m "
            "(tierras altas) con SRTM 90 m. En el mapa de clases, 6 m y 15 m son los cortes de esta capa (≤ 6 m media, 6–15 m baja, > 15 m "
            "'HAND > 15 m'); el corte de 3 m de la clase alta se aplica a la capa 'hand_rio_mayor', no a esta. Los cortes 3 y 6 m son criterio "
            "técnico no calibrado con inundaciones observadas en Cartago; los valores dependen del umbral de la red menor. Las clases baja y "
            "'HAND > 15 m' no descartan amenaza: la referencia oficial es la zonificación del IDEAM, la CVC y el POT."),
        "parametros": {"umbral_drenaje_km2": UMBRAL_KM2, "umbral_relleno_m": UMBRAL_RELLENO_M, "profundidad_quema_m": PROFUNDIDAD_QUEMA,
                       "profundidad_quema_cauces_osm_menores_m": PROFUNDIDAD_QUEMA_MENOR, "sustitucion_derivados_cerca_de_osm_m": CERCA_OSM_M,
                       "correccion_dosel": bool(cal), "dominio": [DOM_OESTE, DOM_SUR, DOM_ESTE, DOM_NORTE]},
        "avisos_legales": [ATRIB_DEM, EXENCION_DEM, FUENTE_OSM] + ([ATRIB_CHM] if cal else []),
    }
    meta_hand_m = {
        "titulo": "Altura sobre el río La Vieja o el Cauca",
        "descripcion": "Cuántos metros está cada lugar por encima del nivel del río La Vieja o del Cauca, en el punto donde llega su agua. Es la base de la clase de susceptibilidad alta.",
        "unidad": "m",
        "fuente": meta_hand["fuente"],
        "periodo": meta_hand["periodo"],
        "resolucion_original_m": 30,
        "procesamiento": proc_hand[:2 + (1 if txt_cal else 0)] + [
            "Red de referencia = solo los ríos La Vieja y Cauca (ejes y polígonos OSM). La cota del río es el mínimo 5×5 del DSM con perfil no creciente aguas abajo, "
            f"calculado solo entre celdas de río mayor (rebaje p99 {es(b['rebaje_mayor']['p99_m'])} m, máx {es(b['rebaje_mayor']['max_m'])} m).",
            "HAND = altura de la celda (DEM corregido del dosel) − cota del río mayor al que llega su drenaje por D8 (pasando por cualquier cauce menor). Negativos → 0.",
            "Remuestreo bilineal a la rejilla común; recorte a 0–60 m.",
        ],
        "limitaciones": [lim_dsm,
                         "No es la amenaza oficial (POT, CVC, IDEAM). Altura relativa ≠ profundidad de inundación: no hay caudales ni diques. Un valor alto no descarta amenaza.",
                         "El nivel de referencia es el del DEM (2011–2015, lámina de agua en aguas medias o bajas según la fecha de adquisición), no el de una creciente.",
                         "Celdas cuyo drenaje sale del dominio sin tocar La Vieja ni el Cauca quedan sin dato.",
                         "Valores > 60 m se guardan como 60 m."],
        "rango_visual": [0, 30],
        "paleta": meta_hand["paleta"],
        "interpretacion": ("Sin umbral oficial. ≤ 3 m y a ≤ 1,5 km del río = clase alta del mapa de susceptibilidad (criterio técnico). "
                           "Es independiente del umbral de la red menor. La amenaza ALTA del IDEAM junto a La Vieja llega a terrenos bastante más "
                           "altos que 3 m: un valor mayor no descarta amenaza."),
        "avisos_legales": meta_hand["avisos_legales"],
    }
    no_descarta = "no descarta amenaza: consultar la zonificación oficial del IDEAM, la CVC y el POT"
    clases = [
        {"valor": 0, "etiqueta": f"HAND > 15 m sobre el cauce más cercano ({no_descarta})",
         "etiqueta_corta": "HAND > 15 m (no descarta amenaza)", "color": "#f2f2f2"},
        {"valor": 1, "etiqueta": f"Baja: HAND 6–15 m ({no_descarta})", "etiqueta_corta": "Baja (no descarta amenaza)", "color": "#c6dbef"},
        {"valor": 2, "etiqueta": ("Media: ≤ 6 m sobre el cauce más cercano (incluidos arroyos y canales de drenaje), ≤ 3 m sobre La Vieja/Cauca a más "
                                  f"de 1,5 km, o franja de ≤ {DIST_PISO_M:g} m junto a La Vieja/Cauca (regla de piso)"),
         "etiqueta_corta": "Media", "color": "#6baed6"},
        {"valor": 3, "etiqueta": "Alta: ≤ 3 m sobre el nivel del río La Vieja o del Cauca y a ≤ 1,5 km de él", "etiqueta_corta": "Alta", "color": "#08519c"},
    ]
    fa = {(f["hand_max_m"], f["distancia_max_m"]): f for f in tabla_a}
    sens_txt = "; ".join(f"{es(d / 1000)} km → {es(fa[(HAND_ALTA, d)]['area_alta_cabecera_ha'])} ha" for d in (1000.0, 1500.0, 2000.0))
    sens_txt += "; con 4 m y 1,5 km → " + es(fa[(4.0, DIST_MAYOR_M)]["area_alta_cabecera_ha"]) + " ha"
    lim_piso = (f"Regla de piso: las celdas a ≤ {DIST_PISO_M:g} m del eje o del polígono OSM de La Vieja o del Cauca no bajan de 'media' "
                f"({es(piso_est['rejilla_ha'])} ha promovidas en la rejilla, {es(piso_est['cabecera_ha'])} ha en la cabecera), porque allí el dosel "
                "residual del DSM y el desfase de los ejes OSM elevan el HAND. Es un criterio de precaución, no una medición.")
    meta_cls = {
        "titulo": "Susceptibilidad topográfica a inundación",
        "descripcion": ("Zonas que por su poca altura sobre los ríos y cauces podrían inundarse con más facilidad. Es una lectura del relieve, no la "
                        "amenaza oficial: las clases baja y 'HAND > 15 m' no descartan inundación (consultar IDEAM, CVC y POT)."),
        "unidad": "clase (0–3)",
        "tipo": "categorica",
        "clases": clases,
        "fuente": meta_hand["fuente"],
        "periodo": meta_hand["periodo"],
        "resolucion_original_m": 30,
        "procesamiento": proc_hand + [
            f"Clases sobre la rejilla común: 3 alta = HAND respecto a La Vieja/Cauca ≤ {HAND_ALTA:g} m y distancia ≤ {DIST_MAYOR_M:g} m al cauce mayor "
            f"(ejes y polígonos OSM); 2 media = HAND respecto al cauce más cercano ≤ {HAND_MEDIA:g} m, o distancia ≤ {DIST_PISO_M:g} m al cauce mayor "
            f"(regla de piso), y no alta; 1 baja = {HAND_MEDIA:g} < HAND ≤ {HAND_BAJA:g} m; 0 = HAND > {HAND_BAJA:g} m.",
        ],
        "limitaciones": ([aviso_bajas] if aviso_bajas else []) + [
            "No es la amenaza oficial por inundación: esa está en el POT de Cartago, en los estudios de la CVC y en la zonificación del IDEAM, "
            "que modelan caudales, periodos de retorno, diques y obras. Para decisiones, usar esa zonificación.",
        ] + ([resumen_val] if resumen_val else []) + [lim_dsm, lim_piso] + lim_hand[2:] + [
            "Las clases heredan todos los sesgos del HAND; los bordes entre clases son graduales en la realidad.",
            "La clase alta no depende de la red menor, pero sí del corte de 3 m y de la distancia de 1,5 km (criterio técnico). Área alta en la "
            f"cabecera según la distancia: {sens_txt}. La clase alta dentro de la cabecera NO es robusta; ver 'sensibilidad_clase_alta' en datos/series/inundacion.json.",
            "En la llanura del Cauca (occidente y suroccidente) el HAND respecto al río es bajo en grandes extensiones; el corte de 1,5 km dibuja "
            "bordes en arco: más allá, celdas a ≤ 3 m del nivel del río quedan en 'media'.",
            "La clase media mezcla situaciones distintas: poca altura sobre un arroyo, canal o cauce derivado (encharcamiento o desborde local), 3–6 m "
            "sobre cualquier cauce, la franja de ribera de la regla de piso y celdas en depresiones del DSM con HAND 0.",
            "Validación parcial: frente a la amenaza por creciente súbita del IDEAM (TR 50 años) y a las áreas afectadas por La Niña 1988–2022 "
            "(IDEAM). Resultados por polígono, por zona y antes/después de las correcciones en 'validacion' de datos/series/inundacion.json.",
        ] + lim_nina,
        "rango_visual": [0, 4],
        "paleta": ["#f2f2f2", "#c6dbef", "#6baed6", "#08519c", "#08519c"],
        "interpretacion": (
            "Las clases baja y 'HAND > 15 m' NO descartan amenaza: la referencia oficial es la zonificación de amenaza del IDEAM, la CVC y el POT. "
            "Capa categórica: el color k de la paleta corresponde a la clase k (0–3); el quinto color repite la clase 3 para que rango_visual [0, 4] "
            "asigne un color exacto a cada clase. Umbrales: 15 m = límite de tierras bajas de Nobre et al. (2011, SRTM 90 m, Amazonia); 3 m, 6 m, "
            f"1,5 km y la franja de {DIST_PISO_M:g} m = criterio técnico. Santos et al. (2021) usaron 0–3 m como 'muy alta', pero con un DEM TOPODATA de "
            "30 m interpolado y una red de 100 celdas (≈ 0,09 km², unas 55 veces más fina que la de aquí): sus cortes no se trasladan a esta red ni a "
            "un modelo de superficie."),
        "avisos_legales": meta_hand["avisos_legales"],
    }

    est_alt = comun.guardar_capa("altitud", altitud, 0.1, 0, meta_alt)
    est_hand = comun.guardar_capa("hand", hand_pub, 0.01, -10, meta_hand)
    est_hm = comun.guardar_capa("hand_rio_mayor", hand_m_pub, 0.01, -10, meta_hand_m)
    est_cls = comun.guardar_capa("susceptibilidad_inundacion", clase, 1, 0, meta_cls)
    est_occ = None
    occ_eje = {}
    desp = None
    if occ is not None:
        from rasterio.features import rasterize
        for rio_n in ("rio_la_vieja", "rio_cauca"):
            m = rasterize([(comun.lineas_rio(rio_n), 1)], out_shape=(comun.ALTO, comun.ANCHO), transform=comun.transformacion(),
                          fill=0, all_touched=True, dtype="uint8").astype(bool)
            occ_eje[rio_n] = float(np.nanmedian(occ[m]))
        desp = desplazamiento_gsw(occ, altitud)
        print("desplazamiento GSW frente al DEM:", desp)
        dsp = desp["altura_relativa_media_m_por_desplazamiento_fila_columna"]
        v15 = gsw["version"] == "1.5"
        meta_occ = {
            "titulo": f"Agua superficial histórica (ocurrencia {'1984–2024' if v15 else '1984–2020'})",
            "descripcion": f"Porcentaje de las observaciones Landsat entre 1984 y {'2024' if v15 else '2020'} en que se vio agua en cada lugar. Muestra el cauce y las zonas que el río ha ocupado.",
            "unidad": "% del tiempo con agua",
            "fuente": {
                "nombre": (f"JRC Global Surface Water v{gsw['version']} ({'1984–2024' if v15 else '1984–2020'}), capa occurrence — EC JRC / Google"
                           + ("" if v15 else ", vía Microsoft Planetary Computer")),
                "url": URL_GSW15.format(c="occurrence") if v15 else "https://planetarycomputer.microsoft.com/dataset/jrc-gsw",
                "licencia": "Programa Copernicus: libre y gratuita, sin restricción de uso, con cita obligatoria",
                "cita": CITA_GSW,
            },
            "periodo": periodo_gsw,
            "resolucion_original_m": 30,
            "procesamiento": [
                ("Lectura por /vsicurl/ de la ventana de la rejilla común en el COG del JRC (tesela 80W_10N, v1.5)." if v15 else
                 "Búsqueda STAC en Microsoft Planetary Computer (colección jrc-gsw), asset 'occurrence', URL firmada."),
                "La malla de GSW (0,00025°, origen −80° O, 10° N) coincide celda a celda con la rejilla común: sin remuestreo.",
                "255 (sin dato) → sin dato; 0 = nunca se detectó agua; 1–100 = % de observaciones válidas con agua.",
            ],
            "limitaciones": [
                "Landsat (30 m) no ve cauces estrechos ni agua bajo los árboles, y la nubosidad reduce las observaciones válidas.",
                f"En esta rejilla la ocurrencia mediana sobre el eje OSM del río La Vieja es {occ_eje['rio_la_vieja']:.0f} % (cauce estrecho y con orillas arboladas) "
                f"y sobre el del Cauca {occ_eje['rio_cauca']:.0f} %: la capa representa sobre todo al Cauca.",
                "Los cauces se desplazan: hay celdas con agua frecuente que el DEM (2011–2015) muestra como orilla, y viceversa.",
                "Es frecuencia de agua observada, no extensión de crecientes extremas: una inundación de pocos días casi no cambia el porcentaje.",
                ("Precisión de posición de ± 1 píxel (≈ 28 m): el agua frecuente (ocurrencia ≥ 50 %) cae sobre terreno más bajo del DEM si se mueve "
                 f"{desp['mover_hacia']} (altura relativa media {es(dsp[desp['desplazamiento_con_menor_altura']])} m frente a {es(dsp['0,0'])} m sin mover), "
                 f"lo que sugiere que GSW está desplazada ≈ 1 celda hacia el {desp['desfase_gsw']} respecto al DEM. No es concluyente (geolocalización de "
                 "Landsat o migración del cauce) y la capa no se mueve."
                 if desp["desplazamiento_con_menor_altura"] != "0,0" else
                 "Precisión de posición de ± 1 píxel (≈ 28 m); no se detecta desfase sistemático frente al DEM."),
            ] + ([] if v15 else ["Versión 1.3 (1984–2020) porque la v1.5 del JRC no se pudo leer en esta ejecución."]),
            "rango_visual": [0, 100],
            "paleta": ["#ffffff", "#c6dbef", "#6baed6", "#2171b5", "#08306b"],
            "interpretacion": "Sin umbrales normativos. 100 % = agua permanente (cauce); valores bajos = agua ocasional (playas, orillas, cauces abandonados).",
            "avisos_legales": ["Source: EC JRC/Google", CITA_GSW],
        }
        est_occ = comun.guardar_capa("agua_ocurrencia", occ, 0.01, 0, meta_occ)

    # ================================================= red de drenaje (GeoJSON) y resúmenes
    rectas = escribir_red(r, b, cauces)
    hall = resumen_zonas(clase, clase_sin_piso, hand, hand_bruto, hand_m, occ, ref, rio, dist, tabla_a, tabla_b, val, b, r, rm, rectas, gsw,
                         cauces, fch, aviso_bajas, desp, extra.get("hand_bruto_anterior"))

    verificar(altitud, hand, hand_m, hand_pub, clase, occ, dist, dem_geo, tr_geo, b, r, rm)
    print(json.dumps({"altitud": est_alt, "hand": est_hand, "hand_rio_mayor": est_hm, "susceptibilidad": est_cls, "agua": est_occ},
                     ensure_ascii=False)[:2500])
    print(json.dumps(hall, ensure_ascii=False, indent=1, default=comun._json_default)[:6000])
    print(f"Listo en {time.time() - t_ini:.0f} s")


def _segmentos(abajo, desde, hacia, tr_utm, W):
    """Enlaces D8 de las celdas 'desde' a su vecina aguas abajo si está en 'hacia', en lon/lat."""
    from pyproj import Transformer
    from shapely.geometry import LineString
    from shapely.ops import linemerge
    a_geo = Transformer.from_crs(CRS_UTM, "EPSG:4326", always_xy=True)
    idx = np.flatnonzero(desde.ravel() & (abajo >= 0))
    idx = idx[hacia.ravel()[abajo[idx]]]
    if idx.size == 0:
        return None
    f0, c0 = np.divmod(idx, W)
    f1, c1 = np.divmod(abajo[idx], W)
    x0, y0 = tr_utm * (c0 + 0.5, f0 + 0.5)
    x1, y1 = tr_utm * (c1 + 0.5, f1 + 0.5)
    lo0, la0 = a_geo.transform(x0, y0)
    lo1, la1 = a_geo.transform(x1, y1)
    return linemerge([LineString([(a, b), (c, d)]) for a, b, c, d in zip(lo0, la0, lo1, la1)])


def tramos_rectos(abajo, mascara, orden, minimo=30):
    """Número de tramos de ≥ 'minimo' celdas seguidas con la misma dirección D8 dentro de la máscara (y celdas en ellos)."""
    m = mascara.ravel()
    n = abajo.size
    delta = np.where(abajo >= 0, abajo - np.arange(n), 0)
    run = np.zeros(n, np.int64)
    ab, dl, ml = abajo.tolist(), delta.tolist(), m.tolist()
    rl = run.tolist()
    for i in orden.tolist():                # aguas abajo primero
        if ml[i]:
            d = ab[i]
            rl[i] = rl[d] + 1 if (d >= 0 and ml[d] and dl[d] == dl[i]) else 1
    run = np.array(rl)
    pred = np.zeros(n, bool)
    j = np.flatnonzero(m & (abajo >= 0))
    j = j[m[abajo[j]] & (delta[abajo[j]] == delta[j])]
    pred[abajo[j]] = True
    inicios = m & (run >= minimo) & ~pred
    return int(inicios.sum()), int(run[inicios].sum())


def escribir_red(r, b, cauces=()):
    """Red de drenaje usada como referencia del HAND, recortada a la rejilla común, y trayectos excluidos."""
    from shapely import set_precision
    from shapely.geometry import MultiLineString, box, mapping
    from shapely.ops import unary_union
    caja = box(comun.OESTE, comun.SUR, comun.ESTE, comun.NORTE)
    abajo, tr_utm, W = b["abajo"], b["tr_utm"], b["W"]
    red, der, exc = r["red"], r["derivados"], r["excluidos"]
    derivada = _segmentos(abajo, der, red, tr_utm, W)
    excluida = _segmentos(abajo, exc, exc | red, tr_utm, W)
    lin = MultiLineString([comun.lineas_rio("rio_la_vieja"), comun.lineas_rio("rio_cauca")])
    ev = b.get("canales_evaluados", {})
    osm_rios = [c["geom"] for c in cauces if c["tipo"] == "rio"]
    osm_menor = [c["geom"] for c in cauces if c["tipo"] == "arroyo" or (c["tipo"] == "canal" and ev.get(c["id"], {}).get("drenaje"))]
    osm_no = [c["geom"] for c in cauces if c["tipo"] == "canal" and not ev.get(c["id"], {}).get("drenaje")]
    feats = []
    for tipo, g, fuente, uso in (
            ("rio_mayor_osm", lin, "Ejes OSM de los ríos La Vieja y Cauca (© colaboradores de OpenStreetMap, ODbL 1.0)", True),
            ("otro_rio_osm", unary_union(osm_rios) if osm_rios else None, "Otros ríos de OSM (© colaboradores de OpenStreetMap, ODbL 1.0)", True),
            ("arroyo_o_canal_de_drenaje_osm", unary_union(osm_menor) if osm_menor else None,
             "Arroyos (con sus alcantarillas) y canales de OSM que pasan la prueba topográfica de drenaje (© colaboradores de OpenStreetMap, ODbL 1.0)", True),
            ("canal_osm_no_usado", unary_union(osm_no) if osm_no else None,
             "Canales de OSM que NO pasan la prueba de drenaje (corren a media ladera o en terraplén, como un canal de riego); no se usan "
             "(© colaboradores de OpenStreetMap, ODbL 1.0)", False),
            ("cauce_derivado", derivada, (f"Derivado del Copernicus DEM GLO-30 (corregido del dosel con Meta/WRI CHM v1): D8 con área drenada ≥ "
                                          f"{UMBRAL_KM2:g} km², fuera de depresiones rellenadas y a más de {CERCA_OSM_M:g} m de los cauces OSM"), True),
            ("trayecto_sobre_relleno", excluida, f"Trayecto D8 con área drenada ≥ {UMBRAL_KM2:g} km² sobre celdas elevadas > {es(UMBRAL_RELLENO_M)} m por el relleno "
             "de depresiones: NO es un cauce observado y NO se usa como referencia del HAND", False)):
        if g is None:
            continue
        g = set_precision(g.intersection(caja).simplify(0.00005), 0.000001)
        if g.is_empty:
            continue
        feats.append({"type": "Feature", "properties": {"tipo": tipo, "usado_como_referencia_hand": uso, "umbral_km2": UMBRAL_KM2,
                                                        "umbral_relleno_m": UMBRAL_RELLENO_M, "fuente": fuente},
                      "geometry": json.loads(json.dumps(mapping(g)))})
    fc = {"type": "FeatureCollection", "name": "inundacion_drenaje",
          "metadatos": {"descripcion": ("Red de drenaje usada como referencia del HAND: ejes OSM de los ríos, arroyos y canales de drenaje OSM "
                                        "y cauces derivados por acumulación de flujo D8 donde OSM no mapea nada. Los trayectos sobre depresiones "
                                        "rellenadas y los canales OSM que no pasan la prueba de drenaje se publican aparte y no se usan."),
                        "licencia": ("Derivado de Copernicus WorldDEM-30, de OpenStreetMap (ODbL 1.0) y de Meta/WRI High Resolution Canopy "
                                     "Height Maps v1 (CC BY 4.0)"),
                        "aviso": ATRIB_DEM, "exencion_responsabilidad": EXENCION_DEM,
                        "avisos_legales": [ATRIB_DEM, EXENCION_DEM, FUENTE_OSM, ATRIB_CHM]},
          "features": feats}
    os.makedirs(VECTORES, exist_ok=True)
    ruta = os.path.join(VECTORES, "inundacion_drenaje.geojson")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, separators=(",", ":"), default=comun._json_default)
    rect_usados = tramos_rectos(abajo, der, b["orden"])
    rect_todos = tramos_rectos(abajo, der | exc, b["orden"])
    print("red de drenaje:", ruta, f"{os.path.getsize(ruta) / 1024:.0f} KB",
          [(x["properties"]["tipo"], x["geometry"]["type"], len(x["geometry"].get("coordinates", []))) for x in feats],
          f"tramos rectos ≥ 30 celdas: usados {rect_usados}, con los excluidos {rect_todos}")
    return {"tramos_rectos_ge_30_celdas_red_usada": {"tramos": rect_usados[0], "celdas": rect_usados[1]},
            "tramos_rectos_ge_30_celdas_sin_exclusion": {"tramos": rect_todos[0], "celdas": rect_todos[1]}}


def resumen_zonas(clase, clase_sin_piso, hand, hand_bruto, hand_m, occ, ref, rio, dist, tabla_a, tabla_b, val, b, r, rm, rectas, gsw,
                  cauces=(), fch=None, aviso_bajas=None, desp=None, hand_bruto_ant=None):
    zonas = comun.comunas()
    mz = comun.mascara_zonas(zonas)
    urb = comun.mascara_urbana()
    area = comun.area_celda_m2()

    def bloque(m):
        v = m & np.isfinite(clase)
        res = {"celdas": int(v.sum()), "area_ha": ha(v, area)}
        for k, nom in ((3, "alta"), (2, "media"), (1, "baja"), (0, "sin")):
            mk = v & (clase == k)
            res[f"celdas_{nom}"] = int(mk.sum())
            res[f"area_{nom}_ha"] = ha(mk, area)
            res[f"pct_{nom}"] = round(100.0 * mk.sum() / max(v.sum(), 1), 2)
        for nom, arr in (("hand", hand), ("hand_rio_mayor", hand_m)):
            h = arr[m & np.isfinite(arr)]
            res[f"{nom}_mediana_m"] = round(float(np.median(h)), 2) if h.size else None
            res[f"{nom}_p10_m"] = round(float(np.percentile(h, 10)), 2) if h.size else None
        if occ is not None:
            o = occ[m & np.isfinite(occ)]
            res["celdas_agua_observada_ge_10pct"] = int((o >= 10).sum())
        med = v & (clase == 2)
        res["area_media_depresion_dsm_ha"] = ha(med & (hand_bruto < 0), area)            # HAND bruto < 0: bajo la cota de su cauce
        res["area_media_0_3m_sobre_cauce_menor_ha"] = ha(med & (hand_bruto >= 0) & (hand <= HAND_ALTA) & (ref > 1), area)
        res["area_media_0_3m_sobre_arroyo_o_canal_osm_ha"] = ha(med & (hand_bruto >= 0) & (hand <= HAND_ALTA) & (ref == GRUPO_OSM_MENOR), area)
        res["area_media_0_3m_sobre_cauce_derivado_ha"] = ha(med & (hand_bruto >= 0) & (hand <= HAND_ALTA) & (ref == GRUPO_DERIVADO), area)
        if hand_bruto_ant is not None:
            res["area_depresion_dsm_ha_version_anterior"] = ha(m & np.isfinite(hand_bruto_ant) & (hand_bruto_ant < 0), area)
            res["area_hand_menor_1cm_ha_version_anterior"] = ha(m & np.isfinite(hand_bruto_ant) & (hand_bruto_ant < 0.01), area)
            dep = m & np.isfinite(hand_bruto_ant) & (hand_bruto_ant < 0)
            res["depresion_anterior_ahora_sobre_arroyo_o_canal_osm_ha"] = ha(dep & (ref == GRUPO_OSM_MENOR), area)
            res["depresion_anterior_hand_actual_p10_p50_p90_m"] = ([round(float(x), 2) for x in np.nanpercentile(hand_bruto[dep], [10, 50, 90])]
                                                                   if dep.any() else None)
        res["area_media_regla_de_piso_ha"] = ha(med & (clase_sin_piso < 2), area)
        res["area_depresion_dsm_ha"] = ha(v & (hand_bruto < 0), area)
        res["area_hand_menor_1cm_ha"] = ha(v & (hand < 0.01), area)
        return res

    out = {"rejilla_completa": bloque(np.ones_like(urb)), "cabecera_urbana": bloque(urb), "zonas": []}
    for z in zonas:
        bl = bloque(mz == z["indice"])
        bl.update({"id": z["id"], "nombre": z["nombre"]})
        out["zonas"].append(bl)
    alta = clase == 3
    alta_urb = urb & alta
    out["zonas_con_alta_en_cabecera"] = [
        {"id": z["id"], "nombre": z["nombre"], "celdas_alta": int((alta_urb & (mz == z["indice"])).sum()),
         "area_alta_ha": ha(alta_urb & (mz == z["indice"]), area)}
        for z in zonas if (alta_urb & (mz == z["indice"])).any()]
    out["celdas_alta_cabecera_fuera_de_comunas"] = int((alta_urb & (mz == 0)).sum())
    # dónde está la clase alta: por río y por sector
    lat, lon = comun.centros_celdas()
    out["alta_por_rio"] = {
        "descripcion": "Área de clase alta según el río mayor al que llega el drenaje de la celda (D8).",
        "la_vieja_ha": ha(alta & (rio == 1), area), "cauca_ha": ha(alta & (rio == 2), area),
        "la_vieja_cabecera_ha": ha(alta_urb & (rio == 1), area), "cauca_cabecera_ha": ha(alta_urb & (rio == 2), area),
        "al_occidente_de_la_cabecera_ha": ha(alta & (lon < -75.93), area),
        "al_norte_de_4_77_ha": ha(alta & (lat > 4.77), area),
        "al_sur_de_4_72_ha": ha(alta & (lat < 4.72), area),
    }
    nom_ref = {1: "rio_mayor", 2: "otros_rios_osm", 3: "cauce_derivado", 4: "arroyo_o_canal_osm"}
    out["referencia_del_hand"] = {
        "descripcion": ("Celdas según el cauce respecto al que se mide 'hand' (el primero de la red al que llegan por D8). 'otros_rios_osm' "
                        "sustituye a la antigua clave 'consota' (Consota y demás ríos OSM)."),
        "rejilla_ha": {nom_ref[k]: ha(ref == k, area) for k in (1, 2, 3, 4)},
        "cabecera_ha": {nom_ref[k]: ha(urb & (ref == k), area) for k in (1, 2, 3, 4)},
        "clase_media_cabecera_por_referencia_ha": {nom_ref[k]: ha(urb & (clase == 2) & (ref == k), area) for k in (1, 2, 3, 4)},
        "clase_media_cabecera_hand_le_3_cauce_menor_ha": ha(urb & (clase == 2) & (hand <= HAND_ALTA) & (ref > 1), area),
    }
    # comparación con la regla de la versión anterior y con la variante 'drena directamente al río mayor'
    vieja = np.isfinite(hand) & (hand <= HAND_ALTA) & (dist <= DIST_MAYOR_M)
    directa = alta & (ref == 1) & (hand <= HAND_ALTA)
    out["comparacion_reglas_clase_alta"] = {
        "regla_publicada": {"descripcion": "hand_rio_mayor ≤ 3 m y ≤ 1,5 km del cauce mayor",
                            "rejilla_ha": ha(alta, area), "cabecera_ha": ha(alta_urb, area), "celdas_cabecera": int(alta_urb.sum())},
        "regla_anterior": {"descripcion": "HAND respecto a cualquier cauce ≤ 3 m y ≤ 1,5 km del cauce mayor (versión anterior; etiqueta engañosa)",
                           "rejilla_ha": ha(vieja, area), "cabecera_ha": ha(vieja & urb, area),
                           "rejilla_con_cauce_menor_de_referencia_ha": ha(vieja & (ref > 1), area)},
        "solo_si_drena_directamente_al_rio_mayor": {"descripcion": "regla publicada y además el primer cauce de la red es La Vieja o el Cauca",
                                                     "rejilla_ha": ha(directa, area), "cabecera_ha": ha(directa & urb, area)},
    }
    puntos = []
    for nom, (la, lo) in PUNTOS.items():
        f, c = celda(la, lo)
        ventana = (slice(max(f - 5, 0), f + 6), slice(max(c - 5, 0), c + 6))
        puntos.append({"punto": nom, "lat": la, "lon": lo, "fila": f, "columna": c,
                       "hand_m": round(float(hand[f, c]), 2), "hand_rio_mayor_m": round(float(hand_m[f, c]), 2),
                       "hand_rio_mayor_ventana_11x11_mediana_m": round(float(np.nanmedian(hand_m[ventana])), 1),
                       "hand_ventana_11x11_min_mediana_max_m": [round(float(np.nanmin(hand[ventana])), 1),
                                                                round(float(np.nanmedian(hand[ventana])), 1),
                                                                round(float(np.nanmax(hand[ventana])), 1)],
                       "clase": int(clase[f, c]), "distancia_cauce_mayor_m": round(float(dist[f, c])),
                       "rio_mayor_de_llegada": {1: "La Vieja", 2: "Cauca"}.get(int(rio[f, c]) if np.isfinite(rio[f, c]) else 0)})
    out["puntos_de_control"] = puntos
    # ---- hallazgos (todas las cifras salen de los datos)
    hallazgos = [aviso_bajas] if aviso_bajas else []
    vi = val.get("ideam_creciente_subita_tr50")
    ef = val.get("efecto_correcciones", {}).get("variantes", {})
    if vi:
        grupos = vi["corredor_la_vieja_frente_a_cauces_menores"]
        cor, men = grupos.get("corredor del río La Vieja"), grupos.get("cauce menor")
        menores = [p for p in vi["por_poligono_alta"] if p["tipo"] == "cauce menor"]
        if cor:
            c = cor["en_nuestras_clases"]
            hallazgos.append(
                f"Corredor del río La Vieja (amenaza ALTA del IDEAM, {es(cor['area_ha'])} ha): {es(c['clase_3_pct'])} % en clase alta, {es(c['clase_2_pct'])} % "
                f"en media y {es(round(c['clase_1_pct'] + c['clase_0_pct'], 1))} % ({es(cor['en_clases_baja_o_0_ha'])} ha) en baja o HAND > 15 m"
                + (f" (a {es(cor['en_clases_baja_o_0_distancia_mediana_al_cauce_mayor_m'])} m del cauce mayor y HAND {es(cor['en_clases_baja_o_0_hand_mediana_m'])} m "
                   "en mediana, fuera de la franja de la regla de piso)" if cor["en_clases_baja_o_0_ha"] else "")
                + ". Antes de corregir el dosel y aplicar la regla de piso, las orillas arboladas de La Vieja caían en baja o HAND > 15 m porque el DSM "
                "cuenta las copas como terreno.")
        if men and menores:
            c = men["en_nuestras_clases"]
            hallazgos.append(
                f"Cauces menores con amenaza ALTA del IDEAM (polígonos {', '.join(str(p['objectid_ideam']) for p in menores)}; sur de la cabecera y "
                f"Zaragoza; {es(men['area_ha'])} ha, el {es(round(100 * men['area_ha'] / vi['por_clase_ideam'][0]['area_ha'], 1))} % de la amenaza ALTA "
                f"de la rejilla): {es(round(c['clase_1_pct'] + c['clase_0_pct'], 1))} % en baja o HAND > 15 m y {es(c['clase_2_pct'])} % en media. "
                "Esos cauces no están en OpenStreetMap y el DSM no los resuelve: el producto NO sirve para descartar amenaza allí.")
        zz = next((z for z in vi["por_zona"] if z["nombre"].startswith("Zaragoza")), None)
        if zz and zz["ideam_alta_ha"]:
            bo = round(zz["ideam_alta_en_nuestra_clase_1_ha"] + zz["ideam_alta_en_nuestra_clase_0_ha"], 2)
            hallazgos.append(
                f"Zaragoza: de {es(zz['ideam_alta_ha'])} ha con amenaza ALTA del IDEAM, {es(zz['ideam_alta_en_nuestra_clase_3_ha'])} ha quedan en clase alta, "
                f"{es(zz['ideam_alta_en_nuestra_clase_2_ha'])} ha en media y {es(bo)} ha ({es(zz['ideam_alta_en_clases_baja_o_0_pct'])} %) en baja o HAND > 15 m "
                f"({es(zz['ideam_alta_en_nuestra_clase_1_ha'])} ha en baja y {es(zz['ideam_alta_en_nuestra_clase_0_ha'])} ha en HAND > 15 m).")
    c4 = next((z for z in out["zonas"] if z["nombre"] == "Comuna 4"), None)
    if c4:
        hallazgos.append(
            f"Comuna 4: {es(c4['area_media_ha'])} ha en clase media ({es(c4['pct_media'])} % de la comuna), fuera de la mancha de amenaza por creciente súbita TR 50 del IDEAM; parte de ella coincide con áreas afectadas por inundación en eventos La Niña del IDEAM (cruce por zona en datos/indicadores.json). De ellas, "
            f"{es(c4['area_media_depresion_dsm_ha'])} ha son depresiones del DSM (celdas por debajo de la cota de su cauce, HAND bruto negativo llevado "
            f"a 0; pueden ser artefactos del modelo de superficie), {es(c4['area_media_0_3m_sobre_cauce_menor_ha'])} ha están a 0–3 m sobre un cauce "
            f"menor ({es(c4['area_media_0_3m_sobre_arroyo_o_canal_osm_ha'])} ha sobre arroyos o canales de drenaje mapeados en OSM, "
            f"{es(c4['area_media_0_3m_sobre_cauce_derivado_ha'])} ha sobre cauces derivados) y el resto a 3–6 m sobre un cauce"
            + (f". En la versión anterior (DSM sin corregir y red solo del DEM) la comuna tenía {es(c4['area_depresion_dsm_ha_version_anterior'])} ha con "
               f"HAND bruto negativo ({es(c4['area_hand_menor_1cm_ha_version_anterior'])} ha con HAND < 1 cm): celdas por debajo de la cota del cauce "
               f"derivado al que drenaban; ahora {es(c4['depresion_anterior_ahora_sobre_arroyo_o_canal_osm_ha'])} ha de ellas miden su HAND respecto a un "
               "arroyo o canal de drenaje mapeado en OSM y quedan a "
               + "–".join(es(x) for x in (c4['depresion_anterior_hand_actual_p10_p50_p90_m'] or [])[::2])
               + f" m sobre él (p10–p90; mediana {es((c4['depresion_anterior_hand_actual_p10_p50_p90_m'] or [None, 0])[1])} m)"
               if c4.get("depresion_anterior_hand_actual_p10_p50_p90_m") else "") + ".")
    if ef and ef.get("version_anterior_dsm_sin_correcciones"):
        a, p = ef["version_anterior_dsm_sin_correcciones"]["cabecera"], ef["publicada_dosel_red_osm_y_regla_de_piso"]["cabecera"]
        rf = out["referencia_del_hand"]["clase_media_cabecera_por_referencia_ha"]
        hallazgos.append(
            f"En la cabecera la clase media pasa de {es(a['area_clase_2_ha'])} ha (versión anterior) a {es(p['area_clase_2_ha'])} ha y la alta de "
            f"{es(a['area_clase_3_ha'])} a {es(p['area_clase_3_ha'])} ha; {es(rf['arroyo_o_canal_osm'])} ha de la clase media se miden ahora respecto a "
            "arroyos o canales de drenaje mapeados en OSM. La función de esos canales (drenaje o riego) no está etiquetada en OSM: se decidió con una "
            "prueba topográfica (corren por lo bajo del relieve), no con documentos.")
    if ef:
        a, p = ef.get("version_anterior_dsm_sin_correcciones"), ef.get("publicada_dosel_red_osm_y_regla_de_piso")
        if a and p and "ideam_alta_en_clases_baja_o_0_pct" in a["cabecera"]:
            hallazgos.append(
                f"Efecto de las correcciones: la amenaza ALTA del IDEAM en la cabecera que caía en baja o HAND > 15 m pasa del "
                f"{es(a['cabecera']['ideam_alta_en_clases_baja_o_0_pct'])} % al {es(p['cabecera']['ideam_alta_en_clases_baja_o_0_pct'])} %, y en la rejilla del "
                f"{es(a['rejilla']['ideam_alta_en_clases_baja_o_0_pct'])} % al {es(p['rejilla']['ideam_alta_en_clases_baja_o_0_pct'])} % (corrección del dosel, "
                "arroyos y canales de OSM y regla de piso de la franja de ribera; detalle por paso en 'validacion.efecto_correcciones').")
    serie = {
        "nombre": "inundacion",
        "titulo": "Susceptibilidad topográfica a inundación por zona (HAND)",
        "descripcion": ("Área por clase de susceptibilidad topográfica (HAND) en la cabecera y en cada zona, sensibilidad a los "
                        "parámetros y validación parcial. No es la amenaza oficial del POT, de la CVC ni del IDEAM."),
        "fuente": [FUENTE_DEM["cita"], FUENTE_OSM, ATRIB_CHM + ". " + CITA_CHM, CITA_GSW + f" (v{gsw['version'] if gsw else '—'})", FUENTE_IDEAM],
        "parametros": {"hand_alta_m": HAND_ALTA, "hand_media_m": HAND_MEDIA, "hand_baja_m": HAND_BAJA,
                       "distancia_cauce_mayor_m": DIST_MAYOR_M, "umbral_drenaje_km2": UMBRAL_KM2, "distancia_regla_de_piso_m": DIST_PISO_M,
                       "profundidad_quema_cauces_osm_menores_m": PROFUNDIDAD_QUEMA_MENOR, "sustitucion_derivados_cerca_de_osm_m": CERCA_OSM_M,
                       "calibracion_dosel": {"ventana_celdas": CAL_VENTANA, "desviacion_max_m": CAL_SD_MAX, "bordes_chm_m": CAL_BORDES},
                       "umbral_relleno_m": UMBRAL_RELLENO_M, "profundidad_quema_m": PROFUNDIDAD_QUEMA},
        "definicion_clases": {"3": "hand_rio_mayor ≤ 3 m y distancia ≤ 1,5 km al cauce mayor",
                              "2": f"hand ≤ 6 m, o distancia ≤ {DIST_PISO_M:g} m al cauce mayor (regla de piso), y no clase 3",
                              "1": "6 < hand ≤ 15 m (no descarta amenaza)", "0": "hand > 15 m (no descarta amenaza)"},
        "hallazgos": hallazgos,
        "aviso": aviso_bajas,
        "correccion_dosel": {"fuente": ATRIB_CHM, "cita": CITA_CHM, "fechas_imagenes_rejilla": fch, **(b.get("calibracion_dosel") or {})},
        "cauces_osm": {"vias_por_tipo": {t: sum(1 for c in cauces if c["tipo"] == t) for t in ("rio", "arroyo", "canal")},
                       "canales_prueba_drenaje": {str(k): v for k, v in b.get("canales_evaluados", {}).items()},
                       "fuente": FUENTE_OSM, "consulta": "Overpass API, way[waterway~river|stream|canal|drain|ditch] en el dominio"},
        "desplazamiento_gsw": desp,
        "fecha_proceso": time.strftime("%Y-%m-%d"),
        "resumen": out,
        "red_de_drenaje": {"toda_la_red": r["est"], "solo_rios_mayores": rm["est"], "perfil_rio_mayor": b["rebaje_mayor"], **rectas},
        "sensibilidad_clase_alta": {
            "descripcion": ("Área de clase alta (hand_rio_mayor ≤ corte y distancia ≤ máximo) según el corte de HAND y la distancia al cauce "
                            "mayor. No depende del umbral de la red menor."),
            "filas": tabla_a},
        "sensibilidad_red_menor": {
            "descripcion": ("Efecto del umbral de área drenada de los cauces derivados y de la exclusión de tramos sobre relleno en 'hand' y en "
                            "las clases media, baja y HAND > 15 m. 'regla_anterior_area_alta_cabecera_ha' muestra cuánto dependía de "
                            "estos parámetros la clase alta de la versión anterior (HAND respecto a cualquier cauce)."),
            "filas": tabla_b},
        "validacion": val,
    }
    comun.guardar_json(os.path.join(SERIES, "inundacion.json"), serie)
    return out


def verificar(altitud, hand, hand_m, hand_pub, clase, occ, dist, dem_geo, tr_geo, b, r, rm):
    from PIL import Image
    print("\n=== VERIFICACIONES ===")
    # 1. PNG decodificada vs .npy
    for nombre, esc, des in (("altitud", 0.1, 0), ("hand", 0.01, -10), ("hand_rio_mayor", 0.01, -10),
                             ("susceptibilidad_inundacion", 1, 0), ("agua_ocurrencia", 0.01, 0)):
        rp = os.path.join(comun.CAPAS, f"{nombre}.png")
        if not os.path.exists(rp):
            continue
        im = np.asarray(Image.open(rp)).astype(np.int64)
        vv = im[..., 0] * 256 + im[..., 1]
        dec = np.where(vv == 0, np.nan, (vv - 1) * esc + des)
        ref = comun.cargar_capa(nombre)
        mismos_nan = np.array_equal(np.isnan(dec), np.isnan(ref))
        err = float(np.nanmax(np.abs(dec - ref)))
        print(f"PNG↔npy {nombre}: NaN iguales={mismos_nan}, error máx={err:.4f} (tolerancia {esc / 2})")
        assert mismos_nan and err <= esc / 2 + 1e-6
    # 2. norte/sur: la altitud de la rejilla común coincide con la del DEM leído en el mismo punto
    for nom, (la, lo) in PUNTOS.items():
        f, c = celda(la, lo)
        cr, fr = ~tr_geo * (lo, la)   # Affine inversa devuelve (columna, fila)
        zdem = float(dem_geo[int(fr), int(cr)])
        print(f"{nom}: altitud rejilla {altitud[f, c]:.1f} m | DEM directo {zdem:.1f} m | HAND {hand[f, c]:.2f} m | "
              f"HAND río mayor {hand_m[f, c]:.2f} m | clase {clase[f, c]:.0f} | dist. cauce mayor {dist[f, c]:.0f} m"
              + (f" | agua {occ[f, c]:.0f} %" if occ is not None else ""))
        assert abs(altitud[f, c] - zdem) < 3, "posible inversión norte/sur o desplazamiento"
    rng = np.random.default_rng(7)
    ff = rng.integers(0, comun.ALTO, 400)
    cc = rng.integers(0, comun.ANCHO, 400)
    lat, lon = comun.centros_celdas()
    cols, filas = ~tr_geo * (lon[ff, cc], lat[ff, cc])
    zdir = dem_geo[filas.astype(int), cols.astype(int)]
    d_ok = float(np.median(np.abs(altitud[ff, cc] - zdir)))
    d_inv = float(np.median(np.abs(altitud[comun.ALTO - 1 - ff, cc] - zdir)))
    print(f"norte/sur: diferencia mediana con el DEM directo {d_ok:.2f} m; si estuviera invertida {d_inv:.2f} m")
    assert d_ok < 2 and d_inv > 3 * d_ok
    # 3. ríos: HAND y agua sobre el eje OSM (dentro de la rejilla)
    from rasterio.features import rasterize
    for rio in ("rio_la_vieja", "rio_cauca"):
        m = rasterize([(comun.lineas_rio(rio), 1)], out_shape=(comun.ALTO, comun.ANCHO), transform=comun.transformacion(),
                      fill=0, all_touched=True, dtype="uint8").astype(bool)
        h = hand_m[m & np.isfinite(hand_m)]
        txt = (f"{rio}: {int(m.sum())} celdas sobre el eje; HAND río mayor mediana {np.median(h):.2f} m, p90 {np.percentile(h, 90):.2f} m; "
               f"clase 3: {100 * np.mean(clase[m] == 3):.0f} %")
        if occ is not None:
            o = occ[m & np.isfinite(occ)]
            txt += f"; agua observada mediana {np.median(o):.0f} % (resto de la rejilla: {np.nanmedian(occ[~m]):.0f} %)"
        print(txt)
    # 4. rangos y relaciones
    print(f"altitud {np.nanmin(altitud):.1f}–{np.nanmax(altitud):.1f} m; HAND {np.nanmin(hand):.2f}–{np.nanmax(hand):.1f} m "
          f"(publicada {np.nanmin(hand_pub):.2f}–{np.nanmax(hand_pub):.1f}); HAND río mayor {np.nanmin(hand_m):.2f}–{np.nanmax(hand_m):.1f} m; "
          f"clases {np.unique(clase[np.isfinite(clase)])}")
    assert 850 < np.nanmin(altitud) and np.nanmax(altitud) < 2500
    both = np.isfinite(hand) & np.isfinite(hand_m)
    print(f"rejilla: celdas con hand > hand_rio_mayor + 1 cm (remuestreo): {int((hand[both] > hand_m[both] + 0.01).sum())}; "
          f"hand_rio_mayor sin dato: {int((~np.isfinite(hand_m)).sum())}")
    urb = comun.mascara_urbana()
    print(f"HAND mediana cabecera {np.nanmedian(hand[urb]):.1f} m (río mayor {np.nanmedian(hand_m[urb]):.1f} m); "
          f"fuera de la cabecera {np.nanmedian(hand[~urb]):.1f} m; cobertura HAND {100 * np.isfinite(hand).mean():.1f} %")


if __name__ == "__main__":
    main()
