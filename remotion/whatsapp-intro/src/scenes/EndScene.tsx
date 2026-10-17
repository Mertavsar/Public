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
import { COLORS, FONT } from "../theme";

const TAP = 46;

export const EndScene: React.FC<IntroProps> = (props) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const s = Math.min(width, height) / 1080;

  const title = spring({ frame: frame - 10, fps, config: { damping: 14 } });
  const button = spring({
    frame: frame - 20,
    fps,
    config: { damping: 10, stiffness: 120 },
  });
  const press = interpolate(frame, [TAP - 3, TAP, TAP + 6], [1, 0.92, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const tap = interpolate(frame, [TAP - 14, TAP - 4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const ripple = interpolate(frame, [TAP, TAP + 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        justifyContent: "center",
        fontFamily: FONT,
        gap: 60 * s,
      }}
    >
      <Logo size={220 * s} accent={props.vurguRengi} />

      <div
        style={{
          color: "white",
          fontSize: 80 * s,
          fontWeight: 800,
          letterSpacing: -1.5 * s,
          textAlign: "center",
          padding: `0 ${60 * s}px`,
          opacity: title,
          transform: `translateY(${(1 - title) * 40 * s}px)`,
        }}
      >
        {props.ctaUstYazi}
      </div>

      <div style={{ position: "relative" }}>
        {/* Nabız halkaları */}
        {[0, 15].map((d) => {
          const p = ((frame - 24 - d) % 30) / 30;
          return frame > 24 + d ? (
            <div
              key={d}
              style={{
                position: "absolute",
                inset: 0,
                borderRadius: 999,
                border: `${4 * s}px solid ${props.vurguRengi}`,
                transform: `scale(${1 + p * 0.25}, ${1 + p * 0.7})`,
                opacity: (1 - p) * 0.6,
              }}
            />
          ) : null;
        })}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 24 * s,
            background: props.vurguRengi,
            color: "white",
            borderRadius: 999,
            padding: `${34 * s}px ${64 * s}px`,
            fontSize: 64 * s,
            fontWeight: 800,
            letterSpacing: 0.5 * s,
            boxShadow: `0 ${20 * s}px ${60 * s}px ${props.vurguRengi}66`,
            transform: `scale(${button * press})`,
            whiteSpace: "nowrap",
          }}
        >
          <svg width={64 * s} height={64 * s} viewBox="0 0 24 24">
            <path
              d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56-.35-.12-.74-.03-1.01.24l-1.57 1.97c-2.83-1.35-5.48-3.9-6.89-6.83l1.95-1.66c.27-.28.35-.67.24-1.02-.37-1.11-.56-2.3-.56-3.53 0-.54-.45-.99-.99-.99H4.19C3.65 3 3 3.24 3 3.99 3 13.28 10.73 21 20.01 21c.71 0 .99-.63.99-1.18v-3.45c0-.54-.45-.99-.99-.99z"
              fill="white"
            />
          </svg>
          {props.telefon}
        </div>

        {/* Dokunma göstergesi */}
        <div
          style={{
            position: "absolute",
            right: 80 * s,
            bottom: -10 * s,
            width: 70 * s,
            height: 70 * s,
            borderRadius: "50%",
            background: "rgba(255,255,255,0.85)",
            border: `${4 * s}px solid ${COLORS.white}`,
            opacity: tap * (1 - ripple * 0.8),
            transform: `translate(${(1 - tap) * 120 * s}px, ${(1 - tap) * 160 * s}px) scale(${frame >= TAP ? 0.85 : 1})`,
          }}
        />
        <div
          style={{
            position: "absolute",
            right: 80 * s - 35 * s,
            bottom: -10 * s - 35 * s,
            width: 140 * s,
            height: 140 * s,
            borderRadius: "50%",
            border: `${3 * s}px solid white`,
            opacity: ripple > 0 ? (1 - ripple) * 0.8 : 0,
            transform: `scale(${0.5 + ripple})`,
          }}
        />
      </div>

      <div
        style={{
          color: "rgba(255,255,255,0.75)",
          fontSize: 44 * s,
          fontWeight: 600,
          opacity: interpolate(frame, [30, 45], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        {props.markaAdi}
      </div>

      <Sfx at={4} src="ding.wav" volume={0.6} enabled={props.sesEfektleri} />
      <Sfx at={TAP} src="pop.wav" volume={0.6} enabled={props.sesEfektleri} />
    </AbsoluteFill>
  );
};
