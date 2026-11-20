"""Author the nine-scene Tesseract version of the Santos story."""
import argparse
import json
from pathlib import Path
import wave

from PIL import Image, ImageFont, ImageColor
from openpyxl import load_workbook
import subprocess

BASE = Path(__file__).resolve().parents[1]
EDITOR = BASE / "assets"
MEDIA = EDITOR
EASE = dict(type="cubicBezier", x1=.20, y1=.78, x2=.24, y2=1)

def run(cli, *args):
    p = subprocess.run([str(cli), *map(str,args)], capture_output=True, encoding="utf-8", errors="replace")
    if p.returncode:
        raise RuntimeError(p.stderr + p.stdout[-5000:])
    if p.stderr:
        print(p.stderr.strip())
    return json.loads(p.stdout)

def rgb(color):
    return [n/255 for n in ImageColor.getrgb(color)] + [1]

def fx(x=0, y=0, *, scale=(100,100), anchor=(0,0), rotation=0, opacity=100):
    return dict(position=[x,y], scale=list(scale), anchorPoint=list(anchor), rotation=rotation, opacity=opacity)

class Author:
    def __init__(self, media):
            self.media = media
            self.actions = []
            self.group = None
            self.duration = sum(TIMES)
            self.id = 0
            self.fonts = {}
            self.images = {}
            self.effect_id = 5000
            self.blurred = []

    def add(self, type_, name, transform=None, start=0, duration=None, grouped=True, **fields):
            self.id += 1
            action = dict(type=type_, compositionId="main", layerId=self.id, name=name,
                          activeRange={"start":start,"duration":self.duration-start if duration is None else duration},
                          insertIndex=0, **fields)
            if transform is not None:
                action["transform"] = transform
            if grouped and self.group is not None:
                action["parentLayerId"] = self.group
            self.actions.append(action)
            return self.id

    def keys(self, layer, prop, values, kind="float", easing=EASE):
            self.actions.append(dict(type="setFxPropertyKeyframes", compositionId="main",
               property=dict(layerId=layer,propertyType=prop), keyframes=[
                 {"id":f"{layer}-{prop}-{at}","layerTime":at,"easing":easing,
                  "value":{"type":kind,"value":value}} for at,value in values]))

    def rect(self,x,y,w,h,color,name,*,rounding=0,outline=None,delay=0,grow=0):
            item = dict(size=[w,h], fillColor=rgb(color),roundness=rounding)
            if outline:
                item.update(fillEnabled=False,strokeEnabled=True,strokeColor=rgb(outline),strokeWidth=4)
            layer = self.add("createFxRectLayer",name,fx(x,y),start=delay,rect=item)
            if grow:
                self.keys(layer,"scaleX",[(0,0),(grow,100)])
            return layer

    def framed(self,asset,x,y,w,h,focus,crop,*,frame_y=300,push=1.03,push_ms=1700):
        # Frame w×h clips the photo; crop scales it around focus (source px) placed at frame_y px from the frame top.
        width,height = self.images[asset]
        cx = w/2 + (width/2 - focus[0])*crop
        cy = frame_y + (height/2 - focus[1])*crop
        item = self.add("createFxImageLayer",asset,fx(x+w/2,y,anchor=(w/2,0)),
                        source=dict(assetId=asset,fit={"custom":{"scale":[crop,crop],"contentCenter":[cx,cy]}},
                                    sourceRect=dict(x=0,y=0,width=w,height=h)))
        self.keys(item,"scaleX",[(0,100),(push_ms,100*push)])
        self.keys(item,"scaleY",[(0,100),(push_ms,100*push)])
        self.grade(item)
        return item

    def picture(self,asset,x,y,w,h,delay=0, tilt=0, *, zoom=True, arrive=.98, end=1.017, settle=True):
        width,height = self.images[asset]
        sx,sy = 100*w/width,100*h/height
        item = self.add("createFxImageLayer",asset,fx(x+w/2,y+h/2,scale=(sx,sy),anchor=(width/2,height/2),rotation=tilt),
                        start=delay,source=dict(assetId=asset,fit="none"))
        if zoom:
            mid = [(430,1)] if settle else []
            self.keys(item,"scaleX",[(t,sx*f) for t,f in [(0,arrive),*mid,(self.duration-delay,end)]])
            self.keys(item,"scaleY",[(t,sy*f) for t,f in [(0,arrive),*mid,(self.duration-delay,end)]])
        self.grade(item)
        return item

    def effect(self, layer, **effect):
        self.effect_id += 1
        self.actions.append(dict(type="addFxLayerEffect",compositionId="main",layerId=layer,
                                 effectId=self.effect_id,effect=effect))

    def grade(self, layer):
        # Un solo tratamiento para todas las fotos: menos saturación, más cuerpo y viñeta suave.
        self.effect(layer,type="primaryGrade",semanticVersion=1,temperature=0,tint=0,exposure=0,
                    contrast=.08,highlights=-.06,shadows=0,whites=0,blacks=-.02,
                    saturation=-.16,vibrance=0)
        self.effect(layer,type="vignette",amount=.35,feather=.8,radius=.9)

