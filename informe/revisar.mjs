/**
 * Detector de desbordes.
 *
 * Las láminas tienen alto FIJO. Si el contenido de la columna se pasa, el
 * texto se monta sobre el pie y se corta —sin que nada avise—. Este script
 * arma una página de prueba que mide `.col` y `.rail` en cada lámina.
 *
 * Uso: node revisar.mjs  →  abra revisar.html; el TÍTULO de la pestaña dice
 * si todas caben o cuáles se desbordan y por cuántos píxeles.
 */
import fs from 'node:fs';
import { CSS, FONTS } from './lib.mjs';

const orden = JSON.parse(fs.readFileSync('canvas.json', 'utf8')).artboards.map(a => a.file);

let out = `<!doctype html><meta charset="utf-8">${FONTS}<style>${CSS}
body{background:#555;padding:34px;display:flex;flex-wrap:wrap;gap:36px;justify-content:center}
.wrap{position:relative}.cap{position:absolute;top:-20px;left:0;color:#fff;font:600 12px sans-serif}
.frame{width:794px;height:1123px;overflow:hidden;outline:2px solid #e11}
</style>`;
for (const f of orden) {
  const s = fs.readFileSync(f, 'utf8');
  out += `<div class="wrap"><div class="cap">${f}</div><div class="frame" data-f="${f}">${
    s.split('</helmet>')[1].split('</x-dc>')[0]}</div></div>`;
}
out += `<script>
window.addEventListener('load',()=>{setTimeout(()=>{
  const mal=[];
  document.querySelectorAll('.frame').forEach(fr=>{
    const col=fr.querySelector('.col'), rail=fr.querySelector('.rail');
    let o=0;
    if(col)  o=Math.max(o, col.scrollHeight-col.clientHeight);
    if(rail) o=Math.max(o, rail.scrollHeight-rail.clientHeight);
    if(o>1) mal.push(fr.dataset.f.replace('.dc.html','')+' +'+Math.round(o)+'px');
  });
  document.title = mal.length ? ('DESBORDA :: '+mal.join(' | ')) : 'OK · todas las laminas caben';
},2000);});
</script>`;
fs.writeFileSync('revisar.html', out);
console.log('revisar.html listo — ábralo y lea el título de la pestaña');
