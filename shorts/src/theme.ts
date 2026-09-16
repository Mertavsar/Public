export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;

/**
 * YouTube Shorts kaplama alanlari (1080x1920 icin).
 * Alt: baslik + kanal adi + aciklama. Sag: begen/yorum/paylas/remix sutunu.
 * Metin bu kutunun disina tasarsa telefonda UI'nin altinda kalir.
 */
export const SAFE = {
  top: 200,
  right: 190,
  bottom: 460,
  left: 80,
} as const;

export const SAFE_WIDTH = WIDTH - SAFE.left - SAFE.right;
export const SAFE_HEIGHT = HEIGHT - SAFE.top - SAFE.bottom;

/**
 * Metin kutusu. SAFE asimetriktir (sagda buton sutunu icin daha genis pay),
 * bu yuzden metni dogrudan SAFE'in ortasina koymak onu karenin merkezinden
 * kaydirir ve goz bunu "ortali degil" diye okur.
 * Cozum: her iki yanda da genis olan payi kullanip kareye gore simetrik,
 * merkezi (540, 960) olan bir kutu uretmek.
 */
const halfWidth = Math.min(WIDTH / 2 - SAFE.left, WIDTH - SAFE.right - WIDTH / 2);
const halfHeight = Math.min(HEIGHT / 2 - SAFE.top, HEIGHT - SAFE.bottom - HEIGHT / 2);

export const CONTENT = {
  width: halfWidth * 2,
  height: halfHeight * 2,
  left: WIDTH / 2 - halfWidth,
  top: HEIGHT / 2 - halfHeight,
} as const;

/** Zamanlama. Ilk satir 8. karede (0.27sn) baslar - Shorts'ta hook geciktirilmez. */
export const TIMING = {
  firstLineAt: 8,
  lineStagger: 26,
  lineReveal: 26,
  /** Bir grup icindeki gorsel satirlarin birbirini kovalama gecikmesi. */
  intraGroupStagger: 5,
  /** Sure hesabina eklenen pay: gorsel satir sayisi Node tarafinda bilinmiyor. */
  intraGroupTail: 14,
  authorDelay: 18,
  outro: 20,
} as const;

export const FONT_BODY = 'PlayfairQ';
export const FONT_UI = 'InterQ';

export const palette = {
  ink: '#f4ece1',
  inkDim: 'rgba(244, 236, 225, 0.62)',
  base: '#0b0705',
} as const;
