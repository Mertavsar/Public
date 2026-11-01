"""Blog yazılarını tek tıkla kopyalanabilir bir sayfaya (kopyala.html) dönüştürür."""
import html, re
from pathlib import Path

ns = {"__file__": "build.py"}
exec((Path(__file__).parent / "build.py").read_text().split("posts, ok, rows = [], True, []")[0], ns)
ROOT = Path(__file__).parent


def content(meta, blocks):
    body = ns["wp"](meta, blocks, [])
    body = re.sub(r"<!-- wp:html -->.*?<!-- /wp:html -->", "", body, flags=re.S)
    body = re.sub(r"<!-- /?wp:[^>]*-->\n?", "", body)
    body = body.replace('href="/', f'href="{ns["SITE"]}/')
    return re.sub(r' class="[^"]*"', "", body).strip()


def field(label, value, fid):
    v = html.escape(value)
    return (f'<div class="row"><dt>{label}</dt><dd><span id="{fid}">{v}</span>'
            f'<button type="button" class="mini" data-copy="{fid}">Kopyala</button></dd></div>')


posts = [ns["parse"](f)[:2] for f in sorted((ROOT / "kaynak").glob("*.txt"))]
tabs, panels = [], []
for i, (m, blocks) in enumerate(posts, 1):
    tabs.append(f'<a class="tab" href="#yazi-{i}" data-tab="{i}"><b>{i}</b><span>{html.escape(m["focus"])}</span></a>')
    rows = "".join(field(l, m[k], f"f{i}-{k}") for l, k in [("Başlık", "title"), ("SEO başlık", "seo_title"),
             ("Meta açıklama", "meta"), ("Kalıcı bağlantı", "slug"), ("Odak kelime", "focus"), ("Özet", "excerpt"),
             ("Görsel alt metni", "alt")])
    panels.append(f'''<section class="panel" id="p{i}" data-panel="{i}" hidden>
  <div class="bar"><div><p class="eyebrow">Yazı {i} / {len(posts)}</p><h2>{html.escape(m["title"])}</h2></div>
  <button type="button" class="big" data-rich="c{i}">Yazıyı kopyala</button></div>
  <p class="status" id="s{i}" role="status"></p>
  <details class="seo"><summary>Başlık ve SEO alanları</summary><dl>{rows}</dl>
  <p class="hint">Öne çıkan görsel önerisi: {html.escape(m["image"])}</p></details>
  <article class="post" id="c{i}">{content(m, blocks)}</article>
</section>''')

