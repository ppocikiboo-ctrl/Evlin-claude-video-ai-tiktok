// v2 "make them want to buy" layers: relatable pain points (no time to jog,
// snack temptation), a daily-routine checklist that ticks off with rising
// dings, and a CTA with a finger tapping the product bag. None of these say
// or show that VBGV causes weight loss, appetite control or fullness.
import React from 'react';
import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {CHECKLIST, CTA_TAP, LINES, SNACKS_AT} from '../timeline';
import {FONT} from '../theme';
import {Star4} from './Icons';
import {BubbleTea, Clock, Cookie, Donut, Fries, PriceTag, Runner, TapFinger} from './VbgvIcons';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// ------------------------------------------------------------------ no time to jog

// A runner with a "no" stamp and a clock spinning far too fast, on the empty
// cabinet side of the frame.
export const NoTimeJog: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {open, done, out} = LINES.joging;
  if (f < open || f >= out) return null;
  const pop = spring({frame: f - open, fps, config: {damping: 9, stiffness: 200}});
  const stamp = f < done ? 0 : spring({frame: f - done, fps, config: {damping: 7, stiffness: 300}});
  const a = interpolate(f, [out - 5, out], [1, 0], clamp);
  const spin = (f - open) / 6; // ~5 turns a second: time flying by
  return (
    <div style={{position: 'absolute', left: 760, top: 560, opacity: a, transform: `scale(${pop})`}}>
      <div style={{position: 'relative', width: 260, height: 300}}>
        <div style={{position: 'absolute', left: 20, top: 0, width: 220, height: 220, borderRadius: '50%', background: 'rgba(90,30,160,0.75)', border: '4px solid #fff', boxShadow: '0 0 24px rgba(139,61,255,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <Runner size={150} />
        </div>
        {/* "no" stamp */}
        <svg width={240} height={240} viewBox="-50 -50 100 100" style={{position: 'absolute', left: 10, top: -10, transform: `scale(${1.6 - 0.6 * stamp}) rotate(-12deg)`, opacity: Math.min(1, stamp * 1.5)}}>
          <circle r="44" fill="none" stroke="#ff3d6e" strokeWidth="9" />
          <path d="M-31 -31 L31 31" stroke="#ff3d6e" strokeWidth="9" strokeLinecap="round" />
        </svg>
        <div style={{position: 'absolute', left: 150, top: 170, transform: `rotate(${Math.sin(f / 2) * 8}deg)`}}>
          <Clock size={110} t={spin} />
        </div>
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ snack temptation

// Snacks pop up around her, wobbling temptingly, then drift away. This is
// a relatable moment only, with no "craving control" message attached.
const SNACKS: {x: number; y: number; node: React.ReactNode; tilt: number}[] = [
  {x: 140, y: 720, node: <Donut size={130} />, tilt: -12},
  {x: 930, y: 660, node: <BubbleTea size={130} />, tilt: 10},
  {x: 120, y: 1060, node: <Fries size={120} />, tilt: 8},
  {x: 950, y: 1010, node: <Cookie size={120} />, tilt: -8},
];

export const SnackTemptation: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {out} = LINES.snek;
  if (f < SNACKS_AT[0] || f >= out) return null;
  return (
    <>
      {SNACKS.map((s, i) => {
        const at = SNACKS_AT[i];
        if (f < at) return null;
        const pop = spring({frame: f - at, fps, config: {damping: 6, stiffness: 220}});
        const leave = interpolate(f, [out - 18 + i * 2, out - 6 + i * 2], [0, 1], {...clamp, easing: Easing.in(Easing.quad)});
        const wobble = Math.sin((f - at) / 4 + i) * 10;
        const bob = Math.sin((f - at) / 9 + i * 1.3) * 12;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: s.x - 70 + (s.x < 540 ? -leave * 260 : leave * 260),
              top: s.y - 70 + bob - leave * 80,
              transform: `scale(${pop * (1 - leave * 0.4)}) rotate(${s.tilt + wobble}deg)`,
              opacity: 1 - leave,
              filter: 'drop-shadow(0 10px 14px rgba(30,0,40,0.45))',
            }}
          >
            <div style={{position: 'absolute', left: -14, top: -14, width: 168, height: 168, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,255,255,0.75), rgba(255,255,255,0) 70%)'}} />
            <div style={{position: 'relative'}}>{s.node}</div>
          </div>
        );
      })}
    </>
  );
};

// ------------------------------------------------------------------ routine checklist

const ITEMS = ['Jalan kaki 10 minit', 'Makan seimbang', 'VBGV selepas sarapan*', 'Minum air cukup'];

