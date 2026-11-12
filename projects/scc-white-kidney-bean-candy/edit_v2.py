#!/usr/bin/env python3
"""Version 2: no voice. Product features, benefits and CTA told with on-screen text.

Outputs two files:
  <out>.mp4          with a soft generated background beat
  <out>-nosound.mp4  silent, for adding a TikTok library sound in the app

Usage: python3 edit_v2.py <input.mp4> <out-without-.mp4>
"""
import math
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

from edit import (DEEP, FONT_BLACK, FONT_BOLD, FPS, H, PINK, W, WHITE, YELLOW,
                  font, progress_bar, review_card, text_card)

HERE = os.path.dirname(os.path.abspath(__file__))
SPEED = 1.10
# Whole clip kept (voice is removed, so no pause-cutting); split for punch-in zooms.
SEGMENTS = [(0.43, 7.00), (7.00, 14.40), (14.40, 17.10), (17.10, 20.30),
            (20.30, 23.20), (23.20, 29.60), (29.60, 33.60), (33.60, 35.55)]
ZOOMS = [1.00, 1.08, 1.00, 1.10, 1.00, 1.08, 1.00, 1.06]
GREEN = (22, 163, 74)


def check_item(num, text, bg=WHITE, fg=DEEP, size=50):
    """Numbered checklist row: pink circle with number + text."""
    f = font(FONT_BLACK, size)
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = d.textlength(text, font=f)
    r = int(size * 0.75)
    pad = 22
    cw, ch = int(tw + r * 2 + pad * 3), int(size * 1.6)
    img = Image.new("RGBA", (cw + 20, ch + 20), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle((10, 10, cw + 10, ch + 10), ch // 2, fill=bg + (240,))
    cx, cy = 10 + pad + r, 10 + ch // 2
    dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=PINK)
    nf = font(FONT_BLACK, int(size * 0.85))
    dr.text((cx, cy), str(num), font=nf, fill=WHITE, anchor="mm")
    dr.text((cx + r + pad, cy), text, font=f, fill=fg, anchor="lm")
    return img


def build_overlays(tmp):
    ov = []

    def add(name, img, t0, t1, y, x=None, anim="up"):
        p = os.path.join(tmp, name + ".png")
        img.save(p)
        ov.append((p, t0, t1, (W - img.width) // 2 if x is None else x, y, anim))

    # HOOK (layered wording, no direct diet claims)
    add("h1", text_card(["Baju impian masih", "tergantung dalam almari?"], size=76,
                        highlight="Baju impian"), 0.0, 3.3, 230, anim="pop")
    add("h2", text_card(["Dah tiba masa dia", "'keluar' dari almari..."], size=76, bg=DEEP,
                        highlight="'keluar'"), 3.3, 6.4, 230, anim="pop")
    add("h3", text_card(["Ini rahsia saya..."], size=50, bg=None), 0.4, 6.4, 1560)
    # PRODUCT
    add("prod", text_card(["SCC White Kidney Bean", "+ L-Carnitine Candy"], size=58,
                          fg=DEEP, bg=WHITE), 6.4, 8.8, 230, anim="pop")
    # FEATURES — checklist that builds up
    t_end = 17.8
    add("fhead", text_card(["CARA MAKAN"], size=60, bg=PINK, pad=(40, 16)), 8.8, t_end, 150, anim="pop")
    items = [("1 pack = 5 biji", 9.1), ("Belah 2 - 1/2 biji sehari", 11.0),
             ("Makan selepas sarapan", 12.9), ("Minum air 3 liter sehari", 14.8)]
    for i, (txt, t0) in enumerate(items):
        add(f"f{i}", check_item(i + 1, txt), t0, t_end, 290 + i * 118, x=60, anim="left")
    # ROUTINE (replaces buyer reviews)
    add("r1", text_card(["Rutin kecil,", "langkah besar"], size=80, highlight="langkah besar"),
        17.8, 20.4, 230, anim="pop")
    add("r2", text_card(["Simple, comel,", "muat dalam beg tangan"], size=70, bg=DEEP,
                        highlight="muat"), 20.4, 22.8, 230, anim="pop")
    # BENEFITS (figurative)
    add("adv1", text_card(["Baju lama pun mula", "'senyum' balik..."], size=72,
                          highlight="'senyum'"), 22.8, 25.4, 230, anim="pop")
    add("adv2", text_card(["Tak perlu tunggu tahun depan,", "biar baju impian", "yang tunggu awak"],
                          size=60, bg=DEEP, highlight="baju impian"), 25.4, 27.6, 230, anim="pop")
    # CTA: what / why now / cost of waiting
    add("cta", text_card(["KLIK BEG KUNING", "SEKARANG"], size=90, fg=(30, 30, 30), bg=YELLOW),
        27.6, 99, 200, anim="pop")
    add("why", text_card(["Kenapa sekarang?", "Mula hari ini, esok selangkah", "lebih dekat"],
                         size=46, bg=GREEN, highlight="Kenapa sekarang?"), 28.3, 99, 1180, anim="up")
    add("lose", text_card(["Tangguh lagi?", "Baju impian terus berhabuk dalam almari"],
                          size=40, bg=(20, 20, 20), highlight="Tangguh lagi?"),
        29.6, 99, 1440, anim="up")
    add("disc", text_card(["Hasil berbeza mengikut individu.",
                           "Amalkan pemakanan seimbang & minum air secukupnya."],
                          size=28, bg=(0, 0, 0), fpath=FONT_BOLD, pad=(22, 10), radius=16),
        22.8, 99, 1730, anim="none")
    return ov


def music(path, dur):
    """Soft 110 BPM beat: kick, off-beat hat, C-Am-F-G pad. Generated, royalty-free."""
    b = 60 / 110
    kick = f"0.55*sin(2*PI*55*t*(1+2*exp(-30*mod(t,{b}))))*exp(-9*mod(t,{b}))"
    hat = f"0.06*(random(0)*2-1)*exp(-60*mod(t+{b/2},{b}))"
    bar = 4 * b
    roots = [261.63, 220.00, 174.61, 196.00]
    chord = lambda r: f"(sin(2*PI*{r}*t)+0.6*sin(2*PI*{r*1.25992}*t)+0.5*sin(2*PI*{r*1.49831}*t))"
    pad = "+".join(f"between(mod(t,{4*bar}),{i*bar},{(i+1)*bar})*{chord(r)}"
                   for i, r in enumerate(roots))
    expr = f"{kick}+{hat}+0.07*({pad})*(0.6+0.4*sin(2*PI*t/{b}))"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                    f"aevalsrc='{expr}':s=44100:d={dur + 0.5}",
                    "-af", f"lowpass=f=6000,afade=t=in:d=0.5,afade=t=out:st={dur - 1.2}:d=1.2,"
                           "loudnorm=I=-16:TP=-1.5", "-ac", "2", path], check=True)


def main(src, out):
    tmp = tempfile.mkdtemp()
    final_len = sum(b - a for a, b in SEGMENTS) / SPEED
    ov = build_overlays(tmp)
    bar = os.path.join(tmp, "bar.png")
    progress_bar().save(bar)

    inputs = ["-i", src]
    fc, cut_times, acc = [], [], 0.0
    for i, ((a, b), z) in enumerate(zip(SEGMENTS, ZOOMS)):
        cw, ch = int(W / z) // 2 * 2, int(H / z) // 2 * 2
        fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,crop={cw}:{ch}:(iw-{cw})/2:(ih-{ch})/2,"
                  f"scale={W}:{H},setsar=1[v{i}]")
        cut_times.append(acc / SPEED)
        acc += b - a
    n = len(SEGMENTS)
    fc.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[vc]")
    flash = "+".join(f"between(t,{t:.3f},{t + 0.08:.3f})" for t in cut_times[1:])
    fc.append(f"[vc]setpts=PTS/{SPEED},fps={FPS},"
              f"eq=contrast=1.06:saturation=1.18:brightness=0.02:gamma=0.98,"
              f"unsharp=5:5:0.6,vignette=PI/6,"
              f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.55:t=fill:enable='{flash}'[v_base]")

    last = "v_base"
    for k, (png, t0, t1, x, y, anim) in enumerate(ov):
        t1 = min(t1, final_len)
        d = t1 - t0
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", png]
        fade = f"fade=t=in:st=0:d=0.2:alpha=1,fade=t=out:st={max(d - 0.2, 0):.3f}:d=0.2:alpha=1"
        if t1 >= final_len - 0.01:
            fade = "fade=t=in:st=0:d=0.2:alpha=1"
        fc.append(f"[{k + 1}:v]format=rgba,{fade},setpts=PTS-STARTPTS+{t0}/TB[o{k}]")
        xe, ye = f"{x}", f"{y}"
        if anim == "pop":
            ye = f"{y}-40*max(0\\,1-(t-{t0})/0.18)*sin(PI*min(1\\,(t-{t0})/0.18))"
        elif anim == "left":
            xe = f"{x}-300*max(0\\,1-(t-{t0})/0.25)"
        elif anim == "up":
            ye = f"{y}+90*max(0\\,1-(t-{t0})/0.25)"
        fc.append(f"[{last}][o{k}]overlay=x='{xe}':y='{ye}':eof_action=pass:"
                  f"enable='between(t,{t0},{t1})'[l{k}]")
        last = f"l{k}"
    inputs += ["-loop", "1", "-framerate", str(FPS), "-i", bar]
    fc.append(f"[{last}][{len(ov) + 1}:v]overlay=x='-W+W*t/{final_len:.3f}':y=H-14:shortest=1,"
              f"format=yuv420p[vout]")

    silent = out + "-nosound.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc),
                    "-map", "[vout]", "-an", "-t", f"{final_len:.3f}", "-c:v", "libx264",
                    "-preset", "medium", "-crf", "18", "-profile:v", "high",
                    "-movflags", "+faststart", silent], check=True)
    wav = os.path.join(tmp, "music.wav")
    music(wav, final_len)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", wav, "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", out + ".mp4"], check=True)
    print(f"done: {out}.mp4 + {silent} ({final_len:.1f}s)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
