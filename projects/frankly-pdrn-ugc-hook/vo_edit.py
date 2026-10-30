#!/usr/bin/env python3
"""Hook edit + Malay voice-over + animated word-by-word (karaoke) subtitles.

Voice: Microsoft Edge neural TTS (ms-MY-YasminNeural) via the `edge-tts` package,
using its word-boundary events to time each subtitle word. If the TTS service
cannot be reached (or --no-voice is given) the script still renders the video
with subtitles timed from a syllable estimate, and keeps the original song.

Usage:
  python3 vo_edit.py --video /path/to/selfie.mp4 [--voice ms-MY-YasminNeural] [--no-voice]
"""
import argparse
import asyncio
import math
import os
import re
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw

import edit
from edit import (BROWN, CTA_YELLOW, FPS, H, HOOK_LEN, SHADOW, SPARKS, W, appear, audio, burst,
                  ease_out, flash, grade, pill, place, prog, src_frame, text_img, zoom)
from edit import HOOK_SRC, MAIN_LEN

DURATION = HOOK_LEN + MAIN_LEN

# Voice-over script: (target start s, sentence). Words wrapped in *...* are emphasised.
SCRIPT = [
    (0.10, "Nak tahu rahsia kulit *glowing* aku? 👀"),
    (2.00, "Ni dia, *FRANKLY* *PDRN* Bounce Ball Serum! 🧡"),
    (4.45, "Dalam botol ada *bola* *serum* *oren* dengan salmon DNA PDRN."),
    (7.55, "*Goncang* dulu, sapu, lepas tu *tepuk* perlahan. ✨"),
    (10.05, "Kulit rasa *lembap* dan nampak *glowing!* 💧"),
    (12.60, "Nak cuba? Tekan *bakul* *kuning* sekarang! 🛒"),
]

WHITE = (255, 255, 255)
HILITE = (255, 222, 60)
EMPH = (255, 150, 60)
SUB_Y = 330
WORDS = []   # filled in main(): dicts {w, emph, emoji, t0, t1, page}
PAGES = []   # [(first_word_index, last_word_index)]


# ------------------------------------------------------------------ timing
def syllables(w):
    return max(1, len(re.findall(r"[aeiou]+", w.lower())) + (1 if re.search(r"\d", w) else 0))


def estimate_timing(words_by_sentence, starts, ends):
    for ws, t0, t1 in zip(words_by_sentence, starts, ends):
        span = t1 - t0
        weights = [syllables(w["w"]) + (0.6 if w["w"][-1] in ",.!?" else 0) for w in ws]
        tot = sum(weights)
        t = t0
        for w, k in zip(ws, weights):
            d = span * k / tot
            w["t0"], w["t1"] = t, t + d
            t += d


async def _tts(text, voice, mp3, rate):
    import edge_tts
    com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary",
                               proxy=os.environ.get("HTTPS_PROXY"))
    bounds = []
    with open(mp3, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                bounds.append((ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]))
    return bounds


def synth_voice(sentences, voice, work, rate="+8%"):
    """-> list of (wav_samples, word_bounds) per sentence, or None if TTS is unreachable."""
    out = []
    for k, s in enumerate(sentences):
        mp3 = os.path.join(work, f"vo{k}.mp3")
        wav = os.path.join(work, f"vo{k}.wav")
        try:
            bounds = asyncio.run(_tts(s, voice, mp3, rate))
        except Exception as e:  # network policy, DNS, service errors
            print(f"[voice] TTS unavailable: {type(e).__name__}: {e}", file=sys.stderr)
            return None
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ac", "1", "-ar", str(audio.SR), wav], check=True)
        with wave.open(wav) as w:
            x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64) / 32768
        out.append((x, bounds))
    return out


def paginate(words, max_chars=17, max_words=4):
    pages, cur, n = [], [], 0
    for i, w in enumerate(words):
        L = len(w["w"]) + (2 if w["emoji"] else 0)
        if cur and (n + L > max_chars or len(cur) >= max_words or w["sent"] != words[cur[0]]["sent"]):
            pages.append((cur[0], cur[-1]))
            cur, n = [], 0
        cur.append(i)
        n += L + 1
    if cur:
        pages.append((cur[0], cur[-1]))
    return pages


# --------------------------------------------------------------- drawing
def word_img(w, state):
    txt = w["w"] + (" " + w["emoji"] if w["emoji"] else "")
    if state == "active":
        return text_img(txt, 84, HILITE, "xb", max_w=1000, shadow=(5, 10, (30, 12, 0, 235)))
    col = EMPH if w["emph"] else WHITE
    return text_img(txt, 80, col, "xb", max_w=1000, shadow=(5, 10, (30, 12, 0, 220)))


