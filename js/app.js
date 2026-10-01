/* BioMap Cartago — núcleo de la interfaz: mapa, capas, leyenda e inspección puntual.
   Los módulos graficos.js, decision.js, abiertos.js y copiloto.js se enganchan con
   BM.alIniciar(fn), que se ejecuta cuando las capas e indicadores están cargados. */
'use strict';
(function () {
  const BM = window.BM;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const fmt = (v, d = 1) => (v === null || v === undefined || !Number.isFinite(+v) ? '—' : (+v).toLocaleString('es-CO', { minimumFractionDigits: d, maximumFractionDigits: d }));
  const esc = (t) => String(t ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  BM.fmt = fmt; BM.esc = esc; BM.$ = $; BM.$$ = $$;

  const enIniciar = [];
  BM.alIniciar = (fn) => enIniciar.push(fn);

  if (!window.L) {
    $('#cargando').innerHTML = '<span>No se pudo cargar la librería de mapas. Revisa la conexión a internet y recarga.</span>';
    return;
  }

  /* ================= mapa ================= */
  const mapa = L.map('mapa', {
    center: BM.CENTRO, zoom: 14, minZoom: 12, maxZoom: 18,
    maxBounds: BM.LIMITES_NAV, maxBoundsViscosity: 0.9,
  });
  BM.mapa = mapa;
  L.control.scale({ imperial: false, position: 'bottomleft' }).addTo(mapa);
  mapa.attributionControl.setPrefix('<a href="https://leafletjs.com" target="_blank" rel="noopener">Leaflet</a>');

  // Etiquetas de los mapas base por encima de las capas de datos, sin capturar clics
  mapa.createPane('etiquetas').style.zIndex = 460;
  mapa.getPane('etiquetas').style.pointerEvents = 'none';

  const ESRI = 'https://services.arcgisonline.com/ArcGIS/rest/services';
  /* Satelital: se fija la versión de World Imagery del 2026-06-30 (Wayback, imagen vigente desde julio de 2025)
     porque el mosaico vigente de agosto de 2026 tiene nubes y sombras sobre el centro de Cartago. */
  /* Capa de etiquetas transparente. Leaflet retira las teselas del zoom anterior con un temporizador que el
     navegador frena en pestañas en segundo plano; como estas teselas son transparentes, la vieja ampliada
     quedaría visible. Se limpia apenas termina la carga. */
  const capaEtiquetas = (url, opciones) => {
    const capa = L.tileLayer(url, { maxZoom: 19, pane: 'etiquetas', ...opciones });
    capa.on('load', () => { if (typeof capa._pruneTiles === 'function') capa._pruneTiles(); });
    return capa;
  };
  const WAYBACK = 'https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/WMTS/1.0.0/default028mm/MapServer/tile/32246/{z}/{y}/{x}';
  const BASES = {
    calle: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>',
    }),
    satelite: L.layerGroup([
      L.tileLayer(WAYBACK, { maxZoom: 19, maxNativeZoom: 18, attribution: 'Imágenes © Esri, Maxar, Earthstar Geographics (World Imagery, versión 2026-06-30)' }),
      capaEtiquetas(`${ESRI}/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}`, { maxNativeZoom: 18, attribution: 'Etiquetas © Esri' }),
    ]),
  };
  let baseActual = BASES.calle.addTo(mapa);
  BM.baseActual = 'calle';
  $$('[data-base]').forEach((b) => b.addEventListener('click', () => {
    const nueva = BASES[b.dataset.base];
    if (nueva === baseActual) return;
    mapa.removeLayer(baseActual);
    baseActual = nueva.addTo(mapa);
    BM.baseActual = b.dataset.base;
    $$('[data-base]').forEach((o) => o.setAttribute('aria-pressed', String(o === b)));
    $('#mapa').dataset.base = b.dataset.base;
    estilarZonas();
  }));

  mapa.createPane('rasters').style.zIndex = 350;
  mapa.createPane('resalte').style.zIndex = 450;
  mapa.createPane('puntos').style.zIndex = 620;
  new ResizeObserver(() => mapa.invalidateSize({ pan: false })).observe($('#mapa'));

  /* ================= panel y pestañas ================= */
  const tabs = $$('[role="tab"]');
  const alCambiar = [];
  BM.alCambiarPestana = (fn) => alCambiar.push(fn);
  function activarPestana(tab, foco = false) {
    tabs.forEach((t) => {
      const sel = t === tab;
      t.setAttribute('aria-selected', String(sel));
      t.tabIndex = sel ? 0 : -1;
      $('#' + t.getAttribute('aria-controls')).hidden = !sel;
    });
    if (foco) tab.focus();
    $('#panel-cuerpo').scrollTop = 0;
    alCambiar.forEach((fn) => fn(tab.getAttribute('aria-controls')));
  }
  BM.irAPestana = (id) => activarPestana(tabs.find((t) => t.getAttribute('aria-controls') === id));
  tabs.forEach((t, i) => {
    t.addEventListener('click', () => activarPestana(t));
    t.addEventListener('keydown', (e) => {
      const d = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
      if (d) { e.preventDefault(); activarPestana(tabs[(i + d + tabs.length) % tabs.length], true); }
    });
  });
  $$('[data-ir]').forEach((b) => b.addEventListener('click', () => {
    BM.irAPestana(b.dataset.ir);
    if (b.dataset.ancla) setTimeout(() => $('#' + b.dataset.ancla).scrollIntoView({ behavior: 'smooth' }), 60);
  }));
  $('#plegar').addEventListener('click', () => {
    const plegado = $('#app').classList.toggle('plegado');
    $('#plegar').setAttribute('aria-expanded', String(!plegado));
    $('#plegar').title = plegado ? 'Mostrar panel' : 'Ocultar panel';
  });

  /* ================= catálogo de capas ================= */
  // Textos cortos de la interfaz; la ficha completa (fuente, método, limitaciones) sale de datos/capas/<id>.json
  const GRUPOS = [
    { titulo: 'Calor urbano', capas: [
      { id: 'lst', nombre: 'Isla de calor urbana', corto: 'Temperatura de la superficie hacia las 10:20 a. m., mediana 2022–2025 (Landsat).', activa: true, op: 0.7 },
    ] },
    { titulo: 'Vegetación', capas: [
      { id: 'ndvi', nombre: 'Cobertura vegetal (NDVI)', corto: 'Vigor de la vegetación 2024–2025 (Sentinel-2): galería del río, parques y potreros.', op: 0.7 },
      { id: 'arbolado', nombre: 'Arbolado', corto: 'Porcentaje de cada celda cubierto por árboles (ESA WorldCover 2021).', op: 0.75, ocultarBajo: 2 },
    ] },
    { titulo: 'Aire', capas: [
      { id: 'trafico', nombre: 'Gases de combustión: exposición al tráfico', corto: 'Índice 0–100 de cercanía a vías según su jerarquía. Es un indicador de exposición, no una medición de NO₂.', op: 0.8, alfaPorValor: true, ocultarBajo: 3 },
    ] },
    { titulo: 'Agua y riesgo', capas: [
      { id: 'ideam_amenaza', externa: true, nombre: 'Riesgo hidrológico oficial (IDEAM)', corto: 'Amenaza por creciente súbita del río La Vieja y quebradas, periodo de retorno de 50 años. Se consulta en vivo al servicio del IDEAM.', op: 0.7,
        servicio: 'https://visualizador.ideam.gov.co/gisserver/rest/services/Amenaza_Ambiental/MapServer', capasServicio: '0',
        leyenda: [['#ff0000', 'Alta'], ['#ff5500', 'Media'], ['#ffff00', 'Baja']],
        atribucion: 'Amenaza por creciente súbita TR 50 años · <a href="https://visualizador.ideam.gov.co/" target="_blank" rel="noopener">IDEAM</a>' },
      { id: 'ideam_nina', externa: true, nombre: 'Inundaciones históricas (La Niña 1988–2022)', corto: 'Áreas afectadas por inundación en los eventos de La Niña de 1988, 2000, 2011, 2012, 2016 y 2020–2022, según el IDEAM. Servicio en vivo.', op: 0.55,
        servicio: 'https://visualizador.ideam.gov.co/gisserver/rest/services/Amenaza_Ambiental/MapServer', capasServicio: '6,7,8,9,22,23,24,26,27',
        leyenda: [['#df73ff', 'Área inundada en algún evento']],
        atribucion: 'Áreas afectadas por inundación, fenómenos de La Niña · <a href="https://visualizador.ideam.gov.co/" target="_blank" rel="noopener">IDEAM</a>' },
      { id: 'susceptibilidad_inundacion', nombre: 'Susceptibilidad topográfica (HAND)', corto: 'Altura sobre el cauce (Copernicus DEM). Complemento técnico, no amenaza oficial: las clases bajas no descartan inundación.', op: 0.7, clases: true, ocultarClase0: true },
      { id: 'agua_ocurrencia', nombre: 'Agua en superficie 1984–2021', corto: 'Frecuencia con que hubo agua en superficie (JRC Global Surface Water).', op: 0.85, ocultarBajo: 1 },
    ] },
    { titulo: 'Población y servicios', capas: [
      { id: 'poblacion', nombre: 'Población', corto: 'Habitantes por celda de ~28 m, 2026: proyección DANE repartida por manzana del censo 2018.', op: 0.75, ocultarBajo: 0.3 },
      { id: 'distancia_verde', nombre: 'Distancia a espacio verde', corto: 'Metros hasta el parque público de al menos 0,5 ha más cercano (criterio OMS: 300 m).', op: 0.65 },
      { id: 'equipamientos', vector: true, nombre: 'Equipamientos sensibles', corto: 'Colegios, centros de salud, hogares de cuidado y servicios de emergencia (OpenStreetMap).' },
      { id: 'espacio_verde', vector: true, nombre: 'Parques y espacio verde público', corto: 'Polígonos de OpenStreetMap; puede estar incompleto.' },
    ] },
    { titulo: 'Límites', capas: [
      { id: 'zonas', vector: true, nombre: 'Comunas y zonas', corto: 'Comunas 1 a 7 (OpenStreetMap) y centro poblado de Zaragoza.', activa: true, op: 0.85 },
    ] },
    { titulo: 'Más capas', plegado: true, capas: [
      { id: 'construido', nombre: 'Área construida', corto: 'Porcentaje de cada celda construido (ESA WorldCover 2021).', op: 0.7, ocultarBajo: 2 },
      { id: 'altitud', nombre: 'Altitud', corto: 'Modelo digital de superficie Copernicus GLO-30.', op: 0.7 },
      { id: 'hand', nombre: 'Altura sobre el cauce (HAND)', corto: 'Metros por encima del drenaje más cercano. Valores bajos: más susceptible.', op: 0.7 },
    ] },
  ];
  const CAPA = {};
  GRUPOS.forEach((g) => g.capas.forEach((c) => (CAPA[c.id] = c)));
  BM.CAPAS_UI = CAPA;
  const RASTER = Object.values(CAPA).filter((c) => !c.vector && !c.externa).map((c) => c.id);

  /* Capa dinámica de un servicio ArcGIS MapServer (operación export): se pide una imagen
     del área visible en cada movimiento. No se copian ni redistribuyen los datos de origen. */
  const CapaArcGIS = L.Layer.extend({
    initialize(url, capas, opciones) { this._url = url; this._capas = capas; L.setOptions(this, opciones); this._op = opciones.opacity ?? 0.7; },
    onAdd(m) {
      this._map = m;
      this._img = L.imageOverlay('data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==', m.getBounds(), { opacity: this._op, pane: 'rasters', interactive: false }).addTo(m);
      this._img.on('error', () => this.fire('falla'));
      this._img.on('load', () => this.fire('cargada'));
      m.on('moveend', this._pedir, this);
      this._pedir();
    },
    onRemove(m) { m.off('moveend', this._pedir, this); m.removeLayer(this._img); },
    setOpacity(o) { this._op = o; if (this._img) this._img.setOpacity(o); return this; },
    getAttribution() { return this.options.attribution; },
    _pedir() {
      const m = this._map, b = m.getBounds(), t = m.getSize();
      const sw = L.CRS.EPSG3857.project(b.getSouthWest()), ne = L.CRS.EPSG3857.project(b.getNorthEast());
      const url = `${this._url}/export?bbox=${sw.x},${sw.y},${ne.x},${ne.y}&bboxSR=3857&imageSR=3857&size=${t.x},${t.y}&dpi=96&layers=show:${this._capas}&format=png32&transparent=true&f=image`;
      const img = this._img, limites = b;
      const pre = new Image();
      pre.onload = () => { img.setUrl(url); img.setBounds(limites); };
      pre.onerror = () => this.fire('falla');
      pre.src = url;
    },
  });

  function prepararExterna(c) {
    c.capa = new CapaArcGIS(c.servicio, c.capasServicio, { opacity: c.op, attribution: c.atribucion });
    c.capa.on('falla', () => {
      if (c.avisado) return;
      c.avisado = true;
      $('.capa-desc', c.el).textContent = 'El servicio del IDEAM no respondió. Intenta más tarde.';
    });
    $('.capa-muestra', c.el).style.background = `linear-gradient(90deg, ${c.leyenda.map((l) => l[0]).join(', ')})`;
    $('input[type=checkbox]', c.el).disabled = false;
  }
  BM.DATOS = {}; // id → capa decodificada

  function estiloDe(c, meta) {
    if (c.clases) {
      return { clases: (meta.clases || []).map((k) => ({ ...k, color: c.ocultarClase0 && k.valor === 0 ? null : k.color })) };
    }
    return { paleta: meta.paleta, rango: meta.rango_visual, ocultarBajo: c.ocultarBajo, alfaPorValor: c.alfaPorValor };
  }

  function fichaHTML(meta) {
    if (!meta) return '';
    const f = meta.fuente || {};
    const lim = (meta.limitaciones || []).slice(0, 4).map((l) => `<li>${esc(l)}</li>`).join('');
    return `<dl class="ficha">
      ${meta.descripcion ? `<p>${esc(meta.descripcion)}</p>` : ''}
      <dt>Fuente</dt><dd>${f.url ? `<a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.nombre || f.url)}</a>` : esc(f.nombre)}</dd>
      ${meta.periodo ? `<dt>Periodo</dt><dd>${esc(typeof meta.periodo === 'string' ? meta.periodo : JSON.stringify(meta.periodo))}</dd>` : ''}
      ${meta.resolucion_original_m ? `<dt>Resolución de origen</dt><dd>${esc(meta.resolucion_original_m)} m (publicada a ~28 m)</dd>` : ''}
      ${f.licencia ? `<dt>Licencia</dt><dd>${esc(f.licencia)}</dd>` : ''}
      ${lim ? `<dt>Limitaciones</dt><dd><ul>${lim}</ul></dd>` : ''}
      <dd class="ficha-acciones"><button type="button" class="enlace" data-ir-capa="${esc(meta.nombre)}">Método completo y descarga</button></dd>
    </dl>`;
  }

  function construirCapas() {
    const cont = $('#capas');
    GRUPOS.forEach((g) => {
      const sec = document.createElement(g.plegado ? 'details' : 'section');
      sec.className = 'grupo-capas';
      sec.innerHTML = g.plegado ? `<summary class="rotulo-grupo">${esc(g.titulo)}</summary>` : `<h3 class="rotulo-grupo">${esc(g.titulo)}</h3>`;
      g.capas.forEach((c) => sec.appendChild(tarjetaCapa(c)));
      cont.appendChild(sec);
    });
    cont.addEventListener('click', (e) => {
      const b = e.target.closest('[data-ir-capa]');
      if (!b) return;
      BM.irAPestana('tab-datos');
      setTimeout(() => { const el = $(`#ficha-${b.dataset.irCapa}`); if (el) { el.open = true; el.scrollIntoView({ behavior: 'smooth' }); } }, 80);
    });
  }

  function tarjetaCapa(c) {
    const el = document.createElement('div');
    el.className = 'capa';
    el.dataset.capa = c.id;
    const op = Math.round((c.op ?? 0.8) * 100);
    el.innerHTML = `
      <div class="capa-cab">
        <span class="capa-muestra" aria-hidden="true"></span>
        <label for="capa-${c.id}"><span class="capa-nombre">${esc(c.nombre)}</span><span class="capa-desc block">${esc(c.corto)}</span></label>
        <span class="interruptor"><input type="checkbox" id="capa-${c.id}" role="switch" disabled><i></i></span>
      </div>
      <div class="capa-opacidad">
        <span>Opacidad</span>
        <input type="range" min="0" max="100" value="${op}" aria-label="Opacidad de ${esc(c.nombre)}">
        <output>${op} %</output>
      </div>
      ${c.vector ? '' : c.externa ? `<details class="capa-info"><summary>Fuente y limitaciones</summary><div class="capa-ficha"><dl class="ficha">
        <dt>Fuente</dt><dd><a href="${esc(c.servicio)}" target="_blank" rel="noopener">IDEAM, servicio Amenaza_Ambiental</a> (consulta en vivo; BioMap no copia estos datos)</dd>
        <dt>Uso</dt><dd>Información pública del IDEAM, con atribución. Es la referencia oficial disponible en datos abiertos; el POT de Cartago y la CVC pueden tener estudios de mayor detalle.</dd>
        ${c.id === 'ideam_amenaza' ? '<dt>Limitaciones</dt><dd><ul><li>Cubre la creciente súbita del río La Vieja y quebradas cercanas; no la inundación lenta del río Cauca.</li><li>Escala 1:2.000 para 8 cabeceras municipales del país.</li></ul></dd>' : '<dt>Limitaciones</dt><dd><ul><li>Manchas cartografiadas de eventos pasados; no predicen el próximo evento.</li><li>Varían en escala y método entre años.</li></ul></dd>'}
      </dl></div></details>` : '<details class="capa-info"><summary>Fuente y limitaciones</summary><div class="capa-ficha">Cargando…</div></details>'}`;
    const chk = $('input[type=checkbox]', el), rng = $('input[type=range]', el), out = $('output', el);
    c.el = el;
    c.op = op / 100;
    c.aplicarOpacidad = () => {
      c.op = rng.value / 100;
      out.textContent = rng.value + ' %';
      if (c.capa) (c.opacidad ? c.opacidad(c.op) : c.capa.setOpacity(c.op));
    };
    chk.addEventListener('change', () => activarCapa(c, chk.checked));
    rng.addEventListener('input', c.aplicarOpacidad);
    return el;
  }

  function activarCapa(c, on) {
    c.activa = on;
    c.el.classList.toggle('activa', on);
    $('input[type=checkbox]', c.el).checked = on;
    if (!c.capa) return;
    if (on) { c.capa.addTo(mapa); c.aplicarOpacidad(); } else mapa.removeLayer(c.capa);
    if (c.id === 'zonas' && on) c.capa.bringToBack();
    pintarLeyenda();
  }
  BM.activarCapa = (id, on = true) => CAPA[id] && activarCapa(CAPA[id], on);

  /* Atribución que muestra Leaflet mientras la capa está activa (exigida por las licencias de origen). */
  const ATRIBUCION = {
    lst: 'Temperatura: Landsat, cortesía del USGS',
    ndvi: 'NDVI: Copernicus Sentinel-2 (ESA)',
    ndvi_seco: 'NDVI: Copernicus Sentinel-2 (ESA)',
    arbolado: 'Arbolado: ESA WorldCover 2021 (CC BY 4.0)',
    construido: 'Construido: ESA WorldCover 2021 (CC BY 4.0)',
    agua: 'Agua: ESA WorldCover 2021 (CC BY 4.0)',
    poblacion: 'Población: DANE (proyección 2026, CNPV 2018)',
    susceptibilidad_inundacion: 'HAND: Copernicus DEM GLO-30 (ESA/Airbus), Meta/WRI CHM (CC BY 4.0), © OpenStreetMap',
    hand: 'HAND: Copernicus DEM GLO-30 (ESA/Airbus), Meta/WRI CHM (CC BY 4.0), © OpenStreetMap',
    altitud: 'Altitud: Copernicus DEM GLO-30 (ESA/Airbus)',
    agua_ocurrencia: 'Agua histórica: JRC Global Surface Water (EC JRC/Google)',
    trafico: 'Tráfico: derivado de © OpenStreetMap (ODbL)',
    distancia_verde: 'Verde: derivado de © OpenStreetMap (ODbL)',
  };

  function prepararRaster(c, datos) {
    const est = estiloDe(c, datos.meta);
    c.meta = datos.meta;
    c.estilo = est;
    const f = datos.meta.fuente || {};
    c.capa = L.imageOverlay(BM.colorearCapa(datos, est), BM.limitesRejilla(datos.meta), {
      opacity: c.op, pane: 'rasters', interactive: false, className: 'bm-raster',
      attribution: esc(ATRIBUCION[c.id] || f.nombre || ''),
    });
    $('.capa-muestra', c.el).style.background = est.clases
      ? `linear-gradient(90deg, ${est.clases.filter((k) => k.color).map((k) => k.color).join(', ')})`
      : `linear-gradient(90deg, ${est.paleta.join(', ')})`;
    $('.capa-ficha', c.el).innerHTML = fichaHTML(datos.meta);
    $('input[type=checkbox]', c.el).disabled = false;
    if (c.activa) activarCapa(c, true);
  }

  function fallaCapa(c, err) {
    console.warn(`Capa ${c.id} no disponible:`, err.message);
    c.el.classList.add('no-disponible');
    $('.capa-desc', c.el).textContent = 'Capa no disponible en esta publicación.';
    const f = $('.capa-ficha', c.el); if (f) f.textContent = err.message;
  }

  /* ---------- capas vectoriales ---------- */
  const ICONOS_EQ = { educacion: { color: '#1d4ed8', letra: 'E' }, salud: { color: '#dc2626', letra: 'S' }, cuidado: { color: '#7c3aed', letra: 'C' }, emergencia_gobierno: { color: '#0f766e', letra: 'G' } };
  BM.ICONOS_EQ = ICONOS_EQ;

  // Borde de las comunas legible sobre cada mapa base: verde oscuro en el callejero, blanco sobre la imagen satelital
  const colorBordeZonas = () => (BM.baseActual === 'calle' ? '#064e3b' : '#f8fafc');
  function estilarZonas() {
    const c = CAPA.zonas;
    if (c && c.capa) c.capa.setStyle({ color: colorBordeZonas(), weight: BM.baseActual === 'calle' ? 1.6 : 2 });
  }

  function prepararZonas() {
    const c = CAPA.zonas;
    const colorZona = (z) => {
      const lst = BM.DATOS.lst ? z.props.lst_media : null;
      return lst && BM.DATOS.lst ? BM.colorPaleta(BM.DATOS.lst.meta.paleta, BM.DATOS.lst.meta.rango_visual, lst) : '#10b981';
    };
    const capas = BM.ZONAS.map((z) => {
      const pol = L.polygon(z.anillos, { color: colorBordeZonas(), weight: 1.6, opacity: 0.9, fillColor: colorZona(z), fillOpacity: 0.08 });
      const p = z.props || {};
      const det = [
        p.lst_media !== undefined ? `LST ${fmt(p.lst_media)} °C` : '',
        p.poblacion !== undefined ? `${fmt(p.poblacion, 0)} hab.` : '',
        p.arbolado_pct !== undefined ? `arbolado ${fmt(p.arbolado_pct, 0)} %` : '',
      ].filter(Boolean).join(' · ');
      pol.bindTooltip(`<b>${esc(z.nombre)}</b>${det ? '<br>' + det : ''}`, { sticky: true, className: 'tip-zona' });
      pol.on('mouseover', () => pol.setStyle({ weight: 3 }));
      pol.on('mouseout', () => pol.setStyle({ weight: BM.baseActual === 'calle' ? 1.6 : 2 }));
      return pol;
    });
    c.capa = L.featureGroup(capas);
    c.capa.getAttribution = () => 'Comunas: © OpenStreetMap (ODbL)';
    c.opacidad = (o) => c.capa.setStyle({ opacity: o, fillOpacity: 0.1 * o });
    $('.capa-muestra', c.el).style.background = 'linear-gradient(135deg,#d1fae5,#064e3b)';
    estilarZonas();
    $('input[type=checkbox]', c.el).disabled = false;
    if (c.activa) activarCapa(c, true);
  }

  async function prepararVectores() {
    const [eq, ev] = await Promise.all([
      BM.leerJSONopcional('vectores/equipamientos_exposicion.geojson').then((g) => g || BM.leerJSONopcional('vectores/equipamientos.geojson')),
      BM.leerJSONopcional('vectores/espacio_verde.geojson'),
    ]);
    BM.EQUIPAMIENTOS = eq;
    if (eq) {
      const c = CAPA.equipamientos;
      c.capa = L.geoJSON(eq, {
        pane: 'puntos', attribution: 'Equipamientos: © OpenStreetMap (ODbL)',
        pointToLayer: (f, ll) => {
          const ic = ICONOS_EQ[f.properties.categoria] || { color: '#334155', letra: '•' };
          return L.marker(ll, { pane: 'puntos', icon: L.divIcon({ className: '', html: `<span class="pin-eq" style="--c:${ic.color}">${ic.letra}</span>`, iconSize: [20, 20], iconAnchor: [10, 10] }) });
        },
        onEachFeature: (f, capa) => {
          const p = f.properties;
          capa.bindTooltip(`<b>${esc(p.nombre || p.subtipo_es || 'Sin nombre en OSM')}</b><br>${esc(p.subtipo_es || p.categoria_es || '')}`, { className: 'tip-zona' });
          capa.on('click', (e) => { L.DomEvent.stopPropagation(e); inspeccionar(e.latlng.lat, e.latlng.lng, p.nombre || p.subtipo_es, p); });
        },
      });
      c.opacidad = (o) => c.capa.eachLayer((m) => m.setOpacity(o));
      $('.capa-muestra', c.el).style.background = 'radial-gradient(circle at 35% 50%, #1d4ed8 0 22%, transparent 24%), radial-gradient(circle at 70% 50%, #dc2626 0 22%, transparent 24%), #f1f5f9';
      $('input[type=checkbox]', c.el).disabled = false;
    } else fallaCapa(CAPA.equipamientos, new Error('sin datos'));
    if (ev) {
      const c = CAPA.espacio_verde;
      c.capa = L.geoJSON(ev, {
        attribution: 'Parques: © OpenStreetMap (ODbL)',
        filter: (f) => String(f.properties.publico) !== 'false',
        style: { color: '#166534', weight: 1.2, fillColor: '#22c55e', fillOpacity: 0.35 },
        onEachFeature: (f, capa) => capa.bindTooltip(`<b>${esc(f.properties.nombre || f.properties.tipo_es || 'Espacio verde')}</b><br>${fmt(f.properties.area_m2 / 10000, 2)} ha`, { sticky: true, className: 'tip-zona' }),
      });
      c.opacidad = (o) => c.capa.setStyle({ opacity: o, fillOpacity: 0.4 * o });
      $('.capa-muestra', c.el).style.background = '#22c55e';
      $('input[type=checkbox]', c.el).disabled = false;
    } else fallaCapa(CAPA.espacio_verde, new Error('sin datos'));
  }

  /* ================= leyenda ================= */
  function pintarLeyenda() {
    const partes = [];
    Object.values(CAPA).forEach((c) => {
      if (c.activa && c.externa) {
        partes.push(`<div><h4>${esc(c.nombre)}</h4><div class="clases">${c.leyenda.map(([col, et]) => `<span><i style="background:${col}"></i>${esc(et)}</span>`).join('')}</div></div>`);
        return;
      }
      if (!c.activa || !c.meta) return;
      const m = c.meta;
      if (c.estilo.clases) {
        const filas = (m.clases || []).filter((k) => !(c.ocultarClase0 && k.valor === 0))
          .map((k) => `<span><i style="background:${k.color}"></i>${esc(k.etiqueta_corta || k.etiqueta.split('(')[0].trim())}</span>`).join('');
        partes.push(`<div><h4>${esc(c.nombre)}</h4><div class="clases">${filas}</div></div>`);
      } else {
        const [a, b] = m.rango_visual, u = m.unidad && m.unidad.length < 14 ? ' ' + m.unidad : '';
        const d = Math.abs(b - a) < 2 ? 2 : 0;
        partes.push(`<div><h4>${esc(c.nombre)}</h4><div class="rampa" style="background:linear-gradient(90deg, ${m.paleta.join(', ')})"></div>
          <div class="extremos"><span>≤ ${fmt(a, d)}${esc(u)}</span><span>≥ ${fmt(b, d)}${esc(u)}</span></div></div>`);
      }
    });
    if (CAPA.equipamientos.activa) {
      partes.push(`<div><h4>Equipamientos</h4><div class="clases">${Object.entries(ICONOS_EQ).map(([k, v]) =>
        `<span><span class="pin-eq mini" style="--c:${v.color}">${v.letra}</span>${{ educacion: 'Educación', salud: 'Salud', cuidado: 'Cuidado', emergencia_gobierno: 'Emergencia y gobierno' }[k]}</span>`).join('')}</div></div>`);
    }
    if (CAPA.espacio_verde.activa) partes.push('<div><h4>Espacio verde público</h4><div class="clases"><span><i style="background:#22c55e"></i>Parques, plazas verdes y zonas de juego</span></div></div>');
    $('#leyenda').innerHTML = partes.join('');
  }
  BM.pintarLeyenda = pintarLeyenda;

  /* ================= hitos ================= */
  function construirHitos() {
    BM.HITOS.forEach((h) => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'chip'; b.textContent = h.nombre;
      b.addEventListener('click', () => { mapa.flyTo(h.coord, h.zoom, { duration: 0.9 }); inspeccionar(h.coord[0], h.coord[1], h.nombre); });
      $('#hitos').appendChild(b);
    });
  }

  /* ================= inspección puntual ================= */
  let marcador = null;
  BM.ultimoPunto = null;

  const ref = (id) => (BM.DATOS[id] && BM.DATOS[id].meta.estadisticas && BM.DATOS[id].meta.estadisticas.cabecera_urbana) || null;
  const val = (id, lat, lon) => (BM.DATOS[id] ? BM.valorEn(BM.DATOS[id], lat, lon) : null);
  const prom = (id, lat, lon, r) => (BM.DATOS[id] ? BM.promedioEn(BM.DATOS[id], lat, lon, r) : null);
  const AREA_CELDA_HA = 0.0765; // 0,00025° × 0,00025° a 4,7° N

  /** Lectura completa de un punto, con comparación contra la cabecera. */
  BM.leerPunto = function (lat, lon) {
    const p = {
      lat, lon, zona: BM.zonaEn(lat, lon),
      lst: val('lst', lat, lon), ndvi: val('ndvi', lat, lon),
      arbolado100: prom('arbolado', lat, lon, 100), construido100: prom('construido', lat, lon, 100),
      pobDensidad: (() => { const m = prom('poblacion', lat, lon, 150); return m === null ? null : m / AREA_CELDA_HA; })(),
      susceptibilidad: val('susceptibilidad_inundacion', lat, lon), hand: val('hand', lat, lon),
      trafico: val('trafico', lat, lon), distVerde: val('distancia_verde', lat, lon),
      rad: BM.radiacion(lat, lon),
    };
    return p;
  };

  function nivelLST(v) {
    const r = ref('lst');
    if (v === null || !r) return { nivel: 'neutro', texto: 'Sin dato' };
    if (v >= r.p90) return { nivel: 'critico', texto: `Entre el 10 % más caliente de la cabecera (≥ ${fmt(r.p90)} °C)` };
    if (v >= r.p50) return { nivel: 'alto', texto: `Más caliente que la mediana urbana (${fmt(r.p50)} °C)` };
    if (v >= r.p10) return { nivel: 'medio', texto: `Más fresco que la mediana urbana (${fmt(r.p50)} °C)` };
    return { nivel: 'bueno', texto: 'Entre las superficies más frescas de la cabecera' };
  }
  function nivelNDVI(v) {
    if (v === null) return { nivel: 'neutro', texto: 'Sin dato' };
    if (v < 0.05) return { nivel: 'neutro', texto: 'Agua o superficie sellada' };
    if (v < 0.25) return { nivel: 'alto', texto: 'Vegetación escasa' };
    if (v < 0.5) return { nivel: 'medio', texto: 'Vegetación dispersa' };
    return { nivel: 'bueno', texto: 'Vegetación densa' };
  }
  function nivelInund(c) {
    const k = c === null ? null : Math.round(c);
    const meta = BM.DATOS.susceptibilidad_inundacion && BM.DATOS.susceptibilidad_inundacion.meta.clases;
    const et = meta && meta.find((x) => x.valor === k);
    // la etiqueta sale de los metadatos de la capa; las clases baja y «HAND > 15 m» no descartan amenaza, por eso no van en verde
    const corto = et ? (et.etiqueta_corta || et.etiqueta.split('(')[0].trim()) : 'Sin dato';
    return { nivel: { 3: 'critico', 2: 'alto' }[k] || 'neutro', texto: corto, detalle: et ? et.etiqueta : '' };
  }
  function nivelTrafico(v) {
    if (v === null) return { nivel: 'neutro', texto: 'Sin dato' };
    if (v >= 60) return { nivel: 'critico', texto: 'Junto a vías de alto flujo' };
    if (v >= 30) return { nivel: 'alto', texto: 'Exposición moderada' };
    if (v >= 10) return { nivel: 'medio', texto: 'Exposición baja' };
    return { nivel: 'bueno', texto: 'Lejos de vías principales' };
  }
  function nivelVerde(v) {
    if (v === null) return { nivel: 'neutro', texto: 'Sin dato' };
    if (v <= 300) return { nivel: 'bueno', texto: 'Cumple el criterio OMS de 300 m' };
    if (v <= 600) return { nivel: 'medio', texto: 'Fuera del criterio OMS de 300 m' };
    return { nivel: 'alto', texto: 'Lejos de cualquier parque de 0,5 ha' };
  }
  function nivelRad(v) {
    if (v < 1) return { nivel: 'neutro', texto: 'Sol bajo el horizonte' };
    if (v > 800) return { nivel: 'alto', texto: 'Radiación intensa (cielo despejado)' };
    if (v > 400) return { nivel: 'medio', texto: 'Radiación moderada (cielo despejado)' };
    return { nivel: 'bueno', texto: 'Radiación baja' };
  }

  const tarjeta = (et, valor, unidad, n) => `<div class="metrica" data-nivel="${n.nivel}"><dt>${et}</dt>
    <dd><div class="valor">${valor}<small>${unidad}</small></div><div class="estado">${esc(n.texto)}</div></dd></div>`;

  /* Consulta en vivo al IDEAM: amenaza por creciente súbita TR 50 y áreas inundadas en La Niña en el punto. */
  const IDEAM = 'https://visualizador.ideam.gov.co/gisserver/rest/services/Amenaza_Ambiental/MapServer';
  BM.consultarIDEAM = async function (lat, lon) {
    const ext = [lon - 0.01, lat - 0.01, lon + 0.01, lat + 0.01].join(',');
    const u = `${IDEAM}/identify?geometry=${lon},${lat}&geometryType=esriGeometryPoint&sr=4326&layers=all:0,6,7,8,9,22,23,24,26,27&tolerance=1&mapExtent=${ext}&imageDisplay=400,400,96&returnGeometry=false&f=json`;
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 12000);
    try {
      const r = await fetch(u, { signal: ctrl.signal });
      const j = await r.json();
      const res = j.results || [];
      const am = res.find((x) => x.layerId === 0);
      const nina = Array.from(new Set(res.filter((x) => x.layerId !== 0).map((x) => ((x.layerName || '').match(/(19|20)\d\d(\s*-\s*20\d\d)?/) || [''])[0].replace(/\s/g, '')))).filter(Boolean).sort();
      return { ok: true, amenaza: am ? String(am.attributes.Amenaza || am.attributes.AME || am.attributes.ame || '').toUpperCase() : null, nina };
    } catch (e) {
      return { ok: false };
    } finally { clearTimeout(t); }
  };

  function textoIDEAM(r) {
    if (!r.ok) return { nivel: 'neutro', valor: 'Sin conexión', texto: 'No se pudo consultar el IDEAM' };
    const partes = [];
    if (r.amenaza) partes.push(`Amenaza ${r.amenaza.toLowerCase()} por creciente súbita (TR 50)`);
    if (r.nina.length) partes.push(`Inundado en La Niña ${r.nina.join(', ')}`);
    if (!partes.length) return { nivel: 'bueno', valor: 'Sin registro', texto: 'Fuera de las manchas oficiales del IDEAM (no descarta otras amenazas)' };
    const nivel = r.amenaza === 'ALTA' ? 'critico' : r.amenaza === 'MEDIA' || r.nina.length ? 'alto' : 'medio';
    return { nivel, valor: r.amenaza ? r.amenaza.charAt(0) + r.amenaza.slice(1).toLowerCase() : 'Registro histórico', texto: partes.join(' · ') };
  }

  let consultaActual = 0;
  function inspeccionar(lat, lon, titulo, equipamiento) {
    const p = BM.leerPunto(lat, lon);
    BM.ultimoPunto = p;
    const zona = p.zona ? p.zona.nombre : 'Fuera de las zonas urbanas';
    const inund = nivelInund(p.susceptibilidad);
    const hora = new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', timeZone: 'America/Bogota' });
    $('#inspeccion').className = 'tarjeta';
    $('#inspeccion').innerHTML = `
      <div class="lectura-cab">
        <div><b>${esc(titulo || zona)}</b><small>${fmt(lat, 5)}, ${fmt(lon, 5)}</small></div>
        <span class="insignia">${esc(titulo ? zona : 'Punto')}</span>
      </div>
      <dl class="metricas">
        ${tarjeta('Temp. superficial', fmt(p.lst), '°C', nivelLST(p.lst))}
        ${tarjeta('Vegetación', fmt(p.ndvi, 2), 'NDVI', nivelNDVI(p.ndvi))}
        <div class="metrica" data-nivel="neutro" id="tarjeta-ideam"><dt>Riesgo hidrológico (IDEAM)</dt><dd><div class="valor" style="font-size:1rem">Consultando…</div><div class="estado">Susceptibilidad topográfica: ${esc(inund.texto.toLowerCase())}${p.hand !== null ? `, ${fmt(p.hand)} m sobre el cauce` : ''}</div></dd></div>
        ${tarjeta('Tráfico', fmt(p.trafico, 0), '/100', nivelTrafico(p.trafico))}
        ${tarjeta('Parque más cercano', p.distVerde === null ? '—' : fmt(p.distVerde, 0), 'm', nivelVerde(p.distVerde))}
        ${tarjeta('Radiación solar', fmt(p.rad.actual, 0), 'W/m²', nivelRad(p.rad.actual))}
      </dl>
      <div class="lectura-pie">
        <p>En un radio de 100 m: <b>${fmt(p.arbolado100, 0)} %</b> de arbolado y <b>${fmt(p.construido100, 0)} %</b> de área construida${p.pobDensidad !== null ? `; densidad cercana de <b>${fmt(p.pobDensidad, 0)} hab/ha</b>` : ''}.</p>
        <p>Radiación en cielo despejado a las ${hora}: máximo del día ${fmt(p.rad.max, 0)} W/m², ${fmt(p.rad.kwhDia, 1)} kWh/m² en el día.</p>
        ${equipamiento ? `<p class="nota">Equipamiento de OpenStreetMap: ${esc(equipamiento.subtipo_es || equipamiento.subtipo || '')}${equipamiento.osm_url ? ` · <a href="${esc(equipamiento.osm_url)}" target="_blank" rel="noopener">ver en OSM</a>` : ''}</p>` : ''}
        <p class="nota">La temperatura superficial es la del suelo y los techos al paso del satélite, no la del aire.</p>
      </div>`;
    $('#limpiar-punto').hidden = false;
    const id = ++consultaActual;
    BM.consultarIDEAM(lat, lon).then((r) => {
      if (id !== consultaActual) return;
      p.ideam = r;
      const t = textoIDEAM(r), el = $('#tarjeta-ideam');
      if (!el) return;
      el.dataset.nivel = t.nivel;
      $('.valor', el).textContent = t.valor;
      $('.estado', el).textContent = `${t.texto}. Susceptibilidad topográfica: ${inund.texto.toLowerCase()}${p.hand !== null ? `, ${fmt(p.hand)} m sobre el cauce` : ''}.`;
    });
    const popup = `<div class="popup-lectura"><b>${esc(titulo || zona)}</b><table>
      <tr><td>Temp. superficial</td><td>${fmt(p.lst)} °C</td></tr>
      <tr><td>NDVI</td><td>${fmt(p.ndvi, 2)}</td></tr>
      <tr><td>Arbolado (100 m)</td><td>${fmt(p.arbolado100, 0)} %</td></tr>
      <tr><td>Susceptibilidad topográfica</td><td>${esc(inund.texto)}</td></tr></table></div>`;
    if (!marcador) {
      marcador = L.marker([lat, lon], {
        icon: L.divIcon({ className: '', html: '<div class="marcador-punto"></div>', iconSize: [18, 18], iconAnchor: [9, 9], popupAnchor: [0, -10] }),
        keyboard: false, pane: 'puntos',
      }).addTo(mapa);
    } else marcador.setLatLng([lat, lon]);
    marcador.bindPopup(popup, { autoPan: true }).openPopup();
  }
  BM.inspeccionar = inspeccionar;

  mapa.on('click', (e) => inspeccionar(e.latlng.lat, e.latlng.lng));
  $('#limpiar-punto').addEventListener('click', () => {
    if (marcador) { mapa.removeLayer(marcador); marcador = null; }
    BM.ultimoPunto = null;
    $('#limpiar-punto').hidden = true;
    $('#inspeccion').className = 'tarjeta vacia';
    $('#inspeccion').innerHTML = '<p><strong>Haz clic en cualquier punto del mapa</strong> para leer su temperatura superficial, vegetación, riesgo hidrológico, tráfico y acceso a parques.</p>';
  });

  // lectura bajo el cursor
  const cursor = $('#cursor');
  let pendiente = null;
  mapa.on('mousemove', (e) => {
    if (pendiente) return;
    pendiente = requestAnimationFrame(() => {
      pendiente = null;
      const { lat, lng } = e.latlng;
      const lst = val('lst', lat, lng), nd = val('ndvi', lat, lng);
      cursor.textContent = `${fmt(lat, 4)}, ${fmt(lng, 4)}${lst !== null ? ` · LST ${fmt(lst)} °C` : ''}${nd !== null ? ` · NDVI ${fmt(nd, 2)}` : ''}`;
      cursor.classList.add('visible');
    });
  });
  mapa.on('mouseout', () => cursor.classList.remove('visible'));

  /* ================= arranque ================= */
  construirCapas();
  construirHitos();
  setTimeout(iniciar, 30);

  async function iniciar() {
    const avance = $('#cargando span');
    // indicadores y zonas primero: colorean las comunas y alimentan los demás módulos
    const [ind, zonas] = await Promise.all([BM.leerJSONopcional('indicadores.json'), BM.leerJSONopcional('vectores/zonas.geojson')]);
    BM.INDICADORES = ind;
    if (zonas) BM.definirZonas(zonas);

    let listas = 0;
    await Promise.all(RASTER.map((id) => BM.cargarCapa(id)
      .then((d) => { BM.DATOS[id] = d; prepararRaster(CAPA[id], d); })
      .catch((e) => fallaCapa(CAPA[id], e))
      .finally(() => { listas++; if (avance) avance.textContent = `Cargando capas ${listas}/${RASTER.length}…`; })));
    prepararZonas();
    Object.values(CAPA).filter((c) => c.externa).forEach(prepararExterna);
    await prepararVectores().catch((e) => console.warn(e));
    pintarLeyenda();
    $('#cargando').classList.add('fuera');
    setTimeout(() => $('#cargando') && $('#cargando').remove(), 400);
    for (const fn of enIniciar) {
      try { await fn(); } catch (e) { console.error(e); }
    }
  }
})();
