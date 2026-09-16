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
          'Gurbet, memleketin adını duyunca\nsusmayı öğrenmektir.\nSen susarsın, için konuşur.',
        author: '',
        cta: 'Sen kaç yıldır gurbettesin?',
        handle: '@30adogru',
        background: undefined,
        accent: '#c9873f',
        holdSeconds: 2.2,
        showSafeArea: false,
      }}
    />
  );
};