def load_data(root):
    v1 = load_workbook(root / "output/tablas.xlsx", read_only=True, data_only=True)
    v2 = load_workbook(root / "output/v2/tablas_v2.xlsx", read_only=True, data_only=True)
    blocks = v1["3_xpts_por_bloque"]
    games = list(v1["3_xpts_por_partido"].values)[1:]
    events = list(v1["5_eventos_por_partido"].values)[1:]
    shots = v1["2_bloques_medias_IC"]
    model = v2["D_sobre_rendimiento"]
    racha = [row for row in games if blocks["B2"].value < row[0] <= blocks["B2"].value + blocks["B3"].value]
    racha_eventos = [events[row[0] - 1] for row in racha]
    # The score difference isolates scored penalties after subtracting own goals.
    def goals(score):
        return int(score.split("-")[0])

    d = dict(
        games=[(row[0], {0: "P", 1: "E", 3: "G"}[row[3]]) for row in games],
        spans=[blocks[f"A{i}"].value for i in (2, 3, 5)],
        start=blocks["C2"].value, run=blocks["C3"].value,
        start_n=blocks["B2"].value, run_n=blocks["B3"].value,
        expected=blocks["D2"].value, bounce=v1["8_descomposicion_salto"]["C3"].value,
        goals=v1["0_anclas"]["B6"].value,
        pens=sum(goals(row[2]) - goals(row[8]) - row[7] for row in racha_eventos),
        reds=sum(row[4].startswith("S") for row in racha_eventos),
        clean=v1["5_eventos_por_bloque"]["G3"].value,
        without=v1["5_eventos_por_bloque"]["C3"].value,
        shots_start=shots["D30"].value, shots_run=shots["D31"].value,
        keeper_start=model["E5"].value, keeper_run=model["E10"].value,
        placement=model["E9"].value, juarez=racha[0][2],
        juarez_date=v1["5_fuerza_rival_partido"]["B9"].value.date().isoformat(),
        atlante_date=v1["5_fuerza_rival_partido"]["B17"].value.date().isoformat(),
        improve=v1["8_descomposicion_salto"]["C5"].value,
    )
    assert shots["A30"].value == shots["A31"].value == "Tiros a puerta"
    assert model["B5"].value == model["B10"].value == "paradas_Acevedo"
    v1.close()
    v2.close()
    return d

IVORY = "#F1EDE1"
INK = "#1B211D"
FOREST = "#243E33"
PITCH = "#355D4C"
SAGE = "#B6C4AB"
GRAY = "#535A51"
RULE = "#A9AD9F"
BROWN = "#80583A"
W, H = 1080, 1920
FOOT = "FotMob/Opta · J1–J16 · análisis propio"
FONT = {
    "head": ("BarlowCondensed-SemiBold.ttf", "Barlow Condensed SemiBold", "Regular"),
    "number": ("BarlowCondensed-Bold.ttf", "Barlow Condensed", "Bold"),
    "body": ("BarlowCondensed-SemiBold.ttf", "Barlow Condensed SemiBold", "Regular"),
}
# Escenas ajustadas a la toma de voz (voz_santos.wav, entra a 0.9 s): cada una
# empieza ~120 ms antes de su primera palabra. Sin voz, el montaje original medía 49.5 s.
TIMES = (4000, 4740, 5180, 3660, 8960, 5790, 5260, 7260, 9150)
VOICE = ("voz_santos_podcast.wav", 900)
# Momentos dentro de escenas, en ms locales, tomados de la voz.
PENALES = (2600, 3500, 4000)      # filas: «penales», «expulsiones», «1 de 6»
RECUENTO = (4700, 6700, 7700)     # tarjeta, «dieciocho», «catorce»
BEATS = ((150, 2600), (2600, 4850), (4850, None))  # «agosto», «septiembre», «noviembre»
CLOSE = 3800                      # «hay cosas que…»
NAMES = ("De 1 a 18", "Seis seguidas", "Lo esperado", "El rebote", "Penales y rojas",
         "Tiros a puerta", "Acevedo", "La tribuna", "Esperanza")
