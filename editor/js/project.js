/* Project model: defaults for "Ageless by NYO3 — My Self-Care Era Before 30",
 * serialisation, and the softgel tracking data measured from the original footage. */
window.NYO = window.NYO || {};

NYO.OUT_W = 1080;
NYO.OUT_H = 1920;
NYO.FPS = 30;
NYO.PALETTE = { gold: '#D6B77A', ivory: '#FFF9F0', rose: '#E8B7BE' };

/* Softgel positions measured from the uploaded clip (864×1426, 30.13 s) with
 * template matching (OpenCV, normalised cross-correlation, every frame, kept
 * where match score ≥ 0.93, thinned to every 2nd frame). Coordinates are
 * normalised to the source frame: [time s, x 0–1, y 0–1].
 * The blister pack is only on screen at ≈0.9–2.7 s and ≈29.0–30.1 s.
 * The footage is mirrored (selfie camera), so on screen the RED column is on
 * the left and the BLACK column on the right. */
NYO.BUNDLED_TRACK = {
  signature: { width: 864, height: 1426, duration: 30.13 },
  red: [[1.0,0.5324,0.5645],[1.067,0.5336,0.5645],[1.167,0.537,0.5659],[1.233,0.5359,0.5666],[1.3,0.5347,0.5673],[1.367,0.5324,0.5673],[1.433,0.5324,0.5673],[1.5,0.5347,0.5666],[1.567,0.5359,0.5666],[1.633,0.5359,0.5666],[1.7,0.537,0.5659],[1.767,0.544,0.5631],[1.833,0.566,0.5596],[1.9,0.5775,0.5617],[1.967,0.5799,0.5624],[2.033,0.5822,0.5631],[2.1,0.5822,0.5631],[2.167,0.5822,0.5624],[2.233,0.5833,0.5617],[2.3,0.581,0.561],[2.367,0.5787,0.5603],[2.433,0.5775,0.5596],[2.5,0.5775,0.5603],[2.567,0.5764,0.5603],[2.633,0.5764,0.5589],[2.7,0.5764,0.5582],[29.133,0.537,0.5645],[29.2,0.537,0.5652],[29.267,0.5359,0.5659],[29.333,0.5359,0.5666],[29.4,0.5324,0.5666],[29.467,0.5324,0.5673],[29.533,0.5347,0.5666],[29.6,0.5359,0.5666],[29.667,0.5359,0.5666],[29.733,0.537,0.5659],[29.8,0.5498,0.5617],[29.867,0.566,0.5596],[29.933,0.5718,0.5603],[30.0,0.5787,0.5624],[30.067,0.581,0.5631],[30.1,0.581,0.5631]],
  black: [[0.9,0.6053,0.5659],[0.967,0.6065,0.5652],[1.033,0.6088,0.5645],[1.1,0.61,0.5652],[1.167,0.6111,0.5666],[1.233,0.61,0.5673],[1.3,0.6076,0.568],[1.367,0.6053,0.568],[1.433,0.6065,0.5687],[1.5,0.6076,0.568],[1.567,0.6088,0.568],[1.633,0.6088,0.568],[1.7,0.61,0.5673],[1.767,0.6169,0.5652],[1.833,0.6377,0.5631],[1.9,0.6493,0.5652],[1.967,0.6516,0.5659],[2.033,0.6539,0.5666],[2.1,0.6539,0.5666],[2.167,0.6551,0.5666],[2.233,0.6551,0.5659],[2.3,0.6528,0.5652],[2.367,0.6505,0.5645],[2.433,0.6493,0.5638],[2.5,0.6481,0.5638],[2.567,0.6481,0.5645],[2.633,0.647,0.5624],[2.7,0.6481,0.5624],[29.0,0.6042,0.5673],[29.067,0.6065,0.5659],[29.133,0.61,0.5673],[29.2,0.61,0.568],[29.267,0.6088,0.5687],[29.333,0.6076,0.5694],[29.4,0.6042,0.5694],[29.467,0.6042,0.5701],[29.533,0.6065,0.5694],[29.6,0.6076,0.5701],[29.667,0.6076,0.5701],[29.733,0.6088,0.5694],[29.8,0.6215,0.5659],[29.867,0.6366,0.5645],[29.933,0.6435,0.5652],[30.0,0.6505,0.5673],[30.067,0.6528,0.568],[30.1,0.6528,0.568]]
};

