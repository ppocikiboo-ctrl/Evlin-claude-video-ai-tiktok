// Every timing in the edit, in frames at 30 fps. The original clip plays
// once, start to finish, underneath everything; these times only say when
// graphics layers come and go. Music is 120 BPM, so one beat is 15 frames.
export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const DURATION = 345; // 11.5 s, the full original clip
export const BEAT = 15;

// One line of text at a time.
//   open = panel/text appears (KLIK), type = text moves in (TIK-TIK),
//   done = line fully shown (TING), out = line has left.
export type Line = {open: number; type: number; done: number; out: number};
export type PanelCue = Pick<Line, 'open' | 'type' | 'done'>;

export const LINES = {
  hook: {open: 0, type: 0, done: 12, out: 54}, // 0.0–1.8 s, visible on frame 0
  selfCare: {open: 58, type: 64, done: 84, out: 102}, // 1.8–3.4 s
  kenali: {open: 104, type: 108, done: 124, out: 150}, // 3.4–5.0 s
  bahan: {open: 152, type: 158, done: 182, out: 216}, // 5.0–7.2 s
  rutin: {open: 218, type: 224, done: 244, out: 276}, // 7.2–9.2 s
  cta: {open: 278, type: 284, done: 304, out: 345}, // 9.2 s to the end
} satisfies Record<string, Line>;

// Graphics layers (frames). Kept deliberately few so the product stays the hero.
export const LAYERS = {
  stretchWoman: {from: 58, to: 104}, // small, bottom left, beside the self-care panel
  ringPack: {from: 108, to: 150}, // digital light ring around the pack
  routineWoman: {from: 218, to: 280}, // walks in, dumbbell presses, sip of water
  routineIcons: {from: 226, to: 276}, // water bottle, walking shoe, balanced plate
  butterflies: {from: 280, to: 345},
  sakuraBurst: {from: 280, to: 345},
  ringFinal: {from: 300, to: 345}, // light ring around the product
};

// Inside the routine woman's window (frames since LAYERS.routineWoman.from)
export const ROUTINE = {
  walkUntil: 12, // walks in from the left
  dumbbellsAt: 12,
  pressFrom: 16,
  rep: 10, // frames per press rep (fast, cheerful)
  reps: 3,
  drinkFrom: 48, // lifts the water bottle for a sip
  sweatFrom: 22,
};

export type Sfx = 'boom' | 'klik' | 'tiktik' | 'ting' | 'whoosh' | 'sparkle' | 'pop' | 'clink' | 'plink' | 'bloop';

const lineSfx = (l: Line, whoosh = true): [number, Sfx][] => [
  ...(whoosh ? ([[l.open - 3, 'whoosh']] as [number, Sfx][]) : []),
  [l.open, 'klik'],
  [l.type, 'tiktik'],
  [l.type + 9, 'tiktik'],
  [l.done, 'ting'],
];

const r0 = LAYERS.routineWoman.from;

export const SFX_CUES: [number, Sfx][] = [
  // hook: BOOM on the very first frame -> KLIK -> TING
  [0, 'boom'],
  [1, 'klik'],
  [LINES.hook.done, 'ting'],
  [4, 'sparkle'],
  ...lineSfx(LINES.selfCare),
  ...lineSfx(LINES.kenali),
  [LAYERS.ringPack.from + 4, 'sparkle'],
  ...lineSfx(LINES.bahan),
  ...lineSfx(LINES.rutin),
  // routine visuals, kept soft under the line sounds
  ...Array.from({length: ROUTINE.reps}, (_, i) => [r0 + ROUTINE.pressFrom + i * ROUTINE.rep + 5, 'clink'] as [number, Sfx]),
  [r0 + ROUTINE.sweatFrom + 6, 'plink'],
  [LAYERS.routineIcons.from, 'pop'],
  [r0 + ROUTINE.drinkFrom, 'bloop'],
  ...lineSfx(LINES.cta),
  [LAYERS.butterflies.from + 2, 'sparkle'],
  [LAYERS.ringFinal.from + 20, 'sparkle'],
];

export const SFX_VOLUME: Record<Sfx, number> = {
  boom: 0.95,
  klik: 0.85,
  tiktik: 0.5,
  ting: 0.65,
  whoosh: 0.5,
  sparkle: 0.45,
  pop: 0.55,
  clink: 0.4,
  plink: 0.45,
  bloop: 0.45,
};

export const MUSIC_VOLUME = 0.42; // starts on frame 0, sits under the SFX
