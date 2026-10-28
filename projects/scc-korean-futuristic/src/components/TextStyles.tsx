// Six different text treatments, one per line, so no two lines enter the
// same way. Every style reads its timings from a Line cue:
//   open -> KLIK (thing appears), type -> TIK-TIK (text moves in), done -> TING.
import React from 'react';
import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Line} from '../timeline';
import {FONT} from '../theme';
import {DecodeText} from './DecodeText';
import {GlassPanel} from './GlassPanel';
import {Star4} from './Icons';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const SHADOW = '0 0 10px rgba(255,79,184,0.9), 0 0 24px rgba(255,79,184,0.55), 0 3px 6px rgba(40,0,40,0.7)';

const exitFade = (f: number, out: number, len = 8) => interpolate(f, [out - len, out], [1, 0], clamp);

// -------------------------------------------------------------- 1. hologram

export const HologramText: React.FC<{line: Line; cx: number; cy: number; width: number; height: number; lines: React.ComponentProps<typeof DecodeText>['lines']; size: number}> = ({
  line,
  cx,
  cy,
  width,
  height,
  lines,
  size,
}) => (
  <GlassPanel cue={line} entrance="open" cx={cx} cy={cy} width={width} height={height} exitAt={line.out}>
    <DecodeText lines={lines} start={line.type} end={line.done - 2} size={size} />
  </GlassPanel>
);

// -------------------------------------------------------------- 2. glass bubble

