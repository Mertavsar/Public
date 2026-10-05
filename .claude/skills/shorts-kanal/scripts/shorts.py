#!/usr/bin/env python3
"""Shorts kanal sistemi — hesap işleri.

Yorum Claude'un işi; sayılar burada. Elle bölme yapınca hata çıkıyor
(ortalama yerine medyan, yaşı oturmamış video, yanlış satır). Bu araç
dört aşamanın sayısal kısmını sabitler:

  outliers   Aşama 3 — rakip videoların kanal medyanına göre performansı
  pool       Aşama 4 — fikir havuzunu puanla, sırala, ilk çekilecekleri seç
  retention  Aşama 9 — elde tutma eğrisindeki sert düşüşleri cümleye/plana bağla
  roadmap    Aşama 10 — para kazanma eşiğine giden hesap

Sadece standart kütüphane. Örnek: python3 shorts.py outliers rakip-videolar.csv
"""
import argparse
import csv
import json
import re
import statistics
import sys
from datetime import date

# ---------------------------------------------------------------- ortak


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f)]
    # baştaki/sondaki boşlukları at, '#' ile başlayan satırları yorum say
    out = []
    for r in rows:
        r = {(k or "").strip(): (v or "").strip() for k, v in r.items()}
        first = next(iter(r.values()), "")
        if first.startswith("#") or not any(r.values()):
            continue
        out.append(r)
    return out


def num(s):
    """'1.2M', '850K', '12.500', '12,500', '3,4B' -> float."""
    s = str(s).strip().lower().replace(" ", "")
    if not s:
        return None
    mult = 1
    for suf, m in (("milyon", 1e6), ("mn", 1e6), ("bin", 1e3), ("b", 1e3),
                   ("k", 1e3), ("m", 1e6)):
        if s.endswith(suf):
            mult, s = m, s[: -len(suf)]
            break
    if mult > 1:
        s = s.replace(",", ".")          # 3,4B -> 3.4
    else:
        s = s.replace(".", "").replace(",", "")  # 12.500 / 12,500 -> 12500
    try:
        return float(s) * mult
    except ValueError:
        return None


def fmt(n):
    if n is None:
        return "—"
    if n >= 1e6:
        return f"{n/1e6:.1f}M"
    if n >= 1e3:
        return f"{n/1e3:.1f}K"
    return f"{n:.0f}"


def parse_date(s):
    try:
        return date.fromisoformat(s[:10])
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------- outliers

def cmd_outliers(a):
    rows = read_csv(a.csv)
    if not rows:
        sys.exit("HATA: dosyada video yok (yorum satırları sayılmaz). Aşama 3 §1: en az 3 kanal × 5 Shorts.")
    today = parse_date(a.bugun) if a.bugun else date.today()
    by_ch = {}
    for r in rows:
        r["_v"] = num(r.get("izlenme"))
        r["_s"] = num(r.get("abone"))
        d = parse_date(r.get("tarih", ""))
        r["_age"] = (today - d).days if d else None
        if r["_v"] is None:
            print(f"UYARI: izlenme okunamadı, atlandı: {r.get('baslik')}", file=sys.stderr)
            continue
        by_ch.setdefault(r.get("kanal", "?"), []).append(r)

    out = []
    for ch, vids in by_ch.items():
        given = num(vids[0].get("kanal_ort", ""))
        settled = [v["_v"] for v in vids if v["_age"] is None or v["_age"] >= a.min_yas]
        base = given or (statistics.median(settled) if settled else None)
        src = "verilen" if given else f"medyan/{len(settled)}"
        for v in vids:
            v["_base"], v["_src"] = base, src
            v["_ratio"] = v["_v"] / base if base else None
            v["_young"] = v["_age"] is not None and v["_age"] < a.min_yas
            v["_thin"] = not given and len(settled) < 3
            out.append(v)

    def label(v):
        r = v["_ratio"]
        if r is None:
            return "?"
        if r >= a.esik:
            return "PATLADI"
        if r >= 1.5:
            return "üstünde"
        if r <= 0.5:
            return "altında"
        return "normal"

    out.sort(key=lambda v: -(v["_ratio"] or 0))
    print(f"| # | Kanal | Başlık | İzlenme | Kanal tabanı | Kat | İzl/abone | Yaş | Durum |")
    print("|---|---|---|---|---|---|---|---|---|")
    for i, v in enumerate(out, 1):
        ps = v["_v"] / v["_s"] if v["_s"] else None
        notes = []
        if v["_young"]:
            notes.append("genç")
        if v["_thin"]:
            notes.append("az veri")
        st = label(v) + (f" ({', '.join(notes)})" if notes else "")
        ratio = "—" if v["_ratio"] is None else f"{v['_ratio']:.1f}x"
        per_sub = "—" if ps is None else f"{ps:.1f}"
        age = "—" if v["_age"] is None else f"{v['_age']}g"
        print(f"| {i} | {v.get('kanal')} | {v.get('baslik')} | {fmt(v['_v'])} | "
              f"{fmt(v['_base'])} ({v['_src']}) | {ratio} | {per_sub} | {age} | {st} |")

    n_out = sum(1 for v in out if label(v) == "PATLADI")
    n_low = sum(1 for v in out if label(v) == "altında")
    print(f"\n{len(out)} video · {len(by_ch)} kanal · {n_out} PATLADI (≥{a.esik}x) · {n_low} altında (≤0.5x)")
    print(f"Taban: kanalın kendi medyanı (yaşı ≥{a.min_yas} gün olanlar). "
          "Ortalama değil — tek bir patlama ortalamayı şişirir.")
    if any(v["_thin"] for v in out):
        print("UYARI: 'az veri' — kanaldan 3'ten az oturmuş video var, kat güvenilmez. "
              "O kanaldan daha fazla video ekle ya da kanal_ort sütununu doldur.")
    if any(v["_young"] for v in out):
        print(f"UYARI: 'genç' — {a.min_yas} günden yeni video, izlenmesi henüz oturmadı; "
              "kat olduğundan düşük görünür.")
    if n_out == 0:
        print("UYARI: hiç PATLADI yok. Aşama 3'ün kuralı outlier'lardan çıkar — "
              "listeye her kanalın en çok izlenen Shorts'larını da ekle.")


