// Self-care and ingredient icons as inline SVG, plus the glowing badge they
// float in.
import React from 'react';
import {useCurrentFrame} from 'remotion';

type P = {size?: number};

export const WaterBottle: React.FC<P> = ({size = 70}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <rect x="40" y="6" width="20" height="12" rx="3" fill="#cfb2ff" />
    <path d="M36 20 H64 Q72 28 72 40 V86 Q72 94 64 94 H36 Q28 94 28 86 V40 Q28 28 36 20 Z" fill="#e9f6ff" stroke="#9fd0ff" strokeWidth="3" />
    <path d="M30 56 H70 V86 Q70 92 64 92 H36 Q30 92 30 86 Z" fill="#8fd0ff" opacity="0.8" />
    <path d="M40 34 V80" stroke="#fff" strokeWidth="4" strokeLinecap="round" opacity="0.8" />
  </svg>
);

export const Sneaker: React.FC<P> = ({size = 70}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M8 70 Q8 50 22 46 L40 40 Q48 52 60 54 L84 60 Q94 64 94 74 V78 H8 Z" fill="#ff8fcf" stroke="#fff" strokeWidth="3" strokeLinejoin="round" />
    <rect x="6" y="76" width="90" height="10" rx="5" fill="#fff" />
    <path d="M44 48 L52 44 M50 53 L58 49 M57 56 L64 53" stroke="#fff" strokeWidth="3" strokeLinecap="round" />
  </svg>
);

export const KidneyBean: React.FC<P> = ({size = 60}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M30 20 C56 6 92 22 88 52 C84 80 52 94 30 80 C18 72 26 58 36 54 C46 50 46 40 36 36 C24 32 18 26 30 20 Z" fill="#fbf4ea" stroke="#e8cfa8" strokeWidth="3" />
    <ellipse cx="62" cy="38" rx="10" ry="6" fill="#fff" opacity="0.8" transform="rotate(20 62 38)" />
  </svg>
);

// simple molecule glyph for L-Carnitine (a label, not a claim)
export const Molecule: React.FC<P> = ({size = 60}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <g stroke="#e9dcff" strokeWidth="5">
      <line x1="50" y1="50" x2="22" y2="28" />
      <line x1="50" y1="50" x2="80" y2="30" />
      <line x1="50" y1="50" x2="50" y2="84" />
    </g>
    <circle cx="50" cy="50" r="13" fill="#cfb2ff" />
    <circle cx="22" cy="28" r="10" fill="#ff9ad8" />
    <circle cx="80" cy="30" r="10" fill="#ffffff" />
    <circle cx="50" cy="84" r="10" fill="#ffd36e" />
  </svg>
);

// self-care symbol: a lotus with a small heart
export const Lotus: React.FC<P & {draw?: number}> = ({size = 120, draw = 1}) => (
  <svg width={size} height={size} viewBox="0 0 100 100" style={{overflow: 'visible'}}>
    <g fill="rgba(255,190,235,0.35)" stroke="#fff" strokeWidth="2.4" strokeLinejoin="round" style={{filter: 'drop-shadow(0 0 5px #ff7ad1)'}}>
      {[
        'M50 76 C36 60 38 36 50 22 C62 36 64 60 50 76 Z',
        'M50 76 C30 72 18 56 20 38 C36 42 48 56 50 76 Z',
        'M50 76 C70 72 82 56 80 38 C64 42 52 56 50 76 Z',
        'M50 78 C30 80 12 72 6 58 C24 54 40 64 50 78 Z',
        'M50 78 C70 80 88 72 94 58 C76 54 60 64 50 78 Z',
      ].map((d) => (
        <path key={d} d={d} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} fillOpacity={draw} />
      ))}
    </g>
    <path
      d="M50 54 C44 49 42 46 42 43 C42 40 45 38 47 38 C48.5 38 49.5 39 50 40 C50.5 39 51.5 38 53 38 C55 38 58 40 58 43 C58 46 56 49 50 54 Z"
      fill="#ff6fbf"
      opacity={draw}
    />
  </svg>
);

// round glass badge with a pink light dot circling it
export const IconBadge: React.FC<{size?: number; children: React.ReactNode; pop?: number; seed?: number}> = ({size = 120, children, pop = 1, seed = 0}) => {
  const f = useCurrentFrame();
  const a = f / 9 + seed;
  const r = size / 2 + 6;
  return (
    <div style={{position: 'relative', width: size, height: size, transform: `scale(${pop})`, opacity: Math.min(1, pop)}}>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: '50%',
          background: 'radial-gradient(circle at 35% 30%, rgba(255,255,255,0.45), rgba(230,200,255,0.18) 60%, rgba(255,120,210,0.18))',
          border: '2.5px solid rgba(255,140,215,0.95)',
          boxShadow: '0 0 16px rgba(255,110,200,0.8), inset 0 0 18px rgba(255,255,255,0.35)',
          backdropFilter: 'blur(6px)',
        }}
      />
      <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{children}</div>
      <div
        style={{
          position: 'absolute',
          left: size / 2 + Math.cos(a) * r - 7,
          top: size / 2 + Math.sin(a) * r - 7,
          width: 14,
          height: 14,
          borderRadius: '50%',
          background: '#fff',
          boxShadow: '0 0 10px #fff, 0 0 22px #ff6fcf',
        }}
      />
    </div>
  );
};
