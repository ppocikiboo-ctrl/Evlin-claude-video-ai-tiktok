"""Jana sarikata gaya TikTok (.ass + .srt) dan render ke video.
Guna: python3 build_subs.py <folder_video_asal>
Setiap baris = (perkataan, mula, tamat). Perkataan bertanda * diwarnakan (kata kunci).
"/" memulakan baris sarikata baru."""
import os, subprocess, sys

CLIPS = {
 "01-vv1": ("d2a322fb-vv1.mp4", """
Guys,@0.00 kamu@0.54 tengok@0.70 apa@0.94 yang@1.08 saya@1.22 *beli!@1.36-1.90 /
*TADAA!@2.50-3.50 /
Benda@5.80 ni@6.32 *bukan@6.66 *sebarang@6.88 *sticker@7.42 tau!@7.72-8.10 /
Itu@8.22 hari@8.74 balik-balik@8.92 lalu@9.60 *FYP@9.84 saya...@10.22-10.70
"""),
 "02-vv2": ("a522059b-vv2.mp4", """
Sekali@0.10 tengok,@0.46 banyak@1.48 *review@2.06 *positif!@2.66-3.28 /
Saya@3.28 sendiri@3.52 pun@3.74 udah@4.00 lama@4.16 sudah.@4.36-4.80 /
Sekali,@4.90 jangan@5.42 pula@6.06 kamu@6.32 pergi@6.44 *tampal@6.62 /
*satu@7.08 *saja@7.32 buah@7.70 *apple@7.90 kamu,@7.98-8.36 /
nanti@8.40 satu@8.64 saja@8.80 pula@9.05 yang...@9.22-9.63
"""),
 "03-vv3": ("f5cfa1cc-vv3.mp4", """
Nanti@0.00 satu@0.38 saja@0.52 pula@0.80 yang@1.02 *besar!@1.12-1.40 /
Mesti@1.48 *dua-dua@1.74 kamu@2.12 pergi@2.22 *tampal.@2.42-3.10 /
Kalau@3.16 kamu@3.26 tidak@3.44 *percaya,@3.64-4.05 /
kamu@4.10 *try@4.24 lah,@4.54 okey!@4.84-5.40 /
Okey,@6.28 bagi@6.76 yang@7.00 *tertanya-tanya@7.02 /
apakah@7.56 *fungsi@7.90 sticker@8.12 ni,@8.44-8.80 /
fungsi@8.86 sticker@9.38 ni@9.76 dia@10.10 boleh@10.32 /
*UP@10.56 lagi@12.16 benda@12.46 yang...@12.90-13.27
"""),
 "04-v44": ("dc404102-v44.mp4", """
yang@0.90 kamu@1.48 kurang@1.72 *yakin!@2.04-2.52 /
Fungsi@2.54 dia@3.10 adalah...@3.38-3.60 /
*LIFT,@3.60-4.15 / *VOLUME,@4.20-5.10 / *FIRM@5.16 dan@6.26 juga@6.56 /
*VISIBLE@6.86 *RESULT!@7.50-8.30 /
Kamu@8.42 jangan@9.00 ragu-ragu@9.08 mahu@9.60 *cuba,@9.80-10.16 /
kamu@10.16 tekan@10.32 *beg@10.62 *kuning@10.72 sekarang!@10.94-11.30 /
Seller@11.38 tengah@11.58 buat@11.88 *harga@12.04 *promo!@12.40-13.06
"""),
}

HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Black,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,7,4,2,110,110,560,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ACTIVE = r"{\c&H00E1FF&}"   # kuning (BGR) - perkataan sedang disebut
KEY = r"{\c&HB469FF&}"      # pink - kata kunci
WHITE = r"{\c&HFFFFFF&}"

def parse(src):
    lines = []
    for chunk in src.split("/"):
        words = []
        for tok in chunk.split():
            w, t = tok.rsplit("@", 1)
            key = w.startswith("*"); w = w.lstrip("*")
            s, _, e = t.partition("-")
            words.append([w, float(s), float(e) if e else None, key])
        lines.append(words)
    flat = [w for l in lines for w in l]
    for i, w in enumerate(flat):
        if w[2] is None: w[2] = flat[i+1][1]
    return lines

