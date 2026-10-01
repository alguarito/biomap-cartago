/**
 * Genera el informe completo y lo publica en ../datos/informe/:
 *   1. arma las láminas (build.mjs) y busca desbordes con Chrome (revisar.mjs);
 *      si una lámina de texto corrido se desborda, reduce su capacidad en paginacion.json y repite;
 *   2. imprime el PDF (print.mjs + Chrome --print-to-pdf);
 *   3. escribe resultados.json para la pestaña «Resultados» con el mismo contenido.
 *
 * Uso: cd informe && node generar.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const DESTINO = path.join(AQUI, '..', 'datos', 'informe');
const PDF = 'BioMap_Cartago_Informe_Recomendaciones_2026.pdf';
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const node = (script) => execFileSync(process.execPath, [script], { cwd: AQUI, stdio: 'pipe' }).toString().trim();
const chrome = (args) => execFileSync(CHROME, ['--headless=new', '--disable-gpu', '--no-pdf-header-footer', ...args], { cwd: AQUI, stdio: ['ignore', 'pipe', 'ignore'], maxBuffer: 64 * 1024 * 1024 }).toString();

/* ---------- 1. armar y revisar desbordes ---------- */
const RUTA_PAG = path.join(AQUI, 'paginacion.json');
const pag = fs.existsSync(RUTA_PAG) ? JSON.parse(fs.readFileSync(RUTA_PAG, 'utf8')) : {};
// nombre de lámina → clave de paginación ajustable
const clave = (lam) => {
  let m;
  if ((m = lam.match(/^Recom(\d+)/))) return `r${+m[1] - 1}`;
  if ((m = lam.match(/^Hallazgo(\d+)$/))) return `h${+m[1] - 1}`;
  if (/^Fuentes/.test(lam)) return 'fuentes';
  if (/^Referencias/.test(lam)) return 'referencias';
  if (/^Limitaciones/.test(lam)) return 'limitaciones';
  return null;
};
let estado = '';
for (let vuelta = 1; vuelta <= 10; vuelta++) {
  fs.writeFileSync(RUTA_PAG, JSON.stringify(pag, null, 1));
  console.log(node('build.mjs'));
  node('revisar.mjs');
  const dom = chrome(['--virtual-time-budget=15000', '--dump-dom', `file://${path.join(AQUI, 'revisar.html')}`]);
  estado = (dom.match(/<title>([^<]*)<\/title>/) || [, 'sin título'])[1];
  console.log(`  vuelta ${vuelta}: ${estado}`);
  if (estado.startsWith('OK')) break;
  const desbordes = estado.replace('DESBORDA :: ', '').split(' | ').map((x) => x.split(' +')[0]);
  const fijos = desbordes.filter((l) => !clave(l));
  if (fijos.length) { console.error(`  ✗ láminas fijas desbordadas (hay que acortar el texto): ${fijos.join(', ')}`); }
  const ajustables = desbordes.filter((l) => clave(l));
  if (!ajustables.length) break;
  ajustables.forEach((l) => { const k = clave(l); pag[k] = Math.round((pag[k] || 1) * 0.84 * 100) / 100; });
}
if (!estado.startsWith('OK')) { console.error(`✗ El informe todavía se desborda: ${estado}`); process.exit(1); }

/* ---------- 2. imprimir ---------- */
console.log(node('print.mjs'));
fs.mkdirSync(DESTINO, { recursive: true });
chrome(['--virtual-time-budget=30000', `--print-to-pdf=${path.join(DESTINO, PDF)}`, `file://${path.join(AQUI, '_print.html')}`]);
const bytes = fs.statSync(path.join(DESTINO, PDF)).size;
const paginas = JSON.parse(fs.readFileSync(path.join(AQUI, 'canvas.json'), 'utf8')).artboards.length;
console.log(`✓ PDF: ${paginas} páginas, ${(bytes / 1048576).toFixed(1)} MB`);

/* ---------- 3. resultados.json para la interfaz ---------- */
const C = JSON.parse(fs.readFileSync(path.join(AQUI, process.env.CONTENIDO || 'contenido.json'), 'utf8'));
const CR = JSON.parse(fs.readFileSync(path.join(AQUI, 'creditos.json'), 'utf8'));
const resultados = {
  meta: {
    titulo: C.meta.titulo, subtitulo: C.meta.subtitulo, fecha: C.meta.fecha,
    destinatarios: C.meta.destinatarios,
    autor: `${CR.estudiantes.join(' y ')} (grado ${CR.grado}, ${CR.jornada.toLowerCase()}) · Docente mentor: ${CR.docente_mentor} · ${CR.institucion}`,
  },
  creditos: CR,
  tarjetas: C.tarjetas,
  hallazgos: C.hallazgos.map((h) => ({ id: h.id, titulo: h.titulo, tesis: h.tesis, implicacion: h.implicacion })),
  prioridades: (C.resumen && C.resumen.prioridades) || [],
  recomendaciones: C.recomendaciones.map((d) => ({
    dependencia: d.dependencia,
    acciones: d.acciones.map((a) => ({
      accion: a.accion, prioridad: a.prioridad, plazo: a.plazo, dato: a.dato, zonas: a.zonas,
      fundamento: a.fundamento ? { tipo: a.fundamento.tipo, norma: a.fundamento.norma, articulo: a.fundamento.articulo, cita: a.fundamento.cita } : null,
    })),
  })),
  aviso: C.aviso_alcance || 'Estimaciones a partir de datos abiertos para priorizar; antes de ejecutar obras deben contrastarse con el POT, la CVC, el IDEAM y una visita técnica.',
  pdf: { archivo: `informe/${PDF}`, paginas, tamano: `${(bytes / 1048576).toFixed(1).replace('.', ',')} MB`, version: String(Math.round(bytes / 1000)) },
  generado: new Date().toISOString().slice(0, 10),
};
fs.writeFileSync(path.join(DESTINO, 'resultados.json'), JSON.stringify(resultados, null, 1));
console.log(`✓ resultados.json: ${resultados.tarjetas.length} tarjetas, ${resultados.recomendaciones.length} dependencias`);
