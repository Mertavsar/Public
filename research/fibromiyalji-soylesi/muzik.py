"""Telifsiz, videoya özel sakin müzik (75 BPM, ölçü = 3.2 sn). Kullanım: python3 muzik.py OUT.wav SURE"""
import sys, wave, numpy as np
OUT=sys.argv[1]; DUR=float(sys.argv[2]); SR=44100; BAR=3.2; BEAT=BAR/4
n=int(SR*DUR); L=np.zeros(n); R=np.zeros(n)
def hz(m): return 440*2**((m-69)/12)
# D major: Dmaj7, Bm9, Gmaj7, Em9, Gmaj7/A, Dmaj9
CH=[[50,57,61,64,66],[47,54,61,62,66],[43,50,59,62,66],[40,47,54,59,62],[45,50,55,59,66],[50,57,64,66,69]]
t=np.arange(n)/SR
def env(start,length,a=0.6,r=1.6):
    e=np.zeros(n); i0=int(start*SR); i1=min(n,int((start+length+r)*SR))
    tt=np.arange(i1-i0)/SR
    e[i0:i1]=np.clip(tt/a,0,1)*np.where(tt<length,1,np.exp(-(tt-length)*3/r)); return e
for b,ch in enumerate(CH):
    st=b*BAR
    if st>=DUR: break
    ln=BAR if b<len(CH)-1 else DUR-st-1.0
    e=env(st,ln)
    for k,m in enumerate(ch):     # pad: hafif detune'lu sinüsler
        f=hz(m+12 if k==0 else m)
        for dt,pan in ((-0.12,0.35),(0.12,0.65)):
            s=np.sin(2*np.pi*(f+dt)*t+k)*0.035*e
            L+=s*(1-pan); R+=s*pan
    # arpej: sekizlik notalar, piyano benzeri
    arp=[ch[0]+24,ch[2]+12,ch[3]+12,ch[4]+12,ch[2]+24,ch[4]+12,ch[3]+12,ch[2]+12]
    for j,m in enumerate(arp):
        s0=st+j*BEAT/2
        if b==len(CH)-1 and j>3: break
        if s0>=DUR-0.5: break
        i0=int(s0*SR); i1=min(n,i0+int(2.4*SR)); tt=np.arange(i1-i0)/SR; f=hz(m)
        tone=(np.sin(2*np.pi*f*tt)+0.35*np.sin(4*np.pi*f*tt)+0.12*np.sin(6*np.pi*f*tt))
        tone*=np.exp(-tt*2.2)*np.clip(tt/0.006,0,1)*(0.06 if j%4==0 else 0.042)
        pan=0.5+0.25*np.sin(j*1.3+b)
        L[i0:i1]+=tone*(1-pan); R[i0:i1]+=tone*pan
    # derin bas
    eb=env(st,ln,0.3,1.2); bs=np.sin(2*np.pi*hz(ch[0]-12)*t)*0.05*eb; L+=bs; R+=bs
# basit yankı (Schroeder comb + allpass)
def reverb(x):
    out=np.zeros_like(x)
    for d,g in ((1557,0.80),(1617,0.79),(1491,0.81),(1422,0.80)):
        y=np.copy(x)
        for i in range(d,len(x),d):
            seg=y[i-d:min(i,len(x)-d)]; y[i:i+len(seg)]+=seg*g
        out+=y*0.25
    return out
L=L*0.75+reverb(L)*0.35; R=R*0.75+reverb(R)*0.35
fade=np.ones(n); fi=int(0.6*SR); fo=int(2.2*SR)
fade[:fi]=np.linspace(0,1,fi); fade[-fo:]=np.linspace(1,0,fo)**1.5
L*=fade; R*=fade; pk=max(np.abs(L).max(),np.abs(R).max()); L/=pk/0.7; R/=pk/0.7
data=(np.stack([L,R],1)*32767).astype(np.int16)
with wave.open(OUT,"wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())
print("ok",OUT,DUR)