# ---------------------------------------------------------------- pool

CRIT = ["merak", "netlik", "kitle", "uretim", "klip"]


def cmd_pool(a):
    rows = read_csv(a.csv)
    if not rows:
        sys.exit("HATA: havuz boş (yorum satırları sayılmaz). Aşama 4 Tur 2: 30 fikir.")
    crit = [c for c in CRIT if c in (rows[0] if rows else {})]
    if not crit:
        sys.exit(f"HATA: puan sütunu yok. Beklenen: {', '.join(CRIT)}")
    w = {c: 1.0 for c in crit}
    for kv in a.agirlik or []:
        k, v = kv.split("=")
        if k not in w:
            sys.exit(f"HATA: bilinmeyen kriter '{k}'. Var olanlar: {', '.join(crit)}")
        w[k] = float(v)
    wmax = sum(10 * w[c] for c in crit)

    scored, bad = [], []
    for r in rows:
        sc = {}
        for c in crit:
            try:
                v = float(r.get(c, "").replace(",", "."))
            except ValueError:
                v = None
            if v is None or not 1 <= v <= 10:
                bad.append(f"{r.get('id')}: '{c}' 1-10 arası değil ({r.get(c)!r})")
                v = None
            sc[c] = v
        if None in sc.values():
            continue
        total = sum(sc[c] * w[c] for c in crit) / wmax * 100
        veto = [c for c in crit if sc[c] <= a.veto]
        r["_t"], r["_veto"], r["_sc"] = total, veto, sc
        scored.append(r)

    for b in bad:
        print("UYARI:", b, file=sys.stderr)
    scored.sort(key=lambda r: (bool(r["_veto"]), -r["_t"]))

    head = " | ".join(c for c in crit)
    print(f"| # | id | Fikir | {head} | Puan /100 | Durum |")
    print("|---|---|---|" + "---|" * len(crit) + "---|---|")
    for i, r in enumerate(scored, 1):
        st = r.get("durum", "") or "havuz"
        if r["_veto"]:
            st = f"ELENDİ ({', '.join(r['_veto'])} ≤{a.veto:g})"
        cells = " | ".join(f"{r['_sc'][c]:g}" for c in crit)
        print(f"| {i} | {r.get('id')} | {r.get('fikir')} | {cells} | {r['_t']:.0f} | {st} |")

    done = {"yayinda", "yayında", "cekildi", "çekildi", "iptal"}
    pick = [r for r in scored if not r["_veto"] and r.get("durum", "").lower() not in done][: a.ilk]
    print(f"\nİLK {a.ilk}: " + " · ".join(f"{r.get('id')} ({r['_t']:.0f})" for r in pick))
    wtxt = ", ".join(f"{c}×{w[c]:g}" for c in crit)
    print(f"Ağırlık: {wtxt} · veto: herhangi bir kriter ≤{a.veto:g} ise fikir elenir "
          "(ortalaması yüksek olsa bile — klip yoksa video yok).")


