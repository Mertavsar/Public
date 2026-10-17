import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Bubble, TypingBubble } from "../components/Chat";
import { Sfx } from "../components/Sfx";
import { IntroProps } from "../schema";
import { COLORS, FONT } from "../theme";

// Sahne içi zamanlama (kare)
const T = {
  typeStart: 20,
  typeEnd: 44,
  send1: 48,
  read1: 62,
  typingFrom: 66,
  reply: 94,
  send2: 112,
  read2: 124,
};

const PHONE_W = 820;
const PHONE_H = 1640;

export const ChatScene: React.FC<IntroProps> = (props) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  // Telefon 1080x1920'lik bir sahnede tasarlandı, kompozisyona göre ölçeklenir.
  const u = Math.min(width / 1080, height / 1920);

  const enter = spring({ frame, fps, config: { damping: 16, stiffness: 90 } });
  const drift = interpolate(frame, [0, 140], [1, 1.04]);

  const chars = Array.from(props.musteriMesaji);
  const typed = Math.floor(
    interpolate(frame, [T.typeStart, T.typeEnd], [0, chars.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  );
  const draft = frame < T.send1 ? chars.slice(0, typed).join("") : "";
  const isTyping = frame >= T.typingFrom && frame < T.reply;
  const caretOn = Math.floor(frame / 8) % 2 === 0;

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <div
        style={{
          width: 1080,
          height: 1920,
          flexShrink: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transform: `scale(${u * drift})`,
        }}
      >
        <div
          style={{
            width: PHONE_W,
            height: PHONE_H,
            borderRadius: 120,
            background: "#0A0A0A",
            padding: 22,
            boxShadow:
              "0 60px 120px rgba(0,0,0,0.55), 0 0 0 3px #2b2b2b, inset 0 0 0 2px #3a3a3a",
            transform: `translateY(${(1 - enter) * 1400}px) rotate(${(1 - enter) * 8}deg)`,
            position: "relative",
          }}
        >
          <div
            style={{
              width: "100%",
              height: "100%",
              borderRadius: 100,
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
              background: COLORS.chatBg,
              fontFamily: FONT,
            }}
          >
            {/* Durum çubuğu + başlık */}
            <div style={{ background: COLORS.teal, color: "white" }}>
              <div
                style={{
                  height: 92,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "16px 70px 0",
                  fontSize: 32,
                  fontWeight: 600,
                }}
              >
                <span>9:41</span>
                <span style={{ letterSpacing: 4, fontSize: 26 }}>●●● ▮</span>
              </div>
              <div
                style={{
                  height: 140,
                  display: "flex",
                  alignItems: "center",
                  gap: 22,
                  padding: "0 36px",
                }}
              >
                <span style={{ fontSize: 50, opacity: 0.9 }}>‹</span>
                <div
                  style={{
                    width: 92,
                    height: 92,
                    borderRadius: "50%",
                    background: `linear-gradient(135deg, ${props.vurguRengi}, ${COLORS.greenDark})`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 44,
                    fontWeight: 800,
                  }}
                >
                  {Array.from(props.markaAdi)[0] ?? ""}
                </div>
                <div style={{ display: "flex", flexDirection: "column" }}>
                  <span style={{ fontSize: 40, fontWeight: 700 }}>
                    {props.markaAdi} <span style={{ color: COLORS.tickBlue }}>✔</span>
                  </span>
                  <span style={{ fontSize: 28, opacity: 0.85 }}>
                    {isTyping ? "yazıyor…" : "çevrimiçi"}
                  </span>
                </div>
              </div>
            </div>

            {/* Mesaj alanı */}
            <div
              style={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                justifyContent: "flex-end",
                gap: 22,
                padding: "30px 32px",
                backgroundImage:
                  "radial-gradient(rgba(0,0,0,0.05) 2px, transparent 2px)",
                backgroundSize: "44px 44px",
              }}
            >
              <div
                style={{
                  alignSelf: "center",
                  background: "#FFFFFFCC",
                  borderRadius: 16,
                  padding: "8px 22px",
                  fontSize: 26,
                  color: COLORS.textMuted,
                  marginBottom: 10,
                }}
              >
                BUGÜN
              </div>
              <Bubble at={T.send1} side="out" time="14:32" readAt={T.read1}>
                {props.musteriMesaji}
              </Bubble>
              <TypingBubble from={T.typingFrom} to={T.reply} />
              <Bubble at={T.reply} side="in" time="14:32">
                {props.isletmeCevabi}
              </Bubble>
              <Bubble at={T.send2} side="out" time="14:33" readAt={T.read2}>
                {props.musteriSonMesaj}
              </Bubble>
            </div>

            {/* Yazı alanı */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 18,
                padding: "16px 24px 48px",
              }}
            >
              <div
                style={{
                  flex: 1,
                  minHeight: 96,
                  background: "white",
                  borderRadius: 48,
                  display: "flex",
                  alignItems: "center",
                  padding: "14px 36px",
                  fontSize: 36,
                  color: draft ? COLORS.textDark : COLORS.textMuted,
                  boxShadow: "0 1px 2px rgba(0,0,0,0.1)",
                }}
              >
                {draft || "Mesaj"}
                {frame >= T.typeStart && frame < T.send1 && caretOn ? (
                  <span style={{ color: props.vurguRengi, marginLeft: 2 }}>|</span>
                ) : null}
              </div>
              <SendButton
                accent={props.vurguRengi}
                pressed={frame >= T.send1 - 3 && frame < T.send1 + 3}
              />
            </div>
          </div>
          {/* Dinamik ada */}
          <div
            style={{
              position: "absolute",
              top: 44,
              left: "50%",
              width: 210,
              height: 58,
              marginLeft: -105,
              borderRadius: 30,
              background: "#000",
            }}
          />
        </div>
      </div>

      <Sfx at={T.send1} src="pop.wav" volume={0.7} enabled={props.sesEfektleri} />
      <Sfx at={T.reply} src="pop.wav" volume={0.7} enabled={props.sesEfektleri} />
      <Sfx at={T.send2} src="pop.wav" volume={0.7} enabled={props.sesEfektleri} />
      <Sfx at={128} src="whoosh.wav" volume={0.5} enabled={props.sesEfektleri} />
    </AbsoluteFill>
  );
};

const SendButton: React.FC<{ accent: string; pressed: boolean }> = ({
  accent,
  pressed,
}) => (
  <div
    style={{
      width: 96,
      height: 96,
      borderRadius: "50%",
      background: accent,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      transform: `scale(${pressed ? 0.86 : 1})`,
      boxShadow: "0 2px 4px rgba(0,0,0,0.15)",
      flexShrink: 0,
    }}
  >
    <svg width={44} height={44} viewBox="0 0 24 24">
      <path d="M2 21l21-9L2 3v7l15 2-15 2z" fill="white" />
    </svg>
  </div>
);
