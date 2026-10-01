/**
 * Sistema editorial «Franja» — informes institucionales
 * I.E. Sor María Juliana · Cartago, Valle del Cauca
 *
 * Los COLORES y las TIPOGRAFÍAS no se declaran aquí: se leen de franja.css,
 * que genera build-tokens.mjs a partir de tokens.json. Este archivo solo
 * aporta la forma —maquetación y componentes— y el andamiaje del artboard.
 *
 * Si un color se ve mal, se corrige en tokens.json y se regenera. Nunca aquí.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));

// Fuentes locales (SIL OFL, carpeta fuentes/): la impresión no depende de la red.
const ff = (fam, file, w, st = 'normal') =>
  `@font-face{font-family:"${fam}";src:url("fuentes/${file}");font-weight:${w};font-style:${st};font-display:block}`;
export const FONTS = '<style>' + [
  ff('Bricolage Grotesque', 'BricolageGrotesque-Regular.otf', 400),
  ff('Bricolage Grotesque', 'BricolageGrotesque-SemiBold.otf', 600),
  ff('Bricolage Grotesque', 'BricolageGrotesque-Bold.otf', 700),
  ff('Bricolage Grotesque', 'BricolageGrotesque-ExtraBold.otf', 800),
  ff('Newsreader', 'Newsreader16pt-Regular.ttf', 400),
  ff('Newsreader', 'Newsreader16pt-Italic.ttf', 400, 'italic'),
  ff('Newsreader', 'Newsreader16pt-SemiBold.ttf', 600),
  ff('Newsreader', 'Newsreader16pt-SemiBoldItalic.ttf', 600, 'italic'),
  ff('Newsreader', 'Newsreader16pt-Bold.ttf', 700),
  ff('Newsreader', 'Newsreader16pt-BoldItalic.ttf', 700, 'italic'),
].join('') + '</style>';

// tokens generados + forma de los componentes
export const CSS =
  fs.readFileSync(path.join(AQUI, 'franja.css'), 'utf8') +
  '\n' +
  fs.readFileSync(path.join(AQUI, 'componentes.css'), 'utf8');

const HEAD = `<!doctype html>
<html>
<head>
  <meta charset="utf-8">
</head>
<body>
<x-dc>
<helmet>
  ${FONTS}
  <style>${CSS}</style>
</helmet>`;

const TAIL = `</x-dc>
</body>
</html>
`;

export function raw(inner) {
  return `${HEAD}\n${inner}\n${TAIL}`;
}

// Encabezado de las láminas interiores (Franja lo trae fijo para la I.E.; aquí es configurable).
export let ENCABEZADO = 'I.E. Sor María Juliana <em>·</em> Cartago, Valle del Cauca';
export const fijarEncabezado = (t) => { ENCABEZADO = t; };

export function page({ running, rail, col, num, foot }) {
  return raw(`<div class="pg">
  <header class="rh">
    <span>${ENCABEZADO}</span>
    <span>${running}</span>
  </header>
  <div class="bd">
    <aside class="rail">${rail}</aside>
    <main class="col">${col}</main>
  </div>
  <footer class="ft">
    <span>${foot || 'Informe de logros ConectaTE <em>·</em> 2026'}</span>
    <span class="pn">${String(num).padStart(2, '0')}</span>
  </footer>
</div>`);
}

// ---------- bloques heredados ----------
export const secno = (n) => `<div class="secno">${n}</div>`;
export const raillab = (t) => `<div class="raillab">${t}</div>`;
export const note = (title, body, tone = '') =>
  `<div class="note ${tone}"><strong>${title}</strong>${body}</div>`;
export const kicker = (t) => `<div class="kicker">${t}</div>`;
export const hsec = (t) => `<h1 class="h-sec">${t}</h1>`;
export const lead = (t) => `<p class="lead">${t}</p>`;
export const par = (t) => `<p>${t}</p>`;
export const tiny = (t) => `<p class="tiny">${t}</p>`;
export const sub = (t, n) =>
  `<h2 class="sub">${n ? `<span>${n}</span>&nbsp;&nbsp;` : ''}${t}</h2>`;
export const stmt = (t) => `<div class="stmt">${t}</div>`;
export const src = (t) => `<div class="src">${t}</div>`;
export const ul = (items, tone = '', style = '') =>
  `<ul class="ul ${tone}" style="${style}">${items.map((i) => `<li><span>${i}</span></li>`).join('')}</ul>`;
export const ol = (items, style = '') =>
  `<ol class="ol" style="${style}">${items.map((i) => `<li><span>${i}</span></li>`).join('')}</ol>`;

export function tb(cols, head, rows, opts = {}) {
  const cls = `tb${opts.num ? ' num' : ''}${opts.airy ? ' airy' : ''}`;
  return `<table class="${cls}">
<colgroup>${cols.map((c) => `<col style="width:${c}">`).join('')}</colgroup>
<thead><tr>${head.map((h) => `<th>${h}</th>`).join('')}</tr></thead>
<tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody>
</table>`;
}

export const figh = (lab, title) =>
  `<div class="figh"><span class="figlab">${lab}</span><span class="figtit">${title}</span></div>`;

// ---------- bloques nuevos ----------

// Marcas de procedencia
export const FB = '<span class="mk f">FB</span>';
export const DOC = '<span class="mk d">DOC</span>';
export const MEM = '<span class="mk m">MEM</span>';

export const stat = (n, k, tone = '') =>
  `<div class="stat"><div class="n ${tone}">${n}</div><div class="k">${k}</div></div>`;

export const statrow = (items, cols = 3, style = '') =>
  `<div class="statrow" style="grid-template-columns:repeat(${cols},minmax(0,1fr));${style}">${items.join('')}</div>`;

export function bars(rows, max, tone = '') {
  const body = rows
    .map(([lb, v]) => {
      const pct = Math.round((v / max) * 100);
      return `<div class="bar"><span class="lb">${lb}</span><span class="tr"><span class="fl ${tone}" style="width:${pct}%"></span></span><span class="vl">${v}</span></div>`;
    })
    .join('');
  return `<div class="bars">${body}</div>`;
}

export const team = (nm, ln, tone = '') =>
  `<div class="team ${tone}"><div class="nm">${nm}</div><div class="ln">${ln}</div></div>`;
export const teams = (items) => `<div class="teams">${items.join('')}</div>`;

export const tlitem = (dt, tt, dd) =>
  `<div class="it"><div class="dt">${dt}</div><div class="bx"><div class="tt">${tt}</div><div class="dd">${dd}</div></div></div>`;
export const timeline = (items) => `<div class="tl">${items.join('')}</div>`;

export const warn = (t, b, tone = '') =>
  `<div class="warn ${tone}"><div class="wt">${t}</div><div class="wb">${b}</div></div>`;
