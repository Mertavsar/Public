#!/usr/bin/env python3
"""
Ham klip + seslendirme -> teslim edilebilir dikey video. Tek komut.

Elle yapıldığında yirmi adım sürüyordu ve her seferinde bir adım atlanıyordu
(ses yatağı eski kesimlere göre kalıyor, kırpılma kontrolü unutuluyor,
altyazı eski sesle hizalı kalıyor). Burada sıra sabit ve kontroller zorunlu.

    python3 build.py --src raw.mp4 --edl edl.tsv --vo vo.mp3 --script script.txt \
        --spec spec.json --out gergedan.mp4 --emphasis kör kıpırdamadığı hayatta

EDL biçimi (sekmeyle ayrılmış, `#` yorum):

    out0  out1  src   slow  z0    z1    cx    cy    cropx  beat  not
    0.00  1.78  5.55  1.60  1.45  1.58  0.32  0.76  40     R     HOOK

out0/out1  planın videodaki yeri (s). Cümle sınırlarına oturur.
src        kaynaktaki başlangıç (s)
slow       ağır çekim çarpanı (1.00 = normal). Kaynaktan çekilen süre
           (out1-out0)/slow kadardır.
z0/z1      zoom başı/sonu. 1.00 = tam kare.
cx/cy      kadrajın yatay/dikey konumu, 0–1 (0.5 = orta).
cropx      kaynaktan kırpmanın sol kenarı. Filigran dönemine göre plan başına
           değişir — SKILL.md "Watermark".
beat       M ana vuruş · m klink · R vuruş+riser · - ses yok
"""

import argparse, json, os, shlex, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FLASH_AMP = {"R": 0.30, "M": 0.24}
BOOM_AMP = {"R": 0.62, "M": 0.50}


def run(cmd, **kw):
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    p = subprocess.run(cmd, **kw)
    if p.returncode:
        raise SystemExit(f"BAŞARISIZ: {' '.join(cmd[:6])} …")
    return p


