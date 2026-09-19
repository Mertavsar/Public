#!/usr/bin/env python3
"""2.5B parallaks motoru.

Derinlik haritasini K katmana ayirir ve kamera her hareket ettiginde her
katmani kendi derinligiyle orantili kaydirir. Sonuc: cekic arka plandan
bagimsiz hareket eder, yani kadraj degil sahne hacim kazanir.

Ayrica derinlige oturan toz zerrecikleri uretir; bunlar da ayni kamerayla
kayar, bu yuzden onde/arkada durduklari hissedilir.
"""
import cv2
import numpy as np

NEAR, FAR = 66.0, 245.0          # segment.py ile ayni araliktan gelir


def build_plate(src_bgr, hole, telea_radius=12):
    """Cekicin arkasindaki zemini doldurur.

    Silueti kaydirinca acilan serit yalnizca birkac piksel oldugu icin
    kritik olan kenarlardir: her satirda en yakin kenar pikselinin rengini
    ice dogru uzatir, derinlerde TELEA dolgusuna gecer.
    """
    telea = cv2.inpaint(src_bgr, hole, telea_radius, cv2.INPAINT_TELEA)

    H, W = hole.shape
    out = telea.astype(np.float32)
    src = src_bgr.astype(np.float32)

    # her satir icin: soldan ve sagdan en yakin gecerli pikselin rengi
    valid = hole == 0
    idx = np.arange(W)[None, :].repeat(H, 0)

    li = np.where(valid, idx, -1)
    np.maximum.accumulate(li, axis=1, out=li)
    ri = np.where(valid, idx, W)
    ri = np.minimum.accumulate(ri[:, ::-1], axis=1)[:, ::-1]

    rows = np.arange(H)[:, None].repeat(W, 1)
    lcol = src[rows, np.clip(li, 0, W - 1)]
    rcol = src[rows, np.clip(ri, 0, W - 1)]
    dl = (idx - li).astype(np.float32)
    dr = (ri - idx).astype(np.float32)
    dl[li < 0] = 1e6
    dr[ri >= W] = 1e6

    # en yakin kenardan uzat
    near = np.where((dl <= dr)[..., None], lcol, rcol)
    d = np.minimum(dl, dr)[..., None]
    # kenardan 45 px'e kadar uzatma, sonrasinda TELEA
    w = np.clip(1.0 - (d - 6.0) / 45.0, 0.0, 1.0)
    filled = near * w + out * (1 - w)
    out = np.where((hole > 0)[..., None], filled, src)
    return np.clip(out, 0, 255).astype(np.uint8)