NYO.matchesBundledFootage = function (w, h, dur) {
  const s = NYO.BUNDLED_TRACK.signature;
  return w === s.width && h === s.height && Math.abs(dur - s.duration) < 0.15;
};

NYO.GRADE_PRESETS = {
  'warm-ivory': {
    name: 'Warm Ivory & Champagne Luxury',
    values: {
      exposure: 0.20, brightness: 5, contrast: 8, highlights: -18, shadows: 12,
      whites: 5, blacks: -5, saturation: 4, vibrance: 8, temperature: 10, tint: 0,
      castCorrection: 35, skinProtect: 75, productProtect: 80, sharpen: 12,
      denoise: 25, vignette: 5, rolloff: 45, midWarmth: 15
    }
  },
  'neutral': {
    name: 'Neutral (no grade)',
    values: {
      exposure: 0, brightness: 0, contrast: 0, highlights: 0, shadows: 0,
      whites: 0, blacks: 0, saturation: 0, vibrance: 0, temperature: 0, tint: 0,
      castCorrection: 0, skinProtect: 0, productProtect: 0, sharpen: 0,
      denoise: 0, vignette: 0, rolloff: 0, midWarmth: 0
    }
  }
};

NYO.uid = function (prefix) {
  return (prefix || 'id') + '_' + Math.random().toString(36).slice(2, 8);
};

NYO.line = function (text, o) {
  return Object.assign({
    text: text, font: 'serif', weight: 500, size: 64, color: NYO.PALETTE.ivory,
    italic: false, highlight: '', highlightColor: NYO.PALETTE.gold, delay: 0, tracking: 0
  }, o || {});
};

