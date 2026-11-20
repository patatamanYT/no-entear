# Reproducir el Reel

Requiere Python con Pillow y openpyxl, Tesseract CLI 0.7.0 o compatible y FFmpeg con H.264. Conserva la carpeta assets junto a src.

Descomprime santos_analisis_completo.zip y usa el directorio que contiene output/tablas.xlsx y output/v2/tablas_v2.xlsx.

```powershell
tsrct project create -p mi_reel.tsrct
python src/reel.py RUTA_AL_EJECUTABLE_TSRCT mi_reel.tsrct RUTA_A_SANTOS_ANALISIS
tsrct export -p mi_reel.tsrct --fps 30 --resolution 1080p --encoder-backend external-ffmpeg-command --ffmpeg-path RUTA_AL_EJECUTABLE_FFMPEG -o mi_reel.mp4
```

Las cifras se leen de las tablas del análisis. Los archivos de imagen y la tipografía son los mismos que contiene el proyecto editable entregado. Los créditos y el contexto de las fotos están en fuentes_fotos.csv.

## Versión 2

`reel.py` genera la versión 2 (santos_cronica_v2.tsrct / santos_cinematic_v2.mp4). Se probó con Tesseract 0.8.0 en Linux x86_64. En Linux, el renderizado necesita un driver Vulkan; sin GPU sirve Mesa lavapipe. En Linux se mide la tipografía con otra versión de Pillow, así que los textos centrados o alineados a la derecha pueden moverse hasta 4 px respecto a una reconstrucción en Windows. `tsrct preview --time` recibe segundos.

## Versión 3

`reel.py` genera la versión 3 (santos_cronica_v3.tsrct / santos_cinematic_v3.mp4). Al ejecutarse escribe en `assets/` cuatro PNG de degradado (`fundido_*.png`), que son los fundidos de las fotos.

Sin las tablas del análisis, `src/reel_sin_tablas.py` construye el mismo proyecto con los valores de la columna valor_exacto de verificacion_numeros.csv:

```bash
tsrct project create -p mi_reel.tsrct
python src/reel_sin_tablas.py RUTA_A_TSRCT mi_reel.tsrct
```

La escena 2 tarda más en renderizar que las demás, alrededor de 1.4 s por fotograma en CPU. La exportación completa tardó unos 3 minutos con Mesa lavapipe.
