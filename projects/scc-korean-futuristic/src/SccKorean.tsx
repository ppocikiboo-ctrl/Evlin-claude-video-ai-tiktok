import React from 'react';
import {AbsoluteFill, Audio, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {FloatingCounters, GlowParticles, LightRing, PearlSheen, Sakura, SoftLight, Stars} from './components/Atmosphere';
import {ButterflyFlight} from './components/Butterfly';
import {IconBadge, Lotus, Sneaker, WaterBottle} from './components/CareIcons';
import {Sparkles, Star4} from './components/Icons';
import {KoreanWoman, POSES, stretchRoutine} from './components/KoreanWoman';
import {BubbleText, DigitalText, HologramText, NeonText, SlideText, ZoomText} from './components/TextStyles';
import {loadFonts} from './theme';
import {DURATION, LAYERS, LINES, MUSIC_VOLUME, SFX_CUES, SFX_VOLUME} from './timeline';

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

const StretchingWoman: React.FC = () => {
  const f = useCurrentFrame();
  const {from, to} = LAYERS.koreanWoman;
  if (f < from || f >= to) return null;
  const a = win(f, from, to, 12, 12);
  const rise = interpolate(f, [from, from + 14], [30, 0], clamp);
  return (
    <div style={{position: 'absolute', left: 150, top: 440 + rise, opacity: a}}>
      <KoreanWoman height={540} pose={stretchRoutine(f - from)} />
    </div>
  );
};

const CareIconColumn: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {from, to} = LAYERS.careIcons;
  if (f < from || f >= to) return null;
  const out = interpolate(f, [to - 6, to], [1, 0], clamp);
  const items: React.ReactNode[] = [<WaterBottle size={64} />, <Sneaker size={70} />, <Lotus size={78} />];
  return (
    <>
      {items.map((icon, i) => {
        const at = from + i * 5;
        const pop = f < at ? 0 : spring({frame: f - at, fps, config: {damping: 10, stiffness: 170}});
        return (
          <div key={i} style={{position: 'absolute', left: 905 - 58, top: 640 + i * 160 + Math.sin(f / 10 + i) * 6, opacity: out}}>
            <IconBadge size={116} pop={pop} seed={i * 2}>
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
      <FloatingCounters amount={0.8} />
      <Sakura bursts={[LAYERS.sakuraBurst1, LAYERS.sakuraBurst2]} />

      <HologramWoman />
      <CareIconColumn />
      <LightRing cx={430} cy={960} rx={380} ry={520} from={LAYERS.ringPack.from} to={LAYERS.ringPack.to} drawFrames={16} tilt={-5} />
      <StretchingWoman />
      <ButterflyFlight
        flights={[
          {from: 186, to: 290, path: [[-60, 1100], [120, 980], [420, 900], [560, 640], [420, 420], [140, 380], [-80, 300]], size: 74, seed: 0},
          {from: 196, to: 290, path: [[640, -60], [600, 160], [520, 420], [600, 560], [520, 700], [300, 760], [-60, 820]], size: 60, hue: 'lilac', seed: 2},
          {from: 300, to: 345, path: [[-60, 1500], [60, 1300], [30, 1050], [110, 820], [50, 600]], size: 70, seed: 1},
          {from: 306, to: 345, path: [[1140, 1300], [990, 1150], [1010, 900], [940, 700]], size: 64, hue: 'lilac', seed: 3},
        ]}
      />
      <LightRing cx={470} cy={1000} rx={430} ry={600} from={LAYERS.ringFinal.from} to={DURATION + 10} drawFrames={30} tilt={-6} />

      {/* the six lines, one at a time, each with its own entrance */}
      <HologramText
        line={L.selfCare}
        cx={410}
        cy={288}
        width={720}
        height={200}
        lines={[['SELF-CARE BUKAN'], ['SEKADAR SKINCARE!', {icon: <Star4 size={44} color="#ffd98a" />}]]}
        size={50}
      />
      <BubbleText line={L.badan} cx={520} cy={1540} rows={[['JANGAN', 'LUPA'], ['PENJAGAAN', 'BADAN', <Sparkles size={52} />]]} size={56} />
      <ZoomText line={L.kenali} cx={540} cy={262} text="KENALI SCC" icon={<Sparkles size={72} />} size={104} />
      <DigitalText line={L.bahan} cx={540} cy={285} rows={['WHITE KIDNEY BEAN +', 'L-CARNITINE']} size={56} width={900} />
      <NeonText line={L.rutin} cx={540} cy={290} rows={[['JADIKAN', 'SELF-CARE'], ['SATU', 'RUTIN', <Blossom size={60} />]]} size={58} width={880} height={200} />
      <SlideText line={L.produk} cx={540} cy={300} width={860} height={150} words={['KENALI', 'PRODUK', 'INI', <Sparkles size={56} />]} size={62} />

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
