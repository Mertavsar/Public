import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONT } from "../theme";

export const Ticks: React.FC<{ read: boolean }> = ({ read }) => (
  <svg width={34} height={22} viewBox="0 0 17 11" style={{ marginLeft: 6 }}>
    <g
      fill="none"
      stroke={read ? COLORS.tickBlue : COLORS.tickGray}
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="1.5,6 4.5,9 11,1.5" />
      <polyline points="8,8.5 8.5,9 15,1.5" />
    </g>
  </svg>
);

// Mesaj kutusu: yüksekliği açılarak eski mesajları yumuşakça yukarı iter.
export const Bubble: React.FC<{
  at: number;
  side: "in" | "out";
  time: string;
  readAt?: number;
  children: React.ReactNode;
}> = ({ at, side, time, readAt, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({
    frame: frame - at,
    fps,
    config: { damping: 13, stiffness: 170 },
  });
  const out = side === "out";

  return (
    <div
      style={{
        maxHeight: interpolate(p, [0, 1], [0, 420], {
          extrapolateRight: "clamp",
        }),
        display: "flex",
        justifyContent: out ? "flex-end" : "flex-start",
        overflow: "hidden",
        padding: "0 4px 6px",
        margin: "0 -4px -6px",
      }}
    >
      <div
        style={{
          maxWidth: "78%",
          background: out ? COLORS.outgoing : COLORS.incoming,
          borderRadius: 28,
          borderTopRightRadius: out ? 6 : 28,
          borderTopLeftRadius: out ? 28 : 6,
          padding: "18px 24px 12px",
          boxShadow: "0 2px 3px rgba(11,20,26,0.13)",
          fontFamily: FONT,
          fontSize: 44,
          lineHeight: 1.3,
          color: COLORS.textDark,
          opacity: p,
          transform: `scale(${interpolate(p, [0, 1], [0.6, 1])}) translateY(${(1 - p) * 30}px)`,
          transformOrigin: out ? "bottom right" : "bottom left",
        }}
      >
        {children}
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            alignItems: "center",
            fontSize: 26,
            color: COLORS.textMuted,
            marginTop: 4,
          }}
        >
          {time}
          {out ? <Ticks read={readAt !== undefined && frame >= readAt} /> : null}
        </div>
      </div>
    </div>
  );
};

export const TypingBubble: React.FC<{ from: number; to: number }> = ({
  from,
  to,
}) => {
  const frame = useCurrentFrame();
  const visible = interpolate(frame, [from, from + 6, to - 4, to], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        maxHeight: visible * 120,
        opacity: visible,
        display: "flex",
      }}
    >
      <div
        style={{
          background: COLORS.incoming,
          borderRadius: 28,
          borderTopLeftRadius: 6,
          padding: "30px 32px",
          display: "flex",
          gap: 12,
          boxShadow: "0 2px 3px rgba(11,20,26,0.13)",
        }}
      >
        {[0, 1, 2].map((i) => {
          const bounce = Math.max(0, Math.sin((frame - i * 4) * 0.35));
          return (
            <div
              key={i}
              style={{
                width: 18,
                height: 18,
                borderRadius: "50%",
                background: COLORS.tickGray,
                transform: `translateY(${-bounce * 10}px)`,
                opacity: 0.5 + bounce * 0.5,
              }}
            />
          );
        })}
      </div>
    </div>
  );
};
