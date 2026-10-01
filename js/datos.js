/* BioMap Cartago — acceso a los datos abiertos procesados (carpeta datos/).
   Cada capa ráster llega como datos/capas/<id>.png (valor en 16 bits: v = R*256 + G,
   v = 0 sin dato, valor = (v − 1) * escala + desplazamiento) y datos/capas/<id>.json
   con sus metadatos. Ver scripts/comun.py. */
'use strict';
(function () {
  const BM = (window.BM = window.BM || {});
  const VERSION_DATOS = '2';
  const url = (ruta) => `datos/${ruta}?v=${VERSION_DATOS}`;

  async function json(ruta) {
    const r = await fetch(url(ruta));
    if (!r.ok) throw new Error(`No se pudo leer ${ruta} (${r.status})`);
    return r.json();
  }
  BM.leerJSON = json;
  BM.leerJSONopcional = async (ruta) => { try { return await json(ruta); } catch { return null; } };

  function decodificarPNG(src, meta) {
    return new Promise((resolver, rechazar) => {
      const img = new Image();
      img.onload = () => {
        const cv = document.createElement('canvas');
        cv.width = img.naturalWidth; cv.height = img.naturalHeight;
        // sin suavizado ni gestión de color: se necesitan los bytes exactos
        const ctx = cv.getContext('2d', { willReadFrequently: true, colorSpace: 'srgb' });
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(img, 0, 0);
        const px = ctx.getImageData(0, 0, cv.width, cv.height).data;
        const n = cv.width * cv.height, val = new Float32Array(n);
        for (let k = 0; k < n; k++) {
          const v = px[4 * k] * 256 + px[4 * k + 1];
          val[k] = v === 0 ? NaN : (v - 1) * meta.escala + meta.desplazamiento;
        }
        resolver({ ancho: cv.width, alto: cv.height, valores: val });
      };
      img.onerror = () => rechazar(new Error(`No se pudo decodificar ${src}`));
      img.src = src;
    });
  }

  const cache = {};
  /** Carga una capa: { id, meta, ancho, alto, valores (Float32Array, NaN = sin dato) } */
  BM.cargarCapa = function (id) {
    if (!cache[id]) {
      cache[id] = (async () => {
        const meta = await json(`capas/${id}.json`);
        const d = await decodificarPNG(url(`capas/${id}.png`), meta);
        if (d.ancho !== meta.rejilla.ancho || d.alto !== meta.rejilla.alto) throw new Error(`Dimensiones inesperadas en ${id}`);
        return { id, meta, ...d };
      })();
      cache[id].catch(() => delete cache[id]);
    }
    return cache[id];
  };
  BM.capaCargada = (id) => cache[id];

  /** Límites Leaflet de la rejilla */
  BM.limitesRejilla = (meta) => [[meta.rejilla.sur, meta.rejilla.oeste], [meta.rejilla.norte, meta.rejilla.este]];

  /** Valor de la capa en (lat, lon), o null si cae fuera o sin dato */
  BM.valorEn = function (capa, lat, lon) {
    const g = capa.meta.rejilla;
    const i = Math.floor((lon - g.oeste) / g.res), j = Math.floor((g.norte - lat) / g.res);
    if (i < 0 || j < 0 || i >= capa.ancho || j >= capa.alto) return null;
    const v = capa.valores[j * capa.ancho + i];
    return Number.isFinite(v) ? v : null;
  };

  /** Promedio de la capa en un radio (m) alrededor de (lat, lon) */
  BM.promedioEn = function (capa, lat, lon, radio) {
    const g = capa.meta.rejilla;
    const rl = radio / 110574, rn = radio / (111320 * Math.cos((lat * Math.PI) / 180));
    let s = 0, n = 0;
    for (let la = lat - rl; la <= lat + rl; la += g.res) {
      for (let lo = lon - rn; lo <= lon + rn; lo += g.res) {
        if (((la - lat) / rl) ** 2 + ((lo - lon) / rn) ** 2 > 1) continue;
        const v = BM.valorEn(capa, la, lo);
        if (v !== null) { s += v; n++; }
      }
    }
    return n ? s / n : null;
  };

  /* ---------- color ---------- */
  const hex2rgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));

  /** Imagen coloreada (data URL) de una capa continua o por clases. */
  BM.colorearCapa = function (capa, estilo) {
    const cv = document.createElement('canvas');
    cv.width = capa.ancho; cv.height = capa.alto;
    const ctx = cv.getContext('2d');
    const img = ctx.createImageData(capa.ancho, capa.alto);
    const d = img.data, val = capa.valores;
    if (estilo.clases) {
      const tabla = {};
      estilo.clases.forEach((c) => (tabla[c.valor] = c.color ? hex2rgb(c.color) : null));
      for (let k = 0; k < val.length; k++) {
        const c = Number.isFinite(val[k]) ? tabla[Math.round(val[k])] : null;
        if (!c) continue;
        d[4 * k] = c[0]; d[4 * k + 1] = c[1]; d[4 * k + 2] = c[2]; d[4 * k + 3] = 255;
      }
    } else {
      const rgb = estilo.paleta.map(hex2rgb), [mn, mx] = estilo.rango, m = rgb.length - 1;
      for (let k = 0; k < val.length; k++) {
        const v = val[k];
        if (!Number.isFinite(v)) continue;
        if (estilo.ocultarBajo !== undefined && v < estilo.ocultarBajo) continue;
        const t = Math.max(0, Math.min(1, (v - mn) / (mx - mn))) * m;
        const i = Math.min(Math.floor(t), m - 1), f = t - i, a = rgb[i], b = rgb[i + 1];
        d[4 * k] = a[0] + (b[0] - a[0]) * f; d[4 * k + 1] = a[1] + (b[1] - a[1]) * f; d[4 * k + 2] = a[2] + (b[2] - a[2]) * f;
        d[4 * k + 3] = estilo.alfaPorValor ? Math.round(255 * Math.max(0.15, Math.min(1, t / m))) : 255;
      }
    }
    ctx.putImageData(img, 0, 0);
    return cv.toDataURL('image/png');
  };

  BM.colorPaleta = function (paleta, rango, v) {
    const rgb = paleta.map(hex2rgb), m = rgb.length - 1;
    const t = Math.max(0, Math.min(1, (v - rango[0]) / (rango[1] - rango[0]))) * m;
    const i = Math.min(Math.floor(t), m - 1), f = t - i, a = rgb[i], b = rgb[i + 1];
    return `rgb(${[0, 1, 2].map((c) => Math.round(a[c] + (b[c] - a[c]) * f)).join(',')})`;
  };
})();
