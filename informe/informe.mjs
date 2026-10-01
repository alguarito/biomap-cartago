/**
 * Informe de hallazgos y recomendaciones — BioMap Cartago
 * Sistema editorial «Franja» (forma en lib.mjs y componentes.css; color y tipografía en franja.css).
 *
 * El texto sale de contenido.json (redactado y verificado aparte) y las cifras y diagramas de
 * ../datos. Este archivo solo compone. La paginación de los bloques largos se ajusta con
 * paginacion.json, que escribe generar.mjs cuando una lámina se desborda.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  raw, page, fijarEncabezado, secno, raillab, note, kicker, hsec, lead, par, tiny, sub, src, ul, ol, tb, figh, stat, statrow, warn,
} from './lib.mjs';
import * as F from './figuras.mjs';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const C = JSON.parse(fs.readFileSync(path.join(AQUI, process.env.CONTENIDO || 'contenido.json'), 'utf8'));
const PAG = fs.existsSync(path.join(AQUI, 'paginacion.json')) ? JSON.parse(fs.readFileSync(path.join(AQUI, 'paginacion.json'), 'utf8')) : {};
const M = C.meta;
// Créditos del proyecto escolar: única fuente para portada, ficha, pie y colofón.
const CR = JSON.parse(fs.readFileSync(path.join(AQUI, 'creditos.json'), 'utf8'));
const ESTUDIANTES = CR.estudiantes.join(' · ');

fijarEncabezado(`${CR.institucion} <em>·</em> ${CR.ciudad}`);
export const TITULO = `${M.titulo} — BioMap Cartago`;
const PIE = `BioMap Cartago <em>·</em> ${CR.institucion} <em>·</em> Grado ${CR.grado} <em>·</em> 2026`;
const esc = (t) => String(t ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
// el contenido puede traer cursivas APA marcadas con *texto* o <em>
const md = (t) => esc(t).replace(/&lt;(\/?)(em|strong|i|b)&gt;/g, '<$1$2>').replace(/\*([^*]+)\*/g, '<em>$1</em>');

const LAMINAS = [];
let n = 1;
const indice = []; // [parte, primera lámina, última lámina]
const marcar = (parte) => indice.push([parte, n + 1, n + 1]);
const extender = () => { if (indice.length) indice[indice.length - 1][2] = n; };
const lamina = (nombre, titulo, { running, rail, col }) => {
  n += 1;
  LAMINAS.push({ nombre, titulo, html: page({ running, rail, col, num: n, foot: PIE }) });
  extender();
};
const aire = (h = 6) => `<div style="height:${h}px"></div>`;
// fila de cifras que no se monta: el tamaño baja con el largo del valor y el número de columnas
const cifrasFila = (items, cols) => {
  const largo = Math.max(...items.map((c) => String(c.valor).length));
  const t = cols >= 4 ? (largo > 4 ? 30 : 38) : cols === 3 ? (largo > 5 ? 34 : 44) : 52;
  return statrow(items.map((c) => stat(`<span style="font-size:${t}px">${esc(c.valor)}${c.unidad ? `<small> ${esc(c.unidad)}</small>` : ''}</span>`, md(c.etiqueta), 'o')), cols);
};

/** Reparte bloques en láminas según una capacidad en caracteres equivalentes (ajustable por clave). */
function paginar(clave, bloques, capacidad, peso = (b) => b.length) {
  const cap = capacidad * (PAG[clave] || 1);
  const grupos = [[]]; let acum = 0;
  bloques.forEach((b) => {
    const p = peso(b);
    if (acum + p > cap && grupos[grupos.length - 1].length) { grupos.push([]); acum = 0; }
    grupos[grupos.length - 1].push(b); acum += p;
  });
  return grupos;
}
const textoPlano = (h) => h.replace(/<[^>]+>/g, '');

