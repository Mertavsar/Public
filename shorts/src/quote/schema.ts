import {z} from 'zod';
import {zColor} from '@remotion/zod-types';
import {FPS, TIMING} from '../theme';
import {splitLines} from './fitQuote';

export const quoteSchema = z.object({
  /** Her satir ayri bir aciliste ekrana gelir. Ilk satir hook'tur. */
  quote: z.string(),
  author: z.string().optional(),
  /** Yorum yemi. Bos birakilirsa gosterilmez. */
  cta: z.string().optional(),
  /** Kanal etiketi, ornegin @30adogru */
  handle: z.string().optional(),
  /** public/ altindaki video veya gorsel. Verilirse scene yok sayilir. */
  background: z.string().optional(),
  /** Hazir arka plan sahnesi. background bos oldugunda kullanilir. */
  scene: z.enum(['gradient', 'bozkir']).optional(),
  accent: zColor(),
  /** Son satir ekranda kaldiktan sonraki bekleme. */
  holdSeconds: z.number().min(0.5).max(8),
  showSafeArea: z.boolean(),
});

export type QuoteProps = z.infer<typeof quoteSchema>;

/**
 * Sure, sozun satir sayisindan hesaplanir - sabit sure verirsen kisa sozlerde
 * olu bekleme, uzun sozlerde kesilme olur.
 * Olcum gerektirmedigi icin Node tarafinda da calisir (calculateMetadata).
 */
export const quoteDurationInFrames = (props: QuoteProps): number => {
  const lines = Math.max(1, splitLines(props.quote).length);
  return (
    TIMING.firstLineAt +
    lines * TIMING.lineStagger +
    TIMING.authorDelay +
    Math.round(props.holdSeconds * FPS) +
    TIMING.outro
  );
};
