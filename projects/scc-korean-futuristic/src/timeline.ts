// Every timing in the edit, in frames at 30 fps. The original clip plays
// once, start to finish, underneath everything; only the graphics layers
// come and go. Music is 120 BPM, so one beat is 15 frames.
export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const DURATION = 345; // 11.5 s, the full original clip
export const BEAT = 15;

// One line of text at a time. open = panel/text appears (KLIK),
// type = text moves in (TIK-TIK), done = animation complete (TING),
// out = line has fully left.
export type Line = {open: number; type: number; done: number; out: number};
export type PanelCue = Pick<Line, 'open' | 'type' | 'done'>;

export const LINES = {
  selfCare: {open: 2, type: 8, done: 32, out: 56}, // hologram panel, top
  badan: {open: 64, type: 70, done: 92, out: 118}, // glass bubble, bottom
  kenali: {open: 124, type: 126, done: 144, out: 170}, // zoom, top
  bahan: {open: 174, type: 178, done: 202, out: 228}, // moving digital text, top
  rutin: {open: 236, type: 242, done: 264, out: 284}, // neon, top
  produk: {open: 296, type: 302, done: 322, out: 345}, // slide-in glass panel, top
} satisfies Record<string, Line>;

// Rotating graphics layers (frames)
export const LAYERS = {
  hologramWoman: {from: 6, to: 58}, // builds up beside the product
  sakuraBurst1: {from: 62, to: 130},
  careIcons: {from: 150, to: 186}, // water bottle, walking shoe, self-care
  ringPack: {from: 150, to: 184}, // digital light ring around the small pack
  butterflies: {from: 186, to: 290},
  koreanWoman: {from: 200, to: 300}, // 3D woman doing light stretches
  sakuraBurst2: {from: 296, to: 345},
  ringFinal: {from: 306, to: 345}, // light ring around the product
};

export type Sfx = 'klik' | 'tiktik' | 'ting' | 'whoosh' | 'sparkle';

const lineSfx = (l: Line, whoosh: boolean): [number, Sfx][] => [
  ...(whoosh ? ([[l.open - 4, 'whoosh']] as [number, Sfx][]) : []),
  [l.open, 'klik'],
  [l.type, 'tiktik'],
  [l.type + 9, 'tiktik'],
  [l.done, 'ting'],
];

export const SFX_CUES: [number, Sfx][] = [
  [0, 'sparkle'], // stars
  ...lineSfx(LINES.selfCare, false),
  ...lineSfx(LINES.badan, true),
  [LAYERS.sakuraBurst1.from, 'sparkle'],
  ...lineSfx(LINES.kenali, true),
  [LAYERS.careIcons.from, 'sparkle'],
  ...lineSfx(LINES.bahan, true),
  [LAYERS.butterflies.from, 'sparkle'],
  ...lineSfx(LINES.rutin, true),
  ...lineSfx(LINES.produk, true),
  [LAYERS.sakuraBurst2.from + 4, 'sparkle'],
  [LAYERS.ringFinal.from + 24, 'sparkle'],
];

export const SFX_VOLUME: Record<Sfx, number> = {
  klik: 0.9,
  tiktik: 0.55,
  ting: 0.7,
  whoosh: 0.55,
  sparkle: 0.5,
};

export const MUSIC_VOLUME = 0.45; // under the SFX so every click is heard
