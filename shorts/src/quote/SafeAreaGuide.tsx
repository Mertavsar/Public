import React from 'react';
import {AbsoluteFill} from 'remotion';
import {SAFE, SAFE_HEIGHT, SAFE_WIDTH} from '../theme';

/**
 * Sadece Studio'da isine yarar: YouTube Shorts arayuzunun kapattigi alanlari
 * gosterir. Kirmizi bolgeler telefonda baslik/kanal adi/butonlarin altinda kalir.
 */
export const SafeAreaGuide: React.FC = () => (
  <AbsoluteFill style={{pointerEvents: 'none'}}>
    <div
      style={{
        position: 'absolute',
        top: SAFE.top,
        left: SAFE.left,
        width: SAFE_WIDTH,
        height: SAFE_HEIGHT,
        border: '2px dashed rgba(90, 220, 160, 0.9)',
        boxSizing: 'border-box',
      }}
    />
    <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: SAFE.top, background: 'rgba(255,60,60,0.16)'}} />
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: SAFE.bottom, background: 'rgba(255,60,60,0.16)'}} />
    <div style={{position: 'absolute', top: 0, bottom: 0, right: 0, width: SAFE.right, background: 'rgba(255,60,60,0.16)'}} />
    <div style={{position: 'absolute', top: 0, bottom: 0, left: 0, width: SAFE.left, background: 'rgba(255,60,60,0.16)'}} />
  </AbsoluteFill>
);
