import {Composition} from 'remotion';
import {WomanTest} from './dev/WomanTest';
import {SccPinkEnergy} from './SccPinkEnergy';
import {DURATION, FPS, HEIGHT, WIDTH} from './timeline';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="SccPinkEnergy" component={SccPinkEnergy} durationInFrames={DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
    <Composition id="WomanTest" component={WomanTest} durationInFrames={1} fps={FPS} width={1600} height={1400} />
  </>
);
