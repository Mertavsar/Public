import React, {useEffect, useMemo} from 'react';
import {AbsoluteFill, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {CONTENT, FONT_BODY, FONT_UI, HEIGHT, SAFE, TIMING, WIDTH, palette} from '../theme';
import {useFontsReady} from '../useFontsReady';
import {Background} from './Background';
import {FilmLook} from './FilmLook';
import {Grain} from './Grain';
import {SafeAreaGuide} from './SafeAreaGuide';
import {fitQuote} from './fitQuote';
import type {QuoteProps} from './schema';

const QUOTE_WEIGHT = 500;
const LINE_HEIGHT = 1.3;
/** Vurgulu satirin puntosu. Buyukten kucuge denenir; ilk sigan secilir. */
const SIZE_STEPS = [92, 84, 76, 70, 64, 58, 52, 46, 41, 36];
/** Metin kutunun kenarina yapismasin; nefes payi. */
const INNER_PAD = 0.94;
/** Yazar satiri ve panel dolgusu icin ayrilan dikey pay. */
const FOOTER_RESERVE = 150;
/** Panel acikken metnin cevresindeki dolgu. */
const PANEL_PAD_X = 46;
const PANEL_PAD_Y = 40;

const reveal = (frame: number, startsAt: number, fps: number) =>
  spring({
    frame: frame - startsAt,
    fps,
    durationInFrames: TIMING.lineReveal,
    config: {damping: 200},
  });

/**
 * Maskeli aciliş: satir gorunmez bir cizginin ardindan yukari kayarak girer.
 * Duz opacity gecisine gore cok daha "tasarlanmis" hissettirir -- hareketin
 * bir yonu ve agirligi olur.
 */
const MaskedLine: React.FC<{
  children: React.ReactNode;
  progress: number;
  fontSize: number;
  style?: React.CSSProperties;
}> = ({children, progress, fontSize, style}) => {
  // Alt tasma payi: overflow hidden olmasa "g, y, ş" kuyruklari kesilirdi.
  const bleed = Math.round(fontSize * 0.22);
  return (
    <div
      style={{
        overflow: 'hidden',
        paddingBottom: bleed,
        marginBottom: -bleed,
      }}
    >
      <div
        style={{
          transform: `translateY(${(1 - progress) * 104}%)`,
          opacity: Math.min(1, progress * 1.4),
          ...style,
        }}
      >
        {children}
      </div>
    </div>
  );
};

export const QuoteShort: React.FC<QuoteProps> = ({
  quote,
  author,
  cta,
  handle,
  background,
  scene,
  accent,
  panel,
  showSafeArea,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fontsReady = useFontsReady();

  const fitted = useMemo(() => {
    if (!fontsReady) return null;
    return fitQuote({
      text: quote,
      maxWidth: CONTENT.width * INNER_PAD - (panel ? PANEL_PAD_X * 2 : 0),
      maxHeight: CONTENT.height - FOOTER_RESERVE - (panel ? PANEL_PAD_Y * 2 : 0),
      fontFamily: FONT_BODY,
      fontWeight: QUOTE_WEIGHT,
      lineHeight: LINE_HEIGHT,
      sizes: SIZE_STEPS,
    });
  }, [fontsReady, quote, panel]);

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

  const authorP = reveal(frame, authorAt, fps);
  const ctaP = reveal(frame, ctaAt, fps);
  const handleP = reveal(frame, 4, fps);

  return (
    <FilmLook>
      <AbsoluteFill style={{backgroundColor: palette.base}}>
        <Background src={bgSrc} scene={scene} />
        <Grain />

        {/* Kanal etiketi: kareye gore ortali, guvenli alanin ustunde */}
        {fitted && handle ? (
          <div
            lang="tr"
            style={{
              position: 'absolute',
              top: SAFE.top,
              left: 0,
              width: WIDTH,
              textAlign: 'center',
              fontFamily: FONT_UI,
              fontSize: 24,
              letterSpacing: 4,
              textTransform: 'uppercase',
              color: palette.inkDim,
              opacity: handleP * 0.75,
            }}
          >
            {handle}
          </div>
        ) : null}

        {/* Fontlar hazir olana kadar metin cizilmez; olculer yanlis cikardi. */}
        {fitted ? (
          <div
            // Kutu kareye gore simetrik ve merkezi (540, 960). SAFE dogrudan
            // kullanilsaydi sagdaki genis buton payi metni sola kaydirirdi.
            style={{
              position: 'absolute',
              top: CONTENT.top,
              left: CONTENT.left,
              width: CONTENT.width,
              height: CONTENT.height,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                ...(panel
                  ? {
                      padding: `${PANEL_PAD_Y}px ${PANEL_PAD_X}px`,
                      borderRadius: 34,
                      backgroundColor: 'rgba(10,7,6,0.62)',
                      backdropFilter: 'blur(14px)',
                      boxShadow: '0 24px 70px rgba(0,0,0,0.42)',
                    }
                  : {}),
              }}
            >
              {!panel ? (
                <div
                  style={{
                    width: 56,
                    height: 2,
                    borderRadius: 2,
                    backgroundColor: accent,
                    opacity: reveal(frame, 2, fps) * 0.7,
                    marginBottom: 52,
                  }}
                />
              ) : null}

              {groups.map((group, i) => {
                const groupStart = TIMING.firstLineAt + i * TIMING.lineStagger;
                return (
                  // eslint-disable-next-line react/no-array-index-key
                  <div key={i} style={{marginBottom: group.emphasis ? 6 : 2}}>
                    {group.visual.map((line, j) => (
                      <MaskedLine
                        // eslint-disable-next-line react/no-array-index-key
                        key={j}
                        fontSize={group.fontSize}
                        progress={reveal(frame, groupStart + j * TIMING.intraGroupStagger, fps)}
                        style={{
                          fontFamily: FONT_BODY,
                          fontWeight: QUOTE_WEIGHT,
                          fontStyle: group.emphasis ? 'italic' : 'normal',
                          fontSize: group.fontSize,
                          lineHeight: LINE_HEIGHT,
                          color: group.emphasis ? accent : palette.ink,
                          textAlign: 'center',
                          // Sicak halation: isigin harflerden tasmasi. Alttaki
                          // koyu golge okunabilirlik, ustteki sicak parilti doku.
                          textShadow: group.emphasis
                            ? `0 0 42px ${accent}55, 0 2px 22px rgba(0,0,0,0.72)`
                            : '0 0 38px rgba(255,214,160,0.20), 0 2px 22px rgba(0,0,0,0.76)',
                          whiteSpace: 'pre',
                        }}
                      >
                        {line}
                      </MaskedLine>
                    ))}
                  </div>
                );
              })}

              {author ? (
                <div
                  style={{
                    marginTop: 42,
                    fontFamily: FONT_UI,
                    fontSize: 28,
                    letterSpacing: 2,
                    color: accent,
                    opacity: authorP * 0.9,
                    transform: `translateY(${(1 - authorP) * 14}px)`,
                  }}
                >
                  {author}
                </div>
              ) : null}
            </div>
          </div>
        ) : null}

        {/* Yorum yemi: kareye gore ortali, alt guvenli sinirin hemen ustunde */}
        {fitted && cta ? (
          <div
            style={{
              position: 'absolute',
              top: HEIGHT - SAFE.bottom - 58,
              left: 0,
              width: WIDTH,
              textAlign: 'center',
              fontFamily: FONT_UI,
              fontSize: 31,
              fontWeight: 600,
              color: palette.ink,
              textShadow: '0 2px 20px rgba(0,0,0,0.85)',
              opacity: ctaP * 0.94,
              transform: `translateY(${(1 - ctaP) * 16}px)`,
            }}
          >
            {cta}
          </div>
        ) : null}

        {showSafeArea ? <SafeAreaGuide /> : null}
      </AbsoluteFill>
    </FilmLook>
  );
};
