import { linearTiming, springTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { AbsoluteFill } from "remotion";
import { Background } from "./components/Background";
import { ChatScene } from "./scenes/ChatScene";
import { EndScene } from "./scenes/EndScene";
import { HeadlineScene } from "./scenes/HeadlineScene";
import { LogoScene } from "./scenes/LogoScene";
import { IntroProps } from "./schema";
import { SCENES, TRANSITION } from "./theme";

export const WhatsAppIntro: React.FC<IntroProps> = (props) => {
  return (
    <AbsoluteFill>
      <Background accent={props.vurguRengi} />
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={SCENES.logo}>
          <LogoScene {...props} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: TRANSITION })}
        />
        <TransitionSeries.Sequence durationInFrames={SCENES.chat}>
          <ChatScene {...props} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={slide({ direction: "from-bottom" })}
          timing={springTiming({
            config: { damping: 200 },
            durationInFrames: TRANSITION,
          })}
        />
        <TransitionSeries.Sequence durationInFrames={SCENES.headline}>
          <HeadlineScene {...props} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: TRANSITION })}
        />
        <TransitionSeries.Sequence durationInFrames={SCENES.end}>
          <EndScene {...props} />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </AbsoluteFill>
  );
};