def draw_subs(base, t):
    page = None
    for k, (a, b) in enumerate(PAGES):
        end = WORDS[b]["t1"] + 0.25
        nxt = WORDS[PAGES[k + 1][0]]["t0"] if k + 1 < len(PAGES) else 1e9
        if WORDS[a]["t0"] - 0.05 <= t < min(max(end, WORDS[b]["t1"]), nxt):
            page = (a, b)
    if not page:
        return
    a, b = page
    imgs, states = [], []
    for i in range(a, b + 1):
        w = WORDS[i]
        if t < w["t0"] - 0.03:
            imgs.append(None)
            states.append(None)
            continue
        st = "active" if w["t0"] - 0.03 <= t < w["t1"] else "past"
        imgs.append(word_img(w, st))
        states.append(st)
    # layout using the final (past) widths so words don't shift while popping in
    widths = [word_img(WORDS[i], "past").width for i in range(a, b + 1)]
    gap = 6
    total = sum(widths) + gap * (len(widths) - 1)
    rows = [list(range(len(widths)))]
    if total > 980:   # wrap into two rows
        acc, split = 0, len(widths)
        for j, wd in enumerate(widths):
            acc += wd + gap
            if acc > total / 2:
                split = j + 1 if j + 1 < len(widths) else j
                break
        rows = [list(range(split)), list(range(split, len(widths)))]
    lh = 108
    y0 = SUB_Y - (len(rows) - 1) * lh / 2
    for r, row in enumerate(rows):
        rw = sum(widths[j] for j in row) + gap * (len(row) - 1)
        x = 540 - rw / 2
        for j in row:
            im, st, w = imgs[j], states[j], WORDS[a + j]
            cx, cy = x + widths[j] / 2, y0 + r * lh
            if im is not None:
                p = prog(t, w["t0"] - 0.03, w["t0"] + 0.15)
                s = 0.55 + 0.45 * edit_back(p)
                if st == "active":
                    s *= 1.0 + 0.06 * math.sin(math.pi * prog(t, w["t0"], w["t1"]))
                    box = Image.new("RGBA", (im.width + 36, im.height + 6), (0, 0, 0, 0))
                    ImageDraw.Draw(box).rounded_rectangle((0, 8, box.width - 1, box.height - 8), 22,
                                                          fill=(240, 104, 32, 225))
                    place(base, box, cx, cy + 4, s, min(1, p * 2))
                place(base, im, cx, cy - 10 * (1 - ease_out(p)), s, min(1, p * 2.5))
            x += widths[j] + gap


def edit_back(p):
    from render import ease_back
    return ease_back(p)


def render_frame(i):
    t = i / FPS
    if t < HOOK_LEN:
        base = grade(src_frame(HOOK_SRC + t))
        z = 1.16 - 0.1 * ease_out(prog(t, 0, 0.5))
        base = zoom(base, z, W / 2 + 14 * math.sin(t * 60) * (1 - prog(t, 0, 0.25)), 820)
        SPARKS.draw(base, t, 0.8)
        s, a, _ = appear(t, 0.5, "pop", 0.4)
        place(base, pill("Serum ada BOLA OREN dalam botol! 🧡", 50), 540, 1570, s, a)
        burst(base, t, 0.55, 540, 1570, seed=2, radius=440)
        fl = 0.9 * (1 - prog(t, 0, 0.12)) + 0.9 * prog(t, HOOK_LEN - 0.12, HOOK_LEN)
    else:
        u = t - HOOK_LEN
        base = zoom(grade(src_frame(u)), 1.0 + 0.06 * (1 - ease_out(prog(u, 0, 0.35))))
        s, a, dy = appear(u, 0.6, "up", 0.4, 3.0, 0.25)
        place(base, pill("FRANKLY PDRN Bounce Ball Serum 🧡", 48), 540, 1570 + dy, s, a)
        s, a, _ = appear(u, 11.6, "pop", 0.4)
        pulse = 1 + 0.05 * math.sin((u - 11.6) * 2 * math.pi * 1.8) * prog(u, 12.0, 12.2)
        place(base, pill("Tekan BAKUL KUNING 🛒", 62, fg=BROWN, bg=CTA_YELLOW, bg2=(255, 178, 40)),
              540, 1575, s * pulse, a)
        burst(base, u, 11.65, 540, 1575, seed=20, radius=460, n=14)
        fl = 0.7 * (1 - prog(u, 0, 0.15))
    draw_subs(base, t)
    base = flash(base, fl)
    return base.convert("RGB").tobytes()


