import {continueRender, delayRender, staticFile} from 'remotion';

export const C = {
  neonPink: '#ff4fb8',
  pink: '#ff8fd0',
  blush: '#ffd1ea',
  roseGold: '#f6c49b',
  gold: '#ffd98a',
  white: '#ffffff',
  lavender: '#cdb6ff',
  red: '#ff3b6b',
};

export const FONT = 'Inter Display';

const faces: [string, string][] = [
  ['900', 'fonts/InterDisplay-Black.otf'],
  ['700', 'fonts/InterDisplay-Bold.otf'],
  ['600', 'fonts/InterDisplay-SemiBold.otf'],
];

let loaded = false;
export const loadFonts = () => {
  if (loaded || typeof document === 'undefined') return;
  loaded = true;
  const handle = delayRender('Loading Inter Display');
  Promise.all(
    faces.map(([weight, file]) => {
      const f = new FontFace(FONT, `url(${staticFile(file)})`, {weight});
      document.fonts.add(f);
      return f.load();
    }),
  ).then(() => continueRender(handle));
};
