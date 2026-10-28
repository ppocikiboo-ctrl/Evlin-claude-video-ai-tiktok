// A generous plate of food seen from slightly above. A fork takes a few
// bites, and the plate is still clearly not finished: a general "mindful
// eating" lifestyle visual. It is not tied to the product in any way.
import React from 'react';
import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

type Piece = {id: number; x: number; y: number; kind: 'chicken' | 'broccoli' | 'carrot' | 'egg' | 'tomato'; r: number};

// coordinates in the plate's 320x220 viewBox
const PIECES: Piece[] = [
  {id: 0, x: 92, y: 96, kind: 'chicken', r: 22},
  {id: 1, x: 126, y: 82, kind: 'chicken', r: 22},
  {id: 2, x: 112, y: 120, kind: 'chicken', r: 21},
  {id: 3, x: 210, y: 82, kind: 'broccoli', r: 20},
  {id: 4, x: 240, y: 104, kind: 'broccoli', r: 19},
  {id: 5, x: 218, y: 128, kind: 'broccoli', r: 18},
  {id: 6, x: 166, y: 146, kind: 'carrot', r: 11},
  {id: 7, x: 186, y: 156, kind: 'carrot', r: 11},
  {id: 8, x: 146, y: 158, kind: 'carrot', r: 11},
  {id: 9, x: 252, y: 136, kind: 'egg', r: 17},
  {id: 10, x: 70, y: 128, kind: 'tomato', r: 12},
  {id: 11, x: 262, y: 74, kind: 'tomato', r: 11},
];

const PieceShape: React.FC<{p: Piece}> = ({p}) => {
  switch (p.kind) {
    case 'chicken':
      return (
        <g>
          <ellipse cx={0} cy={0} rx={p.r} ry={p.r * 0.72} fill="#e7a35c" stroke="#b86d2c" strokeWidth={2} />
          <path d={`M${-p.r * 0.6} ${-3} Q0 ${-p.r * 0.5} ${p.r * 0.6} -2`} stroke="#c97a35" strokeWidth={3} fill="none" />
          <ellipse cx={-p.r * 0.3} cy={-p.r * 0.25} rx={p.r * 0.3} ry={p.r * 0.15} fill="#ffd39b" opacity={0.7} />
        </g>
      );
    case 'broccoli':
      return (
        <g>
          <rect x={-4} y={2} width={8} height={p.r * 0.8} rx={3} fill="#9ccf6a" />
          {[[-8, -4], [8, -4], [0, -10], [-4, 2], [6, 2]].map(([dx, dy], i) => (
            <circle key={i} cx={dx} cy={dy} r={p.r * 0.45} fill={i % 2 ? '#3fa34d' : '#52b85c'} stroke="#2e7d3a" strokeWidth={1.2} />
          ))}
        </g>
      );
    case 'carrot':
      return (
        <g>
          <circle r={p.r} fill="#ff9a3c" stroke="#e0701a" strokeWidth={2} />
          <circle r={p.r * 0.45} fill="#ffc07a" />
        </g>
      );
    case 'egg':
      return (
        <g>
          <ellipse rx={p.r} ry={p.r * 0.8} fill="#fffaf0" stroke="#e8dcc6" strokeWidth={2} />
          <circle r={p.r * 0.45} fill="#ffc531" />
        </g>
      );
    case 'tomato':
      return (
        <g>
          <circle r={p.r} fill="#ff4d5e" stroke="#d22d3f" strokeWidth={1.6} />
          <path d="M-4 -9 L0 -5 L4 -9" stroke="#3fa34d" strokeWidth={2.4} fill="none" strokeLinecap="round" />
          <ellipse cx={-3} cy={-3} rx={3} ry={2} fill="#fff" opacity={0.6} />
        </g>
      );
  }
};