export const RoutineChecklist: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {open, out, ticks} = CHECKLIST;
  if (f < open || f >= out) return null;
  const pop = spring({frame: f - open, fps, config: {damping: 11, stiffness: 180}});
  const a = interpolate(f, [out - 6, out], [1, 0], clamp);
  const allDone = f >= ticks[ticks.length - 1];
  return (
    <div style={{position: 'absolute', left: 540, top: 150, transform: `translateX(-50%) scale(${pop})`, transformOrigin: 'top center', opacity: a}}>
      <div
        style={{
          width: 820,
          padding: '22px 36px 26px',
          borderRadius: 30,
          background: 'linear-gradient(135deg, rgba(60,20,120,0.82), rgba(110,50,190,0.78))',
          border: `3px solid ${allDone ? '#ffd98a' : '#c6a4ff'}`,
          boxShadow: `0 0 ${allDone ? 30 : 18}px rgba(139,61,255,0.7), 0 12px 24px rgba(20,0,40,0.45)`,
          fontFamily: FONT,
          color: '#fff',
        }}
      >
        <div style={{fontWeight: 900, fontSize: 46, marginBottom: 10, display: 'flex', alignItems: 'center', gap: 12}}>
          RUTIN HARIAN SAYA <Star4 size={36} color="#ffd98a" />
        </div>
        {ITEMS.map((item, i) => {
          const t = ticks[i];
          const done = f >= t;
          const s = done ? spring({frame: f - t, fps, config: {damping: 8, stiffness: 260}}) : 0;
          const draw = interpolate(f, [t, t + 6], [0, 1], clamp);
          return (
            <div key={item} style={{display: 'flex', alignItems: 'center', gap: 18, height: 60, transform: `scale(${1 + 0.06 * Math.sin(s * Math.PI)})`, transformOrigin: 'left center'}}>
              <svg width={46} height={46} viewBox="0 0 46 46">
                <rect x={3} y={3} width={40} height={40} rx={10} fill={done ? '#ffd98a' : 'rgba(255,255,255,0.15)'} stroke="#ffffff" strokeWidth={3} />
                <path d="M11 24 L20 33 L36 13" fill="none" stroke="#4a1a8c" strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} />
              </svg>
              <span style={{fontWeight: done ? 900 : 700, fontSize: 42, opacity: done ? 1 : 0.55, textShadow: done ? '0 0 12px rgba(255,217,138,0.6)' : 'none'}}>{item}</span>
            </div>
          );
        })}
      </div>
      <div style={{marginTop: 10, textAlign: 'center', fontFamily: FONT, fontWeight: 700, fontSize: 28, color: '#fff', textShadow: '0 2px 6px rgba(20,0,40,0.9)', opacity: interpolate(f, [ticks[2], ticks[2] + 8], [0, 1], clamp)}}>
        *Ikut arahan pada label produk
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ CTA: price tag + tap

export const CtaExtras: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {open, done} = LINES.cta;
  if (f < open) return null;
  // price tag swings in on a string above the CTA panel
  const tagIn = f < done ? 0 : spring({frame: f - done, fps, config: {damping: 6, stiffness: 160}});
  const swing = Math.sin((f - done) / 5) * 10 * Math.exp(-(f - done) / 30);
  // finger slides toward the bottom-left product bag and taps it
  const move = interpolate(f, [done, CTA_TAP], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const press = interpolate(f, [CTA_TAP - 2, CTA_TAP, CTA_TAP + 4], [0, 1, 0], clamp);
  const fx = 640 - move * 470;
  const fy = 1700 - move * 20;
  const ripple = interpolate(f, [CTA_TAP, CTA_TAP + 18], [0, 1], clamp);
  return (
    <>
      <div style={{position: 'absolute', left: 820, top: 1250, transformOrigin: '10px 0', transform: `scale(${tagIn}) rotate(${-12 + swing}deg)`}}>
        <PriceTag size={190} label="PROMO" />
      </div>
      {f >= done && (
        <>
          {ripple > 0 && ripple < 1 && (
            <>
              {[0, 0.25].map((d, i) => {
                const r = Math.max(0, ripple - d);
                return <div key={i} style={{position: 'absolute', left: fx - 20 - r * 90, top: fy - 50 - r * 90, width: 40 + r * 180, height: 40 + r * 180, borderRadius: '50%', border: `5px solid rgba(255,217,138,${1 - r})`}} />;
              })}
              {Array.from({length: 8}, (_, i) => {
                const ang = (i / 8) * Math.PI * 2;
                return <Star4 key={i} size={26} color={i % 2 ? '#ffd98a' : '#fff'} style={{position: 'absolute', left: fx + Math.cos(ang) * ripple * 150 - 13, top: fy - 30 + Math.sin(ang) * ripple * 150 - 13, opacity: 1 - ripple}} />;
              })}
            </>
          )}
          <div style={{position: 'absolute', left: fx - 30, top: fy - 40, transform: `scale(${1 - press * 0.15}) rotate(-15deg)`, opacity: interpolate(f, [done, done + 6], [0, 1], clamp), filter: 'drop-shadow(0 8px 10px rgba(20,0,40,0.5))'}}>
            <TapFinger size={120} />
          </div>
        </>
      )}
    </>
  );
};
