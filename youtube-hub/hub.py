#!/usr/bin/env python3
"""
YouTube Hub — komut satırı.

  python3 youtube-hub/hub.py serve                      panel (tarayıcı kendiliğinden açılır)
  python3 youtube-hub/hub.py sync                       tüm kanalları senkronize et
  python3 youtube-hub/hub.py status                     kanallar, son 28 gün, kota
  python3 youtube-hub/hub.py thumb VIDEO_ID dosya.jpg   tek videoya kapak
  python3 youtube-hub/hub.py bulk-thumbs klasör/        klasördeki VIDEO_ID.jpg|png dosyaları
  python3 youtube-hub/hub.py banner KANAL_ID dosya.jpg  kanal banner'ı
  python3 youtube-hub/hub.py undo ISLEM_ID              kapak/banner değişikliğini geri al

`sync` zamanlanmış görev (cron / launchd) olarak günde 1-4 kez çalıştırılabilir.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import config  # noqa: E402
from core.images import ImageRejected  # noqa: E402
from core.service import Hub  # noqa: E402


def fmt(n):
    return "—" if n is None else f"{n:,}".replace(",", ".")


def pct(v):
    return "  —  " if v is None else f"{v * 100:+.0f}%"


def cmd_status(hub, a):
    p = hub.portfolio(a.days)
    t = p["totals"]
    print(f"{len(p['channels'])} kanal · {fmt(t['subscribers'])} abone")
    if not p["anchor"]:
        print("Henüz analitik verisi yok. Önce: hub.py sync")
        return
    cur, ch_ = t["cur"], t["change"]
    print(f"Dönem {p['period']['start']} – {p['period']['end']} (önceki {a.days} güne göre)")
    print(f"  izlenme {fmt(cur['views'])} {pct(ch_['views'])} · izlenme süresi "
          f"{fmt(cur['minutes'] // 60)} saat {pct(ch_['minutes'])} · abone net {cur['subs_net']:+d}\n")
    print(f"  {'Kanal':<30} {'Abone':>10} {'İzlenme':>12} {'Değişim':>8} {'Ort.izleme':>10} {'Yükleme':>8}")
    for ch in sorted(p["channels"], key=lambda c: -c["cur"]["views"]):
        avg = ch["cur"]["avg_view_s"]
        avg = f"{avg // 60}:{avg % 60:02d}" if avg is not None else "—"
        err = "  ⚠ " + ch["sync_error"][:60] if ch["sync_error"] else ""
        print(f"  {ch['title'][:30]:<30} {fmt(ch['subscribers']):>10} {fmt(ch['cur']['views']):>12} "
              f"{pct(ch['change']['views']):>8} {avg:>10} {ch['cur']['uploads']:>8}{err}")
    top = hub.top_videos(a.days, limit=5)
    if top:
        print("\n  Dönemin en çok izlenenleri:")
        for v in top:
            print(f"    {fmt(v['views']):>10}  {(v['title'] or v['video_id'])[:50]:<50}  {v['channel_title'][:20]}")
    q = p["quota"]
    print(f"\nKota (tahmini, {q['day']} PT): {q['used']} / {q['limit']}")


def cmd_sync(hub, _):
    results = hub.sync_all()
    if results is None:
        print("Başka bir senkronizasyon zaten çalışıyor.")
        return 1
    if not results:
        print("Bağlı kanal yok. Önce panelden 'Kanal ekle'.")
    bad = 0
    for r in results:
        if r["ok"]:
            print(f"✓ {r['channel_id']}: {r['videos']} video, {r['days']} gün analitik")
        else:
            bad += 1
            print(f"✗ {r['channel_id']}: {r['error']}")
        for n in r.get("notes", []):
            print(f"    not: {n}")
    print(f"Kota (tahmini): {hub.quota_today()['used']} / {config.DAILY_QUOTA}")
    return 1 if bad else 0


def _read(path):
    with open(path, "rb") as f:
        return f.read()


def _show(info):
    for w in info.get("warnings", []):
        print(f"    uyarı: {w}")
    print(f"    işlem no: {info.get('action_id')} (geri almak için: hub.py undo {info.get('action_id')})")


def cmd_thumb(hub, a):
    info = hub.set_thumbnail(a.video_id, _read(a.file))
    print(f"✓ Kapak yüklendi: {a.video_id}")
    _show(info)


def cmd_bulk(hub, a):
    files = sorted(f for f in os.listdir(a.folder)
                   if f.lower().endswith((".jpg", ".jpeg", ".png")) and not f.startswith("."))
    cost = len(files) * config.QUOTA_COST["thumbnails.set"]
    left = config.DAILY_QUOTA - hub.quota_today()["used"]
    print(f"{len(files)} dosya · tahmini {cost} birim · kalan ~{left} birim")
    if cost > left:
        print("Kota yetmeyebilir; ilk dosyalar yüklenecek, kota bitince durulacak.")
    ok = 0
    for f in files:
        vid = os.path.splitext(f)[0]
        try:
            hub.set_thumbnail(vid, _read(os.path.join(a.folder, f)))
            ok += 1
            print(f"✓ {vid}")
        except (ImageRejected, KeyError, ValueError) as e:
            print(f"✗ {vid}: {e}")
        except Exception as e:
            print(f"✗ {vid}: {e}")
            if "quota" in str(e).lower():
                print("Kota bitti, durduruldu. Pasifik saatiyle gece yarısı sıfırlanır.")
                break
    print(f"{ok}/{len(files)} kapak yüklendi.")
    return 0 if ok == len(files) else 1


def cmd_banner(hub, a):
    info = hub.set_banner(a.channel_id, _read(a.file))
    print(f"✓ Banner güncellendi: {a.channel_id}")
    _show(info)


def cmd_undo(hub, a):
    hub.undo(a.action_id)
    print(f"✓ İşlem {a.action_id} geri alındı.")


def main(argv=None):
    p = argparse.ArgumentParser(prog="hub.py", description="YouTube Hub")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve"); s.add_argument("--no-browser", action="store_true")
    sub.add_parser("sync")
    s = sub.add_parser("status"); s.add_argument("--days", type=int, default=28, choices=config.WINDOWS)
    s = sub.add_parser("thumb"); s.add_argument("video_id"); s.add_argument("file")
    s = sub.add_parser("bulk-thumbs"); s.add_argument("folder")
    s = sub.add_parser("banner"); s.add_argument("channel_id"); s.add_argument("file")
    s = sub.add_parser("undo"); s.add_argument("action_id", type=int)
    a = p.parse_args(argv)

    if a.cmd == "serve":
        from web.server import serve
        return serve(open_browser=not a.no_browser)
    hub = Hub()
    handlers = {"sync": cmd_sync, "status": cmd_status, "thumb": cmd_thumb,
                "bulk-thumbs": cmd_bulk, "banner": cmd_banner, "undo": cmd_undo}
    try:
        return handlers[a.cmd](hub, a) or 0
    except KeyError as e:
        print(f"✗ {e.args[0] if e.args else e}")
        return 1
    except (ImageRejected, ValueError, OSError) as e:
        print(f"✗ {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
