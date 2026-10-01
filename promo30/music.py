import numpy as np, wave
from scipy.signal import butter, sosfilt, fftconvolve
SR=48000; DUR=30.0; N=int(SR*DUR); BPM=120; BEAT=60/BPM
rng=np.random.default_rng(5)
L=np.zeros(N); R=np.zeros(N); DRY=[np.zeros(N),np.zeros(N)]; WET=[np.zeros(N),np.zeros(N)]
duck=np.ones(N)
def add(buf,x,t,g=1.0,pan=0.0):
    i=int(t*SR); 
    if i>=N or i<0: return
    x=x[:N-i]; l=g*np.cos((pan+1)*np.pi/4); r=g*np.sin((pan+1)*np.pi/4)
    buf[0][i:i+len(x)]+=x*l; buf[1][i:i+len(x)]+=x*r
def lp(x,f,o=2): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],'band',fs=SR,output='sos'),x)
def tt(d): return np.arange(int(d*SR))/SR
def kick(g=1):
    t=tt(0.45); f=50+110*np.exp(-t*28); ph=2*np.pi*np.cumsum(f)/SR
    x=np.sin(ph)*np.exp(-t*7.5)+0.25*np.sin(ph*2)*np.exp(-t*30); x[:60]+=np.linspace(0.6,0,60); return x*g
def clap():
    t=tt(0.28); n=rng.standard_normal(len(t)); e=np.exp(-t*22)
    for d in (0.0,0.011,0.022): e+=np.where(t>d,np.exp(-(t-d)*60),0)*0.5
    return bp(n,900,5000)*e*0.9
def hat(d=0.06,b=7000):
    t=tt(d); return hp(rng.standard_normal(len(t)),b)*np.exp(-t*(5/d)*0.9)
def saw(f,d,det=0.0):
    t=tt(d); ph=(f*(1+det)*t)%1; return 2*ph-1
def pad_note(f,d):
    t=tt(d); x=sum(saw(f,d,dt)*0.33 for dt in (-0.006,0,0.006))+0.2*np.sin(2*np.pi*f*t)
    a=np.minimum(t/0.5,1)*np.minimum((d-t)/0.6,1); return lp(x,1800)*a
def pluck(f,d=0.35):
    t=tt(d); x=(saw(f,d,0.003)+0.5*np.sin(2*np.pi*f*2*t))*np.exp(-t*9); return lp(x,3500,2)*0.5
def bell(f,d=1.4):
    t=tt(d); x=np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*3)+0.2*np.sin(2*np.pi*f*5.4*t)*np.exp(-t*6); return x*np.exp(-t*2.8)*0.5
def bass(f,d):
    t=tt(d); x=np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*f*2*t)+0.15*saw(f,d); a=np.minimum(t/0.01,1)*np.minimum((d-t)/0.05,1); return lp(x,420)*a
def midi(n): return 440*2**((n-69)/12)
# progression one chord per bar: Dm9, Bbmaj7, F6/9, C(add9)  (MIDI chord tones, root)
CH=[(50,[62,65,69,72]),(46,[58,62,65,69]),(53,[60,65,69,72]),(48,[60,64,67,74])]
def chord(bar): return CH[bar%4]
def bars(a,b): return range(a,b)
# ── scheduling (seconds) ──
KICK_SOFT=[(t) for t in np.arange(4,9.5,BEAT)]+[]
DROP=10.0; BRK=22.0; END_BUILD=24.0; FIN=26.0
def kick_at(t,g=1): add(DRY,kick(g),t,0.9,0); i=int(t*SR); m=min(N-i,int(0.25*SR)); 
def sc(t,depth=0.55,rel=0.28):
    i=int(t*SR); m=min(N-i,int(rel*SR)); 
    if m<=0: return
    e=1-depth*np.exp(-np.arange(m)/SR*9)*(1-np.arange(m)/m); duck[i:i+m]=np.minimum(duck[i:i+m],e)
