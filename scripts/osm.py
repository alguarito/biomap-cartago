"""Regenera js/datos-osm.js a partir de una respuesta de Overpass (OpenStreetMap, ODbL).

Uso:
  1. Descargar la respuesta JSON de esta consulta en https://overpass-turbo.eu
     (Exportar → datos sin procesar) o con POST a https://overpass-api.de/api/interpreter,
     y guardarla como scripts/osm-crudo.json:

     [out:json][timeout:90];
     (relation(id:13993431,13993432,13993433,13993434,13993435,13993436,13993437,13305920,10817533,1460512);
      way(id:749764338,1126843631,558284606,677173687,28243653,525980782);
      way["name"~"^(Variante Cartago|Vía Cartago Zaragoza|Vía Zaragoza Cartago|Vía Cerritos Cartago|Vía Cartago Alcala|Troncal de Occidente|Calle 10)$"](4.68,-75.98,4.80,-75.85);
      way["name"="Carrera 4"]["highway"="secondary"](4.70,-75.98,4.80,-75.85););
     out geom;

  2. python3 scripts/osm.py
"""
import json, math
import os
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(RAIZ, 'scripts', 'osm-crudo.json')))
E = {e['type'][0]+str(e['id']): e for e in d['elements']}
LAT0 = 4.7464
def m(p): return ((p[1]+75.9117)*111320*math.cos(math.radians(LAT0)), (p[0]-LAT0)*110574)
def dp(pts, tol):
    if len(pts) < 3: return pts
    a, b = m(pts[0]), m(pts[-1]); dmax, idx = 0, 0
    for i in range(1, len(pts)-1):
        p = m(pts[i]); dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy)
        dd = math.hypot(p[0]-a[0], p[1]-a[1]) if L == 0 else abs(dy*(p[0]-a[0]) - dx*(p[1]-a[1]))/L
        if dd > dmax: dmax, idx = dd, i
    if dmax > tol: return dp(pts[:idx+1], tol)[:-1] + dp(pts[idx:], tol)
    return [pts[0], pts[-1]]
def geom(w): return [(round(g['lat'],5), round(g['lon'],5)) for g in w['geometry']]
def stitch(segs):
    segs = [list(s) for s in segs]; rings = []
    while segs:
        ring = segs.pop(0)
        while ring[0] != ring[-1] and segs:
            for i, s in enumerate(segs):
                if s[0] == ring[-1]: ring += s[1:]; break
                if s[-1] == ring[-1]: ring += s[::-1][1:]; break
                if s[-1] == ring[0]: ring = s + ring[1:]; break
                if s[0] == ring[0]: ring = s[::-1] + ring[1:]; break
            else: break
            segs.pop(i)
        rings.append(ring)
    return rings
def rel_rings(rid, tol):
    r = E['r'+str(rid)]
    segs = [[(round(g['lat'],5), round(g['lon'],5)) for g in mb['geometry']] for mb in r['members'] if mb['type']=='way' and mb.get('role') in ('outer','') and 'geometry' in mb]
    rings = stitch(segs)
    rings.sort(key=len, reverse=True)
    return [dp(x, tol)[:-1] for x in rings if x[0]==x[-1]], r['tags']
out = {'comunas': [], 'licencia': '© OpenStreetMap contributors, ODbL 1.0'}
for i, rid in enumerate(range(13993431, 13993438), 1):
    rings, tags = rel_rings(rid, 5)
    out['comunas'].append({'id': 'c%d' % i, 'nombre': tags.get('name'), 'osm': rid, 'anillo': rings[0], 'extra': len(rings)-1})
cab, _ = rel_rings(13305920, 6); out['cabecera'] = cab[0]
mun, _ = rel_rings(1460512, 25); out['municipio'] = mun[0]
pb, t = rel_rings(10817533, 2); out['parque_bolivar'] = pb[0]
out['parque_salud'] = dp(geom(E['w677173687']), 2)[:-1]
out['pista'] = geom(E['w28243653']); out['aerodromo'] = dp(geom(E['w525980782']), 5)[:-1]
S, N, W, Ea = 4.688, 4.795, -75.985, -75.855
def clip(pts):
    keep = [p for p in pts if S-0.01 <= p[0] <= N+0.01 and W-0.01 <= p[1] <= Ea+0.01]
    return keep
# ríos: unir La Vieja (dos tramos)
lv = stitch([geom(E['w1126843631']), geom(E['w749764338'])])
lv = max(lv, key=len)
out['rio_la_vieja'] = dp(clip(lv), 8)
out['rio_cauca'] = dp(clip(geom(E['w558284606'])), 10)
# vías
grupos = {'Carrera 4': [], 'Variante Cartago': [], 'Vía a Zaragoza': [], 'Vía a Cerritos (Pereira)': [], 'Vía a Alcalá': [], 'Troncal de Occidente': []}
alias = {'Vía Cartago Zaragoza':'Vía a Zaragoza','Vía Zaragoza Cartago':'Vía a Zaragoza','Calle 10':'Vía a Zaragoza','Vía Cerritos Cartago':'Vía a Cerritos (Pereira)','Vía Cartago Alcala':'Vía a Alcalá'}
for e in d['elements']:
    if e['type']!='way' or 'tags' not in e or 'highway' not in e['tags']: continue
    n = alias.get(e['tags'].get('name'), e['tags'].get('name'))
    if n in grupos: grupos[n].append(geom(e))
vias = []
for n, segs in grupos.items():
    partes = [dp(clip(s), 8) for s in stitch(segs)]
    partes = [p for p in partes if len(p) > 1]
    vias.append({'nombre': n, 'partes': partes, 'nseg': len(segs)})
out['vias'] = vias
for c in out['comunas']: print(c['nombre'], len(c['anillo']), 'anillos extra', c['extra'])
print('cabecera', len(out['cabecera']), 'municipio', len(out['municipio']), 'lavieja', len(out['rio_la_vieja']), 'cauca', len(out['rio_cauca']))
for v in vias: print(v['nombre'], v['nseg'], [len(p) for p in v['partes']])
lats=[p[0] for c in out['comunas'] for p in c['anillo']]; lons=[p[1] for c in out['comunas'] for p in c['anillo']]
print('bbox comunas', min(lats), max(lats), min(lons), max(lons))
print('cab bbox', min(p[0] for p in out['cabecera']), max(p[0] for p in out['cabecera']), min(p[1] for p in out['cabecera']), max(p[1] for p in out['cabecera']))
js = '/* Geometría tomada de OpenStreetMap (© OpenStreetMap contributors, ODbL 1.0), descargada vía Overpass y simplificada (Douglas-Peucker, 2–25 m). Regenerar con scripts/osm.py. */\nwindow.BM_OSM = ' + json.dumps(out, separators=(',', ':'), ensure_ascii=False) + ';\n'
open(os.path.join(RAIZ, 'js', 'datos-osm.js'), 'w').write(js)
print('bytes', len(js))
