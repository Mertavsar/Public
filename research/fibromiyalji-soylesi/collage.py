"""Fibromiyalji söyleşisi için kolaj ve hikâye tasarımları.
Kullanım: python3 collage.py FONT_DIR OUT_DIR [hande ferda plaket salon]
Fotoğraf verilmezse yer tutucularla şablon üretir."""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

FD, OUT = sys.argv[1], sys.argv[2]
PH = sys.argv[3:]
NAVY = (10, 10, 72); LILAC = (183, 179, 240); LILAC_L = (220, 216, 250)
GREEN_L = (229, 245, 200); GREEN = (91, 138, 47); PURPLE = (133, 110, 227); WHITE = (255, 255, 255)
BG = (250, 249, 255)

def F(name, size): return ImageFont.truetype(os.path.join(FD, name), size)

def blobs(img):
    W, H = img.size
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.ellipse((-W*0.35, -H*0.12, W*0.45, H*0.22), fill=LILAC + (150,))
    d.ellipse((W*0.62, -H*0.10, W*1.35, H*0.20), fill=GREEN_L + (255,))
    d.ellipse((-W*0.30, H*0.80, W*0.40, H*1.15), fill=GREEN_L + (255,))
    d.ellipse((W*0.70, H*0.84, W*1.30, H*1.20), fill=LILAC + (130,))
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    img.alpha_composite(layer)
    d = ImageDraw.Draw(img)
    for r in range(3):
        for c in range(4):
            x, y = W - 150 + c*26, 70 + r*26
            d.ellipse((x, y, x+9, y+9), fill=PURPLE)

def cover(path, w, h, ybias=0.38):
    if path is None:
        im = Image.new("RGB", (w, h), (214, 210, 232)); d = ImageDraw.Draw(im)
        d.text((w/2, h/2), "Fotoğraf", font=F("Montserrat-500.ttf", 34), fill=(120, 112, 160), anchor="mm")
        return im
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    s = max(w/im.width, h/im.height)
    im = im.resize((round(im.width*s), round(im.height*s)), Image.LANCZOS)
    x = (im.width - w)//2; y = int((im.height - h)*ybias)
    return im.crop((x, y, x+w, y+h))

def paste_round(canvas, im, xy, r=28, border=8):
    x, y = xy; w, h = im.size
    sh = Image.new("RGBA", (w+60, h+60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((30, 36, 30+w, 36+h), r, fill=(40, 30, 90, 60))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (x-30, y-30))
    frame = Image.new("RGBA", (w+2*border, h+2*border), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle((0, 0, w+2*border-1, h+2*border-1), r+border, fill=WHITE)
    canvas.alpha_composite(frame, (x-border, y-border))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w-1, h-1), r, fill=255)
    canvas.paste(im, (x, y), m)

def header(c, top, scale=1.0):
    d = ImageDraw.Draw(c); W = c.width
    d.text((W/2, top), "Birlikte İyileşelim", font=F("Dancing-700.ttf", int(62*scale)), fill=NAVY, anchor="mt")
    y = top + int(78*scale)
    d.text((W/2, y), "FİBROMİYALJİ KADERİNİZ DEĞİL!", font=F("Montserrat-800.ttf", int(52*scale)), fill=NAVY, anchor="mt")
    y += int(72*scale)
    d.rounded_rectangle((W/2-int(70*scale), y, W/2+int(70*scale), y+5), 3, fill=GREEN)
    y += int(24*scale)
    d.text((W/2, y), "SÖYLEŞİ VE DENEYİM AKTARIMI  ·  9 EKİM 2026", font=F("Montserrat-700.ttf", int(25*scale)), fill=(74, 62, 140), anchor="mt")
    return y + int(40*scale)

def footer(c, y):
    d = ImageDraw.Draw(c); W = c.width
    d.text((W/2, y), "Katılan herkese teşekkür ederiz.", font=F("Montserrat-700.ttf", 34), fill=NAVY, anchor="mt")
    y += 56
    d.text((W/2, y), "Uzm. Dr. Hande Çelik Mehmetoğlu", font=F("Montserrat-700.ttf", 27), fill=(74, 62, 140), anchor="mt")
    y += 38
    d.text((W/2, y), "Konuğumuz: Uzm. Dr. Ferda Firdin · Fizik Tedavi ve Rehabilitasyon Uzmanı", font=F("Montserrat-500.ttf", 22), fill=(74, 62, 140), anchor="mt")

