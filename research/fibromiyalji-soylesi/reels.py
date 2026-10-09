"""Söyleşi Reels videosu (1080x1920, 30fps). Kullanım: python3 reels.py FONT_DIR IMG_DIR OUT_MP4"""
import sys, os, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import imageio_ffmpeg
FD, IMG, OUTMP4 = sys.argv[1:4]
W, H, FPS = 1080, 1920, 30
NAVY=(10,10,72); PURPLE=(86,64,170); DOT=(133,110,227); LILAC=(205,200,250); LILAC2=(183,179,240)
GREENL=(229,245,200); GREEN=(91,138,47); PANEL=(251,250,255); WHITE=(255,255,255)
def F(n,s): return ImageFont.truetype(os.path.join(FD,n),s)
def clamp(x,a=0,b=1): return max(a,min(b,x))
def eo(t): t=clamp(t); return 1-(1-t)**3          # ease-out cubic
def eio(t): t=clamp(t); return t*t*(3-2*t)         # smoothstep

# ---------- fotoğraf hazırlığı ----------
def grade(im, wall):
    a=np.asarray(im).astype(np.float32); x0,y0,x1,y1=wall
    ref=a[y0:y1,x0:x1].reshape(-1,3).mean(0); a=a*(ref.mean()/ref)**0.8
    a=255*((np.clip(a,0,255)/255)**0.92)
    im=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
    return ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.07)).enhance(1.06)
def base(src, y0, wall):
    im=grade(Image.open(os.path.join(IMG,src)).convert("RGB"), wall)
    ch=round(im.width*16/9); y0=max(0,min(y0,im.height-ch))
    im=im.crop((0,y0,im.width,y0+ch)).resize((1296,2304),Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=1.4,percent=50,threshold=2))
def kb(b, z, cx, cy):
    bw,bh=b.size; w,h=bw/z,bh/z
    x=clamp(cx*bw-w/2,0,bw-w); y=clamp(cy*bh-h/2,0,bh-h)
    return b.resize((W,H),Image.LANCZOS,box=(x,y,x+w,y+h))
WALL6=(560,780,760,900); WALL4=(560,780,760,900); WALL5=(280,850,440,1000)
B_SALON=base("6.jpg",250,WALL6); B_FERDA=base("4.jpg",300,WALL4); B_PLAKET=base("5.jpg",359,WALL5)

# alt kısım karartma (yazı okunurluğu)
grad=np.zeros((H,1),np.float32)
for y in range(H): grad[y]=clamp((y/H-0.55)/0.45)**1.6*0.55
GRAD=Image.fromarray((grad*255).astype(np.uint8).repeat(W,1),"L")
def darken(im):
    im=im.convert("RGBA"); l=Image.new("RGBA",(W,H),NAVY+(0,)); l.putalpha(GRAD); im.alpha_composite(l); return im

# ---------- yazı parçaları (önceden çizilir) ----------
def text_img(text,font,fill,pad=6):
    f=font; l,t,r,b=f.getbbox(text); im=Image.new("RGBA",(r-l+2*pad,b-t+2*pad),(0,0,0,0))
    ImageDraw.Draw(im).text((pad-l,pad-t),text,font=f,fill=fill); return im
def pill_img(text,size=26):
    f=F("Montserrat-700.ttf",size); tw=f.getlength(text); h=size+24
    im=Image.new("RGBA",(int(tw+44),h),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,im.width-1,h-1),h//2,fill=LILAC); d.text((22,12),text,font=f,fill=NAVY); return im
def put(c, el, cx, y, a, dy=0, anchor="c"):
    if a<=0: return
    e=el
    if a<1: e=el.copy(); e.putalpha(el.getchannel("A").point(lambda v:int(v*a)))
    x=int(cx-e.width/2) if anchor=="c" else int(cx)
    c.alpha_composite(e,(x,int(y+dy)))