/* ================================ PORTADA ================================ */
const cifras = (M.cifras_portada || []).slice(0, 4);
const destacada = cifras.find((c) => String(c.valor).length <= 5) || null;
LAMINAS.push({ nombre: 'Main', titulo: '01 · Portada', html: raw(`<div class="cover">
  <div class="grid"></div><div class="glow"></div><div class="glow2"></div>
  <div class="z">
    <header class="cvh"><span>República de Colombia · ${esc(CR.institucion)}</span><span>${esc(CR.ciudad)} · ${esc(M.fecha)}</span></header>
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:24px;padding:24px 0">
      <div style="font-family:var(--sans);font-size:11px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--vino-claro)">Informe técnico de hallazgos y recomendaciones</div>
      <h1 class="cvt" style="font-size:58px;line-height:.95">${md(M.titulo)}</h1>
      ${M.subtitulo ? `<div class="cvsub" style="max-width:560px">${md(M.subtitulo)}</div>` : ''}
      ${destacada ? `<div style="display:flex;align-items:flex-end;gap:24px;margin-top:6px"><div class="cvy" style="font-size:120px">${esc(destacada.valor)}</div>
        <div style="padding-bottom:14px" class="cvsub">${md(destacada.etiqueta)}</div></div>` : ''}
    </div>
    <div class="cvstats">${cifras.map((c) => `<div class="cvstat"><div class="n">${esc(c.valor)}</div><div class="k">${md(c.etiqueta)}</div></div>`).join('')}</div>
    <footer class="cvft" style="margin-top:26px"><span>${esc(ESTUDIANTES)}<br>Grado ${esc(CR.grado)} · ${esc(CR.jornada)}</span><span style="text-align:right">Docente mentor<br>${esc(CR.docente_mentor)}</span></footer>
  </div>
</div>`) });

/* ================================ FICHA ================================= */
lamina('Ficha', '02 · Ficha del informe', {
  running: 'Ficha del documento',
  rail: secno('00') + raillab('Ficha<br>técnica') + note('Método', 'Toda cifra sale de los datos abiertos publicados en la plataforma BioMap Cartago y puede reproducirse con sus scripts.'),
  col: kicker('Documento') + hsec('Ficha del informe') + tb(['30%', '70%'], ['Campo', 'Descripción'], [
    ['Título', md(M.titulo)],
    ['Estudiantes responsables', CR.estudiantes.map(esc).join('<br>')],
    ['Grado y jornada', `${esc(CR.grado)} · ${esc(CR.jornada)}`],
    ['Docente mentor', esc(CR.docente_mentor)],
    ['Institución', `${esc(CR.institucion)} · ${esc(CR.ciudad)}`],
    ['Proyecto', `${esc(M.proyecto || 'BioMap Cartago')} · <a class="lnk" href="${esc(M.sitio)}">${esc(M.sitio)}</a>`],
    ['Destinatarios', (M.destinatarios || []).map(md).join('<br>')],
    ['Fecha', esc(M.fecha)],
    ['Alcance', md(M.alcance || '')],
    ['Normas de citación', 'APA, 7.ª edición'],
    ['Licencia', 'Texto y diagramas: CC BY-NC-SA 4.0. Los datos conservan la licencia de su fuente (ver Referencias).'],
  ]) + aire(10) + warn('Lo que este informe no es', md(C.aviso_alcance || 'No reemplaza los estudios oficiales de amenaza, el POT ni las mediciones de las autoridades ambientales. Son estimaciones para priorizar y deben verificarse en campo antes de ejecutar obras.')),
});

/* ================================ ÍNDICE (se completa al final) ========== */
const POS_INDICE = LAMINAS.length; n += 1; LAMINAS.push(null);

/* ================================ RESUMEN ================================ */
marcar('Resumen ejecutivo');
{
  const R = C.resumen || {};
  const parr = (R.parrafos || []).map((p) => par(md(p))).join('');
  const prior = R.prioridades || [];
  lamina('Resumen', 'Resumen ejecutivo', {
    running: 'Resumen ejecutivo',
    rail: secno('★') + raillab('Resumen') + note('En una frase', md(R.frase || (C.hallazgos[0] && C.hallazgos[0].tesis) || ''), 'o'),
    col: kicker('Resumen ejecutivo') + hsec('Lo que encontramos') + parr + aire(4) + cifrasFila(cifras, Math.min(4, cifras.length)),
  });
  lamina('Prioridades', 'Cinco prioridades', {
    running: 'Resumen ejecutivo',
    rail: secno('★') + raillab('Qué hacer<br>primero') + note('Detalle', 'Cada prioridad se desarrolla, con su fundamento legal y su indicador, en las recomendaciones por dependencia.', 't'),
    col: kicker('Resumen ejecutivo') + hsec('Cinco prioridades') + ol(prior.map(md), 'gap:10px'),
  });
}