def pick(i): return PH[i] if i < len(PH) else None
HANDE, FERDA, PLAKET, SALON = pick(0), pick(1), pick(2), pick(3)

os.makedirs(OUT, exist_ok=True)
# 1) Instagram gönderisi 1080x1350: büyük Hande + Ferda ve plaket
c = Image.new("RGBA", (1080, 1350), BG + (255,)); blobs(c)
y = header(c, 70)
paste_round(c, cover(HANDE, 960, 560, 0.30), (60, y))
y2 = y + 560 + 30
paste_round(c, cover(FERDA, 465, 300, 0.30), (60, y2))
paste_round(c, cover(PLAKET, 465, 300, 0.33), (555, y2))
footer(c, y2 + 300 + 36)
c.convert("RGB").save(os.path.join(OUT, "1-gonderi-kolaj-1080x1350.jpg"), quality=93)

# 2) Hikâye 1080x1920: üstte plaket, altta iki konuşmacı
c = Image.new("RGBA", (1080, 1920), BG + (255,)); blobs(c)
y = header(c, 150)
paste_round(c, cover(PLAKET, 900, 690, 0.30), (90, y+10))
y2 = y + 10 + 690 + 36
paste_round(c, cover(HANDE, 435, 640, 0.25), (90, y2))
paste_round(c, cover(FERDA, 435, 640, 0.25), (555, y2))
footer(c, y2 + 640 + 46)
c.convert("RGB").save(os.path.join(OUT, "2-hikaye-1080x1920.jpg"), quality=93)

# 3) Kaydırmalı gönderi: kapak (salon) + tek tek kareler
c = Image.new("RGBA", (1080, 1350), BG + (255,)); blobs(c)
y = header(c, 70)
paste_round(c, cover(SALON, 960, 880, 0.40), (60, y))
d = ImageDraw.Draw(c); ty = y + 880 + 40
d.text((520, ty), "Söyleşiden kareler", font=F("Montserrat-700.ttf", 30), fill=NAVY, anchor="rt")
ax, ay = 545, ty + 18
d.line((ax, ay, ax + 44, ay), fill=NAVY, width=4)
d.polygon([(ax + 44, ay - 9), (ax + 58, ay), (ax + 44, ay + 9)], fill=NAVY)
c.convert("RGB").save(os.path.join(OUT, "3-kaydirmali-1-kapak.jpg"), quality=93)

def slide(path, line1, line2, name, ybias=0.35):
    c = Image.new("RGBA", (1080, 1350), BG + (255,)); blobs(c)
    paste_round(c, cover(path, 960, 1040, ybias), (60, 60))
    d = ImageDraw.Draw(c)
    d.text((540, 1150), line1, font=F("Montserrat-800.ttf", 36), fill=NAVY, anchor="mt")
    d.text((540, 1204), line2, font=F("Montserrat-500.ttf", 25), fill=(74, 62, 140), anchor="mt")
    d.rounded_rectangle((470, 1262, 610, 1267), 3, fill=GREEN)
    c.convert("RGB").save(os.path.join(OUT, name), quality=93)

slide(HANDE, "Uzm. Dr. Hande Çelik Mehmetoğlu", "Aile Hekimliği Uzmanı · Psikoterapist", "3-kaydirmali-2-hande.jpg")
slide(FERDA, "Konuğumuz: Uzm. Dr. Ferda Firdin", "Fizik Tedavi ve Rehabilitasyon Uzmanı", "3-kaydirmali-3-ferda.jpg")
slide(PLAKET, "Değerli konuğumuza teşekkür ederiz", "Birlikte İyileşelim · 9 Ekim 2026", "3-kaydirmali-4-tesekkur.jpg")
print("ok", len(PH), "foto")