def ts(t, ass=True):
    h, m = int(t // 3600), int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}" if ass else f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s%1)*1000)):03d}"

def build(name, src, remap=lambda t: t, aligned=None):
    lines = parse(src)
    for l in lines:
        for w in l: w[1], w[2] = remap(w[1]), remap(w[2])
    if aligned:
        flat = [w for l in lines for w in l]
        for w, (st, en) in zip(flat, aligned): w[1], w[2] = st, en
    ev, srt = [], []
    for n, line in enumerate(lines, 1):
        start, end = line[0][1], line[-1][2]
        srt.append(f"{n}\n{ts(start,False)} --> {ts(end,False)}\n{' '.join(w[0] for w in line)}\n")
        for i, (w, s, e, k) in enumerate(line):
            e = end if i == len(line) - 1 else line[i+1][1]
            pop = r"{\fscx80\fscy80\t(0,90,\fscx108\fscy108)\t(90,160,\fscx100\fscy100)}" if i == 0 else ""
            txt = " ".join(
                (ACTIVE if j == i else KEY if ww[3] else WHITE) + ww[0] for j, ww in enumerate(line))
            ev.append(f"Dialogue: 0,{ts(s)},{ts(e)},Cap,,0,0,0,,{pop}{txt}")
    open(f"{name}.ass", "w").write(HEAD + "\n".join(ev) + "\n")
    open(f"{name}.srt", "w").write("\n".join(srt))


# ---------- Suntingan: buang senyap janggal + percepat ----------
SPEED = 1.15          # 1.15x lebih laju, pic suara kekal (atempo)
PAD = 0.08            # simpan sedikit nafas di tepi setiap potongan
MIN_GAP = 0.25        # senyap lebih panjang dari ini akan dipotong
ZOOM = 1.10           # punch-in zoom berselang-seli setiap potongan

# Potongan manual tambahan (saat dalam video asal): [mula, tamat] dibuang.
EXTRA_CUTS = {
    "01-vv1": [[0.0, 0.30], [3.90, 5.75]],   # pendekkan jeda selepas "TADAA" (masih tunjuk produk 0.3s)
    "02-vv2": [[0.0, 1.15]],                 # buang sisa suara potongan lepas di awal
    "04-v44": [[0.0, 1.15]],                 # buang senyap di awal
}

def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", path], capture_output=True, text=True).stdout)

def silences(path):
    import re
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af",
        f"silencedetect=n=-32dB:d={MIN_GAP}", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(st, en))

def keep_segments(name, path):
    dur = duration(path)
    cuts = [[max(0.0, s + PAD) if s > 0.01 else 0.0, e - PAD] for s, e in silences(path)]
    cuts = [c for c in cuts if c[1] - c[0] > 0.05] + EXTRA_CUTS.get(name, [])
    cuts.sort(); merged = []
    for c in cuts:
        if merged and c[0] <= merged[-1][1]: merged[-1][1] = max(merged[-1][1], c[1])
        else: merged.append(list(c))
    keep, t = [], 0.0
    for s, e in merged:
        if s - t > 0.05: keep.append((t, s))
        t = max(t, e)
    if dur - t > 0.05: keep.append((t, dur))
    return keep

def make_remap(keep):
    def remap(t):
        out = 0.0
        for s, e in keep:
            if t <= s: break
            out += min(t, e) - s
        return out / SPEED
    return remap

def norm(w):
    import re
    w = re.sub(r"[^a-z]", "", w.lower())
    return {"ni": "ini", "seja": "saja", "suja": "saja", "mau": "mahu", "coba": "cuba",
            "oke": "okey", "fungsinya": "fungsi", "function": "fungsi"}.get(w, w)

