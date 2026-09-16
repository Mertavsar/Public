import {continueRender, delayRender, staticFile} from 'remotion';
import {FONT_BODY, FONT_UI} from './theme';

/**
 * Google Fonts'un unicode-range tanimlari.
 * Turkce icin kritik: ı (U+0131) "latin" altkumesinde, ama
 * İ (U+0130), ğ (U+011F), ş (U+015F) "latin-ext" icinde. Ikisi de yuklenmezse
 * render'da eksik glif cikar.
 */
const LATIN =
  'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD';
const LATIN_EXT =
  'U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF';

type Face = {
  family: string;
  file: string;
  weight: string;
  style: string;
  unicodeRange: string;
};

const FACES: Face[] = [
  // Playfair Display degisken font: tek dosya 400-900 agirlik araligini karsilar.
  {family: FONT_BODY, file: 'PlayfairDisplay-500-normal-latin.woff2', weight: '400 900', style: 'normal', unicodeRange: LATIN},
  {family: FONT_BODY, file: 'PlayfairDisplay-500-normal-latin-ext.woff2', weight: '400 900', style: 'normal', unicodeRange: LATIN_EXT},
  {family: FONT_BODY, file: 'PlayfairDisplay-500-italic-latin.woff2', weight: '400 900', style: 'italic', unicodeRange: LATIN},
  {family: FONT_BODY, file: 'PlayfairDisplay-500-italic-latin-ext.woff2', weight: '400 900', style: 'italic', unicodeRange: LATIN_EXT},
  {family: FONT_UI, file: 'Inter-400-normal-latin.woff2', weight: '400 700', style: 'normal', unicodeRange: LATIN},
  {family: FONT_UI, file: 'Inter-400-normal-latin-ext.woff2', weight: '400 700', style: 'normal', unicodeRange: LATIN_EXT},
];

/**
 * Fontlari FontFace API ile yukler. delayRender modul seviyesinde cagrilir:
 * boylece ilk kare yakalanmadan once font hazir olur. CSS @font-face kullanilsa
 * ilk kareler fallback font ile render edilirdi.
 */
const handle = delayRender('Fontlar yukleniyor');

export const fontsReady = Promise.all(
  FACES.map(async (f) => {
    const face = new FontFace(f.family, `url(${staticFile(`fonts/${f.file}`)}) format('woff2')`, {
      weight: f.weight,
      style: f.style,
      unicodeRange: f.unicodeRange,
    });
    await face.load();
    document.fonts.add(face);
  }),
)
  .then(() => {
    continueRender(handle);
  })
  .catch((err) => {
    // eslint-disable-next-line no-console
    console.error('Font yuklenemedi:', err);
    continueRender(handle);
  });
