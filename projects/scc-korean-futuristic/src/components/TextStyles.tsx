// Six text treatments, one per line, all solid (no see-through glass), so no
// two lines enter the same way. Every style reads its timings from a Line:
//   open -> shape appears, type -> text moves in, done -> animation complete.
import React from 'react';
import {Easing, interpolate, random, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Line} from '../timeline';
import {FONT} from '../theme';
import {Star4} from './Icons';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const exitFade = (f: number, out: number, len = 8) => interpolate(f, [out - len, out], [1, 0], clamp);

// Splits rows into characters while keeping icons (non-strings) as one item.
type Row = (string | React.ReactNode)[];

// -------------------------------------------------------------- 1. sticker + bouncing letters

export const StickerText: React.FC<{line: Line; cx: number; cy: number; rows: Row[]; size: number}> = ({line, cx, cy, rows, size}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (f < line.open || f >= line.out) return null;
  const card = spring({frame: f - line.open, fps, config: {damping: 8, stiffness: 180}});
  const wiggle = Math.sin((f - line.open) / 2) * Math.exp(-(f - line.open) / 8) * 6;
  const out = exitFade(f, line.out, 6);
  const total = rows.reduce((n, r) => n + r.reduce((m: number, x) => m + (typeof x === 'string' ? x.length : 1), 0), 0);
  const per = (line.done - line.type - 6) / total;
  let k = 0;
  return (
    <div style={{position: 'absolute', left: cx, top: cy, transform: `translate(-50%, -50%) scale(${card}) rotate(${-3 + wiggle}deg)`, opacity: out}}>
      <div
        style={{
          padding: '22px 40px',
          borderRadius: 34,
          background: 'linear-gradient(180deg, #ffffff 0%, #fff0f7 100%)',
          border: '6px solid #ffffff',
          boxShadow: '0 10px 0 #ff8fc8, 0 14px 24px rgba(60,0,60,0.45)',
          fontFamily: FONT,
          fontWeight: 900,
          fontSize: size,
          lineHeight: 1.12,
          textAlign: 'center',
        }}
      >
        {rows.map((row, ri) => (
          <div key={ri} style={{display: 'flex', justifyContent: 'center', alignItems: 'center', whiteSpace: 'pre'}}>
            {row.flatMap((part, pi) => {
              const items = typeof part === 'string' ? part.split('').map((c) => (c === ' ' ? '\u00a0' : c)) : [part];
              return items.map((ch, ci) => {
                const at = line.type + per * k++;
                const s = f < at ? 0 : spring({frame: f - at, fps, config: {damping: 6, stiffness: 260}});
                return (
                  <span
                    key={`${pi}-${ci}`}
                    style={{
                      display: 'inline-flex',
                      transform: `translateY(${(1 - s) * -40}px) scale(${s})`,
                      color: ri === 0 ? '#8e2fa8' : '#e0347f',
                      textShadow: '0 3px 0 #ffd0e6',
                      marginLeft: typeof ch === 'string' ? 0 : size * 0.2,
                    }}
                  >
                    {ch}
                  </span>
                );
              });
            })}
          </div>
        ))}
      </div>
    </div>
  );
};

// -------------------------------------------------------------- 2. ribbon banner

