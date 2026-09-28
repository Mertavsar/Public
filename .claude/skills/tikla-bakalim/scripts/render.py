#!/usr/bin/env python3
"""
Tıkla Bakalım — bölüm dosyasından (bolum.json) yayına hazır animasyonlu video.

    python3 render.py --bolum bolum.json --kareler                    # her sahneden bir kare (~10 sn)
    python3 render.py --bolum bolum.json                              # sessiz taslak, tahmini zaman
    python3 render.py --bolum bolum.json --vo ses.mp3 [--sikistir]    # final
    python3 render.py --bolum bolum.json --vo ses.mp3 --muzik --efekt # kullanıcı isterse

Format bolum.json'daki "format" alanından: "yatay" (1920x1080, altın videosu gibi,
varsayılan) veya "dikey" (1080x1920 Shorts/Reels). --format ile ezilebilir.

Sıra: kontrol → (duraksama kısaltma) → zamanlama → çizelge → kareler (paralel)
→ ses → birleştirme → 30 MiB sınırı → kapak → kalite kontrol.

Zamanlama
---------
Ses varsa: viral-edit/sentalign.py — cümle sınırlarını sesin duraklamalarına
oturtur, kelimeleri cümle içinde hizalar (align.py uzun seste 1.5 sn'ye kadar
kayıyordu, explainer/README.md). Her sahnenin başı ilk kelimesinin anı.
Ses yoksa: hece sayısından tahmin. Tahmini sürüm TASLAKTIR.

Ses — KULLANICI KURALI (viral-edit SKILL.md §0)
------------------------------------------------
Varsayılan: sadece seslendirme. Müzik ve efekt sesi EKLENMEZ.
Kullanıcı o video için açıkça isterse --muzik / --efekt. Müzik (duck sonrası)
ölçülerek seslendirmenin 21 LU altına oturtulur (--muzik-seviye); efekt sadece
bölüm geçişinde yumuşak whoosh + abone/beğen tıkı.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, wave
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VE = os.path.normpath(os.path.join(HERE, "../../viral-edit/scripts"))
sys.path.insert(0, VE)
import align as AL          # noqa: E402

FPS = 30
SYL_RATE = 4.9              # konuşma içi hız; duraklamalarla toplamda ~4.3 hece/sn (voice-settings.md: 4.0–4.5)
PAUSE = {".": .32, "!": .32, "?": .36, "…": .4, ":": .22, ";": .22, ",": .14}
SECTIONS = ("hook", "ne", "neden", "etki", "kapanis")
# Sahne tipinin kendi içinde kaç görsel olay ürettiği (tempo kontrolü için)
STEPS = {"karsilastir": 3, "sayi": 2, "takvim": 2, "grafik": 2}
# Teslim yolu 30 MiB üstünü reddediyor (explainer/README.md)
MAX_BYTES = 29.5 * 1024 * 1024
TEMPO = {  # format: (adım başına en uzun durağan sn, toplam süre uyarısı)
    "dikey": (5.0, 75),
    "yatay": (9.0, 600),
}


def run(cmd, **kw):
    r = subprocess.run(cmd, **kw)
    if r.returncode:
        sys.exit(f"HATA: {' '.join(map(str, cmd))[:300]}")
    return r


def dur_of(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", path], capture_output=True, text=True).stdout)


def lufs(path):
    r = subprocess.run(["ffmpeg", "-nostdin", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    v = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)
    return float(v[-1]) if v else None


# ---------------------------------------------------------------- doğrulama
def check_bolum(b):
    errs, warns = [], []
    sc = b.get("sahneler") or []
    if not sc:
        errs.append("sahneler boş")
    seen_end = False
    for i, s in enumerate(sc):
        tag = f"sahne {i+1} ({s.get('tip')})"
        if s.get("bolum") not in SECTIONS:
            errs.append(f"{tag}: bolum '{s.get('bolum')}' — {'/'.join(SECTIONS)} olmalı")
        say = (s.get("say") or "").strip()
        if not say:
            if "sure" not in s:
                errs.append(f"{tag}: 'say' yok ve 'sure' verilmemiş")
            seen_end = True
        elif seen_end:
            errs.append(f"{tag}: sessiz sahneden sonra konuşmalı sahne — sessiz sahneler sadece sonda olabilir")
        if re.search(r"\d", say):
            warns.append(f"{tag}: seslendirmede rakam var ('{say[:40]}…'). Sayıyı yazıyla yaz "
                         "(ElevenLabs ve hece sayımı için), ekranda rakam için 'altyazi' eşlemesi kullan")
    order = [s.get("bolum") for s in sc]
    for a in ["ne", "neden", "etki"]:
        if a not in order:
            warns.append(f"'{a}' bölümü yok — format: ne oldu → neden oldu → bizi nasıl etkiler")
    idx = [order.index(x) for x in ["ne", "neden", "etki"] if x in order]
    if idx != sorted(idx):
        errs.append("bölüm sırası bozuk: ne → neden → etki olmalı")
    if not b.get("kaynaklar"):
        errs.append("kaynaklar boş — kaynaksız sayı ekrana çıkmaz (SKILL.md §2)")
    return errs, warns


# ---------------------------------------------------------------- ses hazırlığı
def tighten(src, dst, keep=0.13, xf=0.012):
    """≥0.25 s gerçek sessizlikleri (−35 dB) 0.13 s'ye indirir. Kelime içi ünsüz
    kapanışları (<0.12 s) eşiğe girmez. explainer/altin-neden-dusuyor/tighten.py."""
    sr = 44100
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).copy()
    log = subprocess.run(["ffmpeg", "-nostdin", "-i", src, "-af", "silencedetect=noise=-35dB:d=0.25",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(v) for v in re.findall(r"silence_start: ([0-9.]+)", log)]
    en = [float(v) for v in re.findall(r"silence_end: ([0-9.]+)", log)]
    gaps = [(s, e) for s, e in zip(st, en) if s > 0.05]
    lead = next((e for s, e in zip(st, en) if s <= 0.05), 0)
    segs, cur = [], max(0, lead - 0.05)
    for s, e in gaps:
        segs.append((cur, s + keep / 2)); cur = e - keep / 2
    segs.append((cur, len(x) / sr))
    n = int(xf * sr); ramp = np.linspace(0, 1, n, dtype=np.float32)
    out = x[int(segs[0][0] * sr):int(segs[0][1] * sr)].copy()
    for a, b in segs[1:]:
        p = x[int(a * sr):int(b * sr)]
        out[-n:] = out[-n:] * (1 - ramp) + p[:n] * ramp
        out = np.concatenate([out, p[n:]])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-", dst],
                   input=out.tobytes(), check=True)
    print(f"  {len(gaps)} duraksama kısaltıldı · {len(x)/sr:.2f}s -> {len(out)/sr:.2f}s")
    return dst


# ---------------------------------------------------------------- zamanlama
def estimate(words):
    """Sessiz taslak için kelime zamanları: hece / hız + noktalama duraklaması."""
    t, out = 0.25, []
    for w in words:
        d = max(.2, AL.syllables_text(w) / SYL_RATE)
        out.append((w, t, t + d))
        t += d + PAUSE.get(w[-1], 0)
    return out


def sentalign(vo, text, emphasis, work):
    tp, op = f"{work}/metin.txt", f"{work}/caps.json"
    open(tp, "w", encoding="utf-8").write(text + "\n")
    cmd = [sys.executable, f"{VE}/sentalign.py", "--audio", vo, "--text", tp, "--out", op]
    if emphasis:
        cmd += ["--emphasis"] + emphasis
    r = subprocess.run(cmd, capture_output=True, text=True)
    for l in r.stdout.splitlines():
        if "ŞÜPHELİ" in l or "cümle ·" in l:
            print("  " + l.strip())
    if r.returncode:
        sys.exit(f"HATA: hizalama: {r.stderr[-400:]}")
    return [(c["w"], c["s"], c["e"], c["c"]) for c in json.load(open(op, encoding="utf-8"))]


def display_words(words, table):
    """Konuşma biçimi → ekran biçimi: 'seksen lira' → '80 ₺'. Sahne sınırını geçmez.
    Eşleşme noktalamasız yapılır; son kelimenin noktalaması korunur."""
    if not table:
        return words
    keys = sorted(((k.split(), v) for k, v in table.items()), key=lambda kv: -len(kv[0]))
    norm = lambda w: re.sub(r"[.,!?;:…]+$", "", w).casefold()
    out, i = [], 0
    while i < len(words):
        hit = None
        for ks, v in keys:
            seg = words[i:i + len(ks)]
            if len(seg) == len(ks) and len({w["p"] for w in seg}) == 1 and \
                    [norm(w["w"]) for w in seg] == [k.casefold() for k in ks]:
                hit = (len(ks), v); break
        if hit:
            n, v = hit
            seg = words[i:i + n]
            tail = re.search(r"[.,!?;:…]+$", seg[-1]["w"])
            out.append({"w": v + (tail.group(0) if tail else ""), "s": seg[0]["s"], "e": seg[-1]["e"],
                        "c": "yellow", "p": seg[0]["p"]})
            i += n
        else:
            out.append(words[i]); i += 1
    return out


def timeline(b, fmt, vo=None, work=None):
    sc = b["sahneler"]
    spoken_idx = [i for i, s in enumerate(sc) if (s.get("say") or "").strip()]
    text = " ".join(sc[i]["say"].strip() for i in spoken_idx)
    words = text.split()
    if vo:
        items = sentalign(vo, text, b.get("vurgu", []), work)
        if len(items) != len(words):
            sys.exit(f"HATA: hizalama {len(items)} kelime döndü, metin {len(words)} kelime")
        end = max(dur_of(vo), items[-1][2]) + .5
    else:
        items = AL.colorize(estimate(words), b.get("vurgu", []))
        end = items[-1][2] + .6
    # kelime → sahne numarası
    owner = [si for si in spoken_idx for _ in sc[si]["say"].split()]
    tl_words = [{"w": w, "s": round(s, 3), "e": round(e, 3), "c": c, "p": owner[k]}
                for k, (w, s, e, c) in enumerate(items)]
    starts, k = [], 0
    for si in spoken_idx:
        starts.append(0.0 if k == 0 else round(items[k][1] - .08, 3))
        k += len(sc[si]["say"].split())
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
                       "p": s.get("p", {}), "kaynak": s.get("kaynak"), "etiket": s.get("etiket")})
    # Abone ol / beğen çağrısı: {"sahne": N (1'den), "gecikme": sn, "sure": sn}
    cta = []
    for c in b.get("cta", []):
        s0 = scenes[int(c["sahne"]) - 1]["t0"] + float(c.get("gecikme", .4))
        d = float(c.get("sure", 5.0))
        cta.append({"t0": round(s0, 3), "t1": round(min(s0 + d, end), 3),
                    "abone": round(s0 + 1.3, 3), "begen": round(s0 + 2.4, 3)})
    return {"format": fmt, "gecis": b.get("gecis", True), "dur": round(end, 3), "scenes": scenes,
            "cta": cta, "words": display_words(tl_words, b.get("altyazi"))}, text


def tempo_report(tl):
    step_max, dur_max = TEMPO[tl["format"]]
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
        if x / steps > step_max:
            w.append(f"sahne {i+1} ({s['tip']}) {x:.1f}s, {steps} adım — ekran uzun süre aynı kalıyor, "
                     "cümleyi böl veya adım ekle")
        if x < 1.2 and s["tip"] != "soru":
            w.append(f"sahne {i+1} ({s['tip']}) {x:.1f}s — animasyon oturmadan geçiyor, cümleyi birleştir")
    if tl["dur"] > dur_max:
        w.append(f"süre {tl['dur']:.0f}s — {tl['format']} için uzun")
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
def silence(path, dur):
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
        w.writeframes(b"\x00\x00" * int(48000 * dur))
    return path


DUCK = "sidechaincompress=threshold=0.05:ratio=2.2:attack=30:release=350"
# Bölüm kartının ekranı tam kapattığı an = bölüm başı − 0.19 sn (engine.js CARD.hold / 2)
CARD_CLOSED = 0.19


def section_starts(tl):
    sc = tl["scenes"]
    return [s["t0"] for i, s in enumerate(sc)
            if s["bolum"] in ("ne", "neden", "etki") and (i == 0 or sc[i - 1]["bolum"] != s["bolum"])]


def ui_click(rng, amp=0.14):
    """Yumuşak arayüz tıkı — metalik 'klink' değil. 2 ms gürültü + kısa, boğuk ton."""
    from scipy.signal import butter, sosfilt
    SR = 44100
    n = int(SR * 0.06); t = np.arange(n) / SR
    noise = sosfilt(butter(2, [800, 5000], btype="band", fs=SR, output="sos"),
                    rng.standard_normal(n) * np.exp(-t / 0.002))
    tone = np.sin(2 * np.pi * 820 * t) * np.exp(-t / 0.012) * 0.5
    x = noise + tone
    return x / np.max(np.abs(x)) * amp


def audio(tl, vo, work, muzik=False, efekt=False, seviye=21.0):
    """Varsayılan: sadece seslendirme (kullanıcı kuralı). --muzik / --efekt isteğe bağlı.

    Müzik seviyesi ÖLÇÜLEREK ayarlanır: ducking sonrası müzik, seslendirmenin
    `seviye` LU altına oturur. Geçmiş: altın videosunda 18 LU "arkadan tatlı",
    22 LU'da duyulmuyordu; eşel mobilde ~16 LU "arka ses çok fazla" dendi → 21."""
    dur = tl["dur"]
    draft = vo is None
    vo = vo or silence(f"{work}/sessiz.wav", dur)
    ins = ["-i", vo]
    fc = [f"[0:a]aresample=48000,apad=whole_dur={dur:.3f},asplit=2[vo][sc]"]
    mixin = ["[vo]"]
    if muzik or efekt:
        import audiobed as ab
    if muzik:
        if muzik == "etkili":
            # gergin başlar (minör), 'bizi nasıl etkiler' bölümünde sıcağa döner
            etki = next((s["t0"] for s in tl["scenes"] if s["bolum"] == "etki"), dur * .7)
            ab.build_music(dur, f"{work}/music_raw.wav", bpm=104.0, peak_at=dur * .86, warm_at=etki)
        else:
            # altın videosu tarifi: 'warm' yatak, 92 BPM
            ab.build_music(dur, f"{work}/music_raw.wav", bpm=92.0, peak_at=dur * .5, warm_at=3.0)
        mu = f"{work}/music.wav"
        # tizleri yumuşat: konuşmanın netlik bandından (2–5 kHz) çekil
        run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", f"{work}/music_raw.wav",
             "-af", "lowpass=f=4500,highpass=f=70,equalizer=f=3000:t=q:w=1.2:g=-4", mu])
        vl = -16.0 if draft else lufs(vo)
        g = 10 ** ((vl - seviye - lufs(mu)) / 20)
        md = f"{work}/md.wav"
        for _ in range(3):            # kompresör doğrusal değil — ölç, düzelt
            run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", vo, "-i", mu, "-filter_complex",
                 f"[0:a]aresample=48000,apad=whole_dur={dur:.3f}[sc];[1:a]aresample=48000,volume={g:.5f}[m];"
                 f"[m][sc]{DUCK}[md]", "-map", "[md]", "-t", f"{dur:.3f}", md])
            got = lufs(md)
            g *= 10 ** (((vl - seviye) - got) / 20)
        ins += ["-i", mu]
        k = len(ins) // 2 - 1
        fc.append(f"[{k}:a]aresample=48000,volume={g:.5f}[m]")
        fc.append(f"[m][sc]{DUCK}[md]")
        mixin.append("[md]")
        print(f"  müzik ({muzik}): seslendirme {vl:.1f} LUFS, müzik (duck sonrası) {got:.1f} LUFS "
              f"-> {vl - got:.1f} LU altta (hedef {seviye:.0f})")
    else:
        fc.append("[sc]anullsink")
    if efekt:
        rng = np.random.default_rng(7)
        bus = ab.Bus(dur)
        # Sadece bölüm başlarında, yumuşak whoosh — tepesi kartın ekranı kapattığı ana.
        # Sahne→sahne çözülmelerinde ses yok (her kesimde whoosh+vuruş "fazla" bulundu).
        secs = section_starts(tl) if tl.get("gecis", True) else []
        WD = 0.55
        for t in secs:
            bus.place(ab.whoosh(rng, dur=WD, amp=0.16), t - CARD_CLOSED - 0.88 * WD)
        clicks = [c[k] for c in tl.get("cta", []) for k in ("abone", "begen")]
        for t in clicks:
            bus.place(ui_click(rng), t)
        bus.write(f"{work}/sfx.wav", 80, peak=0.8)
        ins += ["-i", f"{work}/sfx.wav"]
        k = len(ins) // 2 - 1
        fc.append(f"[{k}:a]aresample=48000,highpass=f=90,lowpass=f=9000,volume=0.40[fx]")
        mixin.append("[fx]")
        print(f"  efekt: {len(secs)} bölüm geçişi · {len(clicks)} tık")
    fc.append(f"{''.join(mixin)}amix=inputs={len(mixin)}:normalize=0:duration=first[a]")
    raw, mix = f"{work}/mix_raw.wav", f"{work}/mix.wav"
    run(["ffmpeg", "-nostdin", "-y", "-v", "error"] + ins + ["-filter_complex", ";".join(fc), "-map", "[a]",
         "-ac", "2", "-t", f"{dur:.3f}", "-c:a", "pcm_f32le", raw])
    if draft and not muzik and not efekt:
        return raw                     # taslak: master'lanacak ses yok
    # tavan −4.5: AAC ~3.5 dB taşıyor (master.py)
    run([sys.executable, f"{VE}/master.py", raw, mix, "-14.0", "-4.5"])
    return mix


