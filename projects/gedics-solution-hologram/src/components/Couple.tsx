// Modest hologram silhouettes of an adult married couple, drawn as glowing
// line art: holding hands, sitting side by side, and a polite side hug.
// The wife wears a hijab and a long dress; the husband a long-sleeved top.
import React from 'react';
import {useCurrentFrame} from 'remotion';

export type Pose = 'hands' | 'sitting' | 'hug';

const STROKE = '#ff7ad1';

const head = (cx: number, cy: number) => <circle cx={cx} cy={cy} r={15} />;

// husband, standing (cx = centre line)
const husband = (cx: number, top = 0) => (
  <g transform={`translate(0 ${top})`}>
    {head(cx, 38)}
    <path
      d={`M${cx - 27} 72 Q${cx - 27} 59 ${cx - 15} 57 L${cx + 15} 57 Q${cx + 27} 59 ${cx + 27} 72
          L${cx + 24} 128 L${cx + 16} 128 L${cx + 15} 202 L${cx + 3} 202 L${cx + 1} 136 L${cx - 1} 136
          L${cx - 3} 202 L${cx - 15} 202 L${cx - 16} 128 L${cx - 24} 128 Z`}
    />
  </g>
);

// wife in hijab, standing
const wife = (cx: number, top = 0, tilt = 0) => (
  <g transform={`translate(0 ${top}) rotate(${tilt} ${cx} 60)`}>
    <path d={`M${cx - 17} 50 A17 19 0 1 1 ${cx + 17} 50 L${cx + 23} 76 Q${cx} 86 ${cx - 23} 76 Z`} />
    <path d={`M${cx - 21} 76 Q${cx} 84 ${cx + 21} 76 L${cx + 35} 204 L${cx - 35} 204 Z`} />
  </g>
);

const seatedHusband = (cx: number) => (
  <g>
    {head(cx, 62)}
    <path
      d={`M${cx - 27} 96 Q${cx - 27} 83 ${cx - 15} 81 L${cx + 15} 81 Q${cx + 27} 83 ${cx + 27} 96
          L${cx + 24} 146 L${cx + 22} 202 L${cx + 10} 202 L${cx + 6} 152 L${cx - 6} 152
          L${cx - 10} 202 L${cx - 22} 202 L${cx - 24} 146 Z`}
    />
  </g>
);

const seatedWife = (cx: number) => (
  <g>
    <path d={`M${cx - 17} 74 A17 19 0 1 1 ${cx + 17} 74 L${cx + 23} 100 Q${cx} 110 ${cx - 23} 100 Z`} />
    <path d={`M${cx - 21} 100 Q${cx} 108 ${cx + 21} 100 L${cx + 30} 148 L${cx + 32} 204 L${cx - 32} 204 L${cx - 30} 148 Z`} />
  </g>
);

const smallHeart = (x: number, y: number, s: number) => (
  <path
    transform={`translate(${x} ${y}) scale(${s})`}
    d="M0 9 C-6 4 -10 1 -10 -3 C-10 -7 -6 -9 -3 -9 C-1 -9 0 -7 0 -6 C0 -7 1 -9 3 -9 C6 -9 10 -7 10 -3 C10 1 6 4 0 9 Z"
    fill="#ff9fdc"
    stroke="none"
  />
);

export const Couple: React.FC<{pose: Pose; size?: number; appear?: number}> = ({pose, size = 200, appear = 1}) => {
  const frame = useCurrentFrame();
  const flicker = 0.88 + 0.12 * Math.sin(frame * 1.7) * Math.sin(frame * 0.37);
  const heartBob = Math.sin(frame / 8) * 3;
  const id = `couple-${pose}`;
  const figure = (
    <>
        {pose === 'hands' && (
          <>
            {husband(66)}
            {wife(134, 0)}
            {/* joined hands between them */}
            <path d="M90 70 Q100 100 100 124 M112 76 Q102 100 100 124" fill="none" strokeWidth={6} strokeLinecap="round" />
            <circle cx="100" cy="126" r="5" />
          </>
        )}
        {pose === 'sitting' && (
          <>
            <rect x="22" y="146" width="156" height="12" rx="4" />
            <rect x="34" y="158" width="6" height="46" />
            <rect x="160" y="158" width="6" height="46" />
            {seatedHusband(72)}
            {seatedWife(128)}
          </>
        )}
        {pose === 'hug' && (
          <>
            {husband(78)}
            {wife(124, 4, -6)}
            {/* his arm resting around her shoulders */}
            <path d="M94 68 Q118 52 144 82" fill="none" strokeWidth={7} strokeLinecap="round" />
          </>
        )}
    </>
  );
  return (
    <svg
      width={size}
      height={size * 1.1}
      viewBox="0 0 200 220"
      style={{overflow: 'visible', opacity: appear * flicker, filter: `drop-shadow(0 0 4px #fff) drop-shadow(0 0 10px ${STROKE})`}}
    >
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#ffd0ef" stopOpacity="0.85" />
          <stop offset="1" stopColor="#c59cff" stopOpacity="0.45" />
        </linearGradient>
        <pattern id={`${id}-scan`} width="4" height="4" patternUnits="userSpaceOnUse">
          <rect width="4" height="1.4" fill="#fff" opacity="0.35" />
        </pattern>
        <clipPath id={`${id}-reveal`}>
          <rect x="0" y={220 - 230 * appear} width="200" height="240" />
        </clipPath>
      </defs>
      <g clipPath={`url(#${id}-reveal)`}>
        <g fill={`url(#${id})`} stroke={STROKE} strokeWidth={3} strokeLinejoin="round">
          {figure}
        </g>
        {/* hologram scan lines, only inside the figures */}
        <g fill={`url(#${id}-scan)`} stroke="none" opacity={0.6}>
          {figure}
        </g>
        {smallHeart(100, pose === 'sitting' ? 28 + heartBob : 4 + heartBob, 1.3)}
      </g>
    </svg>
  );
};
