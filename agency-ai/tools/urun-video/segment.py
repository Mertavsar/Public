#!/usr/bin/env python3
"""Tek karelik urun gorselini derinlik katmanlarina ayirir.

Cikti:
  depth.png        - 8 bit derinlik haritasi (0 = kameraya en yakin)
  mask_debug.png   - gorsel kontrol
  bgplate.png      - cekic ve kaya kaldirilip arkasi doldurulmus zemin

Bu katmanlar parallaks render'inda kullanilir: kamera hareket ettiginde
cekic arka plandan bagimsiz kayar, yani gercek hacim hissi olusur.
"""
import sys
import cv2
import numpy as np

from parallax import build_plate


def largest_component(mask):
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    if n <= 1:
        return mask
    k = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    return (lab == k).astype(np.uint8)


def clean(mask, close=9, open_=5):
    m = mask.astype(np.uint8)
    if close:
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE,
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close, close)))
    if open_:
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN,
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_, open_)))
    return m


def main(src_path, out_prefix=""):
    bgr = cv2.imread(src_path)
    H, W = bgr.shape[:2]
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.int16)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    Hh, Ss, Vv = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)

    # ---------------------------------------------------------------- sap
    # Turuncu deri sap: yuksek doygunluk, sicak ton
    handle = ((Ss > 105) & (Hh >= 4) & (Hh <= 22) & (Vv > 45)).astype(np.uint8)
    handle[:430, :] = 0                      # kafanin ustunde sap yok
    handle[:, :390] = 0                      # sap dar bir seritte; sagdaki koyu
    handle[:, 700:] = 0                      # panel turuncuya yakin, disari at
    handle = clean(handle, 13, 7)
    handle = largest_component(handle)
    handle = cv2.morphologyEx(handle, cv2.MORPH_CLOSE,
                              cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    # sapin her satirdaki sol/sag sinirini doldur (ip sarimlari arasi bosluklar)
    for y in range(430, H):
        col = np.nonzero(handle[y])[0]
        if len(col) > 1:
            handle[y, col[0]:col[-1] + 1] = 1

    # ---------------------------------------------------------------- kafa
    # GrabCut: kafanin kabaca sigdigi dikdortgen
    gmask = np.zeros((H, W), np.uint8)
    gmask[:] = cv2.GC_BGD
    rx0, ry0, rx1, ry1 = 170, 60, 890, 615
    gmask[ry0:ry1, rx0:rx1] = cv2.GC_PR_BGD

    # kesin on plan: kafanin govdesinde guvenli bir cekirdek
    core = np.zeros((H, W), np.uint8)
    cv2.fillPoly(core, [np.array([(330, 230), (690, 195), (740, 420), (360, 470)])], 1)
    gmask[core > 0] = cv2.GC_FGD
    # kesin arka plan: dikdortgenin disi zaten GC_BGD
    gmask[:55, :] = cv2.GC_BGD
    gmask[:, :150] = cv2.GC_BGD
    gmask[:, 910:] = cv2.GC_BGD
    gmask[640:, :] = cv2.GC_BGD

    bgdm, fgdm = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(bgr, gmask, None, bgdm, fgdm, 6, cv2.GC_INIT_WITH_MASK)
    head = np.where((gmask == cv2.GC_FGD) | (gmask == cv2.GC_PR_FGD), 1, 0).astype(np.uint8)
    head = clean(head, 15, 9)
    head = largest_component(head)
    head = cv2.morphologyEx(head, cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))

    hammer = np.clip(head + handle, 0, 1).astype(np.uint8)
    hammer = cv2.morphologyEx(hammer, cv2.MORPH_CLOSE,
                              cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35)))

    # ---------------------------------------------------------------- kaya
    # Alt banttaki tasli zemin: dokulu ve duvardan koyu
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    tex = cv2.Laplacian(cv2.GaussianBlur(gray, (5, 5), 0), cv2.CV_32F)
    tex = cv2.GaussianBlur(np.abs(tex), (31, 31), 0)
    rock = ((tex > 3.0) | (gray < 120)).astype(np.uint8)
    rock[:1230, :] = 0
    rock = clean(rock, 41, 21)
    rock = largest_component(rock)
    # kayanin ust sinirini sutun bazinda bul, medyanla yumusat, altini doldur
    top = np.full(W, H, np.int32)
    for x in range(W):
        col = np.nonzero(rock[:, x])[0]
        if len(col):
            top[x] = col[0]
    valid = top < H
    if valid.any():
        top[~valid] = int(np.median(top[valid]))
        top = cv2.medianBlur(top.astype(np.float32).reshape(1, -1), 1).ravel()
        k = 61
        pad = np.pad(top, k // 2, mode="edge")
        top = np.convolve(pad, np.ones(k) / k, mode="valid").astype(int)
        rock[:] = 0
        for x in range(W):
            rock[max(top[x], 0):, x] = 1
    rock[hammer > 0] = 0

    # ---------------------------------------------------------------- bitki
    plant = ((Hh >= 25) & (Hh <= 70) & (Ss > 45) & (Vv > 30)).astype(np.uint8)
    plant[:800, :] = 0
    plant[:, 420:] = 0
    plant = clean(plant, 31, 11)
    plant[rock > 0] = 0
    plant[hammer > 0] = 0

    # ---------------------------------------------------------------- derinlik
    # 0 = en yakin, 255 = en uzak
    depth = np.full((H, W), 245, np.float32)          # duvar
    depth[:, 760:] = np.minimum(depth[:, 760:], 232)  # sagdaki koyu panel biraz onde
    depth[plant > 0] = 196

    ys = np.arange(H, dtype=np.float32)[:, None]
    # kaya: ust kenari uzak, one dogru yaklasiyor
    rock_d = np.clip(158 - (ys - 1230) * 0.055, 100, 158)
    depth = np.where(rock > 0, np.broadcast_to(rock_d, (H, W)), depth)
    # sap: tabanda kayayla ayni derinlikte, yukari dogru yaklasiyor
    handle_d = np.clip(150 - (1380 - ys) * 0.085, 88, 150)
    depth = np.where(handle > 0, np.broadcast_to(handle_d, (H, W)), depth)
    # kafa: en yakin; blok acili durdugu icin soldan saga hafif uzaklasir
    xs = np.arange(W, dtype=np.float32)[None, :]
    head_d = np.clip(66 + (xs - 220) * 0.030, 66, 108)
    depth = np.where(head > 0, np.broadcast_to(head_d, (H, W)), depth)

    depth = cv2.GaussianBlur(depth, (0, 0), 3.0)
    depth_u8 = np.clip(depth, 0, 255).astype(np.uint8)

    # ---------------------------------------------------------------- zemin plakasi
    hole = cv2.dilate(np.clip(hammer + rock, 0, 1),
                      cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
    bgplate = build_plate(bgr, hole)

    # ---------------------------------------------------------------- cikti
    cv2.imwrite(out_prefix + "depth.png", depth_u8)
    cv2.imwrite(out_prefix + "bgplate.png", bgplate)
    np.savez_compressed(out_prefix + "masks.npz", head=head, handle=handle,
                        rock=rock, plant=plant, hammer=hammer)

    dbg = bgr.copy()
    for m, col in [(head, (0, 0, 255)), (handle, (0, 200, 255)),
                   (rock, (255, 0, 0)), (plant, (0, 255, 0))]:
        e = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((5, 5), np.uint8))
        dbg[e > 0] = col
    cv2.imwrite(out_prefix + "mask_debug.png", dbg)

    print("alanlar (px): head=%d handle=%d rock=%d plant=%d"
          % (head.sum(), handle.sum(), rock.sum(), plant.sum()))
    print("derinlik araligi:", int(depth_u8.min()), int(depth_u8.max()))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "")
