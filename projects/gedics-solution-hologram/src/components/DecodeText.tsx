// Digital text reveal: characters type in left to right, the next few flash
// as random glyphs first, inline icons pop in when reached. Once the panel is
// fully on the text pulses with the beat.
import React from 'react';
import {interpolate, random, useCurrentFrame} from 'remotion';
import {BEAT} from '../timeline';
import {C, FONT} from '../theme';

export type Run = string | {icon: React.ReactNode};
type Props = {
  lines: Run[][];
  start: number;
  end: number;
  size: number;
  align?: 'center' | 'left';
};

const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&*+=<>/';

export const DecodeText: React.FC<Props> = ({lines, start, end, size, align = 'center'}) => {
  const f = useCurrentFrame();
  const total = lines.flat().reduce((n, r) => n + (typeof r === 'string' ? r.length : 1), 0);
  const shown = interpolate(f, [start, end], [0, total], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const pulse = f >= end ? 1 + 0.035 * Math.exp((-(f % BEAT) / BEAT) * 5) : 1;

  let idx = 0;
  return (
    <div
      style={{
        fontFamily: FONT,
        fontWeight: 900,
        fontSize: size,
        lineHeight: 1.12,
        color: C.white,
        textAlign: align,
        letterSpacing: 0.5,
        transform: `scale(${pulse})`,
        textShadow: `0 0 10px rgba(255,79,184,0.95), 0 0 26px rgba(255,79,184,0.6), 0 3px 6px rgba(40,0,30,0.7)`,
      }}
    >
      {lines.map((line, li) => (
        <div key={li} style={{whiteSpace: 'nowrap', display: 'flex', justifyContent: align === 'center' ? 'center' : 'flex-start', alignItems: 'center'}}>
          {line.map((run, ri) => {
            if (typeof run !== 'string') {
              const my = idx++;
              const p = interpolate(shown - my, [0, 0.6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
              const pop = p < 1 ? 0.3 + p * 0.95 : 1;
              return (
                <span key={ri} style={{display: 'inline-flex', marginLeft: size * 0.18, transform: `scale(${pop})`, opacity: p}}>
                  {run.icon}
                </span>
              );
            }
            return (
              <span key={ri}>
                {run.split('').map((ch, ci) => {
                  const my = idx++;
                  const d = shown - my;
                  if (ch === ' ') return <span key={ci}>{'\u00a0'}</span>;
                  if (d >= 1) return <span key={ci}>{ch}</span>;
                  if (d > -3) {
                    // scrambled glyph at the typing frontier, laid over the
                    // real (hidden) character so the line never reflows
                    const g = GLYPHS[Math.floor(random(`${my}-${f}`) * GLYPHS.length)];
                    return (
                      <span key={ci} style={{position: 'relative'}}>
                        <span style={{opacity: 0}}>{ch}</span>
                        <span style={{position: 'absolute', left: 0, color: C.pink, opacity: 0.55 + 0.15 * (d + 3)}}>{g}</span>
                      </span>
                    );
                  }
                  return (
                    <span key={ci} style={{opacity: 0}}>
                      {ch}
                    </span>
                  );
                })}
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};
