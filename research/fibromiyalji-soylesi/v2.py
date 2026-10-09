"""v2: fotoğraflar doğal çözünürlükte, tam ekran; sade yazı katmanı.
Kullanım: python3 v2.py FONT_DIR IMG_DIR OUT_DIR"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
FD, IMG, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
NAVY=(10,10,72); LILAC=(200,196,250); GREEN=(160,205,110); WHITE=(255,255,255)
def F(n,s): return ImageFont.truetype(os.path.join(FD,n),s)

def prep(src, y0, w=1080, h=1350):
    im=Image.open(os.path.join(IMG,src)).convert("RGB")
    ch=round(im.width*h/w); y0=max(0,min(y0,im.height-ch))
    im=im.crop((0,y0,im.width,y0+ch)).resize((w,h),Image.LANCZOS)
    # hafif düzeltme: sarılığı biraz al, kontrast ve netlik
    r,g,b=im.split(); b=b.point(lambda v:min(255,int(v*1.05))); r=r.point(lambda v:int(v*0.98)); im=Image.merge("RGB",(r,g,b))
    im=ImageEnhance.Contrast(im).enhance(1.06); im=ImageEnhance.Color(im).enhance(1.05)
    return im.filter(ImageFilter.UnsharpMask(radius=1.2,percent=40,threshold=3)).convert("RGBA")

def shade(im, start=0.52, maxa=225):
    w,h=im.size; g=Image.new("L",(1,h),0)
    for y in range(h):
        t=(y/h-start)/(1-start); g.putpixel((0,y),int(max(0,min(1,t))**1.4*maxa))
    layer=Image.new("RGBA",(w,h),NAVY+(0,)); layer.putalpha(g.resize((w,h)))
    im.alpha_composite(layer); return im

def pill(d,x,y,text,size=24):
    f=F("Montserrat-700.ttf",size); w=d.textlength(text,font=f)
    d.rounded_rectangle((x,y,x+w+36,y+size+22),(size+22)//2,fill=LILAC)
    d.text((x+18,y+11),text,font=f,fill=NAVY)

def cover(src,y0,name,story=False):
    W,H=(1080,1920) if story else (1080,1350)
    im=shade(prep(src,y0,W,H), 0.50 if story else 0.45); d=ImageDraw.Draw(im)
    base=H-(470 if story else 400)
    pill(d,64,base,"SÖYLEŞİ  ·  9 EKİM 2026")
    d.text((64,base+80),"Fibromiyalji",font=F("Montserrat-800.ttf",78),fill=WHITE)
    d.text((64,base+168),"kaderiniz değil.",font=F("Montserrat-800.ttf",78),fill=WHITE)
    d.rectangle((64,base+270,150,base+275),fill=GREEN)
    d.text((64,base+296),"Uzm. Dr. Hande Çelik Mehmetoğlu  ×  Uzm. Dr. Ferda Firdin",font=F("Montserrat-500.ttf",27),fill=(230,228,250))
    if story:
        d.text((64,base+344),"Katılan herkese teşekkür ederiz.",font=F("Montserrat-500.ttf",27),fill=(230,228,250))
    im.convert("RGB").save(os.path.join(OUT,name),quality=94)

def slide(src,y0,l1,l2,name):
    im=shade(prep(src,y0),0.62,215); d=ImageDraw.Draw(im)
    d.text((64,1350-170),l1,font=F("Montserrat-800.ttf",44),fill=WHITE)
    d.text((64,1350-108),l2,font=F("Montserrat-500.ttf",27),fill=(230,228,250))
    d.rectangle((64,1350-195,130,1350-191),fill=GREEN)
    im.convert("RGB").save(os.path.join(OUT,name),quality=94)

cover("6.jpg",560,"v2-1-kapak.jpg")
slide("4.jpg",500,"Uzm. Dr. Ferda Firdin","Fizik Tedavi ve Rehabilitasyon Uzmanı","v2-2-ferda.jpg")
slide("6.jpg",700,"Uzm. Dr. Hande Çelik Mehmetoğlu","Aile Hekimliği Uzmanı · Psikoterapist","v2-3-hande.jpg")
slide("5.jpg",760,"Değerli konuğumuza teşekkürler","Birlikte İyileşelim söyleşileri","v2-4-tesekkur.jpg")
cover("6.jpg",250,"v2-hikaye.jpg",story=True)
print("ok")
