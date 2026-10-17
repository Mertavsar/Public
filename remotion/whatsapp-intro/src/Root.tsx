import { Composition } from "remotion";
import { defaultIntroProps, introSchema } from "./schema";
import { FPS, TOTAL_FRAMES } from "./theme";
import { WhatsAppIntro } from "./WhatsAppIntro";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Reels / Shorts / TikTok / Story */}
      <Composition
        id="WhatsAppIntro"
        component={WhatsAppIntro}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1080}
        height={1920}
        schema={introSchema}
        defaultProps={defaultIntroProps}
      />
      {/* YouTube / web */}
      <Composition
        id="WhatsAppIntroYatay"
        component={WhatsAppIntro}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1920}
        height={1080}
        schema={introSchema}
        defaultProps={defaultIntroProps}
      />
    </>
  );
};
