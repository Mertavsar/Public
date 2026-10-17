import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../theme";

// Tüm sahnelerin altında sabit kalan arka plan; geçişlerde yalnızca içerik hareket eder.
export const Background: React.FC<{ accent: string }> = ({ accent }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const m = Math.max(width, height);

  const blobs = [
    { x: 0.2, y: 0.25, r: 0.55, speed: 0.018, phase: 0, opacity: 0.35 },
    { x: 0.85, y: 0.7, r: 0.6, speed: 0.014, phase: 2, opacity: 0.25 },
    { x: 0.5, y: 1.0, r: 0.5, speed: 0.022, phase: 4, opacity: 0.2 },
  ];

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 50% 40%, ${COLORS.tealDeep} 0%, ${COLORS.night} 75%)`,
        overflow: "hidden",
      }}
    >
      {blobs.map((b, i) => {
        const dx = Math.sin(frame * b.speed + b.phase) * 0.06;
        const dy = Math.cos(frame * b.speed * 1.3 + b.phase) * 0.05;
        const size = m * b.r;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: (b.x + dx) * width - size / 2,
              top: (b.y + dy) * height - size / 2,
              width: size,
              height: size,
              borderRadius: "50%",
              background: i === 1 ? COLORS.greenDark : accent,
              opacity: b.opacity,
              filter: `blur(${m * 0.12}px)`,
            }}
          />
        );
      })}
      {/* İnce nokta deseni */}
      <AbsoluteFill
        style={{
          backgroundImage:
            "radial-gradient(rgba(255,255,255,0.06) 1.5px, transparent 1.5px)",
          backgroundSize: "36px 36px",
          backgroundPosition: `0 ${-frame * 0.4}px`,
          maskImage:
            "radial-gradient(ellipse at center, black 30%, transparent 80%)",
        }}
      />
    </AbsoluteFill>
  );
};
