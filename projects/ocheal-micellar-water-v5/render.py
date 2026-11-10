"""Step 2 (v5 talking-head ad): graphics, music under the voice, final encode.

The creator's processed voice (build/voice.wav) carries the video. On top:
a STOP-SCROLL hook, a pro lower-third when the bottles appear, a "KENAPA
SUKA?" checklist while she handles the bottle, STEP chips on the pump and
first wipe, a payoff line, then a frozen-frame product tail with the
yellow-bag CTA. Jump cuts are punch-ins with a white flash; music is ducked
under her voice. Building blocks come from the earlier O'CHEAL edits.

    python3 build_base.py && python3 render.py   # -> output/ocheal_micellar_tiktok_v5.mp4
    python3 render.py --stills                    # preview stills -> build/stills/
"""
import argparse
import importlib.util
import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from edl import FPS, H, SPEECH_END, TOTAL, W, src_to_out, timeline

ROOT = Path(__file__).resolve().parent


def _load(name, folder):
    spec = importlib.util.spec_from_file_location(name, ROOT.parent / folder / "render.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # each picks up this folder's edl.py (same API)
    return mod


v1 = _load("kbeauty_v1", "ocheal-micellar-water")
v2 = _load("sticker_v2", "ocheal-micellar-water-v2")
v3 = _load("caption_v3", "ocheal-micellar-water-v3")

text_img, paste, clamp = v1.text_img, v1.paste, v1.clamp
ease_out_cubic, ease_out_back, ease_in_out, env = v1.ease_out_cubic, v1.ease_out_back, v1.ease_in_out, v1.env
OUT = ROOT / "output" / "ocheal_micellar_tiktok_v5.mp4"

HOT, YEL, INK, WHITE = v2.HOT, v2.YEL, v2.INK, v2.WHITE
SAFE_L, SAFE_R = 60, 880
TOP_Y = 250
BPM = 118
BEAT = 60 / BPM


def at(t_src):
    t = src_to_out(t_src)
    assert t is not None, f"source time {t_src} was cut"
    return t


class LowerThird:
    """Pro lower-third: pink accent bar wipes in, then a white plate with two lines."""

    def __init__(self, t0, t1, l1, l2, y=1250):
        self.t0, self.t1, self.y = t0, t1, y
        self.l1 = text_img(l1, "Montserrat-ExtraBold.ttf", 54, INK)
        self.l2 = text_img(l2, "Montserrat-Bold.ttf", 38, (120, 70, 95))
        while self.l1.width > SAFE_R - SAFE_L - 70:
            self.l1 = text_img(l1, "Montserrat-ExtraBold.ttf", int(self.l1.height * 0.8), INK)

    def sfx(self):
        return [("swish", self.t0), ("click", self.t0 + 0.25)]

    def draw(self, c):
        if not (self.t0 <= c.t <= self.t1):
            return
        a = c.t - self.t0
        out = clamp((self.t1 - c.t) / 0.25)
        w = max(self.l1.width, self.l2.width) + 70
        h = self.l1.height + self.l2.height + 46
        bar = ease_out_cubic(a / 0.3) * out
        plate = ease_out_cubic((a - 0.12) / 0.35) * out
        d = ImageDraw.Draw(c.ov)
        x0 = SAFE_L
        d.rectangle((x0, self.y, x0 + 14, self.y + h * bar), fill=HOT + (255,))
        if plate > 0:
            pw = int(w * plate)
            im = Image.new("RGBA", (w, h), (255, 255, 255, 235))
            im.alpha_composite(self.l1, (40, 18))
            im.alpha_composite(self.l2, (40, 24 + self.l1.height))
            im = im.crop((0, 0, max(1, pw), h))
            c.ov.alpha_composite(v2.hard_shadow(im, (8, 10), 0.25), (x0 + 14, int(self.y)))



def camera(fi):
    t = fi / FPS
    tl = timeline()
    if t >= SPEECH_END:  # product tail: slow push on the frozen last frame
        z0 = tl[-1][3][4][1]
        u = (t - SPEECH_END) / (TOTAL - SPEECH_END)
        z = z0 * (1 + 0.10 * ease_in_out(u))
    else:
        for n, s, e, seg in tl:
            if s <= t < e:
                break
        z0, z1 = seg[4]
        z = z0 + (z1 - z0) * ease_in_out((t - s) / (e - s))
        z *= 1 + 0.06 * (1 - ease_out_cubic((t - s) / 0.18))  # punch at every jump cut
    z *= 1 + 0.012 * math.exp(-((t % BEAT) * 9))           # subtle pulse on the beat
    dx, dy = v2.shake(t)
    z = max(z, 1.03)
    hw, hh = W / (2 * z), H / (2 * z)
    cx = clamp(W / 2 + dx / z, hw, W - hw)
    cy = clamp(H * 0.45 + dy / z, hh, H - hh)
    return z, cx, cy


def build_elements():
    v2.SLAMS.clear()
    P = v1.Particles
    els = [v1.Vignette()]
    cuts = [s for _, s, _, _ in timeline()[1:]]
    els += [v1.Flash(t, 0.45, 0.16) for t in cuts]

    # 1. HOOK
    els.append(v2.Stack(0.0, 2.6, [(v2.tape("STOP SCROLL! 🛑", 76, YEL, INK, -3), 0.05)], y=TOP_Y - 10))
    els.append(v3.Caption(0.35, 2.6, "nak makeup tanggal tanpa *pedih?* 😍", TOP_Y + 120, size=78, wps=6, big=True))
    els.append(P(0.05, 0.6, "sparkle", (120, 260, 960, 640), 26, life=(0.4, 0.8), size=(16, 30),
                 vel=((-180, 180), (-140, 80)), seed=51))

    # 2. PRODUCT reveal (bottles come up at src 6.75)
    t = at(6.80)
    els.append(LowerThird(t, at(10.3), "O’CHEAL Micellar Water", "300ML  ·  Hyaluronic Acid + Rose 🌹"))
    els.append(P(t, t + 1.4, "sparkle", (520, 700, 1000, 1300), 14, life=(0.5, 1.0), size=(14, 28),
                 vel=((-20, 20), (-40, 10)), seed=52))

    # 3. WHY: checklist while she handles the bottle
    t0 = at(10.6)
    els.append(v2.Checklist(t0, at(15.4), "KENAPA SUKA? 💗", ["X PEDIH", "X BERMINYAK", "X RASA KERING"],
                            [t0 + 0.35, t0 + 1.25, t0 + 2.15]))

    # 4. HOW: real pump + first wipe
    els.append(v3.StepChip(at(15.6), at(17.35), 1, "BASAHKAN KAPAS"))
    els.append(v3.StepChip(at(17.45), at(19.2), 2, "LAP LEMBUT-LEMBUT"))

    # 5. PAYOFF while she talks
    els.append(v3.Caption(at(19.9), at(24.6), "kulit terasa *lembut* & _segar_ 🤍", TOP_Y, size=88, wps=5, big=True))
    els.append(v2.LightSweep(at(22.0), 1.0))
    els.append(P(at(19.9), at(24.6), "sparkle", (250, 520, 830, 1000), 8, life=(0.6, 1.2), size=(14, 26),
                 vel=((-10, 10), (-30, 0)), seed=53))

    # 6. CTA: bottles up at the end, then the frozen-frame tail
    t = at(25.15)
    els.append(v3.Tag(t, TOTAL + 1, "O’CHEAL Micellar Water 300ML", 470, 300, fill=HOT))
    els.append(v3.Caption(t + 0.25, TOTAL + 1, "TEKAN *BEG* *KUNING* 🛍️", 1140, size=88, wps=7, big=True))
    els.append(v3.Caption(SPEECH_END + 0.3, TOTAL + 1, "harga terkini dalam beg kuning", 1340, size=46, wps=9))
    els.append(v3.YellowBag(t + 0.6, TOTAL + 1))
    els.append(P(SPEECH_END, TOTAL + 1, "petal", (40, 60, 1040, 400), 8, life=(2.0, 2.8), size=(22, 34),
                 vel=((-50, 50), (150, 240)), seed=54))
    return els


def cue_list(els):
    cues = []
    for el in els:
        if hasattr(el, "sfx"):
            cues += el.sfx()
    for t in [s for _, s, _, _ in timeline()[1:]]:
        cues.append(("whoosh", t - 0.2))
    return sorted((k, t) for k, t in cues if 0 <= t < TOTAL)


# ---------------------------------------------------------------- audio

def make_audio():
    """Music + SFX bed (numpy), then ffmpeg ducks the music under the voice and mixes."""
    SR = v1.SR
    chords = [[57, 61, 64, 69], [54, 57, 61, 66], [50, 54, 57, 62], [52, 56, 59, 64]]  # A - F#m - D - E
    music = v1.make_music(TOTAL, bpm=BPM, chords=chords)
    n = int((TOTAL + 0.05) * SR)
    music = music[:n]
    music /= np.abs(music).max() + 1e-9
    tail = int(1.0 * SR)
    music[-tail:] *= np.linspace(1, 0, tail)[:, None] ** 1.5
    fx = v2.make_fx()
    sfx = np.zeros((n, 2))
    for kind, t in cue_list(build_elements()):
        s = fx[kind]
        st = int(t * SR)
        seg = sfx[st:st + len(s)]
        seg += s[:len(seg), None]
    import wave

    def write(path, x):
        pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
        with wave.open(str(path), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())

    write(ROOT / "build" / "music.wav", music * 0.5)
    write(ROOT / "build" / "sfx.wav", sfx * 0.6)
    mix = ROOT / "build" / "mix.wav"
    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        "-i", str(ROOT / "build" / "voice.wav"), "-i", str(ROOT / "build" / "music.wav"), "-i", str(ROOT / "build" / "sfx.wav"),
        "-filter_complex",
        "[0]aformat=channel_layouts=stereo,apad,asplit=2[v][key];"
        "[1]volume=-15dB[m];"
        "[m][key]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=350:makeup=1[md];"
        "[2]volume=-9dB[fx];"
        "[v][md][fx]amix=inputs=3:duration=longest:normalize=0,atrim=0:" + f"{TOTAL:.3f}",
        "-ar", "48000", str(mix)], check=True)
    return mix


