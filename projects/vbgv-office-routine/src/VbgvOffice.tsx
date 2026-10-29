import React from 'react';
import {AbsoluteFill, Audio, Easing, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {GlowParticles, PearlSheen, SoftLight, Stars} from './components/Atmosphere';
import {DecodeText} from './components/DecodeText';
import {GlassPanel} from './components/GlassPanel';
import {PinkHeart, Sparkles, Star4} from './components/Icons';
import {ArrowDown, Drop, FastForward, Handbag, Laptop, ShopBag, Sun} from './components/VbgvIcons';
import {FONT, loadFonts} from './theme';
import {DURATION, LINES, MUSIC_VOLUME, SFX_CUES, SFX_VOLUME, SHOTS} from './timeline';

loadFonts();

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const PURPLE = '#8b3dff';
const GOLD = '#ffd98a';
const PurpleHeart: React.FC<{size: number}> = ({size}) => <PinkHeart size={size} color="#9b5de5" />;

// ------------------------------------------------------------------ footage

// The edited original footage (scripts/prep_footage.py). Only a short impact
// shake on the hook and a quick zoom punch at each cut move it.
const Footage: React.FC = () => {
  const f = useCurrentFrame();
  const amp = interpolate(f, [0, 10], [14, 0], clamp);
  let punch = 1;
  for (const s of [SHOTS.pack, SHOTS.open, SHOTS.tablet, SHOTS.water, SHOTS.closeup]) {
    if (f >= s.from && f < s.from + 6) punch = 1 + 0.05 * (1 - (f - s.from) / 6);
  }
  return (
    <AbsoluteFill style={{transform: `translate(${Math.sin(f * 2.7) * amp}px, ${Math.cos(f * 3.1) * amp}px) scale(${punch})`}}>
      <OffthreadVideo src={staticFile('footage.mp4')} muted style={{width: '100%', height: '100%'}} />
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ hook

const bigText: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 14,
  whiteSpace: 'nowrap',
  fontFamily: FONT,
  fontWeight: 900,
  lineHeight: 1.06,
  color: '#ffffff',
  WebkitTextStroke: `5px ${PURPLE}`,
  paintOrder: 'stroke fill',
  textShadow: `0 0 16px ${PURPLE}, 0 0 36px rgba(139,61,255,0.8), 0 6px 0 #3d1580, 0 10px 18px rgba(20,0,40,0.7)`,
};

// "KERJA DUDUK LAMA SEHARIAN?" — readable on frame 0, zoom punch on the BOOM,
// flash + shockwave + sparkles, over the 3x desk timelapse.
const Hook: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {out} = LINES.hook;
  if (f >= out) return null;
  const punch = 0.8 + 0.2 * spring({frame: f, fps, config: {damping: 7, stiffness: 260}});
  const pulse = f > 14 ? 1 + 0.025 * Math.exp((-(f % 15) / 15) * 5) : 1;
  const exit = interpolate(f, [out - 6, out], [1, 0], clamp);
  const exitZoom = interpolate(f, [out - 6, out], [1, 1.2], clamp);
  const flash = interpolate(f, [0, 1, 5], [0.1, 0.32, 0], clamp);
  const wave = interpolate(f, [0, 16], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  return (
    <>
      <AbsoluteFill style={{background: '#fff', opacity: flash}} />
      <div style={{position: 'absolute', left: 540, top: 285, transform: `translate(-50%, -50%) scale(${punch * pulse * exitZoom})`, opacity: exit}}>
        <div style={{position: 'absolute', left: '50%', top: '50%', width: 1100, height: 420, transform: 'translate(-50%, -50%)', background: 'radial-gradient(ellipse at center, rgba(30,0,60,0.55), rgba(30,0,60,0) 70%)'}} />
        <div
          style={{
            position: 'absolute',
            left: '50%',
            top: '50%',
            width: 420 + wave * 900,
            height: 170 + wave * 360,
            transform: 'translate(-50%, -50%)',
            borderRadius: '50%',
            border: `6px solid rgba(190,140,255,${(1 - wave) * 0.9})`,
            boxShadow: `0 0 24px rgba(139,61,255,${(1 - wave) * 0.8})`,
          }}
        />
        <div style={{position: 'relative'}}>
          <div style={{...bigText, fontSize: 92}}>
            KERJA <span style={{color: GOLD}}>DUDUK LAMA</span>
          </div>
          <div style={{...bigText, fontSize: 104}}>
            SEHARIAN? <Laptop size={96} />
          </div>
        </div>
        {[
          [-480, -110],
          [470, -120],
          [-500, 100],
          [480, 110],
        ].map(([x, y], i) => {
          const t = ((f + i * 5) % 20) / 20;
          const s = Math.sin(t * Math.PI);
          return <Star4 key={i} size={20 + 34 * s} color={i % 2 ? GOLD : '#ffffff'} style={{position: 'absolute', left: `calc(50% + ${x}px)`, top: `calc(50% + ${y}px)`, transform: `translate(-50%, -50%) rotate(${t * 90}deg)`, opacity: 0.4 + 0.6 * s}} />;
        })}
      </div>
    </>
  );
};

// "⏩ 3X" badge so the timelapse reads as intentional
const SpeedBadge: React.FC = () => {
  const f = useCurrentFrame();
  const {from, to} = SHOTS.hook;
  if (f >= to) return null;
  const a = interpolate(f, [from + 4, from + 10, to - 6, to], [0, 1, 1, 0], clamp);
  return (
    <div
      style={{
        position: 'absolute',
        right: 160,
        top: 1220,
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        padding: '8px 18px',
        borderRadius: 999,
        background: 'rgba(30,0,60,0.65)',
        border: '2px solid rgba(255,255,255,0.8)',
        opacity: a * (0.75 + 0.25 * Math.sin(f / 3)),
        fontFamily: FONT,
        fontWeight: 900,
        fontSize: 34,
        color: '#fff',
      }}
    >
      <FastForward size={30} /> 3X
    </div>
  );
};

// ------------------------------------------------------------------ product moments

const PackSparkles: React.FC = () => {
  const f = useCurrentFrame();
  const at = 100;
  if (f < at || f > at + 30) return null;
  const p = (f - at) / 30;
  return (
    <>
      {Array.from({length: 9}, (_, i) => {
        const a = (i / 9) * Math.PI * 2;
        const r = 120 + p * 220;
        return (
          <Star4
            key={i}
            size={24 + (i % 3) * 10}
            color={i % 2 ? GOLD : '#ffffff'}
            style={{position: 'absolute', left: 720 + Math.cos(a) * r - 15, top: 1080 + Math.sin(a) * r * 0.9 - 15, opacity: Math.sin(p * Math.PI)}}
          />
        );
      })}
    </>
  );
};

// brand pill under the product name
const BrandPill: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const at = 122;
  const {out} = LINES.kenali;
  if (f < at || f >= out) return null;
  const s = spring({frame: f - at, fps, config: {damping: 10, stiffness: 180}});
  const a = interpolate(f, [out - 6, out], [1, 0], clamp);
  return (
    <div
      style={{
        position: 'absolute',
        left: 540,
        top: 420,
        transform: `translate(-50%, -50%) scale(${s})`,
        opacity: a,
        padding: '10px 30px',
        borderRadius: 999,
        background: 'linear-gradient(180deg, #fff3d6, #ffd98a)',
        boxShadow: '0 5px 0 #b8892e, 0 10px 18px rgba(30,0,40,0.45)',
        fontFamily: FONT,
        fontWeight: 900,
        fontSize: 38,
        letterSpacing: 2,
        color: '#4a1a8c',
        whiteSpace: 'nowrap',
      }}
    >
      VBGV L-CARNITINE CANDY
    </div>
  );
};

const Footnote: React.FC<{text: string; from: number; to: number; top: number}> = ({text, from, to, top}) => {
  const f = useCurrentFrame();
  if (f < from || f >= to) return null;
  const a = Math.min(interpolate(f, [from, from + 8], [0, 1], clamp), interpolate(f, [to - 6, to], [1, 0], clamp));
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top, textAlign: 'center', opacity: a, fontFamily: FONT, fontWeight: 700, fontSize: 32, color: '#fff', textShadow: '0 2px 6px rgba(20,0,40,0.9)'}}>
      {text}
    </div>
  );
};

