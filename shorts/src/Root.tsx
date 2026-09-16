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
          'Anam hâlâ tabağımı koyuyormuş sofraya.\nYirmi yıl oldu gideli.\nO ev kapısını kilitlemedi hiç.',
        author: '',
        cta: 'Seni bekleyen bir kapı var mı?',
        handle: '@30adogru',
        background: undefined,
        scene: 'bozkir' as const,
        accent: '#e0a45c',
        holdSeconds: 2.2,
        showSafeArea: false,
      }}
    />
  );
};
