import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { IntroProps } from "../schema";
import { FONT } from "../theme";

const Line: React.FC<{
  text: string;
  highlight: string;
  delay: number;
  accent: string;
  s: number;
}> = ({ text, highlight, delay, accent, s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = text.split(" ");
  const hl = new Set(highlight.split(" ").filter(Boolean));

  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        columnGap: 26 * s,
        rowGap: 4 * s,
      }}
    >
      {words.map((w, i) => {
        const p = spring({
          frame: frame - delay - i * 4,
          fps,
          config: { damping: 13, stiffness: 150 },
        });
        const isHl = hl.has(w);
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              position: "relative",
              color: isHl ? accent : "white",
              opacity: p,
              transform: `translateY(${(1 - p) * 70 * s}px) rotate(${(1 - p) * 6}deg)`,
              filter: `blur(${(1 - p) * 10 * s}px)`,
            }}
          >
            {w}
            {isHl ? (
              <span
                style={{
                  position: "absolute",
                  left: 0,
                  right: 0,
                  bottom: 2 * s,
                  height: 10 * s,
                  borderRadius: 6 * s,
                  background: accent,
                  opacity: 0.35,
                  transformOrigin: "left",
                  transform: `scaleX(${interpolate(frame - delay - i * 4, [8, 22], [0, 1], {
                    extrapolateLeft: "clamp",
                    extrapolateRight: "clamp",
                  })})`,
                }}
              />
            ) : null}
          </span>
        );
      })}
    </div>
  );
};

export const HeadlineScene: React.FC<IntroProps> = (props) => {
  const { width, height } = useVideoConfig();
  const s = Math.min(width, height) / 1080;

  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        justifyContent: "center",
        padding: 80 * s,
        fontFamily: FONT,
        fontWeight: 800,
        fontSize: 104 * s,
        lineHeight: 1.12,
        letterSpacing: -2 * s,
        textAlign: "center",
        gap: 40 * s,
      }}
    >
      <Line
        text={props.slogan1}
        highlight={props.slogan1Vurgu}
        delay={4}
        accent={props.vurguRengi}
        s={s}
      />
      <Line
        text={props.slogan2}
        highlight={props.slogan2Vurgu}
        delay={24}
        accent={props.vurguRengi}
        s={s}
      />
    </AbsoluteFill>
  );
};