def mux(video, mix, out, dur, work):
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", mix, "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-t", f"{dur:.3f}",
         "-movflags", "+faststart", out])
    size = os.path.getsize(out)
    if size <= MAX_BYTES:
        return
    # 30 MiB sınırı: iki geçişli sabit bit hızıyla yeniden kodla
    vbr = int((MAX_BYTES * 8 / dur - 128_000) * 0.96)
    print(f"  {size/2**20:.1f} MiB > 30 MiB — video {vbr//1000}k ile yeniden kodlanıyor")
    hq = f"{work}/hq.mp4"
    shutil.move(out, hq)
    log = f"{work}/pass"
    run(["ffmpeg", "-v", "error", "-y", "-i", hq, "-c:v", "libx264", "-preset", "slow", "-b:v", str(vbr),
         "-pass", "1", "-passlogfile", log, "-an", "-f", "null", "/dev/null"])
    run(["ffmpeg", "-v", "error", "-y", "-i", hq, "-c:v", "libx264", "-preset", "slow", "-b:v", str(vbr),
         "-pass", "2", "-passlogfile", log, "-pix_fmt", "yuv420p", "-map", "0:v", "-map", "0:a",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out])
    print(f"  -> {os.path.getsize(out)/2**20:.1f} MiB")


# ---------------------------------------------------------------- kontrol
def qc(out, tl, sheet, has_audio):
    d = dur_of(out)
    ok = True
    print(f"  süre {d:.2f}s (çizelge {tl['dur']:.2f}s) · {os.path.getsize(out)/2**20:.1f} MiB")
    if has_audio:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        I = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)
        P = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)
        if I:
            print(f"  ses {float(I[-1]):.1f} LUFS · tepe {float(P[-1]) if P else 0:+.2f} dBFS")
            if P and float(P[-1]) > 0.0:
                print("  UYARI: tepe 0 dBFS üstünde — kırpılma"); ok = False
    if abs(d - tl["dur"]) > .2:
        print("  UYARI: video süresi çizelgeyle uyuşmuyor"); ok = False
    if os.path.getsize(out) > 30 * 2**20:
        print("  UYARI: 30 MiB üstü — teslim yolu reddeder"); ok = False
    tmp = tempfile.mkdtemp()
    yatay = tl["format"] == "yatay"
    for i, s in enumerate(tl["scenes"]):
        t = s["t0"] + (s["t1"] - s["t0"]) * .85
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", out, "-frames:v", "1",
             "-vf", "scale=480:270" if yatay else "scale=270:480", f"{tmp}/k{i:03d}.jpg"])
    cols = min(4 if yatay else 6, len(tl["scenes"]))
    rows = -(-len(tl["scenes"]) // cols)
    run(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", f"{tmp}/k%03d.jpg",
         "-vf", f"tile={cols}x{rows}:padding=6:color=black", "-frames:v", "1", sheet])
    shutil.rmtree(tmp)
    return ok


