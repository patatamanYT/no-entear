"""Radares Choque/Cobertura para el diseño de Canva: PNG transparente, proporción ~0.71, sin título.

Uso (desde liga_mx_stopper_cover/): python radar_canva.py canva
"""
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
sys.path.insert(0, ".")
from radar_centrales import RADAR, radar_percentiles
from matplotlib import font_manager as fm
for f in ["/usr/share/fonts/opentype/inter/Inter-Regular.otf","/usr/share/fonts/opentype/inter/Inter-SemiBold.otf","/usr/share/fonts/opentype/inter/Inter-Bold.otf"]:
    fm.fontManager.addfont(f)
FONT=["Inter","DejaVu Sans"]
INK="#0f2e22"; GRID="#9aa59e"
COLORS=[("#b98cf5","#8f55ea"),("#5ab9ef","#2f95d6")]   # Joaquim morado, Bauermann azul (como el Reel)
players=["Joaquim","Eduardo Bauermann"]; tag="Apertura 26"
df=pd.read_csv("stopper_vs_cover_apertura2026_scores.csv")
out_dir=sys.argv[1]
W,H=7.0,9.9   # proporcion del marco de Canva (~0.71)
for role, metrics in RADAR.items():
    used,pct=radar_percentiles(df,metrics,0.8)
    cols=[c for c,_ in used]; labels=[l.replace("Intercepciones","Intercep-\nciones") for _,l in used]
    n=len(cols); ang=np.pi/2-np.arange(n)*2*np.pi/n
    fig=plt.figure(figsize=(W,H)); fig.patch.set_alpha(0)
    ax=fig.add_axes([0.0,0.22,1.0,0.74]); ax.set_aspect("equal"); ax.axis("off"); ax.patch.set_alpha(0)
    for lvl in (0.25,0.5,0.75,1.0):
        xs,ys=lvl*np.cos(ang),lvl*np.sin(ang)
        ax.plot(np.r_[xs,xs[0]],np.r_[ys,ys[0]],color=GRID,lw=1.3 if lvl==1 else 0.9)
    for a in ang: ax.plot([0,np.cos(a)],[0,np.sin(a)],color=GRID,lw=0.9)
    for p,(fc,ec) in reversed(list(zip(players,COLORS))):
        i=df.index[df.player==p][0]
        v=np.clip(np.nan_to_num(np.array([pct.at[i,c] for c in cols],float))/100,0.04,1)
        xs,ys=v*np.cos(ang),v*np.sin(ang)
        ax.fill(xs,ys,color=fc,alpha=0.40,lw=0); ax.plot(np.r_[xs,xs[0]],np.r_[ys,ys[0]],color=ec,lw=2.6)
        ax.scatter(xs,ys,s=40,color=ec,zorder=4,linewidths=0)
    for a,lab in zip(ang,labels):
        cx,cy=np.cos(a),np.sin(a)
        ha="center" if abs(cx)<0.2 else ("left" if cx>0 else "right")
        va="center" if abs(cy)<0.2 else ("bottom" if cy>0 else "top")
        ax.text(1.14*cx,1.14*cy,lab,ha=ha,va=va,fontsize=17,color=INK,family=FONT,fontweight=600,linespacing=1.15)
    ax.set_xlim(-2.15,2.15); ax.set_ylim(-1.75,1.75)
    fw,fh=fig.get_size_inches()
    for k,(p,(fc,ec)) in enumerate(zip(players,COLORS)):
        y=0.15-k*0.07
        fig.add_artist(Ellipse((0.12,y),0.045,0.045*fw/fh,transform=fig.transFigure,color=ec))
        t=fig.text(0.17,y,p,fontsize=21,color=INK,family=FONT,fontweight=600,va="center")
        fig.canvas.draw(); x1=t.get_window_extent().transformed(fig.transFigure.inverted()).x1
        fig.text(x1+0.015,y,f"· {tag}",fontsize=15,color="#5d6b63",family=FONT,va="center")
    out=f"{out_dir}/radar_{role}_canva.png"
    fig.savefig(out,dpi=200,transparent=True); plt.close(fig); print(out)
