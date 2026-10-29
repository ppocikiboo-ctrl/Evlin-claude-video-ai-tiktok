// Emoji-style icons as inline SVG so the render looks the same on every
// machine, with or without an emoji font.
import React from 'react';

type P = {size?: number; style?: React.CSSProperties};

const HEART = 'M50 88 C20 66 6 50 6 31 C6 16 18 6 31 6 C40 6 46 11 50 18 C54 11 60 6 69 6 C82 6 94 16 94 31 C94 50 80 66 50 88 Z';

export const PinkHeart: React.FC<P & {color?: string; glow?: boolean}> = ({size = 60, style, color, glow = true}) => {
  const id = React.useId();
  return (
    <svg width={size} height={size} viewBox="0 0 100 94" style={{overflow: 'visible', ...style}}>
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={color ?? '#ffb3dc'} />
          <stop offset="1" stopColor={color ?? '#ff3fa4'} />
        </linearGradient>
      </defs>
      <path d={HEART} fill={`url(#${id})`} style={glow ? {filter: 'drop-shadow(0 0 8px rgba(255,80,180,0.9))'} : undefined} />
      <ellipse cx="30" cy="26" rx="10" ry="6" fill="#fff" opacity="0.55" transform="rotate(-30 30 26)" />
    </svg>
  );
};

export const RedHeart: React.FC<P> = (p) => <PinkHeart {...p} color="#ff2e5b" />;

export const HeartOutline: React.FC<P & {progress?: number; stroke?: string}> = ({size = 200, style, progress = 1, stroke = '#ff6fc7'}) => (
  <svg width={size} height={size * 0.94} viewBox="0 0 100 94" style={{overflow: 'visible', ...style}}>
    <path
      d={HEART}
      fill="none"
      stroke={stroke}
      strokeWidth={1.6}
      pathLength={1}
      strokeDasharray={1}
      strokeDashoffset={1 - progress}
      strokeLinecap="round"
      style={{filter: `drop-shadow(0 0 4px ${stroke}) drop-shadow(0 0 10px ${stroke})`}}
    />
  </svg>
);

export const TwinHearts: React.FC<P> = ({size = 70, style}) => (
  <div style={{position: 'relative', width: size * 1.35, height: size, ...style}}>
    <PinkHeart size={size * 0.85} style={{position: 'absolute', left: 0, top: size * 0.08}} />
    <RedHeart size={size * 0.85} style={{position: 'absolute', left: size * 0.5, top: 0}} />
  </div>
);

export const Sparkles: React.FC<P> = ({size = 60, style}) => {
  const star = (cx: number, cy: number, r: number) => {
    const t = r * 0.26;
    return `M${cx} ${cy - r} Q${cx + t} ${cy - t} ${cx + r} ${cy} Q${cx + t} ${cy + t} ${cx} ${cy + r} Q${cx - t} ${cy + t} ${cx - r} ${cy} Q${cx - t} ${cy - t} ${cx} ${cy - r} Z`;
  };
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" style={{overflow: 'visible', ...style}}>
      <g fill="#ffd36e" style={{filter: 'drop-shadow(0 0 6px rgba(255,210,110,0.9))'}}>
        <path d={star(42, 56, 40)} />
        <path d={star(80, 20, 17)} />
        <path d={star(82, 80, 12)} />
      </g>
    </svg>
  );
};

export const Star4: React.FC<P & {color?: string}> = ({size = 30, style, color = '#fff'}) => (
  <svg width={size} height={size} viewBox="-50 -50 100 100" style={{overflow: 'visible', ...style}}>
    <path d="M0 -50 Q8 -8 50 0 Q8 8 0 50 Q-8 8 -50 0 Q-8 -8 0 -50 Z" fill={color} style={{filter: `drop-shadow(0 0 6px ${color})`}} />
  </svg>
);

export const RainbowIcon: React.FC<P> = ({size = 70, style}) => {
  const cols = ['#ff9ec7', '#ffc79e', '#fff1a1', '#a9f0c8', '#a8d8ff', '#c9b2ff'];
  return (
    <svg width={size} height={size * 0.62} viewBox="0 0 100 62" style={{overflow: 'visible', ...style}}>
      {cols.map((c, i) => (
        <path key={c} d={`M${8 + i * 5} 58 A${42 - i * 5} ${42 - i * 5} 0 0 1 ${92 - i * 5} 58`} fill="none" stroke={c} strokeWidth={5} />
      ))}
      <ellipse cx="14" cy="56" rx="13" ry="7" fill="#fff" />
      <ellipse cx="86" cy="56" rx="13" ry="7" fill="#fff" />
    </svg>
  );
};

export const Gift: React.FC<P & {lid?: number}> = ({size = 70, style, lid = 0}) => (
  <svg width={size} height={size} viewBox="0 0 100 100" style={{overflow: 'visible', ...style}}>
    <defs>
      <linearGradient id="giftBody" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor="#ff7cc4" />
        <stop offset="1" stopColor="#d9268a" />
      </linearGradient>
    </defs>
    <rect x="14" y="46" width="72" height="48" rx="5" fill="url(#giftBody)" />
    <rect x="45" y="46" width="10" height="48" fill="#ffd98a" />
    <g transform={`translate(0 ${-lid * 14}) rotate(${-lid * 8} 50 40)`}>
      <rect x="8" y="32" width="84" height="16" rx="4" fill="#ff5fb4" />
      <rect x="45" y="32" width="10" height="16" fill="#ffe3a6" />
      <path d="M50 32 C38 14 22 18 28 28 C32 34 44 33 50 32 Z" fill="#ffd98a" />
      <path d="M50 32 C62 14 78 18 72 28 C68 34 56 33 50 32 Z" fill="#ffd98a" />
    </g>
  </svg>
);

export const ShoppingBag: React.FC<P> = ({size = 60, style}) => (
  <svg width={size} height={size} viewBox="0 0 100 100" style={{overflow: 'visible', ...style}}>
    <path d="M34 36 V28 A16 16 0 0 1 66 28 V36" fill="none" stroke="#a86b10" strokeWidth={7} strokeLinecap="round" />
    <rect x="14" y="32" width="72" height="62" rx="9" fill="#ffc42a" />
    <rect x="14" y="32" width="72" height="12" rx="6" fill="#ffdc78" />
  </svg>
);

// 👀 two eyes glancing to the side
export const Eyes: React.FC<P & {look?: number}> = ({size = 70, style, look = 1}) => (
  <svg width={size * 1.2} height={size} viewBox="0 0 120 100" style={{overflow: 'visible', ...style}}>
    {[30, 86].map((cx) => (
      <g key={cx}>
        <ellipse cx={cx} cy={50} rx={24} ry={36} fill="#ffffff" stroke="#5b3a55" strokeWidth={4} />
        <ellipse cx={cx + 9 * look} cy={56} rx={11} ry={15} fill="#3a2234" />
        <circle cx={cx + 13 * look} cy={50} r={4} fill="#ffffff" />
      </g>
    ))}
  </svg>
);
