#!/usr/bin/env python3
"""
Agency AI — yerel panel.

Çalıştırmak için:   python3 agency-ai/app/server.py
Sonra tarayıcıda:   http://127.0.0.1:7777

Bu sunucu kendi başına analiz yapmaz. Claude Code CLI'ı motor olarak kullanır ve
skill'leri tek tek, sırayla çağırır. Böylece hiçbir skill atlanmaz ve her birinin
çıktısını ayrı ayrı görürsün.
"""

import http.server
import json
import os
import re
import shutil
import socketserver
import subprocess
import threading
import uuid
from datetime import date, timedelta
from urllib.parse import urlparse

# ----------------------------------------------------------------------------
# AYARLAR
# ----------------------------------------------------------------------------

PORT = 7777
APP_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(APP_DIR))
CLIENTS_DIR = os.path.join(REPO_ROOT, "agency-ai", "clients")

# Her adım için üst sınır (saniye). Uzun analizler için yükseltilebilir.
STEP_TIMEOUT = 900

# Claude'un kullanmasına izin verilen araçlar.
# Dosya okuma + Meta REKLAM OKUMA araçları. Yazma araçları bilerek yok:
# agency-ai/CLAUDE.md §0 — reklam hesabına onaysız işlem yasak.
#
# Meta verisi gelmiyorsa: yerel MCP sunucunun adı farklı olabilir.
#   claude mcp list
# komutuyla adı öğren ve aşağıdaki "mcp__Meta_Reklam__" önekini ona göre düzelt.
ALLOWED_TOOLS = [
    "Read", "Glob", "Grep",
    "mcp__Meta_Reklam__ads_get_ad_accounts",
    "mcp__Meta_Reklam__ads_get_ad_entities",
    "mcp__Meta_Reklam__ads_get_ad_account_pages",
    "mcp__Meta_Reklam__ads_get_creatives",
    "mcp__Meta_Reklam__ads_get_creative_ads",
    "mcp__Meta_Reklam__ads_get_errors",
    "mcp__Meta_Reklam__ads_insights_performance_trend",
    "mcp__Meta_Reklam__ads_insights_anomaly_signal",
    "mcp__Meta_Reklam__ads_insights_advertiser_context",
    "mcp__Meta_Reklam__ads_insights_auction_ranking_benchmarks",
    "mcp__Meta_Reklam__ads_insights_industry_benchmark",
    "mcp__Meta_Reklam__ads_get_dataset_quality",
    "mcp__Meta_Reklam__ads_get_datasets",
    "mcp__Meta_Reklam__ads_get_customconversions",
]

# Sıra ve başlıklar. "optional" olanlar arayüzden işaretlenmezse atlanır.
STEPS = [
    {"key": "meta-ads",        "title": "Meta Reklam Teşhisi",     "optional": False},
    {"key": "google-ads",      "title": "Google Ads Teşhisi",      "optional": True},
    {"key": "media-buyer",     "title": "Reklam Aksiyonları",      "optional": False},
    {"key": "cro",             "title": "Site Dönüşümü",           "optional": False},
    {"key": "sales",           "title": "Satış Süreci",            "optional": False},
    {"key": "account-manager", "title": "Müşteri İletişimi",       "optional": False},
    {"key": "agency-ceo",      "title": "İlişki Değerlendirmesi",  "optional": False},
    {"key": "weekly-growth",   "title": "Birleşik Rapor",          "optional": False},
]

RUNS = {}
RUNS_LOCK = threading.Lock()


# ----------------------------------------------------------------------------
# MÜŞTERİLER
# ----------------------------------------------------------------------------

def list_clients():
    if not os.path.isdir(CLIENTS_DIR):
        return []
    out = []
    for slug in sorted(os.listdir(CLIENTS_DIR)):
        path = os.path.join(CLIENTS_DIR, slug)
        if not os.path.isdir(path) or slug.startswith("."):
            continue
        name, account = slug, ""
        cfile = os.path.join(path, "client.md")
        if os.path.isfile(cfile):
            try:
                text = open(cfile, encoding="utf-8").read()
                m = re.search(r"^#\s+(.+)$", text, re.M)
                if m:
                    name = m.group(1).strip()
                m = re.search(r"Meta reklam hesabı ID:\**\s*(\d+)", text)
                if m:
                    account = m.group(1)
            except OSError:
                pass
        out.append({"slug": slug, "name": name, "account": account})
    return out


