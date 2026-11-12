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
    template: 'luxe',
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
  if (project.fx) {
    if (project.fx.chapters) project.fx.chapters = project.fx.chapters.map(scale);
    (project.fx.punches || []).forEach((p) => { p.t = scale(p.t); });
    (project.fx.flashes || []).forEach((f) => { f.t = scale(f.t); });
  }
  if (project.audio && project.audio.breaks) project.audio.breaks = project.audio.breaks.map((b) => b.map(scale));
  project.duration = newDuration;
};

/* Each template keeps its own saved edit, so switching never loses work. */
NYO.saveProjectLocal = function (project) {
  try {
    const tpl = project.template || 'luxe';
    localStorage.setItem('nyo3-editor-project:' + tpl, JSON.stringify(project));
    localStorage.setItem('nyo3-editor-template', tpl);
  } catch (e) { /* storage unavailable */ }
};

NYO.loadProjectLocal = function (template) {
  try {
    const tpl = template || localStorage.getItem('nyo3-editor-template') || 'luxe';
    const raw = localStorage.getItem('nyo3-editor-project:' + tpl) || (tpl === 'luxe' ? localStorage.getItem('nyo3-editor-project') : null);
    if (!raw) return null;
    const p = JSON.parse(raw);
    return p && p.version === 1 ? p : null;
  } catch (e) { return null; }
};

/* ===================== Template 2: Bold FAB + CTA =====================
 * Same original footage, a different edit: bold editorial look (ruby red,
 * black, white), kinetic type, checklist cards and a clear sales structure:
 * Hook → Advantages → Emotion → Why → Features → Benefits → CTA.
 * Every product fact comes from the printed pack (see editor/README.md). */
NYO.GRADE_PRESETS['crisp-editorial'] = {
  name: 'Crisp Clean Editorial',
  values: {
    exposure: 0.15, brightness: 4, contrast: 14, highlights: -14, shadows: 8,
    whites: 8, blacks: -8, saturation: 6, vibrance: 10, temperature: 3, tint: 0,
    castCorrection: 40, skinProtect: 75, productProtect: 85, sharpen: 18,
    denoise: 25, vignette: 8, rolloff: 35, midWarmth: 5
  }
};