class ParallaxRig:
    def __init__(self, src_rgb, depth, plate_rgb, n_layers=8, feather=2.5):
        """src_rgb, plate_rgb: HxWx3 uint8 (RGB). depth: HxW uint8."""
        self.H, self.W = depth.shape
        d = depth.astype(np.float32)
        # disparite: yakin = 1, uzak = 0
        disp = (FAR / np.clip(d, 1, None) - 1.0) / (FAR / NEAR - 1.0)
        self.disp = np.clip(disp, 0.0, 1.0)

        edges = np.linspace(0.0, 1.0, n_layers + 1)
        self.layer_disp = []
        self.layer_alpha = []
        for k in range(n_layers):
            lo, hi = edges[k], edges[k + 1]
            m = (self.disp >= lo) & (self.disp < hi if k < n_layers - 1 else self.disp <= hi)
            if m.sum() < 400:
                continue
            a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), feather)
            self.layer_alpha.append(a[..., None])
            self.layer_disp.append(float(self.disp[m].mean()))

        # en arkadaki katman tam kare olsun ki hicbir yerde delik kalmasin
        self.layer_alpha[0] = np.ones((self.H, self.W, 1), np.float32)
        self.plate = plate_rgb.astype(np.float32)
        self.set_source(src_rgb)

        self.order = np.argsort(self.layer_disp)        # uzaktan yakina

        # toz zerrecikleri: (x, y, disp, boyut, parlaklik, faz)
        rng = np.random.default_rng(5)
        n = 46
        self.dust = np.stack([
            rng.uniform(-0.15, 1.15, n) * self.W,
            rng.uniform(-0.15, 1.15, n) * self.H,
            rng.uniform(0.25, 1.0, n),
            rng.uniform(1.4, 4.2, n),
            rng.uniform(0.25, 1.0, n),
            rng.uniform(0, 6.283, n),
        ], axis=1).astype(np.float32)

    def set_source(self, src_rgb):
        """Kaynak kare degistiginde cagrilir. Katmanlar 4 kanalli tutulur:
        RGB + disparite, boylam tek warp ile hem goruntu hem derinlik tasinir."""
        s = src_rgb.astype(np.float32)
        self.layers = []
        for i, a in enumerate(self.layer_alpha):
            base = self.plate if i == 0 else s
            d = np.full((self.H, self.W, 1), self.layer_disp[i], np.float32)
            self.layers.append(np.concatenate([base, d], axis=2) * a)

    def set_background(self, bg_rgb):
        """Yalnizca en arka katmani gunceller (poster yazilari duvar duzlemindedir)."""
        d = np.full((self.H, self.W, 1), self.layer_disp[0], np.float32)
        self.layers[0] = np.concatenate([bg_rgb.astype(np.float32), d], axis=2) \
            * self.layer_alpha[0]

    def render(self, ox, oy, amp, zoom=0.0, rot_deg=0.0, pivot=None):
        """ox, oy: kamera kaymasi (-1..1). amp: en yakin katmanin px karsiligi.
        rot_deg: yalnizca on plana uygulanan hafif salinim.

        Dondurur: (HxWx3 RGB float, HxWx1 disparite) - disparite haritasi
        efektleri (metal parlamasi gibi) dogru yere oturtmak icin kullanilir."""
        out = np.zeros((self.H, self.W, 4), np.float32)
        cx, cy = self.W / 2.0, self.H / 2.0
        pvx, pvy = pivot if pivot else (cx, self.H * 0.92)
        for i in self.order:
            dsp = self.layer_disp[i]
            tx, ty = ox * amp * dsp, oy * amp * dsp
            sc = 1.0 + zoom * dsp
            ang = np.radians(rot_deg * max(0.0, (dsp - 0.45) / 0.55))
            ca, sa = np.cos(ang) * sc, np.sin(ang) * sc
            M = np.array([
                [ca, -sa, pvx - ca * pvx + sa * pvy + tx],
                [sa, ca, pvy - sa * pvx - ca * pvy + ty]], np.float32)
            rgbd = cv2.warpAffine(self.layers[i], M, (self.W, self.H),
                                  flags=cv2.INTER_LINEAR,
                                  borderMode=cv2.BORDER_REPLICATE)
            al = cv2.warpAffine(self.layer_alpha[i], M, (self.W, self.H),
                                flags=cv2.INTER_LINEAR,
                                borderMode=cv2.BORDER_REPLICATE)[..., None]
            out = rgbd + out * (1.0 - al)
        return out[..., :3], out[..., 3:4]

    def dust_overlay(self, t, ox, oy, amp):
        """Derinlige oturan toz zerrecikleri - ayni kamerayla kayar."""
        layer = np.zeros((self.H, self.W), np.float32)
        for (x, y, dsp, sz, br, ph) in self.dust:
            px = x + ox * amp * dsp + np.sin(t * 0.33 + ph) * 9.0 * dsp
            py = y + oy * amp * dsp - (t * 5.0 * dsp) + np.cos(t * 0.27 + ph * 1.7) * 6.0 * dsp
            py = (py % (self.H + 120)) - 60
            if not (-20 <= px < self.W + 20 and -20 <= py < self.H + 20):
                continue
            a = br * (0.45 + 0.55 * np.sin(t * 1.9 + ph)) * (0.35 + 0.65 * dsp)
            cv2.circle(layer, (int(px), int(py)), int(sz * (0.6 + dsp)),
                       float(max(a, 0.0)), -1, cv2.LINE_AA)
        return cv2.GaussianBlur(layer, (0, 0), 2.6)
