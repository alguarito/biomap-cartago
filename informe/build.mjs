/**
 * Arma las láminas y el canvas.json.
 *
 * Acepta dos formas de informe.mjs:
 *   · un arreglo `LAMINAS` de { nombre, titulo, html }  — para documentos largos
 *   · exports con nombre más un `ORDEN`                 — para informes cortos
 */
import fs from 'node:fs';
import * as I from './informe.mjs';

const lista = I.LAMINAS
  ?? (I.ORDEN ?? []).map(([nombre, html, titulo]) => ({ nombre, html, titulo }));

if (!lista.length) throw new Error('informe.mjs no exporta LAMINAS ni ORDEN');

const W = 794, H = 1123, GAPX = 92, GAPY = 160, PORFILA = 6;

const artboards = lista.map(({ nombre, html, titulo }, i) => {
  if (typeof html !== 'string') throw new Error(`Lámina sin contenido: ${nombre}`);
  fs.writeFileSync(`${nombre}.dc.html`, html);
  return {
    file: `${nombre}.dc.html`, title: titulo,
    x: (i % PORFILA) * (W + GAPX),
    y: Math.floor(i / PORFILA) * (H + GAPY),
    w: W, h: H, print: 'fixed',
  };
});

fs.writeFileSync('canvas.json', JSON.stringify({ artboards, launch: { view: 'canvas' } }, null, 2));
console.log(`${artboards.length} láminas + canvas.json`);
