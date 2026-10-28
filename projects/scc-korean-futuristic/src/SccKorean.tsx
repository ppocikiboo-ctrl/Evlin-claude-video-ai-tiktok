import React from 'react';
import {AbsoluteFill, Audio, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {FloatingCounters, GlowParticles, LightRing, PearlSheen, Sakura, SoftLight, Stars} from './components/Atmosphere';
import {ButterflyFlight} from './components/Butterfly';
import {IconBadge, Lotus, Sneaker, WaterBottle3L} from './components/CareIcons';
import {FoodPlate} from './components/FoodPlate';
import {Sparkles, Star4} from './components/Icons';
import {KoreanWoman, POSES, workoutRoutine} from './components/KoreanWoman';
import {ButtonText, Extrude3DText, FlipBoardText, NeonText, RibbonText, StickerText} from './components/TextStyles';
import {loadFonts} from './theme';
import {DURATION, LAYERS, LINES, MUSIC_VOLUME, PLATE_BITES, SFX_CUES, SFX_VOLUME, SHOW_PLATE, WOMAN} from './timeline';

loadFonts();

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const win = (f: number, from: number, to: number, fadeIn = 10, fadeOut = 10) =>
  Math.min(interpolate(f, [from, from + fadeIn], [0, 1], clamp), interpolate(f, [to - fadeOut, to], [1, 0], clamp));

// ------------------------------------------------------------------ footage

// One continuous take: the whole original clip plays once, uncut. It is only
// lightly cleaned up in scripts/prep_footage.sh; nothing is drawn over the label.
const Footage: React.FC = () => {
  const f = useCurrentFrame();
  const scale = interpolate(f, [0, DURATION], [1, 1.03]);
  return (
    <AbsoluteFill style={{transform: `scale(${scale})`, transformOrigin: '45% 50%'}}>
      <OffthreadVideo src={staticFile('footage.mp4')} muted style={{width: '100%', height: '100%', filter: 'contrast(1.03)'}} />
    </AbsoluteFill>
  );
};

const Blossom: React.FC<{size: number}> = ({size}) => (
  <svg width={size} height={size} viewBox="-50 -50 100 100">
    {[0, 1, 2, 3, 4].map((i) => (
      <path key={i} transform={`rotate(${i * 72})`} d="M0 -6 C-16 -18 -18 -40 -6 -46 Q0 -42 0 -38 Q0 -42 6 -46 C18 -40 16 -18 0 -6 Z" fill="#ffc3dc" stroke="#fff" strokeWidth={2} />
    ))}
    <circle r={9} fill="#ffd36e" />
  </svg>
);

// ------------------------------------------------------------------ rotating layers

const HologramWoman: React.FC = () => {
  const f = useCurrentFrame();
  const {from, to} = LAYERS.hologramWoman;
  if (f < from || f >= to) return null;
  const reveal = interpolate(f, [from, from + 34], [0, 1], clamp);
  return (
    <div style={{position: 'absolute', left: 840, top: 150}}>
      <KoreanWoman height={430} pose={POSES.rest} variant="hologram" reveal={reveal} opacity={win(f, from, to, 1, 8)} />
    </div>
  );
};

// Stretches, then light dumbbell presses with light-drop "sweat" and warm
// light lines circling her body.
const WorkoutWoman: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {from, to} = LAYERS.woman;
  if (f < from || f >= to) return null;
  const t = f - from;
  const a = win(f, from, to, 12, 10);
  const rise = interpolate(f, [from, from + 14], [30, 0], clamp);
  const dumbbells = t < WOMAN.dumbbellsAt ? 0 : spring({frame: t - WOMAN.dumbbellsAt, fps, config: {damping: 9, stiffness: 200}});
  return (
    <div style={{position: 'absolute', left: 150, top: 450 + rise, opacity: a}}>
      <KoreanWoman
        height={540}
        pose={workoutRoutine(t, WOMAN)}
        dumbbells={dumbbells}
        sweat={interpolate(t, [WOMAN.sweatFrom, WOMAN.sweatFrom + 10], [0, 1], clamp)}
        energy={interpolate(t, [WOMAN.energyFrom, WOMAN.energyFrom + 10], [0, 1], clamp)}
      />
    </div>
  );
};

