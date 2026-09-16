import React, {useEffect, useMemo} from 'react';
import {AbsoluteFill, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {FONT_BODY, FONT_UI, SAFE, SAFE_HEIGHT, SAFE_WIDTH, TIMING, palette} from '../theme';
import {useFontsReady} from '../useFontsReady';
import {Background} from './Background';
import {Grain} from './Grain';
import {SafeAreaGuide} from './SafeAreaGuide';
import {fitQuote} from './fitQuote';
import type {QuoteProps} from './schema';

const QUOTE_WEIGHT = 500;
const LINE_HEIGHT = 1.34;
/** Buyukten kucuge denenir; ilk sigan secilir. */
const SIZE_STEPS = [84, 76, 70, 64, 58, 52, 46, 41, 36];

/** Sozun altindaki yazar + yorum yemi icin ayrilan dikey pay. */
const FOOTER_RESERVE = 230;
/** Metin guvenli kutunun kenarina yapismasin; nefes payi. */
const INNER_PAD = 0.94;

type RevealArgs = {frame: number; startsAt: number; fps: number};

const reveal = ({frame, startsAt, fps}: RevealArgs) =>
  spring({
    frame: frame - startsAt,
    fps,
    durationInFrames: TIMING.lineReveal,
    config: {damping: 200},
  });

export const QuoteShort: React.FC<QuoteProps> = ({
  quote,
  author,
  cta,
  handle,
  background,
  accent,
  showSafeArea,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fontsReady = useFontsReady();

  const fitted = useMemo(() => {
    if (!fontsReady) return null;
    return fitQuote({
      text: quote,
      maxWidth: SAFE_WIDTH * INNER_PAD,
      maxHeight: SAFE_HEIGHT - FOOTER_RESERVE,
      fontFamily: FONT_BODY,
      fontWeight: QUOTE_WEIGHT,
      lineHeight: LINE_HEIGHT,
      sizes: SIZE_STEPS,
    });
  }, [fontsReady, quote]);

  // Tasma sessizce gecmesin: toplu render'da onBrowserLog ile yakalanir.
  useEffect(() => {
    if (fitted?.overflow) {
      // eslint-disable-next-line no-console
      console.warn(`[TASMA] Soz en kucuk puntoda bile guvenli alana sigmiyor: "${quote.slice(0, 48)}..."`);
    }
  }, [fitted, quote]);

  const bgSrc = background ? staticFile(background) : undefined;
  const groups = fitted?.groups ?? [];

  const authorAt =
    TIMING.firstLineAt + groups.length * TIMING.lineStagger + TIMING.authorDelay;
  const ctaAt = authorAt + 12;

  const authorP = reveal({frame, startsAt: authorAt, fps});
  const ctaP = reveal({frame, startsAt: ctaAt, fps});
  const handleP = reveal({frame, startsAt: 4, fps});

  return (
    <AbsoluteFill style={{backgroundColor: palette.base}}>
      <Background src={bgSrc} />
      <Grain />

      {/* Fontlar hazir olana kadar metin cizilmez; olculer yanlis cikardi. */}
      {fitted ? (
        <div
          // AbsoluteFill KULLANILMAZ: o bilesen width/height 100% dayatir,
          // top/left/right/bottom verince kutu daralmaz, tasar. Duz div ile
          // inset vererek gercek guvenli alani elde ediyoruz.
          style={{
            position: 'absolute',
            top: SAFE.top,
            left: SAFE.left,
            width: SAFE_WIDTH,
            height: SAFE_HEIGHT,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {handle ? (
            <div
              lang="tr"
              style={{
                position: 'absolute',
                top: 0,
                fontFamily: FONT_UI,
                fontSize: 26,
                letterSpacing: 3,
                textTransform: 'uppercase',
                color: palette.inkDim,
                opacity: handleP * 0.9,
              }}
            >
              {handle}
            </div>
          ) : null}

          <div
            style={{
              width: 64,
              height: 3,
              borderRadius: 2,
              backgroundColor: accent,
              opacity: reveal({frame, startsAt: 2, fps}) * 0.85,
              marginBottom: 48,
            }}
          />

          {groups.map((visualLines, i) => {
            const p = reveal({
              frame,
              startsAt: TIMING.firstLineAt + i * TIMING.lineStagger,
              fps,
            });
            return (
              <div
                // eslint-disable-next-line react/no-array-index-key
                key={i}
                style={{
                  opacity: p,
                  transform: `translateY(${(1 - p) * 30}px)`,
                  filter: `blur(${(1 - p) * 7}px)`,
                  willChange: 'transform, opacity, filter',
                }}
              >
                {visualLines.map((line, j) => (
                  <div
                    // eslint-disable-next-line react/no-array-index-key
                    key={j}
                    style={{
                      fontFamily: FONT_BODY,
                      fontWeight: QUOTE_WEIGHT,
                      fontSize: fitted.fontSize,
                      lineHeight: LINE_HEIGHT,
                      color: palette.ink,
                      textAlign: 'center',
                      textShadow: '0 2px 26px rgba(0,0,0,0.78), 0 1px 3px rgba(0,0,0,0.6)',
                      whiteSpace: 'pre',
                    }}
                  >
                    {line}
                  </div>
                ))}
              </div>
            );
          })}

          {author ? (
            <div
              style={{
                marginTop: 44,
                fontFamily: FONT_UI,
                fontSize: 30,
                letterSpacing: 2,
                color: accent,
                opacity: authorP * 0.95,
                transform: `translateY(${(1 - authorP) * 16}px)`,
              }}
            >
              {author}
            </div>
          ) : null}

          {cta ? (
            <div
              style={{
                position: 'absolute',
                bottom: 18,
                fontFamily: FONT_UI,
                fontSize: 32,
                fontWeight: 600,
                color: palette.ink,
                textAlign: 'center',
                textShadow: '0 2px 18px rgba(0,0,0,0.8)',
                opacity: ctaP,
                transform: `translateY(${(1 - ctaP) * 18}px)`,
              }}
            >
              {cta}
            </div>
          ) : null}
        </div>
      ) : null}

      {showSafeArea ? <SafeAreaGuide /> : null}
    </AbsoluteFill>
  );
};