export const RibbonText: React.FC<{line: Line; cx: number; cy: number; rows: Row[]; size: number; width: number; height: number}> = ({line, cx, cy, rows, size, width, height}) => {
  const f = useCurrentFrame();
  if (f < line.open - 4 || f >= line.out) return null;
  const unroll = interpolate(f, [line.open - 4, line.open + 6], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.4))});
  const wipe = interpolate(f, [line.type, line.done - 4], [0, 100], {...clamp, easing: Easing.inOut(Easing.quad)});
  const out = exitFade(f, line.out, 6);
  const wave = Math.sin(f / 6) * 2;
  const tail = height * 0.42;
  return (
    <div style={{position: 'absolute', left: cx - width / 2, top: cy - height / 2, width, height, opacity: out, transform: `scaleX(${unroll}) rotate(${wave * 0.3}deg)`}}>
      {/* folded tails */}
      {[-1, 1].map((side) => (
        <div
          key={side}
          style={{
            position: 'absolute',
            top: height * 0.22,
            [side < 0 ? 'left' : 'right']: -tail * 0.9,
            width: tail * 1.4,
            height: height * 0.78,
            background: '#c2186b',
            clipPath: side < 0 ? 'polygon(0 0, 100% 0, 100% 100%, 0 100%, 30% 50%)' : 'polygon(0 0, 100% 0, 70% 50%, 100% 100%, 0 100%)',
          }}
        />
      ))}
      {/* main band */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: 14,
          background: 'linear-gradient(180deg, #ff86be 0%, #f0479a 55%, #d92f84 100%)',
          boxShadow: '0 8px 0 #9e1f63, 0 14px 22px rgba(60,0,40,0.45), inset 0 4px 0 rgba(255,255,255,0.35)',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          fontFamily: FONT,
          fontWeight: 900,
          fontSize: size,
          lineHeight: 1.1,
          color: '#fff',
          textShadow: '0 3px 0 #a3125d',
          clipPath: 'inset(0 round 14px)',
        }}
      >
        <div style={{clipPath: `inset(0 ${100 - wipe}% 0 0)`}}>
          {rows.map((row, ri) => (
            <div key={ri} style={{display: 'flex', justifyContent: 'center', alignItems: 'center', gap: size * 0.25, whiteSpace: 'nowrap'}}>
              {row.map((part, i) => (
                <span key={i} style={{display: 'inline-flex'}}>
                  {part}
                </span>
              ))}
            </div>
          ))}
        </div>
        {/* stitched edges */}
        <div style={{position: 'absolute', left: 10, right: 10, top: 8, borderTop: '2px dashed rgba(255,255,255,0.6)'}} />
        <div style={{position: 'absolute', left: 10, right: 10, bottom: 8, borderTop: '2px dashed rgba(255,255,255,0.6)'}} />
      </div>
    </div>
  );
};

// -------------------------------------------------------------- 3. 3D extruded zoom

const EXTRUDE = Array.from({length: 9}, (_, i) => `${0}px ${i + 1}px 0 ${i < 4 ? '#c49bff' : '#8a55d6'}`).join(', ');

export const Extrude3DText: React.FC<{line: Line; cx: number; cy: number; text: string; icon: React.ReactNode; size: number}> = ({line, cx, cy, text, icon, size}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (f < line.open || f >= line.out) return null;
  const z = spring({frame: f - line.open, fps, config: {damping: 10, stiffness: 120}});
  const tilt = interpolate(f, [line.open, line.open + 14], [70, 0], {...clamp, easing: Easing.out(Easing.cubic)});
  const out = exitFade(f, line.out);
  const iconPop = f < line.type + 9 ? 0 : spring({frame: f - line.type - 9, fps, config: {damping: 8, stiffness: 200}});
  const land = interpolate(f, [line.done, line.done + 4, line.done + 10], [1, 0.92, 1], clamp);
  const pulse = f >= line.done + 10 ? 1 + 0.025 * Math.exp((-((f - line.done) % 15) / 15) * 5) : 1;
  const burst = interpolate(f, [line.done, line.done + 16], [0, 1], clamp);
  return (
    <div style={{position: 'absolute', left: cx, top: cy, transform: `translate(-50%, -50%)`, perspective: 900, opacity: out}}>
      {/* landing dust: little colourful dots flying out */}
      {burst > 0 &&
        burst < 1 &&
        Array.from({length: 14}, (_, i) => {
          const a = (i / 14) * Math.PI * 2;
          const r = 60 + burst * 260;
          const cols = ['#ff7fb6', '#ffd36e', '#7fe0d0', '#c49bff'];
          return <div key={i} style={{position: 'absolute', left: '50%', top: '50%', width: 14, height: 14, borderRadius: i % 2 ? 3 : 7, background: cols[i % 4], transform: `translate(${Math.cos(a) * r - 7}px, ${Math.sin(a) * r * 0.45 - 7}px) rotate(${burst * 200}deg)`, opacity: 1 - burst}} />;
        })}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 18,
          whiteSpace: 'nowrap',
          transform: `scale(${z * land * pulse}) rotateX(${tilt}deg)`,
          fontFamily: FONT,
          fontWeight: 900,
          fontSize: size,
          letterSpacing: 2,
          color: '#ffffff',
          textShadow: `${EXTRUDE}, 0 14px 18px rgba(40,0,60,0.55)`,
        }}
      >
        {text}
        <span style={{display: 'inline-flex', transform: `scale(${iconPop})`}}>{icon}</span>
      </div>
    </div>
  );
};

