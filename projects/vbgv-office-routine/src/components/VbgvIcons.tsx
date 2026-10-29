// Emoji-style icons for this edit as inline SVG (renders the same everywhere).
import React from 'react';

type P = {size?: number};

// 💻
export const Laptop: React.FC<P> = ({size = 70}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <rect x="18" y="20" width="64" height="44" rx="5" fill="#3b3f4a" stroke="#cfd3dc" strokeWidth="3" />
    <rect x="24" y="26" width="52" height="32" rx="2" fill="#9fd6ff" />
    <path d="M8 70 H92 L84 80 H16 Z" fill="#cfd3dc" />
    <rect x="42" y="70" width="16" height="3" rx="1.5" fill="#9aa0ad" />
  </svg>
);

// 🛍️ shopping bag (yellow, like TikTok's product button)
export const ShopBag: React.FC<P> = ({size = 70}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M34 36 V28 A16 16 0 0 1 66 28 V36" fill="none" stroke="#a86b10" strokeWidth="7" strokeLinecap="round" />
    <rect x="14" y="32" width="72" height="62" rx="9" fill="#ffc42a" />
    <rect x="14" y="32" width="72" height="12" rx="6" fill="#ffdc78" />
  </svg>
);

// ⏩
export const FastForward: React.FC<P> = ({size = 40}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M10 20 L50 50 L10 80 Z M50 20 L90 50 L50 80 Z" fill="#ffffff" />
  </svg>
);

// 🏃‍♀️ runner silhouette
export const Runner: React.FC<P> = ({size = 120}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <g fill="none" stroke="#ffffff" strokeWidth="9" strokeLinecap="round" strokeLinejoin="round">
      <path d="M48 30 L40 56 L56 70 L54 92" />
      <path d="M40 56 L28 74 L14 74" />
      <path d="M46 36 L62 46 L74 40" />
      <path d="M46 36 L32 40 L24 52" />
    </g>
    <circle cx="56" cy="16" r="10" fill="#ffffff" />
  </svg>
);

// ⏰ clock with spinning hands
export const Clock: React.FC<P & {t?: number}> = ({size = 90, t = 0}) => (
  <svg width={size} height={size} viewBox="-50 -50 100 100">
    <circle r="44" fill="#ffffff" stroke="#ff5a7a" strokeWidth="7" />
    {Array.from({length: 12}, (_, i) => (
      <rect key={i} x="-1.5" y="-38" width="3" height="7" fill="#7a5a8c" transform={`rotate(${i * 30})`} />
    ))}
    <rect x="-2.5" y="-26" width="5" height="28" rx="2.5" fill="#3a2234" transform={`rotate(${t * 30})`} />
    <rect x="-2" y="-34" width="4" height="36" rx="2" fill="#ff5a7a" transform={`rotate(${t * 360})`} />
    <circle r="4" fill="#3a2234" />
  </svg>
);

// 🍩
export const Donut: React.FC<P> = ({size = 90}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <circle cx="50" cy="52" r="40" fill="#e0a35f" />
    <path d="M14 46 Q20 18 50 14 Q80 18 86 46 Q80 60 70 56 Q60 66 50 58 Q38 68 30 58 Q18 62 14 46 Z" fill="#ff8fc8" />
    <circle cx="50" cy="48" r="13" fill="#ffffff" stroke="#e0a35f" strokeWidth="4" />
    {[[30, 30, 20], [64, 26, -30], [74, 44, 60], [36, 50, 80], [58, 62, 10]].map(([x, y, r], i) => (
      <rect key={i} x={x} y={y} width="9" height="3.5" rx="1.75" fill={['#ffd36e', '#7fe0d0', '#ffffff', '#a66bff', '#ffd36e'][i]} transform={`rotate(${r} ${x} ${y})`} />
    ))}
  </svg>
);

// 🧋 bubble tea
export const BubbleTea: React.FC<P> = ({size = 90}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <rect x="56" y="2" width="7" height="34" rx="3" fill="#ff8fc8" transform="rotate(14 60 20)" />
    <path d="M24 28 H76 L68 94 H32 Z" fill="#f3d9bf" stroke="#ffffff" strokeWidth="3" />
    <path d="M22 22 H78 V30 H22 Z" fill="#ffffff" />
    {[[38, 82], [48, 86], [58, 82], [44, 74], [56, 72]].map(([x, y], i) => (
      <circle key={i} cx={x} cy={y} r="5" fill="#3a2234" />
    ))}
  </svg>
);

// 🍪
export const Cookie: React.FC<P> = ({size = 90}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M50 8 A42 42 0 1 0 92 52 A12 12 0 0 1 76 36 A12 12 0 0 1 62 18 A10 10 0 0 1 50 8 Z" fill="#e6b26a" stroke="#c48a3c" strokeWidth="3" />
    {[[34, 36], [52, 54], [30, 64], [64, 72], [46, 80]].map(([x, y], i) => (
      <circle key={i} cx={x} cy={y} r="5" fill="#5a3a22" />
    ))}
  </svg>
);

// 🍟
export const Fries: React.FC<P> = ({size = 90}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    {[30, 40, 50, 60, 70].map((x, i) => (
      <rect key={x} x={x - 4} y={8 + (i % 2) * 8} width="9" height="50" rx="2" fill="#ffcd3c" stroke="#e0a314" strokeWidth="1.5" />
    ))}
    <path d="M18 42 H82 L74 96 H26 Z" fill="#ff4d5e" />
    <path d="M38 56 Q50 70 62 56" stroke="#ffffff" strokeWidth="4" fill="none" />
  </svg>
);

// 👆 tapping finger
export const TapFinger: React.FC<P> = ({size = 110}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path
      d="M40 12 Q40 4 47 4 Q54 4 54 12 V44 Q58 38 64 40 Q70 42 70 48 Q74 44 79 46 Q85 49 84 56 Q88 54 91 58 Q94 62 92 70 L86 86 Q82 96 70 96 H50 Q40 96 34 88 L18 66 Q14 60 19 56 Q24 52 30 57 L40 66 Z"
      fill="#ffd9c2"
      stroke="#7a4a3a"
      strokeWidth="3"
      strokeLinejoin="round"
    />
  </svg>
);

// 🏷️ price tag
export const PriceTag: React.FC<P & {label?: string}> = ({size = 150, label = 'PROMO'}) => (
  <svg width={size} height={size * 0.6} viewBox="0 0 150 90" style={{overflow: 'visible'}}>
    <path d="M30 5 H142 Q147 5 147 10 V80 Q147 85 142 85 H30 L3 45 Z" fill="#ff3d6e" stroke="#ffffff" strokeWidth="4" />
    <circle cx="26" cy="45" r="7" fill="#ffffff" />
    <text x="88" y="56" textAnchor="middle" fontFamily="Inter Display" fontWeight="900" fontSize="30" fill="#ffffff">
      {label}
    </text>
  </svg>
);
