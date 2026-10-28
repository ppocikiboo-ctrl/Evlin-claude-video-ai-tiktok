// Adult woman in a Korean-beauty illustration style, in modest sportswear:
// a loose long-sleeved sweatshirt, long jogger pants and sneakers. Natural,
// constant body proportions: only her pose changes (light stretches, light
// dumbbell presses), never her shape or size.
//
// variant "solid"     soft 3D shading (gradients, rim light, ground shadow)
// variant "hologram"  same figure as translucent pink light with scan lines
import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';

export type Pose = {
  lean: number; // upper-body side bend in degrees (+ = to her left / viewer's right)
  lA1: number; // left (viewer's left) upper arm, 0 = hanging down, + swings outward/up
  lA2: number; // left forearm, relative to upper arm
  rA1: number;
  rA2: number;
};

export const POSES: Record<'rest' | 'up' | 'tee' | 'goal' | 'press', Pose> = {
  rest: {lean: 0, lA1: 10, lA2: -8, rA1: -10, rA2: 8},
  up: {lean: 0, lA1: 165, lA2: 52, rA1: -165, rA2: -52}, // hands clasped overhead
  tee: {lean: 0, lA1: 88, lA2: 0, rA1: -88, rA2: 0}, // arms out to the sides
  goal: {lean: 0, lA1: 90, lA2: 90, rA1: -90, rA2: -90}, // dumbbells at shoulder height
  press: {lean: 0, lA1: 160, lA2: 20, rA1: -160, rA2: -20}, // dumbbells pressed overhead
};

const mix = (a: Pose, b: Pose, t: number): Pose => ({
  lean: a.lean + (b.lean - a.lean) * t,
  lA1: a.lA1 + (b.lA1 - a.lA1) * t,
  lA2: a.lA2 + (b.lA2 - a.lA2) * t,
  rA1: a.rA1 + (b.rA1 - a.rA1) * t,
  rA2: a.rA2 + (b.rA2 - a.rA2) * t,
});

const ease = (t: number) => (t < 0 ? 0 : t > 1 ? 1 : t * t * (3 - 2 * t));

// Light stretch routine, `t` in frames since she appeared:
//   arms up -> side bend one way -> the other way -> arms out (T) -> rest
export const stretchRoutine = (t: number): Pose => {
  if (t < 16) return mix(POSES.rest, POSES.up, ease(t / 16));
  if (t < 64) {
    const bend = Math.sin(((t - 16) / 48) * Math.PI * 2) * 13;
    return {...POSES.up, lean: bend};
  }
  if (t < 80) return mix(POSES.up, POSES.tee, ease((t - 64) / 16));
  if (t < 92) return POSES.tee;
  return mix(POSES.tee, POSES.rest, ease((t - 92) / 14));
};

// Full routine for the solid woman, `t` in frames since she appeared:
//   arms up -> side bend each way -> dumbbells to shoulders -> light presses
export const workoutRoutine = (t: number, w: {dumbbellsAt: number; pressFrom: number; rep: number; reps: number}): Pose => {
  if (t < 16) return mix(POSES.rest, POSES.up, ease(t / 16));
  if (t < 40) return {...POSES.up, lean: Math.sin(((t - 16) / 24) * Math.PI * 2) * 12};
  if (t < w.dumbbellsAt) return mix(POSES.up, POSES.rest, ease((t - 40) / (w.dumbbellsAt - 40)));
  if (t < w.pressFrom) return mix(POSES.rest, POSES.goal, ease((t - w.dumbbellsAt) / (w.pressFrom - w.dumbbellsAt)));
  const k = (t - w.pressFrom) / w.rep;
  if (k >= w.reps) return POSES.goal;
  return mix(POSES.goal, POSES.press, Math.sin((k % 1) * Math.PI));
};

// Two-bone arm IK: angles (a1, a2) that put the hand at (tx, ty), with the
// elbow bending outward. Matches Arm's convention (0 = hanging down).
const UPPER = 74;
const FORE = 76;
const deg = (r: number) => (r * 180) / Math.PI;
const dirAngle = (dx: number, dy: number) => deg(Math.atan2(-dx, dy));
export const reach = (sx: number, sy: number, tx: number, ty: number, elbowOut: 1 | -1): [number, number] => {
  const dx = tx - sx;
  const dy = ty - sy;
  const d = Math.min(Math.hypot(dx, dy), UPPER + FORE - 1);
  const alpha = deg(Math.acos((UPPER * UPPER + d * d - FORE * FORE) / (2 * UPPER * d)));
  const a1 = dirAngle(dx, dy) + elbowOut * alpha;
  const r = (a1 * Math.PI) / 180;
  const ex = sx - Math.sin(r) * UPPER;
  const ey = sy + Math.cos(r) * UPPER;
  return [a1, dirAngle(tx - ex, ty - ey) - a1];
};