NYO.fabProject = function () {
  const RED = '#B3122E', BLACK = '#141414', WHITE = '#FFFFFF', YELLOW = '#FFC400';
  const L = NYO.line;
  const bt = NYO.BUNDLED_TRACK;
  const copyKeys = (arr) => arr.map((k) => k.slice());
  const sans = (text, o) => L(text, Object.assign({ font: 'sans', weight: 600, color: WHITE }, o || {}));
  const chip = (text, o) => sans(text, Object.assign({ weight: 700, size: 26, tracking: 3, chip: true, chipColor: RED, shadow: false }, o || {}));
  const item = (text, color, o) => sans(text, Object.assign({ size: 41, color: color, check: true, checkColor: RED, shadow: false }, o || {}));

  const card = (o) => Object.assign({
    x: 0.5, y: 0.17, align: 'left', anim: 'checklist', stagger: 0.45, inDur: 0.4, outDur: 0.3,
    backdrop: 'box', backdropColor: WHITE, backdropOpacity: 0.95, accentColor: RED, maxWidth: 0.84
  }, o);

  const captions = [
    {
      id: 'h1', name: 'HOOK · 2 biji sehari', start: 0.0, end: 2.75, x: 0.5, y: 0.155,
      anim: 'punch', inDur: 0.35, outDur: 0.25, backdrop: 'scrim', backdropOpacity: 0.42, maxWidth: 0.92,
      lines: [sans('2 BIJI SEHARI.', { weight: 800, size: 96, lineHeight: 1.15, highlight: 'SEHARI.', hlStyle: 'box', highlightColor: RED })]
    },
    {
      id: 'h2', name: 'HOOK · sebab tak skip', start: 0.35, end: 2.75, x: 0.5, y: 0.228,
      anim: 'wordPop', wordGap: 0.11, inDur: 0.3, outDur: 0.25, backdrop: 'none', maxWidth: 0.9,
      lines: [sans('Ini sebab saya tak pernah skip 👇', { size: 46 })]
    },
    card({
      id: 'adv', name: 'KELEBIHAN · 2 softgel', start: 2.85, end: 7.95, stagger: 0.55,
      lines: [
        chip('KELEBIHAN'),
        item('Formula PAGI & MALAM berasingan', BLACK, { highlight: 'PAGI', hlStyle: 'box', highlightColor: RED }),
        item('Hanya 2 softgel sehari', BLACK),
        item('Mudah: ambil bersama makanan', BLACK)
      ]
    }),
    {
      id: 'emo1', name: 'EMOSI · bukan nak muda', start: 8.0, end: 10.6, x: 0.5, y: 0.17,
      anim: 'wordPop', wordGap: 0.13, inDur: 0.35, outDur: 0.35, backdrop: 'scrim', backdropOpacity: 0.4, maxWidth: 0.86,
      lines: [L('Bukan nak nampak muda selamanya…', { italic: true, weight: 500, size: 64, color: WHITE })]
    },
    {
      id: 'emo2', name: 'EMOSI · yakin tanpa filter', start: 10.6, end: 12.7, x: 0.5, y: 0.17,
      anim: 'wordPop', wordGap: 0.1, inDur: 0.3, outDur: 0.3, backdrop: 'scrim', backdropOpacity: 0.4, maxWidth: 0.9,
      lines: [
        sans('…cuma nak YAKIN tengok cermin', { weight: 700, size: 54, highlight: 'YAKIN', hlStyle: 'box', highlightColor: RED }),
        L('tanpa filter 🤍', { italic: true, weight: 500, size: 62, color: WHITE })
      ]
    },
    {
      id: 'why', name: 'WHY · dari dalam?', start: 12.7, end: 14.1, x: 0.5, y: 0.17,
      anim: 'punch', inDur: 0.3, outDur: 0.2, backdrop: 'scrim', backdropOpacity: 0.42, maxWidth: 0.9,
      lines: [
        sans('Skincare luar dah ada…', { size: 44 }),
        sans('Yang dari DALAM? 🤔', { weight: 800, size: 78, lineHeight: 1.2, highlight: 'DALAM?', hlStyle: 'box', highlightColor: RED })
      ]
    },
    card({
      id: 'prod', name: 'CIRI · Ageless by NYO3', start: 14.1, end: 17.0, y: 0.14, stagger: 0.22, align: 'center',
      backdropColor: BLACK, backdropOpacity: 0.9,
      lines: [
        chip('CIRI PRODUK'),
        L('Ageless by NYO3', { weight: 600, size: 62, color: WHITE, shadow: false }),
        sans('Ergothioneine & PQQ · Day & Night Softgels', { weight: 400, size: 26, color: '#E6E6E6', shadow: false })
      ]
    }),
    card({
      id: 'am', name: 'CIRI · softgel merah (pagi)', start: 17.0, end: 20.8, y: 0.165,
      lines: [
        chip('☀️ SOFTGEL MERAH · PAGI'),
        item('Astaxanthin 5mg', BLACK),
        item('PQQ 15mg  ·  SOD 20mg', BLACK),
        item('Vitamin C 20mg', BLACK)
      ]
    }),
    card({
      id: 'pm', name: 'CIRI · softgel hitam (malam)', start: 20.8, end: 24.4, y: 0.165,
      backdropColor: BLACK, backdropOpacity: 0.92, accentColor: WHITE,
      lines: [
        chip('🌙 SOFTGEL HITAM · MALAM', { chipColor: WHITE, color: BLACK }),
        item('L-Ergothioneine 30mg', WHITE),
        item('Krill Oil 50mg  ·  Sage Extract 50mg', WHITE),
        item('Zinc  ·  Vitamin B2 & B3', WHITE)
      ]
    }),
    card({
      id: 'ben', name: 'MANFAAT', start: 24.4, end: 27.0, stagger: 0.5, maxWidth: 0.82,
      lines: [
        chip('MANFAAT'),
        item('Bantu sokong kulit nampak sihat & berseri', BLACK, { size: 37 }),
        item('Antioksidan bantu lindungi sel daripada tekanan oksidatif', BLACK, { size: 37 })
      ]
    }),
    {
      id: 'cta', name: 'CTA · beg kuning', start: 27.0, end: 30.1, x: 0.5, y: 0.175,
      anim: 'wordPop', wordGap: 0.06, inDur: 0.28, outDur: 0.4, backdrop: 'scrim', backdropOpacity: 0.5, maxWidth: 0.92,
      lines: [
        sans('TEKAN BEG KUNING 👇', { weight: 800, size: 70, lineHeight: 1.25, highlight: 'KUNING', hlStyle: 'box', highlightColor: YELLOW, hlTextColor: BLACK, bounce: true }),
        sans('Mulakan rutin 30 hari anda minggu ini', { size: 38 }),
        sans('untuk sokongan antioksidan pagi & malam ✨', { weight: 400, size: 32 })
      ]
    }
  ];

  const lab = {
    cardStyle: 'solid', titleFont: 'sans', titleWeight: 700, subWeight: 500, titleSize: 40, subSize: 23,
    titleColor: WHITE, accent: WHITE, inDur: 0.45, outDur: 0.3, maxGap: 0.6, enabled: true, connector: 'tracked'
  };
  const labels = [
    Object.assign({}, lab, {
      id: 'f_day', name: 'PAGI → red softgel (tracked)', title: 'PAGI ☀️', subtitle: 'Softgel merah',
      start: 1.0, end: 2.7, target: 'red', side: 'left', cardColor: RED, subColor: '#FFDCE3',
      freeX: 0.25, freeY: 0.5, cardDx: -70, cardDy: -150, dotDx: -36, dotDy: 0, keyframes: copyKeys(bt.red)
    }),
    Object.assign({}, lab, {
      id: 'f_night', name: 'MALAM → black softgel (tracked)', title: 'MALAM 🌙', subtitle: 'Softgel hitam',
      start: 1.2, end: 2.7, target: 'black', side: 'right', cardColor: BLACK, subColor: '#D6D6D6',
      freeX: 0.75, freeY: 0.5, cardDx: 18, cardDy: 50, dotDx: 36, dotDy: 0, keyframes: copyKeys(bt.black)
    })
  ];

  const cue = (id, type, link, offset, gain) => ({ id, type, link, offset, t: 0, gain });
  const sfx = [
    cue('y1', 'impact', 'h1', 0.0, 0.7),
    cue('y2', 'snap', 'h2', 0.0, 0.5),
    cue('y3', 'pop', 'f_day', 0.05, 0.45),
    cue('y4', 'snap', 'f_night', 0.05, 0.45),
    cue('y5', 'swoosh', 'adv', 0.0, 0.55),
    cue('y6', 'snap', 'adv', 0.55, 0.5), cue('y7', 'snap', 'adv', 1.1, 0.5), cue('y8', 'snap', 'adv', 1.65, 0.5),
    cue('y9', 'whoosh', 'emo1', 0.0, 0.4),
    cue('y10', 'sparkle', 'emo2', 0.35, 0.45),
    cue('y11', 'impact', 'why', 0.0, 0.45),
    cue('y12', 'impact', 'prod', 0.0, 0.65), cue('y13', 'shimmer', 'prod', 0.1, 0.4),
    cue('y14', 'swoosh', 'am', 0.0, 0.5), cue('y15', 'snap', 'am', 0.45, 0.5), cue('y16', 'snap', 'am', 0.9, 0.5), cue('y17', 'snap', 'am', 1.35, 0.5),
    cue('y18', 'swoosh', 'pm', 0.0, 0.5), cue('y19', 'snap', 'pm', 0.45, 0.5), cue('y20', 'snap', 'pm', 0.9, 0.5), cue('y21', 'snap', 'pm', 1.35, 0.5),
    cue('y22', 'swoosh', 'ben', 0.0, 0.5), cue('y23', 'snap', 'ben', 0.5, 0.5), cue('y24', 'snap', 'ben', 1.0, 0.5),
    { id: 'y25', type: 'riser', link: null, offset: 0, t: 25.8, gain: 0.6 },
    cue('y26', 'impact', 'cta', 0.0, 0.75)
  ];

  return {
    version: 1,
    template: 'fab',
    duration: 30.1,
    layout: { fit: 'fit', background: 'blur', ivory: '#1B1B1B', zoom: 1, offsetY: 0 },
    view: { safeZones: false },
    grade: Object.assign({ enabled: true, preset: 'crisp-editorial' }, NYO.GRADE_PRESETS['crisp-editorial'].values),
    fx: {
      chapters: [0, 2.8, 8.0, 14.1, 24.4, 27.0],
      chapterColor: WHITE,
      punches: [
        { t: 0, amount: 0.1, dur: 0.5 }, { t: 2.85, amount: 0.04 }, { t: 8.0, amount: 0.04 }, { t: 12.7, amount: 0.05 },
        { t: 14.1, amount: 0.07 }, { t: 17.0, amount: 0.04 }, { t: 20.8, amount: 0.04 }, { t: 24.4, amount: 0.04 }, { t: 27.0, amount: 0.08 }
      ],
      flashes: [{ t: 0, alpha: 0.6 }, { t: 14.1, alpha: 0.45 }, { t: 27.0, alpha: 0.5 }]
    },
    captions: captions,
    labels: labels,
    sfx: sfx,
    audio: {
      music: 'generated', style: 'pulse', bpm: 118, musicVolume: 0.6, sfxVolume: 0.9, originalVolume: 0,
      master: 0.9, fadeIn: 0, fadeOut: 1.2, musicOffset: 0, breaks: [[25.9, 27.0]]
    }
  };
};

NYO.TEMPLATES = {
  luxe: { name: 'Luxe Ivory: My Self-Care Era (video 1)', build: NYO.defaultProject },
  fab: { name: 'Bold FAB + CTA: 2 biji sehari (video 2)', build: NYO.fabProject }
};
