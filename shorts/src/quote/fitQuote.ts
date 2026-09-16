import {measureText} from '@remotion/layout-utils';

/** Bir "grup" = elle yazilmis tek satir. Icinde sarilmis gorsel satirlar olabilir. */
export type QuoteGroup = string[];

export type FittedQuote = {
  groups: QuoteGroup[];
  fontSize: number;
  /** En kucuk puntoda bile sigmiyorsa true - toplu render'da uyari basilir. */
  overflow: boolean;
};

type Args = {
  text: string;
  maxWidth: number;
  maxHeight: number;
  fontFamily: string;
  fontWeight: number;
  lineHeight: number;
  /** Buyukten kucuge denenecek punto listesi. */
  sizes: number[];
};

/** Elle yazilan satir sonlari korunur; sadece sigmayanlar kelime bazinda sarilir. */
const wrapAt = (
  text: string,
  fontSize: number,
  maxWidth: number,
  fontFamily: string,
  fontWeight: number,
): QuoteGroup[] | null => {
  const measure = (t: string) =>
    measureText({text: t, fontFamily, fontSize, fontWeight}).width;

  const groups: QuoteGroup[] = [];
  for (const paragraph of splitLines(text)) {
    const words = paragraph.split(/\s+/).filter(Boolean);
    if (words.length === 0) continue;

    const visual: string[] = [];
    let current = '';
    for (const word of words) {
      const candidate = current ? `${current} ${word}` : word;
      if (measure(candidate) <= maxWidth) {
        current = candidate;
        continue;
      }
      if (current) visual.push(current);
      // Tek kelime bile sigmiyorsa bu punto gecersiz; bir kucugunu dene.
      if (measure(word) > maxWidth) return null;
      current = word;
    }
    visual.push(current);
    groups.push(visual);
  }
  return groups;
};

/** Sozun elle yazilmis satirlari. Bos satirlar atilir. Node tarafinda da guvenli. */
export const splitLines = (text: string): string[] =>
  text
    .split('\n')
    .map((l) => l.trim())
    .filter((l) => l.length > 0);

const countVisualLines = (groups: QuoteGroup[]) =>
  groups.reduce((acc, g) => acc + g.length, 0);

/**
 * Metni guvenli kutuya sigdirir. Toplu uretimde soz uzunluklari cok degistigi
 * icin sart: sabit punto kullanilirsa uzun sozler ekrandan tasar ve bunu
 * 50 videoyu yukleyene kadar fark etmezsin.
 */
export const fitQuote = ({
  text,
  maxWidth,
  maxHeight,
  fontFamily,
  fontWeight,
  lineHeight,
  sizes,
}: Args): FittedQuote => {
  for (const fontSize of sizes) {
    const groups = wrapAt(text, fontSize, maxWidth, fontFamily, fontWeight);
    if (groups === null) continue;
    if (countVisualLines(groups) * fontSize * lineHeight <= maxHeight) {
      return {groups, fontSize, overflow: false};
    }
  }

  const smallest = sizes[sizes.length - 1];
  const groups =
    wrapAt(text, smallest, maxWidth, fontFamily, fontWeight) ??
    splitLines(text).map((l) => [l]);
  return {groups, fontSize: smallest, overflow: true};
};