IMAGES = {"arranque-completo":"aficion_aportada.png",
          "celebracion":"celebracion.jpg", "tahiel":"tahiel.jpg", "aleco":"aleco.jpg",
          "acevedo-partido":"acevedo_partido.jpg", "tribuna":"tribuna.jpg",
          "partido-aportado":"partido_aportado.jpg"}
# Golpes: llegada del 18 (escena 1), sexta G (escena 2) y «14 puntos» (escena 5).
CUES = ((1, 1530, "marca"), (2, 875, "marca"), (5, RECUENTO[2]+170, "marca"))


class Cronica(Author):
    def width(self, words, size, role="body", tracking=0):
        file = FONT[role][0]
        extra = tracking/1000*size*max(len(words)-1,0)
        return ImageFont.truetype(self.media / "fonts" / file, size).getlength(words) + extra

    def txt(self, words, x, y, size, color=INK, role="body", *, delay=0, fade=0,
            align="left", limit=None, duration=None, tracking=0):
        file, family, style = FONT[role]
        measure = self.width(words, size, role, tracking)
        if limit and measure > limit:
            size = int(size * limit / measure)
            measure = self.width(words, size, role, tracking)
        start_x = x-measure if align == "right" else x-measure/2 if align == "center" else x
        if start_x < 80 or start_x+measure > 969 or y > 1560:
            raise ValueError(f"{words!r} outside margins ({start_x}, {start_x+measure}, {y})")
        layer = self.add("createFxTextLayer", words, fx(start_x, y), start=delay, duration=duration,
                         sourceText=dict(text=words, fontFamily=family, fontStyle=style,
                                         fontAssetId=self.fonts[role], fontSize=size,
                                         fillColor=rgb(color), strokeWidth=0, tracking=tracking,
                                         justification="left", disableAutoWrap=True))
        if fade:
            self.keys(layer, "opacity", [(0, 0), (fade, 100)])
        return layer

    def lines(self, lines, x, y, size, step, color=INK, role="head", *, delay=0,
              fade=0, limit=None, duration=None):
        return [self.txt(line, x, y+step*i, size, color, role, delay=delay,
                         fade=fade, limit=limit, duration=duration) for i,line in enumerate(lines)]

    def separator(self, y, color=RULE, x=96, w=848, weight=2, *, delay=0, grow=0):
        return self.rect(x,y,w,weight,color,"Filete",delay=delay,grow=grow)

    def section(self, text, y=328, color=GRAY):
        self.txt(text, 96, y, 36, color, "number", tracking=60)

    def reveal(self, layer, y, size, *, delay=0, enter=520, exit_at=None, exit=380, duration=None):
        # El texto sube desde una línea de máscara; con exit_at sale por arriba.
        top, depth = y - size*1.02, size*1.36
        matte = self.add("createFxRectLayer","Máscara · línea",fx(70,top),start=delay,duration=duration,
                         rect=dict(size=[940,depth],fillColor=rgb("#FFFFFF")))
        self.actions.append(dict(type="setFxLayerTrackMatte",compositionId="main",
                                 layerId=layer,matteLayerId=matte,mode="alpha"))
        keys = [(0,y+depth),(enter,y)]
        if exit_at is not None:
            keys += [(exit_at,y),(exit_at+exit,y-depth)]
            self.keys(layer,"opacity",[(exit_at,100),(exit_at+exit*.8,0)])
        self.keys(layer,"positionY",keys)
        self.blurred.append(layer)
        return layer

    def fade(self, y0, y1, color, *, up=False, peak=100, cover_above=False):
        # Degradado suave hacia el color de fondo (PNG con alfa generado por el script).
        # Hacia abajo, un relleno sólido tapa lo que el acercamiento de la foto saque del fundido.
        asset = f"fundido-{color[1:].lower()}-{'arriba' if up else 'abajo'}"
        width,height = self.images[asset]
        layer = self.add("createFxImageLayer","Fundido",fx(0,y0,scale=(100*W/width,100*(y1-y0)/height)),
                         source=dict(assetId=asset,fit="none"))
        if peak != 100:
            self.keys(layer,"opacity",[(0,peak)])
        if not up:
            self.rect(0,y1-1,W,H-y1+1,color,"Fondo bajo el fundido")
        if up and cover_above:
            self.rect(0,0,W,y0+1,color,"Fondo sobre el fundido")

    def bleed(self, asset, bottom, *, delay=0, arrive=1, end=1.03, settle=True):
        # Foto a sangre desde el borde superior; el fundido inferior lo pone fade().
        width,height = self.images[asset]
        k = max(W/width, bottom/height)
        return self.picture(asset,(W-width*k)/2,0,width*k,height*k,delay=delay,arrive=arrive,end=end,settle=settle)

    def scrim(self, height=620, opacity=74):
        # Sombra superior para que los rótulos se lean sobre la foto.
        self.fade(0,height,INK,up=True,peak=opacity)

    def tag(self, words, x, y, size, *, delay=0, duration=None, fade=0, limit=None):
        # Rótulo sobre foto: la caja mide lo que mide su texto.
        width = min(self.width(words,size,"number"), limit or 10**6)
        box = self.rect(x-12,y-size-8,width+24,size+23,INK,"Rótulo de foto",delay=delay)
        if duration is not None:
            self.actions[-1]["activeRange"]["duration"] = duration
        text = self.txt(words,x,y,size,IVORY,"number",delay=delay,duration=duration,fade=fade,limit=limit)
        if fade:
            self.keys(box,"opacity",[(0,0),(fade,100)])
        return box, text

    def title(self, words, x, y, size, color, *, delay=120, limit=None, **kw):
        layer = self.txt(words, x, y, size, color, "head", delay=delay, limit=limit, **kw)
        return self.reveal(layer, y, size, delay=delay, duration=kw.get("duration"))

    def credits(self, text=FOOT, color=GRAY):
        self.txt(text, 96, 1530, 29, color, limit=848)

    def rise(self, x, baseline, w, height, color, label, delay):
        # Keep the baseline fixed and animate only the vertical extent of the bar.
        layer = self.add("createFxRectLayer", label,
                         fx(x,baseline,anchor=(0,height)),
                         start=delay,rect=dict(size=[w,height],fillColor=rgb(color)))
        self.keys(layer,"scaleY",[(0,0),(670,100)])

    def side_slide(self, layer, y, distance=30):
        self.keys(layer,"positionY",[(0,y+distance),(300,y)])

    def arrow(self,x,y,length,color,delay):
        shaft = dict(size=[length,5],fillColor=rgb(color))
        layer = self.add("createFxRectLayer","Flecha · trazo",fx(x,y),
                         start=delay,rect=shaft)
        self.keys(layer,"scaleX",[(0,0),(145,100)])
        tip = dict(size=[26,5],fillColor=rgb(color))
        parts = [layer]
        for rotation in (135,-135):
            end = self.add("createFxRectLayer","Flecha · punta",
                           fx(x+length,y+2,rotation=rotation,anchor=(0,2.5)),
                           start=delay+115,rect=tip)
            self.keys(end,"opacity",[(0,0),(90,100)])
            parts.append(end)
        return parts

    def build(self, d):
        start = 0
        for index, (name, duration) in enumerate(zip(NAMES, TIMES), 1):
            self.group = self.add("createFxGroupLayer", f"{index:02d} · {name}",
                                  fx(), start=start, duration=duration, grouped=False)
            self.duration = duration
            bg = {1:INK, 2:FOREST, 5:FOREST, 7:INK, 8:FOREST, 9:INK}.get(index,IVORY)
            self.rect(0,0,W,H,bg,"Fondo")
            self.content(index,d)
            start += duration

        self.group = None
        # Acabado común: grano fino de película sobre todo el montaje.
        finish = self.add("createFxAdjustmentLayer","Acabado · grano",fx(),start=0,duration=sum(TIMES),grouped=False)
        self.effect(finish,type="grain",amount=.7,size=1.0,softness=.3)
        self.actions.append(dict(type="setFxCompositionMotionBlur",compositionId="main",
                                 settings=dict(enabled=True,shutterAngle=180,shutterPhase=-90,
                                               samplesPerFrame=16,adaptiveSampleLimit=128)))
        for layer in self.blurred:
            self.actions.append(dict(type="setFxLayerMotionBlur",compositionId="main",layerId=layer,enabled=True))
        starts = [sum(TIMES[:i]) for i in range(len(TIMES))]
        for scene, local, asset in CUES:
            time = starts[scene-1] + local
            with wave.open(str(EDITOR / f"{asset}.wav"), "rb") as audio:
                length = round(1000 * audio.getnframes() / audio.getframerate())
            self.add("createFxAudioLayer",f"Acento · {time/1000:.3f} s", start=time, duration=length,
                     sourceRange=dict(start=0,duration=length),
                     sourceIntrinsicDuration=length,source={"assetId":asset})
        if (EDITOR / VOICE[0]).exists():
            with wave.open(str(EDITOR / VOICE[0]), "rb") as audio:
                length = round(1000 * audio.getnframes() / audio.getframerate())
            # La voz (−16 LUFS, mono) va a −1.2 dB: duplicada en estéreo, la mezcla queda cerca de −14 LUFS.
            self.add("createFxAudioLayer","Voz",start=VOICE[1],duration=length,
                     sourceRange=dict(start=0,duration=length),volume=0.87,
                     sourceIntrinsicDuration=length,source={"assetId":"voz"})

    def handoff(self, d):
        # Posición del 18 en la fila J8–J13 de la escena 2; ahí aterriza el 18 de la escena 1.
        rest = f" de {d['run_n']*3} puntos"
        rest_x = 943 - self.width(rest, 46)
        return rest, rest_x, rest_x - self.width(str(d["run"]), 46, "number")

    def content(self, shot, d):
        tx, line, rect = self.txt,self.separator,self.rect
        if shot == 1:
            # Recorte sobre el cartel y los rostros: la afición ocupa el encuadre inicial.
            self.framed("arranque-completo",0,0,1080,1060,focus=(600,380),crop=1.42,frame_y=535)
            # Corte seco al festejo, sobre el primer golpe.
            self.bleed("celebracion",1060,delay=1530,end=1.03)
            self.fade(840,1062,INK)
            self.scrim()
            self.section("SANTOS LAGUNA / APERTURA 2026",342,IVORY)
            # Todo lo que no es el 18 se retira antes del corte; el 18 viaja a la escena 2.
            owner=self.group
            board=self.add("createFxGroupLayer","Marcador que se retira",fx())
            self.group=board
            self.tag("FOTO APORTADA · FECHA SIN CONFIRMAR",96,1000,35,duration=1530,limit=620)
            self.tag("J13 · SANTOS 2–0 PUMAS",96,1000,35,delay=1530)
            tx(str(d["start"]),99,1320,269,IVORY,"number")
            self.arrow(342,1226,111,SAGE,1450)
            tx(f"punto en {d['start_n']} jornadas",99,1420,49,IVORY,limit=397)
            tx(f"puntos en {d['run_n']} victorias",550,1420,49,IVORY,delay=1530,fade=170,limit=385)
            self.group=owner
            self.keys(board,"opacity",[(0,100),(3420,100),(3640,0)])
            score=tx(str(d["run"]),550,1320,269,SAGE,"number",delay=1530,fade=140)
            _, _, land_x = self.handoff(d)
            go, arrive = 3600-1530, 3965-1530
            shrink = 100*46/269
            self.keys(score,"positionY",[(0,1360),(300,1320),(go,1320),(arrive,1380)])
            self.keys(score,"positionX",[(go,550),(arrive,land_x)])
            self.keys(score,"scaleX",[(go,100),(arrive,shrink)])
            self.keys(score,"scaleY",[(go,100),(arrive,shrink)])
            self.blurred.append(score)
            self.credits("FotMob/Opta · Fotos: aportada / Club Santos Laguna",SAGE)
        elif shot == 2:
            # La foto sigue el acercamiento de la escena 1 sin saltos.
            self.bleed("celebracion",1060,arrive=1.03,end=1.06,settle=False)
            self.fade(840,1062,FOREST)
            self.scrim()
            self.tag("APERTURA 2026 · PRIMERA VEZ EN SU HISTORIA",96,342,36)
            self.title("Seis victorias seguidas.",96,1100,87,IVORY,limit=848)
            blocks = (d["games"][:d["start_n"]],
                      d["games"][d["start_n"]:d["start_n"]+d["run_n"]],
                      d["games"][-3:])
            totals = (f"{d['start']} de {d['start_n']*3} puntos",
                      f"{d['run']} de {d['run_n']*3} puntos","Después de la racha")
            # Las filas van en su propio grupo: aísla su render del fundido de la foto.
            owner=self.group
            self.group=self.add("createFxGroupLayer","Resultados",fx())
            for row, games in enumerate(blocks[:2]):
                y = 1215 + 165*row
                label = d["spans"][row]
                row_delay = 1500 if row==2 else 0
                tx(label,98,y,41,SAGE,"number",delay=row_delay)
                if row == 1:
                    rest, rest_x, land_x = self.handoff(d)
                    tx(str(d["run"]),land_x,y,46,SAGE,"number")
                    tx(rest,rest_x,y,46,IVORY,delay=900,fade=190)
                else:
                    tx(totals[row],943,y,46,IVORY,align="right",delay=row_delay)
                for j, (_, symbol) in enumerate(games):
                    x = 97+j*120
                    active = row == 1
                    wait = 200 + 104*j if active else row_delay
                    rect(x,y+22,103,67,SAGE if active else FOREST,f"Jornada · {symbol}",
                         outline=None if active else "#748A79",delay=wait)
                    tx(symbol,x+51,y+69,43,FOREST if active else IVORY,"number",
                       delay=wait,align="center")
            self.group=owner
            self.credits("FotMob/Opta · Foto: Club Santos Laguna",SAGE)
        elif shot == 3:
            self.section("PRIMERAS SIETE JORNADAS")
            # Foto aportada por el usuario, sin texto encima; el crédito va en la línea de fuentes.
            self.framed("partido-aportado",0,370,1080,440,focus=(1280,620),crop=1080/2560,frame_y=220,
                        push=1.025,push_ms=self.duration)
            rect(0,795,1080,1125,IVORY,"El modelo entra sobre el partido")
            self.title("El arranque quedó corto.",96,890,90,INK,limit=848)
            line(1280,INK,x=97,w=846)
            cols = ((143,d["start"],"Puntos reales",BROWN,220),
                    (546,d["expected"],"Puntos esperados",PITCH,520))
            for x, val, title, color, delay in cols:
                bar_h=230*val/d["expected"]
                self.rise(x,1280,320,bar_h,color,title,delay)
                tx(f"{val:.1f}" if isinstance(val,float) else str(val),x+160,1262-bar_h,100,color,
                   "number",align="center",delay=delay+430,fade=240)
                tx(title,x+160,1344,49,INK,align="center")
            tx("xG: goles estimados por la calidad del tiro.",96,1425,40,GRAY,limit=854)
            tx("Con el xG, el modelo estima los puntos.",96,1474,40,GRAY,limit=854)
            self.credits("FotMob/Opta · Foto: aportada")
        elif shot == 4:
            self.section("QUÉ EXPLICA EL SALTO")
            self.title("El rebote",96,536,143,INK)
            tx(f"≈{d['bounce']:.0f}%",93,1011,283,PITCH,"number",delay=210,fade=160)
            line(1084,RULE,weight=84)
            line(1084,PITCH,w=848*d["bounce"]/100,weight=84,delay=295,grow=650)
            tx("del salto se atribuye al rebote, según el modelo.",96,1282,54,INK,limit=844)
            tx("Rebote: tras un mal arranque, volver hacia lo esperado.",96,1370,44,INK,limit=844)
            tx("Compara J1–J7 con J8–J13, por partido.",96,1432,40,GRAY,limit=844)
            self.credits()
        elif shot == 5:
            self.section("LO QUE CAMBIÓ LOS MARCADORES",color=SAGE)
            self.title("Penales y rojas",96,522,123,IVORY,limit=850)
            rows=((f"{d['pens']} de {d['goals']}","goles de penal"),
                  (f"{d['reds']} de {d['run_n']}","partidos con roja rival"),
                  (f"{d['clean']} de {d['run_n']}","triunfos sin penal, roja ni autogol"))
            owner=self.group
            details=self.add("createFxGroupLayer","Eventos observados",fx())
            self.group=details
            for i,(number,label) in enumerate(rows):
                y=700+i*143
                line(y-96,"#769084")
                tx(number,96,y,69,SAGE,"number",delay=PENALES[i],fade=140)
                tx(label,327,y,48,IVORY,delay=PENALES[i],fade=140,limit=614)
            self.keys(details,"opacity",[(0,100),(RECUENTO[0],100),(RECUENTO[0]+300,32)])
            self.group=owner
            recalc=self.add("createFxGroupLayer","Recuento que ocupa el plano",fx())
            self.keys(recalc,"opacity",[(0,0),(RECUENTO[0],0),(RECUENTO[0]+300,100)])
            self.group=recalc
            rect(96,1120,848,310,IVORY,"Franja del recuento")
            tx(f"{d['spans'][1]} · RECUENTO DE MARCADORES",117,1176,35,GRAY,"number")
            tx(str(d["run"]),117,1309,147,FOREST,"number",delay=RECUENTO[1],fade=150)
            self.arrow(284,1255,75,FOREST,RECUENTO[1]+370)
            counter=tx(f"{d['without']} puntos",404,1309,124,FOREST,"number",delay=RECUENTO[2],fade=170,limit=514)
            self.side_slide(counter,1309,24)
            tx("Sin goles de penal ni autogoles.",117,1390,48,INK,limit=800,delay=RECUENTO[2],fade=170)
            self.group=owner
            self.credits(color=SAGE)
        elif shot == 6:
            self.section("EN ATAQUE")
            self.picture("tahiel",0,370,1080,720,arrive=1,end=1.025)
            rect(0,1008,1080,912,IVORY,"Fondo de los remates")
            self.title("Más tiros a puerta.",96,1103,83,INK)
            for y,label,v,color,wait in ((1215,"Arranque",d["shots_start"],BROWN,170),(1355,"Racha",d["shots_run"],PITCH,470)):
                tx(label,97,y,49,INK)
                tx(f"{v:.1f}",946,y,110,color,"number",align="right",delay=wait+260,fade=190)
                line(y+37,RULE,weight=15)
                line(y+37,color,w=848*v/d["shots_run"],weight=15,delay=wait,grow=620)
            tx("Tiros a puerta por partido, en promedio.",96,1440,36,GRAY,limit=848)
            tx("Explica ≈15–22% del salto, según el modelo.",96,1487,42,PITCH,limit=848)
            self.credits("FotMob/Opta · Tahiel Jiménez / Club Santos Laguna")
        elif shot == 7:
            self.framed("acevedo-partido",0,0,1080,1010,focus=(615,230),crop=1.5,frame_y=340,push=1.025,push_ms=self.duration)
            self.fade(790,1012,INK)
            self.scrim()
            self.section("EN LA PORTERÍA",330,SAGE)
            self.title("Carlos Acevedo",96,1086,96,IVORY,limit=846)
            val1=f"≈{d['keeper_start']:+.1f}".replace("-","−")
            val2=f"≈{d['keeper_run']:+.1f}".replace("-","−")
            for x,label,value,wait in ((96,"J1–J7 · Arranque",val1,170),(590,"J8–J13 · Racha",val2,420)):
                tx(label,x,1170,43,SAGE,limit=382)
                tx(value,x,1280,108,IVORY,"number",delay=wait,fade=160,limit=340)
            tx("Puntos estimados acumulados por paradas.",96,1370,44,IVORY,limit=844)
            tx("Frente a lo esperado.",96,1425,43,SAGE,limit=844)
            tx("Además, los rivales colocaron peor sus tiros.",96,1480,43,SAGE,limit=844)
            self.credits("FotMob/Opta · Foto: MEXSPORT / Vanguardia",SAGE)
        elif shot == 8:
            self.section("LO QUE PASÓ FUERA DE LA CANCHA",324,SAGE)
            self.picture("aleco",0,380,1080,608,arrive=1,end=1.015)
            # La foto lleva su fecha toda la escena: no debe leerse como de agosto o septiembre.
            self.tag("FOTO · 2 NOV · TRAS SANTOS–NECAXA",101,926,43,limit=710)
            rect(0,962,1080,958,FOREST,"Fondo de la cronología")
            self.title("Color Esperanza",96,1056,89,IVORY,limit=848)
            tx("Diego Torres",96,1110,41,SAGE,limit=848,delay=560,fade=220)
            line(1160,"#769084")
            # Un momento por golpe: la fecha cambia en el mismo sitio, como un marcador.
            items = (("AGO","Aleco Irarragorri la canta. Llega la burla."),
                     ("13 SEP",f"Suena en el Corona tras el {d['juarez']} a Juárez."),
                     ("NOV","La afición ya la corea."))
            beats = tuple((a, self.duration if b is None else b) for a,b in BEATS)
            for index,((date,copy),(a,b)) in enumerate(zip(items,beats)):
                last = index == len(items)-1
                rect(96+76*index,1186,64,4,"#769084","Paso de la cronología")
                stay = b-a if last else b-a+380
                big = tx(date,96,1350,150,SAGE,"number",delay=a,duration=stay)
                self.reveal(big,1350,150,delay=a,duration=stay,exit_at=None if last else b-a)
                sub = tx(copy,96,1440,52,IVORY,delay=a+90,duration=stay-90,limit=848)
                self.reveal(sub,1440,52,delay=a+90,duration=stay-90,exit_at=None if last else b-a-90)
            cursor = rect(96,1186,64,4,IVORY,"Paso activo")
            moves = [(0,96)]
            for index,(a,_) in enumerate(beats[1:],1):
                moves += [(a,96+76*(index-1)),(a+300,96+76*index)]
            self.keys(cursor,"positionX",moves)
            self.blurred.append(cursor)
            self.credits("Fuentes: Fox Sports, Récord · Foto: zaraespinoza_ / Publimetro",SAGE)
        else:
            width,height = self.images["tribuna"]
            k = 1.6
            self.picture("tribuna",(W-width*k)/2,250,width*k,height*k,arrive=1,end=1.06)
            self.fade(270,440,INK,up=True,cover_above=True)
            self.fade(250+height*k-190,250+height*k+30,INK)
            for i,words in enumerate(("La canción no metió goles.", "Se volvió un símbolo.")):
                y, wait = 1100+91*i, 150+140*i
                layer = tx(words,96,y,76,IVORY,"head",delay=wait,duration=CLOSE-80-wait,limit=848)
                self.reveal(layer,y,76,delay=wait,duration=CLOSE-80-wait,exit_at=CLOSE-80-wait-400)
            for i,words in enumerate(("Hay cosas que", "solo la esperanza", "puede explicar.")):
                y, wait = 1101+118*i, CLOSE+170*i
                layer = tx(words,96,y,115,IVORY,"head",delay=wait,limit=847)
                self.reveal(layer,y,115,delay=wait,enter=640)
            self.credits("Foto de archivo: Jpamanes · Wikimedia Commons",SAGE)


