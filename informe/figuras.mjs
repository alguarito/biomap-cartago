/**
 * Diagramas del informe, en SVG, generados desde los datos publicados de BioMap (../datos).
 * Colores y tipografías de Franja por variables CSS (franja.css): nada de color escrito a mano
 * salvo transparencias. Cada función devuelve una cadena SVG o HTML lista para la lámina.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const DATOS = path.join(AQUI, '..', 'datos');
export const leer = (rel) => JSON.parse(fs.readFileSync(path.join(DATOS, rel), 'utf8'));

const nf = (d) => new Intl.NumberFormat('es-CO', { minimumFractionDigits: d, maximumFractionDigits: d });
export const fmt = (v, d = 1) => (v === null || v === undefined || !Number.isFinite(+v) ? '—' : nf(d).format(+v));
export const signo = (v, d = 2) => (v > 0 ? '+' : v < 0 ? '−' : '±') + fmt(Math.abs(v), d);

/* ---------- datos por zona (indicadores aplanados como en la interfaz) ---------- */
function plano(o, s = {}, pre = '') {
  Object.entries(o || {}).forEach(([k, v]) => {
    const c = pre ? `${pre}_${k}` : k;
    if (v && typeof v === 'object' && !Array.isArray(v)) plano(v, s, c);
    else if (!(c in s)) s[c] = v;
  });
  return s;
}
export function zonas() {
  const I = leer('indicadores.json');
  return I.zonas.map((z) => ({ ...plano(z), id: z.id, nombre: z.nombre }));
}
export const cabecera = () => plano(leer('indicadores.json').cabecera);
const corto = (n) => n.replace('Comuna ', 'C').replace(' (corregimiento)', '');

const T = (x, y, t, { size = 10, w = 600, fill = 'var(--tinta)', anchor = 'start', fam = 'var(--sans)', ls = 0 } = {}) =>
  `<text x="${x}" y="${y}" text-anchor="${anchor}" style="font-family:${fam};font-size:${size}px;font-weight:${w};fill:${fill};letter-spacing:${ls}em">${t}</text>`;

