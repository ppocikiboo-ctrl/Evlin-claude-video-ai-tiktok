import {Composition} from 'remotion';
import {WomanTest} from './dev/WomanTest';
import {SccKorean} from './SccKorean';
import {DURATION, FPS, HEIGHT, WIDTH} from './timeline';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="SccKorean" component={SccKorean} durationInFrames={DURATION} fps={FPS} width={WIDTH} height={HEIGHT} />
    <Composition id="WomanTest" component={WomanTest} durationInFrames={1} fps={FPS} width={1600} height={1400} />
  </>
);
