// Every timing in the edit, in frames at 30 fps. Music is 120 BPM, so one
// beat is 15 frames.
export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const DURATION = 345; // 11.5 s
export const BEAT = 15;

export const SCENES = {
  s1: {from: 0, to: 60}, // SELF-CARE BUKAN SEKADAR SKINCARE!
  s2: {from: 60, to: 120}, // JANGAN LUPA PENJAGAAN BADAN
  s3: {from: 120, to: 210}, // KENALI SCC + ingredient panels
  s4: {from: 210, to: 270}, // JADIKAN SELF-CARE SATU RUTIN
  s5: {from: 270, to: 345}, // SCC – KENALI PRODUK INI
} as const;

// open = panel appears (KLIK), type = text starts (TIK-TIK), done = text
// complete (TING). The visuals read the same numbers.
export type PanelCue = {open: number; type: number; done: number};

export const PANELS: Record<string, PanelCue> = {
  s1: {open: 2, type: 10, done: 34},
  s2: {open: 68, type: 72, done: 92},
  s3: {open: 122, type: 128, done: 150},
  s3a: {open: 156, type: 160, done: 176}, // WHITE KIDNEY BEAN
  s3b: {open: 166, type: 170, done: 186}, // L-CARNITINE
  s4: {open: 216, type: 220, done: 240},
  s5: {open: 274, type: 280, done: 304},
};

export type Sfx = 'klik' | 'tiktik' | 'ting' | 'whoosh' | 'sparkle';

// Sound per scene follows the brief exactly; every text panel gets a KLIK.
export const SFX_CUES: [number, Sfx][] = [
  // 1: KLIK -> TIK-TIK -> TING
  [0, 'sparkle'],
  [PANELS.s1.open, 'klik'],
  [PANELS.s1.type, 'tiktik'],
  [PANELS.s1.type + 9, 'tiktik'],
  [PANELS.s1.done, 'ting'],
  // 2: WHOOSH -> KLIK -> TING
  [58, 'whoosh'],
  [PANELS.s2.open, 'klik'],
  [PANELS.s2.done, 'ting'],
  // 3: KLIK -> TIK-TIK -> SPARKLE
  [PANELS.s3.open, 'klik'],
  [PANELS.s3.type, 'tiktik'],
  [PANELS.s3.type + 9, 'tiktik'],
  [PANELS.s3a.open, 'klik'],
  [PANELS.s3b.open, 'klik'],
  [PANELS.s3b.type, 'tiktik'],
  [176, 'sparkle'], // butterflies + light ring
  // 4: WHOOSH -> KLIK -> TING
  [208, 'whoosh'],
  [PANELS.s4.open, 'klik'],
  [PANELS.s4.done, 'ting'],
  // 5: KLIK -> TIK-TIK -> TING
  [PANELS.s5.open, 'klik'],
  [PANELS.s5.type, 'tiktik'],
  [PANELS.s5.type + 9, 'tiktik'],
  [PANELS.s5.done, 'ting'],
  [312, 'sparkle'], // light ring around the product
];

export const SFX_VOLUME: Record<Sfx, number> = {
  klik: 0.9,
  tiktik: 0.55,
  ting: 0.7,
  whoosh: 0.6,
  sparkle: 0.5,
};

export const MUSIC_VOLUME = 0.45; // kept under the SFX so every click is heard
