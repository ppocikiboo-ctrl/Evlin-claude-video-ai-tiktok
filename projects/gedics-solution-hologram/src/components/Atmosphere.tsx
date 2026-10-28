// Romantic atmosphere layered over the footage: grading light, twinkling
// stars, floating hologram hearts, gold/pink particles, the pastel rainbow
// and the rainbow light transitions between scenes.
import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame} from 'remotion';
import {HEIGHT, WIDTH} from '../timeline';
import {PinkHeart, Star4} from './Icons';

// ---------------------------------------------------------------- grading light

export const RomanticLight: React.FC = () => {
  const f = useCurrentFrame();
  const breathe = 0.85 + 0.15 * Math.sin(f / 20);
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {/* golden sunlight from the top-left */}
      <AbsoluteFill
        style={{
          background: 'radial-gradient(ellipse 75% 45% at 0% 0%, rgba(255,205,130,0.55), rgba(255,170,120,0.18) 45%, transparent 70%)',
          mixBlendMode: 'screen',
          opacity: breathe,
        }}
      />
      {/* soft pink glow from below and the right edge */}
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(ellipse 80% 30% at 50% 100%, rgba(255,90,180,0.5), transparent 70%), radial-gradient(ellipse 30% 50% at 100% 60%, rgba(255,120,200,0.28), transparent 70%)',
          mixBlendMode: 'screen',
        }}
      />
      {/* warm pink edges, centre left clean for the product */}
      <AbsoluteFill
        style={{
          background: 'radial-gradient(ellipse 70% 55% at 50% 42%, transparent 55%, rgba(255,110,190,0.55) 100%)',
          mixBlendMode: 'soft-light',
        }}
      />
      {/* gentle darkening behind the lower panels for text contrast */}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(25,0,25,0.25) 0%, transparent 14%, transparent 58%, rgba(30,0,30,0.45) 100%)'}} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- stars

const STARS = Array.from({length: 46}, (_, i) => ({
  x: random(`sx${i}`) * WIDTH,
  y: random(`sy${i}`) * HEIGHT,
  size: 10 + random(`ss${i}`) * 26,
  speed: 0.12 + random(`sp${i}`) * 0.2,
  phase: random(`ph${i}`) * Math.PI * 2,
  gold: random(`sg${i}`) < 0.55,
}));

export const Stars: React.FC<{amount: number}> = ({amount}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {STARS.map((s, i) => {
        const tw = Math.max(0, Math.sin(f * s.speed + s.phase));
        const appear = interpolate(f, [i * 0.6, i * 0.6 + 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return (
          <Star4
            key={i}
            size={s.size * (0.4 + 0.6 * tw)}
            color={s.gold ? '#ffd98a' : '#ffffff'}
            style={{position: 'absolute', left: s.x, top: s.y, opacity: tw * amount * appear, transform: `rotate(${f * 2 + i * 20}deg)`}}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- hearts

const HEARTS = Array.from({length: 16}, (_, i) => {
  // mostly along the left/right edges so the product stays clear
  const side = i % 2 === 0;
  const x = side ? 20 + random(`hx${i}`) * 170 : 860 + random(`hx${i}`) * 170;
  return {
    x,
    size: 34 + random(`hs${i}`) * 50,
    speed: 2.2 + random(`hv${i}`) * 2.8,
    offset: random(`ho${i}`) * HEIGHT,
    sway: 10 + random(`hw${i}`) * 26,
    phase: random(`hp${i}`) * 6,
  };
});

export const FloatingHearts: React.FC<{amount: number}> = ({amount}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {HEARTS.map((h, i) => {
        const y = HEIGHT + 100 - ((h.offset + f * h.speed) % (HEIGHT + 200));
        const x = h.x + Math.sin(f / 18 + h.phase) * h.sway;
        return (
          <div key={i} style={{position: 'absolute', left: x, top: y, opacity: 0.55 * amount, transform: `rotate(${Math.sin(f / 15 + h.phase) * 12}deg)`}}>
            <PinkHeart size={h.size} />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- particles

const DOTS = Array.from({length: 40}, (_, i) => ({
  x: random(`dx${i}`) * WIDTH,
  y: random(`dy${i}`) * HEIGHT,
  r: 4 + random(`dr${i}`) * 9,
  vy: 0.6 + random(`dv${i}`) * 1.6,
  gold: random(`dg${i}`) < 0.5,
  phase: random(`dp${i}`) * 6,
}));

export const GlowParticles: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {DOTS.map((d, i) => {
        const y = (d.y - f * d.vy + HEIGHT) % HEIGHT;
        const c = d.gold ? '255,214,140' : '255,140,210';
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: d.x + Math.sin(f / 25 + d.phase) * 14,
              top: y,
              width: d.r * 2,
              height: d.r * 2,
              borderRadius: '50%',
              background: `radial-gradient(circle, rgba(${c},0.95), rgba(${c},0) 70%)`,
              opacity: 0.5 + 0.5 * Math.sin(f / 9 + d.phase),
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- rainbow

const PASTEL = ['#ffa8cf', '#ffc9a3', '#fff0a6', '#b4f0cf', '#acd8ff', '#cdb6ff'];

// Pastel rainbow that rises from behind the lower panel; a light shimmer
// travels along it.
export const Rainbow: React.FC<{from: number; to: number}> = ({from, to}) => {
  const f = useCurrentFrame();
  if (f < from || f > to) return null;
  const draw = interpolate(f, [from, from + 30], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const fade = interpolate(f, [to - 10, to], [1, 0], {extrapolateLeft: 'clamp'});
  const shimmer = ((f - from) % 45) / 45;
  const cx = 540;
  const cy = 1590;
  return (
    <AbsoluteFill style={{pointerEvents: 'none', opacity: 0.75 * fade}}>
      <svg width={WIDTH} height={HEIGHT} style={{position: 'absolute', filter: 'blur(1.5px)'}}>
        <defs>
          <linearGradient id="rbShimmer" x1="0" y1="0" x2="1" y2="0">
            <stop offset={Math.max(0, shimmer - 0.12)} stopColor="#fff" stopOpacity="0" />
            <stop offset={shimmer} stopColor="#fff" stopOpacity="0.85" />
            <stop offset={Math.min(1, shimmer + 0.12)} stopColor="#fff" stopOpacity="0" />
          </linearGradient>
        </defs>
        {PASTEL.map((c, i) => {
          const r = 470 - i * 16;
          const d = `M${cx - r} ${cy} A${r} ${r} 0 0 1 ${cx + r} ${cy}`;
          return (
            <g key={c}>
              <path d={d} fill="none" stroke={c} strokeWidth={16} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} />
              <path d={d} fill="none" stroke="url(#rbShimmer)" strokeWidth={16} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} style={{mixBlendMode: 'screen'}} />
            </g>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};

// Quick pastel light sweep used as the scene transition.
export const RainbowSweep: React.FC<{at: number}> = ({at}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [at - 5, at + 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (p <= 0 || p >= 1) return null;
  const x = -60 + p * 220;
  return (
    <AbsoluteFill
      style={{
        pointerEvents: 'none',
        mixBlendMode: 'screen',
        opacity: Math.sin(p * Math.PI) * 0.45, // brief, so the pack's colour is never washed out for long
        background: `linear-gradient(115deg, transparent ${x - 30}%, ${PASTEL.map((c, i) => `${c} ${x - 18 + i * 6}%`).join(', ')}, transparent ${x + 30}%)`,
      }}
    />
  );
};