// CTA arrow bouncing toward TikTok's yellow product bag (bottom left)
const CtaArrow: React.FC = () => {
  const f = useCurrentFrame();
  const at = LINES.cta.done;
  if (f < at) return null;
  const a = interpolate(f, [at, at + 6], [0, 1], clamp);
  const bounce = Math.abs(Math.sin(((f - at) / 15) * Math.PI)) * 18;
  return (
    <div style={{position: 'absolute', left: 150, top: 1640 + bounce, opacity: a, transform: 'rotate(20deg)'}}>
      <ArrowDown size={70} />
    </div>
  );
};

// ------------------------------------------------------------------ composition

export const VbgvOffice: React.FC = () => {
  const L = LINES;
  return (
    <AbsoluteFill style={{backgroundColor: '#140020'}}>
      <Footage />
      {/* soft lavender/white light at the edges, kept light so skin stays natural */}
      <AbsoluteFill style={{opacity: 0.45}}>
        <SoftLight />
        <PearlSheen />
      </AbsoluteFill>
      <GlowParticles />
      <Stars count={14} />

      <Hook />
      <SpeedBadge />
      <GlassPanel cue={L.rutin} entrance="open" cx={540} cy={280} width={900} height={150} exitAt={L.rutin.out}>
        <DecodeText lines={[['INI RUTIN KECIL SAYA', {icon: <PurpleHeart size={60} />}]]} start={L.rutin.type} end={L.rutin.done - 2} size={62} />
      </GlassPanel>

      <PackSparkles />
      <GlassPanel cue={L.kenali} entrance="scan" cx={540} cy={270} width={720} height={170} exitAt={L.kenali.out}>
        <DecodeText lines={[['KENALI VBGV', {icon: <Sparkles size={74} />}]]} start={L.kenali.type} end={L.kenali.done - 2} size={96} />
      </GlassPanel>
      <BrandPill />

      <GlassPanel cue={L.ofis} entrance="slideRight" cx={540} cy={280} width={900} height={150} exitAt={L.ofis.out}>
        <DecodeText lines={[['SENANG BAWA KE OFIS', {icon: <Handbag size={70} />}]]} start={L.ofis.type} end={L.ofis.done - 2} size={64} />
      </GlassPanel>

      <GlassPanel cue={L.cara} entrance="open" cx={540} cy={290} width={940} height={210} exitAt={L.cara.out}>
        <DecodeText lines={[['1/2 BIJI SELEPAS'], ['SARAPAN PAGI', {icon: <Sun size={70} />}]]} start={L.cara.type} end={L.cara.done - 2} size={64} />
      </GlassPanel>
      <Footnote text="*Ikut arahan pada label produk" from={L.cara.done} to={L.cara.out} top={410} />

      <GlassPanel cue={L.air} entrance="slideRight" cx={540} cy={280} width={920} height={150} exitAt={L.air.out}>
        <DecodeText lines={[['JANGAN LUPA MINUM AIR', {icon: <Drop size={64} />}]]} start={L.air.type} end={L.air.done - 2} size={62} />
      </GlassPanel>

      <GlassPanel cue={L.cta} entrance="open" cx={540} cy={1440} width={900} height={210}>
        <DecodeText lines={[['NAK CUBA JUGA?', {icon: <ShopBag size={70} />}], ['TEKAN BEG KUNING']]} start={L.cta.type} end={L.cta.done - 2} size={68} />
      </GlassPanel>
      <CtaArrow />

      {/* sound: original audio removed; new music from frame 0 + SFX on cue */}
      <Audio src={staticFile('audio/music.wav')} volume={MUSIC_VOLUME} />
      {SFX_CUES.map(([at, name], i) => (
        <Sequence key={i} from={at} durationInFrames={50} layout="none">
          <Audio src={staticFile(`audio/${name}.wav`)} volume={SFX_VOLUME[name]} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