NYO.defaultProject = function () {
  const P = NYO.PALETTE;
  const L = NYO.line;
  const bt = NYO.BUNDLED_TRACK;
  const copyKeys = (arr) => arr.map((k) => k.slice());

  const captions = [
    {
      id: 's1', name: 'Scene 1 · Menuju 30-an', start: 0.15, end: 4.0, x: 0.5, y: 0.175,
      anim: 'fadeUpZoom', inDur: 1.1, outDur: 0.55, backdrop: 'scrim', backdropOpacity: 0.34, maxWidth: 0.84,
      lines: [L('Menuju usia 30-an… 🥹', { size: 70, weight: 500 })]
    },
    {
      id: 's2', name: 'Scene 2 · Dari DALAM', start: 4.0, end: 8.0, x: 0.5, y: 0.175,
      anim: 'slideUp', inDur: 0.8, outDur: 0.5, backdrop: 'scrim', backdropOpacity: 0.34, maxWidth: 0.82,
      lines: [L('Saya mula serius jaga kecantikan dari DALAM ✨', { size: 60, highlight: 'DALAM', highlightColor: P.gold, weight: 500 })]
    },
    {
      id: 's3', name: 'Scene 3 · Aging gracefully', start: 8.0, end: 12.0, x: 0.5, y: 0.175,
      anim: 'reveal', inDur: 1.1, outDur: 0.55, backdrop: 'scrim', backdropOpacity: 0.34, maxWidth: 0.84,
      lines: [
        L('Sebab saya nak', { font: 'sans', weight: 300, size: 36, color: P.ivory, tracking: 2 }),
        L('aging gracefully 🤍', { size: 76, italic: true, weight: 400, delay: 0.25 })
      ]
    },
    {
      id: 's6', name: 'Scene 6 · Ingredients', start: 22.0, end: 26.0, x: 0.5, y: 0.165,
      anim: 'stagger', inDur: 0.7, outDur: 0.55, backdrop: 'glass', backdropOpacity: 0.42, maxWidth: 0.9,
      lines: [
        L('Astaxanthin • PQQ • Ergothioneine', { size: 54, color: P.gold, weight: 500 }),
        L('Antioksidan untuk rutin penjagaan dalaman ✨', { font: 'sans', weight: 300, size: 32, color: P.ivory, delay: 1.45, tracking: 0.5 })
      ]
    },
    {
      id: 's7', name: 'Scene 7 · Closing', start: 26.0, end: 30.1, x: 0.5, y: 0.17,
      anim: 'cinematic', inDur: 1.4, outDur: 1.2, backdrop: 'scrim', backdropOpacity: 0.36, maxWidth: 0.86,
      lines: [
        L('Growing older is natural.', { size: 58, italic: true, weight: 400 }),
        L('Taking care of myself is a choice. 💗', { size: 50, weight: 500, color: P.ivory, highlight: 'choice.', highlightColor: P.rose, delay: 0.9 })
      ]
    }
  ];

  const labelBase = {
    titleSize: 46, subSize: 25, titleColor: P.ivory, subColor: P.gold, accent: P.gold,
    inDur: 0.55, outDur: 0.4, maxGap: 0.6, enabled: true
  };

  const labels = [
    Object.assign({}, labelBase, {
      id: 'l_day', name: 'Scene 4 · DAY CARE (card)', title: 'DAY CARE ☀️', subtitle: 'Morning Routine',
      start: 12.0, end: 17.0, connector: 'none', titleSize: 58, subSize: 28, target: 'red', side: 'left',
      freeX: 0.5, freeY: 0.2, cardDx: -60, cardDy: -120, dotDx: -34, dotDy: 0, keyframes: []
    }),
    Object.assign({}, labelBase, {
      id: 'l_night', name: 'Scene 5 · NIGHT CARE (card)', title: 'NIGHT CARE 🌙', subtitle: 'Evening Routine',
      start: 17.0, end: 22.0, connector: 'none', titleSize: 58, subSize: 28, target: 'black', side: 'right',
      freeX: 0.5, freeY: 0.2, cardDx: 60, cardDy: -120, dotDx: 34, dotDy: 0, keyframes: []
    }),
    Object.assign({}, labelBase, {
      id: 'l_day_track', name: 'DAY CARE → red softgel (tracked)', title: 'DAY CARE ☀️', subtitle: 'Morning Routine',
      start: 1.0, end: 2.7, connector: 'tracked', target: 'red', side: 'left', titleSize: 34, subSize: 20,
      freeX: 0.25, freeY: 0.5, cardDx: -70, cardDy: -150, dotDx: -36, dotDy: 0, keyframes: copyKeys(bt.red)
    }),
    Object.assign({}, labelBase, {
      id: 'l_night_track', name: 'NIGHT CARE → black softgel (tracked)', title: 'NIGHT CARE 🌙', subtitle: 'Evening Routine',
      start: 1.25, end: 2.7, connector: 'tracked', target: 'black', side: 'right', titleSize: 34, subSize: 20,
      freeX: 0.75, freeY: 0.5, cardDx: 18, cardDy: 50, dotDx: 36, dotDy: 0, keyframes: copyKeys(bt.black)
    }),
    Object.assign({}, labelBase, {
      id: 'l_day_end', name: 'DAY CARE → red softgel (ending, off)', title: 'DAY CARE ☀️', subtitle: 'Morning',
      start: 29.15, end: 30.1, connector: 'tracked', target: 'red', side: 'left', titleSize: 34, subSize: 20,
      freeX: 0.25, freeY: 0.5, cardDx: -70, cardDy: -60, dotDx: -36, dotDy: 0, keyframes: copyKeys(bt.red), enabled: false
    }),
    Object.assign({}, labelBase, {
      id: 'l_night_end', name: 'NIGHT CARE → black softgel (ending, off)', title: 'NIGHT CARE 🌙', subtitle: 'Evening',
      start: 29.15, end: 30.1, connector: 'tracked', target: 'black', side: 'right', titleSize: 34, subSize: 20,
      freeX: 0.75, freeY: 0.5, cardDx: 18, cardDy: 50, dotDx: 36, dotDy: 0, keyframes: copyKeys(bt.black), enabled: false
    })
  ];

  // Sound effects. `link` ties a cue to a caption/label so it moves with it;
  // `offset` is then relative to that element's start.
  const sfx = [
    { id: 'x1', type: 'shimmer', link: 's1', offset: 0.0, t: 0, gain: 0.55 },
    { id: 'x2', type: 'whoosh', link: 's1', offset: 0.1, t: 0, gain: 0.45 },
    { id: 'x3', type: 'pop', link: 'l_day_track', offset: 0.05, t: 0, gain: 0.35 },
    { id: 'x4', type: 'chime', link: 'l_night_track', offset: 0.05, t: 0, gain: 0.3 },
    { id: 'x5', type: 'swoosh', link: 's2', offset: 0.0, t: 0, gain: 0.55 },
    { id: 'x6', type: 'sparkle', link: 's3', offset: 0.15, t: 0, gain: 0.5 },
    { id: 'x7', type: 'pop', link: 'l_day', offset: 0.05, t: 0, gain: 0.6 },
    { id: 'x8', type: 'riseShimmer', link: 'l_day', offset: 0.18, t: 0, gain: 0.45 },
    { id: 'x9', type: 'chime', link: 'l_night', offset: 0.05, t: 0, gain: 0.55 },
    { id: 'x10', type: 'tick', link: 's6', offset: 0.05, t: 0, gain: 0.55 },
    { id: 'x11', type: 'tick', link: 's6', offset: 0.5, t: 0, gain: 0.55 },
    { id: 'x12', type: 'tick', link: 's6', offset: 0.95, t: 0, gain: 0.55 },
    { id: 'x13', type: 'shimmer', link: 's7', offset: 0.0, t: 0, gain: 0.5 },
    { id: 'x14', type: 'piano', link: 's7', offset: 1.6, t: 0, gain: 0.6 }
  ];

  return {
    version: 1,
    duration: 30.1,
    layout: { fit: 'fit', background: 'blur', ivory: '#EFE6DA', zoom: 1, offsetY: 0 },
    view: { safeZones: false },
    grade: Object.assign({ enabled: true, preset: 'warm-ivory' }, NYO.GRADE_PRESETS['warm-ivory'].values),
    captions: captions,
    labels: labels,
    sfx: sfx,
    audio: {
      music: 'generated', bpm: 100, musicVolume: 0.7, sfxVolume: 0.85, originalVolume: 0,
      master: 0.9, fadeIn: 0.6, fadeOut: 2.0, musicOffset: 0
    }
  };
};

