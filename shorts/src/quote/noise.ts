/** Deterministik: ayni girdi her zaman ayni sonuc. Video kareleri arasi tutarlilik sart. */
export const hash = (n: number): number => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

/** Yumusak 1B gurultu. Kareler arasi sicramasin diye komsu degerler arasi gecis yumusatilir. */
export const noise1 = (x: number): number => {
  const i = Math.floor(x);
  const f = x - i;
  const u = f * f * (3 - 2 * f);
  return hash(i) * (1 - u) + hash(i + 1) * u;
};
