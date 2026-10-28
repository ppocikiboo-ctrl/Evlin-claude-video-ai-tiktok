import React from 'react';
import {AbsoluteFill, Audio, Easing, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {FloatingHearts, GlowParticles, LightRing, SoftLight, Stars} from './components/Atmosphere';
import {ButterflyFlight} from './components/Butterfly';
import {IconBadge, KidneyBean, Lotus, Molecule, Sneaker, WaterBottle} from './components/CareIcons';
import {DecodeText} from './components/DecodeText';
import {GlassPanel} from './components/GlassPanel';
import {HeartOutline, PinkHeart, Sparkles, Star4} from './components/Icons';
import {Woman} from './components/Woman';
import {FONT, loadFonts} from './theme';
import {DURATION, MUSIC_VOLUME, PANELS, SCENES, SFX_CUES, SFX_VOLUME} from './timeline';

loadFonts();

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const ramp = (f: number, a: number, b: number) => interpolate(f, [a, b], [0, 1], clamp);

// ------------------------------------------------------------------ footage

// The original SCC clip, whole and unaltered apart from the light clean-up in
// scripts/prep_footage.sh. Nothing is drawn over the printed label.
const Footage: React.FC = () => {
  const f = useCurrentFrame();
  const scale = interpolate(f, [0, DURATION], [1, 1.035]);
  return (
    <AbsoluteFill style={{transform: `scale(${scale})`, transformOrigin: '45% 50%'}}>
      <OffthreadVideo src={staticFile('footage.mp4')} muted style={{width: '100%', height: '100%', filter: 'contrast(1.03)'}} />
    </AbsoluteFill>
  );
};

const Row: React.FC<{children: React.ReactNode; gap?: number}> = ({children, gap = 20}) => (
  <div style={{display: 'flex', alignItems: 'center', gap, padding: '0 24px'}}>{children}</div>
);

// ------------------------------------------------------------------ woman

// One hologram woman across the edit:
//   scene 1  builds up slowly beside the product (top right)
//   scene 2  stands in the glass panel, turning ~15° with a light ring
//   scene 4  walks slowly across the empty top-left of the frame
//   scene 5  shrinks away into sparkles so the product takes over
const WALK_FROM = 110;
const WALK_TO = 420;

const WomanTrack: React.FC = () => {
  const f = useCurrentFrame();
  if (f < 8) return null;

  if (f < SCENES.s1.to) {
    const reveal = interpolate(f, [8, 50], [0, 1], {...clamp, easing: Easing.inOut(Easing.quad)});
    const out = interpolate(f, [SCENES.s1.to - 6, SCENES.s1.to], [1, 0], clamp);
    return (
      <div style={{position: 'absolute', left: 838, top: 150}}>
        <HeartOutline size={210} progress={ramp(f, 22, 52)} style={{position: 'absolute', left: -45, top: 70, opacity: out}} />
        <Woman height={430} reveal={reveal} opacity={out} />
      </div>
    );
  }

  if (f >= SCENES.s4.from && f < SCENES.s5.from + 24) {
    const p = interpolate(f, [SCENES.s4.from, SCENES.s5.from], [0, 1], clamp);
    const x = WALK_FROM + (WALK_TO - WALK_FROM) * p;
    const walking = f < SCENES.s5.from;
    const fadeIn = ramp(f, SCENES.s4.from, SCENES.s4.from + 10);
    // scene 5: shrink to nothing and dissolve into sparkles
    const shrink = interpolate(f, [SCENES.s5.from, SCENES.s5.from + 22], [1, 0], {...clamp, easing: Easing.in(Easing.cubic)});
    const h = 440;
    const w = (h * 200) / 540;
    return (
      <div style={{position: 'absolute', left: x, top: 470}}>
        <div style={{transform: `scale(${shrink})`, transformOrigin: '50% 60%'}}>
          <Woman height={h} walk={walking ? (f - SCENES.s4.from) * 0.3 : 0} reveal={fadeIn} opacity={Math.min(1, shrink * 1.5)} turn={-12} />
        </div>
        {f >= SCENES.s5.from &&
          Array.from({length: 10}, (_, i) => {
            const q = ramp(f, SCENES.s5.from + 6, SCENES.s5.from + 24);
            const a = (i / 10) * Math.PI * 2;
            return (
              <Star4
                key={i}
                size={18 + (i % 3) * 8}
                color={i % 2 ? '#e2ccff' : '#fff'}
                style={{position: 'absolute', left: w / 2 + Math.cos(a) * q * 140 - 12, top: h * 0.55 + Math.sin(a) * q * 160 - 12, opacity: Math.sin(q * Math.PI)}}
              />
            );
          })}
      </div>
    );
  }
  return null;
};

// ------------------------------------------------------------------ scene pieces

const FloatAround: React.FC<{from: number; to: number; spots: [number, number, 'heart' | 'star'][]}> = ({from, to, spots}) => {
  const f = useCurrentFrame();
  if (f < from || f >= to) return null;
  const out = interpolate(f, [to - 6, to], [1, 0], clamp);
  return (
    <>
      {spots.map(([x, y, kind], i) => {
        const a = ramp(f, from + i * 3, from + i * 3 + 10) * out;
        const bob = Math.sin(f / 10 + i) * 10;
        return (
          <div key={i} style={{position: 'absolute', left: x, top: y + bob, opacity: a, transform: `scale(${0.6 + 0.4 * a})`}}>
            {kind === 'heart' ? <PinkHeart size={46} /> : <Star4 size={34} color="#fff" />}
          </div>
        );
      })}
    </>
  );
};

const SelfCareSymbol: React.FC = () => {
  const f = useCurrentFrame();
  const from = 176;
  if (f < from || f >= SCENES.s3.to) return null;
  const out = interpolate(f, [SCENES.s3.to - 8, SCENES.s3.to], [1, 0], clamp);
  return (
    <div style={{position: 'absolute', left: 880 - 70, top: 470 - 76, opacity: out}}>
      <Lotus size={140} draw={ramp(f, from + 4, from + 26)} />
    </div>
  );
};

const CareIconsRow: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {from, to} = SCENES.s4;
  if (f < from || f >= to) return null;
  const out = interpolate(f, [to - 6, to], [1, 0], clamp);
  const items: [number, React.ReactNode][] = [
    [620, <WaterBottle size={66} />],
    [780, <Sneaker size={72} />],
    [940, <PinkHeart size={58} />],
  ];
  return (
    <>
      {items.map(([x, icon], i) => {
        const at = from + 12 + i * 8;
        const pop = f < at ? 0 : spring({frame: f - at, fps, config: {damping: 10, stiffness: 170}});
        return (
          <div key={i} style={{position: 'absolute', left: x - 60, top: 410 + Math.sin(f / 11 + i) * 6, opacity: out}}>
            <IconBadge size={120} pop={pop} seed={i * 2}>
              {icon}
            </IconBadge>
          </div>
        );
      })}
    </>
  );
};

