// Every timing in the edit, in frames at 30 fps. The original clip plays
// once, start to finish, underneath everything; only the graphics layers
// come and go. Music is 120 BPM, so one beat is 15 frames.
export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const DURATION = 345; // 11.5 s, the full original clip
export const BEAT = 15;

// The leftover-food plate is a general "mindful eating" visual. Set this to
// false to drop it (and its sounds) if TikTok review objects to it.
export const SHOW_PLATE = true;

// One line of text at a time. open = text/shape appears (KLIK),
// type = text moves in (TIK-TIK or the style's own sound), done = animation
// complete (TING), out = line has fully left.
export type Line = {open: number; type: number; done: number; out: number};
export type PanelCue = Pick<Line, 'open' | 'type' | 'done'>;

export const LINES = {
  selfCare: {open: 2, type: 8, done: 32, out: 56}, // sticker + bouncing letters, top
  badan: {open: 64, type: 70, done: 92, out: 118}, // ribbon banner, bottom
  kenali: {open: 124, type: 126, done: 144, out: 170}, // 3D extruded zoom, top
  bahan: {open: 174, type: 178, done: 202, out: 228}, // split-flap board, top
  rutin: {open: 236, type: 242, done: 264, out: 284}, // neon sign on a solid plate, top
  produk: {open: 296, type: 302, done: 322, out: 345}, // 3D button + stamp + confetti, top
} satisfies Record<string, Line>;

// Rotating graphics layers (frames)
export const LAYERS = {
  hologramWoman: {from: 6, to: 58}, // hologram silhouette builds up beside the product
  sakuraBurst1: {from: 62, to: 130},
  plate: {from: 146, to: 184}, // big portion, three bites, food left over
  woman: {from: 190, to: 300}, // 3D woman: stretches, then light dumbbell presses
  careIcons: {from: 205, to: 290}, // 3 L water bottle, walking shoe, self-care lotus
  sakuraBurst2: {from: 296, to: 345},
  ringFinal: {from: 306, to: 345}, // light ring around the product
};

// Inside the woman's window (frames since LAYERS.woman.from)
export const WOMAN = {
  dumbbellsAt: 44, // dumbbells pop into her hands
  pressFrom: 50, // first press rep starts
  rep: 14, // frames per press rep
  reps: 4,
  sweatFrom: 60,
  energyFrom: 54,
};

export const PLATE_BITES = [155, 164, 173]; // fork grabs a piece

export type Sfx =
  | 'klik'
  | 'tiktik'
  | 'ting'
  | 'whoosh'
  | 'sparkle'
  | 'pop'
  | 'boing'
  | 'swish'
  | 'flap'
  | 'thump'
  | 'chime'
  | 'clink'
  | 'plink'
  | 'bite'
  | 'bloop'
  | 'confetti';

const w0 = LAYERS.woman.from;
const reps = Array.from({length: WOMAN.reps}, (_, i) => w0 + WOMAN.pressFrom + i * WOMAN.rep + Math.round(WOMAN.rep / 2));

export const SFX_CUES: [number, Sfx][] = [
  // line 1: sticker pops, letters bounce in
  [0, 'sparkle'],
  [LINES.selfCare.open, 'klik'],
  [LINES.selfCare.open + 1, 'pop'],
  [LINES.selfCare.type, 'boing'],
  [LINES.selfCare.type + 10, 'boing'],
  [LINES.selfCare.done, 'ting'],
  // line 2: ribbon unfurls
  [LINES.badan.open - 4, 'swish'],
  [LINES.badan.open, 'klik'],
  [LINES.badan.type, 'tiktik'],
  [LINES.badan.type + 9, 'tiktik'],
  [LINES.badan.done, 'ting'],
  [LAYERS.sakuraBurst1.from, 'sparkle'],
  // line 3: 3D letters zoom in and land
  [LINES.kenali.open - 4, 'whoosh'],
  [LINES.kenali.open, 'klik'],
  [LINES.kenali.type, 'tiktik'],
  [LINES.kenali.type + 9, 'tiktik'],
  [LINES.kenali.done, 'thump'],
  [LINES.kenali.done + 2, 'ting'],
  // plate
  ...(SHOW_PLATE ? ([[LAYERS.plate.from, 'pop'], ...PLATE_BITES.map((b) => [b, 'bite'])] as [number, Sfx][]) : []),
  // line 4: split-flap board clatters
  [LINES.bahan.open - 4, 'whoosh'],
  [LINES.bahan.open, 'klik'],
  [LINES.bahan.type, 'flap'],
  [LINES.bahan.type + 12, 'tiktik'],
  [LINES.bahan.done, 'ting'],
  // woman
  [w0, 'pop'],
  [w0 + WOMAN.dumbbellsAt, 'clink'],
  ...reps.map((r) => [r, 'clink'] as [number, Sfx]),
  [w0 + WOMAN.energyFrom, 'swish'],
  [w0 + WOMAN.sweatFrom + 4, 'plink'],
  [w0 + WOMAN.sweatFrom + 24, 'plink'],
  // care icons
  [LAYERS.careIcons.from, 'bloop'],
  [LAYERS.careIcons.from + 6, 'pop'],
  [LAYERS.careIcons.from + 12, 'pop'],
  // line 5: neon flickers on
  [LINES.rutin.open - 4, 'whoosh'],
  [LINES.rutin.open, 'klik'],
  [LINES.rutin.type, 'tiktik'],
  [LINES.rutin.type + 9, 'tiktik'],
  [LINES.rutin.done, 'ting'],
  // line 6: button stamps down, confetti
  [LINES.produk.open - 4, 'whoosh'],
  [LINES.produk.open, 'klik'],
  [LINES.produk.type, 'tiktik'],
  [LINES.produk.type + 9, 'tiktik'],
  [LINES.produk.done, 'thump'],
  [LINES.produk.done, 'confetti'],
  [LINES.produk.done + 3, 'chime'],
  [LAYERS.sakuraBurst2.from + 4, 'sparkle'],
  [LAYERS.ringFinal.from + 24, 'sparkle'],
];

export const SFX_VOLUME: Record<Sfx, number> = {
  klik: 0.85,
  tiktik: 0.5,
  ting: 0.65,
  whoosh: 0.5,
  sparkle: 0.45,
  pop: 0.7,
  boing: 0.55,
  swish: 0.55,
  flap: 0.6,
  thump: 0.75,
  chime: 0.6,
  clink: 0.5,
  plink: 0.55,
  bite: 0.6,
  bloop: 0.55,
  confetti: 0.6,
};

export const MUSIC_VOLUME = 0.4; // under the SFX so every click is heard
