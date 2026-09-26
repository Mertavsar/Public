#!/usr/bin/env python3
"""
Cümle sınırlarını sesin duraklamalarına oturtur, sonra kelimeleri HER CÜMLENİN
KENDİ SES PARÇASI İÇİNDE hizalar. `align.py` tek başına kaydığında kullanılır.

Neden: align.py tüm metni bir kerede konuşma bloklarına dağıtıyor. Uzun ve
hızlı seslendirmede bir blokta cümle sınırını bir kelime kaydırıyor ve kayma
sonraki bloklara taşınıyor. Steiner videosunda sonda "Sözünü tutmuştu… Keşke"
0.9 saniyeye sıkıştı (8.9 hece/sn, imkânsız). Ayı videosunda da orta bölüm
bir cümle kaydı.

Yöntem:
1. Metni cümlelere böl (. ! ? …), her cümlenin hecesini say (sesli harf).
2. Dinamik programlama: her cümle ardışık konuşma bloklarını kapsar, cümle
   sonları blok aralarına (duraklamalara) düşer. Maliyet: cümlenin hece
   hızının ortalamadan log-sapmasının karesi. Ölçüldü: Steiner'de 27 cümlenin
   hepsi 4.4–8.2 hece/sn, ayıda 21 cümlenin hepsi 5.3–7.8.
3. Her cümlenin ses parçasını kes, align.py'yi yalnız o cümleyle çalıştır,
   zamanları geri kaydır. Hata cümle sınırını geçemez.

    python3 sentalign.py --audio vo.mp3 --text metin.txt --out captions.json \
        --emphasis kaybetmişti söz kaldırdı

Çıktı align.py ile aynı biçimde (w, s, e, c). Yanında <out>.sentences.json:
her cümlenin başı/sonu — plan kesimlerini buradan al.
"""
import argparse, json, os, re, subprocess, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import align as A

VOW = set("aeıioöuüAEIİOÖUÜâîûÂÎÛ")


def sentences(text):
    flat = re.sub(r"\s+", " ", text.replace("\n", " "))
    return [s.strip() for s in re.findall(r"[^.!?…]+[.!?…]+", flat) if s.strip()]


def map_sentences(audio, text, min_block=0.12):
    x = A.load_audio(audio)
    blocks, _ = A.speech_blocks(A.envelope(x))
    blocks = [b for b in blocks if b[1] - b[0] > min_block]
    sents = sentences(text)
    syl = [max(1, sum(c in VOW for c in s)) for s in sents]
    S, B = len(sents), len(blocks)
    if S > B:
        raise SystemExit(f"{S} cümle ama {B} konuşma bloğu — metin sesle aynı mı?")
    rate = sum(syl) / sum(b[1] - b[0] for b in blocks)
    INF = 1e18
    D = np.full((S + 1, B + 1), INF)
    P = np.zeros((S + 1, B + 1), int)
    D[0][0] = 0
    for k in range(S):
        for i in range(B):
            if D[k][i] >= INF:
                continue
            for j in range(i + 1, B + 1):
                d = blocks[j - 1][1] - blocks[i][0]
                c = D[k][i] + np.log(syl[k] / max(d, 0.05) / rate) ** 2
                if c < D[k + 1][j]:
                    D[k + 1][j], P[k + 1][j] = c, i
    j, spans = B, []
    for k in range(S, 0, -1):
        i = P[k][j]
        spans.append((i, j))
        j = i
    spans.reverse()
    out = []
    for k, (i, j) in enumerate(spans):
        s0, s1 = blocks[i][0], blocks[j - 1][1]
        out.append(dict(s=round(s0, 3), e=round(s1, 3), text=sents[k], syl=syl[k],
                        rate=round(syl[k] / (s1 - s0), 2)))
    return out, rate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--emphasis", nargs="*", default=[])
    ap.add_argument("--pad", type=float, default=0.12, help="cümle parçasına eklenen pay (s)")
    a = ap.parse_args()

    sents, rate = map_sentences(a.audio, open(a.text, encoding="utf-8").read())
    print(f"{len(sents)} cümle · ortalama {rate:.2f} hece/sn")
    for s in sents:
        flag = "" if 3.5 <= s["rate"] <= 9.0 else "   <== ŞÜPHELİ HIZ"
        print(f"  {s['s']:6.2f}-{s['e']:6.2f}  {s['rate']:4.1f} h/s  {s['text'][:60]}{flag}")

    caps = []
    with tempfile.TemporaryDirectory() as td:
        for k, s in enumerate(sents):
            t0 = max(0.0, s["s"] - a.pad)
            w, t, o = f"{td}/s.wav", f"{td}/s.txt", f"{td}/s.json"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}",
                            "-to", f"{s['e'] + a.pad:.3f}", "-i", a.audio,
                            "-ac", "1", "-ar", "44100", w], check=True)
            open(t, "w", encoding="utf-8").write(s["text"] + "\n")
            cmd = [sys.executable, f"{HERE}/align.py", "--audio", w, "--text", t, "--out", o]
            if a.emphasis:
                cmd += ["--emphasis"] + a.emphasis
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode:
                raise SystemExit(f"cümle {k} hizalanamadı: {r.stderr[-300:]}")
            for c in json.load(open(o, encoding="utf-8")):
                c["s"], c["e"] = round(c["s"] + t0, 3), round(c["e"] + t0, 3)
                caps.append(c)
    for i in range(len(caps) - 1):
        caps[i]["e"] = min(caps[i]["e"], caps[i + 1]["s"])
    json.dump(caps, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sp = os.path.splitext(a.out)[0] + ".sentences.json"
    json.dump(sents, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"-> {a.out} ({len(caps)} kelime) · {sp}")


if __name__ == "__main__":
    main()