// right hand (viewer's right) raises a water bottle to her mouth
const [drinkA1, drinkA2] = reach(142, 172, 128, 146, 1);
export const DRINK: Pose = {lean: 0, lA1: 10, lA2: -8, rA1: drinkA1, rA2: drinkA2};

// Light routine for the Pink Energy edit, `t` in frames since she appeared:
//   walks in -> dumbbells to shoulders -> quick light presses -> sip of water
export const pinkRoutine = (t: number, r: {dumbbellsAt: number; pressFrom: number; rep: number; reps: number; drinkFrom: number}): Pose => {
  if (t < r.dumbbellsAt) return POSES.rest;
  if (t < r.pressFrom) return mix(POSES.rest, POSES.goal, ease((t - r.dumbbellsAt) / (r.pressFrom - r.dumbbellsAt)));
  const pressEnd = r.pressFrom + r.reps * r.rep;
  if (t < pressEnd) return mix(POSES.goal, POSES.press, Math.sin((((t - r.pressFrom) / r.rep) % 1) * Math.PI));
  if (t < r.drinkFrom) return POSES.goal;
  return mix(POSES.goal, DRINK, ease((t - r.drinkFrom) / 8));
};

type Props = {
  height: number;
  pose: Pose;
  variant?: 'solid' | 'hologram';
  reveal?: number; // hologram build-up from the feet, 0..1
  opacity?: number;
  dumbbells?: number; // 0..1 pop-in scale of the dumbbells in her hands
  sweat?: number; // 0..1 intensity of the symbolic light-drop "sweat"
  energy?: number; // 0..1 visibility of the light lines circling her body
  walk?: number | null; // walk-cycle phase in radians, null = standing still
  bottle?: number; // 0..1 pop-in scale of a water bottle in her right hand
};

const VB_W = 220;
const VB_H = 580;
const PINK = '#ff7ad1';

// Light, colourful dumbbell, kept level whatever the arm angle is.
const Dumbbell: React.FC<{color: string; scale: number}> = ({color, scale}) => (
  <g transform={`scale(${scale})`}>
    <rect x={-20} y={-3.5} width={40} height={7} rx={3.5} fill="#f4f1f7" stroke="#b9a7d6" strokeWidth={1} />
    {[-1, 1].map((side) => (
      <g key={side}>
        <rect x={side * 20 - 7} y={-17} width={14} height={34} rx={6} fill={color} stroke="#fff" strokeWidth={1.6} />
        <rect x={side * 20 - 4} y={-13} width={4} height={26} rx={2} fill="#fff" opacity={0.55} />
      </g>
    ))}
  </g>
);

// Small water bottle, tilted so the cap points at her mouth when she drinks.
const HandBottle: React.FC<{scale: number}> = ({scale}) => (
  <g transform={`translate(-6 -6) rotate(-40) scale(${scale})`}>
    <rect x={-9} y={-34} width={18} height={44} rx={7} fill="#e8f7ff" stroke="#7fc4f5" strokeWidth={2} />
    <rect x={-9} y={-12} width={18} height={22} rx={6} fill="#6cc4ff" />
    <rect x={-5} y={-42} width={10} height={9} rx={2} fill="#ff8fc8" />
  </g>
);

const Arm: React.FC<{x: number; y: number; a1: number; a2: number; sleeve: string; skin: string; stroke: string; sw: number; dumbbell?: {color: string; scale: number}; bottle?: number}> = ({
  x,
  y,
  a1,
  a2,
  sleeve,
  skin,
  stroke,
  sw,
  dumbbell,
  bottle = 0,
}) => (
  <g transform={`translate(${x} ${y}) rotate(${a1})`}>
    <rect x={-12} y={-6} width={24} height={84} rx={12} fill={sleeve} stroke={stroke} strokeWidth={sw} />
    <g transform={`translate(0 74) rotate(${a2})`}>
      <rect x={-11} y={-4} width={22} height={70} rx={11} fill={sleeve} stroke={stroke} strokeWidth={sw} />
      <rect x={-11} y={56} width={22} height={10} rx={4} fill={sleeve} stroke={stroke} strokeWidth={sw} opacity={0.9} />
      <ellipse cx={0} cy={76} rx={9} ry={11} fill={skin} stroke={stroke} strokeWidth={sw} />
      {dumbbell && dumbbell.scale > 0 && (
        <g transform={`translate(0 76) rotate(${-(a1 + a2)})`}>
          <Dumbbell {...dumbbell} />
        </g>
      )}
      {bottle > 0 && (
        <g transform={`translate(0 76) rotate(${-(a1 + a2)})`}>
          <HandBottle scale={bottle} />
        </g>
      )}
    </g>
  </g>
);