# ----------------------------------------------------------------------------
# PROMPT ÜRETİMİ
# ----------------------------------------------------------------------------

def base_context(run):
    notes = run["notes"].strip() or "(ajans sahibi not girmedi)"
    raw = run.get("data", "").strip()
    veri = f"""
AJANS SAHİBİNİN ELLE GİRDİĞİ VERİ (panelden çekemezsen bunu kullan):
{raw}
""" if raw else """
Elle girilmiş veri yok. Gereken veriyi Meta araçlarıyla kendin çek.
"""
    return f"""Bir dijital ajans işletim sistemi içinde çalışıyorsun.

MARKA:        {run['client_name']}  (klasör: agency-ai/clients/{run['client']}/)
DÖNEM:        {run['date_from']} — {run['date_to']}
AJANS SAHİBİNİN NOTU:
{notes}
{veri}
ÖNCE ŞUNLARI OKU (zorunlu, hafızadan yazma):
- agency-ai/CLAUDE.md            (sistemin anayasası — özellikle §0 ve kanıt disiplini)
- agency-ai/clients/{run['client']}/client.md
- agency-ai/clients/{run['client']}/strategy.md
- agency-ai/clients/{run['client']}/weekly-reports/  (varsa son raporlar)
"""


def step_prompt(run, key, title, previous):
    ctx = base_context(run)
    if key == "weekly-growth":
        birlesim = "\n\n".join(
            f"### {p['title']}\n\n{p['output']}" for p in previous if p.get("output")
        )
        return f"""{ctx}
- .claude/skills/weekly-growth/SKILL.md

Diğer uzmanların bu marka için ürettiği bulgular aşağıda. Bunları BİRLEŞTİR ve
weekly-growth skill'indeki 15 bölümlü raporu üret. Yeni analiz yapma, sentezle.
Rapor "BU HAFTANIN 5 KARARI" ile bitsin.

--- UZMAN BULGULARI ---
{birlesim}
--- BULGULAR BİTTİ ---

Sadece raporu yaz. Giriş cümlesi, "işte rapor" gibi ifadeler kullanma.
"""

    return f"""{ctx}
- .claude/skills/{key}/SKILL.md   ← SENİN ROLÜN BU

Bu skill'in tanımladığı rolü üstlen ve SADECE kendi alanınla ilgilen. Diğer
uzmanların alanına girme; onlar ayrı çalışıyor.

Reklam verisine ihtiyacın varsa Meta araçlarıyla KENDİN ÇEK. client.md'de hesap ID'si
yazılıdır. Ajans sahibinden rakam isteme.

KURALLAR:
- agency-ai/CLAUDE.md §0 geçerli: reklam hesabında HİÇBİR değişiklik yapma. Sadece oku.
- Sadece client.md'de ID'si yazılı hesaba bak. Başka hesaba dokunma.
- Her bulguyu FACT / HYPOTHESIS / MISSING olarak etiketle.
- Veri yoksa uydurma. "Veri mevcut değil" de ve neye ihtiyacın olduğunu yaz.
- Bu alan bu markada geçerli değilse bunu tek cümleyle söyle ve bitir.
- Çıktın markdown olsun. Başlık "## {title}" ile başlasın.
- Giriş cümlesi kurma, doğrudan analize gir.
"""


# ----------------------------------------------------------------------------
# ÇALIŞTIRMA
# ----------------------------------------------------------------------------

def run_claude(prompt):
    exe = shutil.which("claude")
    if not exe:
        raise RuntimeError(
            "Claude Code CLI bulunamadı. Kurulum: https://claude.com/claude-code"
        )
    cmd = [exe, "-p", prompt, "--output-format", "text",
           "--allowedTools", *ALLOWED_TOOLS]
    proc = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=STEP_TIMEOUT
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "bilinmeyen hata").strip()[:2000])
    return proc.stdout.strip()


