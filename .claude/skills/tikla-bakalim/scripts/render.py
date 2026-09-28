#!/usr/bin/env python3
"""
Tıkla Bakalım — bölüm dosyasından (bolum.json) yayına hazır dikey video.

    python3 render.py --bolum bolum.json --out video.mp4              # taslak (sessiz, tahmini zaman)
    python3 render.py --bolum bolum.json --vo ses.mp3 --out video.mp4 # seslendirmeyle
    python3 render.py --bolum bolum.json --kareler                    # sadece sahne kareleri (hızlı)

Sıra: metin → zamanlama → zaman çizelgesi → kareler (paralel) → ses yatağı →
mix → master → birleştirme → kapak → kalite kontrol.

Zamanlama
---------
Ses varsa: viral-edit/align.py metni sese kelime kelime hizalar (ASR yok).
Her sahnenin başlangıcı, o sahnenin ilk kelimesinin söylendiği an.
Ses yoksa: hece sayısından tahmin (4.3 hece/sn, voice-settings.md hedefi).
Tahmini sürüm TASLAKTIR — kurgu sese oturmaz, yalnızca akışı görmek içindir.

Ses yatağı, efekt, master viral-edit'ten gelir — aynı ölçülmüş zincir.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, wave
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
VE = os.path.normpath(os.path.join(HERE, "../../viral-edit/scripts"))
sys.path.insert(0, VE)
import align as AL          # noqa: E402

FPS = 30
SYL_RATE = 4.9              # konuşma içi hız; duraklamalarla toplamda ~4.3 hece/sn (voice-settings.md: 4.0–4.5)
PAUSE = {".": .32, "!": .32, "?": .36, "…": .4, ":": .22, ";": .22, ",": .14}
# Sahne tipinin kendi içinde kaç görsel olay ürettiği (tempo kontrolü için)
STEPS = {"karsilastir": 3, "sayi": 2, "takvim": 2, "grafik": 2}
SECTION_OF = {"hook": None, "ne": "ne", "neden": "neden", "etki": "etki", "kapanis": None}


def run(cmd, **kw):
    r = subprocess.run(cmd, **kw)
    if r.returncode:
        sys.exit(f"HATA: {' '.join(map(str, cmd))[:300]}")
    return r


def dur_of(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", path], capture_output=True, text=True).stdout)


# ---------------------------------------------------------------- doğrulama
def check_bolum(b):
    errs, warns = [], []
    sc = b.get("sahneler") or []
    if not sc:
        errs.append("sahneler boş")
    seen_end = False
    for i, s in enumerate(sc):
        tag = f"sahne {i+1} ({s.get('tip')})"
        if s.get("bolum") not in SECTION_OF:
            errs.append(f"{tag}: bolum '{s.get('bolum')}' — hook/ne/neden/etki/kapanis olmalı")
        say = (s.get("say") or "").strip()
        if not say:
            if "sure" not in s:
                errs.append(f"{tag}: 'say' yok ve 'sure' verilmemiş")
            seen_end = True
        elif seen_end:
            errs.append(f"{tag}: sessiz sahneden sonra konuşmalı sahne — sessiz sahneler sadece sonda olabilir")
        if re.search(r"\d", say):
            warns.append(f"{tag}: seslendirmede rakam var ('{say[:40]}…'). Sayıyı yazıyla yaz "
                         "(ElevenLabs ve hece sayımı için): '12,48' → 'on iki lira kırk sekiz kuruş'")
    order = [s.get("bolum") for s in sc]
    for a, bb in zip(["ne", "neden", "etki"], ["neden", "etki", None]):
        if a not in order:
            warns.append(f"'{a}' bölümü yok — format: ne oldu → neden oldu → bizi nasıl etkiler")
    idx = [order.index(x) for x in ["ne", "neden", "etki"] if x in order]
    if idx != sorted(idx):
        errs.append("bölüm sırası bozuk: ne → neden → etki olmalı")
    if not b.get("kaynaklar"):
        errs.append("kaynaklar boş — kaynaksız sayı ekrana çıkmaz (SKILL.md §2)")
    return errs, warns


# ---------------------------------------------------------------- zamanlama
def estimate(words):
    """Sessiz taslak için kelime zamanları: hece / hız + noktalama duraklaması."""
    t, out = 0.25, []
    for w in words:
        d = max(.2, AL.syllables_text(w) / SYL_RATE)
        out.append((w, t, t + d))
        t += d + PAUSE.get(w[-1], 0)
    return out


def timeline(b, vo=None):
    sc = b["sahneler"]
    spoken = [s for s in sc if (s.get("say") or "").strip()]
    text = " ".join(s["say"].strip() for s in spoken)
    words = text.split()
    if vo:
        items, *_rest = AL.align(vo, text)
        vo_dur = _rest[-3]
        if len(items) != len(words):
            sys.exit(f"HATA: hizalama {len(items)} kelime döndü, metin {len(words)} kelime")
        end = max(vo_dur, items[-1][2]) + .5
    else:
        items = estimate(words)
        end = items[-1][2] + .6
    colored = AL.colorize(items, b.get("vurgu", []))
    tl_words = [{"w": w, "s": round(s, 3), "e": round(e, 3), "c": c} for w, s, e, c in colored]
    # Her sahnenin başlangıcı = ilk kelimesinin başı (ilk sahne 0'dan)
    starts, k = [], 0
    for s in spoken:
        starts.append(0.0 if k == 0 else round(items[k][1] - .08, 3))
        k += len(s["say"].split())
    scenes, j = [], 0
    for s in sc:
        if (s.get("say") or "").strip():
            t0 = starts[j]
            t1 = starts[j + 1] if j + 1 < len(starts) else end
            j += 1
        else:
            t0, t1 = end, end + float(s["sure"])
            end = t1
        scenes.append({"t0": t0, "t1": t1, "tip": s["tip"], "bolum": s["bolum"],
                       "p": s.get("p", {}), "kaynak": s.get("kaynak")})
    return {"dur": round(end, 3), "scenes": scenes, "words": tl_words}, text


def tempo_report(tl):
    d = [s["t1"] - s["t0"] for s in tl["scenes"]]
    print(f"  {len(d)} sahne · {tl['dur']:.1f}s · ort {sum(d)/len(d):.2f}s · "
          f"en kısa {min(d):.2f}s · en uzun {max(d):.2f}s")
    w = []
    for i, (s, x) in enumerate(zip(tl["scenes"], d)):
        # Sahne içinde sırayla beliren öğe sayısı: her biri ekranı değiştirir
        p = s.get("p") or {}
        steps = max(STEPS.get(s["tip"], 1),
                    len(p.get("durumlar") or p.get("adimlar") or p.get("satirlar") or []),
                    (len(p.get("ogeler") or []) + 1) // 2)
        if x / steps > 5.0 or x > 10:
            w.append(f"sahne {i+1} ({s['tip']}) {x:.1f}s, {steps} adım — ekran uzun süre aynı kalıyor, "
                     "cümleyi böl veya adım ekle")
        if x < 1.2 and s["tip"] not in ("soru",):
            w.append(f"sahne {i+1} ({s['tip']}) {x:.1f}s — animasyon oturmadan geçiyor, cümleyi birleştir")
    if tl["dur"] > 75:
        w.append(f"süre {tl['dur']:.0f}s — Shorts için uzun; 45–60s hedef")
    return w


# ---------------------------------------------------------------- görüntü
def capture_still(tl_path, t, out, cover=False):
    cmd = ["node", f"{HERE}/capture.mjs", "--timeline", tl_path, "--still", f"{t:.3f}", "--out", out]
    if cover:
        cmd.append("--cover")
    run(cmd)


def render_video(tl_path, dur, out, work, jobs=4):
    n = int(round(dur * FPS))
    step = -(-n // jobs)
    parts = []
    def one(i):
        a, bnd = i * step, min(n, (i + 1) * step)
        p = f"{work}/parca{i}.mp4"
        run(["node", f"{HERE}/capture.mjs", "--timeline", tl_path, "--from", str(a), "--to", str(bnd),
             "--fps", str(FPS), "--out", p])
        return p
    with ThreadPoolExecutor(jobs) as ex:
        parts = list(ex.map(one, [i for i in range(jobs) if i * step < n]))
    lst = f"{work}/parcalar.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out])


# ---------------------------------------------------------------- ses
def audio_bed(tl, vo, work, mood="drive"):
    import build as VB     # viral-edit/build.py — aynı efekt/müzik/mix/master zinciri
    edl, prev = [], None
    for i, s in enumerate(tl["scenes"]):
        if i == 0:
            beat = "M"          # açılış vuruşu
        elif s["bolum"] != prev and s["bolum"] in ("neden", "etki"):
            beat = "R"          # bölüm geçişi: tırmanış + vuruş
        elif s["bolum"] != prev:
            beat = "M"
        else:
            beat = "m"
        edl.append({"o0": s["t0"], "beat": beat})
        prev = s["bolum"]
    if not vo:
        vo = f"{work}/sessiz.wav"
        with wave.open(vo, "w") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
            w.writeframes(b"\x00\x00" * int(48000 * tl["dur"]))
    return VB.audio(edl, tl["dur"], vo, work, mood=mood)


# ---------------------------------------------------------------- kontrol
def qc(out, tl, sheet):
    d = dur_of(out)
    print(f"  süre {d:.2f}s (çizelge {tl['dur']:.2f}s)")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)
    P = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)
    ok = True
    if I:
        print(f"  ses {float(I[-1]):.1f} LUFS · tepe {float(P[-1]) if P else 0:+.2f} dBFS")
        if P and float(P[-1]) > 0.0:
            print("  UYARI: tepe 0 dBFS üstünde — kırpılma"); ok = False
    if abs(d - tl["dur"]) > .2:
        print("  UYARI: video süresi çizelgeyle uyuşmuyor"); ok = False
    # sahne ortalarından kontak sayfası
    tmp = tempfile.mkdtemp()
    for i, s in enumerate(tl["scenes"]):
        t = s["t0"] + (s["t1"] - s["t0"]) * .85
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", out, "-frames:v", "1",
             "-vf", "scale=270:480", f"{tmp}/k{i:03d}.jpg"])
    cols = min(6, len(tl["scenes"]))
    rows = -(-len(tl["scenes"]) // cols)
    run(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", f"{tmp}/k%03d.jpg",
         "-vf", f"tile={cols}x{rows}:padding=6:color=black", "-frames:v", "1", sheet])
    shutil.rmtree(tmp)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bolum", required=True)
    ap.add_argument("--vo", help="seslendirme (mp3/wav). Yoksa sessiz taslak üretilir.")
    ap.add_argument("--out", help="video.mp4 (varsayılan: bolum klasöründe)")
    ap.add_argument("--kareler", action="store_true", help="sadece her sahneden bir kare (hızlı önizleme)")
    ap.add_argument("--jobs", type=int, default=max(1, min(4, os.cpu_count() or 1)))
    ap.add_argument("--mood", choices=["drive", "sad"], default="drive")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    b = json.load(open(a.bolum, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(a.bolum))
    out = a.out or os.path.join(base, "cikti", "video.mp4" if a.vo else "taslak.mp4")
    odir = os.path.dirname(os.path.abspath(out))
    os.makedirs(odir, exist_ok=True)
    work = tempfile.mkdtemp(prefix="tb_")

    print("1/6 bölüm dosyası kontrol")
    errs, warns = check_bolum(b)
    for w in warns: print("  UYARI:", w)
    for e in errs: print("  HATA:", e)
    if errs and not a.force:
        sys.exit("Durdu. Hataları düzelt.")

    print("2/6 zamanlama " + ("(sese hizalı)" if a.vo else "(TAHMİNİ — ses yok, taslak)"))
    tl, text = timeline(b, a.vo)
    open(os.path.join(odir, "metin.txt"), "w", encoding="utf-8").write(
        "\n\n".join(s["say"].strip() for s in b["sahneler"] if (s.get("say") or "").strip()) + "\n")
    tl_path = os.path.join(odir, "cizelge.json")
    json.dump(tl, open(tl_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for w in tempo_report(tl): print("  UYARI:", w)

    if a.kareler:
        print("3/3 sahne kareleri")
        kd = os.path.join(odir, "kareler"); os.makedirs(kd, exist_ok=True)
        with ThreadPoolExecutor(a.jobs) as ex:
            list(ex.map(lambda x: capture_still(tl_path, x[1]["t0"] + (x[1]["t1"] - x[1]["t0"]) * .85,
                                                f"{kd}/{x[0]+1:02d}-{x[1]['tip']}.jpg"),
                        enumerate(tl["scenes"])))
        print(f"-> {kd}")
        return

    print(f"3/6 kareler ({int(tl['dur']*FPS)} kare, {a.jobs} iş parçacığı)")
    silent = f"{work}/goruntu.mp4"
    render_video(tl_path, tl["dur"], silent, work, a.jobs)

    print("4/6 ses yatağı + mix + master")
    mix = audio_bed(tl, a.vo, work, a.mood)

    print("5/6 birleştirme + kapak")
    run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", mix, "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{tl['dur']:.3f}",
         "-movflags", "+faststart", out])
    if b.get("kapak"):
        ctl = f"{work}/kapak.json"
        json.dump({"dur": 1, "scenes": [{"t0": 0, "t1": 1, "tip": "kapak", "bolum": "hook",
                                         "p": b["kapak"]}], "words": []}, open(ctl, "w"), ensure_ascii=False)
        capture_still(ctl, .5, os.path.join(odir, "kapak.png"), cover=True)

    print("6/6 kalite kontrol")
    ok = qc(out, tl, os.path.join(odir, "kontrol.jpg"))
    shutil.rmtree(work, ignore_errors=True)
    print(("TAMAM" if ok else "SORUNLU") + f" -> {out}")
    if not a.vo:
        print("NOT: bu bir TASLAK. Zamanlama tahmini; seslendirme gelince --vo ile yeniden çalıştır.")


if __name__ == "__main__":
    main()
