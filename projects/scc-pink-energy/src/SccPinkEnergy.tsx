import React from 'react';
import {AbsoluteFill, Audio, Easing, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {GlowParticles, LightRing, PearlSheen, Sakura, SoftLight, Stars} from './components/Atmosphere';
import {ButterflyFlight} from './components/Butterfly';
import {BalancedPlate, IconBadge, Sneaker, WaterBottle3L} from './components/CareIcons';
import {DecodeText} from './components/DecodeText';
import {GlassPanel} from './components/GlassPanel';
import {Eyes, PinkHeart, Sparkles, Star4} from './components/Icons';
import {KoreanWoman, pinkRoutine, stretchRoutine} from './components/KoreanWoman';
import {FONT, loadFonts} from './theme';
import {DURATION, LAYERS, LINES, MUSIC_VOLUME, ROUTINE, SFX_CUES, SFX_VOLUME} from './timeline';

loadFonts();

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const win = (f: number, from: number, to: number, fadeIn = 8, fadeOut = 8) =>
  Math.min(interpolate(f, [from, from + fadeIn], [0, 1], clamp), interpolate(f, [to - fadeOut, to], [1, 0], clamp));

// ------------------------------------------------------------------ footage

// One continuous take: the whole original clip plays once, uncut. Only a
// short impact shake on the hook moves it; nothing is drawn over the label.
const Footage: React.FC = () => {
  const f = useCurrentFrame();
  const scale = interpolate(f, [0, DURATION], [1, 1.04]);
  const amp = interpolate(f, [0, 10], [14, 0], clamp);
  const sx = Math.sin(f * 2.7) * amp;
  const sy = Math.cos(f * 3.1) * amp;
  return (
    <AbsoluteFill style={{transform: `translate(${sx}px, ${sy}px) scale(${scale})`, transformOrigin: '45% 50%'}}>
      <OffthreadVideo src={staticFile('footage.mp4')} muted style={{width: '100%', height: '100%', filter: 'contrast(1.04) saturate(1.02)'}} />
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ hook

// "JAGA MUKA DAH, BADAN PULA?" — fully readable on frame 0, fast zoom punch,
// impact shockwave + flash, sparkles around it, held for 1.8 s.
const Hook: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {out} = LINES.hook;
  if (f >= out) return null;
  // starts readable at 0.78x and punches past 1x on the BOOM
  const punch = 0.78 + 0.22 * spring({frame: f, fps, config: {damping: 7, stiffness: 260}});
  const pulse = f > 14 ? 1 + 0.025 * Math.exp((-(f % 15) / 15) * 5) : 1;
  const exit = interpolate(f, [out - 6, out], [1, 0], clamp);
  const exitZoom = interpolate(f, [out - 6, out], [1, 1.25], clamp);
  // light flash peaks just after frame 0, so the cover frame stays clear
  const flash = interpolate(f, [0, 1, 5], [0.12, 0.35, 0], clamp);
  const wave = interpolate(f, [0, 16], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const eyesLook = Math.sin(f / 6) > 0 ? 1 : -1;
  const lineStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 14,
    whiteSpace: 'nowrap',
    fontFamily: FONT,
    fontWeight: 900,
    fontSize: 104,
    lineHeight: 1.05,
    color: '#ffffff',
    WebkitTextStroke: '5px #ff3fae',
    paintOrder: 'stroke fill',
    textShadow: '0 0 16px #ff3fae, 0 0 38px rgba(255,63,174,0.85), 0 6px 0 #8f1a6a, 0 10px 18px rgba(40,0,40,0.7)',
  };
  return (
    <>
      {/* impact flash */}
      <AbsoluteFill style={{background: '#fff', opacity: flash, pointerEvents: 'none'}} />
      <div style={{position: 'absolute', left: 540, top: 300, transform: `translate(-50%, -50%) scale(${punch * pulse * exitZoom})`, opacity: exit}}>
        {/* dark-pink glow behind the text so it reads on the bright pack */}
        <div style={{position: 'absolute', left: '50%', top: '50%', width: 1100, height: 420, transform: 'translate(-50%, -50%)', background: 'radial-gradient(ellipse at center, rgba(70,0,55,0.6), rgba(70,0,55,0) 70%)'}} />
        {/* shockwave rings */}
        {[0, 1].map((i) => {
          const w = Math.max(0, wave - i * 0.15);
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: '50%',
                top: '50%',
                width: 400 + w * 900,
                height: 160 + w * 360,
                transform: 'translate(-50%, -50%)',
                borderRadius: '50%',
                border: `${6 - i * 2}px solid rgba(255,120,210,${(1 - w) * 0.9})`,
                boxShadow: `0 0 24px rgba(255,63,174,${(1 - w) * 0.8})`,
              }}
            />
          );
        })}
        <div style={{position: 'relative'}}>
          <div style={lineStyle}>JAGA MUKA DAH,</div>
          <div style={lineStyle}>
            BADAN PULA?
            <Eyes size={78} look={eyesLook} />
            <PinkHeart size={78} />
          </div>
        </div>
        {/* sparkles around the hook */}
        {[
          [-470, -120],
          [460, -130],
          [-500, 90],
          [490, 110],
          [-120, -190],
          [200, 170],
        ].map(([x, y], i) => {
          const t = ((f + i * 5) % 20) / 20;
          const s = Math.sin(t * Math.PI);
          return <Star4 key={i} size={20 + 36 * s} color={i % 2 ? '#ffd98a' : '#ffffff'} style={{position: 'absolute', left: `calc(50% + ${x}px)`, top: `calc(50% + ${y}px)`, transform: `translate(-50%, -50%) rotate(${t * 90}deg)`, opacity: 0.4 + 0.6 * s}} />;
        })}
      </div>
    </>
  );
};

