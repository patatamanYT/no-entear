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