# ---------------------------------------------------------------- main

def render_frame(fi, img, els):
    z, cx, cy = camera(fi)
    img = v1.apply_camera(img, z, cx, cy)
    img = v1.bloom(img, 0.07)
    frame = img.convert("RGBA")
    ov = Image.new("RGBA", (W, H))
    c = v1.Ctx(fi, frame, ov, (z, cx, cy))
    for el in els:
        el.draw(c)
    return Image.alpha_composite(frame, ov).convert("RGB")


def all_frames(base):
    """Base frames, then the last one held for the music-only tail."""
    last = None
    fi = 0
    for img in v1.frames_from(base):
        last = img
        yield fi, img
        fi += 1
    while fi < round(TOTAL * FPS):
        yield fi, last
        fi += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    args = ap.parse_args()
    els = build_elements()
    base = ROOT / "build" / "base.mp4"
    if args.stills:
        outdir = ROOT / "build" / "stills"
        outdir.mkdir(exist_ok=True)
        want = {round(t * FPS) for t in [0.3, 1.2, 2.2, 4.0, 6.9, 7.8, 10.6, 11.6, 13.2, 14.6, 16.3, 17.5, 19.0,
                                          20.6, 22.2, 23.0, 24.2, 25.0]}
        for fi, img in all_frames(base):
            if fi in want:
                render_frame(fi, img, els).save(outdir / f"f_{fi / FPS:05.2f}.jpg", quality=88)
        return
    mix = make_audio()
    OUT.parent.mkdir(exist_ok=True)
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", str(mix),
        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(OUT)], stdin=subprocess.PIPE)
    els = build_elements()
    for fi, img in all_frames(base):
        enc.stdin.write(render_frame(fi, img, els).tobytes())
        if fi % 60 == 0:
            print(f"frame {fi}/{round(TOTAL * FPS)}", flush=True)
    enc.stdin.close()
    enc.wait()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
