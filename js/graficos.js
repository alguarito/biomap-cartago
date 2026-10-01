/* BioMap Cartago — tendencias: clima (ERA5-Land, CHIRPS), satélite (Landsat) y aire (CAMS).
   Cada cifra y cada frase de lectura sale de datos/series/*.json; aquí solo se presentan. */
'use strict';
(function () {
  const BM = window.BM;
  const { $, fmt, esc } = BM;
  const signo = (v, d = 2) => (v === null || v === undefined ? '—' : (v > 0 ? '+' : v < 0 ? '−' : '') + fmt(Math.abs(v), d));
  const media = (a) => { const x = a.filter((v) => Number.isFinite(v)); return x.length ? x.reduce((s, v) => s + v, 0) / x.length : null; };

  let S = {}; // series cargadas
  let grafico = null;

  const ejes = (unidad, extra = {}) => ({
    x: { grid: { display: false }, ticks: { maxTicksLimit: 8, autoSkip: true } },
    y: { grid: { color: '#eef2f7' }, title: { display: !!unidad, text: unidad }, ...extra },
  });

  /* ---------- definiciones ---------- */
  const SERIES = [
    { id: 'temp_aire', grupo: 'Clima del aire (reanálisis, 1950–2025)', nombre: 'Temperatura del aire: anomalía anual', req: 'clima', construir: tempAire },
    { id: 'dias_calidos', grupo: 'Clima del aire (reanálisis, 1950–2025)', nombre: 'Días muy cálidos por año', req: 'clima', construir: diasCalidos },
    { id: 'lluvia', grupo: 'Clima del aire (reanálisis, 1950–2025)', nombre: 'Lluvia anual (CHIRPS, 1981–2025)', req: 'clima', construir: lluvia },
    { id: 'lst', grupo: 'Satélite (Landsat, 2000–2025)', nombre: 'Temperatura superficial urbana y rural', req: 'landsat', construir: lstLandsat },
    { id: 'isla', grupo: 'Satélite (Landsat, 2000–2025)', nombre: 'Intensidad de la isla de calor', req: 'landsat', construir: islaCalor },
    { id: 'ndvi', grupo: 'Satélite (Landsat, 2000–2025)', nombre: 'Vegetación urbana (NDVI)', req: 'landsat', construir: ndviLandsat },
    { id: 'lst_zona', grupo: 'Satélite (Landsat, 2000–2025)', nombre: 'Temperatura superficial por zona', req: 'zonas', zona: true, construir: lstZona },
    { id: 'no2', grupo: 'Calidad del aire regional (CAMS, 2022–2026)', nombre: 'Dióxido de nitrógeno (NO₂) mensual', req: 'aire', construir: (z) => aireMensual('no2', 'NO₂', 10, z) },
    { id: 'pm25', grupo: 'Calidad del aire regional (CAMS, 2022–2026)', nombre: 'Material particulado PM2,5 mensual', req: 'aire', construir: (z) => aireMensual('pm2_5', 'PM2,5', 5, z) },
  ];

  /* ---------- clima ---------- */
  function anualesCompletos() {
    const a = S.clima.anual;
    return a.anio.map((y, i) => ({ y, i })).filter(({ i }) => !a.parcial[i]);
  }
  function tend(periodo, variable) {
    return S.clima.tendencias && S.clima.tendencias.periodos && S.clima.tendencias.periodos[periodo] && S.clima.tendencias.periodos[periodo][variable];
  }
  function fuenteClima(extra) {
    return `Fuente: ERA5-Land (Copernicus/ECMWF) vía Open-Meteo, celda de ~9 km que cubre Cartago. ${extra} <a href="#" data-ficha-serie="clima">Método y validación con el IDEAM</a>.`;
  }

  function tempAire() {
    const a = S.clima.anual, filas = anualesCompletos();
    const ys = filas.map(({ y }) => y), vs = filas.map(({ i }) => a.anomalia_tmedia_vs_1991_2020[i]);
    const t91 = tend('1991-2025', 'tmedia'), t50 = tend('1950-2025', 'tmedia');
    const rango = S.clima.tendencias && S.clima.tendencias.rango_entre_reanalisis_tmedia_c_por_decada;
    const r91 = rango && rango['1991-2025'];
    let max = null;
    filas.forEach(({ y, i }) => { if (max === null || a.tmedia[i] > a.tmedia[max.i]) max = { y, i }; });
    return {
      tipo: 'bar', labels: ys, unidad: '°C respecto a 1991–2020',
      datasets: [{ label: 'Anomalía', data: vs, backgroundColor: vs.map((v) => (v >= 0 ? '#dc2626cc' : '#2563ebcc')), borderWidth: 0 }],
      clave: t91 ? `La temperatura media del aire sube entre <b>${signo(r91 ? Math.min(r91.era5land, r91.era5) : t91.ols_por_decada)} y ${signo(r91 ? Math.max(r91.era5land, r91.era5) : t91.ols_por_decada)} °C por década</b> desde 1991, según la versión del reanálisis (ERA5-Land: ${signo(t91.ols_por_decada)}, IC 95 % ajustado por autocorrelación ${signo((t91.ols_ic95_ajustado_ar1 || t91.ols_ic95)[0])} a ${signo((t91.ols_ic95_ajustado_ar1 || t91.ols_ic95)[1])}). Desde 1950, ${signo(t50 && t50.ols_por_decada)} °C por década en ERA5-Land. El año más cálido fue <b>${max.y}</b>.` : '',
      nota: fuenteClima('Barras: anomalía de ERA5-Land frente a 1991–2020. Se muestran anomalías porque el reanálisis subestima los valores absolutos de las estaciones del IDEAM. Las dos versiones del reanálisis coinciden en que hay calentamiento, pero no en su ritmo: úsese el rango.'),
      tooltip: (v) => `${signo(v)} °C`,
    };
  }

  function diasCalidos() {
    const a = S.clima.anual, filas = anualesCompletos();
    const campo = a.dias_tx90p ? 'dias_tx90p' : 'pct_tx90p';
    const ys = filas.map(({ y }) => y), vs = filas.map(({ i }) => a[campo][i]);
    const prom = (d, h) => media(filas.filter(({ y }) => y >= d && y <= h).map(({ i }) => a[campo][i]));
    const base = prom(1961, 1990), rec = prom(2016, 2025);
    return {
      tipo: 'bar', labels: ys, unidad: 'días por año',
      datasets: [{ label: 'Días con máxima sobre el percentil 90 de 1961–1990', data: vs, backgroundColor: '#ea580ccc', borderWidth: 0 }],
      clave: base !== null ? `Los días con temperatura máxima inusualmente alta (índice TX90p) pasaron de <b>${fmt(base, 0)} al año</b> en 1961–1990 a <b>${fmt(rec, 0)} al año</b> en 2016–2025.` : '',
      nota: fuenteClima('TX90p: días con máxima por encima del percentil 90 del mismo día del calendario en 1961–1990 (definición ETCCDI).'),
      tooltip: (v) => `${fmt(v, 0)} días`,
    };
  }

  function lluvia() {
    const a = S.clima.anual, filas = anualesCompletos().filter(({ i }) => Number.isFinite(a.precip_chirps[i]));
    const ys = filas.map(({ y }) => y), vs = filas.map(({ i }) => a.precip_chirps[i]);
    const normal = media(filas.filter(({ y }) => y >= 1991 && y <= 2020).map(({ i }) => a.precip_chirps[i]));
    const t = tend('1981-2025', 'precip_chirps');
    return {
      tipo: 'bar', labels: ys, unidad: 'mm por año',
      datasets: [
        { type: 'line', label: 'Normal 1991–2020', data: ys.map(() => normal), borderColor: '#0f172a', borderDash: [4, 4], borderWidth: 1.5, pointRadius: 0 },
        { label: 'Lluvia anual', data: vs, backgroundColor: '#2563ebb3', borderWidth: 0 },
      ],
      clave: normal !== null ? `Lluvia normal (1991–2020): <b>${fmt(normal, 0)} mm al año</b>. ${t ? (t.significativa_5pct ? `Tendencia de ${signo(t.ols_por_decada, 0)} mm por década.` : `Sin tendencia significativa desde 1981 (p = ${fmt(t.ols_p, 2)}).`) : ''}` : '',
      nota: 'Fuente: CHIRPS v3 (Climate Hazards Center, UCSB), promedio sobre la huella urbana. Se usa CHIRPS porque coincide con las normales del IDEAM (cociente 1,1), mientras que la lluvia del reanálisis ERA5 las triplica. <a href="#" data-ficha-serie="clima">Método</a>.',
      tooltip: (v) => `${fmt(v, 0)} mm`,
    };
  }

  /* ---------- Landsat ---------- */
  function anios(campo) {
    const ok = new Set(S.landsat.anios_confiables || []);
    return S.landsat.anios.map((a) => ({ y: a.anio, v: ok.has(a.anio) ? a[campo] : null }));
  }
  /** Dos tramos por sensor: Landsat 5/7 (2000–2012) y Landsat 8/9 (2013–2025) */
  function tramos(campo, etiqueta, color) {
    const d = anios(campo);
    const labels = d.map((x) => x.y);
    return [
      { label: `${etiqueta} · Landsat 5/7`, data: d.map((x) => (x.y <= 2012 ? x.v : null)), borderColor: color, backgroundColor: color, borderDash: [5, 4], pointRadius: 2.5, borderWidth: 2, spanGaps: false, tension: 0.2 },
      { label: `${etiqueta} · Landsat 8/9`, data: d.map((x) => (x.y >= 2013 ? x.v : null)), borderColor: color, backgroundColor: color, pointRadius: 2.5, borderWidth: 2.5, spanGaps: false, tension: 0.2 },
      labels,
    ];
  }
  const lectura = (var_, tramo) => {
    const l = S.landsat.lectura_de_tendencias && S.landsat.lectura_de_tendencias[var_];
    return l && l[tramo] ? l[tramo] : '';
  };
  const primeraFrase = (t) => (String(t || '').match(/^.*?[.!?](\s|$)/) || [''])[0].trim();
  const notaLandsat = () => {
    const geos = (S.landsat.advertencias || []).find((a) => /GEOS/.test(a));
    return 'Fuente: USGS Landsat Collection 2 (dominio público) vía Microsoft Planetary Computer; mediana anual de 3 a 6 escenas despejadas hacia las 10 a. m. Línea discontinua: Landsat 5/7; continua: Landsat 8/9. Los años sin datos suficientes se omiten. '
      + (geos ? esc(primeraFrase(geos)) + ' ' : '')
      + '<a href="#" data-ficha-serie="landsat">Método y advertencias</a>.';
  };
  const conTramo = (texto) => (texto ? `En 2013–2025 (Landsat 8/9): ${esc(texto.charAt(0).toLowerCase() + texto.slice(1))}` : '');

  function lstLandsat() {
    const [a1, a2, labels] = tramos('lst_mediana_nucleo', 'Núcleo construido', '#b91c1c');
    const [b1, b2] = tramos('lst_mediana_urbana', 'Cabecera', '#f97316');
    const [c1, c2] = tramos('lst_mediana_rural', 'Campo', '#16a34a');
    const ult = S.landsat.anios[S.landsat.anios.length - 1];
    return {
      tipo: 'line', labels, unidad: '°C (superficie)', datasets: [a1, a2, b1, b2, c1, c2], leyenda: true,
      clave: `En ${ult.anio}, la superficie del núcleo construido llegó a <b>${fmt(ult.lst_mediana_nucleo)} °C</b> frente a ${fmt(ult.lst_mediana_rural)} °C en el campo. ${conTramo(lectura('lst_urbana', '2013_2025_landsat_8_9'))}`,
      nota: notaLandsat(), tooltip: (v) => `${fmt(v)} °C`,
    };
  }
  function islaCalor() {
    const [a1, a2, labels] = tramos('isla_calor_nucleo', 'Núcleo − campo', '#b91c1c');
    const [b1, b2] = tramos('isla_calor', 'Cabecera − campo', '#f97316');
    const ult = S.landsat.anios[S.landsat.anios.length - 1];
    return {
      tipo: 'line', labels, unidad: '°C de diferencia', datasets: [a1, a2, b1, b2], leyenda: true,
      clave: `En ${ult.anio} el núcleo construido estuvo <b>${fmt(ult.isla_calor_nucleo)} °C más caliente</b> que el campo al paso del satélite. ${esc((S.landsat.sintesis_salto_2012_2013 && S.landsat.sintesis_salto_2012_2013.conclusion) ? S.landsat.sintesis_salto_2012_2013.conclusion.split('. ').slice(0, 3).join('. ') + '.' : conTramo(lectura('isla_calor', '2013_2025_landsat_8_9')))}`,
      nota: notaLandsat(), tooltip: (v) => `${signo(v, 1)} °C`,
    };
  }
  function ndviLandsat() {
    const [a1, a2, labels] = tramos('ndvi_mediana_periurbano', 'Periferia urbana', '#16a34a');
    const [b1, b2] = tramos('ndvi_mediana_urbana', 'Cabecera', '#65a30d');
    const [c1, c2] = tramos('ndvi_mediana_nucleo', 'Núcleo construido', '#a16207');
    return {
      tipo: 'line', labels, unidad: 'NDVI', datasets: [a1, a2, b1, b2, c1, c2], leyenda: true,
      clave: conTramo(lectura('ndvi_urbano', '2013_2025_landsat_8_9')),
      nota: notaLandsat() + ' El NDVI de Landsat 8/9 tiende a ser algo mayor que el de Landsat 5/7 sobre vegetación (Roy et al., 2016).',
      tooltip: (v) => fmt(v, 3), decimales: 2,
    };
  }
  function lstZona(zonaId) {
    const z = S.zonas, lista = z.zonas || [];
    const serie = lista.find((x) => x.id === zonaId) || lista[0];
    if (!serie) return null;
    const anios_ = z.anios;
    const conf = (z.metadatos_anio || []).map((m) => m.confiable);
    const ok = (i) => conf.length ? conf[i] : true;
    const cab = serie.id !== 'cabecera' ? lista.find((x) => x.id === 'cabecera') : null;
    const ds = [];
    const tramo = (vals, etiqueta, color, extra = {}) => [
      { label: `${etiqueta} · Landsat 5/7`, data: vals.map((v, i) => (anios_[i] <= 2012 && ok(i) ? v : null)), borderColor: color, backgroundColor: color, borderDash: [5, 4], pointRadius: 2.5, borderWidth: 2, spanGaps: false, tension: 0.2, ...extra },
      { label: `${etiqueta} · Landsat 8/9`, data: vals.map((v, i) => (anios_[i] >= 2013 && ok(i) ? v : null)), borderColor: color, backgroundColor: color, pointRadius: 2.5, borderWidth: 2.5, spanGaps: false, tension: 0.2, ...extra },
    ];
    ds.push(...tramo(serie.lst, serie.nombre, '#dc2626'));
    if (cab) ds.push(...tramo(cab.lst, 'Cabecera', '#94a3b8', { pointRadius: 0, borderWidth: 1.5 }));
    return {
      tipo: 'line', labels: anios_, unidad: '°C (superficie)', datasets: ds, leyenda: true,
      clave: serie.lectura ? esc(serie.lectura.split('. El tramo 2000')[0]) + '.' : '',
      nota: notaLandsat(), tooltip: (x) => `${fmt(x)} °C`,
    };
  }

  /* ---------- aire (CAMS) ---------- */
  function aireMensual(campo, nombre, guiaAnual) {
    const m = S.aire.mensual;
    const idx = m.mes.map((_, i) => i).filter((i) => m.completo ? m.completo[i] : true);
    const labels = idx.map((i) => m.mes[i]);
    const vals = idx.map((i) => m[campo][i]);
    // cada versión (ciclo) de CAMS se resume por separado: mezclarlas no es comparable
    const pc = (S.aire.comparacion_anual && S.aire.comparacion_anual.por_ciclo_modelo) || {};
    const medias = Object.entries(pc).map(([ciclo, v]) => ({ ciclo, m: v[campo] && v[campo].media })).filter((x) => Number.isFinite(x.m));
    const mn = medias.length ? Math.min(...medias.map((x) => x.m)) : null, mx = medias.length ? Math.max(...medias.map((x) => x.m)) : null;
    const encima = medias.filter((x) => x.m > guiaAnual).length;
    return {
      tipo: 'line', labels, unidad: 'µg/m³', leyenda: true,
      datasets: [
        { label: `${nombre} (media mensual)`, data: vals, borderColor: '#7c3aed', backgroundColor: '#7c3aed22', fill: true, pointRadius: 0, borderWidth: 2, tension: 0.25 },
        { label: `Guía anual OMS 2021 (${guiaAnual} µg/m³)`, data: labels.map(() => guiaAnual), borderColor: '#0f172a', borderDash: [5, 4], pointRadius: 0, borderWidth: 1.5 },
      ],
      clave: medias.length ? `Según la versión del modelo, el ${nombre} medio regional va de <b>${fmt(mn)} a ${fmt(mx)} µg/m³</b>; supera la guía anual de la OMS (${guiaAnual} µg/m³) en ${encima} de ${medias.length} versiones. ${encima === medias.length ? 'Con todas las versiones queda por encima de la guía.' : encima === 0 ? 'Con todas las versiones queda por debajo de la guía.' : 'No se puede afirmar si supera la guía.'}` : '',
      nota: 'Fuente: Copernicus Atmosphere Monitoring Service (CAMS global) vía Open-Meteo. Es un modelo regional de ~40 km: describe el aire de la región, no el de una calle, y no se compara con la capa de tráfico. El modelo cambió de versión en 2023, 2024 y 2026; los saltos pueden deberse a eso. <a href="#" data-ficha-serie="aire">Método</a>.',
      tooltip: (v) => `${fmt(v)} µg/m³`,
    };
  }

  /* ---------- dibujo ---------- */
  function dibujar() {
    const id = $('#serie-var').value;
    const def = SERIES.find((s) => s.id === id);
    const zonaSel = $('#serie-zona');
    zonaSel.hidden = !def.zona;
    let r = null;
    try { r = def.construir(zonaSel.value); } catch (e) { console.error(e); }
    if (!r) { $('#serie-clave').textContent = 'Serie no disponible.'; return; }
    $('#serie-clave').innerHTML = r.clave || '';
    $('#serie-nota').innerHTML = r.nota || '';
    const config = {
      type: r.tipo, data: { labels: r.labels, datasets: r.datasets },
      options: {
        responsive: true, maintainAspectRatio: false, interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: !!r.leyenda, position: 'bottom', labels: { boxWidth: 10, boxHeight: 2, font: { size: 10 }, filter: (it) => !/Landsat 5\/7/.test(it.text) } },
          tooltip: { callbacks: { label: (c) => (c.parsed.y === null ? null : ` ${c.dataset.label}: ${r.tooltip ? r.tooltip(c.parsed.y) : fmt(c.parsed.y)}`) } },
        },
        scales: ejes(r.unidad),
      },
    };
    if (grafico) grafico.destroy();
    grafico = new Chart($('#grafico-serie'), config);
  }

  BM.alIniciar(async () => {
    if (!window.Chart) { $('#tendencias .grafico').innerHTML = '<p class="nota">No se pudo cargar Chart.js.</p>'; return; }
    Chart.defaults.font.family = '"Plus Jakarta Sans", Inter, system-ui, sans-serif';
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#64748b';
    const [clima, landsat, aire, zonas] = await Promise.all(['clima', 'landsat', 'aire', 'zonas'].map((n) => BM.leerJSONopcional(`series/${n}.json`)));
    S = { clima, landsat, aire, zonas };
    BM.SERIES = S;
    const sel = $('#serie-var');
    const grupos = {};
    SERIES.filter((s) => S[s.req]).forEach((s) => {
      if (!grupos[s.grupo]) { grupos[s.grupo] = document.createElement('optgroup'); grupos[s.grupo].label = s.grupo; sel.appendChild(grupos[s.grupo]); }
      grupos[s.grupo].appendChild(new Option(s.nombre, s.id));
    });
    if (zonas) {
      const lista = zonas.zonas || zonas.series || [];
      lista.forEach((z) => $('#serie-zona').add(new Option(z.nombre, z.id)));
    }
    sel.addEventListener('change', dibujar);
    $('#serie-zona').addEventListener('change', dibujar);
    $('#tendencias').addEventListener('click', (e) => {
      const a = e.target.closest('[data-ficha-serie]');
      if (!a) return;
      e.preventDefault();
      BM.irAPestana('tab-datos');
      setTimeout(() => { const el = $(`#ficha-serie-${a.dataset.fichaSerie}`); if (el) { el.open = true; el.scrollIntoView({ behavior: 'smooth' }); } }, 80);
    });
    if (sel.options.length) dibujar();
    BM.alCambiarPestana((id) => { if (id === 'tab-capas' && grafico) grafico.resize(); });
  });
})();
