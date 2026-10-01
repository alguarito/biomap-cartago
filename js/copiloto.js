/* BioMap Cartago — Copiloto IA (API de Google Gemini, v1beta).
   El modelo recibe como contexto los datos abiertos ya publicados en la plataforma
   (indicadores, series y el punto inspeccionado) y la instrucción de no inventar cifras.
   La clave la aporta cada usuario y solo se guarda en su navegador si lo pide.
   En un despliegue con clave institucional hay que poner un proxy propio delante de la API. */
'use strict';
(function () {
  const BM = window.BM;
  const { $, fmt, esc } = BM;
  const ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/';
  const CLAVE_LS = 'biomap.gemini.clave';
  const MODELO_LS = 'biomap.gemini.modelo';
  const MODELO_POR_DEFECTO = 'gemini-flash-latest';

  const leerLS = (k) => { try { return localStorage.getItem(k) || ''; } catch { return ''; } };
  const escribirLS = (k, v) => { try { v ? localStorage.setItem(k, v) : localStorage.removeItem(k); } catch { /* almacenamiento bloqueado */ } };

  /* ---------- contexto con los datos de la plataforma ---------- */
  const n = (v, d = 1) => (v === null || v === undefined || !Number.isFinite(+v) ? 's. d.' : (+v).toFixed(d));

  function contexto(punto) {
    const partes = [];
    partes.push(`Eres el Copiloto geoambiental de BioMap Cartago, plataforma de datos abiertos para la toma de decisiones del municipio de Cartago, Valle del Cauca (Colombia): ciudad de unos 140.000 habitantes en la cabecera, a ~917 m s. n. m., en el valle geográfico del río Cauca, junto al río La Vieja.

Respondes en español, con rigor técnico y lenguaje claro para ciudadanía y funcionarios. Usa Markdown (títulos ###, listas, tablas si ayudan). Máximo ~350 palabras salvo que pidan más.

Reglas:
- Usa SOLO las cifras del contexto de abajo y di de qué fuente salen. Si una cifra no está, dilo; no la inventes ni la estimes.
- Distingue siempre: temperatura SUPERFICIAL (Landsat, suelo y techos ~10 a. m.) ≠ temperatura del AIRE (reanálisis ERA5-Land). La capa de tráfico es un índice de exposición, no una medición de NO₂; el NO₂ y el PM2,5 de CAMS son regionales (~40 km).
- Inundación: la referencia oficial es el IDEAM (amenaza por creciente súbita TR 50 del río La Vieja y áreas afectadas en eventos La Niña 1988–2022), además del POT y la CVC. La «susceptibilidad topográfica» (HAND) es un complemento técnico: sus clases bajas NO descartan amenaza. La mancha urbana de La Niña 2011 podría sobrestimar.
- Son estimaciones para priorizar; recomienda verificación en campo y con la Secretaría de Planeación, la CVC o el IDEAM antes de ejecutar obras.
- No cites normas, estudios ni especies que no puedas respaldar. Para arbolado, prioriza especies nativas del valle del Cauca y del bosque seco o de galería, y aclara que la selección final la valida la CVC o un jardín botánico.
- Guías de referencia: OMS 2021, NO₂ anual 10 µg/m³ y PM2,5 anual 5 µg/m³; criterio OMS Europa de acceso a espacio verde a 300 m.`);

    const cab = BM.cabeceraIndicadores && BM.cabeceraIndicadores();
    const zonas = BM.zonasIndicadores ? BM.zonasIndicadores() : [];
    if (zonas.length) {
      const col = [['poblacion', 'Población', 0], ['lst_media', 'LST media °C', 1], ['poblacion_calor_extremo', 'Pob. calor extremo', 0], ['arbolado_pct', 'Arbolado %', 0],
        ['pct_poblacion_sin_verde_300m', '% pob. sin parque 300 m', 0], ['poblacion_evidencia_inundacion_ideam', 'Pob. con registro oficial de inundación (IDEAM)', 0], ['pct_poblacion_susceptibilidad_media', '% pob. susceptibilidad topográfica media', 1], ['poblacion_trafico_alto', 'Pob. tráfico alto', 0]]
        .filter(([k]) => zonas.some((z) => z[k] !== undefined));
      partes.push(`Indicadores por zona (datos/indicadores.json):\n| Zona | ${col.map((c) => c[1]).join(' | ')} |\n|---|${col.map(() => '---').join('|')}|\n${zonas.map((z) => `| ${z.nombre} | ${col.map(([k, , d]) => n(z[k], d)).join(' | ')} |`).join('\n')}${cab ? `\n| Cabecera | ${col.map(([k, , d]) => n(cab[k], d)).join(' | ')} |` : ''}`);
    }
    if (BM.PRIORIDAD_ACTUAL) partes.push(`Ranking de prioridad con los pesos que eligió el usuario: ${BM.PRIORIDAD_ACTUAL}`);

    const S = BM.SERIES || {};
    if (S.clima && S.clima.hallazgos) partes.push(`Clima del aire, ERA5-Land 1950–2025 (subestima valores absolutos de estaciones IDEAM; usar tendencias):\n- ${S.clima.hallazgos.slice(0, 6).join('\n- ')}`);
    if (S.landsat && S.landsat.lectura_de_tendencias) {
      const l = S.landsat.lectura_de_tendencias, u = S.landsat.anios[S.landsat.anios.length - 1];
      partes.push(`Temperatura superficial Landsat: en ${u.anio} núcleo construido ${n(u.lst_mediana_nucleo)} °C, cabecera ${n(u.lst_mediana_urbana)} °C, campo ${n(u.lst_mediana_rural)} °C. Lectura de tendencias: isla de calor 2013–2025: ${l.isla_calor && l.isla_calor['2013_2025_landsat_8_9']}; LST urbana 2013–2025: ${l.lst_urbana && l.lst_urbana['2013_2025_landsat_8_9']}`);
    }
    if (S.aire && S.aire.ultimos_365_dias && S.aire.ultimos_365_dias.media) {
      const m = S.aire.ultimos_365_dias.media;
      partes.push(`Aire regional CAMS (últimos 365 días, media): NO₂ ${n(m.no2)} µg/m³, PM2,5 ${n(m.pm2_5)} µg/m³, PM10 ${n(m.pm10)} µg/m³.`);
    }
    if (punto) {
      partes.push(`Último punto inspeccionado: ${n(punto.lat, 5)}, ${n(punto.lon, 5)} (${punto.zona ? punto.zona.nombre : 'fuera de las zonas'}). Temperatura superficial ${n(punto.lst)} °C; NDVI ${n(punto.ndvi, 2)}; arbolado en 100 m ${n(punto.arbolado100, 0)} %; construido en 100 m ${n(punto.construido100, 0)} %; IDEAM en el punto: ${punto.ideam && punto.ideam.ok ? `${punto.ideam.amenaza ? `amenaza ${punto.ideam.amenaza.toLowerCase()} por creciente súbita TR 50` : 'sin amenaza TR 50'}${punto.ideam.nina.length ? `; inundado en La Niña ${punto.ideam.nina.join(', ')}` : '; sin registro La Niña'}` : 'no consultado'}; susceptibilidad topográfica clase ${n(punto.susceptibilidad, 0)} (0 a 3), ${n(punto.hand)} m sobre el cauce; índice de tráfico ${n(punto.trafico, 0)}/100; parque ≥ 0,5 ha a ${n(punto.distVerde, 0)} m; radiación en cielo despejado ahora ${n(punto.rad.actual, 0)} W/m².`);
    }
    return partes.join('\n\n');
  }

  /* ---------- cliente ---------- */
  const historial = [];
  async function preguntar(texto, { clave, modelo, punto }) {
    historial.push({ role: 'user', parts: [{ text: texto }] });
    const cuerpo = {
      system_instruction: { parts: [{ text: contexto(punto) }] },
      contents: historial.slice(-12),
      generationConfig: { temperature: 0.3, maxOutputTokens: 2048 },
    };
    let resp;
    try {
      resp = await fetch(ENDPOINT + encodeURIComponent(modelo) + ':generateContent', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'x-goog-api-key': clave }, body: JSON.stringify(cuerpo),
      });
    } catch {
      historial.pop();
      throw new Error('No hubo conexión con la API de Gemini. Revisa tu red.');
    }
    let datos = null;
    try { datos = await resp.json(); } catch { /* cuerpo vacío */ }
    if (!resp.ok) {
      historial.pop();
      const msg = datos && datos.error && datos.error.message ? datos.error.message : resp.statusText;
      if (resp.status === 400 && /API key/i.test(msg)) throw new Error('La clave de API no es válida.');
      if (resp.status === 403) throw new Error('La clave no tiene permiso para este modelo o la API no está habilitada.');
      if (resp.status === 404) throw new Error(`El modelo «${modelo}» no existe o no está disponible. Prueba con ${MODELO_POR_DEFECTO}.`);
      if (resp.status === 429) throw new Error('Se alcanzó el límite de uso de la API. Espera un momento y vuelve a intentar.');
      throw new Error(`Error ${resp.status}: ${msg}`);
    }
    const cand = datos && datos.candidates && datos.candidates[0];
    const respuesta = cand && cand.content && cand.content.parts ? cand.content.parts.map((p) => p.text || '').join('') : '';
    if (!respuesta) {
      historial.pop();
      const motivo = (datos && datos.promptFeedback && datos.promptFeedback.blockReason) || (cand && cand.finishReason) || 'sin contenido';
      throw new Error(`La API no devolvió respuesta (${motivo}).`);
    }
    historial.push({ role: 'model', parts: [{ text: respuesta }] });
    return respuesta;
  }

  function markdown(texto) {
    if (window.marked && window.DOMPurify) return window.DOMPurify.sanitize(window.marked.parse(texto));
    return '<p>' + esc(texto).replace(/\n{2,}/g, '</p><p>').replace(/\n/g, '<br>') + '</p>';
  }

  /* ---------- interfaz ---------- */
  BM.alIniciar(() => {
    const clave = $('#ia-clave'), modelo = $('#ia-modelo'), recordar = $('#ia-recordar');
    let claveSesion = leerLS(CLAVE_LS);
    clave.value = claveSesion; modelo.value = leerLS(MODELO_LS) || MODELO_POR_DEFECTO; recordar.checked = !!claveSesion;
    const estado = () => { $('#ia-estado').textContent = claveSesion ? 'Conectado' : 'Sin clave'; $('#ia-estado').classList.toggle('ok', !!claveSesion); };
    if (!claveSesion) $('#ia-config').open = true;
    estado();
    $('#ia-guardar').addEventListener('click', () => {
      claveSesion = clave.value.trim();
      modelo.value = modelo.value.trim() || MODELO_POR_DEFECTO;
      escribirLS(CLAVE_LS, recordar.checked ? claveSesion : '');
      escribirLS(MODELO_LS, modelo.value !== MODELO_POR_DEFECTO ? modelo.value : '');
      estado();
      if (claveSesion) $('#ia-config').open = false;
    });
    $('#ia-olvidar').addEventListener('click', () => { claveSesion = ''; clave.value = ''; recordar.checked = false; escribirLS(CLAVE_LS, ''); estado(); });

    const centro = BM.zonaEn(4.7497, -75.9132);
    [
      `¿Qué medidas contra el calor priorizarías en el centro tradicional${centro ? ` (${centro.nombre})` : ''}, alrededor del Parque Bolívar?`,
      '¿Qué zona debería intervenirse primero y por qué, según los indicadores?',
      '¿Qué especies nativas recomiendas para restaurar el bosque de galería del río La Vieja?',
      '¿Cómo ha cambiado el clima de Cartago desde 1950 y qué implica para la salud?',
      '¿Qué colegios o centros de salud están más expuestos al calor o a inundaciones?',
      'Interpreta el último punto que inspeccioné en el mapa.',
    ].forEach((q) => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'chip'; b.textContent = q;
      b.addEventListener('click', () => enviar(q));
      $('#ia-sugeridas').appendChild(b);
    });

    const chat = $('#chat'), texto = $('#ia-texto'), boton = $('#ia-enviar');
    const agregar = (clase, html) => {
      const d = document.createElement('div');
      d.className = 'msg ' + clase; d.innerHTML = html;
      chat.appendChild(d);
      d.scrollIntoView({ block: 'end', behavior: 'smooth' });
      return d;
    };
    let ocupado = false;
    async function enviar(q) {
      q = q.trim();
      if (!q || ocupado) return;
      if (!claveSesion) {
        $('#ia-config').open = true; clave.focus();
        agregar('msg-error', '<p>Para usar el copiloto, pega tu clave de API de Gemini y pulsa <b>Guardar</b>.</p>');
        return;
      }
      if (/último punto/i.test(q) && !BM.ultimoPunto) {
        agregar('msg-error', '<p>Aún no has inspeccionado ningún punto. Haz clic en el mapa y vuelve a preguntar.</p>');
        return;
      }
      ocupado = true; boton.disabled = true; texto.value = '';
      agregar('msg-usuario', esc(q));
      const espera = agregar('msg-ia msg-pensando', 'Analizando…');
      try {
        const r = await preguntar(q, { clave: claveSesion, modelo: modelo.value.trim() || MODELO_POR_DEFECTO, punto: $('#ia-punto').checked ? BM.ultimoPunto : null });
        espera.className = 'msg msg-ia';
        espera.innerHTML = `<div class="prosa">${markdown(r)}</div>`;
        espera.querySelectorAll('a').forEach((a) => { a.target = '_blank'; a.rel = 'noopener'; });
      } catch (e) {
        espera.className = 'msg msg-error';
        espera.textContent = e.message;
      } finally {
        ocupado = false; boton.disabled = false;
      }
    }
    $('#ia-form').addEventListener('submit', (e) => { e.preventDefault(); enviar(texto.value); });
    texto.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); enviar(texto.value); } });
  });

  BM.contextoCopiloto = contexto; // útil para revisar qué ve el modelo
})();