def gradient_assets():
    # PNG de 8×512 con alfa en curva suave; el color es el del fondo de cada escena.
    made = {}
    for color in (INK, FOREST):
        for up in (False, True):
            name = f"fundido_{color[1:].lower()}_{'arriba' if up else 'abajo'}.png"
            image = Image.new("RGBA", (8, 512), ImageColor.getrgb(color) + (0,))
            for y in range(512):
                t = (y + .5) / 512
                a = t*t*(3-2*t)
                alpha = round(255 * ((1-a) if up else a))
                for x in range(8):
                    image.putpixel((x, y), ImageColor.getrgb(color) + (alpha,))
            image.save(MEDIA / name)
            made[f"fundido-{color[1:].lower()}-{'arriba' if up else 'abajo'}"] = name
    return made


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cli",type=Path)
    parser.add_argument("project",type=Path)
    parser.add_argument("analysis",type=Path, help="Directorio santos_analisis descomprimido")
    args=parser.parse_args()
    cli, project=args.cli.resolve(),args.project.resolve()
    source=run(cli,"project","inspect","-p",project)
    if source["composition"]["layers"]:
        raise ValueError("Start with a new Tesseract document")
    source["duration"]=sum(TIMES)/1000
    root_json=MEDIA/"root.json"
    root_json.write_text(json.dumps(source),encoding="utf-8")
    run(cli,"project","commit","-p",project,"--file",root_json)
    data=load_data(args.analysis)
    author=Cronica(MEDIA)
    embedded = {}
    for role,(filename, family, _) in FONT.items():
        if filename not in embedded:
            font=run(cli,"project","import-font","-p",project,"--file",MEDIA/"fonts"/filename)
            assert font["fontFamily"] == family, font
            embedded[filename] = font["assetId"]
        author.fonts[role]=embedded[filename]
    for asset, name in gradient_assets().items():
        file=MEDIA/name
        run(cli,"project","import-asset","-p",project,"--file",file,"--asset-id",asset,"--kind","image")
        with Image.open(file) as image:
            author.images[asset]=image.size
    for asset, name in IMAGES.items():
        file=MEDIA/name
        run(cli,"project","import-asset","-p",project,"--file",file,"--asset-id",asset,"--kind","image")
        with Image.open(file) as image:
            author.images[asset]=image.size
    run(cli,"project","import-asset","-p",project,"--file",EDITOR/"marca.wav","--asset-id","marca","--kind","audio")
    if (EDITOR/VOICE[0]).exists():
        run(cli,"project","import-asset","-p",project,"--file",EDITOR/VOICE[0],"--asset-id","voz","--kind","audio")
    author.build(data)
    action_file=MEDIA/"crónica_acciones.json"
    action_file.write_text(json.dumps(author.actions,ensure_ascii=False),encoding="utf-8")
    applied=run(cli,"project","apply","-p",project,"--actions",action_file)
    print(applied["appliedActions"], "actions")
    print(run(cli,"project","check","-p",project))


if __name__ == "__main__":
    main()
