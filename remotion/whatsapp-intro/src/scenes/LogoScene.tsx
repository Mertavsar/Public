import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Logo } from "../components/Logo";
import { Sfx } from "../components/Sfx";
import { IntroProps } from "../schema";
import { FONT } from "../theme";

export const LogoScene: React.FC<IntroProps> = (props) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const s = Math.min(width, height) / 1080;
  const logoSize = 300 * s;

  const letters = Array.from(props.logoYazisi);
  const exit = interpolate(frame, [55, 70], [1, 1.08], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        justifyContent: "center",
        transform: `scale(${exit})`,
      }}
    >
      {/* Yayılan halkalar */}
      {[0, 8, 16].map((d) => {
        const p = interpolate(frame - d, [0, 45], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        return (
          <div
            key={d}
            style={{
              position: "absolute",
              width: logoSize,
              height: logoSize,
              borderRadius: "50%",
              border: `${4 * s}px solid ${props.vurguRengi}`,
              transform: `translateY(${-70 * s}px) scale(${1 + p * 2.6})`,
              opacity: (1 - p) * 0.7 * (p > 0 ? 1 : 0),
            }}
          />
        );
      })}

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 56 * s,
        }}
      >
        <Logo size={logoSize} accent={props.vurguRengi} />
        <div
          style={{
            display: "flex",
            fontFamily: FONT,
            fontWeight: 800,
            fontSize: 120 * s,
            letterSpacing: -3 * s,
            color: "white",
          }}
        >
          {letters.map((ch, i) => {
            const p = spring({
              frame: frame - 22 - i * 2,
              fps,
              config: { damping: 14, stiffness: 160 },
            });
            return (
              <span
                key={i}
                style={{
                  display: "inline-block",
                  whiteSpace: "pre",
                  opacity: p,
                  transform: `translateY(${(1 - p) * 60 * s}px)`,
                  filter: `blur(${(1 - p) * 8 * s}px)`,
                }}
              >
                {ch}
              </span>
            );
          })}
        </div>
      </div>

      <Sfx at={0} src="pop.wav" volume={0.8} enabled={props.sesEfektleri} />
      <Sfx at={58} src="whoosh.wav" volume={0.5} enabled={props.sesEfektleri} />
    </AbsoluteFill>
  );
};
