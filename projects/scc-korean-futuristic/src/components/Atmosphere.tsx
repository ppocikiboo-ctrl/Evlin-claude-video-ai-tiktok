// Light and particle layers: white + pastel-purple grading light, twinkling
// stars, floating hearts at the edges, soft glow particles, and light rings.
import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame} from 'remotion';
import {HEIGHT, WIDTH} from '../timeline';
import {PinkHeart, Star4} from './Icons';

export const SoftLight: React.FC = () => {
  const f = useCurrentFrame();
  const breathe = 0.85 + 0.15 * Math.sin(f / 22);
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {/* white key light from the top */}
      <AbsoluteFill
        style={{
          background: 'radial-gradient(ellipse 70% 32% at 50% 0%, rgba(255,255,255,0.42), rgba(235,220,255,0.12) 55%, transparent 75%)',
          mixBlendMode: 'screen',
          opacity: breathe,
        }}
      />
      {/* pastel purple from the bottom corners */}
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(ellipse 60% 30% at 0% 100%, rgba(190,150,255,0.45), transparent 70%), radial-gradient(ellipse 60% 30% at 100% 100%, rgba(255,150,220,0.38), transparent 70%)',
          mixBlendMode: 'screen',
        }}
      />
      {/* lavender soft-light around the edges, centre left clean for the product */}
      <AbsoluteFill
        style={{
          background: 'radial-gradient(ellipse 70% 55% at 50% 45%, transparent 55%, rgba(205,170,255,0.6) 100%)',
          mixBlendMode: 'soft-light',
        }}
      />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(25,5,40,0.3) 0%, transparent 16%, transparent 70%, rgba(25,5,40,0.35) 100%)'}} />
    </AbsoluteFill>
  );
};

const STARS = Array.from({length: 44}, (_, i) => ({
  x: random(`sx${i}`) * WIDTH,
  y: random(`sy${i}`) * HEIGHT,
  size: 10 + random(`ss${i}`) * 24,
  speed: 0.12 + random(`sp${i}`) * 0.2,
  phase: random(`ph${i}`) * Math.PI * 2,
  lilac: random(`sg${i}`) < 0.45,
}));

export const Stars: React.FC = () => {
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
            color={s.lilac ? '#e2ccff' : '#ffffff'}
            style={{position: 'absolute', left: s.x, top: s.y, opacity: tw * appear, transform: `rotate(${f * 2 + i * 20}deg)`}}
          />
        );
      })}
    </AbsoluteFill>
  );
};

const HEARTS = Array.from({length: 12}, (_, i) => {
  const side = i % 2 === 0;
  return {
    x: side ? 15 + random(`hx${i}`) * 140 : 900 + random(`hx${i}`) * 140,
    size: 30 + random(`hs${i}`) * 40,
    speed: 2 + random(`hv${i}`) * 2.5,
    offset: random(`ho${i}`) * HEIGHT,
    sway: 10 + random(`hw${i}`) * 22,
    phase: random(`hp${i}`) * 6,
  };
});

