import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Inter (OFL) projeye gömülü: render internet gerektirmez.
// latin-ext dosyası Türkçe karakterleri (ş, ğ, İ) taşır.
const FAMILY = "Inter Intro";
loadFont({
  family: FAMILY,
  url: staticFile("fonts/inter-latin.woff2"),
  weight: "400 900",
  unicodeRange:
    "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD",
});
loadFont({
  family: FAMILY,
  url: staticFile("fonts/inter-latin-ext.woff2"),
  weight: "400 900",
  unicodeRange:
    "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF",
});

export const FONT = `"${FAMILY}", "Noto Color Emoji", sans-serif`;

export const COLORS = {
  green: "#25D366",
  greenDark: "#128C7E",
  teal: "#075E54",
  tealDeep: "#04261F",
  night: "#020F0C",
  chatBg: "#EFEAE2",
  outgoing: "#D9FDD3",
  incoming: "#FFFFFF",
  tickBlue: "#53BDEB",
  tickGray: "#8696A0",
  textDark: "#111B21",
  textMuted: "#667781",
  white: "#FFFFFF",
};

export const FPS = 30;

// Sahne süreleri (kare). Geçişler sahneleri üst üste bindirdiği için
// toplam süre = sahneler - geçişler.
export const SCENES = {
  logo: 70,
  chat: 140,
  headline: 70,
  end: 85,
};
export const TRANSITION = 15;
export const TOTAL_FRAMES =
  SCENES.logo + SCENES.chat + SCENES.headline + SCENES.end - 3 * TRANSITION;
