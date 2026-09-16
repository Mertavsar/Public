// data/quotes.json icindeki her sozu ayri bir mp4 olarak render eder.
// Bundle bir kez yapilir, sonra her soz icin yeniden kullanilir.
import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';
import fs from 'node:fs/promises';
import {findLocalChrome} from './find-chrome.mjs';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '..');
const OUT_DIR = path.join(ROOT, 'out');
const COMPOSITION_ID = 'QuoteShort';

/** JSON'daki null degerler zod'un optional alanlarini bozar; temizle. */
const stripNulls = (obj) =>
  Object.fromEntries(Object.entries(obj).filter(([, v]) => v !== null && v !== undefined));

const main = async () => {
  // Node API remotion.config.ts'i okumaz; tarayici yolu burada verilir.
  const browserExecutable = findLocalChrome();
  const raw = await fs.readFile(path.join(ROOT, 'data/quotes.json'), 'utf8');
  const {defaults = {}, quotes = []} = JSON.parse(raw);

  const only = process.argv.slice(2);
  const selected = only.length ? quotes.filter((q) => only.includes(q.id)) : quotes;
  if (selected.length === 0) {
    console.error('Render edilecek soz bulunamadi.');
    process.exit(1);
  }

  await fs.mkdir(OUT_DIR, {recursive: true});

  console.log('Bundle hazirlaniyor...');
  const serveUrl = await bundle({
    entryPoint: path.join(ROOT, 'src/index.ts'),
    onProgress: (p) => process.stdout.write(`\rBundle %${p}   `),
  });
  console.log('\nBundle hazir.\n');

  const overflowed = [];

  for (const [i, q] of selected.entries()) {
    const {id, ...rest} = q;
    const inputProps = stripNulls({...defaults, ...rest});
    const outputLocation = path.join(OUT_DIR, `${id}.mp4`);

    const composition = await selectComposition({
      serveUrl,
      id: COMPOSITION_ID,
      inputProps,
      browserExecutable,
    });

    let lastPct = -1;
    await renderMedia({
      composition,
      serveUrl,
      browserExecutable,
      codec: 'h264',
      crf: 18,
      outputLocation,
      inputProps,
      onBrowserLog: (log) => {
        if (log.text.includes('[TASMA]')) {
          overflowed.push(id);
          console.log(`\n  ! ${log.text}`);
        }
      },
      onProgress: ({progress}) => {
        const pct = Math.round(progress * 100);
        if (pct !== lastPct) {
          lastPct = pct;
          process.stdout.write(`\r[${i + 1}/${selected.length}] ${id}  %${pct}   `);
        }
      },
    });
    const {size} = await fs.stat(outputLocation);
    console.log(`\r[${i + 1}/${selected.length}] ${id}  bitti  (${(size / 1024 / 1024).toFixed(2)} MB, ${(composition.durationInFrames / composition.fps).toFixed(1)} sn)`);
  }

  console.log(`\n${selected.length} video hazir: ${OUT_DIR}`);
  if (overflowed.length) {
    console.log(`UYARI - metni kisalt: ${[...new Set(overflowed)].join(', ')}`);
  }
};

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