def align(name, src, remap, video):
    """Selaraskan masa setiap perkataan kepada audio video yang sudah disunting (Whisper)."""
    import difflib
    import numpy as np
    from faster_whisper import WhisperModel
    global _MODEL
    if "_MODEL" not in globals():
        _MODEL = WhisperModel("medium", device="cpu", compute_type="int8")
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-ac", "1", "-ar", "16000",
        "-f", "s16le", "-"], capture_output=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    segs, _ = _MODEL.transcribe(audio, language="ms", word_timestamps=True, beam_size=5)
    heard = []   # pecahkan "ragu-ragu" -> "ragu", "-ragu" seperti whisper
    for sg in segs:
        for w in sg.words:
            heard.append((norm(w.word), w.start, w.end))
    mine = []    # (indeks perkataan sarikata, token)
    words = [w for l in parse(src) for w in l]
    for i, w in enumerate(words):
        for tok in w[0].split("-"):
            if norm(tok): mine.append((i, norm(tok)))
    sm = difflib.SequenceMatcher(a=[m[1] for m in mine], b=[h[0] for h in heard], autojunk=False)
    times = [[None, None] for _ in words]
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            i = mine[a + k][0]; _, st, en = heard[b + k]
            if times[i][0] is None: times[i][0] = st
            times[i][1] = en
    # perkataan tidak dikesan (cth "TADAA"): guna anggaran lama, diapit jiran
    est = [(remap(w[1]), remap(w[2])) for w in words]
    for i, t in enumerate(times):
        if t[0] is None:
            prev = max([times[j][1] for j in range(i) if times[j][1] is not None] or [0])
            nxt = min([times[j][0] for j in range(i + 1, len(words)) if times[j][0] is not None] or [99])
            t[0] = min(max(est[i][0], prev), nxt); t[1] = max(min(est[i][1], nxt), t[0] + 0.2)
        if t[1] is None: t[1] = t[0] + 0.3
    # tamat baris terakhir = tamat video (atau perkataan seterusnya)
    print(f"  {name}: {len(mine)} token, padanan {sum(n for *_, n in sm.get_matching_blocks())}")
    return [tuple(t) for t in times]

def render(name, inp, keep):
    parts, labels = [], ""
    for i, (s, e) in enumerate(keep):
        z = ZOOM if i % 2 else 1.0
        vz = (f",scale={int(1080*z)//2*2}:-2,crop=1080:1920:(iw-1080)/2:(ih-1920)*0.3" if z != 1.0 else "")
        fade = min(0.02, (e - s) / 4)
        parts.append(f"[0:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS{vz},setsar=1[v{i}]")
        parts.append(f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d={fade:.3f},afade=t=out:st={e-s-fade:.3f}:d={fade:.3f}[a{i}]")
        labels += f"[v{i}][a{i}]"
    parts.append(f"{labels}concat=n={len(keep)}:v=1:a=1[cv][ca]")
    parts.append(f"[cv]setpts=PTS/{SPEED},fps=30[vout]")
    parts.append(f"[ca]atempo={SPEED},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", inp, "-filter_complex", ";".join(parts),
        "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        f"output/_raw_{name}.mp4"], check=True)

def burn(name):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"output/_raw_{name}.mp4", "-vf",
        f"ass={name}.ass", "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt",
        "yuv420p", "-c:a", "copy", "-movflags", "+faststart", f"output/{name}-sarikata.mp4"], check=True)
    os.remove(f"output/_raw_{name}.mp4")

if __name__ == "__main__":
    srcdir = sys.argv[1]
    os.makedirs("output", exist_ok=True)
    for name, (vid, src) in CLIPS.items():
        inp = os.path.join(srcdir, vid)
        keep = keep_segments(name, inp)
        remap = make_remap(keep)
        render(name, inp, keep)
        try:
            aligned = align(name, src, remap, f"output/_raw_{name}.mp4")
        except ImportError:
            aligned = None   # tiada faster-whisper: guna anggaran masa sahaja
        build(name, src, remap, aligned)
        burn(name)
        before, after = duration(inp), duration(f"output/{name}-sarikata.mp4")
        print(f"siap {name}: {before:.1f}s -> {after:.1f}s, {len(keep)} potongan")