/* ================================ MÉTODO ================================= */
marcar('Datos y método');
{
  const Me = C.metodo || {};
  lamina('Metodo', 'Datos y método', {
    running: 'Datos y método',
    rail: secno('01') + raillab('Datos<br>y método') + note('Rejilla común', '520 × 428 celdas de unos 28 m sobre Cartago, en EPSG:4326.', 't'),
    col: kicker('Datos y método') + hsec('Cómo se obtuvieron las cifras') + (Me.parrafos || []).map((p) => par(md(p))).join('') + aire(4) +
      figh('Figura 1', 'Flujo de trabajo, de los datos abiertos a las recomendaciones') + F.flujoMetodo({ ancho: 510 }),
  });
  const filasF = (Me.fuentes || []).map((f) => [md(f.dato), md(f.fuente), md(f.periodo || ''), md(f.resolucion || ''), md(f.licencia || '')]);
  paginar('fuentes', filasF, 2200, (r) => textoPlano(r.join(' ')).length + 80).forEach((g, i) => lamina(`Fuentes${i + 1}`, 'Fuentes de datos', {
    running: 'Datos y método',
    rail: secno('01') + raillab('Fuentes<br>de datos') + note('Licencias', 'Cada fuente conserva su licencia; la geometría de OpenStreetMap se publica bajo ODbL.', 't'),
    col: kicker('Datos y método') + hsec(i ? 'Fuentes de datos (continuación)' : 'Fuentes de datos') + tb(['20%', '30%', '17%', '13%', '20%'], ['Dato', 'Fuente', 'Periodo', 'Resolución', 'Licencia'], g),
  }));
}

/* ================================ HALLAZGOS ============================== */
marcar('Hallazgos');
let numFig = 2;
function figura(h) {
  const f = h.figura || {};
  const tit = esc(f.titulo || h.titulo);
  const Z = F.zonas();
  const tiene = (v) => Z.some((z) => Number.isFinite(+z[v]));
  try {
    if (f.tipo === 'ranking') return figh(`Figura ${numFig++}`, tit) + F.rankingFig();
    if (f.tipo === 'serie_anual' && f.archivo) {
      const S = F.leer(f.archivo);
      if (S.anual && S.anual[f.variable]) {
        const filas = S.anual.anio.map((a, i) => ({ a, v: S.anual[f.variable][i], p: S.anual.parcial && S.anual.parcial[i] })).filter((x) => !x.p && Number.isFinite(x.v));
        const anom = /anomal/.test(f.variable);
        return figh(`Figura ${numFig++}`, tit) + F.serie({ anios: filas.map((x) => x.a), series: [{ valores: filas.map((x) => x.v) }], tipo: anom ? 'barras' : 'linea', unidad: f.unidad || '', ancho: 510, alto: 200 });
      }
      if (Array.isArray(S.anios) && S.anios[0] && f.variable in S.anios[0]) {
        const ok = new Set(S.anios_confiables || S.anios.map((a) => a.anio));
        const anios = S.anios.map((a) => a.anio);
        const vars = Array.isArray(f.variables) && f.variables.length ? f.variables : [f.variable];
        const tonos = ['var(--vino)', 'var(--teal)', 'var(--tinta3)'];
        const series = vars.map((v, k) => ({ nombre: v, tono: tonos[k % 3], valores: S.anios.map((a) => (ok.has(a.anio) ? a[v] : null)) }));
        return figh(`Figura ${numFig++}`, tit) + F.serie({ anios, series, ancho: 510, alto: 200, unidad: f.unidad || '', marcas: [{ anio: 2013, texto: 'Landsat 8/9' }] }) +
          (vars.length > 1 ? F.leyenda(series.map((s, k) => [tonos[k % 3], esc((f.etiquetas && f.etiquetas[k]) || s.nombre)])) : '');
      }
    }
    if (f.tipo === 'mapa_zonas' && tiene(f.variable)) {
      const pct = /pct|porcent/.test(f.variable);
      return figh(`Figura ${numFig++}`, tit) + `<div style="display:flex;justify-content:center">${F.mapaZonas({ valor: (z) => +z[f.variable], decimales: f.decimales ?? (pct ? 0 : 1), unidad: f.unidad ?? (pct ? ' %' : ''), ancho: 510 })}</div>`;
    }
    if ((f.tipo === 'barras_zonas' || f.tipo === 'mapa_zonas') && tiene(f.variable)) {
      const pct = /pct|porcent/.test(f.variable);
      return figh(`Figura ${numFig++}`, tit) + F.barrasZonas({ valor: (z) => +z[f.variable], decimales: f.decimales ?? (pct ? 0 : 1), unidad: f.unidad ?? (pct ? ' %' : ''), tono: f.tono || '' });
    }
    if (f.tipo === 'bosque') return figh(`Figura ${numFig++}`, tit) + F.bosque({ ancho: 510 });
    if (f.tipo === 'tabla' && Array.isArray(f.filas) && Array.isArray(f.columnas)) {
      return figh(`Tabla`, tit) + tb(f.anchos || f.columnas.map(() => `${Math.round(100 / f.columnas.length)}%`), f.columnas.map(esc), f.filas.map((r) => r.map(md)));
    }
  } catch (e) { console.warn(`Figura de ${h.id} omitida: ${e.message}`); }
  return '';
}

