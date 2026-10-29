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

// 👜 handbag
export const Handbag: React.FC<P> = ({size = 70}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M34 40 V32 A16 16 0 0 1 66 32 V40" fill="none" stroke="#7a3fc0" strokeWidth="6" strokeLinecap="round" />
    <path d="M18 40 H82 L88 88 H12 Z" fill="#a66bff" stroke="#ffffff" strokeWidth="3" strokeLinejoin="round" />
    <rect x="44" y="52" width="12" height="9" rx="2" fill="#ffd98a" />
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

// 🌞
export const Sun: React.FC<P> = ({size = 70}) => (
  <svg width={size} height={size} viewBox="-50 -50 100 100">
    {Array.from({length: 10}, (_, i) => (
      <path key={i} transform={`rotate(${i * 36})`} d="M0 -46 L7 -32 L-7 -32 Z" fill="#ffb21f" />
    ))}
    <circle r="28" fill="#ffd23f" stroke="#ffb21f" strokeWidth="3" />
    <path d="M-12 -4 Q-8 -8 -4 -4 M4 -4 Q8 -8 12 -4" stroke="#8a4b00" strokeWidth="3" fill="none" strokeLinecap="round" />
    <path d="M-10 8 Q0 16 10 8" stroke="#8a4b00" strokeWidth="3" fill="none" strokeLinecap="round" />
  </svg>
);

// 💧
export const Drop: React.FC<P> = ({size = 70}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M50 8 C66 32 80 48 80 64 A30 30 0 0 1 20 64 C20 48 34 32 50 8 Z" fill="#5ec2ff" stroke="#ffffff" strokeWidth="3" />
    <ellipse cx="38" cy="62" rx="7" ry="12" fill="#ffffff" opacity="0.7" transform="rotate(20 38 62)" />
  </svg>
);

// ⏩
export const FastForward: React.FC<P> = ({size = 40}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M10 20 L50 50 L10 80 Z M50 20 L90 50 L50 80 Z" fill="#ffffff" />
  </svg>
);

// down-pointing arrow for the CTA
export const ArrowDown: React.FC<P> = ({size = 60}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M50 8 V70" stroke="#ffd98a" strokeWidth="14" strokeLinecap="round" />
    <path d="M18 56 L50 92 L82 56 Z" fill="#ffd98a" />
  </svg>
);
