import React from 'react';
import {
  AbsoluteFill,
  Img,
  OffthreadVideo,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {palette} from '../theme';

const isVideo = (src: string) => /\.(mp4|mov|webm|mkv)$/i.test(src);

/**
 * Yavas Ken Burns zoom. Sabit goruntu Shorts'ta "durgun" hissettirir ve
 * kaydirilma oranini artirir; hafif surekli hareket izleyiciyi tutar.
 */
const useKenBurns = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  return interpolate(frame, [0, durationInFrames], [1.06, 1.16], {
    extrapolateRight: 'clamp',
  });
};

const GradientFallback: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const drift = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const x1 = 28 + drift * 10;
  const y1 = 24 + drift * 8;
  const x2 = 74 - drift * 8;
  const y2 = 76 - drift * 6;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: palette.base,
        backgroundImage: [
          `radial-gradient(62% 44% at ${x1}% ${y1}%, rgba(214, 138, 66, 0.62), transparent 68%)`,
          `radial-gradient(58% 42% at ${x2}% ${y2}%, rgba(142, 52, 36, 0.58), transparent 70%)`,
          `radial-gradient(95% 72% at 50% 50%, rgba(40, 22, 14, 0.10), rgba(8, 5, 4, 0.72))`,
        ].join(', '),
      }}
    />
  );
};

export const Background: React.FC<{src?: string}> = ({src}) => {
  const scale = useKenBurns();

  return (
    <AbsoluteFill style={{overflow: 'hidden', backgroundColor: palette.base}}>
      <AbsoluteFill style={{transform: `scale(${scale})`}}>
        {!src ? (
          <GradientFallback />
        ) : isVideo(src) ? (
          <OffthreadVideo
            src={src}
            muted
            style={{width: '100%', height: '100%', objectFit: 'cover'}}
          />
        ) : (
          <Img src={src} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        )}
      </AbsoluteFill>

      {/*
        Okunabilirlik perdesi. B-roll varken agir olmali (goruntu metinle yarisir),
        gradyan fallback'te hafif - yoksa arka plan tamamen olu siyaha doner.
      */}
      <AbsoluteFill
        style={{
          backgroundImage: src
            ? 'linear-gradient(180deg, rgba(6,4,3,0.72) 0%, rgba(6,4,3,0.34) 32%, rgba(6,4,3,0.52) 68%, rgba(6,4,3,0.88) 100%)'
            : 'linear-gradient(180deg, rgba(6,4,3,0.42) 0%, rgba(6,4,3,0.10) 34%, rgba(6,4,3,0.22) 66%, rgba(6,4,3,0.62) 100%)',
        }}
      />
      {/* Vinyet */}
      <AbsoluteFill
        style={{
          backgroundImage:
            'radial-gradient(72% 58% at 50% 45%, transparent 42%, rgba(6,4,3,0.62) 100%)',
        }}
      />
    </AbsoluteFill>
  );
};
