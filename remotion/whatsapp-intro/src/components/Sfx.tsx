import { Html5Audio, Sequence, staticFile } from "remotion";

export const Sfx: React.FC<{
  at: number;
  src: "pop.wav" | "ding.wav" | "whoosh.wav";
  volume?: number;
  enabled: boolean;
}> = ({ at, src, volume = 1, enabled }) => {
  if (!enabled) {
    return null;
  }
  return (
    <Sequence from={at} layout="none">
      <Html5Audio src={staticFile(src)} volume={volume} />
    </Sequence>
  );
};