// detalle para especialistas, en letra pequeña al final del hallazgo
const notaTecnica = (h) => (h.nota_tecnica ? `<p style="font-family:var(--sans);font-size:9.5px;line-height:1.5;color:var(--tinta3);border-top:1px solid var(--filete);padding-top:6px"><strong style="color:var(--tinta2)">Nota técnica.</strong> ${md(h.nota_tecnica)}</p>` : '');

C.hallazgos.forEach((h, i) => {
  const cif = (h.cifras || []).slice(0, 3);
  const fig = figura(h);
  const cuerpo = (h.parrafos || []).map((p) => par(md(p)));
  // la lámina principal lleva tesis, cifras y figura; el texto va detrás o en una lámina de continuación
  // capacidad de texto según el alto de la figura de esa lámina
  const tipoFig = (h.figura || {}).tipo;
  const base = !fig ? 2300 : tipoFig === 'mapa_zonas' ? 900 : tipoFig === 'ranking' || tipoFig === 'tabla' ? 1100 : 1400;
  const cap = base * (PAG[`h${i}`] || 1);
  let usado = 0; const aqui = [], resto = [];
  cuerpo.forEach((b) => { const L = textoPlano(b).length; (usado + L <= cap && !resto.length ? aqui : resto).push(b); if (!resto.length) usado += L; });
  const rail = secno(String(i + 1).padStart(2, '0')) + raillab(`Hallazgo<br>${String(i + 1).padStart(2, '0')}`) +
    (h.implicacion ? note('Implicación', md(h.implicacion), 'o') : '');
  lamina(`Hallazgo${i + 1}`, `Hallazgo ${i + 1}`, {
    running: 'Hallazgos',
    rail,
    col: kicker(`Hallazgo ${String(i + 1).padStart(2, '0')}`) + hsec(md(h.titulo)) + lead(md(h.tesis)) +
      (cif.length ? cifrasFila(cif, cif.length) : '') +
      fig + aqui.join('') + (resto.length ? '' : (h.incertidumbre ? warn('Qué tan seguro es este dato', md(h.incertidumbre), 't') : '') + notaTecnica(h)),
  });
  if (resto.length) {
    lamina(`Hallazgo${i + 1}b`, `Hallazgo ${i + 1} (cont.)`, {
      running: 'Hallazgos',
      rail: secno(String(i + 1).padStart(2, '0')) + raillab(`Hallazgo<br>${String(i + 1).padStart(2, '0')}`),
      col: kicker(`Hallazgo ${String(i + 1).padStart(2, '0')} · continuación`) + resto.join('') + (h.incertidumbre ? warn('Qué tan seguro es este dato', md(h.incertidumbre), 't') : '') + notaTecnica(h),
    });
  }
});

