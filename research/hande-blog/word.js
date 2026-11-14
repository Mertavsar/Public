// posts.json (build.py parse çıktısı) → WordPress'e kopyala-yapıştır için Word dosyası
const fs = require("fs");
const d = require("docx");
const { Document, Packer, Paragraph, TextRun, ExternalHyperlink, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, LevelFormat, AlignmentType, PageBreak } = d;

const [src, out] = process.argv.slice(2);
const { posts, author, disclaimer, site } = JSON.parse(fs.readFileSync(src, "utf8"));
const NAVY = "0A0A48", PURPLE = "5640AA", LILAC = "F2F0FF", GREEN = "5B8A2F";

function runs(text, extra = {}) {
  const out = [];
  const re = /\*\*(.+?)\*\*|\[(.+?)\]\((.+?)\)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...extra }));
    if (m[1]) out.push(new TextRun({ text: m[1], bold: true, ...extra }));
    else out.push(new ExternalHyperlink({ link: site + m[3], children: [new TextRun({ text: m[2], style: "Hyperlink", ...extra })] }));
    last = re.lastIndex;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...extra }));
  return out;
}

const W = 9638, K = 2600;
const cell = (children, w, fill) => new TableCell({ width: { size: w, type: WidthType.DXA }, children,
  shading: fill ? { type: ShadingType.CLEAR, fill, color: "auto" } : undefined,
  margins: { top: 60, bottom: 60, left: 100, right: 100 } });
const small = (t, bold) => new Paragraph({ children: [new TextRun({ text: t, size: 18, bold })] });

function seoTable(m) {
  const rows = [["Başlık alanına", m.title], ["SEO başlık", m.seo_title], ["Meta açıklama", m.meta],
    ["Kalıcı bağlantı", m.slug], ["Odak anahtar kelime", m.focus], ["İkincil kelimeler", m.secondary],
    ["Özet", m.excerpt], ["Öne çıkan görsel", m.image], ["Görsel alt metni", m.alt]];
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [K, W - K],
    rows: rows.map(([k, v]) => new TableRow({ children: [cell([small(k, true)], K, LILAC), cell([small(v)], W - K)] })) });
}

const marker = (t, color) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 240, after: 240 },
  shading: { type: ShadingType.CLEAR, fill: color, color: "auto" },
  children: [new TextRun({ text: t, bold: true, color: "FFFFFF", size: 18 })] });

let listId = 0;
const children = [
  new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("Hipnoz Blog Yazıları")] }),
  new Paragraph({ children: [new TextRun({ text: "Uzm. Dr. Hande Çelik Mehmetoğlu · Bursa · WordPress'e kopyala-yapıştır formatı", color: "666666" })] }),
  new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Nasıl kullanılır?")] }),
  ...[
    "WordPress'te Yazılar → Yeni Ekle'yi açın.",
    "Tablodaki \"Başlık alanına\" satırını yazının başlık alanına yazın.",
    "Yeşil \"KOPYALAMA BAŞLANGICI\" ile mor \"KOPYALAMA SONU\" çubukları arasındaki her şeyi seçip kopyalayın (Ctrl+C), WordPress'te yazının gövdesine yapıştırın (Ctrl+V). Başlıklar, listeler, kalın yazılar ve bağlantılar kendiliğinden bloklara dönüşür.",
    "Rank Math veya Yoast kutusuna SEO başlığını, meta açıklamayı, kalıcı bağlantıyı ve odak kelimeyi tablodan girin.",
    "Öne çıkan görseli ekleyin, alt metni tablodan kopyalayın. Kategori: Hipnoz.",
    "Beş yazıyı da önce taslak kaydedin, sonra yayınlayın; yazılar birbirine bağlantı veriyor.",
  ].map(t => new Paragraph({ numbering: { reference: "num", level: 0, instance: 999 }, children: [new TextRun(t)] })),
  new Paragraph({ spacing: { before: 200 }, children: [new TextRun({ text: "Not: ", bold: true }), new TextRun("\"Sık sorulan sorular\" bölümünün Google'da zengin sonuç olarak görünmesi için Rank Math/Yoast SSS bloğu kullanılabilir. Yayından önce Hande Hoca'nın metinleri okuyup onaylaması gerekir.")] }),
];

posts.forEach((p, i) => {
  const m = p.meta;
  children.push(new Paragraph({ children: [new PageBreak()] }));
  children.push(new Paragraph({ children: [new TextRun({ text: `YAZI ${i + 1} / ${posts.length}`, bold: true, color: PURPLE, size: 18 })] }));
  children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(m.title)] }));
  children.push(seoTable(m));
  children.push(marker("▼  KOPYALAMA BAŞLANGICI  ▼", GREEN));
  let curList = null;
  for (const [kind, v] of p.blocks) {
    if (kind === "p") children.push(new Paragraph({ children: runs(v) }));
    else if (kind === "h2") children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs(v) }));
    else if (kind === "h3") children.push(new Paragraph({ heading: HeadingLevel.HEADING_3, children: runs(v) }));
    else if (kind === "quote") children.push(new Paragraph({ style: "Quote", children: runs(v) }));
    else if (kind === "faq") {
      children.push(new Paragraph({ heading: HeadingLevel.HEADING_3, children: runs(v[0]) }));
      children.push(new Paragraph({ children: runs(v[1]) }));
    } else {
      const inst = ++listId;
      for (const it of v) children.push(new Paragraph({
        numbering: { reference: kind === "ol" ? "num" : "bul", level: 0, instance: inst }, children: runs(it) }));
    }
  }
  children.push(new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC", space: 4 } }, children: [] }));
  children.push(new Paragraph({ children: [new TextRun({ text: "Yazar: ", bold: true }), new TextRun(author)] }));
  children.push(new Paragraph({ children: [new TextRun({ text: disclaimer, italics: true })] }));
  children.push(marker("▲  KOPYALAMA SONU  ▲", PURPLE));
});

const doc = new Document({
  creator: "Ajans", title: "Hipnoz Blog Yazıları",
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 }, paragraph: { spacing: { after: 140, line: 300 } } } },
    paragraphStyles: [
      { id: "Title", name: "Title", run: { font: "Calibri", size: 48, bold: true, color: NAVY } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 34, bold: true, color: NAVY }, paragraph: { spacing: { before: 120, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: PURPLE }, paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: "1D1B2E" }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 } },
      { id: "Quote", name: "Quote", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { italics: true }, paragraph: { indent: { left: 400 }, border: { left: { style: BorderStyle.SINGLE, size: 18, color: GREEN, space: 8 } } } },
    ],
  },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  ] },
  sections: [{ properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } }, children }],
});
Packer.toBuffer(doc).then(b => fs.writeFileSync(out, b));