export const KoreanWoman: React.FC<Props> = ({height, pose, variant = 'solid', reveal = 1, opacity = 1, dumbbells = 0, sweat = 0, energy = 0, walk = null, bottle = 0}) => {
  const f = useCurrentFrame();
  const u = React.useId().replace(/:/g, '');
  const holo = variant === 'hologram';
  const width = (height * VB_W) / VB_H;
  const flicker = holo ? 0.88 + 0.12 * Math.sin(f * 1.9) * Math.sin(f * 0.41) : 1;
  const breathe = Math.sin(f / 14) * 1.2;
  const pony = Math.sin(f / 9) * 4 - pose.lean * 0.6;
  const legSwing = walk === null ? 0 : Math.sin(walk) * 11;
  const bob = walk === null ? 0 : -Math.abs(Math.cos(walk)) * 5;

  const P = holo
    ? {skin: `url(#${u}-holo)`, hair: `url(#${u}-holo)`, top: `url(#${u}-holo)`, pants: `url(#${u}-holo)`, shoe: `url(#${u}-holo)`, stroke: PINK, sw: 2.4}
    : {skin: `url(#${u}-skin)`, hair: `url(#${u}-hair)`, top: `url(#${u}-top)`, pants: `url(#${u}-pants)`, shoe: '#ffffff', stroke: 'rgba(255,255,255,0.55)', sw: 1.2};

  const figure = (p: typeof P) => (
    <>
      {/* legs: long loose joggers + sneakers, swinging when she walks */}
      <g transform={`rotate(${legSwing} 95 318)`}>
        <path d="M82 318 L108 318 L106 506 Q104 516 92 516 L86 516 Q78 512 78 502 Z" fill={p.pants} stroke={p.stroke} strokeWidth={p.sw} />
        <path d="M70 514 Q72 504 88 504 L102 506 Q108 512 106 526 L72 528 Q66 524 70 514 Z" fill={p.shoe} stroke={p.stroke} strokeWidth={p.sw} />
      </g>
      <g transform={`rotate(${-legSwing} 125 318)`}>
        <path d="M112 318 L138 318 L142 502 Q142 512 134 516 L128 516 Q116 516 114 506 Z" fill={p.pants} stroke={p.stroke} strokeWidth={p.sw} />
        <path d="M150 514 Q148 504 132 504 L118 506 Q112 512 114 526 L148 528 Q154 524 150 514 Z" fill={p.shoe} stroke={p.stroke} strokeWidth={p.sw} />
      </g>

      {/* upper body bends at the hips */}
      <g transform={`rotate(${pose.lean} 110 318) translate(0 ${breathe * 0.3 + bob})`}>
        {/* ponytail swings behind the head */}
        <path d={`M128 62 Q${168 + pony} 74 ${160 + pony} 128 Q${154 + pony} 160 ${142 + pony} 172 Q${150 + pony * 0.5} 124 132 82 Z`} fill={p.hair} stroke={p.stroke} strokeWidth={p.sw} />
        {/* neck */}
        <rect x={101} y={124} width={18} height={34} rx={8} fill={p.skin} stroke={p.stroke} strokeWidth={p.sw} />
        {/* loose sweatshirt, hem at the hips */}
        <path d="M70 166 Q110 150 150 166 Q160 206 156 250 Q155 290 154 322 Q110 336 66 322 Q65 290 64 250 Q60 206 70 166 Z" fill={p.top} stroke={p.stroke} strokeWidth={p.sw} />
        {/* sporty details: collar, half-zip and ribbed hem */}
        <path d="M96 156 Q110 166 124 156" fill="none" stroke={p.stroke} strokeWidth={p.sw + 0.6} />
        <path d="M110 162 L110 214" stroke={holo ? p.stroke : '#e889b4'} strokeWidth={2} />
        <path d="M68 312 Q110 324 152 312" fill="none" stroke={holo ? p.stroke : '#e889b4'} strokeWidth={2} opacity={0.7} />
        {/* arms in front of the torso */}
        <Arm x={78} y={172} a1={pose.lA1} a2={pose.lA2} sleeve={p.top} skin={p.skin} stroke={holo ? p.stroke : 'rgba(220,120,170,0.7)'} sw={p.sw} dumbbell={{color: '#ff7fb6', scale: dumbbells}} />
        <Arm x={142} y={172} a1={pose.rA1} a2={pose.rA2} sleeve={p.top} skin={p.skin} stroke={holo ? p.stroke : 'rgba(220,120,170,0.7)'} sw={p.sw} dumbbell={{color: '#5fd4c4', scale: dumbbells}} bottle={bottle} />
        {/* head */}
        <ellipse cx={110} cy={98} rx={30} ry={35} fill={p.skin} stroke={p.stroke} strokeWidth={p.sw} />
        {/* hair cap with soft see-through bangs */}
        <path d="M78 104 Q72 52 110 50 Q148 52 142 104 Q140 82 128 74 Q116 86 96 80 Q84 88 78 104 Z" fill={p.hair} stroke={p.stroke} strokeWidth={p.sw} />
        <path d="M80 100 Q78 120 84 134 Q78 128 76 112 Z M140 100 Q142 120 136 134 Q142 128 144 112 Z" fill={p.hair} />
      </g>
    </>
  );

  // face is drawn separately so it follows the lean but stays crisp
  const face = (
    <g transform={`rotate(${pose.lean} 110 318) translate(0 ${breathe * 0.3 + bob})`} opacity={holo ? 0.6 : 1}>
      <path d="M94 104 Q99 109 104 104 M116 104 Q121 109 126 104" fill="none" stroke={holo ? '#fff' : '#5b3a33'} strokeWidth={2.2} strokeLinecap="round" />
      {!holo && (
        <>
          <ellipse cx={93} cy={115} rx={7} ry={4} fill="#ff9fb8" opacity={0.45} />
          <ellipse cx={127} cy={115} rx={7} ry={4} fill="#ff9fb8" opacity={0.45} />
        </>
      )}
      <path d="M104 120 Q110 125 116 120" fill="none" stroke={holo ? '#fff' : '#d4697f'} strokeWidth={2.2} strokeLinecap="round" />
    </g>
  );

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${VB_W} ${VB_H}`}
      style={{
        overflow: 'visible',
        opacity: opacity * flicker,
        filter: holo ? `drop-shadow(0 0 3px #fff) drop-shadow(0 0 12px ${PINK})` : 'drop-shadow(0 0 2px rgba(255,255,255,0.8)) drop-shadow(0 0 14px rgba(255,140,210,0.65))',
      }}
    >
      <defs>
        <radialGradient id={`${u}-skin`} cx="0.35" cy="0.3" r="0.9">
          <stop offset="0" stopColor="#ffe8db" />
          <stop offset="1" stopColor="#efc2a8" />
        </radialGradient>
        <linearGradient id={`${u}-hair`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#4a3330" />
          <stop offset="1" stopColor="#1e1414" />
        </linearGradient>
        <linearGradient id={`${u}-top`} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#ffe1ee" />
          <stop offset="0.55" stopColor="#ffbfd9" />
          <stop offset="1" stopColor="#f191bb" />
        </linearGradient>
        <linearGradient id={`${u}-pants`} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#efe6ff" />
          <stop offset="0.5" stopColor="#d3c2f5" />
          <stop offset="1" stopColor="#ab95dd" />
        </linearGradient>
        <linearGradient id={`${u}-holo`} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#ffd6f1" stopOpacity="0.22" />
          <stop offset="0.5" stopColor="#f6eaff" stopOpacity="0.6" />
          <stop offset="1" stopColor="#c9a6ff" stopOpacity="0.28" />
        </linearGradient>
        <pattern id={`${u}-scan`} width="4" height="5" patternUnits="userSpaceOnUse">
          <rect width="4" height="1.5" fill="#fff" opacity="0.45" />
        </pattern>
        <clipPath id={`${u}-reveal`}>
          <rect x="-200" y={VB_H + 20 - (VB_H + 300) * reveal} width={VB_W + 400} height={VB_H + 400} />
        </clipPath>
      </defs>

      {holo ? (
        <>
          <ellipse cx="110" cy="532" rx="92" ry="16" fill="rgba(255,150,220,0.3)" stroke={PINK} strokeWidth="3" opacity={reveal} />
          <g clipPath={`url(#${u}-reveal)`}>
            {figure(P)}
            {figure({skin: `url(#${u}-scan)`, hair: `url(#${u}-scan)`, top: `url(#${u}-scan)`, pants: `url(#${u}-scan)`, shoe: `url(#${u}-scan)`, stroke: 'none', sw: 0})}
            {face}
          </g>
          {reveal > 0 && reveal < 1 && (
            <rect x="-10" y={VB_H + 20 - (VB_H + 300) * reveal - 2} width="240" height="4" rx="2" fill="#fff" style={{filter: `drop-shadow(0 0 8px ${PINK})`}} />
          )}
        </>
      ) : (
        <>
          {/* soft ground shadow */}
          <ellipse cx="110" cy="530" rx="70" ry="10" fill="rgba(30,0,40,0.35)" style={{filter: 'blur(3px)'}} />
          {energy > 0 && <EnergyLines f={f} amount={energy} half="back" />}
          {figure(P)}
          {face}
          {energy > 0 && <EnergyLines f={f} amount={energy} half="front" />}
          {sweat > 0 && <SweatDrops f={f} amount={sweat} lean={pose.lean} />}
          {/* pink rim light on the right edge for the 3D look */}
          <g transform={`rotate(${pose.lean} 110 318)`} opacity={0.5}>
            <path d="M150 170 Q158 210 154 252 L152 320" fill="none" stroke="#ff8fd0" strokeWidth={3} style={{filter: 'blur(1.5px)'}} />
          </g>
        </>
      )}
      {/* sparkle of light along the body while she stretches */}
      <circle cx={110 + Math.sin(f / 7) * 50} cy={300 + Math.cos(f / 7) * 120} r={3.5} fill="#fff" opacity={interpolate(Math.sin(f / 5), [-1, 1], [0.2, 0.9])} />
    </svg>
  );
};

