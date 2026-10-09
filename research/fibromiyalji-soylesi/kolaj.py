"""Dergi tarzı kolaj (gönderi 1080x1350 + hikâye 1080x1920). Kullanım: python3 kolaj.py FONT_DIR IMG_DIR OUT_DIR"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
FD, IMG, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
NAVY=(10,10,72); PURPLE=(86,64,170); DOT=(133,110,227); LILAC=(205,200,250); LILAC2=(183,179,240)
GREENL=(229,245,200); GREEN=(91,138,47); PANEL=(251,250,255)
def F(n,s): return ImageFont.truetype(os.path.join(FD,n),s)
WALLS={"2.jpg":(180,860,340,980),"4.jpg":(560,780,760,900),"6.jpg":(560,780,760,900),"5.jpg":(280,850,440,1000)}
_cache={}
def graded(src):
    if src not in _cache:
        im=Image.open(os.path.join(IMG,src)).convert("RGB"); a=np.asarray(im).astype(np.float32)
        x0,y0,x1,y1=WALLS[src]; ref=a[y0:y1,x0:x1].reshape(-1,3).mean(0); a=a*(ref.mean()/ref)**0.8
        a=255*((np.clip(a,0,255)/255)**0.92); im=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
        _cache[src]=ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.07)).enhance(1.06)
    return _cache[src]
def photo(src, cx, headY, cw, size, head_at=0.25):
    w,h=size; ch=round(cw*h/w); im=graded(src)
    x0=int(min(max(cx-cw/2,0),im.width-cw)); y0=int(min(max(headY-head_at*ch,0),im.height-ch))
    out=im.crop((x0,y0,x0+cw,y0+ch)).resize(size,Image.LANCZOS)
    return out.filter(ImageFilter.UnsharpMask(radius=1.2,percent=45,threshold=2))
def place(c, im, xy, r=24, label=None):
    x,y=xy; w,h=im.size
    sh=Image.new("RGBA",(w+80,h+80),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((40,52,40+w,52+h),r,fill=(30,20,90,70))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)),(x-40,y-40))
    m=Image.new("L",(w,h),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),r,fill=255); c.paste(im,(x,y),m)
    if label:
        f=F("Montserrat-700.ttf",20); tw=f.getlength(label); d=ImageDraw.Draw(c)
        d.rounded_rectangle((x+16,y+h-56,x+16+tw+30,y+h-18),19,fill=PANEL+(240,))
        d.text((x+31,y+h-48),label,font=f,fill=NAVY)
def bg(W,H):
    c=Image.new("RGBA",(W,H),PANEL+(255,)); L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.ellipse((-360,-330,420,330),fill=LILAC2+(150,)); d.ellipse((W-360,-300,W+380,300),fill=GREENL+(255,))
    d.ellipse((-300,H-260,360,H+300),fill=GREENL+(255,)); d.ellipse((W-330,H-240,W+330,H+340),fill=LILAC2+(140,))
    c.alpha_composite(L); d=ImageDraw.Draw(c)
    for i in range(3):
        for j in range(4): x,y=W-150+j*26,52+i*26; d.ellipse((x-4,y-4,x+4,y+4),fill=DOT)
    return c
def fit(text,font,maxw,size):
    while F(font,size).getlength(text)>maxw: size-=2
    return F(font,size)
def header(c,y,k=1.0):
    W=c.width; d=ImageDraw.Draw(c)
    f=F("Montserrat-700.ttf",int(21*k)); t="SÖYLEŞİ VE DENEYİM AKTARIMI  ·  9 EKİM 2026"; tw=f.getlength(t); ph=int(21*k)+20
    d.rounded_rectangle((W/2-tw/2-20,y,W/2+tw/2+20,y+ph),ph//2,fill=LILAC); d.text((W/2,y+10),t,font=f,fill=NAVY,anchor="mt")
    y+=ph+int(14*k); d.text((W/2,y),"Birlikte İyileşelim",font=F("Dancing-700.ttf",int(60*k)),fill=PURPLE,anchor="mt")
    y+=int(74*k); d.text((W/2,y),"FİBROMİYALJİ KADERİNİZ DEĞİL!",font=fit("FİBROMİYALJİ KADERİNİZ DEĞİL!","Montserrat-800.ttf",W-100,int(56*k)),fill=NAVY,anchor="mt")
    y+=int(76*k); d.rounded_rectangle((W/2-70,y,W/2+70,y+6),3,fill=GREEN); return y+int(30*k)
def footer(c,y,k=1.0):
    W=c.width; d=ImageDraw.Draw(c)
    d.text((W/2,y),"Katılan herkese teşekkür ederiz.",font=F("Montserrat-800.ttf",int(34*k)),fill=NAVY,anchor="mt")
    d.text((W/2,y+int(50*k)),"Uzm. Dr. Hande Çelik Mehmetoğlu  &  Uzm. Dr. Ferda Firdin",font=fit("Uzm. Dr. Hande Çelik Mehmetoğlu  &  Uzm. Dr. Ferda Firdin","Montserrat-700.ttf",W-120,int(25*k)),fill=PURPLE,anchor="mt")

# --- gönderi 1080x1350 ---
W,H=1080,1350; c=bg(W,H); y=header(c,40)
G=14; X0=44; X1=W-44; top=y; Lw=500; Rw=X1-X0-Lw-G; rowH=650
place(c,photo("4.jpg",405,895,560,(Lw,rowH)),(X0,top),label="KONUĞUMUZ")
hh=(rowH-G)//2
place(c,photo("6.jpg",475,965,600,(Rw,hh)),(X0+Lw+G,top),label="EV SAHİBİMİZ")
place(c,photo("5.jpg",540,1040,620,(Rw,rowH-hh-G),0.22),(X0+Lw+G,top+hh+G))
sy=top+rowH+G; sh=1350-150-sy
place(c,photo("2.jpg",461,975,923,(X1-X0,sh),0.10),(X0,sy))
footer(c,H-128)
c.convert("RGB").save(os.path.join(OUT,"kolaj-gonderi-1080x1350.jpg"),quality=95)

# --- hikâye 1080x1920 ---
W,H=1080,1920; c=bg(W,H); y=header(c,120,1.15)
Wd=W-88; hw=(Wd-G)//2; th=620
place(c,photo("4.jpg",405,895,440,(hw,th)),(44,y),label="KONUĞUMUZ")
place(c,photo("6.jpg",475,965,440,(hw,th)),(44+hw+G,y),label="EV SAHİBİMİZ")
y2=y+th+G; place(c,photo("5.jpg",540,1040,700,(Wd,380),0.22),(44,y2))
y3=y2+380+G; place(c,photo("2.jpg",461,975,923,(Wd,300),0.10),(44,y3))
footer(c,y3+300+46,1.15)
ImageDraw.Draw(c).text((W/2,y3+300+46+120),"@drhandecelikmehmetoglu",font=F("Montserrat-700.ttf",30),fill=PURPLE,anchor="mt")
c.convert("RGB").save(os.path.join(OUT,"kolaj-hikaye-1080x1920.jpg"),quality=95)
print("ok")