export const BubbleText: React.FC<{line: Line; cx: number; cy: number; rows: React.ReactNode[][]; size: number}> = ({line, cx, cy, rows, size}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (f < line.open || f >= line.out) return null;
  const s = spring({frame: f - line.open, fps, config: {damping: 7, stiffness: 140}});
  const wob = Math.sin((f - line.open) / 2.2) * Math.exp(-(f - line.open) / 10) * 0.08;
  const popOut = interpolate(f, [line.out - 6, line.out], [1, 1.15], clamp);
  const a = exitFade(f, line.out, 6);
  const words = rows.flat().length;
  let w = 0;
  return (
    <div style={{position: 'absolute', left: cx, top: cy, transform: `translate(-50%, -50%) scale(${s * popOut * (1 + wob)}, ${s * popOut * (1 - wob)})`, opacity: a}}>
      <div
        style={{
          position: 'relative',
          padding: '30px 58px',
          borderRadius: 120,
          background: 'radial-gradient(ellipse at 30% 20%, rgba(255,255,255,0.55), rgba(255,205,235,0.2) 45%, rgba(200,170,255,0.25) 100%)',
          border: '2.5px solid rgba(255,255,255,0.85)',
          boxShadow: '0 0 24px rgba(255,120,210,0.7), inset 0 0 30px rgba(255,255,255,0.35), inset -10px -14px 30px rgba(190,150,255,0.35)',
          backdropFilter: 'blur(8px)',
        }}
      >
        {/* bubble highlight */}
        <div style={{position: 'absolute', left: 40, top: 12, width: 160, height: 26, borderRadius: 20, background: 'linear-gradient(90deg, rgba(255,255,255,0.85), rgba(255,255,255,0))', transform: 'rotate(-6deg)'}} />
        <div style={{position: 'absolute', right: 46, bottom: 16, width: 18, height: 18, borderRadius: '50%', background: 'rgba(255,255,255,0.75)'}} />
        <div style={{fontFamily: FONT, fontWeight: 900, fontSize: size, lineHeight: 1.12, color: '#fff', textAlign: 'center', textShadow: SHADOW}}>
          {rows.map((row, ri) => (
            <div key={ri} style={{display: 'flex', justifyContent: 'center', alignItems: 'center', gap: size * 0.28, whiteSpace: 'nowrap'}}>
              {row.map((word, i) => {
                const at = line.type + ((line.done - line.type - 6) * w++) / Math.max(1, words - 1);
                const ws = f < at ? 0 : spring({frame: f - at, fps, config: {damping: 9, stiffness: 220}});
                return (
                  <span key={i} style={{display: 'inline-flex', transform: `scale(${ws}) translateY(${(1 - ws) * 20}px)`, opacity: Math.min(1, ws * 1.5)}}>
                    {word}
                  </span>
                );
              })}
            </div>
          ))}
        </div>
      </div>
      {/* tiny bubbles rising off it */}
      {Array.from({length: 7}, (_, i) => {
        const t = (f - line.open - i * 4) / 30;
        if (t < 0 || t > 1) return null;
        const r = 8 + (i % 3) * 6;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${10 + i * 13}%`,
              top: -t * 140,
              width: r,
              height: r,
              borderRadius: '50%',
              border: '1.5px solid rgba(255,255,255,0.9)',
              background: 'radial-gradient(circle at 30% 30%, rgba(255,255,255,0.8), rgba(255,200,235,0.15))',
              opacity: 1 - t,
            }}
          />
        );
      })}
    </div>
  );
};

// -------------------------------------------------------------- 3. zoom

export const ZoomText: React.FC<{line: Line; cx: number; cy: number; text: string; icon: React.ReactNode; size: number}> = ({line, cx, cy, text, icon, size}) => {
  const f = useCurrentFrame();
  if (f < line.open || f >= line.out) return null;
  const z = interpolate(f, [line.open, line.open + 12], [2.8, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const blur = interpolate(f, [line.open, line.open + 10], [14, 0], clamp);
  const spacing = interpolate(f, [line.type, line.done], [34, 2], {...clamp, easing: Easing.out(Easing.quad)});
  const pulse = f >= line.done ? 1 + 0.03 * Math.exp((-((f - line.done) % 15) / 15) * 5) : 1;
  const out = exitFade(f, line.out);
  const outZoom = interpolate(f, [line.out - 8, line.out], [1, 0.7], clamp);
  const iconPop = interpolate(f, [line.type + 9, line.type + 15], [0, 1], {...clamp, easing: Easing.out(Easing.back(3))});
  const burst = interpolate(f, [line.done, line.done + 14], [0, 1], clamp);
  return (
    <div style={{position: 'absolute', left: cx, top: cy, transform: `translate(-50%, -50%) scale(${z * pulse * outZoom})`, opacity: out * interpolate(f, [line.open, line.open + 4], [0, 1], clamp), filter: `blur(${blur}px)`}}>
      {/* landing burst: rays + ring */}
      {burst > 0 && burst < 1 && (
        <svg width={700} height={300} viewBox="-350 -150 700 300" style={{position: 'absolute', left: '50%', top: '50%', transform: 'translate(-50%, -50%)', overflow: 'visible'}}>
          {Array.from({length: 16}, (_, i) => {
            const a = (i / 16) * Math.PI * 2;
            const r1 = 120 + burst * 140;
            const r2 = r1 + 40;
            return <line key={i} x1={Math.cos(a) * r1} y1={Math.sin(a) * r1 * 0.45} x2={Math.cos(a) * r2} y2={Math.sin(a) * r2 * 0.45} stroke="#fff" strokeWidth={3} opacity={1 - burst} />;
          })}
          <ellipse rx={150 + burst * 200} ry={60 + burst * 80} fill="none" stroke="#ff8fd6" strokeWidth={4} opacity={1 - burst} />
        </svg>
      )}
      <div
        style={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          gap: 18,
          whiteSpace: 'nowrap',
          fontFamily: FONT,
          fontWeight: 900,
          fontSize: size,
          letterSpacing: spacing,
          color: '#fff',
          WebkitTextStroke: '2px rgba(255,140,215,0.9)',
          textShadow: '0 0 14px rgba(255,79,184,1), 0 0 34px rgba(255,79,184,0.7), 0 0 60px rgba(190,140,255,0.6), 0 4px 8px rgba(40,0,40,0.6)',
        }}
      >
        {text}
        <span style={{display: 'inline-flex', transform: `scale(${iconPop})`}}>{icon}</span>
      </div>
    </div>
  );
};

// -------------------------------------------------------------- 4. moving digital text

export const DigitalText: React.FC<{line: Line; cx: number; cy: number; rows: string[]; size: number; width: number}> = ({line, cx, cy, rows, size, width}) => {
  const f = useCurrentFrame();
  if (f < line.open || f >= line.out) return null;
  const frameIn = interpolate(f, [line.open, line.open + 6], [0, 1], clamp);
  const out = exitFade(f, line.out);
  const total = rows.join('').length;
  const perChar = (line.done - line.type - 6) / total;
  const scan = ((f - line.open) % 24) / 24;
  const progress = interpolate(f, [line.type, line.done], [0, 1], clamp);
  let k = 0;
  return (
    <div style={{position: 'absolute', left: cx - width / 2, top: cy, transform: 'translateY(-50%)', width, opacity: out}}>
      <div
        style={{
          position: 'relative',
          padding: '22px 28px 26px',
          clipPath: `inset(0 ${(1 - frameIn) * 50}% 0 ${(1 - frameIn) * 50}%)`,
          background:
            'linear-gradient(90deg, rgba(40,10,70,0.38), rgba(70,20,110,0.28)), repeating-linear-gradient(90deg, rgba(255,255,255,0.06) 0 1px, transparent 1px 28px), repeating-linear-gradient(0deg, rgba(255,255,255,0.05) 0 1px, transparent 1px 28px)',
          borderTop: '2px solid rgba(220,190,255,0.9)',
          borderBottom: '2px solid rgba(255,140,215,0.9)',
          boxShadow: '0 0 20px rgba(190,140,255,0.45)',
        }}
      >
        {rows.map((row, ri) => (
          <div key={ri} style={{display: 'flex', justifyContent: 'center', fontFamily: FONT, fontWeight: 800, fontSize: size, letterSpacing: 3, lineHeight: 1.18, whiteSpace: 'pre'}}>
            {row.split('').map((ch, ci) => {
              const at = line.type + perChar * k++;
              const p = interpolate(f, [at, at + 6], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
              const block = p > 0 && p < 0.5;
              return (
                <span
                  key={ci}
                  style={{
                    display: 'inline-block',
                    transform: `translateX(${(1 - p) * 80}px)`,
                    opacity: p,
                    color: block ? '#ffd6f4' : '#fff',
                    background: block ? 'rgba(255,140,215,0.55)' : 'transparent',
                    textShadow: '0 0 8px rgba(200,160,255,0.95), 0 0 20px rgba(255,100,200,0.6), 0 2px 4px rgba(30,0,40,0.8)',
                  }}
                >
                  {ch}
                </span>
              );
            })}
          </div>
        ))}
        {/* scan line */}
        <div style={{position: 'absolute', left: 0, right: 0, top: `${scan * 100}%`, height: 3, background: 'rgba(255,255,255,0.7)', boxShadow: '0 0 12px #fff, 0 0 24px #ff6fcf'}} />
        {/* progress bar */}
        <div style={{position: 'absolute', left: 28, bottom: 8, height: 4, width: `calc(${progress * 100}% - 56px)`, maxWidth: 'calc(100% - 56px)', background: 'linear-gradient(90deg, #cdb6ff, #ff8fd6)', borderRadius: 2}} />
      </div>
      {/* corner brackets */}
      {[
        {left: -8, top: -8, borderWidth: '3px 0 0 3px'},
        {right: -8, top: -8, borderWidth: '3px 3px 0 0'},
        {left: -8, bottom: -8, borderWidth: '0 0 3px 3px'},
        {right: -8, bottom: -8, borderWidth: '0 3px 3px 0'},
      ].map((st, i) => (
        <div key={i} style={{position: 'absolute', width: 26, height: 26, borderStyle: 'solid', borderColor: '#fff', opacity: frameIn, filter: 'drop-shadow(0 0 6px #ff6fcf)', ...st}} />
      ))}
    </div>
  );
};

// -------------------------------------------------------------- 5. neon

const FLICKER = [1, 0.15, 1, 0.3, 0.9, 1];

export const NeonText: React.FC<{line: Line; cx: number; cy: number; rows: React.ReactNode[][]; size: number; width: number; height: number}> = ({line, cx, cy, rows, size, width, height}) => {
  const f = useCurrentFrame();
  if (f < line.open || f >= line.out) return null;
  const out = exitFade(f, line.out);
  const draw = interpolate(f, [line.open, line.open + 12], [0, 1], {...clamp, easing: Easing.inOut(Easing.quad)});
  const words = rows.flat().length;
  const hum = 0.92 + 0.08 * Math.sin(f * 2.3);
  let w = 0;
  return (
    <div style={{position: 'absolute', left: cx - width / 2, top: cy - height / 2, width, height, opacity: out}}>
      {/* neon tube frame drawing itself */}
      <svg width={width} height={height} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
        <rect x={4} y={4} width={width - 8} height={height - 8} rx={36} fill="rgba(40,0,50,0.25)" stroke="#ff6fcf" strokeWidth={5} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} style={{filter: 'drop-shadow(0 0 6px #ff6fcf) drop-shadow(0 0 18px #ff6fcf)'}} />
        <rect x={14} y={14} width={width - 28} height={height - 28} rx={28} fill="none" stroke="#cdb6ff" strokeWidth={2} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} opacity={0.8} />
      </svg>
      <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center'}}>
        {rows.map((row, ri) => (
          <div key={ri} style={{display: 'flex', alignItems: 'center', gap: size * 0.3, whiteSpace: 'nowrap', fontFamily: FONT, fontWeight: 900, fontSize: size, lineHeight: 1.15}}>
            {row.map((word, i) => {
              const at = line.type + ((line.done - line.type - 6) * w++) / Math.max(1, words - 1);
              const k = Math.floor(f - at);
              const on = k < 0 ? 0 : k < FLICKER.length ? FLICKER[k] : hum;
              return (
                <span
                  key={i}
                  style={{
                    display: 'inline-flex',
                    color: on > 0.5 ? '#fff' : 'rgba(255,200,235,0.25)',
                    WebkitTextStroke: '1.5px rgba(255,120,210,0.6)',
                    textShadow: on > 0.05 ? `0 0 4px #fff, 0 0 ${10 * on}px #ff4fb8, 0 0 ${24 * on}px #ff4fb8, 0 0 ${46 * on}px #ff4fb8` : 'none',
                    opacity: 0.35 + 0.65 * on,
                  }}
                >
                  {word}
                </span>
              );
            })}
          </div>
        ))}
      </div>
      {/* star effect around the sign once it is fully lit */}
      {f >= line.done &&
        [
          [-20, -20],
          [width - 10, 10],
          [width + 6, height - 30],
          [30, height + 4],
          [width / 2, -30],
        ].map(([x, y], i) => {
          const t = ((f - line.done - i * 3) % 24) / 24;
          const s = Math.sin(t * Math.PI);
          return <Star4 key={i} size={34 * s + 6} color={i % 2 ? '#ffd98a' : '#fff'} style={{position: 'absolute', left: x - 18, top: y - 18, opacity: s, transform: `rotate(${t * 90}deg)`}} />;
        })}
    </div>
  );
};

