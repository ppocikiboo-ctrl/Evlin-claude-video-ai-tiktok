// Every timing in the edit, in frames at 30 fps. Music is 120 BPM, so one
// beat is 15 frames; every shot change is on a beat (see scripts/prep_footage.py).
export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const DURATION = 555; // 18.5 s
export const BEAT = 15;

// Shot boundaries in the edited footage (frames)
export const SHOTS = {
  hook: {from: 0, to: 90}, // desk work, 3x timelapse
  pack: {from: 90, to: 210}, // takes out the VBGV pack
  open: {from: 210, to: 330}, // opens the pack
  tablet: {from: 330, to: 420}, // holds up a tablet
  water: {from: 420, to: 480}, // drinks water
  closeup: {from: 480, to: 555}, // smiling close-up + CTA
};

// One line of text at a time.
//   open = appears (KLIK), type = text moves in (TIK-TIK), done = fully shown (TING)
export type Line = {open: number; type: number; done: number; out: number};
export type PanelCue = Pick<Line, 'open' | 'type' | 'done'>;

export const LINES = {
  hook: {open: 0, type: 0, done: 12, out: 52}, // KERJA DUDUK LAMA SEHARIAN?
  joging: {open: 54, type: 56, done: 72, out: 90}, // TAK SEMPAT JOGING? (+ clock)
  kenali: {open: 96, type: 100, done: 118, out: 206}, // KENALI VBGV + brand pill
  snek: {open: 214, type: 218, done: 236, out: 326}, // SELALU TERGODA NAK SNEK? (+ snacks)
  cta: {open: 484, type: 488, done: 508, out: 555}, // CEK HARGA PROMO / TEKAN BEG KUNING
} satisfies Record<string, Line>;

// Daily-routine checklist card (tablet + water shots). Each item ticks on a beat.
export const CHECKLIST = {
  open: 334,
  out: 478,
  ticks: [348, 364, 380, 432], // jalan kaki, makan seimbang, VBGV ikut label, minum air
};

export const SNACKS_AT = [222, 228, 234, 240]; // snack icons pop in
export const CTA_TAP = 514; // finger taps toward the product bag

export type Sfx =
  | 'boom'
  | 'klik'
  | 'tiktik'
  | 'ting'
  | 'whoosh'
  | 'sparkle'
  | 'pop'
  | 'bloop'
  | 'ticktock'
  | 'check1'
  | 'check2'
  | 'check3'
  | 'check4'
  | 'boing'
  | 'tap'
  | 'kaching';

const lineSfx = (l: Line): [number, Sfx][] => [
  [l.open, 'klik'],
  [l.type, 'tiktik'],
  [l.type + 9, 'tiktik'],
  [l.done, 'ting'],
];

export const SFX_CUES: [number, Sfx][] = [
  // hook: BOOM on frame 0 -> KLIK -> TING
  [0, 'boom'],
  [1, 'klik'],
  [LINES.hook.done, 'ting'],
  // no time to jog: KLIK + fast clock
  [LINES.joging.open, 'klik'],
  [LINES.joging.type, 'ticktock'],
  [LINES.joging.done + 4, 'ting'],
  // a whoosh on every shot change
  ...[SHOTS.pack, SHOTS.open, SHOTS.tablet, SHOTS.water, SHOTS.closeup].map((s) => [s.from - 4, 'whoosh'] as [number, Sfx]),
  [102, 'pop'], // the pack appears
  [104, 'sparkle'],
  ...lineSfx(LINES.kenali),
  // tempted by snacks: snacks boing in
  ...lineSfx(LINES.snek),
  ...SNACKS_AT.map((t) => [t, 'boing'] as [number, Sfx]),
  // checklist: rising dings
  [CHECKLIST.open, 'klik'],
  ...CHECKLIST.ticks.map((t, i) => [t, `check${i + 1}`] as [number, Sfx]),
  [SHOTS.water.from + 6, 'bloop'],
  // CTA: tap -> ka-ching
  ...lineSfx(LINES.cta),
  [CTA_TAP, 'tap'],
  [CTA_TAP + 4, 'kaching'],
];

export const SFX_VOLUME: Record<Sfx, number> = {
  boom: 0.95,
  klik: 0.8,
  tiktik: 0.5,
  ting: 0.6,
  whoosh: 0.5,
  sparkle: 0.45,
  pop: 0.6,
  bloop: 0.45,
  ticktock: 0.5,
  check1: 0.6,
  check2: 0.6,
  check3: 0.6,
  check4: 0.65,
  boing: 0.5,
  tap: 0.6,
  kaching: 0.7,
};

export const MUSIC_VOLUME = 0.45;