def make_cover(b, fmt, odir, work):
    """kapak.png (+ yatayda 1280x720 kapak_youtube.jpg)."""
    if not b.get("kapak"):
        return
    ctl = f"{work}/kapak.json"
    json.dump({"format": fmt, "dur": 1, "scenes": [{"t0": 0, "t1": 1, "tip": "kapak", "bolum": "hook",
                                                    "p": b["kapak"]}], "words": []},
              open(ctl, "w"), ensure_ascii=False)
    kp = os.path.join(odir, "kapak.png")
    capture_still(ctl, .5, kp, cover=True)
    if fmt == "yatay":   # YouTube küçük resmi: 1280x720, < 2 MB
        run(["ffmpeg", "-v", "error", "-y", "-i", kp, "-vf", "scale=1280:720", "-q:v", "2",
             os.path.join(odir, "kapak_youtube.jpg")])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bolum", required=True)
    ap.add_argument("--vo", help="seslendirme (mp3/wav). Yoksa sessiz taslak üretilir.")
    ap.add_argument("--out", help="video.mp4 (varsayılan: bolum klasöründe cikti/)")
    ap.add_argument("--format", choices=["yatay", "dikey"], help="bolum.json'daki formatı ezer")
    ap.add_argument("--kareler", action="store_true", help="sadece her sahneden bir kare (hızlı önizleme)")
    ap.add_argument("--sikistir", action="store_true", help="seslendirmedeki ≥0.25 s duraksamaları 0.13 s'ye indir")
    ap.add_argument("--muzik", nargs="?", const="yumusak", choices=["yumusak", "etkili"],
                    help="SADECE kullanıcı isterse. yumusak: altın videosu (92 BPM, ~18 LU altta) · "
                         "etkili: 104 BPM, gergin→sıcak")
    ap.add_argument("--muzik-seviye", type=float, default=21.0,
                    help="müziğin seslendirmenin kaç LU altında duracağı (ölçülür). Büyük = daha kısık")
    ap.add_argument("--efekt", action="store_true", help="SADECE kullanıcı isterse: geçişlerde whoosh")
    ap.add_argument("--jobs", type=int, default=max(1, min(4, os.cpu_count() or 1)))
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    b = json.load(open(a.bolum, encoding="utf-8"))
    fmt = a.format or b.get("format", "yatay")
    base = os.path.dirname(os.path.abspath(a.bolum))
    out = a.out or os.path.join(base, "cikti", "video.mp4" if a.vo else "taslak.mp4")
    odir = os.path.dirname(os.path.abspath(out))
    os.makedirs(odir, exist_ok=True)
    work = tempfile.mkdtemp(prefix="tb_")

    print(f"1/7 bölüm dosyası kontrol · format {fmt}")
    errs, warns = check_bolum(b)
    for w in warns: print("  UYARI:", w)
    for e in errs: print("  HATA:", e)
    if errs and not a.force:
        sys.exit("Durdu. Hataları düzelt.")

    vo = a.vo
    if vo and a.sikistir:
        print("   duraksama kısaltma")
        vo = tighten(vo, f"{work}/vo_tight.wav")

    print("2/7 zamanlama " + ("(sese hizalı, sentalign)" if vo else "(TAHMİNİ — ses yok, taslak)"))
    tl, text = timeline(b, fmt, vo, work)
    open(os.path.join(odir, "metin.txt"), "w", encoding="utf-8").write(
        "\n\n".join(s["say"].strip() for s in b["sahneler"] if (s.get("say") or "").strip()) + "\n")
    tl_path = os.path.join(odir, "cizelge.json")
    json.dump(tl, open(tl_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for w in tempo_report(tl): print("  UYARI:", w)

    if a.kareler:
        print("3/3 sahne kareleri")
        kd = os.path.join(odir, "kareler")
        shutil.rmtree(kd, ignore_errors=True); os.makedirs(kd)
        with ThreadPoolExecutor(a.jobs) as ex:
            list(ex.map(lambda x: capture_still(tl_path, x[1]["t0"] + (x[1]["t1"] - x[1]["t0"]) * .85,
                                                f"{kd}/{x[0]+1:02d}-{x[1]['tip']}.jpg"),
                        enumerate(tl["scenes"])))
        make_cover(b, fmt, odir, work)
        print(f"-> {kd} (+ kapak)")
        return

    print(f"3/7 kareler ({int(tl['dur']*FPS)} kare, {a.jobs} iş parçacığı)")
    silent = f"{work}/goruntu.mp4"
    render_video(tl_path, tl["dur"], silent, work, a.jobs)

    print("4/7 ses" + (" + müzik" if a.muzik else "") + (" + efekt" if a.efekt else "") +
          ("" if vo or a.muzik or a.efekt else " (yok — taslak sessiz)"))
    mix = audio(tl, vo, work, a.muzik, a.efekt, a.muzik_seviye)

    print("5/7 birleştirme")
    mux(silent, mix, out, tl["dur"], work)

    print("6/7 kapak")
    make_cover(b, fmt, odir, work)

    print("7/7 kalite kontrol")
    ok = qc(out, tl, os.path.join(odir, "kontrol.jpg"), bool(vo or a.muzik or a.efekt))
    shutil.rmtree(work, ignore_errors=True)
    print(("TAMAM" if ok else "SORUNLU") + f" -> {out}")
    if not vo:
        print("NOT: bu bir TASLAK. Zamanlama tahmini; seslendirme gelince --vo ile yeniden çalıştır.")


if __name__ == "__main__":
    main()