// Warm light lines travelling around her body while she moves: a general
// "using energy" visual, with no fat-burning or product claim attached.
const RINGS = [
  {y: 210, rx: 96, speed: 0.11, phase: 0},
  {y: 320, rx: 104, speed: -0.09, phase: 2},
  {y: 440, rx: 84, speed: 0.13, phase: 4},
];

const EnergyLines: React.FC<{f: number; amount: number; half: 'front' | 'back'}> = ({f, amount, half}) => (
  <g opacity={amount * (half === 'front' ? 1 : 0.45)} style={{filter: 'drop-shadow(0 0 4px #fff) drop-shadow(0 0 10px #ff9a5c)'}}>
    {RINGS.map((r, i) => {
      const y = r.y + Math.sin(f / 12 + r.phase) * 14;
      // front half = lower arc of the ellipse (towards the viewer)
      const d = half === 'front' ? `M${110 + r.rx} ${y} A${r.rx} 20 0 0 1 ${110 - r.rx} ${y}` : `M${110 - r.rx} ${y} A${r.rx} 20 0 0 1 ${110 + r.rx} ${y}`;
      return (
        <path
          key={i}
          d={d}
          fill="none"
          stroke={i === 1 ? '#ffd27a' : '#ff8a6e'}
          strokeWidth={3.5}
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray="0.35 0.65"
          strokeDashoffset={(f * r.speed) % 1}
        />
      );
    })}
  </g>
);