// ------------------------------------------------------------------ woman

const StretchWoman: React.FC = () => {
  const f = useCurrentFrame();
  const {from, to} = LAYERS.stretchWoman;
  if (f < from || f >= to) return null;
  return (
    <div style={{position: 'absolute', left: 30, top: 1330, opacity: win(f, from, to)}}>
      <KoreanWoman height={400} pose={stretchRoutine(Math.min(63, (f - from) * 1.35))} />
    </div>
  );
};

// walks in, light dumbbell presses with light-drop sweat, then a sip of water
const RoutineWoman: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {from, to} = LAYERS.routineWoman;
  if (f < from || f >= to) return null;
  const t = f - from;
  const x = interpolate(t, [0, ROUTINE.walkUntil], [-60, 130], {...clamp, easing: Easing.out(Easing.quad)});
  const pressEnd = ROUTINE.pressFrom + ROUTINE.reps * ROUTINE.rep;
  const dbIn = t < ROUTINE.dumbbellsAt ? 0 : spring({frame: t - ROUTINE.dumbbellsAt, fps, config: {damping: 9, stiffness: 220}});
  const dbOut = interpolate(t, [pressEnd, ROUTINE.drinkFrom + 2], [1, 0], clamp);
  const bottle = t < ROUTINE.drinkFrom ? 0 : spring({frame: t - ROUTINE.drinkFrom, fps, config: {damping: 10, stiffness: 200}});
  const sweat = interpolate(t, [ROUTINE.sweatFrom, ROUTINE.sweatFrom + 6, pressEnd + 6, pressEnd + 12], [0, 1, 1, 0], clamp);
  return (
    <div style={{position: 'absolute', left: x, top: 440, opacity: win(f, from, to, 4, 8)}}>
      <KoreanWoman
        height={520}
        pose={pinkRoutine(t, ROUTINE)}
        walk={t < ROUTINE.walkUntil ? t * 0.55 : null}
        dumbbells={dbIn * dbOut}
        sweat={sweat}
        bottle={bottle}
      />
    </div>
  );
};