/* ---------- mapa de las comunas ---------- */
/** Coroplético de las 7 comunas con Zaragoza en recuadro. valores: id → número. */
export function mapaZonas({ valor, decimales = 0, unidad = '', titulo = '', ancho = 470 }) {
  const G = leer('vectores/zonas.geojson');
  const Z = zonas();
  const val = Object.fromEntries(Z.map((z) => [z.id, valor(z)]));
  const vs = Object.values(val).filter(Number.isFinite);
  const mn = Math.min(...vs), mx = Math.max(...vs);
  // cinco tonos del papel al vino, por cuantiles iguales del rango
  const tonos = ['var(--papel3)', 'oklch(0.86 0.06 18)', 'oklch(0.74 0.11 17)', 'oklch(0.60 0.14 16)', 'var(--vino-profundo)'];
  const tono = (v) => (Number.isFinite(v) ? tonos[Math.min(4, Math.floor(((v - mn) / ((mx - mn) || 1)) * 4.999))] : 'var(--papel2)');
  const anillos = (f) => (f.geometry.type === 'Polygon' ? [f.geometry.coordinates[0]] : f.geometry.coordinates.map((p) => p[0]));
  const principales = G.features.filter((f) => f.properties.id !== 'zaragoza');
  const zar = G.features.find((f) => f.properties.id === 'zaragoza');
  const lat0 = 4.745, kx = Math.cos((lat0 * Math.PI) / 180);
  const proyectar = (feats, w, h, pad) => {
    const pts = feats.flatMap((f) => anillos(f).flat());
    const xs = pts.map((p) => p[0] * kx), ys = pts.map((p) => p[1]);
    const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
    const s = Math.min((w - 2 * pad) / (x1 - x0), (h - 2 * pad) / (y1 - y0));
    const ox = pad + ((w - 2 * pad) - (x1 - x0) * s) / 2, oy = pad + ((h - 2 * pad) - (y1 - y0) * s) / 2;
    return ([lon, lat]) => [ox + (lon * kx - x0) * s, oy + (y1 - lat) * s];
  };
  const h = Math.round(ancho * 0.74);
  const P = proyectar(principales, ancho, h, 14);
  const dibujar = (f, P2) => {
    const d = anillos(f).map((r) => 'M' + r.map((p) => P2(p).map((c) => c.toFixed(1)).join(' ')).join('L') + 'Z').join('');
    return `<path d="${d}" style="fill:${tono(val[f.properties.id])};stroke:var(--papel);stroke-width:1.6"/>`;
  };
  const centro = (f, P2) => {
    const pts = anillos(f)[0].map(P2);
    return [pts.reduce((a, p) => a + p[0], 0) / pts.length, pts.reduce((a, p) => a + p[1], 0) / pts.length];
  };
  let s = `<svg width="${ancho}" height="${h}" viewBox="0 0 ${ancho} ${h}" role="img" aria-label="${titulo}">`;
  s += principales.map((f) => dibujar(f, P)).join('');
  principales.forEach((f) => {
    const [cx, cy] = centro(f, P);
    const v = val[f.properties.id];
    const oscuro = Number.isFinite(v) && (v - mn) / ((mx - mn) || 1) > 0.55;
    s += T(cx, cy - 2, corto(f.properties.nombre), { size: 10, w: 800, anchor: 'middle', fill: oscuro ? 'var(--papel)' : 'var(--tinta)' });
    s += T(cx, cy + 11, `${fmt(v, decimales)}${unidad}`, { size: 9.5, w: 600, anchor: 'middle', fill: oscuro ? 'var(--papel)' : 'var(--tinta2)' });
  });
  if (zar) { // recuadro de Zaragoza, abajo a la izquierda
    const w2 = 92, h2 = 70, x2 = 4, y2 = h - h2 - 4;
    const P2 = proyectar([zar], w2, h2, 8);
    s += `<g transform="translate(${x2} ${y2})"><rect width="${w2}" height="${h2}" style="fill:none;stroke:var(--filete2);stroke-width:1"/>${dibujar(zar, P2)}`;
    s += T(w2 / 2, h2 - 6, `Zaragoza · ${fmt(val.zaragoza, decimales)}${unidad}`, { size: 8.5, w: 700, anchor: 'middle' }) + '</g>';
  }
  // leyenda
  const lx = ancho - 150, ly = h - 26;
  tonos.forEach((t, i) => { s += `<rect x="${lx + i * 26}" y="${ly}" width="26" height="8" style="fill:${t}"/>`; });
  s += T(lx, ly + 20, `${fmt(mn, decimales)}${unidad}`, { size: 8.5, w: 600, fill: 'var(--tinta3)' });
  s += T(lx + 130, ly + 20, `${fmt(mx, decimales)}${unidad}`, { size: 8.5, w: 600, fill: 'var(--tinta3)', anchor: 'end' });
  return s + '</svg>';
}

/* ---------- barras por zona ---------- */
export function barrasZonas({ valor, decimales = 0, unidad = '', tono = '', orden = true, filas }) {
  let Z = filas || zonas().map((z) => ({ nombre: z.nombre, v: valor(z) }));
  if (orden) Z = Z.slice().sort((a, b) => b.v - a.v);
  const mx = Math.max(...Z.map((z) => z.v).filter(Number.isFinite)) || 1;
  return `<div class="bars">${Z.map((z) => `<div class="bar" style="grid-template-columns:132px 1fr 62px"><span class="lb">${z.nombre.replace(' (corregimiento)', '')}</span><span class="tr"><span class="fl ${tono}" style="width:${Math.max(0, (z.v / mx) * 100).toFixed(1)}%"></span></span><span class="vl">${fmt(z.v, decimales)}${unidad}</span></div>`).join('')}</div>`;
}

