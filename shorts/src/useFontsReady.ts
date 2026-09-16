import {useEffect, useState} from 'react';
import {continueRender, delayRender} from 'remotion';
import {fontsReady} from './fonts';

/**
 * Metin olcumu (measureText) dogru sonuc vermesi icin fontun yuklu olmasi sart.
 * fonts.ts render'i bekletiyor ama React bilesenini otomatik yeniden
 * render etmiyor; bu hook hazir olunca state degistirip yeniden render tetikler
 * ve o ana kadar kendi delayRender handle'i ile kare yakalanmasini engeller.
 */
export const useFontsReady = (): boolean => {
  const [ready, setReady] = useState(false);
  const [handle] = useState(() => delayRender('Font olculeri bekleniyor'));

  useEffect(() => {
    let alive = true;
    fontsReady.then(() => {
      if (alive) setReady(true);
    });
    return () => {
      alive = false;
      // Bilesen erken sokulurse render asili kalmasin.
      continueRender(handle);
    };
  }, [handle]);

  useEffect(() => {
    if (ready) continueRender(handle);
  }, [ready, handle]);

  return ready;
};