const RoutineIcons: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {from, to} = LAYERS.routineIcons;
  if (f < from || f >= to) return null;
  const out = interpolate(f, [to - 6, to], [1, 0], clamp);
  const fill = interpolate(f, [from + 4, from + 30], [0, 1], clamp);
  const items: [React.ReactNode, string][] = [
    [<WaterBottle3L size={68} fill={fill} />, `${(3 * fill).toFixed(1)} LITER`],
    [<Sneaker size={68} />, 'JALAN'],
    [<BalancedPlate size={74} />, 'SEIMBANG'],
  ];
  return (
    <>
      {items.map(([icon, label], i) => {
        const at = from + i * 5;
        const pop = f < at ? 0 : spring({frame: f - at, fps, config: {damping: 10, stiffness: 170}});
        return (
          <div key={i} style={{position: 'absolute', left: 650 + i * 160 - 56, top: 430 + Math.sin(f / 10 + i) * 5, opacity: out}}>
            <IconBadge size={112} pop={pop} seed={i * 2} label={label}>
              {icon}
            </IconBadge>
          </div>
        );
      })}
    </>
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

const BagIcon: React.FC<{size: number}> = ({size}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M34 36 V28 A16 16 0 0 1 66 28 V36" fill="none" stroke="#a86b10" strokeWidth={7} strokeLinecap="round" />
    <rect x="14" y="32" width="72" height="62" rx="9" fill="#ffc42a" />
    <rect x="14" y="32" width="72" height="12" rx="6" fill="#ffdc78" />
  </svg>
);

const TwoHearts: React.FC<{size: number}> = ({size}) => (
  <span style={{display: 'inline-flex', position: 'relative', width: size * 1.3, height: size}}>
    <PinkHeart size={size * 0.85} style={{position: 'absolute', left: 0, top: size * 0.12}} />
    <PinkHeart size={size * 0.7} color="#ff6fa8" style={{position: 'absolute', left: size * 0.55, top: -size * 0.04}} />
  </span>
);

// ------------------------------------------------------------------ composition

export const SccPinkEnergy: React.FC = () => {
  const L = LINES;
  return (
    <AbsoluteFill style={{backgroundColor: '#140020'}}>
      <Footage />
      {/* grading: white key light, pastel pink, pearl-white reflection at the edges */}
      <SoftLight />
      <PearlSheen />
      <GlowParticles />
      <Stars count={18} />
      <Sakura bursts={[LAYERS.sakuraBurst]} drift={6} />

      <StretchWoman />
      <LightRing cx={520} cy={830} rx={570} ry={720} from={LAYERS.ringPack.from} to={LAYERS.ringPack.to} drawFrames={16} tilt={-8} />
      <RoutineWoman />
      <RoutineIcons />
      <ButterflyFlight
        flights={[
          {from: 280, to: 345, path: [[-60, 1500], [60, 1300], [30, 1050], [110, 820], [50, 600]], size: 72, seed: 1},
          {from: 286, to: 345, path: [[1140, 1300], [990, 1150], [1010, 900], [940, 700]], size: 64, hue: 'lilac', seed: 3},
        ]}
      />
      <LightRing cx={470} cy={1000} rx={430} ry={600} from={LAYERS.ringFinal.from} to={DURATION + 10} drawFrames={24} tilt={-6} />

      {/* text: one line at a time */}
      <Hook />
      <GlassPanel cue={L.selfCare} entrance="slideRight" cx={620} cy={1560} width={780} height={230} exitAt={L.selfCare.out}>
        <DecodeText lines={[['SELF-CARE BUKAN'], ['SEKADAR SKINCARE', {icon: <Sparkles size={58} />}]]} start={L.selfCare.type} end={L.selfCare.done - 2} size={60} />
      </GlassPanel>
      <GlassPanel cue={L.kenali} entrance="open" cx={540} cy={1560} width={760} height={170} exitAt={L.kenali.out}>
        <DecodeText lines={[['KENALI SCC', {icon: <TwoHearts size={78} />}]]} start={L.kenali.type} end={L.kenali.done - 2} size={92} />
      </GlassPanel>
      <GlassPanel cue={L.bahan} entrance="scan" cx={540} cy={290} width={920} height={220} exitAt={L.bahan.out}>
        <DecodeText lines={[['WHITE KIDNEY BEAN +'], ['L-CARNITINE']]} start={L.bahan.type} end={L.bahan.done - 2} size={66} />
      </GlassPanel>
      <GlassPanel cue={L.rutin} entrance="slideRight" cx={540} cy={275} width={920} height={150} exitAt={L.rutin.out}>
        <DecodeText lines={[['RUTIN PENJAGAAN DIRI', {icon: <Blossom size={62} />}]]} start={L.rutin.type} end={L.rutin.done - 2} size={58} />
      </GlassPanel>
      <GlassPanel cue={L.cta} entrance="open" cx={540} cy={300} width={940} height={160}>
        <DecodeText lines={[['NAK TAHU LEBIH LANJUT?', {icon: <BagIcon size={64} />}]]} start={L.cta.type} end={L.cta.done - 2} size={56} />
      </GlassPanel>

      {/* sound: music from frame 0, SFX on cue */}
      <Audio src={staticFile('audio/music.wav')} volume={MUSIC_VOLUME} />
      {SFX_CUES.map(([at, name], i) => (
        <Sequence key={i} from={at} durationInFrames={50} layout="none">
          <Audio src={staticFile(`audio/${name}.wav`)} volume={SFX_VOLUME[name]} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