/* ---------- series anuales ---------- */
/** Barras con signo (anomalías) o líneas. series: [{nombre, valores, tono, discontinua}] */
export function serie({ anios, series, tipo = 'linea', ancho = 470, alto = 190, unidad = '', decimales = 1, marcas = [] }) {
  const pad = { l: 34, r: 8, t: 10, b: 24 };
  const W = ancho - pad.l - pad.r, H = alto - pad.t - pad.b;
  const todos = series.flatMap((s) => s.valores).filter(Number.isFinite);
  let mn = Math.min(...todos), mx = Math.max(...todos);
  if (tipo === 'barras') { mn = Math.min(mn, 0); mx = Math.max(mx, 0); }
  const rango = mx - mn || 1; mn -= rango * 0.06; mx += rango * 0.06;
  const x = (i) => pad.l + (anios.length === 1 ? W / 2 : (i / (anios.length - 1)) * W);
  const y = (v) => pad.t + (1 - (v - mn) / (mx - mn)) * H;
  let s = `<svg width="${ancho}" height="${alto}" viewBox="0 0 ${ancho} ${alto}" role="img">`;
  // rejilla y eje y
  const paso = (() => { const r = mx - mn, e = Math.pow(10, Math.floor(Math.log10(r / 4))); return [1, 2, 2.5, 5, 10].map((m) => m * e).find((p) => r / p <= 5); })();
  for (let v = Math.ceil(mn / paso) * paso; v <= mx; v += paso) {
    s += `<line x1="${pad.l}" x2="${ancho - pad.r}" y1="${y(v)}" y2="${y(v)}" style="stroke:var(--filete);stroke-width:${Math.abs(v) < 1e-9 ? 1.4 : 0.7}"/>`;
    s += T(pad.l - 5, y(v) + 3, fmt(v, paso < 1 ? (paso < 0.1 ? 2 : 1) : 0), { size: 8, w: 600, fill: 'var(--tinta3)', anchor: 'end' });
  }
  // marcas verticales (p. ej. cambio de sensor)
  marcas.forEach(({ anio, texto }) => {
    const i = anios.indexOf(anio); if (i < 0) return;
    s += `<line x1="${x(i)}" x2="${x(i)}" y1="${pad.t}" y2="${pad.t + H}" style="stroke:var(--tinta3);stroke-width:1;stroke-dasharray:3 3"/>`;
    s += T(x(i) + 4, pad.t + 9, texto, { size: 8, w: 600, fill: 'var(--tinta3)' });
  });
  if (tipo === 'barras') {
    const bw = Math.max(1.5, (W / anios.length) * 0.72);
    series[0].valores.forEach((v, i) => {
      if (!Number.isFinite(v)) return;
      s += `<rect x="${x(i) - bw / 2}" y="${Math.min(y(v), y(0))}" width="${bw}" height="${Math.abs(y(v) - y(0))}" style="fill:${v >= 0 ? 'var(--vino)' : 'var(--teal)'}"/>`;
    });
  } else {
    series.forEach((se) => {
      let d = '', abierto = false;
      se.valores.forEach((v, i) => { if (!Number.isFinite(v)) { abierto = false; return; } d += `${abierto ? 'L' : 'M'}${x(i).toFixed(1)} ${y(v).toFixed(1)}`; abierto = true; });
      s += `<path d="${d}" style="fill:none;stroke:${se.tono || 'var(--vino)'};stroke-width:${se.grosor || 2};${se.discontinua ? 'stroke-dasharray:5 3;' : ''}stroke-linejoin:round"/>`;
    });
  }
  // eje x: primer y último año y décadas
  anios.forEach((a, i) => {
    if (i === 0 || i === anios.length - 1 || a % 10 === 0) s += T(x(i), alto - 8, a, { size: 8, w: 600, fill: 'var(--tinta3)', anchor: 'middle' });
  });
  if (unidad) s += T(pad.l - 30, pad.t - 1, unidad, { size: 7.5, w: 700, fill: 'var(--tinta3)' });
  return s + '</svg>';
}

export const leyenda = (items) =>
  `<div style="display:flex;gap:16px;flex-wrap:wrap;font-family:var(--sans);font-size:9.5px;font-weight:600;color:var(--tinta2)">${items.map(([tono, t, disc]) =>
    `<span style="display:inline-flex;align-items:center;gap:6px"><i style="display:inline-block;width:18px;height:0;border-top:2.5px ${disc ? 'dashed' : 'solid'} ${tono}"></i>${t}</span>`).join('')}</div>`;