# ---------------------------------------------------------------- retention

def load_sentences(path):
    """captions.json (align.py çıktısı) -> [(başlangıç, bitiş, cümle)]."""
    words = json.load(open(path, encoding="utf-8"))
    sents, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r"[.!?:…]$", w["w"]):
            sents.append((cur[0]["s"], cur[-1]["e"], " ".join(x["w"] for x in cur)))
            cur = []
    if cur:
        sents.append((cur[0]["s"], cur[-1]["e"], " ".join(x["w"] for x in cur)))
    return sents


def load_edl(path):
    plans = []
    for line in open(path, encoding="utf-8"):
        if not line.strip() or line.startswith("#"):
            continue
        f = line.rstrip("\n").split("\t")
        plans.append((float(f[0]), float(f[1]), f[-1] if len(f) > 10 else ""))
    return plans


def at(items, t):
    for i, (s, e, txt) in enumerate(items):
        if s <= t < e:
            return i, txt
    # boşluğa düştüyse en yakın önceki
    prev = [i for i, (s, _, _) in enumerate(items) if s <= t]
    return (prev[-1], items[prev[-1]][2]) if prev else (None, "")


def cmd_retention(a):
    pts = []
    for r in read_csv(a.csv):
        try:
            t = float(r.get("saniye", "").replace(",", "."))
            p = float(r.get("yuzde", "").replace("%", "").replace(",", "."))
        except ValueError:
            continue
        pts.append((t, p))
    pts.sort()
    if len(pts) < 4:
        sys.exit("HATA: en az 4 nokta gerekli (saniye,yuzde).")

    sents = load_sentences(a.captions) if a.captions else []
    plans = load_edl(a.edl) if a.edl else []
    dur = a.sure or pts[-1][0]

    def where(t):
        s = at(sents, t) if sents else (None, "")
        p = at(plans, t) if plans else (None, "")
        parts = []
        if s[0] is not None:
            parts.append(f'cümle {s[0]+1}: "{s[1]}"')
        if p[0] is not None:
            parts.append(f"plan {p[0]+1}" + (f" ({p[1]})" if p[1] else ""))
        return " · ".join(parts) or "—"

    # 1) açılış: ilk 3 saniyedeki kayıp normal ama boyutu önemli
    p0 = pts[0][1]
    p3 = next((p for t, p in pts if t >= a.acilis), pts[-1][1])
    print(f"AÇILIŞ (0–{a.acilis:g}s): %{p0:.0f} → %{p3:.0f}  ({p3 - p0:+.0f} puan)")
    print("  Beklenen kayıp; asıl açılış metriği Studio'daki 'izlemeye devam eden' oranı. "
          "Onu ayrıca not et.\n")

    # 2) gövde: saniye başına kayıp
    seg = []
    for (t0, q0), (t1, q1) in zip(pts, pts[1:]):
        if t1 <= a.acilis or t1 == t0:
            continue
        seg.append((t0, t1, q0, q1, (q0 - q1) / (t1 - t0)))
    if not seg:
        sys.exit("HATA: açılış sonrasında nokta yok.")
    rates = [s[4] for s in seg]
    base = max(statistics.median(rates), 0.0)
    thr = max(a.kat * base, a.min_dusus)

    drops, cur = [], None
    for s in seg:
        if s[4] >= thr:
            cur = [s[0], s[1], s[2], s[3]] if cur is None else [cur[0], s[1], cur[2], s[3]]
        elif cur:
            drops.append(cur)
            cur = None
    if cur:
        drops.append(cur)

    print(f"GÖVDE: normal kayıp {base:.2f} puan/s · sert düşüş eşiği {thr:.2f} puan/s")
    if not drops:
        print("  Sert düşüş yok.\n")
    for i, (t0, t1, q0, q1) in enumerate(sorted(drops, key=lambda d: d[3] - d[2]), 1):
        print(f"  DÜŞÜŞ {i}: {t0:.1f}–{t1:.1f}s  %{q0:.0f} → %{q1:.0f} ({q1 - q0:+.1f} puan)")
        # izleyici bir önceki cümlede karar verir — ikisini de göster
        print(f"    o an    : {where((t0 + t1) / 2)}")
        print(f"    hemen önce: {where(max(t0 - 1.0, 0))}")

    # 3) düz bölgeler = güçlü malzeme; yükselişler = tekrar izlenen an
    def runs(pred, min_len):
        res, cur = [], None
        for s in seg:
            if pred(s[4]):
                cur = [s[0], s[1], s[2], s[3]] if cur is None else [cur[0], s[1], cur[2], s[3]]
            else:
                if cur and cur[1] - cur[0] >= min_len:
                    res.append(cur)
                cur = None
        if cur and cur[1] - cur[0] >= min_len:
            res.append(cur)
        return res

    flat = runs(lambda r: abs(r) <= a.duz, a.duz_sure)
    rise = runs(lambda r: r < -a.duz, 0)
    print("\nGÜÇLÜ BÖLGE (eğri düz — malzeme tutuyor, daha fazlasını yap):")
    if not flat:
        print("  Yok.")
    for t0, t1, q0, q1 in flat:
        print(f"  {t0:.1f}–{t1:.1f}s  %{q0:.0f} → %{q1:.0f} · {where((t0 + t1) / 2)}")
    print("\nTEKRAR İZLENEN AN (eğri yükseliyor — izleyici geri sarıyor):")
    if not rise:
        print("  Yok.")
    for t0, t1, q0, q1 in rise:
        end = " (son saniyeler → döngü)" if t1 >= pts[-1][0] else ""
        print(f"  {t0:.1f}–{t1:.1f}s  %{q0:.0f} → %{q1:.0f}{end} · {where((t0 + t1) / 2)}")

    # 4) kapanış: döngü çalışıyor mu
    last = pts[-1][1]
    print(f"\nKAPANIŞ: son nokta %{last:.0f}")
    if last >= 100:
        print("  %100 üstü — döngü çalışıyor, izleyici başa sarıyor.")
    elif pts[-1][1] > pts[-2][1]:
        print("  Sonda yükseliş var — döngü kısmen tutuyor.")
    else:
        print("  Sonda yükseliş yok — döngü cümlesi ilk cümleye bağlanmıyor olabilir.")
    if not sents:
        print("\nNOT: --captions verilmedi; düşüşler cümleye bağlanamadı. "
              "viral-edit build.py --work klasöründeki captions.json'ı ver.")