for t in np.arange(4,9.5,BEAT): kick_at(t,0.7); sc(t,0.35)
for t in np.arange(DROP,BRK,BEAT): kick_at(t,1.0); sc(t,0.6)
for t in np.arange(BRK,END_BUILD,2*BEAT): kick_at(t,0.8); sc(t,0.4)
for t in np.arange(END_BUILD,FIN-0.5,BEAT): kick_at(t,0.75); sc(t,0.4)
for t in np.arange(FIN,28,BEAT): kick_at(t,1.0); sc(t,0.6)
kick_at(28.0,1.0)
# claps/snares
for t in np.arange(DROP+BEAT,BRK,2*BEAT): add(DRY,clap(),t,0.55,0.05); add(WET,clap(),t,0.25,0.05)
for t in np.arange(FIN+BEAT,28,2*BEAT): add(DRY,clap(),t,0.55,0.05)
for t in np.arange(6,8,BEAT): add(DRY,clap(),t,0.35,0)       # early backbeat in build
# snare roll 8→10 accelerating, and 24→26
def roll(t0,t1):
    t=t0; step=BEAT/2; k=0
    while t<t1:
        add(DRY,clap(),t,0.2+0.45*(t-t0)/(t1-t0),0); t+=max(step*(1-(t-t0)/(t1-t0))**0.8,0.045)
roll(8.0,DROP-0.02); roll(END_BUILD+0.5,FIN-0.02)
# hats
for t in np.arange(2,DROP-0.5,BEAT/2): add(DRY,hat(0.05),t+BEAT/4*0,0.16,0.3)
for t in np.arange(DROP,BRK,BEAT/4): add(DRY,hat(0.035,8500),t,0.10+0.06*((round((t-DROP)/(BEAT/4)))%4==2),0.35)
for t in np.arange(DROP+BEAT/2,BRK,BEAT): add(DRY,hat(0.18,6000),t,0.12,-0.3)
for t in np.arange(FIN,28,BEAT/4): add(DRY,hat(0.035,8500),t,0.10,0.35)
# pad (every bar, each chord) ; sidechained later
def pad(bar,g=0.20):
    r,ts=chord(bar); t0=bar*2*BEAT*2/2*1.0
    t0=bar*4*BEAT/2*2/2*1.0
def bar_t(b): return b*4*BEAT
for b in range(0,15):
    r,ts=chord(b); t0=bar_t(b); d=4*BEAT+0.3
    g=0.16 if b>=1 else 0.11
    for n in ts: x=pad_note(midi(n),d); add(WET,x,t0,g*0.6,-0.3); add(DRY,x,t0,g*0.55,0.3)
# intro bells: logo bloom at 1.0, wordmark 2.0 / 2.5
for t,n in ((0.5,86),(1.0,81),(1.5,89),(2.0,93),(2.5,98),(3.0,93),(3.5,89)): add(WET,bell(midi(n)),t,0.35,0.0); add(DRY,bell(midi(n)),t,0.18,0.0)
# arp 16ths (pluck) from 4s; sparse 8ths 4-10, full 16ths drop
def arp(t0,t1,step,g):
    t=t0; k=0
    while t<t1-1e-6:
        b=int(t/(4*BEAT)); r,ts=chord(b); seq=[ts[0]+12,ts[2],ts[3],ts[1]+12,ts[3]+12,ts[2]+12,ts[3],ts[1]]
        n=seq[k%len(seq)]; x=pluck(midi(n)); add(DRY,x,t,g,-0.4+0.8*((k%8)/7)); add(WET,x,t,g*0.5,0.4); t+=step; k+=1
arp(4,8,BEAT/2,0.20); arp(DROP,BRK,BEAT/4,0.17); arp(BRK,END_BUILD,BEAT/2,0.20); arp(FIN,28,BEAT/4,0.16)
# bass
def bassline(t0,t1,g=0.55):
    for b in range(int(t0/(4*BEAT)),int(t1/(4*BEAT))):
        r,ts=chord(b); f=midi(r-12)
        for k in range(8):
            t=bar_t(b)+k*BEAT/2
            if t<t0-1e-6 or t>=t1: continue
            if k in (0,3,6,7) or (k==4): add(DRY,bass(f*(2 if k==6 else 1),BEAT/2*0.9),t,g,0)