/* ================================ PRIORIZACIÓN =========================== */
marcar('Priorización de zonas');
{
  const Pz = C.priorizacion || {};
  lamina('Priorizacion', 'Priorización de zonas', {
    running: 'Priorización',
    rail: secno('P') + raillab('Dónde<br>intervenir<br>primero') + note('Sensibilidad', '*Rango: puestos que ocupa la zona al cambiar de variante de criterio o al quitar uno a la vez.', 't'),
    col: kicker('Priorización') + hsec('¿Dónde intervenir primero?') + (Pz.parrafos || []).map((p) => par(md(p))).join('') + aire(4) +
      figh(`Figura ${numFig++}`, 'Índice de prioridad por zona y aporte de cada criterio') + F.rankingFig(),
  });
}

/* ================================ INTERVENCIONES ========================= */
{
  const Iv = C.intervenciones || {};
  lamina('Intervenciones', 'Intervenciones y temperatura de superficie', {
    running: 'Priorización',
    rail: secno('S') + raillab('Simulador') + note('Asociación, no causalidad', 'Los coeficientes de Cartago comparan lugares distintos de la ciudad; no miden el antes y el después de una obra.', 'o'),
    col: kicker('Simulador calibrado') + hsec(md(Iv.titulo || 'Intervenciones asociadas a menor temperatura de superficie')) + (Iv.parrafos || []).map((p) => par(md(p))).join('') + aire(4) +
      figh(`Figura ${numFig++}`, 'Cambio de temperatura superficial por cada 10 puntos porcentuales del área intervenida') + F.bosque({ ancho: 510 }),
  });
}

/* ================================ RECOMENDACIONES ======================== */
marcar('Recomendaciones por dependencia');
const TIPO_F = { obligacion: 'Obligación de la entidad', obligacion_condicionada: 'Obligación condicionada', competencia: 'Competencia de la entidad', orientacion: 'Orientación técnica' };
C.recomendaciones.forEach((d, k) => {
  const bloques = d.acciones.map((a, j) => {
    const fu = a.fundamento || {};
    return `<div style="border-top:${j ? '1px solid var(--filete)' : '2px solid var(--tinta)'};padding-top:8px;display:flex;flex-direction:column;gap:4px">
      <div style="font-family:var(--sans);font-size:13px;font-weight:700;color:var(--tinta);line-height:1.3">${md(a.accion)}</div>
      <div style="font-family:var(--sans);font-size:9px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--vino)">Prioridad ${esc(a.prioridad)} · Plazo ${esc(a.plazo)}${a.zonas ? ` · ${md(a.zonas)}` : ''}</div>
      ${a.dato ? `<p style="font-size:12.5px;line-height:1.45;color:var(--tinta2)"><strong style="color:var(--tinta)">Por qué:</strong> ${md(a.dato)}</p>` : ''}
      ${fu.norma ? `<p style="font-size:12px;line-height:1.45;color:var(--tinta2)"><strong style="color:var(--teal)">${esc(TIPO_F[fu.tipo] || 'Fundamento')}:</strong> ${md(fu.norma)}${fu.articulo ? `, ${md(fu.articulo)}` : ''}${fu.cita ? ` — <em>«${md(fu.cita)}»</em>` : ''}</p>` : ''}
      ${a.indicador ? `<p style="font-size:12px;line-height:1.45;color:var(--tinta2)"><strong style="color:var(--tinta)">Cómo medir el avance:</strong> ${md(a.indicador)}</p>` : ''}
    </div>`;
  });
  const grupos = paginar(`r${k}`, bloques, 3200, (b) => textoPlano(b).length + 160);
  grupos.forEach((g, i) => lamina(`Recom${k + 1}${i ? String.fromCharCode(97 + i) : ''}`, `Recomendaciones · ${textoPlano(md(d.dependencia))}`, {
    running: 'Recomendaciones',
    rail: secno(String(k + 1).padStart(2, '0')) + raillab('Recomendaciones') +
      (i === 0 && d.nota ? note('Contexto', md(d.nota), 't') : '') +
      (!d.nombre_verificado ? note('Nombre', 'Denominación genérica: no se pudo verificar el nombre oficial vigente de la dependencia.', '') : ''),
    col: kicker(i ? 'Recomendaciones · continuación' : 'Recomendaciones para') + hsec(md(d.dependencia)) + `<div style="display:flex;flex-direction:column;gap:10px">${g.join('')}</div>`,
  }));
});

