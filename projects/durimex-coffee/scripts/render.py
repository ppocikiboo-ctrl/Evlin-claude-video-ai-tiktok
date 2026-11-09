"""Composite animated overlays onto the cut video and mux final audio."""
import sys, json, math, subprocess, wave
import numpy as np
from PIL import Image
sys.path.insert(0, sys.path[0])
from gfx import *

cut, front, out = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, FPS = 1080, 1920, 30
segs = json.load(open(cut + ".json"))
VID_END = segs[-1]["out"][1]
HOLD = 1.3
TOTAL = VID_END + HOLD
NF = int(TOTAL * FPS)

fr = Image.open(front)
CARD = {
    "durian": ingredient_card(circle_crop(fr, 410, 1215, 135, 300), "DURIAN BELANDA", photo=True),
    "khitam": ingredient_card(black_turmeric(400), "KUNYIT HITAM"),
    "kunyit": ingredient_card(turmeric(400), "KUNYIT"),
    "sacha": ingredient_card(sacha_inchi(400), "SACHA INCHI"),
    "robusta": ingredient_card(coffee_beans(400), "KOPI ROBUSTA"),
}
Y_ = YELLOW
def T(lines, size=92, **kw):
    return stroke_text(lines, size, max_w=960, **kw)

# ---- element list: (image, t_in, t_out, center_x, center_y, anim)
E = []
def add(img, t0, t1, cx, cy, anim="pop", sfx=True):
    E.append(dict(img=img, t0=t0, t1=t1, cx=cx, cy=cy, anim=anim, sfx=sfx))

s = [x["out"] for x in segs]
# 0. HOOK (visible from frame 0 for the thumbnail)
add(pill("RAMAI TAK TAHU!", 60, rot=-3), 0, s[0][1], 540, 230, "static", False)
add(T([[("KOPI ", WHITE), ("DURIAN BELANDA", Y_)], [("+ ", WHITE), ("KUNYIT HITAM", Y_), ("?!", WHITE)]], 100),
    0, s[0][1], 540, 420, "static", False)
add(CARD["durian"], 0.15, s[0][1], 300, 1390)
add(T(["+"], 120), 0.35, s[0][1], 540, 1370)
add(CARD["khitam"], 0.5, s[0][1], 780, 1390)
# 1. not ordinary coffee
t = s[1][0]
add(T([[("BUKAN KOPI ", WHITE), ("BIASA!", Y_)]], 104), t, t + 4.0, 540, 300)
add(pill("Campuran herba dalam 1 sachet", 46, bg=GREEN_D, fg=WHITE), t + 0.3, t + 4.0, 540, 440)
add(CARD["durian"], t + 0.5, t + 4.0, 290, 1400)
# 2. black turmeric + sacha inchi
t = s[1][0] + 4.0
add(T([[("Ada ", WHITE), ("KUNYIT HITAM", Y_)], [("& ", WHITE), ("SACHA INCHI", Y_)]], 96), t, s[1][1], 540, 330)
add(CARD["khitam"], t + 0.15, s[1][1], 290, 1400)
add(CARD["sacha"], t + 1.6, s[1][1], 790, 1400)
# 3. robusta + nano sugar
t = s[2][0]
add(T([[("Kopi ", WHITE), ("ROBUSTA", Y_)], [("+ ", WHITE), ("NANO SUGAR", Y_)]], 100), t, t + 2.7, 540, 330)
add(CARD["robusta"], t + 0.2, t + 2.7, 290, 1400)
add(CARD["kunyit"], t + 1.0, t + 2.7, 790, 1400)
# 4. easy to make
t = s[2][0] + 2.7
add(T([[("SENANG ", WHITE), ("BANCUH!", Y_)]], 104), t, s[2][1], 540, 300)
add(pill("1 sachet + air panas = siap", 48, bg=GREEN_D, fg=WHITE), t + 0.3, s[2][1], 540, 440)
add(CARD["robusta"], t + 0.4, s[2][1], 290, 1400)
# 5. ingredient checklist
t = s[3][0]
add(T([[("SEMUA DALAM ", WHITE), ("1 CAWAN", Y_)]], 96), t, s[3][1], 540, 300)
rows = ["Ekstrak durian belanda", "Ekstrak kunyit hitam", "Ekstrak kunyit", "Minyak sacha inchi", "Kopi robusta asli"]
from PIL import ImageDraw as _D
def backdrop(w, h):
    b = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    _D.Draw(b).rounded_rectangle([0, 0, w - 1, h - 1], radius=44, fill=(10, 40, 20, 170))
    return b
add(backdrop(860, 5 * 100 + 50), t + 0.2, s[3][1], 540, 1060 + 2 * 100, "pop", False)
for i, r in enumerate(rows):
    im = check_row(r, 60)
    add(im, t + 0.35 + i * 0.55, s[3][1], 160 + im.width / 2, 1060 + i * 100, "slide")
# 6. certifications
t = s[4][0]
add(T([[("LULUS ", WHITE), ("HALAL", Y_), (" & ", WHITE), ("MeSTI", Y_)]], 92), t, s[4][1], 540, 300)
add(backdrop(760, 3 * 115 + 50), t + 0.15, s[4][1], 540, 1180 + 115, "pop", False)
for i, r in enumerate(["Halal JAKIM", "Lulus MeSTI", "10 sachet x 25g"]):
    im = check_row(r, 66)
    add(im, t + 0.3 + i * 0.6, s[4][1], 210 + im.width / 2, 1180 + i * 115, "slide")
