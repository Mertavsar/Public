#!/usr/bin/env python3
"""Ses gelince: python3 bitir.py vo.mp3  → final.mp4
Kareler (fr/, altyazısız, tahmini zamanlama) sesin cümle sürelerine esnetilir,
altyazı ASS katmanı olarak eklenir, ses + müzik + tık miksi yapılır.
Ses yoksa: python3 bitir.py --sessiz → taslak.mp4 (sadece müzik, altyazısız)."""
import json, os, subprocess, sys, re
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
FPS = 30
old = json.load(open("timeline.json"))
OS = old["S"]; OEND = old["END"]; NFR = len(os.listdir("fr"))
SESSIZ = "--sessiz" in sys.argv
CIKAR = next((a.split("=",1)[1].split(",") for a in sys.argv if a.startswith("--cikar=")), [])
run = lambda c: subprocess.run(c, shell=True, check=True)

def cta_clicks(S, END):                       # film.html ctaAnim ile aynı hesap
    i = [k for k, s in enumerate(S) if s["id"].split("#")[0] == "cta"][0]
    st = S[i]["s"] - .09; nxt = S[i + 1]["s"] - .09; d = min(nxt - st, 3.1); k = (d - .25) / 3.4
    return [st + c * k for c in (1.0, 2.0, 2.8)]

if SESSIZ:
    NS, NEND, caps = OS, OEND, None
else:
    vo = sys.argv[1]
    KEEP = [s for s in OS if s["id"] not in CIKAR]
    txt = " ".join(s["text"] for s in KEEP); open("metin.txt", "w").write(txt)
    run(f"/tmp/claude-0/-home-user-Public/c9db20bb-f3d2-52b3-98e5-e5b3107fcb6a/scratchpad/ppv/bin/python /home/user/Public/.claude/skills/viral-edit/scripts/sentalign.py --audio '{vo}' --text metin.txt --out caps.json")
    caps = json.load(open("caps.json")); sents = json.load(open("caps.sentences.json"))
    assert len(sents) == len(KEEP), f"cümle sayısı tutmuyor: {len(sents)} / {len(KEEP)} — metin birebir okunmamış"
    kn = {o["id"]: n for o, n in zip(KEEP, sents)}; NS = []
    for j, o in enumerate(OS):
        if o["id"] in kn: NS.append(dict(id=o["id"], s=kn[o["id"]]["s"], e=kn[o["id"]]["e"]))
        else: nx = next(kn[x["id"]] for x in OS[j:] if x["id"] in kn); NS.append(dict(id=o["id"], s=nx["s"], e=nx["s"], cut=True))
    NEND = round(sents[-1]["e"] + .7, 2)

# yeni → eski zaman eşlemesi (parçalı doğrusal)
ob = [0.0] + [s["s"] - .09 for s in OS[1:]] + [OEND]
nb = [0.0] + [s["s"] - .09 for s in NS[1:]] + [NEND]
def n2o(t):
    for i in range(len(nb) - 1):
        if t < nb[i + 1] or i == len(nb) - 2:
            r = (t - nb[i]) / max(1e-6, nb[i + 1] - nb[i]); return ob[i] + r * (ob[i + 1] - ob[i])
def o2n(t):
    for i in range(len(ob) - 1):
        if t < ob[i + 1] or i == len(ob) - 2:
            r = (t - ob[i]) / max(1e-6, ob[i + 1] - ob[i]); return nb[i] + r * (nb[i + 1] - nb[i])

out = "fr2"; os.makedirs(out, exist_ok=True)
for f in os.listdir(out): os.remove(os.path.join(out, f))
nout = int(NEND * FPS)
for k in range(nout):
    src = min(NFR - 1, max(0, round(n2o(k / FPS) * FPS)))
    os.symlink(os.path.join(W, "fr", f"f_{src:05d}.jpg"), os.path.join(out, f"g_{k:05d}.jpg"))

# altyazı (ASS): 2–3 kelimelik parçalar, konuşulan kelime sarı
def ts(t): t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60; return f"{h}:{m:02d}:{s:05.2f}"
ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "",
       "[V4+ Styles]", "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: C,Poppins SemiBold,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,4.5,3,8,60,60,1215,1", "",
       "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
if caps:
    k = 0
    for s in NS:
        if s.get("cut"): continue
        n = len([o for o in OS if o["id"] == s["id"]][0]["text"].split()); W_ = caps[k:k + n]; k += n
        chunks, cur = [], []
        for w in W_:
            cur.append(w)
            if len(cur) >= 3 or re.search(r"[,.!?;:]$", w["w"]): chunks.append(cur); cur = []
        if cur: chunks.append(cur)
        for ch in chunks:
            for j, w in enumerate(ch):
                st = w["s"] - (.05 if j == 0 else 0); en = ch[j + 1]["s"] if j + 1 < len(ch) else ch[-1]["e"] + .12
                txt = " ".join((r"{\c&H004AD5FF&}" + x["w"] + r"{\c&H00FFFFFF&}") if x is w else x["w"] for x in ch)
                ass.append(f"Dialogue: 0,{ts(st)},{ts(en)},C,,0,0,0,,{txt}")
open("altyazi.ass", "w").write("\n".join(ass) + "\n")

# ses
clicks = [o2n(t) for t in cta_clicks(OS, OEND)]
D = NEND
cl = "".join(f"[{2 + i}]adelay={int(c * 1000)}|{int(c * 1000)},volume=0.5[c{i}];" for i, c in enumerate(clicks))
if SESSIZ:
    run(f"ffmpeg -loglevel error -y -i muzik.mp3 -i click.wav -i click.wav -i click.wav -filter_complex \""
        f"[0]atrim=0:{D},aformat=channel_layouts=stereo,loudnorm=I=-20:TP=-3,afade=in:d=1,afade=out:st={D-1.5}:d=1.5[m];"
        + cl.replace("[2", "[1").replace("[3", "[2").replace("[4", "[3") +
        f"[m][c0][c1][c2]amix=inputs=4:normalize=0:duration=first\" -ar 48000 mix.wav")
else:
    run(f"ffmpeg -loglevel error -y -i '{vo}' -i muzik.mp3 -i click.wav -i click.wav -i click.wav -filter_complex \""
        f"[0]aresample=48000,aformat=channel_layouts=stereo,highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,loudnorm=I=-15:TP=-2:LRA=9[v];"
        f"[1]atrim=0:{D},aformat=channel_layouts=stereo,loudnorm=I=-36:TP=-9,afade=in:d=1.2,afade=out:st={D-1.5}:d=1.5[m];{cl}"
        f"[v][m][c0][c1][c2]amix=inputs=5:normalize=0:duration=first,apad=whole_dur={D},loudnorm=I=-14:TP=-1.5:LRA=11\" -ar 48000 mix.wav")
vf = "" if SESSIZ else "-vf \"ass=altyazi.ass:fontsdir=fonts\""
name = "taslak.mp4" if SESSIZ else "final.mp4"
run(f"ffmpeg -loglevel error -y -framerate {FPS} -i fr2/g_%05d.jpg -i mix.wav {vf} -c:v libx264 -preset slow -crf 23 -maxrate 3500k -bufsize 7000k "
    f"-pix_fmt yuv420p -c:a aac -b:a 160k -shortest -movflags +faststart {name}")
print(name, D)