/* Absolute time of an SFX cue (follows its linked element if any). */
NYO.sfxTime = function (project, cue) {
  if (cue.link) {
    const el = project.captions.find((c) => c.id === cue.link) || project.labels.find((l) => l.id === cue.link);
    if (el) {
      if (el.enabled === false) return null;
      return el.start + (cue.offset || 0);
    }
  }
  return cue.t;
};

/* Scale every time value so the edit follows a video of a different length. */
NYO.retimeProject = function (project, newDuration) {
  const k = newDuration / project.duration;
  if (!isFinite(k) || k <= 0) return;
  const scale = (v) => Math.round(v * k * 1000) / 1000;
  project.captions.forEach((c) => { c.start = scale(c.start); c.end = scale(c.end); });
  project.labels.forEach((l) => {
    l.start = scale(l.start); l.end = scale(l.end);
    l.keyframes.forEach((kf) => { kf[0] = scale(kf[0]); });
  });
  project.sfx.forEach((s) => { if (!s.link) s.t = scale(s.t); });
  project.duration = newDuration;
};

NYO.saveProjectLocal = function (project) {
  try { localStorage.setItem('nyo3-editor-project', JSON.stringify(project)); } catch (e) { /* storage unavailable */ }
};

NYO.loadProjectLocal = function () {
  try {
    const raw = localStorage.getItem('nyo3-editor-project');
    if (!raw) return null;
    const p = JSON.parse(raw);
    return p && p.version === 1 ? p : null;
  } catch (e) { return null; }
};
