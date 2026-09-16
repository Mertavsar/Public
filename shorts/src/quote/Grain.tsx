import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';

const TILE = 240;

/**
 * Film graini. feTurbulence 1080x1920'de kare basina pahali oldugu icin
 * kucuk bir karo uretilip CSS ile olceklenir - gorsel fark yok, render hizli.
 */
export const Grain: React.FC<{opacity?: number}> = ({opacity = 0.07}) => {
  const frame = useCurrentFrame();
  // Her 2 karede bir yeni tohum: hareketli grain hissi, yarisi kadar maliyet.
  const seed = Math.floor(frame / 2) % 12;

  return (
    <AbsoluteFill
      style={{
        opacity,
        mixBlendMode: 'overlay',
        pointerEvents: 'none',
        backgroundImage: `url("data:image/svg+xml;utf8,${encodeURIComponent(
          `<svg xmlns='http://www.w3.org/2000/svg' width='${TILE}' height='${TILE}'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' seed='${seed}'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>`,
        )}")`,
        backgroundSize: `${TILE}px ${TILE}px`,
      }}
    />
  );
};