const Fork: React.FC = () => (
  <g>
    <rect x={-4} y={10} width={8} height={130} rx={4} fill="#e9e6f0" stroke="#a9a3b8" strokeWidth={1.4} />
    <path d="M-12 14 L-12 -26 M-4 14 L-4 -28 M4 14 L4 -28 M12 14 L12 -26" stroke="#d9d5e3" strokeWidth={4} strokeLinecap="round" />
    <path d="M-14 10 Q0 22 14 10" fill="#e9e6f0" stroke="#a9a3b8" strokeWidth={1.4} />
  </g>
);

// Which pieces the fork takes, and when (absolute frames)
type Bite = {at: number; piece: number};
type ForkState = {x: number; y: number; carrying: Piece | null; alpha: number};

export const FoodPlate: React.FC<{from: number; to: number; bites: number[]; width: number}> = ({from, to, bites, width}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (f < from || f >= to) return null;
  const plan: Bite[] = bites.map((at, i) => ({at, piece: [1, 4, 7][i % 3]}));
  const pop = spring({frame: f - from, fps, config: {damping: 11, stiffness: 160}});
  const out = interpolate(f, [to - 6, to], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scale = width / 320;

  // fork: approaches a piece 6 frames before the bite, then lifts up-right
  let fork = null as ForkState | null;
  const eaten = new Set<number>();
  for (const b of plan) {
    const p = PIECES[b.piece];
    if (f >= b.at + 8) eaten.add(b.piece);
    if (f >= b.at - 6 && f < b.at + 8) {
      const down = interpolate(f, [b.at - 6, b.at], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
      const up = interpolate(f, [b.at, b.at + 8], [0, 1], {extrapolateLeft: 'clamp', easing: Easing.in(Easing.quad)});
      fork = {
        x: interpolate(down, [0, 1], [340, p.x]) + up * 140,
        y: interpolate(down, [0, 1], [-60, p.y - 24]) - up * 170,
        carrying: f >= b.at ? p : null,
        alpha: Math.min(1, (1 - up) * 1.6),
      };
      if (f >= b.at) eaten.add(b.piece);
    }
  }

  return (
    <div style={{position: 'absolute', transform: `scale(${pop})`, opacity: out, transformOrigin: 'center'}}>
      <svg width={width} height={(width * 220) / 320} viewBox="0 0 320 220" style={{overflow: 'visible', filter: 'drop-shadow(0 10px 16px rgba(30,0,40,0.45))'}}>
        {/* plate */}
        <ellipse cx={160} cy={118} rx={156} ry={96} fill="#ffffff" stroke="#ead9f2" strokeWidth={3} />
        <ellipse cx={160} cy={116} rx={124} ry={72} fill="#fbf5fd" stroke="#f1e3f6" strokeWidth={2} />
        <path d="M30 104 A156 96 0 0 1 170 22" fill="none" stroke="#fff" strokeWidth={6} opacity={0.8} />
        {/* rice mound, a generous portion */}
        <ellipse cx={168} cy={102} rx={46} ry={34} fill="#fffdf7" stroke="#eee6d6" strokeWidth={2} />
        {Array.from({length: 18}, (_, i) => (
          <ellipse key={i} cx={136 + ((i * 37) % 64)} cy={82 + ((i * 23) % 40)} rx={4} ry={2} fill="#f3ead9" transform={`rotate(${i * 40} ${136 + ((i * 37) % 64)} ${82 + ((i * 23) % 40)})`} />
        ))}
        {PIECES.filter((p) => !eaten.has(p.id)).map((p) => (
          <g key={p.id} transform={`translate(${p.x} ${p.y})`}>
            <PieceShape p={p} />
          </g>
        ))}
        {fork && (
          <g transform={`translate(${fork.x} ${fork.y}) rotate(-20)`} opacity={fork.alpha}>
            {fork.carrying && (
              <g transform="translate(0 -30) scale(0.8)">
                <PieceShape p={fork.carrying} />
              </g>
            )}
            <Fork />
          </g>
        )}
      </svg>
    </div>
  );
};
