import {Composition} from 'remotion';
import {SccVideo} from './SccVideo';
import {DURATION, FPS, HEIGHT, WIDTH} from './timeline';

export const RemotionRoot: React.FC = () => (
  <Composition id="SccBodyCare" component={SccVideo} durationInFrames={DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
);