def read_edl(path):
    rows = []
    for ln in open(path, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        f = ln.split("\t")
        if len(f) < 10:
            raise SystemExit(f"EDL satırı eksik ({len(f)} sütun, 10 gerekli): {ln[:60]}")
        rows.append(dict(o0=float(f[0]), o1=float(f[1]), src=float(f[2]), slow=float(f[3]),
                         z0=float(f[4]), z1=float(f[5]), cx=float(f[6]), cy=float(f[7]),
                         cropx=int(f[8]), beat=f[9].strip(), note=f[10] if len(f) > 10 else ""))
    return rows


def check_edl(edl, src_dur, crop_w, usable_end):
    """Teslimden sonra fark edilen hatalar burada yakalanır."""
    bad = []
    for i, r in enumerate(edl):
        d = r["o1"] - r["o0"]
        if d > 3.0:
            bad.append(f"plan {i}: {d:.2f}s — 3 saniye kuralı (SKILL.md 0b)")
        if d <= 0:
            bad.append(f"plan {i}: süre sıfır veya negatif")
        e = r["src"] + d / r["slow"]
        if e > usable_end:
            bad.append(f"plan {i}: kaynak {e:.2f}s — kullanılabilir son {usable_end:.2f}s")
        if i and abs(r["o0"] - edl[i - 1]["o1"]) > 1e-6:
            bad.append(f"plan {i}: önceki planla boşluk/çakışma")
    n, tot = len(edl), edl[-1]["o1"] - edl[0]["o0"]
    print(f"EDL: {n} plan · {tot:.2f}s · ortalama {tot/n:.2f}s · {n/tot:.2f} kesim/s")
    if tot / n > 2.0:
        bad.append(f"ortalama plan {tot/n:.2f}s — 1.2–1.6s olmalı, tempo düşük")
    for b in bad:
        print("  UYARI:", b)
    return bad


def cut(src, edl, crop, work, fps=30, cropy=0):
    cw, ch = crop
    os.makedirs(f"{work}/clips", exist_ok=True)
    lst = f"{work}/concat.txt"
    with open(lst, "w") as fh:
        for i, r in enumerate(edl):
            d = r["o1"] - r["o0"]
            nf = max(1, round(d * fps))
            out = f"{work}/clips/c{i:02d}.mp4"
            slo = ""
            if abs(r["slow"] - 1.0) > 1e-3:
                slo = (f"setpts={r['slow']}*PTS,minterpolate=fps={fps}:mi_mode=mci:"
                       f"mc_mode=aobmc:me_mode=bidir:vsbmc=1,")
            vf = (f"crop={cw}:{ch}:{r['cropx']}:{cropy},{slo}fps={fps},"
                  f"scale=1080:1920:flags=lanczos,setsar=1,"
                  f"zoompan=z='{r['z0']}+({r['z1']}-{r['z0']})*on/{nf}':"
                  f"x='(iw-iw/zoom)*{r['cx']}':y='(ih-ih/zoom)*{r['cy']}':"
                  f"d=1:s=1080x1920:fps={fps},trim=end_frame={nf},setpts=PTS-STARTPTS")
            run(["ffmpeg", "-nostdin", "-v", "error", "-y",
                 "-ss", str(r["src"]), "-t", f"{d/r['slow']+0.25:.4f}", "-i", src,
                 "-vf", vf, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                 "-pix_fmt", "yuv420p", "-r", str(fps), out])
            fh.write(f"file '{out}'\n")
    content = f"{work}/content.mp4"
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", lst, "-c", "copy", content])
    return content


def audio(edl, dur, vo, work, warm_at=None):
    major = [f"{r['o0']:.2f}:{BOOM_AMP[r['beat']]}" for r in edl if r["beat"] in BOOM_AMP]
    minor = [f"{r['o0']:.2f}" for r in edl if r["beat"] == "m"]
    risers = [f"{r['o0']:.2f}" for r in edl if r["beat"] == "R"]
    sfx, mus = f"{work}/sfx.wav", f"{work}/music.wav"
    cmd = [sys.executable, f"{HERE}/audiobed.py", "--dur", f"{dur:.2f}",
           "--out-sfx", sfx, "--out-music", mus, "--peak-at", f"{dur*0.86:.2f}"]
    if major: cmd += ["--major"] + major
    if minor: cmd += ["--minor"] + minor
    if risers:
        cmd += ["--riser"] + risers
        cmd += ["--duck"] + [f"{t}:0.78" for t in risers[:1]]
    if warm_at is not None:
        cmd += ["--warm-at", f"{warm_at:.2f}"]
    run(cmd)

    raw, mix = f"{work}/mix_raw.wav", f"{work}/mix.wav"
    fc = (f"[0:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
          f"highpass=f=80,apad=whole_dur={dur:.2f}[vo];[vo]asplit=3[vo_out][sc1][sc2];"
          f"[1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
          f"highpass=f=45,volume=0.85[sfx];"
          f"[2:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
          f"highpass=f=52,volume=0.52[mus];"
          f"[sfx][sc1]sidechaincompress=threshold=0.05:ratio=4:attack=8:release=260[sfxd];"
          f"[mus][sc2]sidechaincompress=threshold=0.035:ratio=8:attack=6:release=300[musd];"
          f"[vo_out][sfxd][musd]amix=inputs=3:duration=longest:normalize=0[mix]")
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", vo, "-i", sfx, "-i", mus,
         "-filter_complex", fc, "-map", "[mix]", "-c:a", "pcm_f32le",
         "-ar", "48000", "-ac", "2", raw])
    # volume+alimiter KULLANMA — SKILL.md §6. Tavan -3.5: AAC ~3.5 dB taşıyor.
    run([sys.executable, f"{HERE}/master.py", raw, mix, "-14.0", "-3.5"])
    return mix


def fx_expr(edl):
    """Ana vuruşlarda ışık parlaması + hafif sarsıntı. Zamanlar sesle aynı."""
    beats = [(r["o0"], FLASH_AMP[r["beat"]]) for r in edl if r["beat"] in FLASH_AMP]
    if not beats:
        return "0", "14", "24"
    FL, SH = 0.13, 0.28
    flash = "+".join(f"if(between(t,{t},{t+FL}),{a:.2f}*(1-(t-{t})/{FL}),0)" for t, a in beats)
    def sh(amp, freq, fn):
        return "+".join(f"if(between(t,{t},{t+SH}),{amp*a/0.30:.2f}*exp(-(t-{t})/0.080)"
                        f"*{fn}(2*PI*{freq}*(t-{t})),0)" for t, a in beats)
    return flash, "14+" + sh(10.0, 43, "sin"), "24+" + sh(8.0, 35, "cos")



def shot_words(edl, caps_path):
    """Her planın üstünde O AN NE SÖYLENDİĞİNİ bas.

    Bu oturumda iki kez aynı hata yapıldı: "Gergedan ot yiyor" cümlesinin
    altında domuz yürüyordu; fil videosunda "akıntıda kapana kısılan bu adam"
    denirken ekranda fil vardı. İkisi de ancak kontakt sayfasına gözle
    bakarken fark edildi — yani atlanabilirdi.

    Tablo planın notunu ve o an konuşulan kelimeleri yan yana koyuyor.
    İkisi birbirini tutmuyorsa EDL yanlıştır.
    """
    if not caps_path or not os.path.exists(caps_path):
        return
    caps = json.load(open(caps_path, encoding="utf-8"))
    print("\nPLAN ↔ SÖZ  (notu ve sözü karşılaştır; tutmuyorsa EDL yanlış)")
    for i, r in enumerate(edl):
        said = " ".join(c["w"] for c in caps if c["s"] < r["o1"] and c["e"] > r["o0"])
        print(f"{i:3d} {r['o0']:6.2f}-{r['o1']:6.2f}  {r['note'][:28]:28s} | {said[:58]}")


