import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {HEIGHT, WIDTH} from '../../theme';

/** Ufuk cizgisi. Metin blogunun altinda kalir; gokyuzu parlakligi metnin arkasinda durur. */
const HORIZON = 1440;

/**
 * Deterministik sozde-rastgele: ayni kare her zaman ayni sonucu verir.
 * Math.random() kullanilsaydi her kare farkli cikar, video titrerdi.
 */
const rand = (seed: number) => {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

type Ridge = {
  /** Tepe hattinin ortalama yuksekligi (px, ustten). */
  baseY: number;
  /** Tepelerin genligi. */
  amp: number;
  /** Kac tepe. */
  freq: number;
  phase: number;
  fill: string;
  /** Paralaks hizi: buyuk deger = daha hizli kayar = daha yakin. */
  parallax: number;
};

/**
 * Bozkir siluetinde yumusak tepe hatti uretir. Iki farkli frekansta sinus
 * ust uste binince tek sinusun yapay ritmi kirilir, dogal gorunur.
 */
const ridgePath = (r: Ridge, offset: number): string => {
  const step = 24;
  const pts: string[] = [];
  for (let x = -120; x <= WIDTH + 120; x += step) {
    const t = (x + offset) / WIDTH;
    const y =
      r.baseY +
      Math.sin(t * Math.PI * 2 * r.freq + r.phase) * r.amp * 0.55 +
      Math.sin(t * Math.PI * 2 * r.freq * 2.37 + r.phase * 1.7) * r.amp * 0.28 +
      Math.sin(t * Math.PI * 2 * r.freq * 5.1 + r.phase * 0.6) * r.amp * 0.1;
    pts.push(`${x.toFixed(0)},${y.toFixed(1)}`);
  }
  return `M-120,${HEIGHT} L${pts.join(' L')} L${WIDTH + 120},${HEIGHT} Z`;
};

const RIDGES: Ridge[] = [
  {baseY: HORIZON - 18, amp: 46, freq: 1.3, phase: 0.4, fill: '#6b4632', parallax: 0.18},
  {baseY: HORIZON + 46, amp: 66, freq: 0.9, phase: 2.1, fill: '#4a2e23', parallax: 0.34},
  {baseY: HORIZON + 148, amp: 92, freq: 0.7, phase: 4.3, fill: '#2c1a15', parallax: 0.58},
  {baseY: HORIZON + 300, amp: 120, freq: 0.5, phase: 5.9, fill: '#150c0a', parallax: 0.92},
];

/**
 * Ufukta yalniz bir agac: bozkirin klasik imgesi, olcek ve yalnizlik verir.
 * Tac tek bir sekil degil, ust uste binen duzensiz elipslerden olusur -
 * tek govdeli bir sekil siluette lolipop gibi gorunuyordu.
 */
const CANOPY: Array<[number, number, number]> = [
  [0, -58, 27],
  [-24, -52, 21],
  [22, -55, 23],
  [-12, -76, 20],
  [14, -74, 18],
  [-34, -66, 14],
  [32, -68, 13],
  [2, -90, 15],
  [-18, -88, 11],
];

const LoneTree: React.FC<{x: number; y: number; scale: number; drift: number}> = ({
  x,
  y,
  scale,
  drift,
}) => (
  <g transform={`translate(${x - drift}, ${y}) scale(${scale})`} fill="#140c09">
    {/* Govde: dibe dogru genisleyen, hafif egri */}
    <path d="M-2.6,0 C-3.4,-18 -4.2,-30 -2.2,-46 L2.4,-46 C4,-30 3.6,-18 3.4,0 Z" />
    {/* Dal catallari */}
    <path
      d="M-1,-44 L-15,-58 M1,-44 L14,-56 M0,-48 L-6,-64"
      stroke="#140c09"
      strokeWidth="2.6"
      strokeLinecap="round"
      fill="none"
    />
    {CANOPY.map(([cx, cy, r], i) => (
      // eslint-disable-next-line react/no-array-index-key
      <ellipse key={i} cx={cx} cy={cy} rx={r} ry={r * 0.76} />
    ))}
  </g>
);

export const Bozkir: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  // Cok yavas yatay kayma: katmanlar farkli hizda gidince derinlik olusur.
  const t = interpolate(frame, [0, durationInFrames], [0, 1], {extrapolateRight: 'clamp'});
  const drift = t * 46;

  const sunY = HORIZON - 96 + t * 10;

  return (
    <AbsoluteFill>
      <svg
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        width={WIDTH}
        height={HEIGHT}
        style={{display: 'block'}}
      >
        <defs>
          <linearGradient id="gokyuzu" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#241a20" />
            <stop offset="34%" stopColor="#4a2a26" />
            <stop offset="62%" stopColor="#8d4a2b" />
            <stop offset="84%" stopColor="#c8703a" />
            <stop offset="100%" stopColor="#e3a862" />
          </linearGradient>
          <radialGradient id="gunesHale">
            <stop offset="0%" stopColor="#ffd89b" stopOpacity="0.85" />
            <stop offset="45%" stopColor="#e8873f" stopOpacity="0.34" />
            <stop offset="100%" stopColor="#e8873f" stopOpacity="0" />
          </radialGradient>
          <linearGradient id="pus" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#e0a05c" stopOpacity="0" />
            <stop offset="100%" stopColor="#e0a05c" stopOpacity="0.30" />
          </linearGradient>
        </defs>

        {/* Gokyuzu */}
        <rect x="0" y="0" width={WIDTH} height={HORIZON + 8} fill="url(#gokyuzu)" />

        {/* Gunes ve halesi */}
        <circle cx={186} cy={sunY} r={430} fill="url(#gunesHale)" />
        <circle cx={186} cy={sunY} r={58} fill="#ffe6bd" opacity="1" />

        {/* Ufuk pusu: tepelerin dibini yumusatir, derinlik hissini artirir */}
        <rect x="0" y={HORIZON - 230} width={WIDTH} height={238} fill="url(#pus)" />

        {/* Tepe katmanlari, uzaktan yakina */}
        {RIDGES.map((r, i) => (
          // eslint-disable-next-line react/no-array-index-key
          <path key={i} d={ridgePath(r, drift * r.parallax)} fill={r.fill} />
        ))}

        <LoneTree x={792} y={HORIZON + 78} scale={1.25} drift={drift * 0.34} />

        {/* Bozkir tozu: ufukta suzulen zerrecikler */}
        {Array.from({length: 38}).map((_, i) => {
          const speed = 0.35 + rand(i * 3.1) * 0.9;
          const x = (rand(i) * WIDTH + t * 150 * speed) % WIDTH;
          const y = HORIZON - 460 + rand(i * 7.7) * 560;
          const r = 1.1 + rand(i * 5.3) * 2.3;
          const o = 0.10 + rand(i * 11.3) * 0.26;
          return (
            // eslint-disable-next-line react/no-array-index-key
            <circle key={i} cx={x} cy={y} r={r} fill="#ffdcaa" opacity={o} />
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};
