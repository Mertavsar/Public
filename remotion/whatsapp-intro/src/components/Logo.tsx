import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

// Konuşma balonu içinde ahize. Kendi çizimimiz; resmi logo kullanmak
// isterseniz public/ altına koyup <Img src={staticFile(...)} /> ile değiştirin.
const BUBBLE =
  "M25.45 74.33 A36 36 0 1 1 36.51 81.38 L15 88 Z";
const HANDSET =
  "M20.01 15.38c-1.23 0-2.42-.2-3.53-.56-.35-.12-.74-.03-1.01.24l-1.57 1.97c-2.83-1.35-5.48-3.9-6.89-6.83l1.95-1.66c.27-.28.35-.67.24-1.02-.37-1.11-.56-2.3-.56-3.53 0-.54-.45-.99-.99-.99H4.19C3.65 3 3 3.24 3 3.99 3 13.28 10.73 21 20.01 21c.71 0 .99-.63.99-1.18v-3.45c0-.54-.45-.99-.99-.99z";

export const Logo: React.FC<{
  size: number;
  accent: string;
  delay?: number;
  glow?: boolean;
}> = ({ size, accent, delay = 0, glow = true }) => {
  const frame = useCurrentFrame() - delay;
  const { fps } = useVideoConfig();

  const pop = spring({ frame, fps, config: { damping: 11, stiffness: 140 } });
  const draw = interpolate(frame, [6, 26], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const handset = spring({
    frame: frame - 18,
    fps,
    config: { damping: 9, stiffness: 180 },
  });
  const fillBubble = interpolate(frame, [24, 32], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        background: `linear-gradient(160deg, ${accent} 0%, #1DA851 100%)`,
        transform: `scale(${pop}) rotate(${interpolate(pop, [0, 1], [-25, 0])}deg)`,
        boxShadow: glow
          ? `0 ${size * 0.08}px ${size * 0.35}px ${accent}66, inset 0 ${-size * 0.04}px ${size * 0.1}px rgba(0,0,0,0.15)`
          : undefined,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <svg viewBox="0 0 100 100" width={size * 0.78} height={size * 0.78}>
        <path
          d={BUBBLE}
          fill="none"
          stroke="white"
          strokeWidth={7}
          strokeLinejoin="round"
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - draw}
        />
        <path d={BUBBLE} fill="white" opacity={fillBubble * 0.08} />
        <g
          transform={`translate(50 48) scale(${1.55 * handset}) translate(-12 -12)`}
        >
          <path d={HANDSET} fill="white" />
        </g>
      </svg>
    </div>
  );
};
