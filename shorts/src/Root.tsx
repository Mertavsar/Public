import React from 'react';
import {Composition} from 'remotion';
import './fonts';
import {FPS, HEIGHT, WIDTH} from './theme';
import {QuoteShort} from './quote/QuoteShort';
import {quoteDurationInFrames, quoteSchema} from './quote/schema';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="QuoteShort"
      component={QuoteShort}
      schema={quoteSchema}
      width={WIDTH}
      height={HEIGHT}
      fps={FPS}
      durationInFrames={300}
      calculateMetadata={({props}) => ({
        durationInFrames: quoteDurationInFrames(props),
      })}
      defaultProps={{
        quote:
          'Herkes gidebilir.\nMesele kimin yokluğunun\n> ev gibi kokması.',
        author: '',
        cta: 'Kimin yokluğu ev gibi kokuyor?',
        handle: '@30adogru',
        background: 'bg/bugday-ruzgar.mp4',
        scene: 'bozkir' as const,
        panel: true,
        accent: '#e0a45c',
        holdSeconds: 2.2,
        showSafeArea: false,
      }}
    />
  );
};
