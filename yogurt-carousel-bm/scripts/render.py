import sys, math, random, subprocess, os, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool

S = sys.argv[1]
OUT = sys.argv[2]
V = f'{S}/vid'
W, H, FPS = 1080, 1920, 30
FONT = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
GROUND_Y = 1648

# (layer, text, duration, kind, fontsize)   *word* = highlight
SLIDES = [
    (1, "Bayangkan anda jual yogurt… tapi tiada siapa yang beli.", 3.4, 'full', 64),
    (2, "Okey…", 2.0, 'close', 84),
    (3, "Satu cawan tulis *20% lemak.* Satu lagi *80% bebas lemak.* Mana satu laku?", 4.4, 'full', 60),
    (4, "*80% bebas lemak.*", 2.4, 'close', 76),
    (1, "Kenapa?", 2.0, 'full', 104),
    (6, "Sebab bunyinya *lebih sihat.*", 2.6, 'close', 72),
    (7, "Padahal… ia yogurt yang *sama.*", 3.0, 'full', 68),
    (8, "Jadi orang beli *perkataan…* bukan yogurt.", 3.6, 'close', 68),
    (9, "Itulah *framing effect.* Orang beli cara ia *disampaikan.*", 3.6, 'close', 64),
    (10, "Apa lagi?", 2.0, 'close', 84),
    (11, "Beg dan jam tangan RM49. Atau beg RM49, jam tangan *PERCUMA?*", 4.6, 'full', 60),
    (12, "Jam *percuma* la. Mestilah.", 2.6, 'close', 72),
    (13, "Harga sama. Barang sama.", 2.6, 'close', 72),
    (14, "Tapi *'percuma'* rasa lebih untung.", 3.0, 'close', 68),
    (15, "Itulah *bundle pricing.*", 2.6, 'close', 76),
    (16, "Dan yang terakhir?", 2.2, 'close', 76),
    (17, "Butang tulis *'beli sekarang'.* Anda terus beli?", 3.8, 'full', 62),
    (18, "Tak. Nanti-nanti la beli.", 2.6, 'close', 72),
    (19, "Sekarang tulis *'tinggal 3 lagi'.*", 3.4, 'full', 66),
    (20, "…saya beli *sekarang juga.*", 2.6, 'close', 72),
    (21, "Kenapa?", 2.0, 'close', 104),
    (22, "Sebab *takut terlepas.*", 2.6, 'close', 76),
    (23, "*Scarcity.* Takut terlepas (FOMO) buat orang *cepat bertindak.*", 3.8, 'close', 64),
    (24, "Jadi produk tak pernah berubah. Cuma *cara saya sampaikan.*", 3.8, 'close', 64),
    (25, "Follow untuk lagi tips *marketing!*", 3.2, 'full', 68),
]
starts = np.cumsum([0] + [s[2] for s in SLIDES])
T = float(starts[-1])
NF = int(round(T * FPS))
XF = 0.35  # crossfade

def lerp(a, b, t): return a + (b - a) * t
def ease(t): t = min(max(t, 0), 1); return 1 - (1 - t) ** 3

# ---------- static assets ----------
def sky(stops):
    ys = np.linspace(0, 1, H)
    pos = [p for p, _ in stops]; cols = np.array([c for _, c in stops], float)
    g = np.stack([np.interp(ys, pos, cols[:, k]) for k in range(3)], 1)
    return np.repeat(g[:, None, :], W, 1).astype(np.float32)

SKY_A = sky([(0, (38, 28, 92)), (0.35, (118, 52, 128)), (0.6, (226, 96, 96)), (0.78, (250, 150, 86)), (0.84, (255, 200, 120)), (1, (255, 210, 130))])
SKY_B = sky([(0, (12, 12, 44)), (0.35, (62, 30, 96)), (0.6, (170, 62, 92)), (0.78, (226, 104, 72)), (0.84, (246, 150, 84)), (1, (246, 160, 90))])