bassline(DROP,BRK); bassline(FIN,28)
for b in range(4,10): 
    if b*4*BEAT>=4: r,ts=chord(b); add(DRY,bass(midi(r-12),4*BEAT*0.9),bar_t(b),0.30,0)
# risers
def riser(t0,t1,g=0.35):
    t=tt(t1-t0); n=rng.standard_normal(len(t)); k=(t/(t1-t0))
    f=300+7000*k**2.2; out=np.zeros(len(t)); 
    for i in range(0,len(t),2048):
        seg=n[i:i+2048]; fc=f[min(i,len(t)-1)]; out[i:i+2048]=bp(seg,max(80,fc*0.6),min(fc*1.3,20000),2)[:len(seg)] if len(seg)>16 else seg
    add(WET,out*(k**1.5)*g,t0,1,0.0); add(DRY,out*(k**1.5)*g,t0,0.6,0.0)
riser(6.0,DROP,0.5); riser(END_BUILD,FIN,0.5); 
# impacts
def impact(t,g=1.0):
    d=2.4; x=tt(d); s=np.sin(2*np.pi*(38*np.exp(-x*0.6)+22)*x)*np.exp(-x*1.6)
    cr=hp(rng.standard_normal(len(x)),3500)*np.exp(-x*2.2)*0.35
    add(DRY,s*0.9*g,t,1,0); add(WET,cr*g,t,0.8,0); add(DRY,cr*g,t,0.4,0)
impact(DROP,1.0); impact(FIN,1.0); impact(28.0,0.9)
# transition whooshes (visual wipes) at 14,18,22 and 4,8
def whoosh(t,d=0.6,g=0.4):
    x=tt(d); k=x/d; n=rng.standard_normal(len(x)); fc=800+4000*np.sin(np.pi*k); out=np.zeros(len(x))
    for i in range(0,len(x),1024):
        seg=n[i:i+1024]; f=fc[min(i,len(x)-1)]; out[i:i+1024]=bp(seg,f*0.5,f*1.5)[:len(seg)]
    add(WET,out*np.sin(np.pi*k)*g,t-d*0.5,1,0); add(DRY,out*np.sin(np.pi*k)*g,t-d*0.5,0.6,0)
for t in (4.0,10.0,14.0,18.0,22.0,26.0): whoosh(t)
# final chord ring + fade
for n in (62,65,69,74,77): x=bell(midi(n+12),3.0); add(WET,x,28.0,0.35,0); add(DRY,x,28.0,0.20,0)
add(DRY,bell(midi(81),3.0),28.5,0.2,0)
# mix
def reverb(x,T=1.6):
    t=tt(T); ir=rng.standard_normal(len(t))*np.exp(-t*4.2/ (T/1.6)); ir=lp(ir,6000); return fftconvolve(x,ir*0.08)[:N]
wl=reverb(WET[0]); wr=reverb(WET[1],1.7)
dl=DRY[0]; dr=DRY[1]
# sidechain pad/arp/wet but not drums: approximate by ducking the whole wet and a share of dry
mixL=dl*(0.55+0.45*duck)+wl*duck; mixR=dr*(0.55+0.45*duck)+wr*duck
# master: tape-ish soft clip, hp, fades
st=np.stack([mixL,mixR]); st=hp(st,28,2); st=np.tanh(st*1.5)/1.2
env=np.ones(N); env[:int(0.02*SR)]=np.linspace(0,1,int(0.02*SR)); env[-int(1.4*SR):]=np.linspace(1,0,int(1.4*SR))**1.5
for g0,g1 in ((9.80,9.995),(25.80,25.995)):
    a,b=int(g0*SR),int(g1*SR); f=int(0.012*SR); env[a:b]=0.0; env[a-f:a]=np.linspace(1,0,f); env[b:b+f]=np.linspace(0,1,f)
st*=env
st/=np.max(np.abs(st))/0.89; st*=0.37
pcm=(st.T*32767).astype('<i2')
with wave.open('music.wav','wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok',np.sqrt(np.mean(st**2)))