// -------------------------------------------------------------- 4. split-flap board

const FLAP_GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ+-';

export const FlipBoardText: React.FC<{line: Line; cx: number; cy: number; rows: string[]; tile: number}> = ({line, cx, cy, rows, tile}) => {
  const f = useCurrentFrame();
  if (f < line.open || f >= line.out) return null;
  const out = exitFade(f, line.out);
  const boardIn = interpolate(f, [line.open, line.open + 6], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.6))});
  const total = rows.join('').length;
  const per = (line.done - line.type - 8) / total;
  let k = 0;
  return (
    <div style={{position: 'absolute', left: cx, top: cy, transform: `translate(-50%, -50%) scaleY(${boardIn})`, opacity: out}}>
      <div style={{padding: 16, borderRadius: 18, background: '#2b0f3d', boxShadow: '0 8px 0 #160620, 0 14px 24px rgba(0,0,0,0.5)', display: 'flex', flexDirection: 'column', gap: 8}}>
        {rows.map((row, ri) => (
          <div key={ri} style={{display: 'flex', justifyContent: 'center', gap: 4}}>
            {row.split('').map((ch, ci) => {
              const settle = line.type + per * k++ + 6;
              const spinning = f < settle;
              const shown = ch === ' ' ? ' ' : spinning ? FLAP_GLYPHS[Math.floor(random(`${ri}-${ci}-${f}`) * FLAP_GLYPHS.length)] : ch;
              // flip: the top half folds down every frame while spinning
              const flip = spinning && f >= line.type ? (f % 2) * 40 : 0;
              const blank = f < line.type;
              return (
                <div
                  key={ci}
                  style={{
                    position: 'relative',
                    width: ch === ' ' ? tile * 0.45 : tile * 0.72,
                    height: tile,
                    borderRadius: 6,
                    background: ch === ' ' ? 'transparent' : 'linear-gradient(180deg, #5a2378 0%, #4a1a66 49%, #3a1052 51%, #451760 100%)',
                    boxShadow: ch === ' ' ? 'none' : 'inset 0 -2px 0 rgba(0,0,0,0.35)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontFamily: FONT,
                    fontWeight: 800,
                    fontSize: tile * 0.68,
                    color: spinning ? '#ffb7dc' : '#ffffff',
                    textShadow: spinning ? 'none' : '0 0 10px rgba(255,140,215,0.8)',
                    transform: `perspective(300px) rotateX(${flip}deg)`,
                  }}
                >
                  {!blank && shown}
                  {ch !== ' ' && <div style={{position: 'absolute', left: 0, right: 0, top: '50%', height: 2, background: 'rgba(0,0,0,0.45)'}} />}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
};

// -------------------------------------------------------------- 5. neon sign on a solid plate

const FLICKER = [1, 0.15, 1, 0.3, 0.9, 1];

export const NeonText: React.FC<{line: Line; cx: number; cy: number; rows: Row[]; size: number; width: number; height: number}> = ({line, cx, cy, rows, size, width, height}) => {
  const f = useCurrentFrame();
  if (f < line.open || f >= line.out) return null;
  const out = exitFade(f, line.out);
  const draw = interpolate(f, [line.open, line.open + 12], [0, 1], {...clamp, easing: Easing.inOut(Easing.quad)});
  const words = rows.flat().length;
  const hum = 0.92 + 0.08 * Math.sin(f * 2.3);
  let w = 0;
  return (
    <div style={{position: 'absolute', left: cx - width / 2, top: cy - height / 2, width, height, opacity: out}}>
      <svg width={width} height={height} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
        {/* solid dark sign plate */}
        <rect x={4} y={4} width={width - 8} height={height - 8} rx={36} fill="#24062f" opacity={draw} />
        <rect x={4} y={4} width={width - 8} height={height - 8} rx={36} fill="none" stroke="#ff6fcf" strokeWidth={5} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} style={{filter: 'drop-shadow(0 0 6px #ff6fcf) drop-shadow(0 0 18px #ff6fcf)'}} />
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

// -------------------------------------------------------------- 6. 3D button + stamp + confetti

export const ButtonText: React.FC<{line: Line; cx: number; cy: number; words: Row; size: number}> = ({line, cx, cy, words, size}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (f < line.open) return null;
  const pop = spring({frame: f - line.open, fps, config: {damping: 9, stiffness: 170}});
  // stamp: the button is pressed down when the text lands
  const press = interpolate(f, [line.done - 2, line.done, line.done + 6], [0, 1, 0], clamp);
  const shine = interpolate(f, [line.done + 4, line.done + 22], [-30, 130], clamp);
  const breathe = f > line.done + 8 ? 1 + 0.03 * Math.sin(((f - line.done) / 15) * Math.PI * 2) : 1;
  const confetti = f - line.done;
  return (
    <div style={{position: 'absolute', left: cx, top: cy, transform: `translate(-50%, -50%) scale(${pop * breathe})`}}>
      {confetti >= 0 &&
        confetti < 40 &&
        Array.from({length: 26}, (_, i) => {
          const a = -Math.PI / 2 + (random(`ca${i}`) - 0.5) * Math.PI * 1.6;
          const v = 9 + random(`cv${i}`) * 9;
          const x = Math.cos(a) * v * confetti;
          const y = Math.sin(a) * v * confetti + 0.55 * confetti * confetti;
          const cols = ['#ff7fb6', '#ffd36e', '#7fe0d0', '#c49bff', '#ffffff'];
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: '50%',
                top: '50%',
                width: 12,
                height: 18,
                borderRadius: 3,
                background: cols[i % 5],
                transform: `translate(${x}px, ${y}px) rotate(${confetti * (20 + i * 3)}deg) scaleX(${Math.cos(confetti / 3 + i)})`,
                opacity: interpolate(confetti, [28, 40], [1, 0], clamp),
              }}
            />
          );
        })}
      <div
        style={{
          position: 'relative',
          overflow: 'hidden',
          padding: '26px 56px',
          borderRadius: 999,
          background: 'linear-gradient(180deg, #ff9ccc 0%, #f45aa7 50%, #b84fe0 100%)',
          boxShadow: `0 ${12 - press * 8}px 0 #7e2fae, 0 ${18 - press * 8}px 26px rgba(40,0,60,0.5), inset 0 5px 0 rgba(255,255,255,0.45)`,
          transform: `translateY(${press * 8}px)`,
          display: 'flex',
          alignItems: 'center',
          gap: size * 0.25,
          whiteSpace: 'nowrap',
          fontFamily: FONT,
          fontWeight: 900,
          fontSize: size,
          color: '#fff',
          textShadow: '0 3px 0 #9b2c88',
        }}
      >
        {words.map((word, i) => {
          const at = line.type + ((line.done - line.type - 6) * i) / Math.max(1, words.length - 1);
          const p = f < at ? 0 : spring({frame: f - at, fps, config: {damping: 9, stiffness: 240}});
          return (
            <span key={i} style={{display: 'inline-flex', transform: `translateY(${(1 - p) * 50}px)`, opacity: Math.min(1, p * 1.5)}}>
              {word}
            </span>
          );
        })}
        <div style={{position: 'absolute', top: -20, bottom: -20, left: `${shine}%`, width: 80, background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.7), transparent)', transform: 'skewX(-20deg)'}} />
      </div>
    </div>
  );
};