def glow_sprite(r, core, glow_r):
    size = glow_r * 2
    yy, xx = np.mgrid[0:size, 0:size] - glow_r
    d = np.sqrt(xx ** 2 + yy ** 2)
    a = np.clip(1 - (d - r) / (glow_r - r), 0, 1) ** 2.2 * 0.55
    a[d <= r] = 1.0
    edge = (d > r - 2) & (d <= r)
    a[edge] = 0.9
    img = np.zeros((size, size, 4), np.uint8)
    img[..., :3] = core
    img[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(img, 'RGBA')

DITHER = np.random.default_rng(1).uniform(-1.5, 1.5, (H, W, 1)).astype(np.float32)
SUN = glow_sprite(150, (255, 232, 168), 520)

def mountains():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rnd = random.Random(7)
    for base, amp, col, step in [(1500, 140, (120, 50, 110, 255), 90), (1575, 90, (72, 30, 78, 255), 60)]:
        pts = [(0, H)]; x = -40
        while x < W + 80:
            pts.append((x, base - rnd.random() * amp)); x += step + rnd.randint(-20, 30)
        pts.append((W, H)); d.polygon(pts, fill=col)
    return im.filter(ImageFilter.GaussianBlur(1.2))

MOUNT = mountains()
# haze over mountains near horizon
haze = np.zeros((H, W, 4), np.uint8)
for y in range(1450, 1660):
    haze[y, :, :3] = (255, 150, 110); haze[y, :, 3] = int(70 * math.sin(math.pi * (y - 1450) / 210))
HAZE = Image.fromarray(haze, 'RGBA')

def ground():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(0, H), (0, GROUND_Y - 30)]
    for x in range(0, W + 1, 20):
        yy = GROUND_Y - 28 * math.exp(-((x - 80) / 160) ** 2) - 34 * math.exp(-((x - 1010) / 170) ** 2) - 4 * math.sin(x / 37)
        pts.append((x, yy))
    pts.append((W, H)); d.polygon(pts, fill=(14, 8, 22, 255))
    rnd = random.Random(3)
    for _ in range(260):  # grass blades
        x = rnd.uniform(0, W)
        if 300 < x < 800 and rnd.random() < .75: continue
        yb = GROUND_Y + 2 - 28 * math.exp(-((x - 80) / 160) ** 2) - 34 * math.exp(-((x - 1010) / 170) ** 2)
        h = rnd.uniform(12, 44); lean = rnd.uniform(-10, 10)
        d.polygon([(x - 2.5, yb), (x + 2.5, yb), (x + lean, yb - h)], fill=(14, 8, 22, 255))
    return im

GROUND = ground()

