/* BioMap Cartago — pestaña Datos Abiertos: matriz de indicadores, descargas y fichas de método. */
'use strict';
(function () {
  const BM = window.BM;
  const { $, $$, fmt, esc } = BM;

  /* Columnas por grupo. Solo se muestran las que existan en datos/indicadores.json. */
  const GRUPOS_TABLA = [
    { id: 'calor', nombre: 'Calor', cols: [
      { k: 'lst_media', t: 'LST media', u: '°C', d: 1 },
      { k: 'lst_anomalia', t: 'vs. cabecera', u: '°C', d: 1, signo: true },
      { k: 'pct_area_calor_extremo', t: 'Área en calor extremo', u: '%', d: 0 },
      { k: 'poblacion_calor_extremo', t: 'Personas en calor extremo', u: '', d: 0 },
      { k: 'tendencia_lst_c_decada', t: 'Tendencia', u: '°C/déc.', d: 2, signo: true },
    ] },
    { id: 'verde', nombre: 'Vegetación y parques', cols: [
      { k: 'arbolado_pct', t: 'Arbolado', u: '%', d: 0 },
      { k: 'ndvi_medio', t: 'NDVI', u: '', d: 2 },
      { k: 'm2_arbolado_por_hab', t: 'Arbolado por hab.', u: 'm²', d: 1 },
      { k: 'm2_verde_publico_por_hab', t: 'Verde público por hab.', u: 'm²', d: 1 },
      { k: 'pct_poblacion_sin_verde_300m', t: 'Sin parque a 300 m', u: '% pob.', d: 0 },
    ] },
    { id: 'riesgo', nombre: 'Inundación (registros oficiales)', cols: [
      { k: 'poblacion_evidencia_inundacion_ideam', alt: 'ideam_evidencia_oficial_poblacion', t: 'Personas en zonas con registro de inundación (IDEAM)', u: '', d: 0 },
      { k: 'pct_poblacion_evidencia_inundacion_ideam', alt: 'ideam_evidencia_oficial_pct_poblacion', t: 'Población con registro', u: '%', d: 1 },
      { k: 'contraste_ideam_creciente_subita_tr50_poblacion_amenaza_alta', t: 'Personas en amenaza alta TR 50 (IDEAM)', u: '', d: 0 },
      { k: 'ideam_nina_observada_poblacion', t: 'Personas en áreas inundadas en La Niña (IDEAM)', u: '', d: 0 },
      { k: 'pct_poblacion_susceptibilidad_media', t: 'Susceptibilidad topográfica media', u: '% pob.', d: 1 },
    ] },
    { id: 'trafico', nombre: 'Tráfico', cols: [
      { k: 'trafico_medio_pob', alt: 'trafico_medio', t: 'Índice medio donde vive la gente', u: '/100', d: 0 },
      { k: 'poblacion_trafico_alto', t: 'Personas con tráfico alto (≥ 60)', u: '', d: 0 },
      { k: 'pct_poblacion_trafico_alto', t: 'Población con tráfico alto', u: '%', d: 1 },
    ] },
    { id: 'poblacion', nombre: 'Población y territorio', cols: [
      { k: 'poblacion', t: 'Población', u: 'hab.', d: 0 },
      { k: 'area_km2', t: 'Área', u: 'km²', d: 2 },
      { k: 'densidad_hab_km2', t: 'Densidad', u: 'hab/km²', d: 0 },
      { k: 'construido_pct', t: 'Construido', u: '%', d: 0 },
    ] },
  ];

  /** Normaliza la lista de zonas de indicadores.json (acepta lista o diccionario). */
  BM.zonasIndicadores = function () {
    const ind = BM.INDICADORES;
    if (!ind) return [];
    let z = ind.zonas || ind.por_zona || ind.features || [];
    if (!Array.isArray(z)) z = Object.entries(z).map(([id, v]) => ({ id, ...v }));
    return z.map((x) => (x.properties ? x.properties : x)).map((x) => conAlternos({ ...plano(x), id: x.id, nombre: x.nombre }));
  };
  /** Completa campos de primer nivel desde sus equivalentes anidados (versiones anteriores de los datos). */
  function conAlternos(o) {
    GRUPOS_TABLA.forEach((g) => g.cols.forEach((c) => { if (o[c.k] === undefined && c.alt && o[c.alt] !== undefined) o[c.k] = o[c.alt]; }));
    return o;
  }
  BM.cabeceraIndicadores = function () {
    const ind = BM.INDICADORES;
    const c = ind && (ind.cabecera || ind.cabecera_urbana || ind.total_cabecera);
    return c ? conAlternos(plano(c)) : null;
  };
  /** Aplana un objeto anidado: los campos internos llevan el prefijo de su padre (a.b → a_b), así no pisan los de primer nivel. */
  function plano(o, salida = {}, prefijo = '') {
    Object.entries(o || {}).forEach(([k, v]) => {
      const clave = prefijo ? `${prefijo}_${k}` : k;
      if (v && typeof v === 'object' && !Array.isArray(v)) plano(v, salida, clave);
      else if (!(clave in salida)) salida[clave] = v;
    });
    return salida;
  }

  /* ---------- matriz ---------- */
  let grupo = GRUPOS_TABLA[0], orden = { k: null, dir: -1 };
  function construirTabla() {
    const zonas = BM.zonasIndicadores();
    if (!zonas.length) {
      $('#tabla').innerHTML = '';
      $('#tabla-nota').textContent = 'Los indicadores por zona aún no están publicados.';
      return;
    }
    const sel = $('#tabla-grupo');
    sel.innerHTML = '';
    GRUPOS_TABLA.forEach((g) => { if (g.cols.some((c) => zonas.some((z) => z[c.k] !== undefined))) sel.add(new Option(g.nombre, g.id)); });
    sel.addEventListener('change', () => { grupo = GRUPOS_TABLA.find((g) => g.id === sel.value); orden = { k: null, dir: -1 }; pintar(); });
    grupo = GRUPOS_TABLA.find((g) => g.id === sel.value) || GRUPOS_TABLA[0];
    $('#tabla tbody').addEventListener('click', (e) => { const tr = e.target.closest('tr'); if (tr) irAZona(tr.dataset.id); });
    $('#tabla tbody').addEventListener('keydown', (e) => { const tr = e.target.closest('tr'); if (tr && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); irAZona(tr.dataset.id); } });
    pintar();
  }

  function pintar() {
    const zonas = BM.zonasIndicadores();
    const cols = grupo.cols.filter((c) => zonas.some((z) => z[c.k] !== undefined));
    $('#tabla thead').innerHTML = `<tr><th data-k="nombre" scope="col">Zona</th>${cols.map((c) =>
      `<th data-k="${c.k}" scope="col" class="num" title="${esc(c.t)}${c.u ? ` (${esc(c.u)})` : ''}">${esc(c.t)}${c.u ? `<small> ${esc(c.u)}</small>` : ''}</th>`).join('')}</tr>`;
    const filas = zonas.slice();
    if (orden.k) filas.sort((a, b) => {
      const va = a[orden.k], vb = b[orden.k];
      return (typeof va === 'string' ? String(va).localeCompare(vb, 'es', { numeric: true }) : (va ?? -Infinity) - (vb ?? -Infinity)) * orden.dir;
    });
    const celda = (c, v) => {
      if (v === null || v === undefined || v === '') return '—';
      if (typeof v !== 'number') return esc(v);
      return (c.signo && v > 0 ? '+' : '') + fmt(v, c.d);
    };
    const cab = BM.cabeceraIndicadores();
    $('#tabla tbody').innerHTML = filas.map((z) => `<tr data-id="${esc(z.id)}" tabindex="0"><td>${esc(z.nombre)}</td>${cols.map((c) => `<td class="num">${celda(c, z[c.k])}</td>`).join('')}</tr>`).join('')
      + (cab ? `<tr class="fila-total"><td>Cabecera urbana</td>${cols.map((c) => `<td class="num">${celda(c, cab[c.k])}</td>`).join('')}</tr>` : '');
    $$('#tabla th').forEach((th) => {
      th.setAttribute('aria-sort', th.dataset.k === orden.k ? (orden.dir > 0 ? 'ascending' : 'descending') : 'none');
      th.addEventListener('click', () => { const k = th.dataset.k; orden = { k, dir: orden.k === k ? -orden.dir : (k === 'nombre' ? 1 : -1) }; pintar(); });
    });
    $('#tabla-nota').innerHTML = 'Toca una fila para verla en el mapa y un encabezado para ordenar. «Calor extremo»: celdas por encima del percentil 90 de la temperatura superficial de la cabecera.';
  }

  function irAZona(id) {
    const z = BM.ZONAS.find((q) => q.id === id);
    if (!z) return;
    const b = L.latLngBounds(z.anillos.flat());
    BM.mapa.flyToBounds(b, { padding: [40, 40], maxZoom: 16, duration: 0.8 });
    const c = b.getCenter();
    BM.inspeccionar(c.lat, c.lng, z.nombre);
  }
  BM.irAZona = irAZona;

  /* ---------- descargas ---------- */
  function descargar(nombre, contenido, tipo) {
    const url = URL.createObjectURL(new Blob([contenido], { type: tipo }));
    const a = Object.assign(document.createElement('a'), { href: url, download: nombre });
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function csvIndicadores() {
    const zonas = BM.zonasIndicadores();
    const claves = Array.from(new Set(zonas.flatMap((z) => Object.keys(z).filter((k) => typeof z[k] !== 'object')))).filter((k) => k !== 'id' && k !== 'nombre');
    const q = (v) => (v === null || v === undefined ? '' : typeof v === 'string' ? `"${v.replace(/"/g, '""')}"` : v);
    return ['# BioMap Cartago - indicadores por zona. Fuentes y licencias: datos/catalogo.json', ['id', 'nombre', ...claves].join(','),
      ...zonas.map((z) => [q(z.id), q(z.nombre), ...claves.map((k) => q(z[k]))].join(','))].join('\n');
  }

  function construirDescargas(catalogo) {
    const items = [];
    if (BM.zonasIndicadores().length) {
      items.push(`<button type="button" class="descarga" data-accion="csv"><b>Indicadores por zona</b><span>CSV</span></button>`);
      items.push(`<a class="descarga" href="datos/vectores/zonas.geojson" download><b>Zonas con indicadores</b><span>GeoJSON</span></a>`);
    }
    const capas = (catalogo && catalogo.capas) || Object.values(BM.DATOS).map((d) => ({ id: d.id, titulo: d.meta.titulo, png: `capas/${d.id}.png`, metadatos: `capas/${d.id}.json` }));
    capas.forEach((c) => {
      const href = c.geotiff ? `datos/${c.geotiff}` : `datos/${c.png}`;
      items.push(`<a class="descarga" href="${esc(href)}" download><b>${esc(c.titulo || c.id)}</b><span>${c.geotiff ? 'GeoTIFF (COG)' : 'PNG codificado'}${c.tamano_tif_kb ? ` · ${c.tamano_tif_kb} KB` : ''}</span><small>Metadatos: <span data-href="datos/${esc(c.metadatos)}">JSON</span></small></a>`);
    });
    [['vectores/equipamientos_exposicion.geojson', 'Equipamientos y su exposición'], ['vectores/equipamientos.geojson', 'Equipamientos sensibles'], ['vectores/espacio_verde.geojson', 'Espacio verde público'],
      ['series/clima.json', 'Clima 1950–2026'], ['series/landsat.json', 'Serie Landsat 2000–2025'], ['series/aire.json', 'Calidad del aire (CAMS)'], ['series/zonas.json', 'Series por zona'], ['calibracion.json', 'Calibración del simulador']]
      .forEach(([f, t]) => {
        const listado = catalogo ? [...(catalogo.series || []), ...(catalogo.vectores || []), ...(catalogo.tablas || [])].find((x) => x.archivo === f) : null;
        if (catalogo && !listado) return;
        items.push(`<a class="descarga" href="datos/${f}" download><b>${esc(t)}</b><span>${f.endsWith('geojson') ? 'GeoJSON' : 'JSON'}${listado ? ` · ${listado.tamano_kb} KB` : ''}</span></a>`);
      });
    $('#descargas').innerHTML = items.join('');
    $('#descargas').addEventListener('click', (e) => {
      if (e.target.closest('[data-accion="csv"]')) descargar('biomap-cartago-indicadores.csv', '﻿' + csvIndicadores(), 'text/csv;charset=utf-8');
      const meta = e.target.closest('[data-href]');
      if (meta) { e.preventDefault(); window.open(meta.dataset.href, '_blank', 'noopener'); }
    });
    $('#descargas-nota').innerHTML = 'Rejilla común EPSG:4326 de 0,00025° (~28 m), 520 × 428 celdas. Cada archivo conserva la licencia de su fuente (ver fichas). Geometría de comunas, vías y parques: © colaboradores de OpenStreetMap, <a href="https://opendatacommons.org/licenses/odbl/" target="_blank" rel="noopener">ODbL</a>.';
  }

  /* ---------- fichas de método ---------- */
  const lista = (a) => (Array.isArray(a) && a.length ? `<ul>${a.map((x) => `<li>${esc(typeof x === 'string' ? x : JSON.stringify(x))}</li>`).join('')}</ul>` : '');
  function fichaFuente(f) {
    if (!f) return '';
    const arr = Array.isArray(f) ? f : [f];
    return arr.map((x) => `<p><b>Fuente:</b> ${x.url ? `<a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.nombre || x.url)}</a>` : esc(x.nombre)}${x.licencia ? ` · <b>Licencia:</b> ${esc(x.licencia)}` : ''}${x.cita ? `<br><small>${esc(x.cita)}</small>` : ''}</p>`).join('');
  }

  function construirFichas() {
    const html = [];
    Object.values(BM.DATOS).forEach(({ meta }) => {
      html.push(`<details class="ficha-capa" id="ficha-${esc(meta.nombre)}"><summary>${esc(meta.titulo || meta.nombre)}<small>${esc(meta.unidad || '')}</small></summary>
        <div class="prosa">
          ${meta.descripcion ? `<p>${esc(meta.descripcion)}</p>` : ''}
          ${fichaFuente(meta.fuente)}
          ${meta.periodo ? `<p><b>Periodo:</b> ${esc(typeof meta.periodo === 'string' ? meta.periodo : JSON.stringify(meta.periodo))}</p>` : ''}
          ${meta.resolucion_original_m ? `<p><b>Resolución de origen:</b> ${esc(meta.resolucion_original_m)} m</p>` : ''}
          ${meta.interpretacion ? `<p><b>Cómo leerla:</b> ${esc(typeof meta.interpretacion === 'string' ? meta.interpretacion : JSON.stringify(meta.interpretacion))}</p>` : ''}
          ${meta.procesamiento ? `<h4>Procesamiento</h4>${lista(meta.procesamiento)}` : ''}
          ${meta.limitaciones ? `<h4>Limitaciones</h4>${lista(meta.limitaciones)}` : ''}
          <p><small>Procesado el ${esc(meta.fecha_proceso || '')} · cobertura ${fmt(meta.cobertura_pct, 1)} % · script <code>scripts/</code></small></p>
        </div></details>`);
    });
    const S = BM.SERIES || {};
    [['clima', S.clima], ['landsat', S.landsat], ['aire', S.aire]].forEach(([id, s]) => {
      if (!s) return;
      html.push(`<details class="ficha-capa" id="ficha-serie-${id}"><summary>${esc(s.titulo)}<small>serie</small></summary><div class="prosa">
        ${s.descripcion ? `<p>${esc(s.descripcion)}</p>` : ''}
        ${fichaFuente(s.fuentes || s.fuente)}
        ${s.hallazgos ? `<h4>Hallazgos</h4>${lista(s.hallazgos)}` : ''}
        ${s.advertencias ? `<h4>Advertencias</h4>${lista(s.advertencias)}` : ''}
        ${s.limitaciones ? `<h4>Limitaciones</h4>${lista(s.limitaciones)}` : ''}
      </div></details>`);
    });
    $('#fichas').innerHTML = html.join('');
  }

  function metodoGeneral() {
    const cab = BM.cabeceraIndicadores();
    $('#metodo-general').innerHTML = `
      <p><strong>Todo lo que muestra BioMap sale de datos abiertos verificables.</strong> Cada capa se procesó con un script reproducible (carpeta <code>scripts/</code>) a partir de su fuente original, se llevó a una rejilla común de ~28 m y pasó una revisión independiente de plausibilidad, alineación y licencias.</p>
      <p>Las cifras son <strong>estimaciones a partir de sensores remotos, censos y cartografía colaborativa</strong>, no mediciones de campo. Sirven para comparar zonas y priorizar; antes de ejecutar obras deben contrastarse con información oficial (POT, CVC, IDEAM, Secretaría de Planeación) y visitas técnicas.</p>
      ${cab && cab.poblacion ? `<p>Población de referencia de la cabecera: <b>${fmt(cab.poblacion, 0)} habitantes</b> (proyección DANE, repartida por manzana del censo 2018).</p>` : ''}`;
  }

  function resumenCiudad() {
    const cab = BM.cabeceraIndicadores();
    if (!cab) return;
    const t = BM.SERIES && BM.SERIES.clima && BM.SERIES.clima.tendencias && BM.SERIES.clima.tendencias.periodos['1991-2025'];
    const kpis = [
      cab.poblacion_calor_extremo !== undefined && [`${fmt(cab.poblacion_calor_extremo, 0)}`, `personas viven en las superficies más calientes (${fmt(cab.pct_poblacion_calor_extremo, 0)} %)`],
      cab.pct_poblacion_sin_verde_300m !== undefined && [`${fmt(cab.pct_poblacion_sin_verde_300m, 0)} %`, 'de la población vive a más de 300 m de un parque'],
      t && t.tmedia && (() => {
        const r = BM.SERIES.clima.tendencias.rango_entre_reanalisis_tmedia_c_por_decada;
        const r91 = r && r['1991-2025'];
        const a = r91 ? Math.min(r91.era5land, r91.era5) : t.tmedia.ols_por_decada, b = r91 ? Math.max(r91.era5land, r91.era5) : a;
        return [a === b ? `+${fmt(a, 2)} °C` : `+${fmt(a, 1)} a +${fmt(b, 1)} °C`, 'por década sube la temperatura del aire desde 1991 (según reanálisis)'];
      })(),
    ].filter(Boolean);
    const h = (BM.INDICADORES && BM.INDICADORES.hallazgos) || [];
    $('#resumen-ciudad').innerHTML = `<div class="resumen-ciudad">${kpis.map(([v, e]) => `<div class="kpi-c"><b>${v}</b><span>${esc(e)}</span></div>`).join('')}</div>
      ${h.length ? `<details class="plegable mt-2"><summary>Hallazgos clave del análisis (${h.length})</summary><ul class="prosa hallazgos">${h.map((x) => `<li>${esc(x)}</li>`).join('')}</ul></details>` : ''}`;
  }

  BM.alIniciar(async () => {
    resumenCiudad();
    const catalogo = await BM.leerJSONopcional('catalogo.json');
    BM.CATALOGO = catalogo;
    construirTabla();
    construirDescargas(catalogo);
    construirFichas();
    metodoGeneral();
  });
})();
