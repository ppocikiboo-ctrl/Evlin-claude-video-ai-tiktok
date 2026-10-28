import {AbsoluteFill} from 'remotion';
import {KoreanWoman, POSES, stretchRoutine} from '../components/KoreanWoman';

// Dev-only sheet to check poses: npx remotion still WomanTest out/woman.png
export const WomanTest: React.FC = () => (
  <AbsoluteFill style={{background: '#2a1640', flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'center', gap: 20}}>
    <KoreanWoman height={600} pose={POSES.rest} />
    <KoreanWoman height={600} pose={POSES.up} />
    <KoreanWoman height={600} pose={stretchRoutine(28)} />
    <KoreanWoman height={600} pose={POSES.tee} />
    <KoreanWoman height={600} pose={POSES.rest} variant="hologram" />
    <KoreanWoman height={600} pose={stretchRoutine(52)} variant="hologram" reveal={0.7} />
  </AbsoluteFill>
);