// ------------------------------------------------------------------ composition

export const SccVideo: React.FC = () => {
  const f = useCurrentFrame();
  const p = PANELS;
  const s2Turn = interpolate(f, [SCENES.s2.from, SCENES.s2.to], [0, 15], {...clamp, easing: Easing.inOut(Easing.sin)});
  return (
    <AbsoluteFill style={{backgroundColor: '#140020'}}>
      <Footage />
      <SoftLight />
      <GlowParticles />
      <Stars />
      <FloatingHearts amount={0.8} />

      {/* 1: SELF-CARE BUKAN SEKADAR SKINCARE! */}
      <GlassPanel cue={p.s1} entrance="open" cx={410} cy={288} width={720} height={200} exitAt={SCENES.s1.to}>
        <DecodeText lines={[['SELF-CARE BUKAN'], ['SEKADAR SKINCARE!', {icon: <PinkHeart size={50} />}]]} start={p.s1.type} end={p.s1.done - 2} size={50} />
      </GlassPanel>

      {/* 2: JANGAN LUPA PENJAGAAN BADAN */}
      <FloatAround
        from={70}
        to={SCENES.s2.to}
        spots={[
          [40, 1320, 'heart'],
          [150, 1290, 'star'],
          [880, 1300, 'heart'],
          [980, 1340, 'star'],
        ]}
      />
      <GlassPanel cue={p.s2} entrance="slideRight" cx={500} cy={1515} width={900} height={250} exitAt={SCENES.s2.to}>
        <Row gap={34}>
          <Woman height={220} turn={s2Turn} ring={ramp(f, p.s2.open, p.s2.open + 10)} />
          <DecodeText lines={[['JANGAN LUPA'], ['PENJAGAAN BADAN', {icon: <Sparkles size={50} />}]]} start={p.s2.type} end={p.s2.done - 2} size={54} />
        </Row>
      </GlassPanel>

      {/* 3: KENALI SCC + ingredient panels */}
      <GlassPanel cue={p.s3} entrance="scan" cx={540} cy={250} width={860} height={190} exitAt={SCENES.s3.to}>
        <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6}}>
          <DecodeText lines={[['KENALI SCC', {icon: <PinkHeart size={60} />}]]} start={p.s3.type} end={p.s3.done - 6} size={66} />
          <div
            style={{
              fontFamily: FONT,
              fontWeight: 600,
              fontSize: 32,
              color: '#fff',
              opacity: ramp(f, p.s3.done - 6, p.s3.done + 4),
              textShadow: '0 0 10px rgba(200,160,255,0.9), 0 2px 4px rgba(30,0,40,0.7)',
            }}
          >
            White Kidney Bean + L-Carnitine Candy
          </div>
        </div>
      </GlassPanel>
      <GlassPanel cue={p.s3a} entrance="scan" cx={280} cy={1515} width={430} height={140} exitAt={SCENES.s3.to}>
        <Row gap={14}>
          <KidneyBean size={62} />
          <DecodeText lines={[['WHITE KIDNEY'], ['BEAN']]} start={p.s3a.type} end={p.s3a.done} size={36} align="left" />
        </Row>
      </GlassPanel>
      <GlassPanel cue={p.s3b} entrance="scan" cx={745} cy={1515} width={410} height={140} exitAt={SCENES.s3.to}>
        <Row gap={14}>
          <Molecule size={64} />
          <DecodeText lines={[['L-CARNITINE']]} start={p.s3b.type} end={p.s3b.done} size={38} align="left" />
        </Row>
      </GlassPanel>
      <LightRing cx={880} cy={470} rx={100} ry={100} from={176} to={SCENES.s3.to} />
      <SelfCareSymbol />

      {/* 4: JADIKAN SELF-CARE SATU RUTIN */}
      <GlassPanel cue={p.s4} entrance="open" cx={540} cy={262} width={900} height={180} exitAt={SCENES.s4.to}>
        <DecodeText
          lines={[['JADIKAN SELF-CARE'], ['SATU RUTIN', {icon: <PinkHeart size={46} />}, {icon: <PinkHeart size={38} color="#ff6fa8" />}]]}
          start={p.s4.type}
          end={p.s4.done - 2}
          size={54}
        />
      </GlassPanel>
      <CareIconsRow />

      <WomanTrack />

      {/* 5: SCC – KENALI PRODUK INI */}
      <GlassPanel cue={p.s5} entrance="open" cx={540} cy={292} width={900} height={150}>
        <DecodeText lines={[['SCC – KENALI PRODUK INI', {icon: <Sparkles size={52} />}]]} start={p.s5.type} end={p.s5.done - 2} size={52} />
      </GlassPanel>
      <LightRing cx={470} cy={1000} rx={430} ry={600} from={300} to={DURATION + 10} drawFrames={30} tilt={-6} />

      <ButterflyFlight
        flights={[
          // scene 3: around the self-care symbol, top right
          {from: 168, to: 240, path: [[1120, 820], [960, 640], [760, 560], [700, 380], [880, 300], [1000, 420], [1140, 300]], size: 76, seed: 0},
          {from: 178, to: 250, path: [[-60, 900], [80, 760], [60, 520], [200, 420], [120, 300], [-80, 250]], size: 62, hue: 'lilac', seed: 2},
          // scene 5: slow flights down the sides, clear of the product
          {from: 278, to: 345, path: [[-60, 1500], [60, 1300], [30, 1050], [110, 820], [50, 600], [140, 420]], size: 70, seed: 1},
          {from: 290, to: 345, path: [[1140, 1300], [990, 1150], [1010, 900], [940, 700], [1010, 520]], size: 64, hue: 'lilac', seed: 3},
        ]}
      />

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
