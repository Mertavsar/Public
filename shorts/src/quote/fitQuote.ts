import {measureText} from '@remotion/layout-utils';

export type ParsedLine = {text: string; emphasis: boolean};

/** Vurgulu satir tam puntoda, digerleri kucuk -- olcek kontrasti hiyerarsi kurar. */
export const EMPHASIS_SCALE = 1;
export const NORMAL_SCALE = 0.82;

/**
 * Elle yazilan satirlari ayirir. Basinda ">" olan satir vurguludur.
 * Vurgu satir bazinda: kelime ici isaretleme kullanilsa satir sarmasi
 * isaretin ortasindan kirilabilirdi.
 * Node tarafinda da calisir (olcum gerektirmez).
 */
export const parseQuote = (text: string): ParsedLine[] =>
  text
    .split('\n')
    .map((l) => l.trim())
    .filter((l) => l.length > 0)
    .map((l) =>
      l.startsWith('>') ? {text: l.slice(1).trim(), emphasis: true} : {text: l, emphasis: false},
    );

/** Bir grup = elle yazilmis tek satir; icinde sarilmis gorsel satirlar olabilir. */
export type QuoteGroup = {
  visual: string[];
  emphasis: boolean;
  fontSize: number;
};

export type FittedQuote = {
  groups: QuoteGroup[];
  overflow: boolean;
};

type Args = {
  text: string;
  maxWidth: number;
  maxHeight: number;
  fontFamily: string;
  fontWeight: number;
  lineHeight: number;
  /** Vurgulu satirin puntosu; digerleri bunun NORMAL_SCALE kati. Buyukten kucuge. */
  sizes: number[];
};

const wrapAt = (
  lines: ParsedLine[],
  baseSize: number,
  maxWidth: number,
  fontFamily: string,
  fontWeight: number,
): QuoteGroup[] | null => {
  const groups: QuoteGroup[] = [];

  for (const line of lines) {
    const fontSize = Math.round(baseSize * (line.emphasis ? EMPHASIS_SCALE : NORMAL_SCALE));
    const measure = (t: string) => measureText({text: t, fontFamily, fontSize, fontWeight}).width;

    const words = line.text.split(/\s+/).filter(Boolean);
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
    groups.push({visual, emphasis: line.emphasis, fontSize});
  }

  return groups;
};

const totalHeight = (groups: QuoteGroup[], lineHeight: number) =>
  groups.reduce((acc, g) => acc + g.visual.length * g.fontSize * lineHeight, 0);

/**
 * Metni guvenli kutuya sigdirir. Toplu uretimde soz uzunluklari cok degistigi
 * icin sart: sabit punto ile uzun sozler tasar ve bunu ancak yukledikten
 * sonra fark edersin.
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
  const lines = parseQuote(text);

  for (const baseSize of sizes) {
    const groups = wrapAt(lines, baseSize, maxWidth, fontFamily, fontWeight);
    if (groups === null) continue;
    if (totalHeight(groups, lineHeight) <= maxHeight) {
      return {groups, overflow: false};
    }
  }

  const smallest = sizes[sizes.length - 1];
  const groups =
    wrapAt(lines, smallest, maxWidth, fontFamily, fontWeight) ??
    lines.map((l) => ({
      visual: [l.text],
      emphasis: l.emphasis,
      fontSize: Math.round(smallest * (l.emphasis ? EMPHASIS_SCALE : NORMAL_SCALE)),
    }));
  return {groups, overflow: true};
};
