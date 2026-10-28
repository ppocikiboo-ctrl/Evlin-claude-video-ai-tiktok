// Hologram butterflies: translucent pink/lavender wings that flap, flying
// along gentle curved paths.
import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';

export const Butterfly: React.FC<{size?: number; flap: number; hue?: 'pink' | 'lilac'}> = ({size = 70, flap, hue = 'pink'}) => {
  const u = React.useId().replace(/:/g, '');
  const c1 = hue === 'pink' ? '#ff9ad8' : '#cfb2ff';
  const c2 = hue === 'pink' ? '#ffd9f1' : '#f1e8ff';
  const open = 0.25 + 0.75 * Math.abs(Math.cos(flap)); // wing opening, seen from above
  return (
    <svg width={size} height={size} viewBox="-50 -50 100 100" style={{overflow: 'visible', filter: `drop-shadow(0 0 4px #fff) drop-shadow(0 0 10px ${c1})`}}>
      <defs>
        <radialGradient id={`${u}-w`} cx="0.3" cy="0.4" r="0.8">
          <stop offset="0" stopColor={c2} stopOpacity="0.95" />
          <stop offset="1" stopColor={c1} stopOpacity="0.45" />
        </radialGradient>
      </defs>
      {[-1, 1].map((side) => (
        <g key={side} transform={`scale(${side * open} 1)`}>
          <path d="M2 -4 C14 -34 46 -38 44 -14 C42 2 22 4 2 0 Z" fill={`url(#${u}-w)`} stroke="#fff" strokeWidth="1.5" />
          <path d="M2 2 C20 4 38 12 30 30 C22 42 8 28 2 8 Z" fill={`url(#${u}-w)`} stroke="#fff" strokeWidth="1.5" />
        </g>
      ))}
      <ellipse cx="0" cy="2" rx="3" ry="16" fill="#fff" />
      <path d="M-1 -13 Q-8 -26 -12 -28 M1 -13 Q8 -26 12 -28" stroke="#fff" strokeWidth="1.4" fill="none" />
    </svg>
  );
};

type Flight = {from: number; to: number; path: [number, number][]; size?: number; hue?: 'pink' | 'lilac'; seed?: number};

// Catmull-Rom style interpolation through the waypoints
const along = (pts: [number, number][], p: number): [number, number, number] => {
  const n = pts.length - 1;
  const x = Math.min(n - 1e-6, Math.max(0, p * n));
  const i = Math.floor(x);
  const t = x - i;
  const P = (k: number) => pts[Math.max(0, Math.min(n, k))];
  const [p0, p1, p2, p3] = [P(i - 1), P(i), P(i + 1), P(i + 2)];
  const cr = (a: number, b: number, c: number, d: number) =>
    0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t * t * t);
  const px = cr(p0[0], p1[0], p2[0], p3[0]);
  const py = cr(p0[1], p1[1], p2[1], p3[1]);
  const heading = Math.atan2(p2[1] - p1[1], p2[0] - p1[0]);
  return [px, py, heading];
};

export const ButterflyFlight: React.FC<{flights: Flight[]}> = ({flights}) => {
  const f = useCurrentFrame();
  return (
    <>
      {flights.map((fl, i) => {
        if (f < fl.from || f > fl.to) return null;
        const p = (f - fl.from) / (fl.to - fl.from);
        const [x, y, h] = along(fl.path, p);
        const fade = interpolate(p, [0, 0.08, 0.9, 1], [0, 1, 1, 0]);
        const size = fl.size ?? 70;
        const tilt = (h * 180) / Math.PI + 90;
        return (
          <div key={i} style={{position: 'absolute', left: x - size / 2, top: y - size / 2 + Math.sin(f / 5 + i) * 6, opacity: fade, transform: `rotate(${tilt * 0.35}deg)`}}>
            <Butterfly size={size} flap={f * 0.55 + (fl.seed ?? i)} hue={fl.hue} />
          </div>
        );
      })}
    </>
  );
};
