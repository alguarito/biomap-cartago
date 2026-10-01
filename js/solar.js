/* BioMap Cartago — radiación solar en cielo despejado.
   Posición solar con las fórmulas simplificadas del Almanaque Astronómico (precisión
   de ~0,01°, suficiente aquí) y modelo de cielo despejado de Haurwitz (1945):
   GHI = 1098 · cos z · exp(−0,057 / cos z) W/m². No considera nubes. */
'use strict';
(function () {
  const BM = (window.BM = window.BM || {});

  function cosZenit(fecha, lat, lon) {
    const rad = Math.PI / 180;
    const n = fecha.getTime() / 86400000 + 2440587.5 - 2451545.0;
    const L = (280.46 + 0.9856474 * n) % 360;
    const g = ((357.528 + 0.9856003 * n) % 360) * rad;
    const lam = (L + 1.915 * Math.sin(g) + 0.02 * Math.sin(2 * g)) * rad;
    const eps = (23.439 - 0.0000004 * n) * rad;
    const dec = Math.asin(Math.sin(eps) * Math.sin(lam));
    const ra = Math.atan2(Math.cos(eps) * Math.sin(lam), Math.cos(lam));
    const gmst = (((18.697374558 + 24.06570982441908 * n) % 24) + 24) % 24;
    const ha = (gmst * 15 + lon) * rad - ra;
    return Math.sin(lat * rad) * Math.sin(dec) + Math.cos(lat * rad) * Math.cos(dec) * Math.cos(ha);
  }
  const haurwitz = (cz) => (cz > 0.01 ? 1098 * cz * Math.exp(-0.057 / cz) : 0);

  /** { actual W/m², max W/m² del día, kwhDia kWh/m² } para la hora actual en Colombia (UTC−5). */
  BM.radiacion = function (lat, lon, ahora = new Date()) {
    const actual = haurwitz(cosZenit(ahora, lat, lon));
    const base = new Date(ahora.getTime() - 5 * 3600e3);
    base.setUTCHours(0, 0, 0, 0);
    const t0 = base.getTime() + 5 * 3600e3;
    let max = 0, energia = 0;
    for (let m = 0; m < 1440; m += 10) {
      const g = haurwitz(cosZenit(new Date(t0 + m * 60e3), lat, lon));
      if (g > max) max = g;
      energia += (g * 10) / 60;
    }
    return { actual, max, kwhDia: energia / 1000 };
  };
})();