// Symbolic "sweat": little glowing light drops that pop off the head and
// shoulders and fall away while she works out.
const DROP_SOURCES = [
  [84, 88, -1],
  [136, 84, 1],
  [76, 170, -1],
  [146, 170, 1],
  [110, 60, 0],
];

const SweatDrops: React.FC<{f: number; amount: number; lean: number}> = ({f, amount, lean}) => (
  <g transform={`rotate(${lean} 110 318)`} opacity={amount}>
    {DROP_SOURCES.map(([x0, y0, dir], i) => {
      const period = 22;
      const t = ((f + i * 7) % period) / period;
      const x = x0 + dir * t * 34 + (dir === 0 ? Math.sin(i + f / 9) * 10 : 0);
      const y = y0 - 12 * Math.sin(t * Math.PI) + t * t * 46;
      const a = Math.sin(t * Math.PI);
      return (
        <g key={i} transform={`translate(${x} ${y}) rotate(${dir * 25}) scale(1.5)`} opacity={a}>
          <path d="M0 -9 C5 -2 7 3 7 6 A7 7 0 0 1 -7 6 C-7 3 -5 -2 0 -9 Z" fill="#dff7ff" stroke="#fff" strokeWidth={1.2} style={{filter: 'drop-shadow(0 0 4px #9fe6ff) drop-shadow(0 0 8px #ffffff)'}} />
          <circle cx={-2} cy={4} r={1.8} fill="#fff" />
        </g>
      );
    })}
  </g>
);