def check_cuts_on_pauses(edl, vo, min_ratio=0.40):
    """Kesimler konuşmanın duraklamalarına oturuyor mu?

    İlk sürüm kesimi KELİME sınırıyla karşılaştırıyordu ve 15 kesimin 7'sine
    yanlış uyarı verdi. Yanlıştı: referans stilde altyazı kesimin üstünden
    devam ediyor (style-profile.md), kelime ortasında kesmek kusur değil.

    Asıl kural SKILL.md §3'te: kesimleri DURAKLAMALARIN içine yerleştir, her
    cümle yeni görüntüyle açılsın. Ölçülen şey o: kaç kesim sessizliğe denk
    geliyor."""
    sys.path.insert(0, HERE)
    import align as A
    x = A.load_audio(vo)
    blocks, _ = A.speech_blocks(A.envelope(x))
    gaps = [(blocks[i][1], blocks[i + 1][0]) for i in range(len(blocks) - 1)]
    cuts = [r["o0"] for r in edl[1:]]
    if not cuts:
        return []
    on_pause = sum(any(g0 - 0.10 <= t <= g1 + 0.10 for g0, g1 in gaps) for t in cuts)
    ratio = on_pause / len(cuts)
    print(f"\nKESİM–DURAKLAMA: {on_pause}/{len(cuts)} kesim sessizliğe oturuyor (%{ratio*100:.0f})")
    if ratio < min_ratio:
        return [f"kesimlerin sadece %{ratio*100:.0f}'i duraklamaya oturuyor "
                f"(hedef %{min_ratio*100:.0f}+). Plan sınırlarını cümle aralarına taşı; "
                f"araları `silencedetect` ile çıkar."]
    return []


