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
  rutin: {open: 54, type: 58, done: 74, out: 90}, // INI RUTIN KECIL SAYA
  kenali: {open: 96, type: 100, done: 118, out: 206}, // KENALI VBGV + brand pill
  ofis: {open: 216, type: 220, done: 240, out: 326}, // SENANG BAWA KE OFIS
  cara: {open: 336, type: 340, done: 360, out: 416}, // 1/2 BIJI SELEPAS SARAPAN
  air: {open: 424, type: 428, done: 444, out: 478}, // JANGAN LUPA MINUM AIR
  cta: {open: 484, type: 488, done: 508, out: 555}, // NAK CUBA JUGA? TEKAN BEG KUNING
} satisfies Record<string, Line>;

export type Sfx = 'boom' | 'klik' | 'tiktik' | 'ting' | 'whoosh' | 'sparkle' | 'pop' | 'bloop';

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
  ...lineSfx(LINES.rutin),
  // a whoosh on every shot change
  ...[SHOTS.pack, SHOTS.open, SHOTS.tablet, SHOTS.water, SHOTS.closeup].map((s) => [s.from - 4, 'whoosh'] as [number, Sfx]),
  [102, 'pop'], // the pack appears
  [104, 'sparkle'],
  ...lineSfx(LINES.kenali),
  ...lineSfx(LINES.ofis),
  ...lineSfx(LINES.cara),
  ...lineSfx(LINES.air),
  [SHOTS.water.from + 6, 'bloop'],
  ...lineSfx(LINES.cta),
  [LINES.cta.done + 2, 'sparkle'],
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
};

export const MUSIC_VOLUME = 0.45;
