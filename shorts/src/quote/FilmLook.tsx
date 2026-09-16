import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {noise1} from './noise';

/**
 * Goruntuyu "cekilmis" hissettiren katman.
 *
 * Duz render ile gercek goruntu arasindaki fark cogunlukla icerik degil,
 * bu kusurlardir: negatifin kapida oynamasi, isigin tasmasi, siyahlarin
 * tam siyah olmamasi, renk ayrimi. Hicbiri "efekt" gibi gorunmemeli --
 * fark edilirse fazla kacmis demektir.
 */
export const FilmLook: React.FC<{children: React.ReactNode; intensity?: number}> = ({
  children,
  intensity = 1,
}) => {
  const frame = useCurrentFrame();

  // Gate weave: film negatifi projektorde mikroskobik oynar. Tek basina
  // "kamerayla cekilmis" hissini veren en ucuz ve en etkili detay.
  const wx = (noise1(frame * 0.6) - 0.5) * 2.4 * intensity;
  const wy = (noise1(frame * 0.6 + 41) - 0.5) * 2.4 * intensity;
  const wr = (noise1(frame * 0.35 + 91) - 0.5) * 0.14 * intensity;

  // Pozlama titremesi: analog kaynakta isik hic sabit degildir.
  const exposure = 1 + (noise1(frame * 0.8 + 17) - 0.5) * 0.035 * intensity;

  return (
    <AbsoluteFill style={{overflow: 'hidden', backgroundColor: '#000'}}>
      <AbsoluteFill
        style={{
          transform: `translate(${wx}px, ${wy}px) rotate(${wr}deg) scale(1.012)`,
          filter: `brightness(${exposure}) contrast(1.07) saturate(1.06)`,
        }}
      >
        {children}
      </AbsoluteFill>

      {/* Golgelere hafif soguk kayma -- sicak isik / soguk golge film grade'i */}
      <AbsoluteFill
        style={{
          backgroundImage:
            'linear-gradient(180deg, rgba(38,52,74,0.20) 0%, rgba(30,42,62,0.08) 45%, rgba(14,18,28,0.16) 100%)',
          mixBlendMode: 'soft-light',
          pointerEvents: 'none',
        }}
      />

      {/* Kaldirilmis siyahlar: filmde siyah asla #000 degildir, hafif sisli acilir */}
      <AbsoluteFill
        style={{
          backgroundColor: 'rgba(58,44,52,0.055)',
          pointerEvents: 'none',
        }}
      />

      {/* Kenar karartmasi -- merkezden hafif kacik, mekanik durmasin */}
      <AbsoluteFill
        style={{
          backgroundImage:
            'radial-gradient(78% 62% at 48% 43%, transparent 38%, rgba(8,5,6,0.40) 78%, rgba(4,2,3,0.74) 100%)',
          pointerEvents: 'none',
        }}
      />
    </AbsoluteFill>
  );
};
