import {Composition} from 'remotion';
import {VbgvOffice} from './VbgvOffice';
import {DURATION, FPS, HEIGHT, WIDTH} from './timeline';

export const RemotionRoot: React.FC = () => (
  <Composition id="VbgvOffice" component={VbgvOffice} durationInFrames={DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
);