const CareIconRow: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {from, to} = LAYERS.careIcons;
  if (f < from || f >= to) return null;
  const out = interpolate(f, [to - 6, to], [1, 0], clamp);
  const waterFill = interpolate(f, [from + 2, from + 26], [0, 1], clamp);
  const items: [React.ReactNode, string][] = [
    [<WaterBottle3L size={70} fill={waterFill} />, `${(3 * waterFill).toFixed(1)} LITER`],
    [<Sneaker size={70} />, 'JALAN'],
    [<Lotus size={76} />, 'SELF-CARE'],
  ];
  return (
    <>
      {items.map(([icon, label], i) => {
        const at = from + i * 6;
        const pop = f < at ? 0 : spring({frame: f - at, fps, config: {damping: 10, stiffness: 170}});
        return (
          <div key={i} style={{position: 'absolute', left: 640 + i * 160 - 58, top: 420 + Math.sin(f / 10 + i) * 6, opacity: out}}>
            <IconBadge size={116} pop={pop} seed={i * 2} label={label}>
              {icon}
            </IconBadge>
          </div>
        );
      })}
    </>
  );
};

// ------------------------------------------------------------------ composition

export const SccKorean: React.FC = () => {
  const L = LINES;
  return (
    <AbsoluteFill style={{backgroundColor: '#140020'}}>
      <Footage />
      {/* grading: white key light, pastel pink/lavender, pearl reflection */}
      <SoftLight />
      <PearlSheen />
      <GlowParticles />
      <Stars />
      <FloatingCounters amount={0.95} />
      <Sakura bursts={[LAYERS.sakuraBurst1, LAYERS.sakuraBurst2]} />

      <HologramWoman />
      {SHOW_PLATE && (
        <div style={{position: 'absolute', left: 750, top: 720}}>
          <FoodPlate from={LAYERS.plate.from} to={LAYERS.plate.to} bites={PLATE_BITES} width={300} />
        </div>
      )}
      <WorkoutWoman />
      <CareIconRow />
      <ButterflyFlight
        flights={[
          {from: 300, to: 345, path: [[-60, 1500], [60, 1300], [30, 1050], [110, 820], [50, 600]], size: 70, seed: 1},
          {from: 306, to: 345, path: [[1140, 1300], [990, 1150], [1010, 900], [940, 700]], size: 64, hue: 'lilac', seed: 3},
        ]}
      />
      <LightRing cx={470} cy={1000} rx={430} ry={600} from={LAYERS.ringFinal.from} to={DURATION + 10} drawFrames={30} tilt={-6} />

      {/* the six lines, one at a time, each with its own solid style */}
      <StickerText line={L.selfCare} cx={410} cy={292} rows={[['SELF-CARE BUKAN'], ['SEKADAR SKINCARE!', <Star4 size={40} color="#ffc531" />]]} size={50} />
      <RibbonText line={L.badan} cx={540} cy={1540} rows={[['JANGAN LUPA'], ['PENJAGAAN BADAN', <Sparkles size={50} />]]} size={52} width={800} height={160} />
      <Extrude3DText line={L.kenali} cx={540} cy={262} text="KENALI SCC" icon={<Sparkles size={72} />} size={100} />
      <FlipBoardText line={L.bahan} cx={540} cy={290} rows={['WHITE KIDNEY BEAN +', 'L-CARNITINE']} tile={58} />
      <NeonText line={L.rutin} cx={540} cy={290} rows={[['JADIKAN', 'SELF-CARE'], ['SATU', 'RUTIN', <Blossom size={60} />]]} size={58} width={880} height={200} />
      <ButtonText line={L.produk} cx={540} cy={300} words={['KENALI', 'PRODUK', 'INI', <Sparkles size={56} />]} size={58} />

      {/* sound */}
      <Audio src={staticFile('audio/music.wav')} volume={MUSIC_VOLUME} />
      {SFX_CUES.map(([at, name], i) => (
        <Sequence key={i} from={at} durationInFrames={45} layout="none">
          <Audio src={staticFile(`audio/${name}.wav`)} volume={SFX_VOLUME[name]} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
