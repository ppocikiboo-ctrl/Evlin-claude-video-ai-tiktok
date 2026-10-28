// Hologram silhouette of a modestly dressed woman (hijab, long-sleeved top,
// loose full-length abaya). The shape never changes size or proportions: it
// only appears, turns, walks and fades. That is deliberate, so it can't be read
// as before/after or a "slimming" visual.
import React from 'react';
import {useCurrentFrame} from 'remotion';

type Props = {
  height: number;
  reveal?: number; // 0..1 hologram builds up from the feet
  turn?: number; // degrees around the vertical axis
  walk?: number | null; // walk-cycle phase in radians, null = standing
  ring?: number; // 0..1 visibility of the pink light ring travelling around her
  opacity?: number;
};

const PINK = '#ff7ad1';
const VB_W = 200;
const VB_H = 540;

export const Woman: React.FC<Props> = ({height, reveal = 1, turn = 0, walk = null, ring = 0, opacity = 1}) => {
  const f = useCurrentFrame();
  const u = React.useId().replace(/:/g, '');
  const width = (height * VB_W) / VB_H;
  const flicker = 0.9 + 0.1 * Math.sin(f * 1.9) * Math.sin(f * 0.43);

  const ph = walk ?? 0;
  const walking = walk !== null;
  const armL = walking ? Math.sin(ph) * 9 : 0;
  const armR = walking ? -Math.sin(ph) * 9 : 0;
  const sway = walking ? Math.sin(ph) * 7 : 0;
  const bob = walking ? Math.abs(Math.cos(ph)) * -4 : 0;
  const footL = walking ? Math.sin(ph) * 10 : 0;
  const footR = walking ? -Math.sin(ph) * 10 : 0;

  // shading slides across the body as she turns, which sells the 3D turn
  const shade = 0.5 + turn / 60;

  // light ring travelling up and down the figure
  const ringY = 300 + Math.sin(f / 16) * 170;
  const ringRx = 98 + Math.cos(f / 16) * 6;
  const ringDash = (f * 0.02) % 1;

  const body = (
    <g transform={`translate(0 ${bob})`}>
      {/* abaya: loose A-line from the shoulders to the floor, no waist shaping */}
      <path d={`M58 132 Q100 124 142 132 L150 178 L154 300 L${172 + sway} 512 Q100 ${528 + sway * 0.3} ${28 + sway} 512 L46 300 L50 178 Z`} />
      {/* long sleeves with hands, swinging slightly when walking */}
      <g transform={`rotate(${armL} 58 140)`}>
        <path d="M58 134 Q42 144 40 174 L36 282 Q36 292 44 294 L54 294 Q58 286 58 278 L62 182 Z" />
        <ellipse cx="46" cy="305" rx="7" ry="11" />
      </g>
      <g transform={`rotate(${armR} 142 140)`}>
        <path d="M142 134 Q158 144 160 174 L164 282 Q164 292 156 294 L146 294 Q142 286 142 278 L138 182 Z" />
        <ellipse cx="154" cy="305" rx="7" ry="11" />
      </g>
      {/* hijab draped over the shoulders to mid-chest */}
      <path d="M74 60 C72 16 128 16 126 60 C130 80 140 96 146 120 Q150 152 128 162 Q100 172 72 162 Q50 152 54 120 C60 96 70 80 74 60 Z" />
      {/* shoes peeking out under the hem */}
      <ellipse cx={80 + footL} cy={522} rx={14} ry={6} />
      <ellipse cx={120 + footR} cy={522} rx={14} ry={6} />
    </g>
  );

  // fabric detail: hijab edge, sleeve cuffs and soft dress folds
  const details = (
    <g transform={`translate(0 ${bob})`} fill="none" stroke="#fff" strokeWidth="1.6" strokeLinecap="round" opacity="0.65">
      <path d="M78 64 Q100 98 122 64" />
      <path d="M62 150 Q100 176 138 150" opacity="0.6" />
      <path d={`M84 200 L${74 + sway * 0.6} 506 M100 192 L${100 + sway * 0.8} 516 M116 200 L${126 + sway * 0.6} 506`} opacity="0.45" />
      <g transform={`rotate(${armL} 58 140)`}><path d="M38 282 L56 284" /></g>
      <g transform={`rotate(${armR} 142 140)`}><path d="M144 284 L162 282" /></g>
    </g>
  );

  return (
    <div style={{width, height, perspective: 900, opacity: opacity * flicker}}>
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${VB_W} ${VB_H}`}
        style={{overflow: 'visible', transform: `rotateY(${turn}deg)`, filter: `drop-shadow(0 0 3px #fff) drop-shadow(0 0 12px ${PINK})`}}
      >
        <defs>
          <linearGradient id={`${u}-wBody`} x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stopColor="#ffd6f1" stopOpacity="0.2" />
            <stop offset={Math.max(0.05, Math.min(0.95, shade))} stopColor="#f2e6ff" stopOpacity="0.6" />
            <stop offset="1" stopColor="#c9a6ff" stopOpacity="0.25" />
          </linearGradient>
          <linearGradient id={`${u}-wFade`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#fff" stopOpacity="1" />
            <stop offset="0.85" stopColor="#fff" stopOpacity="1" />
            <stop offset="1" stopColor="#fff" stopOpacity="0.4" />
          </linearGradient>
          <linearGradient id={`${u}-coneGrad`} x1="0" y1="1" x2="0" y2="0">
            <stop offset="0" stopColor="#ffb3e6" />
            <stop offset="1" stopColor="#ffb3e6" stopOpacity="0" />
          </linearGradient>
          <pattern id={`${u}-wScan`} width="4" height="5" patternUnits="userSpaceOnUse">
            <rect width="4" height="1.5" fill="#fff" opacity="0.45" />
          </pattern>
          <clipPath id={`${u}-wReveal`}>
            <rect x="-50" y={VB_H + 20 - (VB_H + 60) * reveal} width={VB_W + 100} height={VB_H + 100} />
          </clipPath>
          <mask id={`${u}-wMask`}>
            <rect width={VB_W} height={VB_H + 20} fill={`url(#${u}-wFade)`} />
          </mask>
        </defs>

        {/* projector base and light cone */}
        <ellipse cx="100" cy="528" rx="88" ry="16" fill="none" stroke={PINK} strokeWidth="3" opacity={0.8 * reveal} />
        <ellipse cx="100" cy="528" rx="70" ry="11" fill="rgba(255,150,220,0.35)" opacity={reveal} />
        <path d="M30 528 L70 120 L130 120 L170 528 Z" fill={`url(#${u}-coneGrad)`} opacity={0.18 * reveal} />

        {/* back half of the ring, behind her */}
        {ring > 0 && (
          <path
            d={`M${100 - ringRx} ${ringY} A${ringRx} 22 0 0 1 ${100 + ringRx} ${ringY}`}
            fill="none"
            stroke={PINK}
            strokeWidth="3"
            opacity={0.45 * ring}
            pathLength={1}
            strokeDasharray="0.55 0.45"
            strokeDashoffset={-ringDash}
          />
        )}

        <g clipPath={`url(#${u}-wReveal)`} mask={`url(#${u}-wMask)`}>
          <g fill={`url(#${u}-wBody)`} stroke={PINK} strokeWidth="2.6" strokeLinejoin="round">
            {body}
          </g>
          {/* face opening: a soft glow only, no features */}
          <ellipse cx="100" cy={62 + bob} rx="18" ry="23" fill="rgba(255,244,252,0.7)" stroke={PINK} strokeWidth="1.5" />
          {details}
          <g fill={`url(#${u}-wScan)`} stroke="none">
            {body}
          </g>
        </g>

        {/* front half of the ring, in front of her */}
        {ring > 0 && (
          <path
            d={`M${100 + ringRx} ${ringY} A${ringRx} 22 0 0 1 ${100 - ringRx} ${ringY}`}
            fill="none"
            stroke="#fff"
            strokeWidth="4"
            opacity={ring}
            pathLength={1}
            strokeDasharray="0.6 0.4"
            strokeDashoffset={ringDash}
            style={{filter: `drop-shadow(0 0 6px ${PINK})`}}
          />
        )}

        {/* bright scan line while the hologram builds */}
        {reveal > 0 && reveal < 1 && (
          <rect x="10" y={VB_H + 20 - (VB_H + 60) * reveal - 2} width="180" height="4" rx="2" fill="#fff" style={{filter: `drop-shadow(0 0 8px ${PINK})`}} />
        )}
      </svg>
    </div>
  );
};
