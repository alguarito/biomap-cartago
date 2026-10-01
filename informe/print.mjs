/**
 * Prepara el HTML paginado para imprimir a PDF.
 *
 * Después:
 *   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
 *     --headless=new --disable-gpu --no-pdf-header-footer \
 *     --virtual-time-budget=30000 --print-to-pdf=informe.pdf \
 *     "file://$PWD/_print.html"
 *
 * Chrome incrusta las fuentes y el texto queda buscable.
 */
import fs from 'node:fs';
import { CSS, FONTS } from './lib.mjs';
import * as I from './informe.mjs';

// El título del PDF: de INFORME si existe, o de TITULO, o uno genérico.
const TITULO = I.TITULO
  ?? (I.INFORME ? I.INFORME.titulo.join(' ') : 'Documento institucional');

const orden = JSON.parse(fs.readFileSync('canvas.json', 'utf8')).artboards.map(a => a.file);

const PAGINACION = `
@page{size:794px 1123px;margin:0}
html,body{margin:0;padding:0;background:#fff}
*{-webkit-print-color-adjust:exact !important;print-color-adjust:exact !important}
.pg,.cover{break-after:page;page-break-after:always;overflow:hidden}
.pg:last-child,.cover:last-child{break-after:auto;page-break-after:auto}
`;

let out = `<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>${TITULO}</title>
${FONTS}<style>${CSS}${PAGINACION}</style></head><body>`;
for (const f of orden) {
  const s = fs.readFileSync(f, 'utf8');
  out += s.split('</helmet>')[1].split('</x-dc>')[0];
}
out += `</body></html>`;
fs.writeFileSync('_print.html', out);
console.log(`_print.html listo — ${orden.length} láminas`);
