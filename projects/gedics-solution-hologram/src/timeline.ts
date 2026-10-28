// Every timing in the edit, in frames at 30 fps. Music is 120 BPM, so one
// beat is 15 frames and every scene starts on a beat.
export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const DURATION = 300; // 10 s
export const BEAT = 15;

export const SCENES = {
  s1: {from: 0, to: 60}, // BAHAGIA ITU BILA SALING MENGHARGAI
  s2: {from: 60, to: 120}, // KEJUTAN UNTUK ORANG RUMAH
  s3: {from: 120, to: 210}, // WARNA-WARNI KASIH SAYANG
  s4: {from: 210, to: 300}, // KENALI GEDICS SOLUTION / KETAHUI LEBIH LANJUT
} as const;

// Panel activation per line of text: KLIK (panel opens) -> TIK-TIK (text
// types in) -> TING (panel fully on). The visuals read the same numbers.
export type PanelCue = {open: number; type: number; done: number};

export const PANELS: Record<string, PanelCue> = {
  s1: {open: 2, type: 10, done: 34},
  s2: {open: 70, type: 74, done: 96},
  s3: {open: 122, type: 134, done: 158},
  s4a: {open: 214, type: 220, done: 238},
  s4b: {open: 242, type: 247, done: 262},
};

export type Sfx = 'klik' | 'tiktik' | 'ting' | 'whoosh' | 'sparkle';

const panelSfx = (c: PanelCue): [number, Sfx][] => [
  [c.open, 'klik'],
  [c.type, 'tiktik'],
  [c.type + 9, 'tiktik'],
  [c.done, 'ting'],
];

export const SFX_CUES: [number, Sfx][] = [
  [0, 'sparkle'], // stars + hearts appear
  ...panelSfx(PANELS.s1),
  [58, 'whoosh'], // panel 2 slides in from the right
  ...panelSfx(PANELS.s2),
  [80, 'sparkle'], // gift box pops
  ...panelSfx(PANELS.s3),
  [126, 'sparkle'], // rainbow forms
  [150, 'sparkle'], // hearts orbit the panel
  [208, 'whoosh'],
  ...panelSfx(PANELS.s4a),
  ...panelSfx(PANELS.s4b),
  [270, 'sparkle'], // closing shimmer
];

export const SFX_VOLUME: Record<Sfx, number> = {
  klik: 0.9,
  tiktik: 0.55,
  ting: 0.7,
  whoosh: 0.6,
  sparkle: 0.5,
};

export const MUSIC_VOLUME = 0.45; // kept under the SFX so every click is heard
