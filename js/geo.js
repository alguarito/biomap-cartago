/* BioMap Cartago — geometría de referencia (OpenStreetMap, ODbL) y utilidades. */
'use strict';
(function () {
  const BM = (window.BM = window.BM || {});
  const OSM = window.BM_OSM;

  BM.CENTRO = [4.7464, -75.9117];
  BM.LIMITES_NAV = [[4.660, -76.020], [4.825, -75.820]];

  BM.RIO = OSM.rio_la_vieja;
  BM.CAUCA = OSM.rio_cauca;
  BM.CABECERA = OSM.cabecera;

  BM.HITOS = [
    { id: 'bolivar', nombre: 'Parque Simón Bolívar', coord: [4.7497, -75.9132], zoom: 17 },
    // orilla urbana del río junto al Puente Bolívar (OSM no trae el trazado del malecón)
    { id: 'malecon', nombre: 'Malecón Río La Vieja', coord: [4.75774, -75.89882], zoom: 16 },
    { id: 'zaragoza', nombre: 'Variante Zaragoza', coord: [4.7154, -75.9191], zoom: 15 },
    { id: 'aeropuerto', nombre: 'Aeropuerto Santa Ana', coord: [4.7601, -75.9545], zoom: 15 },
    { id: 'salud', nombre: 'Parque La Salud', coord: [4.7403, -75.9141], zoom: 17 },
  ];

  /** Punto en polígono; anillo como [[lat, lon], ...] */
  BM.dentro = (lat, lon, anillo) => {
    let c = false;
    for (let i = 0, j = anillo.length - 1; i < anillo.length; j = i++) {
      const [yi, xi] = anillo[i], [yj, xj] = anillo[j];
      if (yi > lat !== yj > lat && lon < ((xj - xi) * (lat - yi)) / (yj - yi) + xi) c = !c;
    }
    return c;
  };

  /** Zonas de análisis: se reemplazan con datos/vectores/zonas.geojson al cargar los indicadores. */
  BM.ZONAS = OSM.comunas.map((c) => ({ id: c.id, nombre: c.nombre, anillos: [c.anillo], props: {} }));

  BM.definirZonas = function (geojson) {
    BM.ZONAS = geojson.features.map((f) => {
      const g = f.geometry;
      const poligonos = g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
      return {
        id: f.properties.id, nombre: f.properties.nombre, props: f.properties,
        anillos: poligonos.map((p) => p[0].map(([lon, lat]) => [lat, lon])),
      };
    });
  };

  BM.zonaEn = (lat, lon) => BM.ZONAS.find((z) => z.anillos.some((a) => BM.dentro(lat, lon, a))) || null;
})();