# ------------------------------------------------------------------ audio
def build_audio(video, path, work, voice_parts, starts):
    raw = os.path.join(work, "orig.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-ac", "2", "-ar", str(audio.SR), raw], check=True)
    with wave.open(raw) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2).astype(np.float64) / 32768
    sr = audio.SR

    def seg(a, b, fi=0.01, fo=0.06):
        s = x[int(a * sr):int(b * sr)].copy()
        e = np.ones(len(s))
        e[:int(fi * sr)] = np.linspace(0, 1, int(fi * sr))
        e[len(s) - int(fo * sr):] = np.linspace(1, 0, int(fo * sr))
        return s * e[:, None]

    song = np.concatenate([seg(HOOK_SRC, HOOK_SRC + HOOK_LEN) * 0.8, seg(0, MAIN_LEN, 0.01, 0.4)])
    fx = np.zeros_like(song)
    rng = np.random.default_rng(5)
    for t0, kind in [(0.0, "impact"), (0.1, "shimmer"), (0.5, "pop"), (HOOK_LEN - 0.3, "whoosh"),
                     (HOOK_LEN + 11.6, "pop"), (HOOK_LEN + 11.65, "sparkle")]:
        audio.add(fx, audio.sfx(kind, rng), t0)
    if voice_parts:
        vo = np.zeros(len(song))
        for (v, _), t0 in zip(voice_parts, starts):
            i = int(t0 * sr)
            v = v[: len(vo) - i]
            vo[i:i + len(v)] += v
        vo *= 0.9 / max(1e-6, np.abs(vo).max())
        # duck the song under the voice (smoothed envelope)
        env = np.convolve(np.abs(vo) > 0.02, np.ones(int(0.25 * sr)) / int(0.25 * sr), "same")
        duck = 1 - 0.72 * np.clip(env * 3, 0, 1)
        mix = song * 0.6 * duck[:, None] + vo[:, None] * 0.95 + fx * 0.3
    else:
        mix = song + fx * 0.45
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    mix *= 0.93 / np.abs(mix).max()
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((mix * 32767).astype("<i2").tobytes())


def main():
    global WORDS, PAGES
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", default=os.path.join(edit.HERE, "output", "frankly-pdrn-ugc-voiceover.mp4"))
    ap.add_argument("--voice", default="ms-MY-YasminNeural", help="or ms-MY-OsmanNeural (male)")
    ap.add_argument("--no-voice", action="store_true")
    ap.add_argument("--stills")
    args = ap.parse_args()
    work = tempfile.mkdtemp(prefix="vo-")
    edit.FRAMES = os.path.join(work, "f")
    os.makedirs(edit.FRAMES)
    subprocess.run(["ffmpeg", "-v", "error", "-i", args.video, "-vf", f"fps={FPS}", "-q:v", "2",
                    os.path.join(edit.FRAMES, "f%04d.jpg")], check=True)

    starts = [s for s, _ in SCRIPT]
    ends = starts[1:] + [DURATION - 0.4]
    by_sent = []
    for k, (_, s) in enumerate(SCRIPT):
        ws = [dict(w, sent=k) for w in tokens_with_emoji(s)]
        by_sent.append(ws)
    spoken = [re.sub(r"[*]|[^\w\s,.!?'-]", "", s).strip() for _, s in SCRIPT]
    voice = None if args.no_voice else synth_voice(spoken, args.voice, work)
    if voice:
        for ws, (v, bounds), t0 in zip(by_sent, voice, starts):
            if len(bounds) == len(ws):
                for w, (a, b, _) in zip(ws, bounds):
                    w["t0"], w["t1"] = t0 + a, t0 + b
            else:
                estimate_timing([ws], [t0], [t0 + len(v) / audio.SR])
            # stretch each word to the next word's start so highlights don't blink
        print("[voice] used", args.voice)
    else:
        estimate_timing(by_sent, starts, [e - 0.15 for e in ends])
        print("[voice] none — subtitles timed by syllable estimate; original song kept")
    WORDS = [w for ws in by_sent for w in ws]
    for i in range(len(WORDS) - 1):
        if WORDS[i + 1]["sent"] == WORDS[i]["sent"]:
            WORDS[i]["t1"] = WORDS[i + 1]["t0"]
    PAGES = paginate(WORDS)

    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    if args.stills:
        for s in args.stills.split(","):
            Image.frombytes("RGB", (W, H), render_frame(int(float(s) * FPS))).save(
                os.path.join(out_dir, f"vo_still_{float(s):05.2f}.jpg"), quality=90)
        return
    wav = os.path.join(work, "mix.wav")
    build_audio(args.video, wav, work, voice, starts)
    n = int(round(DURATION * FPS))
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-shortest", args.out], stdin=subprocess.PIPE)
    from multiprocessing import Pool
    with Pool(os.cpu_count()) as pool:
        for buf in pool.imap(render_frame, range(n), chunksize=4):
            enc.stdin.write(buf)
    enc.stdin.close()
    enc.wait()
    print("wrote", args.out)


def tokens_with_emoji(sentence):
    out = []
    for raw in sentence.split():
        if not re.search(r"\w", raw):
            if out:
                out[-1]["emoji"] = raw
            continue
        out.append(dict(w=raw.replace("*", ""), emph=raw.startswith("*"), emoji=""))
    return out


if __name__ == "__main__":
    main()
