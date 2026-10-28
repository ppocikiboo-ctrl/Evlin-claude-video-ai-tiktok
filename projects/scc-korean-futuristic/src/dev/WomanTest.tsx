import {AbsoluteFill} from 'remotion';
import {KoreanWoman, POSES, stretchRoutine} from '../components/KoreanWoman';

// Dev-only sheet to check poses: npx remotion still WomanTest out/woman.png
export const WomanTest: React.FC = () => (
  <AbsoluteFill style={{background: '#2a1640', flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'center', gap: 30}}>
    <KoreanWoman height={600} pose={POSES.rest} />
    <KoreanWoman height={600} pose={stretchRoutine(28)} />
    <KoreanWoman height={600} pose={POSES.goal} dumbbells={1} energy={1} sweat={1} />
    <KoreanWoman height={600} pose={POSES.press} dumbbells={1} energy={1} sweat={1} />
    <KoreanWoman height={600} pose={POSES.rest} variant="hologram" />
  </AbsoluteFill>
);