// -------------------------------------------------------------- 6. slide-in

export const SlideText: React.FC<{line: Line; cx: number; cy: number; width: number; height: number; words: React.ReactNode[]; size: number}> = ({line, cx, cy, width, height, words, size}) => {
  const f = useCurrentFrame();
  const slide = interpolate(f, [line.open - 12, line.open], [0, 1], clamp);
  return (
    <>
      {/* star trail behind the panel as it slides in from the left */}
      {slide > 0 && slide < 1 &&
        Array.from({length: 8}, (_, i) => {
          const x = cx - width / 2 + (slide - 1) * (width + 200) - i * 40;
          return <Star4 key={i} size={30 - i * 3} color={i % 2 ? '#ffd98a' : '#fff'} style={{position: 'absolute', left: x, top: cy - 15 + Math.sin(i * 1.7) * 40, opacity: 1 - i / 8}} />;
        })}
      {/* the closing line stays on screen to the last frame, so no exit */}
      <GlassPanel cue={line} entrance="slideLeft" cx={cx} cy={cy} width={width} height={height}>
        <div style={{display: 'flex', alignItems: 'center', gap: size * 0.28, fontFamily: FONT, fontWeight: 900, fontSize: size, color: '#fff', textShadow: SHADOW, whiteSpace: 'nowrap'}}>
          {words.map((word, i) => {
            const at = line.type + ((line.done - line.type - 6) * i) / Math.max(1, words.length - 1);
            const p = interpolate(f, [at, at + 8], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
            return (
              <span key={i} style={{display: 'inline-flex', transform: `translateX(${(1 - p) * -120}px) skewX(${(1 - p) * 20}deg)`, opacity: p}}>
                {word}
              </span>
            );
          })}
        </div>
      </GlassPanel>
    </>
  );
};