page = f'''<title>Hipnoz Blog Yazıları</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;700;800&family=Lora:ital,wght@0,400;0,600;1,400&display=swap">
<style>
/* Tek sütun: üstte sekmeler, altta seçili yazının kopyalama çubuğu ve önizlemesi */
:root {{
  --bg: #f7f6fd; --paper: #ffffff; --ink: #1d1b2e; --muted: #5f5b78; --line: #dcd8f3;
  --navy: #0a0a48; --accent: #5640aa; --accent-ink: #ffffff; --soft: #eeebff; --ok: #3f6f1c;
  --display: "Montserrat", "Segoe UI", system-ui, sans-serif; --body: "Lora", Georgia, serif;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #12111f; --paper: #1b1a2c; --ink: #ecebf7; --muted: #a9a5c6; --line: #33304d;
  --navy: #d9d4ff; --accent: #a594f0; --accent-ink: #15132a; --soft: #262344; --ok: #9fd27a; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #12111f; --paper: #1b1a2c; --ink: #ecebf7; --muted: #a9a5c6; --line: #33304d;
  --navy: #d9d4ff; --accent: #a594f0; --accent-ink: #15132a; --soft: #262344; --ok: #9fd27a; color-scheme: dark }}
body {{ background: var(--bg); color: var(--ink); font-family: var(--display); }}
.wrap {{ max-width: 820px; margin: 0 auto; padding-block: 28px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }}
header h1 {{ font-size: 1.7rem; font-weight: 800; color: var(--navy); margin: 0 0 6px; text-wrap: balance; }}
header p {{ color: var(--muted); margin: 0; line-height: 1.5; }}
ol.steps {{ margin: 14px 0 0; padding-left: 1.2em; color: var(--muted); line-height: 1.6; font-size: .92rem; }}
.tabs {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 6px; margin: 22px 0 18px; }}
.tab {{ display: flex; flex-direction: column; gap: 2px; padding: 10px; border: 1px solid var(--line); border-radius: 8px;
  background: var(--paper); color: var(--ink); text-decoration: none; min-width: 0; }}
.tab b {{ font-size: 1.1rem; color: var(--accent); }}
.tab span {{ font-size: .72rem; color: var(--muted); overflow-wrap: anywhere; line-height: 1.3; }}
.tab[aria-current="true"] {{ background: var(--accent); border-color: var(--accent); }}
.tab[aria-current="true"] b, .tab[aria-current="true"] span {{ color: var(--accent-ink); }}
.bar {{ display: flex; gap: 14px; align-items: flex-end; justify-content: space-between; flex-wrap: wrap; }}
.bar > div {{ min-width: 0; flex: 1 1 320px; }}
.eyebrow {{ text-transform: uppercase; letter-spacing: .08em; font-size: .72rem; color: var(--accent); margin: 0 0 4px; font-weight: 700; }}
.bar h2 {{ margin: 0; font-size: 1.25rem; color: var(--navy); text-wrap: balance; }}
button {{ font-family: var(--display); cursor: pointer; }}
.big {{ background: var(--accent); color: var(--accent-ink); border: 0; border-radius: 8px; padding: 13px 20px; font-weight: 700; font-size: 1rem; }}
.mini {{ background: var(--soft); color: var(--accent); border: 0; border-radius: 6px; padding: 4px 9px; font-size: .74rem; font-weight: 700; flex: none; }}
button:focus-visible, .tab:focus-visible {{ outline: 3px solid var(--accent); outline-offset: 2px; }}
.status {{ min-height: 1.3em; margin: 8px 0; color: var(--ok); font-weight: 700; font-size: .9rem; }}
.seo {{ background: var(--paper); border: 1px solid var(--line); border-radius: 8px; padding: 10px 14px; margin-bottom: 16px; }}
.seo summary {{ font-weight: 700; cursor: pointer; color: var(--navy); }}
.seo dl {{ margin: 10px 0 0; display: grid; gap: 8px; }}
.row {{ display: grid; grid-template-columns: 130px minmax(0, 1fr); gap: 10px; font-size: .86rem; }}
.row dt {{ color: var(--muted); font-weight: 700; }}
.row dd {{ margin: 0; display: flex; gap: 8px; align-items: flex-start; justify-content: space-between; }}
.row dd span {{ min-width: 0; overflow-wrap: anywhere; line-height: 1.45; }}
.hint {{ font-size: .8rem; color: var(--muted); margin: 10px 0 2px; }}
.post {{ background: var(--paper); border: 1px solid var(--line); border-radius: 8px; padding: 26px 28px;
  font-family: var(--body); line-height: 1.7; font-size: 1.02rem; }}
.post h2 {{ font-family: var(--display); color: var(--accent); font-size: 1.2rem; margin: 1.6em 0 .4em; text-wrap: balance; }}
.post h3 {{ font-family: var(--display); font-size: 1rem; margin: 1.3em 0 .3em; }}
.post p:first-child {{ margin-top: 0; }}
.post a {{ color: var(--accent); }}
.post blockquote {{ margin: 1em 0; padding: 8px 16px; border-left: 3px solid var(--ok); background: var(--soft); }}
.post hr {{ border: 0; border-top: 1px solid var(--line); margin: 2em 0 1em; }}
@media (max-width: 560px) {{
  .tabs {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
  .row {{ grid-template-columns: minmax(0, 1fr); gap: 2px; }}
  .post {{ padding: 18px 16px; }}
  .big {{ width: 100%; }}
}}
</style>
<div class="wrap">
<header>
  <h1>Hipnoz Blog Yazıları</h1>
  <p>Uzm. Dr. Hande Çelik Mehmetoğlu · Bursa · WordPress'e hazır 5 yazı</p>
  <ol class="steps">
    <li>WordPress'te Yazılar → Yeni Ekle'yi açın, "Başlık" alanını kopyalayıp başlığa yapıştırın.</li>
    <li>"Yazıyı kopyala"ya basın ve yazının gövdesine yapıştırın. Başlıklar, listeler ve bağlantılar bloklara dönüşür.</li>
    <li>SEO başlığı, meta açıklama ve kalıcı bağlantıyı Rank Math ya da Yoast kutusuna yapıştırın.</li>
  </ol>
</header>
<nav class="tabs" aria-label="Yazılar">{"".join(tabs)}</nav>
{"".join(panels)}
</div>
<script>
const panels = [...document.querySelectorAll('[data-panel]')], tabs = [...document.querySelectorAll('[data-tab]')];
function show() {{
  const m = location.hash.match(/^#yazi-(\\d)$/); const n = m ? m[1] : '1';
  panels.forEach(p => p.hidden = p.dataset.panel !== n);
  tabs.forEach(t => t.setAttribute('aria-current', t.dataset.tab === n ? 'true' : 'false'));
}}
addEventListener('hashchange', show); show();
function say(msg) {{ const p = panels.find(p => !p.hidden); const s = p && p.querySelector('.status'); if (s) {{ s.textContent = msg; clearTimeout(say.t); say.t = setTimeout(() => s.textContent = '', 4000); }} }}
function selectEl(el) {{ const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r); }}
function fallback(el, okMsg) {{
  selectEl(el);
  let ok = false; try {{ ok = document.execCommand('copy'); }} catch (e) {{}}
  if (ok) {{ getSelection().removeAllRanges(); say(okMsg); }} else say('Metin seçildi. Kopyalamak için Ctrl+C (telefonda Kopyala) kullanın.');
}}
document.addEventListener('click', e => {{
  const rich = e.target.closest('[data-rich]'), plain = e.target.closest('[data-copy]');
  if (rich) {{
    const el = document.getElementById(rich.dataset.rich), msg = 'Yazı kopyalandı. WordPress\\'te gövdeye yapıştırın.';
    try {{
      navigator.clipboard.write([new ClipboardItem({{
        'text/html': new Blob([el.innerHTML], {{ type: 'text/html' }}),
        'text/plain': new Blob([el.innerText], {{ type: 'text/plain' }}) }})]).then(() => say(msg), () => fallback(el, msg));
    }} catch (err) {{ fallback(el, msg); }}
  }} else if (plain) {{
    const el = document.getElementById(plain.dataset.copy), msg = 'Kopyalandı.';
    try {{ navigator.clipboard.writeText(el.textContent).then(() => say(msg), () => fallback(el, msg)); }}
    catch (err) {{ fallback(el, msg); }}
  }}
}});
</script>
'''
(ROOT / "kopyala.html").write_text(page)
print(len(page))
