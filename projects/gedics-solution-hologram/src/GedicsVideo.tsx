import React from 'react';
import {AbsoluteFill, Audio, Easing, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {FloatingHearts, GlowParticles, RainbowSweep, Rainbow, RomanticLight, Stars} from './components/Atmosphere';
import {Couple} from './components/Couple';
import {DecodeText} from './components/DecodeText';
import {GlassPanel} from './components/GlassPanel';
import {Gift, HeartOutline, PinkHeart, RainbowIcon, RedHeart, ShoppingBag, Sparkles, Star4, TwinHearts} from './components/Icons';
import {loadFonts} from './theme';
import {DURATION, MUSIC_VOLUME, PANELS, SCENES, SFX_CUES, SFX_VOLUME} from './timeline';

loadFonts();

// ------------------------------------------------------------------ footage

// The original clip is the base layer. It is only trimmed, denoised and
// lightly brightened (scripts/prep_footage.sh); the pack is never covered,
// recoloured or replaced. A slow push-in keeps it the focus.
const Footage: React.FC = () => {
  const f = useCurrentFrame();
  const scale = interpolate(f, [0, DURATION], [1, 1.04]);
  return (
    <AbsoluteFill style={{transform: `scale(${scale})`, transformOrigin: '50% 40%'}}>
      <OffthreadVideo src={staticFile('footage.mp4')} muted style={{width: '100%', height: '100%', filter: 'contrast(1.04) saturate(1.03)'}} />
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ helpers

const PANEL_W = 900;
const LOW_CX = 500; // lower panels sit left of TikTok's right-hand buttons
const LOW_CY = 1375;

const Row: React.FC<{children: React.ReactNode}> = ({children}) => (
  <div style={{display: 'flex', alignItems: 'center', gap: 22, padding: '0 26px'}}>{children}</div>
);

const appear = (f: number, at: number, len = 10) =>
  interpolate(f, [at, at + len], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

// ------------------------------------------------------------------ scene 2 gift

const GiftBurst: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const at = 78;
  if (f < at || f >= SCENES.s2.to) return null;
  const s = spring({frame: f - at, fps, config: {damping: 9, stiffness: 160}});
  const lid = interpolate(f, [84, 92], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.back(2))});
  const out = interpolate(f, [SCENES.s2.to - 6, SCENES.s2.to], [1, 0], {extrapolateLeft: 'clamp'});
  const cx = 915;
  const cy = 290;
  return (
    <div style={{position: 'absolute', left: 0, top: 0, opacity: out}}>
      {/* glow behind the box */}
      <div style={{position: 'absolute', left: cx - 130, top: cy - 130, width: 260, height: 260, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,120,200,0.55), transparent 70%)', transform: `scale(${s})`}} />
      <div style={{position: 'absolute', left: cx - 75, top: cy - 75, transform: `scale(${s}) rotate(${(1 - s) * -20}deg)`}}>
        <Gift size={150} lid={lid} />
      </div>
      {/* sparkle burst as the lid opens */}
      {Array.from({length: 10}, (_, i) => {
        const p = interpolate(f, [84, 104], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
        const a = (i / 10) * Math.PI * 2;
        const r = 30 + p * 120;
        return (
          <Star4
            key={i}
            size={22 + (i % 3) * 10}
            color={i % 2 ? '#ffd98a' : '#fff'}
            style={{position: 'absolute', left: cx + Math.cos(a) * r - 15, top: cy - 20 + Math.sin(a) * r * 0.8 - 15, opacity: p > 0 ? Math.sin(p * Math.PI) : 0}}
          />
        );
      })}
      {/* two glowing hearts rising out of the box */}
      {[0, 1].map((i) => {
        const p = interpolate(f, [88 + i * 5, 118], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        if (p <= 0) return null;
        const H = i ? RedHeart : PinkHeart;
        return (
          <div key={i} style={{position: 'absolute', left: cx - 30 + (i ? 30 : -34), top: cy - 70 - p * 120, opacity: Math.min(1, p * 4) * (1 - p * 0.3), transform: `scale(${0.5 + p * 0.6}) rotate(${(i ? 1 : -1) * 10}deg)`}}>
            <H size={64} />
          </div>
        );
      })}
    </div>
  );
};

// ------------------------------------------------------------------ scene 3 orbit

const OrbitHearts: React.FC<{layer: 'back' | 'front'}> = ({layer}) => {
  const f = useCurrentFrame();
  const {from, to} = SCENES.s3;
  if (f < from + 18 || f >= to) return null;
  const a0 = appear(f, from + 18, 12) * interpolate(f, [to - 8, to], [1, 0], {extrapolateLeft: 'clamp'});
  return (
    <>
      {Array.from({length: 6}, (_, i) => {
        const ang = (f - from) / 14 + (i / 6) * Math.PI * 2;
        const depth = Math.sin(ang);
        if ((layer === 'front') !== depth > 0) return null;
        const x = LOW_CX + Math.cos(ang) * 500;
        const y = LOW_CY + depth * 150 - 10;
        const s = 0.75 + 0.35 * depth;
        return (
          <div key={i} style={{position: 'absolute', left: x - 30, top: y - 30, transform: `scale(${s})`, opacity: a0 * (0.65 + 0.35 * depth)}}>
            <PinkHeart size={60} color={i % 3 === 0 ? '#ff5d8f' : undefined} />
          </div>
        );
      })}
    </>
  );
};

// ------------------------------------------------------------------ composition

export const GedicsVideo: React.FC = () => {
  const f = useCurrentFrame();
  const p = PANELS;
  return (
    <AbsoluteFill style={{backgroundColor: '#12001a'}}>
      <Footage />
      <RomanticLight />
      <Rainbow from={124} to={SCENES.s3.to + 30} />
      <GlowParticles />
      <Stars amount={1} />
      <FloatingHearts amount={f < SCENES.s2.from ? 1 : 0.7} />

      {/* scene 1: BAHAGIA ITU BILA SALING MENGHARGAI */}
      <GlassPanel cue={p.s1} entrance="open" cx={LOW_CX} cy={LOW_CY} width={PANEL_W} height={260} exitAt={SCENES.s1.to}>
        <Row>
          <div style={{position: 'relative'}}>
            <HeartOutline size={190} progress={appear(f, 6, 24)} style={{position: 'absolute', left: -14, top: -10}} />
            <Couple pose="hug" size={170} appear={appear(f, 8, 16)} />
          </div>
          <DecodeText lines={[['BAHAGIA ITU BILA'], ['SALING MENGHARGAI', {icon: <PinkHeart size={52} />}]]} start={p.s1.type} end={p.s1.done - 2} size={52} />
        </Row>
      </GlassPanel>

      {/* scene 2: KEJUTAN UNTUK ORANG RUMAH */}
      <GiftBurst />
      <GlassPanel cue={p.s2} entrance="slideRight" cx={LOW_CX} cy={LOW_CY} width={PANEL_W} height={260} exitAt={SCENES.s2.to}>
        <Row>
          <Couple pose="hands" size={170} appear={appear(f, p.s2.open, 14)} />
          <DecodeText
            lines={[['KEJUTAN UNTUK'], ['ORANG RUMAH', {icon: <Gift size={54} />}, {icon: <RedHeart size={50} />}]]}
            start={p.s2.type}
            end={p.s2.done - 2}
            size={56}
          />
        </Row>
      </GlassPanel>

      {/* scene 3: WARNA-WARNI KASIH SAYANG */}
      <OrbitHearts layer="back" />
      <GlassPanel cue={p.s3} entrance="scan" cx={LOW_CX} cy={LOW_CY} width={PANEL_W} height={260} exitAt={SCENES.s3.to}>
        <Row>
          <Couple pose="sitting" size={170} appear={appear(f, p.s3.open + 6, 14)} />
          <DecodeText
            lines={[['WARNA-WARNI'], ['KASIH SAYANG', {icon: <RainbowIcon size={64} />}, {icon: <Sparkles size={50} />}]]}
            start={p.s3.type}
            end={p.s3.done - 2}
            size={58}
          />
        </Row>
      </GlassPanel>
      <OrbitHearts layer="front" />

      {/* scene 4: two panels around the product */}
      <GlassPanel cue={p.s4a} entrance="open" cx={540} cy={278} width={880} height={170}>
        <DecodeText lines={[['KENALI'], ['GEDICS SOLUTION', {icon: <PinkHeart size={54} />}]]} start={p.s4a.type} end={p.s4a.done - 2} size={54} />
      </GlassPanel>
      <GlassPanel cue={p.s4b} entrance="scan" cx={LOW_CX} cy={1400} width={840} height={150}>
        <Row>
          <TwinHearts size={62} />
          <DecodeText lines={[['KETAHUI LEBIH LANJUT', {icon: <ShoppingBag size={58} />}]]} start={p.s4b.type} end={p.s4b.done - 2} size={50} />
        </Row>
      </GlassPanel>

      {/* rainbow light transitions between scenes */}
      <RainbowSweep at={SCENES.s2.from} />
      <RainbowSweep at={SCENES.s3.from} />
      <RainbowSweep at={SCENES.s4.from} />

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