# ---------------------------------------------------------------- roadmap

def days_to(target, have, per_day):
    if have >= target:
        return 0
    if per_day <= 0:
        return None
    return (target - have) / per_day


def cmd_roadmap(a):
    win = a.pencere
    vids = a.gunluk * win
    need_v = max(a.hedef_izlenme - a.mevcut_izlenme, 0)
    need_s = max(a.hedef_abone - a.mevcut_abone, 0)

    print(f"HEDEF: {fmt(a.hedef_abone)} abone + {fmt(a.hedef_izlenme)} Shorts izlenmesi / {win} gün")
    print(f"Şu an: {fmt(a.mevcut_abone)} abone · son {win} günde {fmt(a.mevcut_izlenme)} izlenme\n")
    print(f"Plan: günde {a.gunluk:g} Shorts → {win} günde {vids:.0f} video")
    per_vid = need_v / vids if vids else float("inf")
    print(f"  İzlenme hedefi için video başına ORTALAMA {fmt(per_vid)} izlenme gerekiyor.")
    if need_v and a.abone_orani:
        print(f"  Bu izlenmeyle gelen abone: ~{fmt(need_v / 1000 * a.abone_orani)} "
              f"(1000 izlenmede {a.abone_orani:g} abone)")
    if need_v:
        conv = need_s / (need_v / 1000)
        print(f"  Aynı pencerede abone hedefi için gereken oran: 1000 izlenmede {conv:.2f} abone")

    if a.ort_izlenme:
        v_day = a.ort_izlenme * a.gunluk
        s_day = v_day / 1000 * a.abone_orani if a.abone_orani else 0
        dv, ds = days_to(a.hedef_izlenme, a.mevcut_izlenme, v_day), days_to(a.hedef_abone, a.mevcut_abone, s_day)
        print(f"\nMevcut gidişle (video başına ortalama {fmt(a.ort_izlenme)}):")
        print(f"  günde {fmt(v_day)} izlenme · {s_day:.1f} abone")
        print(f"  izlenme hedefi: {'—' if dv is None else f'{dv:.0f} gün'}")
        print(f"  abone hedefi  : {'—' if ds is None else f'{ds:.0f} gün'}")
        if dv is not None and ds is not None:
            first = "ABONE" if ds < dv else "İZLENME"
            print(f"  ÖNCE GELEN: {first}. Plan diğerine göre kurulur — darboğaz o.")
        if dv is not None and dv > win:
            print(f"  UYARI: izlenme hedefi {win} günlük pencereyi aşıyor. Pencere kayan "
                  f"bir pencere: eski izlenmeler düşer. Sabit hızla hiç yetişmeyebilir.")
            gap = per_vid / a.ort_izlenme if a.ort_izlenme else 0
            print(f"  Gereken ortalama mevcut ortalamanın {gap:.1f} katı.")
        if a.medyan:
            print("  NOT: verdiğin sayı medyansa ortalama daha yüksektir — Shorts izlenmesi "
                  "birkaç patlamaya yığılır. Hesap ortalamayla yapılır.")

    if a.patlama:
        hits = need_v * a.patlama_payi / a.patlama
        print(f"\nGerçekçi dağılım: izlenmenin %{a.patlama_payi*100:.0f}'i patlamalardan gelirse "
              f"{fmt(a.patlama)} izlenmelik ~{hits:.0f} patlama gerekir "
              f"({vids:.0f} videonun %{hits / vids * 100 if vids else 0:.0f}'i).")
    print("\nEşikler YouTube'un kararıdır ve değişebilir — başlamadan önce YouTube "
          "İş Ortağı Programı sayfasından güncel değeri teyit et.")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)

    o = sp.add_parser("outliers", help="Aşama 3: rakip videoları kanal tabanına göre kıyasla")
    o.add_argument("csv", help="kanal,abone,baslik,izlenme,tarih[,kanal_ort]")
    o.add_argument("--esik", type=float, default=3.0, help="PATLADI eşiği (kat, vars. 3)")
    o.add_argument("--min-yas", type=int, default=7, help="izlenmesi oturmuş sayılan yaş (gün)")
    o.add_argument("--bugun", help="YYYY-MM-DD (test için)")
    o.set_defaults(f=cmd_outliers)

    p = sp.add_parser("pool", help="Aşama 4: fikir havuzunu puanla ve sırala")
    p.add_argument("csv", help="id,fikir,merak,netlik,kitle,uretim,klip,durum")
    p.add_argument("--ilk", type=int, default=5, help="ilk çekilecek fikir sayısı")
    p.add_argument("--veto", type=float, default=3, help="bu puan ve altı fikri eler")
    p.add_argument("--agirlik", nargs="*", help="ör. merak=2 klip=1.5")
    p.set_defaults(f=cmd_pool)

    r = sp.add_parser("retention", help="Aşama 9: elde tutma düşüşlerini cümleye bağla")
    r.add_argument("csv", help="saniye,yuzde")
    r.add_argument("--captions", help="viral-edit captions.json (kelime zamanları)")
    r.add_argument("--edl", help="viral-edit edl.tsv (planlar)")
    r.add_argument("--sure", type=float, help="video süresi (s)")
    r.add_argument("--acilis", type=float, default=3.0, help="açılış bölgesi (s)")
    r.add_argument("--kat", type=float, default=2.5, help="normal kaybın kaç katı sert sayılır")
    r.add_argument("--min-dusus", type=float, default=1.5, help="sert düşüş alt sınırı (puan/s)")
    r.add_argument("--duz", type=float, default=0.3, help="düz bölge üst sınırı (puan/s)")
    r.add_argument("--duz-sure", type=float, default=3.0, help="düz bölge en kısa süre (s)")
    r.set_defaults(f=cmd_retention)

    m = sp.add_parser("roadmap", help="Aşama 10: para kazanma eşiği hesabı")
    m.add_argument("--hedef-abone", type=float, default=1000)
    m.add_argument("--hedef-izlenme", type=float, default=10_000_000)
    m.add_argument("--pencere", type=int, default=90, help="gün")
    m.add_argument("--mevcut-abone", type=float, default=0)
    m.add_argument("--mevcut-izlenme", type=float, default=0, help="son <pencere> gündeki Shorts izlenmesi")
    m.add_argument("--gunluk", type=float, default=1, help="günde kaç Shorts")
    m.add_argument("--ort-izlenme", type=float, help="video başına ortalama izlenme (kendi verin)")
    m.add_argument("--medyan", action="store_true", help="--ort-izlenme aslında medyan")
    m.add_argument("--abone-orani", type=float, default=0, help="1000 izlenmede kazanılan abone")
    m.add_argument("--patlama", type=float, help="bir patlamanın izlenmesi, ör. 1000000")
    m.add_argument("--patlama-payi", type=float, default=0.7, help="izlenmenin patlamalardan gelen payı")
    m.set_defaults(f=cmd_roadmap)

    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