def brand_bg():
    c=Image.new("RGBA",(W,H),PANEL+(255,)); L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    d.ellipse((-420,-300,560,560),fill=LILAC2+(160,)); d.ellipse((620,-260,1500,520),fill=GREENL+(255,))
    d.ellipse((-380,1460,420,2260),fill=GREENL+(255,)); d.ellipse((700,1520,1500,2300),fill=LILAC2+(140,))
    c.alpha_composite(L.filter(ImageFilter.GaussianBlur(1))); d=ImageDraw.Draw(c)
    for i in range(3):
        for j in range(4): x,y=W-170+j*30,120+i*30; d.ellipse((x-5,y-5,x+5,y+5),fill=DOT)
    return c
BG=brand_bg()

# açılış
I_PILL=pill_img("SÖYLEŞİ VE DENEYİM AKTARIMI  ·  9 EKİM 2026",26)
I_SCRIPT=text_img("Birlikte İyileşelim",F("Dancing-700.ttf",96),PURPLE)
I_T1=text_img("FİBROMİYALJİ",F("Montserrat-800.ttf",118),NAVY)
I_T2=text_img("KADERİNİZ",F("Montserrat-800.ttf",118),NAVY)
I_T3=text_img("DEĞİL!",F("Montserrat-800.ttf",118),NAVY)
I_N1=text_img("Uzm. Dr. Hande Çelik Mehmetoğlu",F("Montserrat-700.ttf",38),PURPLE)
I_N2=text_img("&  Uzm. Dr. Ferda Firdin",F("Montserrat-700.ttf",38),PURPLE)
# kapanış
E_T1=text_img("Katılan herkese",F("Montserrat-800.ttf",76),NAVY)
E_T2=text_img("teşekkür ederiz.",F("Montserrat-800.ttf",76),NAVY)
E_H=text_img("@drhandecelikmehmetoglu",F("Montserrat-700.ttf",40),PURPLE)

