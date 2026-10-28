import {Composition} from 'remotion';
import {GedicsVideo} from './GedicsVideo';
import {DURATION, FPS, HEIGHT, WIDTH} from './timeline';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="GedicsHologram"
    component={GedicsVideo}
    durationInFrames={DURATION}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);
