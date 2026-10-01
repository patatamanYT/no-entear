import os, sys
sys.path.insert(0, os.path.expanduser("~/.claude/skills/onetake/scripts"))
from sfx_palette import Score, air, glass, wood, sub, bubble, pan_of
import numpy as np
rng=np.random.default_rng(11); s=Score(dur=15.0,T60=1.0); place=s.place
# card opens around the caret
place(air(0.55,250,2200,1.2,0.5),1.15,0.22,0.0,0.5)
# typing: muted keys
TXT='fix the failing test in the API'
for i,ch in enumerate(TXT):
    if ch==' ' or rng.uniform()<0.3: continue
    place(wood(180+rng.uniform(-20,20),0.08),1.9+i/17+rng.uniform(0,0.004),0.10*rng.uniform(.7,1.3),-0.05,0.15)
# enter: down / up, card grows
place(wood(235,0.08),4.05,0.32,0.0,0.2); place(wood(185,0.07),4.10,0.2,0.0,0.2)
place(air(0.4,300,2400,1.3),4.08,0.2,0.0,0.4); place(sub(66,0.5),4.2,0.22,0.0,0.3)
# four ticks up a scale
for f,t in zip((523,659,784,1046),(4.55,5.20,5.95,6.70)): place(glass(f,0.6,0.8),t,0.16,-0.05,0.4)
# diff lands
place(air(0.3,2200,400,1.5),7.3,0.16,0.0,0.4)
for i in range(5): place(wood(150+i*12,0.06),7.41+i*0.06,0.08,0.0,0.2)
# pass: soft two-note chord + felt hit
place(glass(1318,1.3,0.5),8.55,0.17,0.0,0.6); place(glass(1976,1.3,0.4),8.58,0.11,0.05,0.6); place(sub(62,0.6),8.55,0.2,0.0,0.3)
# fold into the caret, then the name types
place(air(0.8,1800,260,1.3),10.7,0.25,0.0,0.5)
NAME='Claude Code'
for i in range(len(NAME)):
    if NAME[i]!=' ': place(wood(200+rng.uniform(-15,15),0.07),11.6+i/9,0.09,0.0,0.2)
place(glass(392,1.8,0.3),12.85,0.10,0.0,0.7)
s.write(os.path.join(os.path.dirname(os.path.abspath(__file__)),"sfx.wav"))
