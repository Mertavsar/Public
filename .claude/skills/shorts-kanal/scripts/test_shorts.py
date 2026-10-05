#!/usr/bin/env python3
"""shorts.py regresyon testi — koda dokunduysan çalıştır: python3 test_shorts.py"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "shorts.py")
sys.path.insert(0, HERE)
import shorts  # noqa: E402


def run(*args):
    r = subprocess.run([sys.executable, TOOL, *args], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


def write(d, name, text):
    p = os.path.join(d, name)
    open(p, "w", encoding="utf-8").write(text)
    return p


def test_num():
    cases = {"1.2M": 1.2e6, "850K": 850e3, "12.500": 12500, "12,500": 12500,
             "3,4 B": 3400, "1,5 Mn": 1.5e6, "2 milyon": 2e6, "": None, "abc": None}
    for s, want in cases.items():
        got = shorts.num(s)
        assert got == want, (s, got, want)


def test_outliers(d):
    csv = write(d, "r.csv",
                "kanal,abone,baslik,izlenme,tarih\n"
                "A,10K,a1,10K,2026-09-01\nA,10K,a2,12K,2026-09-02\n"
                "A,10K,a3,8K,2026-09-03\nA,10K,a4,90K,2026-09-04\n"
                "A,10K,a5,1K,2026-10-04\n"            # genç
                "B,1M,b1,200K,2026-09-01\nB,1M,b2,1.2M,2026-09-01\n")  # az veri
    out = run("outliers", csv, "--bugun", "2026-10-05")
    lines = [l for l in out.splitlines() if l.startswith("| 1 |")]
    assert "a4" in lines[0] and "PATLADI" in lines[0], out   # 90K / medyan 11K
    assert "genç" in out and "az veri" in out, out
    assert "1 PATLADI" in out, out


def test_pool(d):
    csv = write(d, "p.csv",
                "id,fikir,merak,netlik,kitle,uretim,klip,durum\n"
                "F1,iyi,9,9,8,8,9,\n"
                "F2,klipsiz,10,10,10,10,2,\n"         # veto
                "F3,orta,6,6,6,6,6,\n"
                "F4,yayinda,9,9,9,9,9,yayinda\n")
    out = run("pool", csv, "--ilk", "2")
    assert "ELENDİ (klip" in out, out
    assert "İLK 2: F1" in out and "F3" in out.split("İLK 2:")[1], out
    assert "F4" not in out.split("İLK 2:")[1].splitlines()[0], out
    out = run("pool", csv, "--agirlik", "klip=3")
    assert "klip×3" in out, out


def test_retention(d):
    # 0-3s açılış kaybı, 12-14s sert düşüş, 20-26s düz, sonda yükseliş
    pts = [(0, 100), (1, 85), (2, 78), (3, 74), (6, 71), (9, 68), (12, 65),
           (13, 58), (14, 51), (17, 48), (20, 46), (23, 45.5), (26, 45.2), (29, 52)]
    csv = write(d, "ret.csv", "saniye,yuzde\n" + "\n".join(f"{t},{p}" for t, p in pts))
    words = []
    sents = [("Gergedan", "onu", "görmüyor."), ("Bir", "karış", "ötede."),
             ("Asıl", "mesele", "çukur.")]
    spans = [(0, 4), (4, 12.5), (12.5, 30)]
    for (s0, s1), sent in zip(spans, sents):
        step = (s1 - s0) / len(sent)
        for i, w in enumerate(sent):
            words.append({"w": w, "s": s0 + i * step, "e": s0 + (i + 1) * step, "c": "white"})
    cap = write(d, "cap.json", json.dumps(words, ensure_ascii=False))
    edl = write(d, "edl.tsv", "# out0\tout1\n"
                "0.00\t12.50\t0\t1\t1\t1\t.5\t.5\t40\tR\tHOOK\n"
                "12.50\t30.00\t0\t1\t1\t1\t.5\t.5\t40\tM\tcukur\n")
    out = run("retention", csv, "--captions", cap, "--edl", edl)
    assert "DÜŞÜŞ 1: 12.0–14.0s" in out, out
    assert 'cümle 3: "Asıl mesele çukur."' in out, out
    assert "plan 2 (cukur)" in out, out
    assert "GÜÇLÜ BÖLGE" in out and "20.0–26.0s" in out, out
    assert "26.0–29.0s" in out and "döngü" in out, out
    assert "Sonda yükseliş var" in out, out


def test_roadmap():
    out = run("roadmap", "--gunluk", "2", "--ort-izlenme", "20000", "--abone-orani", "1.5")
    assert "180 video" in out, out
    assert "55.6K" in out, out                      # 10M / 180
    assert "ÖNCE GELEN: ABONE" in out, out          # 60 abone/gün vs 40K izlenme/gün
    assert "pencereyi aşıyor" in out, out           # 250 gün > 90


if __name__ == "__main__":
    test_num()
    with tempfile.TemporaryDirectory() as d:
        test_outliers(d)
        test_pool(d)
        test_retention(d)
    test_roadmap()
    print("tamam: 5 test geçti")
