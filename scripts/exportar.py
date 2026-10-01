"""Exporta las capas publicadas a formatos abiertos para SIG y arma el catálogo de datos.

Entradas: datos/capas/<capa>.json (metadatos) y fuentes/rejilla/<capa>.npy (valores).
Salidas:
  datos/descargas/<capa>.tif   GeoTIFF optimizado para la nube (COG), float32, NaN como sin dato,
                               EPSG:4326, con descripción, unidad y fuente en las etiquetas.
  datos/catalogo.json          inventario de capas, series y vectores con su fuente y licencia
                               (lo lee la pestaña Datos Abiertos).

Uso: .venv/bin/python scripts/exportar.py
"""
from __future__ import annotations

import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comun  # noqa: E402

DESCARGAS = os.path.join(comun.DATOS, "descargas")
os.makedirs(DESCARGAS, exist_ok=True)


def exportar_geotiff(nombre: str, meta: dict) -> str | None:
    import rasterio
    ruta_npy = os.path.join(comun.REJILLA_NPY, f"{nombre}.npy")
    if not os.path.exists(ruta_npy):
        print(f"  ! {nombre}: falta {ruta_npy}; se omite el GeoTIFF")
        return None
    v = np.load(ruta_npy).astype("float32")
    destino = os.path.join(DESCARGAS, f"{nombre}.tif")
    perfil = dict(
        driver="COG", width=comun.ANCHO, height=comun.ALTO, count=1, dtype="float32",
        crs=comun.CRS, transform=comun.transformacion(), nodata=float("nan"),
        compress="DEFLATE", predictor=3, blocksize=256,
    )
    fuente = meta.get("fuente") or {}
    with rasterio.open(destino, "w", **perfil) as dst:
        dst.write(v, 1)
        dst.set_band_description(1, meta.get("titulo", nombre))
        dst.update_tags(
            TITULO=meta.get("titulo", ""), UNIDAD=meta.get("unidad", ""), PERIODO=str(meta.get("periodo", "")),
            FUENTE=fuente.get("nombre", ""), FUENTE_URL=fuente.get("url", ""), LICENCIA=fuente.get("licencia", ""),
            CITA=fuente.get("cita", ""), PRODUCTOR="BioMap Cartago", FECHA_PROCESO=meta.get("fecha_proceso", ""),
        )
        dst.update_tags(1, unidad=meta.get("unidad", ""))
    return destino


def main():
    capas = []
    for ruta in sorted(glob.glob(os.path.join(comun.CAPAS, "*.json"))):
        meta = json.load(open(ruta, encoding="utf-8"))
        nombre = meta.get("nombre") or os.path.splitext(os.path.basename(ruta))[0]
        tif = exportar_geotiff(nombre, meta)
        fuente = meta.get("fuente") or {}
        capas.append({
            "id": nombre, "titulo": meta.get("titulo"), "descripcion": meta.get("descripcion"),
            "unidad": meta.get("unidad"), "periodo": meta.get("periodo"),
            "resolucion_original_m": meta.get("resolucion_original_m"),
            "fuente": fuente, "geotiff": os.path.relpath(tif, comun.DATOS) if tif else None,
            "png": f"capas/{nombre}.png", "metadatos": f"capas/{nombre}.json",
            "tamano_tif_kb": round(os.path.getsize(tif) / 1024) if tif else None,
        })
        print(f"  ✓ {nombre}: {capas[-1]['tamano_tif_kb']} KB")

    def inventario(carpeta, patron):
        salida = []
        for ruta in sorted(glob.glob(os.path.join(comun.DATOS, carpeta, patron))):
            item = {"archivo": os.path.relpath(ruta, comun.DATOS), "tamano_kb": round(os.path.getsize(ruta) / 1024)}
            try:
                obj = json.load(open(ruta, encoding="utf-8"))
                meta = obj.get("metadata") or obj
                item["titulo"] = meta.get("titulo") or meta.get("title")
                f = meta.get("fuente") or meta.get("fuentes")
                if isinstance(f, dict):
                    item["fuente"] = {k: f.get(k) for k in ("nombre", "url", "licencia", "cita") if f.get(k)}
                elif isinstance(f, list):
                    item["fuente"] = [{k: x.get(k) for k in ("nombre", "url", "licencia") if isinstance(x, dict) and x.get(k)} for x in f]
            except Exception as e:  # el inventario no debe romperse por un archivo
                item["nota"] = f"no se pudo leer: {e}"
            salida.append(item)
        return salida

    catalogo = {
        "titulo": "Catálogo de datos abiertos de BioMap Cartago",
        "rejilla": {"crs": comun.CRS, "oeste": comun.OESTE, "este": comun.ESTE, "sur": comun.SUR, "norte": comun.NORTE,
                    "res_grados": comun.RES, "res_m_aprox": 27.7, "ancho": comun.ANCHO, "alto": comun.ALTO},
        "capas": capas,
        "series": inventario("series", "*.json"),
        "vectores": inventario("vectores", "*.geojson"),
        "tablas": inventario("", "*.json"),
    }
    comun.guardar_json(os.path.join(comun.DATOS, "catalogo.json"), catalogo)
    print(f"catálogo: {len(capas)} capas, {len(catalogo['series'])} series, {len(catalogo['vectores'])} vectores")


if __name__ == "__main__":
    main()