def save_report(run):
    folder = os.path.join(CLIENTS_DIR, run["client"], "weekly-reports")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{run['date_to']}.md")
    parts = [
        f"# {run['client_name']} — ANALİZ",
        f"**Dönem:** {run['date_from']} — {run['date_to']}",
        f"**Üretim:** {run['started']}",
        "",
    ]
    if run["notes"].strip():
        parts += ["## Ajans sahibinin notu", "", "> " + run["notes"].strip(), ""]
    for s in run["steps"]:
        if s["status"] == "done" and s["output"]:
            parts += [s["output"], "", "---", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    return os.path.relpath(path, REPO_ROOT)


def execute(run_id):
    with RUNS_LOCK:
        run = RUNS[run_id]
    done = []
    for step in run["steps"]:
        with RUNS_LOCK:
            step["status"] = "running"
        try:
            out = run_claude(step_prompt(run, step["key"], step["title"], done))
            with RUNS_LOCK:
                step["output"] = out
                step["status"] = "done"
            done.append(step)
        except subprocess.TimeoutExpired:
            with RUNS_LOCK:
                step["status"] = "error"
                step["error"] = f"Zaman aşımı ({STEP_TIMEOUT} sn). Dönemi daraltmayı dene."
        except Exception as exc:  # noqa: BLE001 - hatayı arayüze taşımak istiyoruz
            with RUNS_LOCK:
                step["status"] = "error"
                step["error"] = str(exc)
    try:
        path = save_report(run)
    except OSError as exc:
        path, run["save_error"] = None, str(exc)
    with RUNS_LOCK:
        run["report_path"] = path
        run["status"] = "done"


# ----------------------------------------------------------------------------
# HTTP
# ----------------------------------------------------------------------------

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            try:
                body = open(os.path.join(APP_DIR, "index.html"), "rb").read()
            except OSError:
                self.send_error(500, "index.html bulunamadi")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/init":
            yesterday = date.today() - timedelta(days=1)
            self._json({
                "clients": list_clients(),
                "steps": STEPS,
                "date_from": str(yesterday - timedelta(days=6)),
                "date_to": str(yesterday),
            })
            return
        if path.startswith("/api/run/"):
            run_id = path.rsplit("/", 1)[-1]
            with RUNS_LOCK:
                run = RUNS.get(run_id)
                payload = json.loads(json.dumps(run, ensure_ascii=False)) if run else None
            if payload is None:
                self._json({"error": "bulunamadi"}, 404)
            else:
                self._json(payload)
            return
        self.send_error(404)

    def do_POST(self):
        if urlparse(self.path).path != "/api/run":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._json({"error": "gecersiz istek"}, 400)
            return

        slug = data.get("client")
        clients = {c["slug"]: c for c in list_clients()}
        if slug not in clients:
            self._json({"error": "Müşteri bulunamadı"}, 400)
            return

        chosen = set(data.get("steps") or [])
        steps = [
            {"key": s["key"], "title": s["title"], "status": "pending",
             "output": "", "error": ""}
            for s in STEPS if not s["optional"] or s["key"] in chosen
        ]
        run_id = uuid.uuid4().hex[:12]
        run = {
            "id": run_id,
            "client": slug,
            "client_name": clients[slug]["name"],
            "account": clients[slug]["account"],
            "date_from": data.get("date_from") or "",
            "date_to": data.get("date_to") or str(date.today() - timedelta(days=1)),
            "notes": data.get("notes") or "",
            "data": data.get("data") or "",
            "started": __import__("datetime").datetime.now().strftime("%d.%m.%Y %H:%M"),
            "status": "running",
            "steps": steps,
            "report_path": None,
        }
        with RUNS_LOCK:
            RUNS[run_id] = run
        threading.Thread(target=execute, args=(run_id,), daemon=True).start()
        self._json({"id": run_id})


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    if not shutil.which("claude"):
        print("UYARI: Claude Code CLI bulunamadı. Analiz çalışmaz.")
        print("Kurulum: https://claude.com/claude-code\n")
    print(f"Agency AI paneli:  http://127.0.0.1:{PORT}")
    print(f"Proje kökü:        {REPO_ROOT}")
    print("Durdurmak için Ctrl+C\n")
    with Server(("127.0.0.1", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKapatıldı.")


if __name__ == "__main__":
    main()