def lower_third(label,name,sub):
    p=pill_img(label,24)
    fs=58
    while F("Montserrat-800.ttf",fs).getlength(name)>860: fs-=2
    n=text_img(name,F("Montserrat-800.ttf",fs),NAVY); s=text_img(sub,F("Montserrat-500.ttf",32),PURPLE)
    h=p.height+n.height+s.height+110; card=Image.new("RGBA",(W-120,h),(0,0,0,0))
    sh=Image.new("RGBA",(W-60,h+60),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((30,40,W-90,h+30),36,fill=(10,10,72,90))
    sh=sh.filter(ImageFilter.GaussianBlur(16))
    d=ImageDraw.Draw(card); d.rounded_rectangle((0,0,card.width-1,h-1),36,fill=PANEL+(250,))
    card.alpha_composite(p,(48,40)); card.alpha_composite(n,(42,40+p.height+14))
    d.rounded_rectangle((50,40+p.height+14+n.height+10,150,40+p.height+14+n.height+16),3,fill=GREEN)
    card.alpha_composite(s,(44,40+p.height+14+n.height+32))
    out=Image.new("RGBA",(W,h+60),(0,0,0,0)); out.alpha_composite(sh,(30,0)); out.alpha_composite(card,(60,10)); return out
LT_SALON=lower_third("9 EKİM 2026  ·  BURSA","Söyleşimiz gerçekleşti","Fibromiyaljiyle yaşamda güncel yaklaşımlar")
LT_FERDA=lower_third("KONUĞUMUZ","Uzm. Dr. Ferda Firdin","Fizik Tedavi ve Rehabilitasyon Uzmanı")
LT_HANDE=lower_third("EV SAHİBİMİZ","Uzm. Dr. Hande Çelik Mehmetoğlu","Aile Hekimliği Uzmanı · Psikoterapist")
LT_PLAKET=lower_third("TEŞEKKÜRLER","Değerli konuğumuza","katkıları için teşekkür ederiz")

# ---------- sahneler ----------
def s_intro(t,d):
    c=BG.copy(); y0=560
    put(c,I_PILL,W/2,y0,eo((t-0.15)/0.5),30*(1-eo((t-0.15)/0.5)))
    put(c,I_SCRIPT,W/2,y0+110,eo((t-0.45)/0.6),40*(1-eo((t-0.45)/0.6)))
    for k,el in enumerate((I_T1,I_T2,I_T3)):
        a=eo((t-0.75-k*0.18)/0.55); put(c,el,W/2,y0+250+k*140,a,60*(1-a))
    gw=int(180*eo((t-1.45)/0.5)); dr=ImageDraw.Draw(c)
    if gw>0: dr.rounded_rectangle((W/2-gw/2,y0+690,W/2+gw/2,y0+699),4,fill=GREEN)
    a=eo((t-1.7)/0.5); put(c,I_N1,W/2,y0+740,a,20*(1-a)); put(c,I_N2,W/2,y0+795,a,20*(1-a))
    return c
def s_photo(b,z0,z1,c0,c1,lt):
    def f(t,d):
        p=eio(t/d); z=z0+(z1-z0)*p; cx=c0[0]+(c1[0]-c0[0])*p; cy=c0[1]+(c1[1]-c0[1])*p
        c=darken(kb(b,z,cx,cy)); a=eo((t-0.35)/0.55)
        put(c,lt,W/2,H-lt.height-400,a,70*(1-a)); return c
    return f
def s_end(t,d):
    c=BG.copy(); y0=720
    put(c,I_SCRIPT,W/2,y0,eo(t/0.6),30*(1-eo(t/0.6)))
    a=eo((t-0.3)/0.55); put(c,E_T1,W/2,y0+150,a,50*(1-a))
    a=eo((t-0.45)/0.55); put(c,E_T2,W/2,y0+250,a,50*(1-a))
    gw=int(160*eo((t-0.9)/0.5)); dr=ImageDraw.Draw(c)
    if gw>0: dr.rounded_rectangle((W/2-gw/2,y0+380,W/2+gw/2,y0+389),4,fill=GREEN)
    a=eo((t-1.1)/0.5); put(c,E_H,W/2,y0+430,a,20*(1-a)); return c

SC=[(3.3,s_intro),
    (3.8,s_photo(B_SALON,1.00,1.10,(0.5,0.50),(0.5,0.46),LT_SALON)),
    (3.6,s_photo(B_FERDA,1.10,1.24,(0.42,0.40),(0.45,0.37),LT_FERDA)),
    (3.6,s_photo(B_SALON,1.20,1.34,(0.52,0.47),(0.52,0.43),LT_HANDE)),
    (3.4,s_photo(B_PLAKET,1.05,1.16,(0.58,0.45),(0.58,0.42),LT_PLAKET)),
    (3.2,s_end)]
XF=0.4
starts=[];t=0
for d,_ in SC: starts.append(t); t+=d
TOTAL=t
def frame(t):
    out=None
    for i,(d,fn) in enumerate(SC):
        s=starts[i]; e=s+d
        if s-XF<=t<e:
            img=fn(t-s if t>=s else 0, d).convert("RGB")
            if out is None: out=img
            else: out=Image.blend(out,img,clamp((t-(s-XF))/XF))
    return out

ff=imageio_ffmpeg.get_ffmpeg_exe()
p=subprocess.Popen([ff,"-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
   "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest",
   "-c:v","libx264","-preset","slow","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k",
   "-movflags","+faststart",OUTMP4],stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
N=int(TOTAL*FPS)
for i in range(N):
    fr=frame(i/FPS); p.stdin.write(fr.tobytes())
    if i in (int(1.9*FPS),int(5.5*FPS),int(9*FPS),int(12.5*FPS),int(16*FPS),int((TOTAL-0.5)*FPS)):
        fr.save(OUTMP4.replace(".mp4",f"_kare{i:03d}.jpg"),quality=88)
p.stdin.close(); p.wait(); print("ok",N,"kare",round(TOTAL,1),"sn")
