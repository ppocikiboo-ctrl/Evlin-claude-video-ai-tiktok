// Adult woman in a Korean-beauty illustration style, in modest sportswear:
// a loose long-sleeved sweatshirt, long jogger pants and sneakers. Natural,
// constant body proportions: only her pose changes (light stretches), never
// her shape or size.
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

export const POSES: Record<'rest' | 'up' | 'tee', Pose> = {
  rest: {lean: 0, lA1: 10, lA2: -8, rA1: -10, rA2: 8},
  up: {lean: 0, lA1: 165, lA2: 52, rA1: -165, rA2: -52}, // hands clasped overhead
  tee: {lean: 0, lA1: 88, lA2: 0, rA1: -88, rA2: 0}, // arms out to the sides
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

type Props = {
  height: number;
  pose: Pose;
  variant?: 'solid' | 'hologram';
  reveal?: number; // hologram build-up from the feet, 0..1
  opacity?: number;
};

const VB_W = 220;
const VB_H = 580;
const PINK = '#ff7ad1';

const Arm: React.FC<{x: number; y: number; a1: number; a2: number; sleeve: string; skin: string; stroke: string; sw: number}> = ({x, y, a1, a2, sleeve, skin, stroke, sw}) => (
  <g transform={`translate(${x} ${y}) rotate(${a1})`}>
    <rect x={-12} y={-6} width={24} height={84} rx={12} fill={sleeve} stroke={stroke} strokeWidth={sw} />
    <g transform={`translate(0 74) rotate(${a2})`}>
      <rect x={-11} y={-4} width={22} height={70} rx={11} fill={sleeve} stroke={stroke} strokeWidth={sw} />
      <rect x={-11} y={56} width={22} height={10} rx={4} fill={sleeve} stroke={stroke} strokeWidth={sw} opacity={0.9} />
      <ellipse cx={0} cy={76} rx={9} ry={11} fill={skin} stroke={stroke} strokeWidth={sw} />
    </g>
  </g>
);

export const KoreanWoman: React.FC<Props> = ({height, pose, variant = 'solid', reveal = 1, opacity = 1}) => {
  const f = useCurrentFrame();
  const u = React.useId().replace(/:/g, '');
  const holo = variant === 'hologram';
  const width = (height * VB_W) / VB_H;
  const flicker = holo ? 0.88 + 0.12 * Math.sin(f * 1.9) * Math.sin(f * 0.41) : 1;
  const breathe = Math.sin(f / 14) * 1.2;
  const pony = Math.sin(f / 9) * 4 - pose.lean * 0.6;

  const P = holo
    ? {skin: `url(#${u}-holo)`, hair: `url(#${u}-holo)`, top: `url(#${u}-holo)`, pants: `url(#${u}-holo)`, shoe: `url(#${u}-holo)`, stroke: PINK, sw: 2.4}
    : {skin: `url(#${u}-skin)`, hair: `url(#${u}-hair)`, top: `url(#${u}-top)`, pants: `url(#${u}-pants)`, shoe: '#ffffff', stroke: 'rgba(255,255,255,0.55)', sw: 1.2};

  const figure = (p: typeof P) => (
    <>
      {/* legs: long loose joggers + sneakers */}
      <path d="M82 318 L108 318 L106 506 Q104 516 92 516 L86 516 Q78 512 78 502 Z" fill={p.pants} stroke={p.stroke} strokeWidth={p.sw} />
      <path d="M112 318 L138 318 L142 502 Q142 512 134 516 L128 516 Q116 516 114 506 Z" fill={p.pants} stroke={p.stroke} strokeWidth={p.sw} />
      <path d="M70 514 Q72 504 88 504 L102 506 Q108 512 106 526 L72 528 Q66 524 70 514 Z" fill={p.shoe} stroke={p.stroke} strokeWidth={p.sw} />
      <path d="M150 514 Q148 504 132 504 L118 506 Q112 512 114 526 L148 528 Q154 524 150 514 Z" fill={p.shoe} stroke={p.stroke} strokeWidth={p.sw} />

      {/* upper body bends at the hips */}
      <g transform={`rotate(${pose.lean} 110 318) translate(0 ${breathe * 0.3})`}>
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
        <Arm x={78} y={172} a1={pose.lA1} a2={pose.lA2} sleeve={p.top} skin={p.skin} stroke={holo ? p.stroke : 'rgba(220,120,170,0.7)'} sw={p.sw} />
        <Arm x={142} y={172} a1={pose.rA1} a2={pose.rA2} sleeve={p.top} skin={p.skin} stroke={holo ? p.stroke : 'rgba(220,120,170,0.7)'} sw={p.sw} />
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
    <g transform={`rotate(${pose.lean} 110 318)`} opacity={holo ? 0.6 : 1}>
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
          {figure(P)}
          {face}
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