export const FloatingHearts: React.FC<{amount?: number}> = ({amount = 1}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {HEARTS.map((h, i) => {
        const y = HEIGHT + 100 - ((h.offset + f * h.speed) % (HEIGHT + 200));
        const x = h.x + Math.sin(f / 18 + h.phase) * h.sway;
        return (
          <div key={i} style={{position: 'absolute', left: x, top: y, opacity: 0.5 * amount, transform: `rotate(${Math.sin(f / 15 + h.phase) * 12}deg)`}}>
            <PinkHeart size={h.size} />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const DOTS = Array.from({length: 36}, (_, i) => ({
  x: random(`dx${i}`) * WIDTH,
  y: random(`dy${i}`) * HEIGHT,
  r: 4 + random(`dr${i}`) * 8,
  vy: 0.6 + random(`dv${i}`) * 1.4,
  lilac: random(`dg${i}`) < 0.5,
  phase: random(`dp${i}`) * 6,
}));

export const GlowParticles: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {DOTS.map((d, i) => {
        const y = (d.y - f * d.vy + HEIGHT) % HEIGHT;
        const c = d.lilac ? '215,190,255' : '255,255,255';
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
              opacity: 0.45 + 0.45 * Math.sin(f / 9 + d.phase),
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// A glowing ellipse that draws itself, with sparkles riding along it.
export const LightRing: React.FC<{cx: number; cy: number; rx: number; ry: number; from: number; to: number; drawFrames?: number; tilt?: number}> = ({
  cx,
  cy,
  rx,
  ry,
  from,
  to,
  drawFrames = 24,
  tilt = 0,
}) => {
  const f = useCurrentFrame();
  if (f < from || f > to) return null;
  const draw = interpolate(f, [from, from + drawFrames], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const fade = interpolate(f, [to - 8, to], [1, 0], {extrapolateLeft: 'clamp'});
  const spin = (f - from) / 30;
  return (
    <AbsoluteFill style={{pointerEvents: 'none', opacity: fade}}>
      <svg width={WIDTH} height={HEIGHT} style={{position: 'absolute', overflow: 'visible'}}>
        <g transform={`rotate(${tilt} ${cx} ${cy})`}>
          <ellipse
            cx={cx}
            cy={cy}
            rx={rx}
            ry={ry}
            fill="none"
            stroke="#ff8fd6"
            strokeWidth={4}
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - draw}
            style={{filter: 'drop-shadow(0 0 6px #ff6fcf) drop-shadow(0 0 16px #c9a6ff)'}}
          />
          <ellipse cx={cx} cy={cy} rx={rx} ry={ry} fill="none" stroke="#fff" strokeWidth={1.5} opacity={0.7 * draw} />
          {draw >= 1 &&
            [0, 1, 2, 3].map((k) => {
              const a = spin + (k / 4) * Math.PI * 2;
              return <circle key={k} cx={cx + Math.cos(a) * rx} cy={cy + Math.sin(a) * ry} r={7} fill="#fff" style={{filter: 'drop-shadow(0 0 8px #ff6fcf)'}} />;
            })}
        </g>
      </svg>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- pearl sheen

// Slow pearlescent reflection (white -> pink -> lavender) drifting across the
// edges of the frame; the centre, where the product is, stays clean.
export const PearlSheen: React.FC = () => {
  const f = useCurrentFrame();
  const x = -40 + ((f / 3) % 180);
  return (
    <AbsoluteFill
      style={{
        pointerEvents: 'none',
        mixBlendMode: 'screen',
        opacity: 0.32,
        background: `linear-gradient(120deg, transparent ${x - 30}%, rgba(255,255,255,0.9) ${x - 10}%, rgba(255,190,225,0.8) ${x}%, rgba(205,185,255,0.8) ${x + 10}%, transparent ${x + 30}%)`,
        WebkitMaskImage: 'radial-gradient(ellipse 52% 40% at 48% 52%, transparent 60%, #000 100%)',
        maskImage: 'radial-gradient(ellipse 52% 40% at 48% 52%, transparent 60%, #000 100%)',
      }}
    />
  );
};

// ---------------------------------------------------------------- sakura

const Petal: React.FC<{size: number; flip: number}> = ({size, flip}) => (
  <svg width={size} height={size} viewBox="-50 -50 100 100" style={{overflow: 'visible', transform: `scaleX(${flip})`}}>
    <defs>
      <radialGradient id="petalGrad" cx="0.5" cy="0.8" r="0.9">
        <stop offset="0" stopColor="#ffffff" />
        <stop offset="0.5" stopColor="#ffd3e6" />
        <stop offset="1" stopColor="#ff9cc6" />
      </radialGradient>
    </defs>
    {/* sakura petal: rounded with a small notch at the tip */}
    <path d="M0 46 C-30 30 -40 -10 -18 -40 Q-8 -46 0 -36 Q8 -46 18 -40 C40 -10 30 30 0 46 Z" fill="url(#petalGrad)" opacity={0.92} />
  </svg>
);

type PetalSpec = {x: number; y: number; size: number; vy: number; vx: number; spin: number; phase: number};

const edgeX = (r: number) => (r < 0.5 ? r * 2 * 230 : 850 + (r - 0.5) * 2 * 230);

const DRIFT: PetalSpec[] = Array.from({length: 14}, (_, i) => ({
  x: edgeX(random(`px${i}`)),
  y: random(`py${i}`) * HEIGHT,
  size: 22 + random(`ps${i}`) * 22,
  vy: 1.6 + random(`pv${i}`) * 1.6,
  vx: 0.4 + random(`pw${i}`) * 0.8,
  spin: 2 + random(`pr${i}`) * 4,
  phase: random(`pp${i}`) * 6,
}));

const PetalAt: React.FC<{p: PetalSpec; x: number; y: number; f: number; alpha: number}> = ({p, x, y, f, alpha}) => (
  <div style={{position: 'absolute', left: x, top: y, opacity: alpha, transform: `rotate(${f * p.spin + p.phase * 50}deg)`, filter: 'drop-shadow(0 0 6px rgba(255,170,210,0.8))'}}>
    <Petal size={p.size} flip={Math.cos(f / 8 + p.phase)} />
  </div>
);

// Gentle continuous petal drift along the edges, plus bursts on cue.
export const Sakura: React.FC<{bursts: {from: number; to: number}[]}> = ({bursts}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {DRIFT.map((p, i) => {
        const y = ((p.y + f * p.vy) % (HEIGHT + 100)) - 50;
        const x = p.x + Math.sin(f / 20 + p.phase) * 30 + f * p.vx * 0.3;
        return <PetalAt key={i} p={p} x={x} y={y} f={f} alpha={0.75} />;
      })}
      {bursts.map((b, bi) => {
        if (f < b.from || f > b.to) return null;
        const t = f - b.from;
        const fade = interpolate(f, [b.to - 12, b.to], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return Array.from({length: 16}, (_, i) => {
          const r = random(`b${bi}-${i}`);
          const p: PetalSpec = {x: edgeX(r), y: -40 - random(`by${bi}-${i}`) * 260, size: 24 + random(`bs${bi}-${i}`) * 22, vy: 6 + random(`bv${bi}-${i}`) * 5, vx: 0, spin: 3 + random(`br${bi}-${i}`) * 4, phase: r * 6};
          const y = p.y + t * p.vy;
          const x = p.x + Math.sin(t / 10 + p.phase) * 40;
          return <PetalAt key={`${bi}-${i}`} p={p} x={x} y={y} f={f} alpha={fade * Math.min(1, t / 6)} />;
        });
      })}
    </AbsoluteFill>
  );
};