def qc_sheet(out, edl, caps_path, path):
    """Teslim öncesi zorunlu görsel kontrol: her planın orta karesi + o anki altyazı.

    Elle üretiliyordu ve bu yüzden bazen atlanıyordu. Artık boru hattının
    parçası — dosya her zaman yazılıyor, BAKMAK zorunlu."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("  (PIL yok, kontrol sayfası atlandı)")
        return
    caps = json.load(open(caps_path, encoding="utf-8")) if (
        caps_path and os.path.exists(caps_path)) else []
    tmp = os.path.join(os.path.dirname(path) or ".", "_qc")
    os.makedirs(tmp, exist_ok=True)
    ims = []
    for i, r in enumerate(edl):
        t = (r["o0"] + r["o1"]) / 2
        f = f"{tmp}/s{i:02d}.png"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{t:.2f}",
                        "-i", out, "-frames:v", "1", "-vf", "scale=170:302", f], check=True)
        w = next((c["w"] for c in caps if c["s"] <= t < c["e"]), "")
        im = Image.open(f).convert("RGB")
        d = ImageDraw.Draw(im)
        d.text((4, 3), f"{i} {t:.1f}s", fill=(255, 60, 60))
        d.text((4, 286), w, fill=(0, 255, 255))
        ims.append(im)
    cols = min(9, len(ims))
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 170, rows * 302))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * 170, (i // cols) * 302))
    sheet.save(path)
    print(f"  kontrol sayfası -> {path}   ** BAK: her planın altyazısı görüntüyle uyuyor mu? **")


def qc(out, dur):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", out, "-ac", "2", "-ar", "48000",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).T
    pk = 20 * np.log10(np.abs(x).max())
    over = int((np.abs(x) >= 1.0).sum())
    m = np.maximum(np.abs(x[0]), np.abs(x[1])) > 0.985
    runs, i = 0, 0
    while i < len(m):
        if m[i]:
            j = i
            while j < len(m) and m[j]:
                j += 1
            runs += (j - i >= 3)
            i = j
        else:
            i += 1
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", out, "-af", "ebur128",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    lufs = next((l.split()[1] for l in err.splitlines()[::-1] if "I:" in l and "LUFS" in l), "?")
    print(f"\nKALİTE KONTROL")
    print(f"  tepe {pk:+.2f} dBFS · 1.0 aşan {over} · kırpık plato {runs} · {lufs} LUFS")
    ok = over == 0 and runs == 0 and pk < -1.0
    print("  ses:", "TEMİZ" if ok else "⛔ KIRPILMA VAR — teslim etme")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True); ap.add_argument("--edl", required=True)
    ap.add_argument("--vo", required=True)
    ap.add_argument("--script", default=None,
                    help="seslendirme metni. YOKSA altyazı üretilmez — "
                         "metin gelince aynı komutu --script ile tekrar çalıştır")
    ap.add_argument("--spec", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--work", default=None)
    ap.add_argument("--crop", default="416:740", help="kaynaktan kırpma GxY (9:16 olmalı)")
    ap.add_argument("--crop-y", type=int, default=0,
                    help="kırpmanın üst kenarı (kaynak piksel)")
    ap.add_argument("--warm-at", type=float, default=None,
                    help="bu andan sonra müzik gerginden sıcağa döner (s)")
    ap.add_argument("--usable-end", type=float, default=1e9,
                    help="kaynakta kullanılabilir son an (end card öncesi)")
    ap.add_argument("--emphasis", nargs="*", default=[])
    ap.add_argument("--banner-words", type=int, default=0,
                    help="banner'ın kapsadığı kelime sayısı — altyazıdan düşülür")
    ap.add_argument("--force", action="store_true", help="uyarılara rağmen devam et")
    a = ap.parse_args()

    work = a.work or os.path.dirname(os.path.abspath(a.out)) + "/_build"
    os.makedirs(work, exist_ok=True)
    cw, ch = (int(v) for v in a.crop.split(":"))
    if abs(cw / ch - 1080 / 1920) > 0.005:
        raise SystemExit(f"crop {a.crop} 9:16 değil — görüntü dikey esner.")

    info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                           "-show_entries", "stream=width,height:format=duration",
                           "-of", "csv=p=0", a.src],
                          capture_output=True, text=True).stdout.split()
    sw, sh = (int(v) for v in info[0].split(",")[:2])
    src_dur = float(info[-1])
    if a.crop_y + ch > sh:
        raise SystemExit(f"crop {cw}x{ch} +{a.crop_y} kaynağı ({sw}x{sh}) aşıyor. "
                         f"--crop-y küçült veya --crop daralt.")
    edl = read_edl(a.edl)
    bad = check_edl(edl, src_dur, cw, min(a.usable_end, src_dur))
    if bad and not a.force:
        raise SystemExit("EDL uyarıları var. Düzelt veya --force ver.")
    dur = edl[-1]["o1"]

    caps = None
    if a.script:
        print("\n1/5 hizalama")
        caps = f"{work}/captions.json"
        run([sys.executable, f"{HERE}/align.py", "--audio", a.vo, "--text", a.script,
             "--out", caps, "--check"] + (["--emphasis"] + a.emphasis if a.emphasis else []))
        if a.banner_words:
            c = json.load(open(caps, encoding="utf-8"))
            json.dump(c[a.banner_words:], open(caps, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            print(f"banner {a.banner_words} kelimeyi kapsıyor, altyazıdan düşüldü")
    else:
        print("\n1/5 hizalama ATLANDI — metin verilmedi, ALTYAZI YOK")

    print("\n2/5 planlar")
    content = cut(a.src, edl, (cw, ch), work, cropy=a.crop_y)

    print("\n3/5 ses")
    mix = audio(edl, dur, a.vo, work, a.warm_at)

    print("\n4/5 grafik")
    spec = json.load(open(a.spec, encoding="utf-8"))
    spec.update(canvas=[1080, 1920], fps=30, duration=round(dur, 2),
                card={"x": 0, "y": 0, "w": 1080, "h": 1920}, captions=caps or "")
    sp = f"{work}/spec.resolved.json"
    json.dump(spec, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ov = f"{work}/overlay.mov"
    run([sys.executable, f"{HERE}/overlay.py", "--spec", sp, "--out", ov])

    print("\n5/5 birleştirme")
    flash, sx, sy = fx_expr(edl)
    fc = (f"[0:v]scale=1108:1968:flags=bicubic,crop=1080:1920:x='{sx}':y='{sy}',"
          f"eq=brightness='{flash}':eval=frame,eq=contrast=1.04:saturation=1.06,"
          f"setsar=1[bg];[bg][1:v]overlay=0:0:format=auto[v]")
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", content, "-i", ov, "-i", mix,
         "-filter_complex", fc, "-map", "[v]", "-map", "2:a", "-t", f"{dur:.2f}",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-profile:v", "high", "-level", "4.0", "-r", "30",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
         "-movflags", "+faststart", a.out])

    ok = qc(a.out, dur)
    shot_words(edl, caps)
    for b in check_cuts_on_pauses(edl, a.vo):
        print("  UYARI:", b)
    qc_sheet(a.out, edl, caps, os.path.splitext(a.out)[0] + "_kontrol.png")
    if not ok:
        raise SystemExit("Kırpılma var — teslim etme.")
    print(f"\n-> {a.out}")


if __name__ == "__main__":
    main()
