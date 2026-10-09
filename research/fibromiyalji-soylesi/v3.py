"""v3: afiş kimliğiyle dergi düzeni. Kullanım: python3 v3.py FONT_DIR IMG_DIR OUT_DIR"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
FD, IMG, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
NAVY=(10,10,72); PURPLE=(86,64,170); DOT=(133,110,227); LILAC=(205,200,250); LILAC2=(183,179,240)
GREENL=(229,245,200); GREEN=(91,138,47); PANEL=(251,250,255)
def F(n,s): return ImageFont.truetype(os.path.join(FD,n),s)

def grade(im, wall):
    a=np.asarray(im).astype(np.float32)
    x0,y0,x1,y1=wall; ref=a[y0:y1,x0:x1].reshape(-1,3).mean(0)
    gain=(ref.mean()/ref)**0.8 * np.array([1.0,1.0,1.0])   # duvarı nötre yaklaştır
    a=a*gain
    a=255*((a/255)**0.92)                                    # gölgeleri hafif aç
    a=np.clip(a,0,255).astype(np.uint8); im=Image.fromarray(a)
    im=ImageEnhance.Contrast(im).enhance(1.07); im=ImageEnhance.Color(im).enhance(1.06)
    return im

def shot(src, box, size, wall):
    im=Image.open(os.path.join(IMG,src)).convert("RGB")
    im=grade(im, wall).crop(box).resize(size, Image.LANCZOS)
    im=im.filter(ImageFilter.UnsharpMask(radius=1.4,percent=55,threshold=2))
    # hafif kenar karartma
    w,h=size; yy,xx=np.mgrid[0:h,0:w]; d=np.sqrt(((xx-w/2)/(w/1.6))**2+((yy-h*0.42)/(h/1.4))**2)
    v=np.clip(1-0.22*np.clip(d-0.55,0,1)*1.8,0.75,1)[...,None]
    return Image.fromarray(np.clip(np.asarray(im)*v,0,255).astype(np.uint8)).convert("RGBA")

def dots(d,x,y,rows=3,cols=4,gap=24,r=4):
    for i in range(rows):
        for j in range(cols): cx,cy=x+j*gap,y+i*gap; d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=DOT)

def panel(c, top, curve=70):
    W,H=c.size; L=Image.new("RGBA",c.size,(0,0,0,0)); d=ImageDraw.Draw(L)
    d.rectangle((0,top+curve//2,W,H),fill=PANEL+(255,))
    d.ellipse((-W*0.25,top,W*1.25,top+curve*2.2),fill=PANEL+(255,))
    c.alpha_composite(L)
    B=Image.new("RGBA",c.size,(0,0,0,0)); d=ImageDraw.Draw(B)
    d.ellipse((-260,H-230,260,H+260),fill=GREENL+(255,))
    d.ellipse((W-240,H-200,W+260,H+300),fill=LILAC2+(150,))
    m=Image.new("L",c.size,0); ImageDraw.Draw(m).rectangle((0,top+curve,W,H),fill=255)
    c.paste(B,(0,0),Image.composite(B.split()[3],Image.new("L",c.size,0),m))

def swoosh(d,cx,y,w=150):
    d.rounded_rectangle((cx-w//2,y,cx+w//2,y+6),3,fill=GREEN)

def pill(d,cx,y,text,size=22):
    f=F("Montserrat-700.ttf",size); w=d.textlength(text,font=f)
    d.rounded_rectangle((cx-w/2-20,y,cx+w/2+20,y+size+20),(size+20)//2,fill=LILAC)
    d.text((cx,y+10),text,font=f,fill=NAVY,anchor="mt")

def fit(d,text,font,maxw,size):
    while d.textlength(text,font=F(font,size))>maxw and size>20: size-=2
    return F(font,size)

WALL6=(560,780,760,900); WALL4=(560,780,760,900); WALL5=(280,850,440,1000)

def cover(name, story=False):
    W,H=(1080,1920) if story else (1080,1350)
    ph=1220 if story else 900
    box=(0,560,923,560+round(923*ph/W)) if story else (0,700,923,700+round(923*ph/W))
    c=Image.new("RGBA",(W,H),PANEL+(255,)); c.alpha_composite(shot("6.jpg",box,(W,ph),WALL6))
    panel(c, ph-60); d=ImageDraw.Draw(c); dots(d,W-140,60)
    k=1.25 if story else 1.0
    y=ph+40 if not story else ph+50
    pill(d,W//2,y,"SÖYLEŞİ VE DENEYİM AKTARIMI  ·  9 EKİM 2026",int(22*k))
    d.text((W//2,y+int(62*k)),"Birlikte İyileşelim",font=F("Dancing-700.ttf",int(64*k)),fill=PURPLE,anchor="mt")
    d.text((W//2,y+int(140*k)),"FİBROMİYALJİ KADERİNİZ DEĞİL!",font=fit(d,"FİBROMİYALJİ KADERİNİZ DEĞİL!","Montserrat-800.ttf",980,int(58*k)),fill=NAVY,anchor="mt")
    swoosh(d,W//2,y+int(222*k))
    if story:
        d.text((W//2,y+int(250*k)),"Uzm. Dr. Hande Çelik Mehmetoğlu",font=F("Montserrat-700.ttf",32),fill=PURPLE,anchor="mt")
        d.text((W//2,y+int(250*k)+44),"&  Uzm. Dr. Ferda Firdin",font=F("Montserrat-700.ttf",32),fill=PURPLE,anchor="mt")
        d.text((W//2,y+int(250*k)+118),"Katılan herkese teşekkür ederiz.",font=F("Montserrat-500.ttf",34),fill=NAVY,anchor="mt")
        d.text((W//2,y+int(250*k)+176),"@drhandecelikmehmetoglu",font=F("Montserrat-700.ttf",30),fill=PURPLE,anchor="mt")
    else:
        d.text((W//2,y+250),"Uzm. Dr. Hande Çelik Mehmetoğlu  &  Uzm. Dr. Ferda Firdin",font=F("Montserrat-700.ttf",25),fill=PURPLE,anchor="mt")
    c.convert("RGB").save(os.path.join(OUT,name),quality=95)

def slide(src,box,wall,l1,l2,name,label):
    W,H=1080,1350; ph=1000
    c=Image.new("RGBA",(W,H),PANEL+(255,)); c.alpha_composite(shot(src,box,(W,ph),wall))
    panel(c, ph-60); d=ImageDraw.Draw(c); dots(d,W-140,60)
    y=ph+42
    pill(d,W//2,y,label,20)
    d.text((W//2,y+60),l1,font=fit(d,l1,"Montserrat-800.ttf",960,46),fill=NAVY,anchor="mt")
    swoosh(d,W//2,y+130,120)
    d.text((W//2,y+156),l2,font=F("Montserrat-500.ttf",27),fill=PURPLE,anchor="mt")
    c.convert("RGB").save(os.path.join(OUT,name),quality=95)

def crop(cx, headY, w=780, ph=1000, head_at=0.30):
    h=round(w*ph/1080); x0=int(min(max(cx-w/2,0),923-w)); y0=int(min(max(headY-head_at*h,0),2000-h))
    return (x0,y0,x0+w,y0+h)

cover("v3-1-kapak.jpg")
slide("4.jpg",crop(405,895),WALL4,"Uzm. Dr. Ferda Firdin","Fizik Tedavi ve Rehabilitasyon Uzmanı","v3-2-ferda.jpg","KONUĞUMUZ")
slide("6.jpg",crop(475,965),WALL6,"Uzm. Dr. Hande Çelik Mehmetoğlu","Aile Hekimliği Uzmanı · Psikoterapist","v3-3-hande.jpg","EV SAHİBİMİZ")
slide("5.jpg",crop(540,1040,800),WALL5,"Katılan herkese teşekkürler","Birlikte İyileşelim  ·  9 Ekim 2026","v3-4-tesekkur.jpg","TEŞEKKÜRLER")
cover("v3-hikaye.jpg",story=True)
print("ok")
