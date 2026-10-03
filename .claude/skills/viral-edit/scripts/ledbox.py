import numpy as np, cv2
def classify(f):
    r=f.astype(int); mx=r.max(2); mn=r.min(2); R,G,B=r[...,2],r[...,1],r[...,0]
    dark=mx<60; white=mn>170; red=(R>40)&(G<0.6*R)&(B<0.6*R)
    return dark,white,red
def find_box(f):
    """LED kutusu: sağ kenara kadar uzanan siyah dikdörtgen. (y0,y1,x0,kx1) ya da None"""
    dark,white,red=classify(f[250:520])
    ok=dark|white|red
    col=ok[:,1030:1068].mean(1)>0.85
    best=None;s=None
    for y in range(len(col)+1):
        v=col[y] if y<len(col) else False
        if v and s is None: s=y
        if not v and s is not None:
            if best is None or y-s>best[1]-best[0]: best=(s,y)
            s=None
    if not best or not (80<=best[1]-best[0]<=220): return None
    y0,y1=best[0]+250,best[1]+250
    band=ok[best[0]+6:best[1]-6]
    cf=band.mean(0)>0.92
    x=1068
    while x>0 and cf[x]: x-=1
    x0=x+1
    if 1080-x0<60: return None
    wt=white[best[0]:best[1],x0:]
    kx1=None
    if wt.sum()>300:
        xs=np.nonzero(wt.any(0))[0]
        kx1=x0+xs.max()
    return y0,y1,x0,kx1