/* ---------- ranking de prioridad con aportes ---------- */
export function rankingFig() {
  const P = leer('prioridades.json');
  const comps = P.componentes;
  const tonos = { calor: 'var(--vino)', deficit_verde: 'var(--teal)', inundacion: 'var(--tinta)', trafico: 'var(--vino-claro)', densidad: 'var(--tinta3)' };
  const peso = 1 / comps.length;
  const filas = P.zonas.map((z) => {
    const aportes = comps.map((c) => ({ id: c.id, nombre: c.nombre, v: (c.normalizado[z.id] || 0) * peso }));
    return { z, aportes, total: aportes.reduce((s, a) => s + a.v, 0), rango: P.sensibilidad_ranking.rango_de_puesto_por_zona[z.id] };
  }).sort((a, b) => b.total - a.total);
  const mx = Math.max(...filas.map((f) => f.total));
  const cuerpo = filas.map((f, i) => `<div style="display:grid;grid-template-columns:18px 118px 1fr 44px 58px;gap:8px;align-items:center;padding:5px 0;border-bottom:1px solid var(--filete)">
    <span style="font-family:var(--sans);font-size:10px;font-weight:800;color:var(--vino)">${i + 1}</span>
    <span style="font-family:var(--sans);font-size:10.5px;font-weight:700;color:var(--tinta)">${f.z.nombre.replace(' (corregimiento)', '')}</span>
    <span style="display:flex;height:10px;background:var(--papel3)">${f.aportes.map((a) => `<i style="display:block;height:10px;width:${((a.v / mx) * 100).toFixed(1)}%;background:${tonos[a.id]}"></i>`).join('')}</span>
    <span style="font-family:var(--sans);font-size:11px;font-weight:800;color:var(--tinta);text-align:right">${fmt(f.total, 2)}</span>
    <span style="font-family:var(--sans);font-size:9px;font-weight:600;color:var(--tinta3);text-align:right">${f.rango[0] === f.rango[1] ? `puesto ${f.rango[0]}` : `${f.rango[0]}.º–${f.rango[1]}.º`}</span>
  </div>`).join('');
  const ley = comps.map((c) => `<span style="display:inline-flex;align-items:center;gap:5px"><i style="width:10px;height:10px;display:inline-block;background:${tonos[c.id]}"></i>${c.nombre}</span>`).join('');
  return `<div><div style="display:flex;flex-wrap:wrap;gap:12px;font-family:var(--sans);font-size:9px;font-weight:600;color:var(--tinta2);margin-bottom:8px">${ley}</div>
    <div style="border-top:2px solid var(--tinta)">${cuerpo}</div>
    <div style="display:grid;grid-template-columns:18px 118px 1fr 44px 58px;gap:8px;font-family:var(--sans);font-size:8px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--tinta3);margin-top:5px"><span></span><span></span><span>Aporte de cada criterio (pesos iguales)</span><span style="text-align:right">Índice</span><span style="text-align:right">Rango*</span></div></div>`;
}