# 7. CTA
t = s[5][0]
cta_txt = T([[("TEKAN ", BLACK), ("BAKUL KUNING", BLACK)]], 84, stroke=YELLOW, sw=1)
cart = cart_icon(110)
row = Image.new("RGBA", (cart.width + 20 + cta_txt.width, max(cart.height, cta_txt.height)), (0, 0, 0, 0))
row.alpha_composite(cart, (0, (row.height - cart.height) // 2))
row.alpha_composite(cta_txt, (cart.width + 20, (row.height - cta_txt.height) // 2))
add(panel(row, 34, bg=YELLOW + (255,), radius=60), t, TOTAL + 1, 540, 330, "pulse")
add(T([[("Grab sekarang ", WHITE), ("sebelum habis stok!", Y_)]], 62), t + 0.4, TOTAL + 1, 540, 500)
add(arrow_down(190), t + 0.6, TOTAL + 1, 190, 1400, "bounce")


# ---- animation
def ease_back(x):
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def state(e, t):
    if t < e["t0"] or t >= e["t1"]:
        return None
    age, left = t - e["t0"], e["t1"] - t
    sc, a, dx, dy = 1.0, 1.0, 0, 0
    if e["anim"] in ("pop", "pulse"):
        if age < 0.3:
            sc = 0.4 + 0.6 * ease_back(age / 0.3); a = min(1, age / 0.12)
        if e["anim"] == "pulse" and age >= 0.3:
            sc = 1 + 0.04 * math.sin((age - 0.3) * 2 * math.pi * 1.6)
    elif e["anim"] == "slide":
        if age < 0.25:
            k = ease_back(age / 0.25); dx = -(1 - k) * 500; a = min(1, age / 0.15)
    elif e["anim"] == "bounce":
        a = min(1, age / 0.15); dy = -abs(math.sin(age * math.pi * 2.2)) * 50
    if e["anim"] != "static" and left < 0.15:
        a *= left / 0.15; sc *= 0.85 + 0.15 * left / 0.15
    return sc, max(0, min(1, a)), dx, dy

def seg_at(t):
    for i, x in enumerate(segs):
        if t < x["out"][1]:
            return i, t - x["out"][0], x["out"][1] - x["out"][0]
    return len(segs) - 1, t - segs[-1]["out"][0], segs[-1]["out"][1] - segs[-1]["out"][0]

# ---- pipes
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", cut, "-vf",
                        f"eq=contrast=1.06:saturation=1.18:brightness=0.01,unsharp=5:5:0.4,tpad=stop_mode=clone:stop_duration={HOLD}",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                        "-pix_fmt", "yuv420p", out + ".video.mp4"], stdin=subprocess.PIPE)
for n in range(NF):
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    t = n / FPS
    img = Image.frombuffer("RGB", (W, H), buf)
    i, age, dur = seg_at(min(t, VID_END - 1e-3))
    if t >= VID_END:
        age = dur + (t - VID_END)
    z = (1.0 if i % 2 == 0 else 1.08) + 0.03 * min(age, dur + HOLD) / max(dur, 1)
    if t < 0.12:  # punch-in on the very first frames for energy
        z += 0.06 * (1 - t / 0.12)
    cw, ch = W / z, H / z
    x0, y0 = (W - cw) / 2, (H - ch) * 0.45
    img = img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")
    for e in E:
        st = state(e, t)
        if not st:
            continue
        sc, a, dx, dy = st
        o = e["img"]
        if abs(sc - 1) > 1e-3:
            o = o.resize((max(1, int(o.width * sc)), max(1, int(o.height * sc))), Image.BILINEAR)
        if a < 0.999:
            o = o.copy(); o.putalpha(o.split()[3].point(lambda v: int(v * a)))
        img.alpha_composite(o, (int(e["cx"] - o.width / 2 + dx), int(e["cy"] - o.height / 2 + dy)))
    enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); dec.kill()

# ---- audio: voice + pop SFX
SR = 44100
v = subprocess.run(["ffmpeg", "-v", "error", "-i", cut, "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                   capture_output=True).stdout
voice = np.frombuffer(v, np.int16).reshape(-1, 2).astype(np.float32) / 32768
N = int(TOTAL * SR)
mix = np.zeros((N, 2), np.float32)
mix[:min(N, len(voice))] += voice[:N]
def pop(f0=900, f1=1500, d=0.07):
    tt = np.arange(int(d * SR)) / SR
    f = f0 + (f1 - f0) * tt / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 45) * 0.22
def whoosh(d=0.25):
    rng = np.random.default_rng(1); nz = rng.normal(0, 1, int(d * SR))
    env = np.sin(np.linspace(0, np.pi, len(nz))) ** 2
    nz = np.convolve(nz, np.ones(12) / 12, "same")
    return nz * env * 0.08
def put(sig, t):
    k = int(t * SR); m = min(len(sig), N - k)
    if m > 0: mix[k:k + m] += sig[:m, None]
for e in E:
    if e["sfx"] and e["anim"] != "static":
        put(pop() if e["anim"] != "slide" else pop(600, 1100, 0.06), e["t0"])
for x in segs[1:]:
    put(whoosh(), max(0, x["out"][0] - 0.12))
with wave.open(out + ".audio.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out + ".video.mp4", "-i", out + ".audio.wav",
                "-af", "highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-1.5:LRA=9",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", "-movflags", "+faststart", out],
               check=True)
print("done", out, TOTAL)