def cloud(w, h, seed):
    rnd = random.Random(seed)
    im = Image.new('RGBA', (w + 120, h + 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for _ in range(9):
        cw = rnd.uniform(.3, .6) * w; ch = rnd.uniform(.4, 1) * h
        cx = rnd.uniform(60 + cw / 2, 60 + w - cw / 2); cy = 60 + h - ch / 2 - rnd.uniform(0, h * .3)
        d.ellipse((cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2), fill=(255, 190, 200, 120))
    return im.filter(ImageFilter.GaussianBlur(14))

CLOUDS = [(cloud(420, 70, 1), 120, 260, 10), (cloud(520, 90, 2), 640, 610, -14), (cloud(360, 60, 3), -80, 1020, 18), (cloud(300, 50, 4), 760, 1240, -10)]

rs = random.Random(11)
STARS = [(rs.uniform(0, W), rs.uniform(0, 650), rs.uniform(1, 2.6), rs.uniform(0, 6.28)) for _ in range(70)]
MOTES = [(rs.uniform(0, W), rs.uniform(900, 1900), rs.uniform(1.5, 3.5), rs.uniform(20, 60), rs.uniform(0, 6.28)) for _ in range(40)]
BIRDS = [(-0.5, 520, 1.0, 0.0), (-1.3, 470, 0.8, 1.3), (-1.0, 580, 0.7, 2.1), (6.0, 700, 0.9, 0.7), (6.6, 650, 0.65, 2.9)]

LAYERS = {i: Image.open(f'{V}/layer_{i}.png').convert('RGBA').copy() for i in range(1, 26) if i != 5}
FLOOR = {k: int(np.where((np.array(v.getchannel('A')) > 200).sum(1) > 5)[0].max()) for k, v in LAYERS.items()}
SC = W / 1100.0
LAYER_ID = {id(v): k for k, v in LAYERS.items()}

# ---------- text sprites ----------
def build_text(text, size):
    f = ImageFont.truetype(FONT, size)
    tokens = []; hl = False
    for raw in text.split(' '):
        w = raw; start_hl = hl
        if w.startswith('*'): start_hl = True; w = w[1:]
        end = w.endswith('*')
        if end: w = w[:-1]
        tokens.append((w, start_hl)); hl = start_hl and not end
    tmp = ImageDraw.Draw(Image.new('L', (1, 1)))
    space = tmp.textlength(' ', font=f)
    lines = []; cur = []; cw = 0
    for w, h in tokens:
        tw = tmp.textlength(w, font=f)
        if cur and cw + space + tw > 920: lines.append((cur, cw)); cur = []; cw = 0
        cw = cw + (space if cur else 0) + tw; cur.append((w, h, tw))
    lines.append((cur, cw))
    lh = int(size * 1.22); words = []
    for li, (ws, lw) in enumerate(lines):
        x = (W - lw) / 2
        for w, h, tw in ws:
            pad = 30
            im = Image.new('RGBA', (int(tw) + pad * 2, lh + pad * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
            ds.text((pad, pad + 4), w, font=f, fill=(20, 5, 30, 200)); sh = sh.filter(ImageFilter.GaussianBlur(7))
            im.alpha_composite(sh)
            d.text((pad, pad), w, font=f, fill=(255, 214, 92) if h else (255, 255, 255), stroke_width=2, stroke_fill=(40, 12, 40))
            words.append((im, x - pad, li * lh - pad))
            x += tw + space
    return words, len(lines) * lh

TEXTS = [build_text(t, sz) for _, t, _, _, sz in SLIDES]

# ---------- frame ----------
def place_fg(layer, kind, local_t, dur, alpha):
    z = 1.0 + 0.035 * (local_t / dur)
    w = int(1100 * SC * z); h = int(1464 * SC * z)
    fg = layer.resize((w, h), Image.BILINEAR)
    if kind == 'full':
        ax, ay = 540, GROUND_Y + 4; src_ay = FLOOR[LAYER_ID[id(layer)]] * SC * z
    else:
        ax, ay = 540, 1830; src_ay = h
    x = int(ax - w / 2); y = int(ay - src_ay)
    if alpha < 1:
        a = fg.getchannel('A').point(lambda v: int(v * alpha)); fg.putalpha(a)
    return fg, (x, y)

def frame(n):
    t = n / FPS; p = t / T
    base = Image.fromarray(np.clip(SKY_A * (1 - p) + SKY_B * p + DITHER, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    d = ImageDraw.Draw(base)
    sa = ease((p - 0.25) / 0.75)
    for sx, sy, r, ph in STARS:
        a = int(255 * sa * (0.55 + 0.45 * math.sin(t * 2 + ph)) * (1 - sy / 700))
        if a > 8: d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(255, 245, 230, a))
    sun_y = lerp(1300, 1590, p)
    base.alpha_composite(SUN, (540 - 520, int(sun_y - 520)))
    for img, x0, y0, v in CLOUDS:
        base.alpha_composite(img, (int(x0 + v * t), y0))
    base.alpha_composite(MOUNT); base.alpha_composite(HAZE)
    # birds
    for t0, by, sc, ph in BIRDS:
        tt = t - t0
        if tt < 0: continue
        bx = -60 + tt * 150 if t0 < 3 else W + 60 - tt * 140
        if bx < -80 or bx > W + 80: continue
        yb = by + 12 * math.sin(tt * 1.5 + ph)
        flap = math.sin(tt * 9 + ph) * 12 * sc
        s = 32 * sc
        d2 = ImageDraw.Draw(base)
        d2.line([(bx - s, yb - flap), (bx - s * .4, yb - flap * .3 - 3), (bx, yb), (bx + s * .4, yb - flap * .3 - 3), (bx + s, yb - flap)], fill=(30, 12, 40, 255), width=max(3, int(4 * sc)), joint='curve')
    # slide index
    i = int(np.searchsorted(starts, t, 'right') - 1); i = min(i, len(SLIDES) - 1)
    lt = t - starts[i]; dur = SLIDES[i][2]
    layers_to_draw = []
    if i > 0 and lt < XF:
        pl, _, pd, pk, _ = SLIDES[i - 1]
        layers_to_draw.append((pl, pk, pd + lt, pd + XF, 1.0))
        layers_to_draw.append((SLIDES[i][0], SLIDES[i][3], lt, dur, ease(lt / XF)))
    else:
        layers_to_draw.append((SLIDES[i][0], SLIDES[i][3], lt, dur, 1.0))
    # ground goes under full scenes, over closeups
    for li, (lay, kind, ltt, dd, al) in enumerate(layers_to_draw):
        if kind == 'full':
            fg, pos = place_fg(LAYERS[lay], kind, ltt, dd, al); base.alpha_composite(fg, pos)
    base.alpha_composite(GROUND)
    for lay, kind, ltt, dd, al in layers_to_draw:
        if kind == 'close':
            fg, pos = place_fg(LAYERS[lay], kind, ltt, dd, al)
            # clip closeup bottom into ground
            base.alpha_composite(fg, pos)
    # re-cover closeup bottom edge with ground strip
    base.alpha_composite(GROUND.crop((0, 1800, W, H)), (0, 1800))
    # floating motes
    d3 = ImageDraw.Draw(base)
    for mx, my, r, sp, ph in MOTES:
        yy = (my - t * sp) % 1100 + 820
        xx = mx + 18 * math.sin(t * .8 + ph)
        a = int(110 + 80 * math.sin(t * 3 + ph))
        d3.ellipse((xx - r, yy - r, xx + r, yy + r), fill=(255, 220, 150, a))
    # text
    words, th = TEXTS[i]
    kind = SLIDES[i][3]
    ty = (330 if kind == 'full' else 470) - th / 2
    if i == len(SLIDES) - 1: ty = 300 - th / 2
    out_a = 1.0
    if dur - lt < 0.25 and i < len(SLIDES) - 1: out_a = (dur - lt) / 0.25
    for k, (im, wx, wy) in enumerate(words):
        a = ease((lt - 0.12 - k * 0.07) / 0.35) * out_a
        if a <= 0: continue
        dy = (1 - a) * 28 if out_a == 1 else 0
        if a < 1:
            im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
        base.alpha_composite(im, (int(wx), int(ty + wy + dy)))
    # vignette-ish fade in/out at start/end
    if t < 0.4 or t > T - 0.5:
        k = min(t / 0.4, (T - t) / 0.5); k = max(0, min(1, k))
        base = Image.blend(Image.new('RGBA', (W, H), (0, 0, 0, 255)), base, k)
    return base.convert('RGB')

def render_chunk(args):
    ci, a, b = args
    path = f'{V}/seg_{ci}.mp4'
    pr = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    for n in range(a, b):
        pr.stdin.write(frame(n).tobytes())
    pr.stdin.close(); pr.wait()
    return path

# ---------- audio ----------
def audio(path):
    sr = 44100; n = int(T * sr); t = np.arange(n) / sr
    out = np.zeros(n)
    def note(f): return 440 * 2 ** ((f - 69) / 12)
    chords = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]  # Am F C G
    cd = 3.2
    for ci in range(int(T / cd) + 1):
        s0 = ci * cd; ch = chords[ci % 4]
        idx = (t >= s0) & (t < s0 + cd + 1.5)
        tt = t[idx] - s0
        env = np.minimum(tt / 0.8, 1) * np.exp(-np.maximum(tt - cd, 0) / 0.5)
        for m in ch:
            f = note(m)
            out[idx] += env * (0.5 * np.sin(2 * np.pi * f * tt) + 0.15 * np.sin(2 * np.pi * f * 2.003 * tt)) * 0.09
        out[idx] += env * np.sin(2 * np.pi * note(ch[0] - 12) * tt) * 0.12
    for s0 in starts[:-1]:  # soft chime at each slide
        idx = (t >= s0) & (t < s0 + 1.5); tt = t[idx] - s0
        out[idx] += np.exp(-tt * 4) * np.sin(2 * np.pi * 1318.5 * tt) * 0.08 + np.exp(-tt * 3) * np.sin(2 * np.pi * 1975.5 * tt) * 0.04
    fade = np.minimum(1, np.minimum(t / 0.5, (T - t) / 1.2))
    out *= fade; out /= max(1e-9, np.abs(out).max()) / 0.7
    st = np.stack([out, np.roll(out, 300)], 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((st * 32767).astype(np.int16).tobytes())

if __name__ == '__main__':
    if len(sys.argv) > 3:  # preview frames
        for sec in sys.argv[3].split(','):
            frame(int(float(sec) * FPS)).save(f'{V}/prev_{sec}.png')
        sys.exit()
    k = 4; step = math.ceil(NF / k)
    chunks = [(c, c * step, min(NF, (c + 1) * step)) for c in range(k)]
    with Pool(k) as pool: segs = pool.map(render_chunk, chunks)
    with open(f'{V}/list.txt', 'w') as fl:
        for s in segs: fl.write(f"file '{s}'\n")
    audio(f'{V}/music.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{V}/list.txt', '-i', f'{V}/music.wav',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', OUT], check=True)
    print('done', T, NF)