/* ---------- diagrama de bosque: efecto de las intervenciones ---------- */
export function bosque({ ancho = 470 } = {}) {
  const C = leer('calibracion.json').intervenciones;
  const arb = C.arbolado.variantes;
  const pred = (x) => (x.heterogeneidad && x.heterogeneidad.intervalo_prediccion_95_lst_por_10pp) || x.ic95_lst_por_10pp;
  const filas = [
    ['Árboles en lugar de superficie construida', arb.sustituye_construido.delta_lst_c_por_10pp, arb.sustituye_construido.ic95_lst, 'Cartago'],
    ['Árboles en lugar de pasto o lote', arb.sustituye_pasto.delta_lst_c_por_10pp, arb.sustituye_pasto.ic95_lst, 'Cartago'],
    ['Techos verdes', C.techos_verdes.delta_lst_c_por_10pp, pred(C.techos_verdes), 'literatura'],
    ['Pavimento frío (sobre asfalto)', C.pavimento_frio.delta_lst_c_por_10pp, pred(C.pavimento_frio), 'literatura'],
    ['Pavimento permeable', C.pavimento_permeable.delta_lst_c_por_10pp, C.pavimento_permeable.ic95_lst_por_10pp, 'literatura'],
  ];
  const lx = 168, W = ancho - lx - 54, fila = 30, alto = filas.length * fila + 44;
  const mn = Math.min(...filas.flatMap((f) => f[2])), mx = Math.max(0.3, ...filas.flatMap((f) => f[2]));
  const x = (v) => lx + ((v - mn) / (mx - mn)) * W;
  let s = `<svg width="${ancho}" height="${alto}" viewBox="0 0 ${ancho} ${alto}" role="img">`;
  s += `<line x1="${x(0)}" x2="${x(0)}" y1="4" y2="${alto - 32}" style="stroke:var(--tinta);stroke-width:1.2"/>`;
  filas.forEach(([nom, v, ic, org], i) => {
    const yy = 16 + i * fila, local = org === 'Cartago';
    s += T(0, yy + 4, nom, { size: 10, w: 700 });
    s += T(0, yy + 15, local ? 'medido en Cartago · IC 95 % del coeficiente' : 'estimado por BioMap con datos de literatura', { size: 7.5, w: 600, fill: local ? 'var(--teal)' : 'var(--tinta3)' });
    s += `<line x1="${x(ic[0])}" x2="${x(ic[1])}" y1="${yy}" y2="${yy}" style="stroke:${local ? 'var(--teal)' : 'var(--tinta3)'};stroke-width:3"/>`;
    s += `<rect x="${x(v) - 5}" y="${yy - 5}" width="10" height="10" style="fill:${local ? 'var(--teal)' : 'var(--vino)'}"/>`;
    s += T(ancho, yy + 4, `${signo(v, 2)} °C`, { size: 10, w: 800, anchor: 'end' });
  });
  [mn, 0, mx].forEach((v) => { s += T(x(v), alto - 20, v === 0 ? '0' : signo(v, 1), { size: 8, w: 600, fill: 'var(--tinta3)', anchor: 'middle' }); });
  s += T(lx + W / 2, alto - 4, '°C de temperatura superficial por cada 10 puntos porcentuales del área de la zona', { size: 7.5, w: 600, fill: 'var(--tinta3)', anchor: 'middle' });
  return s + '</svg>';
}

/* ---------- diagrama del método ---------- */
export function flujoMetodo({ ancho = 470 } = {}) {
  const pasos = [
    ['Fuentes abiertas', 'Landsat · Sentinel-2 · ESA · DANE · IDEAM · OSM · ERA5'],
    ['Rejilla común', '520 × 428 celdas de ~28 m, scripts reproducibles'],
    ['Revisión independiente', 'Plausibilidad, alineación, unidades y licencias'],
    ['Indicadores por zona', 'Comunas 1 a 7 y Zaragoza'],
    ['Priorización y simulador', 'Pesos ajustables · modelo calibrado'],
    ['Recomendaciones', 'Por dependencia, con su fundamento'],
  ];
  const h = 40, g = 12, alto = pasos.length * (h + g);
  let s = `<svg width="${ancho}" height="${alto}" viewBox="0 0 ${ancho} ${alto}" role="img" aria-label="Flujo del método">`;
  s += `<defs><marker id="fm" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 z" style="fill:var(--tinta3)"/></marker></defs>`;
  pasos.forEach(([t, d], i) => {
    const y = i * (h + g), fuerte = i === pasos.length - 1;
    s += `<rect x="0" y="${y}" width="${ancho}" height="${h}" style="fill:${fuerte ? 'var(--vino)' : i === 2 ? 'var(--teal-suave)' : 'var(--papel2)'};stroke:${fuerte ? 'var(--vino)' : 'var(--filete2)'};stroke-width:1"/>`;
    s += T(14, y + 17, `${String(i + 1).padStart(2, '0')}  ${t}`, { size: 11.5, w: 800, fill: fuerte ? 'var(--papel)' : 'var(--tinta)' });
    s += T(14, y + 31, d, { size: 9.5, w: 600, fill: fuerte ? 'oklch(0.97 0.013 85 / .85)' : 'var(--tinta2)' });
    if (i < pasos.length - 1) s += `<line x1="${ancho / 2}" x2="${ancho / 2}" y1="${y + h + 1}" y2="${y + h + g - 1}" style="stroke:var(--tinta3);stroke-width:1.4" marker-end="url(#fm)"/>`;
  });
  return s + '</svg>';
}
