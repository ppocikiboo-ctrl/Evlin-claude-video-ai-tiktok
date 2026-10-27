/* Audio engine: original synthesised background music (luxury K-beauty style,
 * dreamy electric piano, ambient pads, soft beat, ~100 BPM), synthesised
 * cinematic sound effects, mixing and limiting. The same scheduler drives
 * live preview (AudioContext) and export (OfflineAudioContext), so what you
 * hear is exactly what is rendered.
 *
 * All music and effects are generated from oscillators and noise in code:
 * no samples or third-party recordings are used. */
window.NYO = window.NYO || {};

NYO.SFX_TYPES = {
  shimmer: 'Soft cinematic shimmer',
  whoosh: 'Airy whoosh',
  swoosh: 'Gentle swoosh',
  sparkle: 'Subtle sparkle',
  pop: 'Delicate digital pop',
  riseShimmer: 'Rising shimmer',
  chime: 'Glass chime',
  tick: 'Sparkle tick',
  piano: 'Piano resolution'
};

NYO.AudioEngine = (function () {
  const mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);

  function prng(seed) {
    let s = seed >>> 0;
    return () => {
      s = (s + 0x6D2B79F5) >>> 0;
      let t = s;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function noiseBuffer(ctx, seconds, seed) {
    const len = Math.floor(ctx.sampleRate * seconds);
    const buf = ctx.createBuffer(2, len, ctx.sampleRate);
    for (let ch = 0; ch < 2; ch++) {
      const r = prng(seed + ch * 101);
      const d = buf.getChannelData(ch);
      for (let i = 0; i < len; i++) d[i] = r() * 2 - 1;
    }
    return buf;
  }

  function reverbIR(ctx, seconds, decay, seed) {
    const len = Math.floor(ctx.sampleRate * seconds);
    const buf = ctx.createBuffer(2, len, ctx.sampleRate);
    for (let ch = 0; ch < 2; ch++) {
      const r = prng(seed + ch * 7);
      const d = buf.getChannelData(ch);
      let lp = 0;
      for (let i = 0; i < len; i++) {
        const x = i / len;
        lp = lp * 0.55 + (r() * 2 - 1) * 0.45; // darker tail, no harsh highs
        d[i] = lp * Math.pow(1 - x, decay) * (i < ctx.sampleRate * 0.01 ? i / (ctx.sampleRate * 0.01) : 1);
      }
    }
    return buf;
  }

  /* Build the mixer graph. Returns nodes to schedule into. */
  function buildGraph(ctx, dest, project) {
    const a = project.audio;
    const master = ctx.createGain();
    master.gain.value = a.master;
    const comp = ctx.createDynamicsCompressor(); // gentle glue
    comp.threshold.value = -18; comp.knee.value = 12; comp.ratio.value = 2.5;
    comp.attack.value = 0.02; comp.release.value = 0.25;
    const limiter = ctx.createDynamicsCompressor(); // clip prevention
    limiter.threshold.value = -2; limiter.knee.value = 0; limiter.ratio.value = 20;
    limiter.attack.value = 0.002; limiter.release.value = 0.1;
    const softTop = ctx.createBiquadFilter(); // tame harsh highs overall
    softTop.type = 'lowpass'; softTop.frequency.value = 12500; softTop.Q.value = 0.5;
    master.connect(comp); comp.connect(softTop); softTop.connect(limiter); limiter.connect(dest);

    const musicBus = ctx.createGain(); musicBus.gain.value = a.musicVolume;
    const musicFade = ctx.createGain();
    musicBus.connect(musicFade); musicFade.connect(master);

    const sfxBus = ctx.createGain(); sfxBus.gain.value = a.sfxVolume;
    const sfxTone = ctx.createBiquadFilter(); sfxTone.type = 'lowpass'; sfxTone.frequency.value = 9000;
    sfxBus.connect(sfxTone); sfxTone.connect(master);

    const verb = ctx.createConvolver();
    verb.buffer = reverbIR(ctx, 3.2, 2.6, 11);
    const verbReturn = ctx.createGain(); verbReturn.gain.value = 0.55;
    verb.connect(verbReturn);
    const musicVerbSend = ctx.createGain(); musicVerbSend.gain.value = 0.32;
    musicVerbSend.connect(verb);
    const sfxVerbSend = ctx.createGain(); sfxVerbSend.gain.value = 0.5;
    sfxVerbSend.connect(verb);
    // Reverb returns into each bus' post-fader path.
    const verbMusic = ctx.createGain(); verbMusic.gain.value = 1;
    verbReturn.connect(verbMusic); verbMusic.connect(master);

    const musicIn = ctx.createGain(); musicIn.connect(musicBus); musicIn.connect(musicVerbSend);
    const sfxIn = ctx.createGain(); sfxIn.connect(sfxBus); sfxIn.connect(sfxVerbSend);

    const noise = noiseBuffer(ctx, 2.0, 5);
    return { ctx, master, musicBus, musicFade, musicIn, sfxIn, sfxBus, noise, all: [master, comp, limiter, softTop, musicBus, musicFade, sfxBus, sfxTone, verb, verbReturn, musicVerbSend, sfxVerbSend, verbMusic, musicIn, sfxIn] };
  }

  /* ---------- instruments (each schedules at absolute ctx time `w`) ---------- */

  function env(g, w, peak, att, dec, sus, rel, len) {
    g.gain.setValueAtTime(0.0001, w);
    g.gain.linearRampToValueAtTime(peak, w + att);
    g.gain.setTargetAtTime(peak * sus, w + att, dec / 3);
    g.gain.setTargetAtTime(0.0001, w + len, rel / 4);
  }

  // Dreamy Rhodes-like electric piano: 2-op FM with tremolo.
  function ePiano(G, out, w, midi, vel, len) {
    const ctx = G.ctx, f = mtof(midi);
    const car = ctx.createOscillator(); car.frequency.value = f;
    const mod = ctx.createOscillator(); mod.frequency.value = f * 1.0;
    const modG = ctx.createGain();
    modG.gain.setValueAtTime(f * 1.6 * vel, w);
    modG.gain.exponentialRampToValueAtTime(f * 0.12, w + 0.9);
    mod.connect(modG); modG.connect(car.frequency);
    const bell = ctx.createOscillator(); bell.frequency.value = f * 4.0;
    const bellG = ctx.createGain();
    bellG.gain.setValueAtTime(0.06 * vel, w); bellG.gain.exponentialRampToValueAtTime(0.0001, w + 0.5);
    const g = ctx.createGain();
    env(g, w, 0.16 * vel, 0.006, 1.6, 0.35, 0.9, len);
    const trem = ctx.createOscillator(); trem.frequency.value = 4.2;
    const tremG = ctx.createGain(); tremG.gain.value = 0.035 * vel;
    trem.connect(tremG); tremG.connect(g.gain);
    const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 3200;
    car.connect(g); bell.connect(bellG); bellG.connect(g); g.connect(lp); lp.connect(out);
    const end = w + len + 1.2;
    [car, mod, bell, trem].forEach((o) => { o.start(w); o.stop(end); });
  }

  // Ambient pad: detuned saws through a slowly opening low-pass.
  function pad(G, out, w, midis, len, level) {
    const ctx = G.ctx;
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, w);
    g.gain.linearRampToValueAtTime(level, w + Math.min(1.4, len * 0.4));
    g.gain.setValueAtTime(level, w + len - 0.2);
    g.gain.linearRampToValueAtTime(0.0001, w + len + 1.4);
    const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.Q.value = 0.4;
    lp.frequency.setValueAtTime(500, w);
    lp.frequency.linearRampToValueAtTime(1500, w + len * 0.6);
    lp.frequency.linearRampToValueAtTime(900, w + len + 1.2);
    lp.connect(g); g.connect(out);
    midis.forEach((m, i) => {
      [-7, 7].forEach((det) => {
        const o = ctx.createOscillator(); o.type = 'sawtooth';
        o.frequency.value = mtof(m); o.detune.value = det + i;
        const og = ctx.createGain(); og.gain.value = 0.18 / midis.length;
        o.connect(og); og.connect(lp);
        o.start(w); o.stop(w + len + 1.6);
      });
    });
  }

  function bass(G, out, w, midi, len) {
    const ctx = G.ctx;
    const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.value = mtof(midi);
    const o2 = ctx.createOscillator(); o2.type = 'triangle'; o2.frequency.value = mtof(midi + 12);
    const g = ctx.createGain(); env(g, w, 0.22, 0.03, 0.6, 0.6, 0.3, len);
    const g2 = ctx.createGain(); g2.gain.value = 0.12;
    const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 420;
    o.connect(g); o2.connect(g2); g2.connect(g); g.connect(lp); lp.connect(out);
    o.start(w); o2.start(w); o.stop(w + len + 0.5); o2.stop(w + len + 0.5);
  }

  function kick(G, out, w, vel) {
    const ctx = G.ctx;
    const o = ctx.createOscillator(); o.type = 'sine';
    o.frequency.setValueAtTime(110, w); o.frequency.exponentialRampToValueAtTime(46, w + 0.14);
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, w); g.gain.linearRampToValueAtTime(0.42 * vel, w + 0.004);
    g.gain.exponentialRampToValueAtTime(0.0001, w + 0.42);
    o.connect(g); g.connect(out); o.start(w); o.stop(w + 0.5);
  }

  function noiseHit(G, out, w, type, freq, q, peak, decay, offset) {
    const ctx = G.ctx;
    const s = ctx.createBufferSource(); s.buffer = G.noise;
    const f = ctx.createBiquadFilter(); f.type = type; f.frequency.value = freq; f.Q.value = q;
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, w); g.gain.linearRampToValueAtTime(peak, w + 0.003);
    g.gain.exponentialRampToValueAtTime(0.0001, w + decay);
    s.connect(f); f.connect(g); g.connect(out);
    s.start(w, offset || 0); s.stop(w + decay + 0.05);
  }

  function snare(G, out, w, vel) {
    noiseHit(G, out, w, 'bandpass', 1700, 0.8, 0.13 * vel, 0.22, 0.3);
    const ctx = G.ctx;
    const o = ctx.createOscillator(); o.type = 'triangle'; o.frequency.value = 190;
    const g = ctx.createGain(); g.gain.setValueAtTime(0.06 * vel, w); g.gain.exponentialRampToValueAtTime(0.0001, w + 0.09);
    o.connect(g); g.connect(out); o.start(w); o.stop(w + 0.12);
  }

  function hat(G, out, w, vel) {
    noiseHit(G, out, w, 'highpass', 7000, 0.7, 0.035 * vel, 0.05, 0.9);
  }

  function bellTone(G, out, w, midi, vel, decay) {
    const ctx = G.ctx, f = mtof(midi);
    [[1, 1], [2.0, 0.25], [3.0, 0.08]].forEach(([r, a]) => {
      const o = ctx.createOscillator(); o.frequency.value = f * r;
      const g = ctx.createGain();
      g.gain.setValueAtTime(0.0001, w); g.gain.linearRampToValueAtTime(0.07 * vel * a, w + 0.005);
      g.gain.exponentialRampToValueAtTime(0.0001, w + decay / r);
      o.connect(g); g.connect(out); o.start(w); o.stop(w + decay + 0.1);
    });
  }

  /* ---------- composition ---------- */

  // Fmaj9 – Am9 – Dm9 – Bbmaj9(#11): warm, dreamy, unresolved-to-resolved.
  const PROG = [
    { root: 41, voicing: [57, 60, 64, 67], arp: [65, 69, 72, 76] },
    { root: 45, voicing: [55, 59, 60, 64], arp: [64, 67, 71, 72] },
    { root: 38, voicing: [53, 57, 60, 64], arp: [62, 65, 69, 72] },
    { root: 46, voicing: [57, 60, 62, 65], arp: [62, 65, 69, 74] }
  ];

  function scheduleMusic(G, project, from, when, dur) {
    const bpm = Math.max(90, Math.min(110, project.audio.bpm || 100));
    const beat = 60 / bpm, bar = beat * 4;
    const out = G.musicIn;
    const at = (T) => when + (T - from);
    const live = (T, len) => T + (len || 0) >= from - 0.001 && T < dur + 0.5;
    const nBars = Math.ceil(dur / bar) + 1;
    const r = prng(77);

    for (let b = 0; b < nBars; b++) {
      const T0 = b * bar;
      if (T0 > dur) break;
      const ch = PROG[b % 4];
      const lastBars = T0 > dur - bar * 1.2;
      // Pads (whole bar, overlapping tails).
      if (live(T0, bar + 1.4) && T0 >= from - 0.05) pad(G, out, at(T0), ch.voicing.map((m) => m - 12).concat([ch.voicing[3]]), bar, 0.05);
      // Electric piano: chord on 1, softer re-voice on the "and" of 2.
      const ep = [[0, 1.0, beat * 2.2], [beat * 1.5, 0.6, beat * 1.4], [beat * 3, 0.45, beat]];
      ep.forEach(([o, v, len]) => {
        const T = T0 + o;
        if (T >= from - 0.01 && T < dur - 0.3) ch.voicing.forEach((m, i) => ePiano(G, out, at(T + i * 0.012), m, v * (0.85 + r() * 0.15), len));
      });
      // Bass from bar 2.
      if (b >= 2 && !lastBars) {
        [[0, beat * 1.8], [beat * 2.5, beat * 1.2]].forEach(([o, len]) => {
          const T = T0 + o; if (T >= from - 0.01) bass(G, out, at(T), ch.root, len);
        });
      }
      // Soft modern beat from bar 2, fuller from bar 4, drops for the ending.
      const endBeat = dur - 4.2;
      if (b >= 2) {
        for (let s = 0; s < 8; s++) {
          const T = T0 + s * beat / 2;
          if (T < from - 0.01 || T > endBeat) continue;
          if (s === 0 || s === 5 || (b >= 4 && s === 4 && b % 2 === 1)) kick(G, out, at(T), s === 0 ? 1 : 0.7);
          if (b >= 4 && (s === 2 || s === 6)) snare(G, out, at(T), 0.9);
          hat(G, out, at(T), (s % 2 ? 0.55 : 1) * (b >= 4 ? 1 : 0.6));
        }
      }
      // Bell arpeggio sparkle from bar 4.
      if (b >= 4) {
        for (let s = 0; s < 8; s++) {
          const T = T0 + s * beat / 2;
          if (T < from - 0.01 || T > dur - 3.6) continue;
          bellTone(G, out, at(T), ch.arp[(s + b) % 4] + 12, 0.35 + r() * 0.2, 1.1);
        }
      }
    }
    // Airy texture bed across the whole piece.
    if (from < dur) {
      const s = G.ctx.createBufferSource(); s.buffer = G.noise; s.loop = true;
      const bp = G.ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 2200; bp.Q.value = 0.6;
      const g = G.ctx.createGain(); g.gain.value = 0.012;
      const lfo = G.ctx.createOscillator(); lfo.frequency.value = 0.12;
      const lfoG = G.ctx.createGain(); lfoG.gain.value = 900;
      lfo.connect(lfoG); lfoG.connect(bp.frequency);
      s.connect(bp); bp.connect(g); g.connect(out);
      s.start(when); lfo.start(when);
      s.stop(when + (dur - from) + 0.2); lfo.stop(when + (dur - from) + 0.2);
    }
  }

  /* ---------- sound effects ---------- */

  const SFX = {
    shimmer(G, w, gain) {
      const r = prng(Math.floor(w * 1000) + 3);
      const notes = [84, 88, 91, 93, 96, 91, 88];
      notes.forEach((m, i) => {
        const tt = w + i * 0.09 + r() * 0.03;
        bellTone(G, G.sfxIn, tt, m, 0.9 * gain, 1.6);
      });
      swell(G, w, gain * 0.5, 1.2, 1800, 5200, 'bandpass');
    },
    whoosh(G, w, gain) { swell(G, w, gain * 0.9, 0.95, 350, 2600, 'bandpass', true); },
    swoosh(G, w, gain) { swell(G, w, gain * 0.9, 0.55, 600, 3200, 'bandpass', true); },
    sparkle(G, w, gain) {
      const r = prng(Math.floor(w * 1000) + 9);
      for (let i = 0; i < 6; i++) bellTone(G, G.sfxIn, w + r() * 0.5, 91 + Math.floor(r() * 9), 0.7 * gain, 0.6);
    },
    pop(G, w, gain) {
      const ctx = G.ctx;
      const o = ctx.createOscillator(); o.type = 'sine';
      o.frequency.setValueAtTime(700, w); o.frequency.exponentialRampToValueAtTime(1250, w + 0.05);
      const g = ctx.createGain();
      g.gain.setValueAtTime(0.0001, w); g.gain.linearRampToValueAtTime(0.32 * gain, w + 0.006);
      g.gain.exponentialRampToValueAtTime(0.0001, w + 0.16);
      o.connect(g); g.connect(G.sfxIn); o.start(w); o.stop(w + 0.2);
      bellTone(G, G.sfxIn, w + 0.02, 88, 0.6 * gain, 0.5);
    },
    riseShimmer(G, w, gain) {
      swell(G, w, gain * 0.6, 0.8, 900, 4200, 'bandpass');
      [79, 84, 88, 91].forEach((m, i) => bellTone(G, G.sfxIn, w + 0.12 + i * 0.13, m, 0.55 * gain, 0.9));
    },
    chime(G, w, gain) {
      const ctx = G.ctx, f = 1318.5;
      [[1, 1, 2.4], [2.76, 0.35, 1.3], [5.4, 0.12, 0.6], [8.93, 0.05, 0.3]].forEach(([ratio, amp, dec]) => {
        const o = ctx.createOscillator(); o.frequency.value = f * ratio / 2;
        const g = ctx.createGain();
        g.gain.setValueAtTime(0.0001, w); g.gain.linearRampToValueAtTime(0.16 * amp * gain, w + 0.004);
        g.gain.exponentialRampToValueAtTime(0.0001, w + dec);
        o.connect(g); g.connect(G.sfxIn); o.start(w); o.stop(w + dec + 0.05);
      });
    },
    tick(G, w, gain) {
      bellTone(G, G.sfxIn, w, 96, 0.9 * gain, 0.35);
      bellTone(G, G.sfxIn, w + 0.035, 103, 0.35 * gain, 0.25);
    },
    piano(G, w, gain) {
      // Gentle piano resolution on F major (add9): F3 C4 A4 E5 G5 F5.
      [[53, 0], [60, 0.14], [69, 0.3], [76, 0.48], [79, 0.7], [77, 0.95]].forEach(([m, o]) => pianoNote(G, w + o, m, gain));
    }
  };

  function pianoNote(G, w, midi, gain) {
    const ctx = G.ctx, f = mtof(midi);
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, w); g.gain.linearRampToValueAtTime(0.16 * gain, w + 0.005);
    g.gain.exponentialRampToValueAtTime(0.05 * gain, w + 0.6);
    g.gain.exponentialRampToValueAtTime(0.0001, w + 3.4);
    const lp = ctx.createBiquadFilter(); lp.type = 'lowpass';
    lp.frequency.setValueAtTime(Math.min(6000, f * 6), w); lp.frequency.exponentialRampToValueAtTime(Math.min(2500, f * 2.2), w + 1.5);
    [[1, 1], [2, 0.42], [3, 0.16], [4, 0.07]].forEach(([r, a]) => {
      const o = ctx.createOscillator(); o.type = r === 1 ? 'triangle' : 'sine';
      o.frequency.value = f * r * (1 + (r - 1) * 0.0007);
      const og = ctx.createGain(); og.gain.value = a;
      o.connect(og); og.connect(lp); o.start(w); o.stop(w + 3.5);
    });
    lp.connect(g); g.connect(G.sfxIn);
  }

  function swell(G, w, gain, len, f0, f1, type, pan) {
    const ctx = G.ctx;
    const s = ctx.createBufferSource(); s.buffer = G.noise;
    const f = ctx.createBiquadFilter(); f.type = type; f.Q.value = 1.1;
    f.frequency.setValueAtTime(f0, w);
    f.frequency.exponentialRampToValueAtTime(f1, w + len * 0.55);
    f.frequency.exponentialRampToValueAtTime(f0 * 1.4, w + len);
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, w);
    g.gain.linearRampToValueAtTime(0.22 * gain, w + len * 0.5);
    g.gain.linearRampToValueAtTime(0.0001, w + len);
    let last = g;
    if (pan && ctx.createStereoPanner) {
      const p = ctx.createStereoPanner();
      p.pan.setValueAtTime(-0.6, w); p.pan.linearRampToValueAtTime(0.6, w + len);
      g.connect(p); last = p;
    }
    s.connect(f); f.connect(g); last.connect(G.sfxIn);
    s.start(w, 0.5); s.stop(w + len + 0.05);
  }

  /* ---------- public scheduling ---------- */

  /* Schedule the full mix from timeline time `from`, starting at ctx time `when`.
   * buffers: { music: AudioBuffer|null, original: AudioBuffer|null } */
  function schedule(ctx, dest, project, from, when, buffers) {
    const G = buildGraph(ctx, dest, project);
    const a = project.audio;
    const dur = project.duration;
    const sources = [];

    // Music fade-in at start and fade-out over the final seconds.
    const fadeG = G.musicFade.gain;
    const fo = Math.max(0.1, a.fadeOut);
    const atT = (T) => when + (T - from);
    const valAt = (T) => {
      let v = 1;
      if (a.fadeIn > 0 && T < a.fadeIn) v = Math.max(0.0001, T / a.fadeIn);
      if (T > dur - fo) v = Math.min(v, Math.max(0.0001, (dur - T) / fo));
      return v;
    };
    fadeG.setValueAtTime(valAt(from), when);
    if (from < a.fadeIn) fadeG.linearRampToValueAtTime(1, atT(a.fadeIn));
    if (from < dur - fo) fadeG.setValueAtTime(1, atT(dur - fo));
    fadeG.linearRampToValueAtTime(0.0001, atT(dur));

    if (a.music === 'file' && buffers && buffers.music) {
      const s = ctx.createBufferSource(); s.buffer = buffers.music;
      s.connect(G.musicBus); // uploaded track is already mixed; skip the reverb send
      const off = (a.musicOffset || 0) + from;
      if (off < buffers.music.duration) { s.start(when, off); s.stop(atT(dur) + 0.05); sources.push(s); }
    } else if (a.music === 'generated') {
      scheduleMusic(G, project, from, when, dur);
    }

    if (a.originalVolume > 0 && buffers && buffers.original) {
      const s = ctx.createBufferSource(); s.buffer = buffers.original;
      const g = ctx.createGain(); g.gain.value = a.originalVolume;
      s.connect(g); g.connect(G.master);
      if (from < buffers.original.duration) { s.start(when, from); s.stop(atT(dur)); sources.push(s); }
    }

    project.sfx.forEach((cue) => {
      const T = NYO.sfxTime(project, cue);
      if (T === null || T < from - 0.02 || T > dur) return;
      const fn = SFX[cue.type];
      if (fn) fn(G, atT(Math.max(T, from)), cue.gain == null ? 0.5 : cue.gain);
    });

    return {
      stop() {
        const t = ctx.currentTime;
        try {
          G.master.gain.cancelScheduledValues(t);
          G.master.gain.setValueAtTime(G.master.gain.value, t);
          G.master.gain.linearRampToValueAtTime(0, t + 0.04);
        } catch (e) { /* ignore */ }
        setTimeout(() => G.all.forEach((n) => { try { n.disconnect(); } catch (e) { /* ignore */ } }), 80);
      }
    };
  }

  /* Live preview of one SFX at its default level. */
  function previewSfx(ctx, project, type, gain) {
    const G = buildGraph(ctx, ctx.destination, project);
    SFX[type](G, ctx.currentTime + 0.05, gain == null ? 0.6 : gain);
    setTimeout(() => G.all.forEach((n) => { try { n.disconnect(); } catch (e) { /* ignore */ } }), 4500);
  }

  async function renderOffline(project, buffers, sampleRate) {
    sampleRate = sampleRate || 48000;
    const len = Math.ceil(project.duration * sampleRate);
    const ctx = new OfflineAudioContext(2, len, sampleRate);
    schedule(ctx, ctx.destination, project, 0, 0, buffers);
    return ctx.startRendering();
  }

  function encodeWav(buf) {
    const ch = buf.numberOfChannels, len = buf.length, sr = buf.sampleRate;
    const out = new DataView(new ArrayBuffer(44 + len * ch * 2));
    const ws = (o, s) => { for (let i = 0; i < s.length; i++) out.setUint8(o + i, s.charCodeAt(i)); };
    ws(0, 'RIFF'); out.setUint32(4, 36 + len * ch * 2, true); ws(8, 'WAVE'); ws(12, 'fmt ');
    out.setUint32(16, 16, true); out.setUint16(20, 1, true); out.setUint16(22, ch, true);
    out.setUint32(24, sr, true); out.setUint32(28, sr * ch * 2, true); out.setUint16(32, ch * 2, true);
    out.setUint16(34, 16, true); ws(36, 'data'); out.setUint32(40, len * ch * 2, true);
    const data = []; for (let c = 0; c < ch; c++) data.push(buf.getChannelData(c));
    let o = 44;
    for (let i = 0; i < len; i++) for (let c = 0; c < ch; c++) {
      const s = Math.max(-1, Math.min(1, data[c][i]));
      out.setInt16(o, s < 0 ? s * 0x8000 : s * 0x7fff, true); o += 2;
    }
    return new Blob([out.buffer], { type: 'audio/wav' });
  }

  function peak(buf) {
    let p = 0;
    for (let c = 0; c < buf.numberOfChannels; c++) {
      const d = buf.getChannelData(c);
      for (let i = 0; i < d.length; i++) { const v = Math.abs(d[i]); if (v > p) p = v; }
    }
    return p;
  }

  return { schedule, previewSfx, renderOffline, encodeWav, peak };
})();
