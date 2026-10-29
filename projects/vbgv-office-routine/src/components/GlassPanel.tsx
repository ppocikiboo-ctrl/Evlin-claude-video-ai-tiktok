// Floating holographic glass panel: ~35% glass, neon pink border, HUD
// corner brackets, scan lines and three ways to switch on.
import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import type {PanelCue} from '../timeline';
import {C} from '../theme';

export type Entrance = 'open' | 'slideRight' | 'scan';

type Props = {
  cue: PanelCue;
  entrance: Entrance;
  cx: number;
  cy: number;
  width: number;
  height: number;
  exitAt?: number;
  children: React.ReactNode;
};

const ease = Easing.bezier(0.16, 1, 0.3, 1);

export const GlassPanel: React.FC<Props> = ({cue, entrance, cx, cy, width, height, exitAt, children}) => {
  const f = useCurrentFrame();
  const startAt = entrance === 'slideRight' ? cue.open - 12 : cue.open;
  if (f < startAt) return null;

  let transform = '';
  let clip = 'none';
  let scanY: number | null = null;
  if (entrance === 'open') {
    // hologram switches on: a bright line that unfolds vertically
    const sy = interpolate(f, [cue.open, cue.open + 8], [0.03, 1], {extrapolateRight: 'clamp', easing: ease});
    const sx = interpolate(f, [cue.open, cue.open + 4], [0.4, 1], {extrapolateRight: 'clamp', easing: ease});
    transform = `scale(${sx}, ${sy})`;
  } else if (entrance === 'slideRight') {
    const x = interpolate(f, [cue.open - 12, cue.open], [width + 200, 0], {extrapolateRight: 'clamp', easing: ease});
    const skew = interpolate(f, [cue.open - 12, cue.open], [-10, 0], {extrapolateRight: 'clamp'});
    transform = `translateX(${x}px) skewX(${skew}deg)`;
  } else {
    // digital scan: revealed top to bottom behind a bright scan line
    const p = interpolate(f, [cue.open, cue.open + 14], [0, 1], {extrapolateRight: 'clamp', easing: Easing.inOut(Easing.quad)});
    clip = `inset(0 0 ${(1 - p) * 100}% 0 round 28px)`;
    if (p < 1) scanY = p * height;
  }

  // neon flicker while powering up, then a steady glow
  const flicker = f < cue.open + 6 ? [1, 0.35, 1, 0.6, 1, 0.85][Math.max(0, f - cue.open)] ?? 1 : 1;
  const exit = exitAt ? interpolate(f, [exitAt - 6, exitAt], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1;
  if (exit <= 0) return null;
  const glint = interpolate(f, [cue.done, cue.done + 12], [-0.4, 1.4], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scanBar = ((f - cue.open) % 40) / 40;
  const bob = Math.sin(f / 14) * 4; // gentle floating

  return (
    <div
      style={{
        position: 'absolute',
        left: cx - width / 2,
        top: cy - height / 2 + bob,
        width,
        height,
        opacity: exit,
        transform,
        transformOrigin: 'center',
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          clipPath: clip,
          borderRadius: 28,
          overflow: 'hidden',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.26) 0%, rgba(200,160,255,0.16) 55%, rgba(190,150,255,0.18) 100%)',
          backdropFilter: 'blur(10px) saturate(1.25)',
          WebkitBackdropFilter: 'blur(10px) saturate(1.25)',
          border: `3px solid ${C.neonPink}`,
          boxShadow: `0 0 ${16 * flicker}px ${C.neonPink}, 0 0 ${44 * flicker}px rgba(163,91,255,0.55), inset 0 0 26px rgba(163,91,255,0.35)`,
        }}
      >
        {/* scan lines */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'repeating-linear-gradient(0deg, rgba(255,255,255,0.07) 0px, rgba(255,255,255,0.07) 1px, transparent 2px, transparent 5px)',
          }}
        />
        {/* travelling scan bar */}
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: `${scanBar * 130 - 15}%`,
            height: 26,
            background: 'linear-gradient(180deg, transparent, rgba(220,200,255,0.28), transparent)',
          }}
        />
        {/* glint once the panel is fully on */}
        <div
          style={{
            position: 'absolute',
            top: -40,
            bottom: -40,
            width: 120,
            left: `${glint * 100}%`,
            transform: 'skewX(-20deg)',
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.45), transparent)',
          }}
        />
        <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          {children}
        </div>
      </div>
      {scanY !== null && (
        <div
          style={{
            position: 'absolute',
            left: -20,
            right: -20,
            top: scanY - 3,
            height: 6,
            borderRadius: 3,
            background: '#fff',
            boxShadow: `0 0 14px #fff, 0 0 30px ${C.neonPink}`,
          }}
        />
      )}
      <HudCorners flicker={flicker} />
    </div>
  );
};

const HudCorners: React.FC<{flicker: number}> = ({flicker}) => {
  const s = 30;
  const common: React.CSSProperties = {position: 'absolute', width: s, height: s, borderColor: '#fff', borderStyle: 'solid', opacity: 0.9 * flicker, filter: `drop-shadow(0 0 6px ${C.neonPink})`};
  return (
    <>
      <div style={{...common, left: -12, top: -12, borderWidth: '4px 0 0 4px', borderTopLeftRadius: 10}} />
      <div style={{...common, right: -12, top: -12, borderWidth: '4px 4px 0 0', borderTopRightRadius: 10}} />
      <div style={{...common, left: -12, bottom: -12, borderWidth: '0 0 4px 4px', borderBottomLeftRadius: 10}} />
      <div style={{...common, right: -12, bottom: -12, borderWidth: '0 4px 4px 0', borderBottomRightRadius: 10}} />
    </>
  );
};
