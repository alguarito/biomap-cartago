/* BioMap Cartago — herramientas de decisión.
   1) Priorización de zonas con pesos ajustables (datos/prioridades.json).
   2) Simulador de intervenciones con coeficientes calibrados en Cartago o tomados de
      literatura verificada (datos/calibracion.json), siempre con su intervalo de confianza. */
'use strict';
(function () {
  const BM = window.BM;
  const { $, $$, fmt, esc } = BM;
  const signo = (v, d = 2) => (v === null || v === undefined || !Number.isFinite(v) ? '—' : (v > 0 ? '+' : v < 0 ? '−' : '±') + fmt(Math.abs(v), d));

  const COLORES = { calor: '#dc2626', deficit_verde: '#16a34a', inundacion: '#2563eb', trafico: '#7c3aed', densidad: '#64748b' };

  /* ================= prioridades ================= */
  let P = null, pesos = {}, varianteInund = 'por_defecto';

  /** Variantes del criterio de inundación publicadas en prioridades.json (la primera es la de por defecto). */
  function variantesInundacion() {
    const base = P.componentes.find((c) => c.id === 'inundacion');
    const lista = [{ id: 'por_defecto', nombre: base ? base.nombre : 'Inundación' }];
    Object.entries(P.variantes_componentes || {}).forEach(([id, v]) => {
      if (id.startsWith('inundacion_') && v.normalizado) lista.push({ id, nombre: v.nombre || id });
    });
    return lista;
  }

  function componentes() {
    return P.componentes.map((c) => {
      if (c.id === 'inundacion' && varianteInund !== 'por_defecto') {
        const v = P.variantes_componentes[varianteInund];
        return { ...c, nombre: v.nombre || c.nombre, normalizado: v.normalizado, valores_origen: v.valores_origen || null, formula: v.formula || c.formula, advertencia: v.advertencia || '', unidad_origen: 'fracción de la población (0–1)' };
      }
      return c;
    });
  }

  function valorOrigenTexto(c, v, zonaId) {
    if (c.id === 'deficit_verde') {
      const z = BM.zonasIndicadores().find((q) => q.id === zonaId) || {};
      return `${fmt(z.pct_poblacion_sin_verde_300m, 0)} % sin parque a 300 m, ${fmt(z.arbolado_pct_pob, 0)} % de arbolado donde vive la gente`;
    }
    if (v === null || v === undefined) return '—';
    if (/fracción/.test(c.unidad_origen || '')) return `${fmt(v * 100, 0)} % de la población`;
    if (/hab/.test(c.unidad_origen || '')) return `${fmt(v, 0)} hab/km²`;
    return `${fmt(v, 2)} ${c.unidad_origen || ''}`;
  }

  function calcularRanking() {
    const comps = componentes();
    const total = comps.reduce((s, c) => s + (pesos[c.id] || 0), 0) || 1;
    return P.zonas.map((z) => {
      const aportes = comps.map((c) => ({ c, v: (c.normalizado[z.id] || 0) * (pesos[c.id] || 0) / total }));
      const indice = aportes.reduce((s, a) => s + a.v, 0);
      const motivos = aportes.filter((a) => a.v > 0).sort((a, b) => b.v - a.v).slice(0, 2)
        .map((a) => `${a.c.nombre.toLowerCase()}: ${valorOrigenTexto(a.c, a.c.valores_origen ? a.c.valores_origen[z.id] : null, z.id)}`);
      const rango = P.sensibilidad_ranking && P.sensibilidad_ranking.rango_de_puesto_por_zona && P.sensibilidad_ranking.rango_de_puesto_por_zona[z.id];
      return { z, indice, aportes, motivos, rango };
    }).sort((a, b) => b.indice - a.indice);
  }

  function pintarRanking() {
    const r = calcularRanking();
    $('#ranking').innerHTML = r.map((x, i) => `
      <button type="button" class="fila-rank" data-zona="${esc(x.z.id)}">
        <span class="pos">${i + 1}</span>
        <span>
          <span class="nom">${esc(x.z.nombre)}</span>
          <span class="barras">${x.aportes.map((a) => `<i style="width:${(a.v * 100).toFixed(1)}%;background:${COLORES[a.c.id] || '#94a3b8'}" title="${esc(a.c.nombre)}"></i>`).join('')}</span>
          <span class="motivo">${x.motivos.length ? esc(x.motivos.join(' · ')) : 'Sin criterios activos'}${x.rango ? ` · puesto ${x.rango[0] === x.rango[1] ? x.rango[0] : `${x.rango[0]}–${x.rango[1]}`} en las variantes de sensibilidad` : ''}</span>
        </span>
        <span class="indice">${fmt(x.indice, 2)}${i > 0 && r[i - 1].indice - x.indice < 0.01 ? '<small class="empate">≈ empate</small>' : ''}</span>
      </button>`).join('');
    BM.PRIORIDAD_ACTUAL = r.map((x, i) => `${i + 1}. ${x.z.nombre} (${fmt(x.indice, 2)}; ${x.motivos.join('; ')})`).join(' · ')
      + ` [pesos: ${componentes().map((c) => `${c.nombre} ${pesos[c.id]}`).join(', ')}]`;
  }

  /** El déficit de verde es el promedio de dos subcriterios normalizados: su rango entre zonas es menor que 0–1. */
  function notaDeficit() {
    const c = P.componentes.find((x) => x.id === 'deficit_verde');
    if (!c || !c.normalizado) return '';
    const v = Object.values(c.normalizado);
    const mn = Math.min(...v), mx = Math.max(...v);
    return mx - mn < 0.95 ? ` El déficit de verde varía entre ${fmt(mn, 2)} y ${fmt(mx, 2)} (promedio de dos subcriterios), así que con pesos iguales influye algo menos que los demás.` : '';
  }

  function construirPrioridades() {
    const comps = componentes();
    comps.forEach((c) => (pesos[c.id] = 1));
    $('#prioridades').innerHTML = `
      <div class="pesos">${comps.map((c) => `
        <div class="peso">
          <label for="peso-${c.id}" title="${esc(c.advertencia || '')}"><span style="color:${COLORES[c.id]}">●</span> <span data-nombre="${c.id}">${esc(c.nombre)}</span><small>${esc(c.formula)}</small></label>
          <input type="range" id="peso-${c.id}" min="0" max="3" step="1" value="1" data-comp="${c.id}">
          <output id="peso-${c.id}-v">×1</output>
        </div>`).join('')}
      </div>
      <label class="campo mt-3"><span>Fuente del criterio de inundación</span>
        <select id="variante-inund" class="selector">${variantesInundacion().map((v) => `<option value="${esc(v.id)}">${esc(v.nombre)}${v.id === 'por_defecto' ? ' (recomendado)' : ''}</option>`).join('')}</select></label>
      <div class="ranking" id="ranking"></div>
      <p class="nota mt-2">${esc(P.metodo && P.metodo.relativo ? P.metodo.relativo : '')} Índice de 0 a 1: promedio ponderado de los criterios normalizados entre las 8 zonas.${notaDeficit()} Diferencias menores de 0,01 se marcan como empate. Toca una zona para verla y simular una intervención.</p>`;
    $$('#prioridades input[type=range]').forEach((r) => r.addEventListener('input', () => {
      pesos[r.dataset.comp] = +r.value;
      $(`#peso-${r.dataset.comp}-v`).textContent = '×' + r.value;
      pintarRanking();
    }));
    $('#variante-inund').addEventListener('change', (e) => {
      varianteInund = e.target.value;
      const c = componentes().find((x) => x.id === 'inundacion');
      if (c) {
        $('[data-nombre="inundacion"]').textContent = c.nombre;
        $('label[for="peso-inundacion"] small').textContent = c.formula;
        $('label[for="peso-inundacion"]').title = c.advertencia || '';
      }
      pintarRanking();
    });
    $('#prioridades').addEventListener('click', (e) => {
      const b = e.target.closest('[data-zona]');
      if (!b) return;
      BM.irAZona(b.dataset.zona);
      const sel = $('#sim-comuna');
      if (sel) { sel.value = b.dataset.zona; sel.dispatchEvent(new Event('change')); }
    });
    pintarRanking();
  }

  /* ================= simulador ================= */
  let C = null, graficoSim = null, resalte = null;

  /** Intervenciones disponibles según calibracion.json. disponible(z): puntos porcentuales del área de la zona
      que la intervención puede ocupar (topes de disponibilidad_por_zona). intervalo: para los coeficientes locales,
      IC 95 % del coeficiente por bootstrap espacial; para los de literatura, el intervalo de predicción para un sitio
      nuevo (recoge la heterogeneidad entre estudios), no el IC de la media. */
  function intervenciones() {
    const I = C.intervenciones, D = C.disponibilidad_por_zona;
    const arb = I.arbolado && I.arbolado.variantes;
    const prediccion = (x) => (x.heterogeneidad && x.heterogeneidad.intervalo_prediccion_95_lst_por_10pp) || null;
    const sv = C.superficie_vial && C.superficie_vial.superficie_etiquetada_pct_de_la_longitud;
    const lista = [];
    if (arb && arb.sustituye_pasto) lista.push({
      id: 'arbolado_pasto', nombre: 'Arbolado en zonas verdes y lotes (incluye bosque de galería)', sub: 'Sembrar árboles donde hoy hay pasto, lote o suelo desnudo. Supuesto conservador recomendado.',
      origen: 'local', lst: arb.sustituye_pasto.delta_lst_c_por_10pp, intervalo: arb.sustituye_pasto.ic95_lst, tipoIntervalo: 'coeficiente',
      ndvi: arb.sustituye_pasto.delta_ndvi_por_10pp, base: 'pasto', disponible: (z) => D[z].max_pp_arbolado_sustituyendo_pasto,
    });
    if (arb && arb.sustituye_construido) lista.push({
      id: 'arbolado_duro', nombre: 'Arbolado en la superficie vial', sub: 'Sembrar árboles retirando pavimento en calzadas y separadores. El efecto se midió comparando árboles con superficie construida; el área disponible se limita a las vías de OpenStreetMap.',
      origen: 'local', lst: arb.sustituye_construido.delta_lst_c_por_10pp, intervalo: arb.sustituye_construido.ic95_lst, tipoIntervalo: 'coeficiente',
      ndvi: arb.sustituye_construido.delta_ndvi_por_10pp, base: 'calzadas', disponible: (z) => D[z].calzadas_osm_pct ?? D[z].max_pp_pavimento_frio,
    });
    if (I.techos_verdes) lista.push({
      id: 'techos', nombre: 'Techos verdes y jardines verticales', sub: 'Cubrir techos con vegetación.',
      origen: 'literatura', lst: I.techos_verdes.delta_lst_c_por_10pp,
      intervalo: prediccion(I.techos_verdes) || I.techos_verdes.ic95_lst_por_10pp, tipoIntervalo: prediccion(I.techos_verdes) ? 'prediccion' : 'media',
      icMedia: I.techos_verdes.ic95_lst_por_10pp,
      ndvi: I.techos_verdes.delta_ndvi ? I.techos_verdes.delta_ndvi.delta_ndvi_por_10pp : 0, base: 'techos', disponible: (z) => D[z].max_pp_techos_verdes,
      cita: I.techos_verdes.cita, url: I.techos_verdes.url, local: I.techos_verdes.contraste_local,
      aviso: I.techos_verdes.advertencia_ic || null,
    });
    if (I.pavimento_frio) lista.push({
      id: 'pav_frio', nombre: 'Pavimento frío (reflectivo)', sub: 'Reemplazar asfalto oscuro por superficies claras.',
      origen: 'literatura', lst: I.pavimento_frio.delta_lst_c_por_10pp,
      intervalo: prediccion(I.pavimento_frio) || I.pavimento_frio.ic95_lst_por_10pp, tipoIntervalo: prediccion(I.pavimento_frio) ? 'prediccion' : 'media',
      icMedia: I.pavimento_frio.ic95_lst_por_10pp, ndvi: 0,
      base: 'calzadas', disponible: (z) => D[z].max_pp_pavimento_frio, cita: I.pavimento_frio.cita, url: I.pavimento_frio.url,
      aviso: `Solo vale sobre asfalto: frente a concreto el efecto no es significativo.${sv ? ` En OpenStreetMap solo el ${fmt(sv.asphalt, 1)} % de la longitud vial está etiquetada como asfalto y el ${fmt(sv['sin etiqueta'], 0)} % no tiene etiqueta, así que la superficie realmente aplicable es desconocida y probablemente menor.` : ''}`,
    });
    if (I.pavimento_permeable) lista.push({
      id: 'pav_perm', nombre: 'Pavimento permeable y peatonalización', sub: 'Pavimentos porosos y calles peatonales.',
      origen: 'literatura', lst: I.pavimento_permeable.delta_lst_c_por_10pp, intervalo: I.pavimento_permeable.ic95_lst_por_10pp, tipoIntervalo: 'media', ndvi: 0,
      base: 'calzadas', disponible: (z) => D[z].max_pp_pavimento_frio, cita: I.pavimento_permeable.cita, url: I.pavimento_permeable.url,
      aviso: I.pavimento_permeable.recomendacion_simulador,
    });
    return lista;
  }

  const NOMBRE_INTERVALO = {
    coeficiente: 'IC 95 % del coeficiente (no incluye el error del modelo)',
    prediccion: 'Rango probable en un sitio nuevo (intervalo de predicción 95 %)',
    media: 'IC 95 % de la media de los estudios',
  };
  const BASE = { pasto: 'pasto, lotes y suelo', techos: 'techos estimados (construido menos calzadas)', calzadas: 'calzadas de las vías de OpenStreetMap' };
  const citaCorta = (c) => { const m = String(c || '').match(/^(.*?\(\d{4}\))/); return m ? m[1] : String(c || '').slice(0, 60); };

  const zonaInd = (id) => BM.zonasIndicadores().find((z) => z.id === id) || {};

  /** Efecto de una intervención. Los pisos (delta_lst_minimo_c, delta_ndvi_maximo) impiden extrapolar más allá
      de lo observado en Cartago: ninguna zona queda más fresca que su bosque urbano actual. */
  function calcular(t, zonaId, I) {
    const D = C.disponibilidad_por_zona[zonaId] || {};
    const disp = t.disponible(zonaId) || 0;
    const pp = (disp * I) / 100;
    const f = pp / 10;
    const pisoLST = Number.isFinite(D.delta_lst_minimo_c) ? D.delta_lst_minimo_c : -Infinity;
    const topeNDVI = Number.isFinite(D.delta_ndvi_maximo) ? D.delta_ndvi_maximo : Infinity;
    const acotar = (v) => Math.max(v, pisoLST);
    const crudo = t.lst * f;
    const z = zonaInd(zonaId);
    return {
      pp, disp, ha: (pp / 100) * (z.area_km2 || 0) * 100, dLST: acotar(crudo), enPiso: crudo < pisoLST, pisoLST,
      intervalo: t.intervalo ? [acotar(t.intervalo[0] * f), acotar(t.intervalo[1] * f)].sort((a, b) => a - b) : null,
      dNDVI: Math.min((t.ndvi || 0) * f, topeNDVI),
    };
  }

  function recalcular() {
    const zonaId = $('#sim-comuna').value;
    const tipos = intervenciones();
    const t = tipos.find((x) => x.id === ($('input[name=sim-tipo]:checked') || {}).value) || tipos[0];
    const I = +$('#sim-int').value;
    $('#sim-int-val').textContent = I + ' %';
    const z = zonaInd(zonaId), r = calcular(t, zonaId, I);
    $('#sim-int-ayuda').textContent = `Porcentaje de la superficie disponible que se interviene. Disponible en esta zona: ${fmt(r.disp, 1)} % del área (${BASE[t.base]}). Equivale a ${fmt(r.pp, 1)} puntos porcentuales, unas ${fmt(r.ha, 1)} ha.`;

    const etiqueta = `<span class="etiqueta-origen ${t.origen}">${t.origen === 'local' ? 'medido en Cartago' : 'estimado con literatura'}</span>`;
    const cruza = r.intervalo && r.intervalo[0] < 0 && r.intervalo[1] > 0;
    $('#sim-kpis').innerHTML = `
      <dl class="kpi"><dt>Temp. superficial</dt><dd><div class="delta">${signo(r.dLST, 2)} °C</div><div class="de-a">${r.intervalo ? `${NOMBRE_INTERVALO[t.tipoIntervalo]}: ${signo(r.intervalo[0], 2)} a ${signo(r.intervalo[1], 2)}${cruza ? ' (puede no enfriar)' : ''}` : ''}</div><div class="de-a">${fmt(z.lst_media)} → ${fmt((z.lst_media || 0) + r.dLST)} °C</div></dd></dl>
      <dl class="kpi"><dt>Vegetación (NDVI)</dt><dd><div class="delta">${signo(r.dNDVI, 3)}</div><div class="de-a">${fmt(z.ndvi_medio, 2)} → ${fmt((z.ndvi_medio || 0) + r.dNDVI, 2)}</div></dd></dl>
      <dl class="kpi"><dt>NO₂ y tráfico</dt><dd><div class="delta" style="font-size:.95rem">No cuantificable</div><div class="de-a">Sin base local ni de literatura verificada</div></dd></dl>`;
    $('#sim-nota').innerHTML = `<b>${esc(z.nombre || '')}</b> · ${fmt(z.poblacion, 0)} habitantes · ${fmt(z.area_km2, 2)} km². ${esc(t.nombre)} ${etiqueta}`
      + (t.aviso ? `<br><b>Atención:</b> ${esc(t.aviso)}` : '')
      + (r.enPiso ? `<br><b>Tope alcanzado:</b> el efecto se limita a ${signo(r.pisoLST, 2)} °C, lo que dejaría la zona tan fresca como el bosque urbano que ya existe en Cartago; el modelo no extrapola más allá.` : '')
      + `<br>Comparación de las intervenciones al ${I} % de su propia superficie disponible (el área intervenida cambia en cada una; ver hectáreas). Barra: intervalo; punto: estimación central.`;

    if (window.Chart) {
      const filas = tipos.map((x) => ({ x, r: calcular(x, zonaId, I) }));
      const datos = {
        labels: filas.map((f) => `${f.x.nombre.replace(' (incluye bosque de galería)', '')} · ${fmt(f.r.ha, 1)} ha`),
        datasets: [
          { type: 'bar', label: 'Intervalo', data: filas.map((f) => f.r.intervalo || [f.r.dLST, f.r.dLST]), backgroundColor: filas.map((f) => (f.x.id === t.id ? '#05966955' : '#94a3b844')), borderColor: filas.map((f) => (f.x.id === t.id ? '#059669' : '#94a3b8')), borderWidth: 1, borderSkipped: false, barPercentage: 0.55 },
          { type: 'scatter', label: 'Estimación', data: filas.map((f, i) => ({ x: f.r.dLST, y: i })), backgroundColor: '#022c22', pointRadius: 4, pointStyle: 'rectRot' },
        ],
      };
      const opciones = {
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => {
          const f = filas[c.dataIndex];
          return c.dataset.type === 'scatter' ? ` ${signo(c.parsed.x, 2)} °C sobre ${fmt(f.r.ha, 1)} ha` : ` ${NOMBRE_INTERVALO[f.x.tipoIntervalo]}: ${signo(c.raw[0], 2)} a ${signo(c.raw[1], 2)} °C`;
        } } } },
        scales: {
          x: { title: { display: true, text: 'Cambio de temperatura superficial media de la zona (°C)' }, grid: { color: '#eef2f7' } },
          y: { type: 'category', labels: datos.labels, grid: { display: false }, ticks: { font: { size: 10 } } },
        },
      };
      if (graficoSim) graficoSim.destroy();
      graficoSim = new Chart($('#grafico-sim'), { data: datos, options: opciones });
    }
    resaltarZona(zonaId);
  }

  function supuestos() {
    const m = C.modelos && C.modelos.lst;
    const mn = C.modelos && C.modelos.ndvi;
    const ref = (t) => (t.url ? `<a href="${esc(t.url)}" target="_blank" rel="noopener">${esc(citaCorta(t.cita) || t.url)}</a>` : esc(citaCorta(t.cita)));
    const tipos = intervenciones();
    $('#sim-supuestos').innerHTML = `
      <p><b>${esc(C.advertencia_principal || '')}</b></p>
      ${m ? `<p><span class="etiqueta-origen local">medido en Cartago</span> Modelo de regresión con ${fmt(m.n, 0)} unidades de ~111 m de la cabecera: temperatura superficial (Landsat 2022–2025) según arbolado, área construida, agua y altitud (ESA WorldCover, Copernicus DEM). R² = ${fmt(m.r2, 2)}; error típico ${fmt(m.rmse_c, 1)} °C. Intervalos del coeficiente por remuestreo de bloques espaciales de 500 m (1.000 réplicas); no incluyen el error del modelo.${mn ? ` El NDVI se modela igual con ${fmt(mn.n, 0)} celdas (R² = ${fmt(mn.r2, 2)}).` : ''}</p>` : ''}
      <ul>${tipos.map((t) => `<li><b>${esc(t.nombre)}:</b> ${signo(t.lst, 2)} °C por cada 10 puntos porcentuales del área${t.intervalo ? ` (${NOMBRE_INTERVALO[t.tipoIntervalo]}: ${signo(t.intervalo[0], 2)} a ${signo(t.intervalo[1], 2)}${t.icMedia && t.tipoIntervalo === 'prediccion' ? `; IC de la media: ${signo(t.icMedia[0], 2)} a ${signo(t.icMedia[1], 2)}` : ''})` : ''} <span class="etiqueta-origen ${t.origen}">${t.origen === 'local' ? 'medido en Cartago' : 'estimado con literatura'}</span>${t.cita ? `<br><small>${ref(t)}${t.local ? `. Contraste con el modelo local: ${signo(t.local.delta_lst_c_por_10pp, 2)} °C` : ''}</small>` : ''}</li>`).join('')}</ul>
      <p><span class="etiqueta-origen cualitativo">cualitativo</span> ${esc((C.efecto_no2_trafico && (C.efecto_no2_trafico.cualitativo || C.efecto_no2_trafico.texto)) || '')}</p>
      ${C.limitaciones ? `<h4>Limitaciones</h4><ul>${C.limitaciones.map((l) => `<li>${esc(l)}</li>`).join('')}</ul>` : ''}`;
  }

  function resaltarZona(id) {
    if ($('#tab-sim').hidden) return;
    const z = BM.ZONAS.find((q) => q.id === id);
    if (!z) return;
    if (resalte) BM.mapa.removeLayer(resalte);
    resalte = L.polygon(z.anillos, { pane: 'resalte', color: '#059669', weight: 3.5, fillColor: '#10b981', fillOpacity: 0.1, interactive: false }).addTo(BM.mapa);
  }

  function construirSimulador() {
    const sel = $('#sim-comuna');
    BM.zonasIndicadores().forEach((z) => sel.add(new Option(z.nombre, z.id)));
    const cont = $('#sim-tipos');
    intervenciones().forEach((t, i) => {
      const l = document.createElement('label');
      l.className = 'opcion';
      l.innerHTML = `<input type="radio" name="sim-tipo" value="${t.id}" ${i === 0 ? 'checked' : ''}><div><b>${esc(t.nombre)}</b><span>${esc(t.sub)} <span class="etiqueta-origen ${t.origen}">${t.origen === 'local' ? 'medido en Cartago' : 'estimado con literatura'}</span></span></div>`;
      cont.appendChild(l);
    });
    sel.addEventListener('change', recalcular);
    cont.addEventListener('change', recalcular);
    $('#sim-int').addEventListener('input', recalcular);
    supuestos();
    recalcular();
    BM.alCambiarPestana((id) => {
      if (id === 'tab-sim') { resaltarZona(sel.value); if (graficoSim) graficoSim.resize(); }
      else if (resalte) { BM.mapa.removeLayer(resalte); resalte = null; }
    });
  }

  BM.alIniciar(async () => {
    [P, C] = await Promise.all([BM.leerJSONopcional('prioridades.json'), BM.leerJSONopcional('calibracion.json')]);
    if (P && P.componentes) construirPrioridades();
    else $('#prioridades').innerHTML = '<p class="nota">La priorización aún no está publicada.</p>';
    if (C && C.intervenciones && C.disponibilidad_por_zona && BM.zonasIndicadores().length) construirSimulador();
    else $('#sim-kpis').innerHTML = '<p class="nota">La calibración del simulador aún no está publicada.</p>';
  });
})();
