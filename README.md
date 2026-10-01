# BioMap Cartago

**Sitio:** <https://alguarito.github.io/biomap-cartago/>

Plataforma geoambiental de **datos abiertos** para la toma de decisiones en Cartago, Valle del Cauca. Muestra calor urbano, vegetación, arbolado, exposición al tráfico, riesgo hidrológico, población y acceso a parques; prioriza las comunas según criterios ajustables; simula intervenciones con coeficientes calibrados en la propia ciudad; y responde preguntas con un copiloto IA que solo usa estos datos.

Es una página estática sin paso de compilación: HTML, CSS y JavaScript con las librerías incluidas en `vendor/`. Los datos se generan con scripts de Python reproducibles en `scripts/`.

## Qué datos usa

Todas las capas comparten una rejilla de ~28 m (EPSG:4326, 0,00025°, 520 × 428 celdas).

| Capa o serie | Fuente | Licencia |
|---|---|---|
| Temperatura superficial (LST) 2022–2025 y serie 2000–2025 | USGS Landsat 5/7/8/9 Collection 2 Nivel 2, vía Microsoft Planetary Computer | Dominio público (USGS) |
| Vegetación (NDVI) 2024–2025 | Sentinel-2 L2A (Copernicus), vía Element84 Earth Search | Copernicus, libre con atribución |
| Arbolado, área construida y agua | ESA WorldCover 10 m 2021 v200 | CC BY 4.0 |
| Población 2026 | Proyección DANE repartida por manzana del CNPV 2018 (MGN) | DANE, datos abiertos |
| Susceptibilidad topográfica a inundación (HAND), altitud | Copernicus DEM GLO-30 + ejes de ríos OSM | Copernicus DEM, libre con atribución |
| Agua en superficie 1984–2021 | JRC Global Surface Water | Copernicus/JRC, libre con atribución |
| Amenaza por creciente súbita e inundaciones de La Niña | IDEAM, servicio Amenaza_Ambiental (consulta en vivo, no se copia) | Información pública del IDEAM, con atribución |
| Exposición al tráfico | Índice derivado de la red vial de OpenStreetMap | ODbL |
| Parques y equipamientos sensibles | OpenStreetMap | ODbL |
| Comunas, cabecera, ríos y vías | OpenStreetMap | ODbL |
| Clima 1950–2026 | ERA5-Land y ERA5 (Copernicus C3S) vía Open-Meteo; lluvia CHIRPS v3; validación con estaciones IDEAM | CC BY 4.0 |
| Calidad del aire 2022–2026 | CAMS global (Copernicus) vía Open-Meteo | CC BY 4.0 |

Cada capa trae su ficha en `datos/capas/<capa>.json`: fuente, periodo, resolución, pasos de procesamiento, limitaciones y estadísticas. La pestaña **Datos Abiertos** las muestra todas.

### Lo que hay que saber antes de decidir

- **Son estimaciones** de sensores remotos, censos y cartografía colaborativa, no mediciones de campo. Sirven para comparar zonas y priorizar; antes de ejecutar obras hay que contrastarlas con el POT, la CVC, el IDEAM y una visita técnica.
- **Temperatura superficial ≠ temperatura del aire.** La LST es la del suelo y los techos hacia las 10:20 a. m.; la del aire viene del reanálisis ERA5-Land, que subestima los valores absolutos de las estaciones del IDEAM (por eso la plataforma muestra anomalías y tendencias).
- **El tráfico es un índice de exposición**, no una medición de NO₂. El NO₂ y el PM2,5 de CAMS son regionales (~40 km).
- **La susceptibilidad topográfica no es la amenaza oficial.** La referencia oficial disponible es la capa del IDEAM, que la plataforma muestra en vivo.
- **El simulador mide asociaciones**, no causalidad: compara lugares distintos de la ciudad. Los coeficientes de arbolado salen de Cartago; los de techos verdes y pavimentos, de una revisión sistemática (Das et al., 2025). El efecto sobre el NO₂ no se cuantifica porque no hay base.

## Ejecutar en local

```bash
python3 -m http.server 8765
```

y abrir <http://localhost:8765>. Hace falta un servidor (la página lee `datos/` con `fetch`); abrir el archivo directamente no funciona.

## Regenerar los datos

Requiere Python 3.12 con un entorno local:

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python numpy rasterio pyproj shapely pystac-client planetary-computer pillow scipy requests
```

Orden de ejecución (cada script documenta en su cabecera fuentes, licencias y pasos):

1. `scripts/worldcover.py`, `scripts/landsat.py`, `scripts/sentinel2.py`, `scripts/poblacion.py`, `scripts/inundacion.py`, `scripts/aire.py`, `scripts/clima.py`, `scripts/verdes.py` (independientes entre sí)
2. `scripts/indicadores.py` (usa las capas anteriores)
3. `scripts/exportar.py` (GeoTIFF y catálogo de descargas)

Los datos de OpenStreetMap (`fuentes/osm-*.json`) se descargan de Overpass; la consulta está en la cabecera de `scripts/osm.py`. La carpeta `fuentes/` guarda descargas crudas y rejillas intermedias y no se publica.

## Estructura

```
index.html            interfaz (4 pestañas + mapa)
css/app.css           estilos (sin dependencias externas)
vendor/               Leaflet, Chart.js, marked, DOMPurify y la fuente Plus Jakarta Sans
js/datos-osm.js       geometría de referencia de OpenStreetMap (generada)
js/geo.js             zonas, hitos y utilidades geométricas
js/datos.js           lectura y decodificación de las capas (PNG de 16 bits)
js/solar.js           radiación solar en cielo despejado
js/app.js             mapa, capas, leyenda e inspección puntual
js/graficos.js        tendencias de clima, Landsat y aire
js/decision.js        priorización de zonas y simulador calibrado
js/abiertos.js        indicadores, descargas y fichas de método
js/copiloto.js        copiloto IA (Gemini) con contexto de datos
datos/capas/          capas publicadas (PNG codificado + metadatos JSON)
datos/descargas/      las mismas capas en GeoTIFF (COG)
datos/series/         series temporales
datos/vectores/       GeoJSON de zonas, parques y equipamientos
datos/indicadores.json, prioridades.json, calibracion.json, catalogo.json
scripts/              procesamiento reproducible
```

## Copiloto IA

Cada usuario pega su clave de Google AI Studio en la pestaña Copiloto; la clave va del navegador a Google y solo se guarda si el usuario lo pide. Para un despliegue institucional con clave propia, poner un proxy (función serverless) delante de la API.

## Licencias

- Código y contenido propio: CC BY-NC-SA 4.0 (ver `LICENSE`).
- Datos derivados: cada archivo conserva la licencia de su fuente (tabla anterior). Los productos que incluyen geometría de OpenStreetMap se publican bajo ODbL.
- Librerías y tipografía incluidas en `vendor/`: Leaflet (BSD-2), Chart.js y marked (MIT), DOMPurify (Apache-2.0 o MPL-2.0) y Plus Jakarta Sans (OFL 1.1). Sus avisos están en `vendor/LEEME.md` y `vendor/licencias/`.
- Teselas de los mapas base: OpenStreetMap, Esri World Imagery y CARTO, con sus propias condiciones de uso.
- El mapa muestra la atribución de cada fuente mientras su capa está activa.
