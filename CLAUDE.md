# BioMap Cartago — contexto para Claude

- Producto para decisiones municipales con **datos abiertos reales**. Nunca introducir valores sintéticos, de relleno o inventados; si un dato falta, la interfaz lo dice.
- Página estática sin compilación. Librerías locales en `vendor/` (no volver a CDN: la red del autor es inestable). No introducir npm, bundlers ni frameworks sin que el autor lo pida.
- Todo el JavaScript vive en `window.BM`. Orden de carga en `index.html`: vendor → `datos-osm.js` → `geo.js` → `datos.js` → `solar.js` → `app.js` → `graficos.js` → `decision.js` → `abiertos.js` → `copiloto.js`. Los módulos posteriores a `app.js` se registran con `BM.alIniciar(fn)`.
- Interfaz, comentarios y metadatos en español.
- Contrato de capas: `scripts/comun.py` (rejilla común, PNG de 16 bits, metadatos). Cualquier capa nueva se construye con un script en `scripts/` que use `guardar_capa`.
- Cifras y frases de interpretación en la interfaz salen de los JSON de `datos/`, no se escriben a mano.
- Distinciones obligatorias en todo texto: temperatura superficial (Landsat) ≠ temperatura del aire (ERA5-Land); índice de tráfico ≠ NO₂; susceptibilidad topográfica ≠ amenaza oficial (IDEAM/POT); simulador = asociación, no causalidad.
- Capas del IDEAM: se consultan en vivo (servicio ArcGIS); no copiar sus polígonos a `datos/` mientras la licencia no esté declarada.
- Atribución OpenStreetMap (ODbL) en la interfaz, el README y los metadatos de exportación.
- Python: `.venv/bin/python` (3.12). `fuentes/` es caché local y no se publica.
- Probar con `python3 -m http.server 8765` y revisar la consola: no debe haber errores propios.

## Mapas base
- Satelital: Esri World Imagery fijado en la versión Wayback 32246 (2026-06-30). El mosaico vigente de agosto de 2026 tiene nubes sobre el centro de Cartago; antes de cambiar de versión, comparar visualmente a zoom 16–17.
- No hay modo oscuro: el autor lo pidió retirar el 01-10-2026 (CARTO `dark_all` exige clave de API desde 2026).
- Las etiquetas van en el panel `etiquetas`, por encima de los datos, con `capaEtiquetas()` (limpia las teselas del zoom anterior al cargar).

## Despliegue
Repositorio público github.com/alguarito/biomap-cartago; cada push a `main` publica en https://alguarito.github.io/biomap-cartago/ con `.github/workflows/deploy.yml` (copia index.html, css, js, vendor y datos; sin compilación). `fuentes/` y `.venv/` no se versionan (`/fuentes/` solo en la raíz: `vendor/fuentes/` sí va).

## Versiones
Los recursos locales se enlazan con `?v=N` en `index.html`. Al cambiar CSS o JS, subir N. Los datos usan `VERSION_DATOS` en `js/datos.js`: subirlo al regenerar `datos/`.