/* ================================ LIMITACIONES =========================== */
marcar('Limitaciones');
paginar('limitaciones', (C.limitaciones || []).map(md), 2600, (b) => textoPlano(b).length + 40).forEach((g, i) => lamina(`Limitaciones${i + 1}`, 'Limitaciones', {
  running: 'Limitaciones',
  rail: secno('!') + raillab('Limitaciones') + note('Antes de decidir', 'Contrastar con el POT, la CVC, el IDEAM y una visita técnica.', 'o'),
  col: kicker('Alcance') + hsec(i ? 'Lo que hay que saber (continuación)' : 'Lo que hay que saber antes de usar estas cifras') + ul(g),
}));

/* ================================ REFERENCIAS ============================ */
marcar('Referencias');
{
  const ref = (r) => `<p class="tiny" style="padding-left:18px;text-indent:-18px;font-size:11.5px;line-height:1.42">${md(r.apa)}</p>`;
  // contenido.json ya trae el orden APA 7 (mismo autor: «s. f.» antes que los años); no se reordena aquí
  const refs = (C.referencias || []).slice();
  paginar('referencias', refs.map(ref), 3600, (b) => textoPlano(b).length + 60).forEach((g, i) => lamina(`Referencias${i + 1}`, 'Referencias', {
    running: 'Referencias',
    rail: secno('··') + raillab('Referencias') + note('Estilo', 'Normas APA, 7.ª edición.', 't'),
    col: kicker('Documento') + hsec(i ? 'Referencias (continuación)' : 'Referencias') + g.join(''),
  }));
}

/* ================================ CIERRE ================================= */
lamina('Cierre', 'Colofón', {
  running: 'Colofón',
  rail: raillab('Colofón') + note('Elaboración', `Informe compuesto con el sistema editorial «Franja» de la ${esc(CR.institucion)}.`, 't'),
  col: `<div class="colof">
    <div class="kicker">${esc(CR.institucion)} · ${esc(CR.ciudad)}</div>
    <p class="q">${md(C.cierre || 'Los datos para decidir ya son abiertos; lo que falta es convertirlos en obras.')}</p>
    <div style="width:64px;height:2px;background:var(--vino)"></div>
    <p class="tiny" style="max-width:380px">Datos, mapas, simulador y descargas en <a class="lnk" href="${esc(M.sitio)}">${esc(M.sitio)}</a></p>
    <p class="src" style="margin-top:6px">${esc(ESTUDIANTES)} · Grado ${esc(CR.grado)} · ${esc(CR.jornada)}</p>
    <p class="src">Docente mentor · ${esc(CR.docente_mentor)}</p>
  </div>`,
});

/* ================================ ÍNDICE ================================= */
const filasIndice = indice.map(([p, a, b]) => [esc(p), a === b ? String(a).padStart(2, '0') : `${String(a).padStart(2, '0')} – ${String(b).padStart(2, '0')}`]);
LAMINAS[POS_INDICE] = { nombre: 'Indice', titulo: '03 · Índice', html: page({
  running: 'Índice del informe', num: 3, foot: PIE,
  rail: secno('00') + raillab('Índice'),
  col: kicker('Documento') + hsec('Qué contiene este informe') + tb(['72%', '28%'], ['Parte', 'Lámina'], filasIndice, { airy: true }),
}) };

export { LAMINAS };
