"""Generate the HyperFrames project for the loan-scam academic video.

Writes static HTML: index.html (video, music, SFX, scene hosts) and one scene file per
chapter in compositions/. Every timed element is written out in the HTML; the per-scene
script only builds tweens from the data-* attributes it finds.
"""
import json, os, html, sys

S = sys.argv[1]
P = f"{S}/loanscam"
W, H = 1080, 1920
EDL = json.load(open(f"{S}/work/edl.json"))
TALK_DUR = round(EDL["duration"], 3)
TAIL = 4.4                       # end card holds after the last word
TOTAL = round(TALK_DUR + TAIL, 3)
SFXM = json.load(open(f"{S}/work/sfx_meta.json"))
SEC = {s["id"]: s for s in EDL["sections"]}

esc = html.escape

# ----------------------------------------------------------------------------------------------
# Card builders. Times are absolute (film seconds); scenes convert them to local time.
# Inner elements carry data-fx (how they enter) and data-in (seconds after the card starts).
# ----------------------------------------------------------------------------------------------

def chars(text, cls="tw"):
    return "".join(f'<span class="{cls}">{esc(c) if c != " " else "&nbsp;"}</span>' for c in text)

def card(cid, start, end, inner, zone="top", extra_cls="", style=""):
    return dict(id=cid, start=start, end=end, zone=zone,
                html=f'<div id="{cid}" class="clip card zone-{zone} {extra_cls}" data-start="{{L}}" data-duration="{round(end-start,3)}" style="{style}">'
                     f'<div class="card-in">{inner}</div></div>')

def kicker(text, at=0.0, color="red"):
    return f'<div class="kicker k-{color}" data-fx="wipe" data-in="{at}"><span class="kdot"></span>{esc(text)}</div>'

def chapter(cid, start, end, num, title, sub=""):
    """Big slate (2.6 s) + a small dock tab that stays for the rest of the chapter."""
    slate = (f'<div class="slate" data-fx="slate" data-in="0">'
             f'<div class="slate-num" data-fx="rise" data-in="0.05">BAB {num:02d} / 07</div>'
             f'<div class="slate-rule" data-fx="draw" data-in="0.15"></div>'
             f'<div class="slate-title" data-fx="rise" data-in="0.25">{title}</div>'
             + (f'<div class="slate-sub" data-fx="rise" data-in="0.45">{esc(sub)}</div>' if sub else "")
             + '</div>')
    out = [card(cid, start, min(start + 2.9, end), slate, zone="top")]
    dock = (f'<div class="dock" data-fx="dock" data-in="0"><span class="dock-num">{num:02d}</span>'
            f'<span class="dock-t">{esc(sub or title)}</span></div>')
    if end - (start + 2.7) > 1:
        out.append(card(cid + "-dock", start + 2.7, end, dock, zone="dock"))
    return out

def note(cid, start, end, kick, head, body="", zone="top", accent="red", head_size=None):
    hs = f' style="font-size:{head_size}px"' if head_size else ""
    inner = (kicker(kick, 0.0, accent) +
             f'<div class="head"{hs} data-fx="rise" data-in="0.12">{head}</div>' +
             (f'<div class="body" data-fx="rise" data-in="0.3">{body}</div>' if body else ""))
    return card(cid, start, end, f'<div class="paper">{inner}</div>', zone)

def stat(cid, start, end, kick, prefix, to, suffix, label, land, fmt="comma", decimals=0, accent="red", source=""):
    """Counter that lands on `land` (absolute)."""
    inner = (kicker(kick, 0.0, accent) +
             f'<div class="stat"><span class="stat-pre">{esc(prefix)}</span>'
             f'<span class="stat-num" data-fx="count" data-in="0.15" data-to="{to}" data-land="{round(land-start,3)}" data-fmt="{fmt}" data-dec="{decimals}">0</span>'
             f'<span class="stat-suf">{esc(suffix)}</span></div>'
             f'<div class="body" data-fx="rise" data-in="0.35">{label}</div>' +
             (f'<div class="src" data-fx="rise" data-in="0.6">{esc(source)}</div>' if source else ""))
    return card(cid, start, end, f'<div class="paper">{inner}</div>')

def steps(cid, start, end, kick, items, accent="red"):
    """items: (absolute_time, title, sub)"""
    rows = "".join(
        f'<div class="step" data-fx="slide" data-in="{round(t-start,3)}"><div class="step-n">{i+1}</div>'
        f'<div class="step-txt"><div class="step-t">{tt}</div>' + (f'<div class="step-s">{esc(ss)}</div>' if ss else "") + '</div></div>'
        for i, (t, tt, ss) in enumerate(items))
    return card(cid, start, end, f'<div class="paper">{kicker(kick, 0, accent)}<div class="steps">{rows}</div></div>')

def chips(cid, start, end, kick, items, accent="red", head=""):
    row = "".join(f'<span class="chip" data-fx="pop" data-in="{round(t-start,3)}">{esc(x)}</span>' for t, x in items)
    hd = f'<div class="head" data-fx="rise" data-in="0.1" style="font-size:54px">{head}</div>' if head else ""
    return card(cid, start, end, f'<div class="paper">{kicker(kick, 0, accent)}{hd}<div class="chips">{row}</div></div>')

def evidence(cid, start, end, img, label, pos="50% 50%", h=340, w=900, rot=-1.6, pan=None, fit="cover", zone="top", tag="BUKTI"):
    pan_attr = f' data-pan="{pan[0]},{pan[1]}"' if pan else ""
    inner = (f'<div class="photo" data-fx="drop" data-in="0" data-rot="{rot}" style="width:{w}px">'
             f'<div class="tape"></div>' +
             (f'<div class="photo-win" style="height:{h}px"><img class="photo-img pan-img" src="assets/img/{img}"{pan_attr} data-fx="pan" data-in="0"/></div>' if pan else f'<div class="photo-win" style="height:{h}px"><img class="photo-img" src="assets/img/{img}" style="object-fit:{fit};object-position:{pos}"/></div>') +
             f'<div class="photo-cap"><span class="cap-tag">{tag}</span>{esc(label)}</div></div>')
    return card(cid, start, end, inner, zone)

def stamp(text, at_rel, color="red", size=96, rot=-9, x=0, y=0):
    return (f'<div class="stamp st-{color}" data-fx="stamp" data-in="{at_rel}" '
            f'data-rot="{rot}" style="font-size:{size}px;margin-left:{x}px;margin-top:{y}px">{esc(text)}</div>')

def lower(cid, start, end, name, role):
    inner = (f'<div class="lt"><div class="lt-bar" data-fx="draw" data-in="0"></div>'
             f'<div class="lt-name" data-fx="rise" data-in="0.12">{esc(name)}</div>'
             f'<div class="lt-role" data-fx="rise" data-in="0.25">{role}</div></div>')
    return card(cid, start, end, inner, zone="bottom")

def tag_bottom(cid, start, end, text, accent="red"):
    return card(cid, start, end, f'<div class="btag bt-{accent}" data-fx="rise" data-in="0">{text}</div>', zone="bottom")

# ----------------------------------------------------------------------------------------------
# Beats. Times are on the edited timeline (see words_out.json).
# ----------------------------------------------------------------------------------------------
B = {}   # scene id -> list of cards
X = []   # SFX cues: (time_of_hit, name, volume)

def sfx(t, name, vol=0.5):
    X.append((t, name, vol))

# ---- Beats for the retake (n1..n4). Times are on the edited timeline (words_out.json). ----------
PIECES = EDL["pieces"]

def o(src, t, sec):
    """Map a source time in `src` to the edited timeline, inside section `sec`."""
    best = None
    for p in PIECES:
        if p["src"] == src and p["sec"] == sec:
            if p["in"] <= t < p["out"]:
                return round(p["at"] + t - p["in"], 3)
            if p["in"] > t and best is None:
                best = p["at"]
    return best

def admock(cid, start, end, head, lines, stamp_at=None, stamp_txt="PALSU", note=""):
    rows = "".join(f'<div class="ad-line" data-fx="type" data-in="{round(t-start,3)}">{chars(x)}</div>' for t, x in lines)
    inner = ('<div class="admock" data-fx="drop" data-in="0">'
             '<div class="ad-top"><div class="ad-logo">B</div><div><div class="ad-name">Pinjaman Peribadi Rasmi</div><div class="ad-spon">Ditaja · Iklan</div></div></div>'
             f'<div class="ad-body"><div class="ad-big" data-fx="rise" data-in="0.2">{head}</div>{rows}</div>'
             + (f'<div class="ad-logo-note" data-fx="rise" data-in="0.8">{note}</div>' if note else "")
             + (stamp(stamp_txt, round(stamp_at - start, 3), "red", 116, -12) if stamp_at else "") + '</div>')
    return card(cid, start, end, inner)

# ---- HOOK 0 -> 15.93 ---------------------------------------------------------------------------
hook = []
hook.append(admock("hk-ad", 0.0, 11.42, "PINJAMAN SEGERA", [
    (1.45, "✓ Tanpa semakan CTOS"), (2.55, "✓ Blacklist pun boleh"), (4.6, "✓ Lulus kurang 24 jam"),
    (6.85, "✓ Tanpa slip gaji"), (9.4, "✓ Jumlah sangat besar")]))
sfx(0.05, "drone-hit", 0.5); sfx(0.12, "whoosh-3", 0.35)
for t, n in [(1.47, "pop-1"), (2.57, "pop-2"), (4.62, "pop-1"), (6.87, "pop-2"), (9.42, "pop-1")]: sfx(t, n, 0.55)
hook.append(card("hk-truth", 11.45, 15.93,
    '<div class="paper paper-dark quote hk-c">' + kicker("JABATAN SIASATAN JENAYAH KOMERSIAL · PDRM", 0, "amber")
    + '<div class="q q-light" data-fx="rise" data-in="0.1" style="font-size:54px">Mana-mana pinjaman yang meminta <span class="hl-amber">bayaran pendahuluan</span> adalah…</div>'
    + stamp("PENIPUAN", round(15.12 - 11.45, 3), "red", 96, -8) + '</div>'))
sfx(11.47, "glitch-1", 0.4); sfx(15.12, "stamp-thud", 0.6); sfx(15.12 - SFXM["riser-slam"]["peak"], "riser-slam", 0.25)
sfx(15.14, "impact-boom", 0.45)
B["s-hook"] = hook

# ---- INTRO 15.93 -> 40.10 ----------------------------------------------------------------------
intro = []
intro.append(card("in-title", 16.0, 20.3,
    '<div class="title-card">'
    '<div class="tc-kick" data-fx="rise" data-in="0.05">TUGASAN VIDEO · MPU 3182</div>'
    '<div class="tc-main" data-fx="slam" data-in="0.1">LOAN SCAM</div>'
    '<div class="tc-rule" data-fx="draw" data-in="0.35"></div>'
    '<div class="tc-sub" data-fx="rise" data-in="0.5">Penipuan pinjaman tidak wujud: krisis etika di era digital</div>'
    '</div>'))
sfx(16.02, "impact-boom", 0.5)
intro.append(lower("in-lt", 20.4, 29.2, "Evelyn Sofidu", "MPU 3182 · Penghayatan Etika dan Peradaban 2"))
sfx(20.42, "paper", 0.5)
intro.append(note("in-isu", 29.5, 40.0, "ISU YANG DIBINCANGKAN",
    'Penipuan <span class="hl">pinjaman tidak wujud</span>',
    '<i>Loan scam</i>: tawaran pinjaman palsu dalam talian yang menyasarkan orang yang terdesak.'))
sfx(29.52, "whoosh-2", 0.4)
B["s-intro"] = intro

# ---- DATA 40.10 -> 79.47 -----------------------------------------------------------------------
data = []
data += chapter("da-ch", 40.15, 79.47, 1, "Data &amp; Fakta", "Data & Fakta")
sfx(40.17, "whoosh-1", 0.45)
data.append(note("da-src", 46.8, 56.9, "SUMBER DATA",
    'Infografik <span class="hl">BERNAMA</span>', 'Diterbitkan pada <b>4 Ogos 2026</b>.'))
sfx(46.82, "click", 0.5)
data.append(stat("da-280", 57.0, 64.4, "SKMM · SEJAK 2022", "≈", 280000, "", "kandungan penipuan &amp; iklan palsu <b>diturunkan</b>", 60.75))
sfx(57.02, "whoosh-3", 0.35); sfx(60.8, "pop-2", 0.6)
data.append(stat("da-3b", 64.5, 72.6, "TAHUN 2025", "RM", 3, " bilion+", "kerugian akibat penipuan dalam talian", 71.55, fmt="plain"))
sfx(64.52, "whoosh-2", 0.35); sfx(71.6, "cash", 0.4)
data.append(evidence("da-aktif", 72.7, 79.4, "poster-tipu-pinjaman.jpg", "Antara penipuan paling aktif · JSJK PDRM", h=330, w=860, rot=-1.2, pan=(-2, -40)))
sfx(72.72, "shutter", 0.45)
B["s-data"] = data

# ---- UMPAN 79.47 -> 108.73 ---------------------------------------------------------------------
um = []
um += chapter("um-ch", 79.55, 162.33, 2, "Umpan &amp; Jerat", "Umpan & jerat")
sfx(79.57, "whoosh-1", 0.45)
claims = [(o("n2", 25.7, "umpan"), "Tanpa semakan CTOS"), (o("n2", 28.2, "umpan"), "Blacklist pun boleh"),
          (o("n2", 31.86, "umpan"), "Lulus < 24 jam"), (o("n2", 35.12, "umpan"), "Tanpa slip gaji"),
          (o("n2", 37.56, "umpan"), "Jumlah sangat besar")]
um.append(chips("um-umpan", 82.3, 96.6, "UMPAN DALAM IKLAN", [(84.9, "Mudah lulus"), (85.5, "Cepat")] + claims,
    head="Iklan pinjaman yang terlalu indah"))
sfx(82.32, "paper", 0.45)
for i, (t, _) in enumerate([(84.9, 0), (85.5, 0)] + claims): sfx(t, "pop-1" if i % 2 else "pop-2", 0.5)
um.append(evidence("um-rtm", 96.7, 108.6, "berita-rtm.jpg", "Contoh: rugi RM167,050 · Berita RTM 24/05/2026", h=330, w=900, rot=-1.4, pan=(-12, -42)))
sfx(96.72, "shutter", 0.45)
um.append(tag_bottom("um-akhir", 102.8, 108.6, 'Perlukan wang → <b class="hl-red">akhirnya hilang wang</b>'))
sfx(107.4, "stamp-clack", 0.45)
B["s-umpan"] = um

# ---- JERAT 108.73 -> 162.33 --------------------------------------------------------------------
je = []
je.append(card("je-dock", 108.73, 162.33, '<div class="dock" data-fx="dock" data-in="0"><span class="dock-num">02</span><span class="dock-t">Umpan & jerat</span></div>', zone="dock"))
je.append(card("je-plat", 111.6, 124.5,
    '<div class="paper">' + kicker("IKLAN BERBAYAR DI MEDIA SOSIAL", 0, "red")
    + '<div class="logos">'
    + '<div class="logo-tile" data-fx="pop" data-in="3.7"><div class="logo-crop" style="background-image:url(assets/img/sosmed-logos.jpg);background-position:-30px -107px"></div><span>Facebook</span></div>'
    + '<div class="logo-tile" data-fx="pop" data-in="4.5"><div class="logo-crop" style="background-image:url(assets/img/sosmed-logos.jpg);background-position:-200px -107px"></div><span>Instagram</span></div>'
    + '<div class="logo-tile" data-fx="pop" data-in="5.9"><div class="logo-crop" style="background-image:url(assets/img/sosmed-logos.jpg);background-position:-366px -107px"></div><span>TikTok</span></div>'
    + '</div><div class="body" data-fx="rise" data-in="6.6">Aplikasi yang kita guna <b>setiap hari</b>.</div></div>'))
sfx(111.62, "whoosh-2", 0.35); sfx(115.3, "pop-1", 0.55); sfx(116.1, "pop-2", 0.55); sfx(117.5, "pop-1", 0.55)
je.append(card("je-sah", 124.6, 137.5,
    '<div class="paper">' + kicker("IKLAN PALSU MENYAMAR SEBAGAI SAH", 0, "red")
    + '<div class="head" data-fx="rise" data-in="0.1" style="font-size:56px">Guna <span class="hl">logo bank</span> &amp; nama syarikat yang nampak sah</div>'
    + '<div class="chips"><span class="chip" data-fx="pop" data-in="5.5">Logo bank</span>'
      '<span class="chip" data-fx="pop" data-in="8.0">Nama syarikat “sah”</span>'
      '<span class="chip" data-fx="pop" data-in="11.9">“Di bawah KPKT”</span></div>'
    + stamp("PALSU", 12.4, "red", 96, -10) + '</div>'))
sfx(124.62, "whoosh-3", 0.35); sfx(130.1, "pop-1", 0.5); sfx(132.6, "pop-2", 0.5); sfx(136.5, "pop-1", 0.5); sfx(137.0, "stamp-thud", 0.55)
je.append(card("je-chat", 137.6, 146.3,
    '<div class="paper">' + kicker("KLIK PAUTAN → TERUS KE WHATSAPP", 0, "red")
    + '<div class="chat">'
    '<div class="bub bub-in" data-fx="pop" data-in="2.6">Salam. Saya <b>pegawai pinjaman</b>. Boleh saya bantu? 😊</div>'
    '<div class="bub bub-out" data-fx="pop" data-in="4.6">Saya nak mohon pinjaman RM5,000</div>'
    '</div>' + stamp("PEGAWAI PALSU", 7.6, "red", 70, -6) + '</div>'))
sfx(137.62, "click", 0.5); sfx(140.15, "ping-1", 0.5); sfx(142.15, "ping-2", 0.4); sfx(145.2, "stamp-clack", 0.55)
je.append(card("je-apk", 146.4, 162.2,
    '<div class="perm" data-fx="drop" data-in="0">'
    '<div class="perm-k">⚠ PAUTAN / APLIKASI YANG DIMUAT TURUN</div>'
    '<div class="perm-t">Benarkan <b>“PinjamanCepat”</b> mengakses:</div>'
    '<div class="perm-row" data-fx="slide" data-in="9.3"><span class="perm-ic">▣</span>Data telefon</div>'
    '<div class="perm-row" data-fx="slide" data-in="11.6"><span class="perm-ic">◉</span>Gambar &amp; galeri</div>'
    '<div class="perm-row" data-fx="slide" data-in="13.3"><span class="perm-ic">☎</span>Senarai kenalan</div>'
    '<div class="perm-btns"><span class="perm-no">TOLAK</span><span class="perm-yes">BENARKAN</span></div>'
    '</div>'))
sfx(146.45, "ping-2", 0.45); sfx(155.7, "click", 0.45); sfx(158.0, "click", 0.45); sfx(159.7, "click", 0.45); sfx(161.0, "glitch-2", 0.35)
B["s-jerat"] = je

# ---- MODUS 162.33 -> 280.13 --------------------------------------------------------------------
mo = []
mo += chapter("mo-ch", 162.4, 280.13, 3, "Modus<br>operandi", "Modus operandi")
sfx(162.42, "whoosh-1", 0.45)
mo.append(steps("mo-steps", 164.3, 191.1, "CORAK PENIPUAN · HAMPIR SAMA SETIAP KES", [
    (167.9, "Hantar salinan IC &amp; maklumat diri", ""),
    (176.0, "Pinjaman “lulus” dengan sangat cepat", "kadang-kadang dengan surat kelulusan palsu"),
]))
sfx(164.32, "paper", 0.45); sfx(167.95, "pop-2", 0.55); sfx(176.05, "pop-2", 0.55)
mo.append(chips("mo-fees", 191.2, 212.45, "03 · DI SINILAH PENIPUAN BERLAKU", [
    (204.8, "Yuran guaman"), (206.6, "Yuran perjanjian"), (208.0, "Yuran CTOS"), (209.2, "Insurans"), (210.6, "Yuran pengaktifan akaun")],
    head="Minta <span class=\"hl\">bayaran pendahuluan</span>"))
sfx(191.22, "whoosh-3", 0.35); sfx(199.4, "cash", 0.3)
for i, t in enumerate([204.8, 206.6, 208.0, 209.2, 210.6]): sfx(t, "pop-1" if i % 2 else "pop-2", 0.5)
mo.append(card("mo-amt", 212.55, 228.4,
    '<div class="paper">' + kicker("MENURUT DATA POLIS", 0, "red")
    + f'<div class="range"><div class="range-a" data-fx="rise" data-in="{round(217.1-212.55,2)}">RM150–RM200</div>'
      f'<div class="range-arrow" data-fx="draw" data-in="{round(220.6-212.55,2)}"></div>'
      f'<div class="range-b" data-fx="slam" data-in="{round(223.0-212.55,2)}">RIBUAN RINGGIT</div></div>'
      f'<div class="body" data-fx="rise" data-in="{round(224.1-212.55,2)}">melalui pelbagai lagi yuran tambahan</div></div>'))
sfx(212.57, "whoosh-2", 0.35); sfx(223.05, "impact-boom", 0.4)
mo.append(note("mo-batal", 228.5, 234.85, "MAHU TARIK DIRI?",
    'Kena bayar <span class="hl">“yuran pembatalan”</span> pula'))
sfx(228.52, "paper", 0.4)
mo.append(card("mo-psiko", 234.95, 257.7,
    '<div class="paper">' + kicker("PERANGKAP PSIKOLOGI", 0, "red")
    + '<div class="vs">'
    + f'<div class="vs-row" data-fx="slide" data-in="{round(239.8-234.95,2)}"><span class="vs-k">SUDAH BAYAR</span><span class="vs-v">rugi jika tarik diri</span></div>'
    + f'<div class="vs-row vs-bad" data-fx="slide" data-in="{round(249.6-234.95,2)}"><span class="vs-k">AKIBATNYA</span><span class="vs-v">sanggup transfer beribu-ribu ringgit</span></div>'
    + '</div></div>'))
sfx(234.97, "whoosh-3", 0.35); sfx(239.82, "pop-2", 0.5); sfx(249.62, "pop-2", 0.5); sfx(255.2, "cash", 0.35)
mo.append(evidence("mo-keldai", 257.85, 268.35, "keldai-ilustrasi.jpg", "Wang masuk akaun keldai · sukar dijejak", pos="50% 45%", h=330, rot=1.4))
sfx(257.87, "shutter", 0.45)
mo.append(card("mo-quote", 268.45, 280.05,
    '<div class="paper quote">' + kicker("PENEGASAN JSJK · PDRM", 0, "red")
    + '<div class="q" data-fx="rise" data-in="0.15" style="font-size:54px">Mana-mana pinjaman yang meminta <span class="hl">bayaran pendahuluan</span> adalah</div>'
    + stamp("PENIPUAN", round(279.55 - 268.45, 3), "red", 100, -7) + '</div>'))
sfx(268.47, "paper", 0.45); sfx(279.6, "stamp-thud", 0.6)
B["s-modus"] = mo

# ---- KESAN 280.13 -> 328.53 --------------------------------------------------------------------
ke = []
ke += chapter("ke-ch", 280.25, 328.53, 4, "Kesan kepada<br>mangsa", "Kesan kepada mangsa")
sfx(280.27, "whoosh-1", 0.45)
ke.append(card("ke-rows", 283.1, 303.0,
    '<div class="paper">' + kicker("KESANNYA SANGAT BERAT", 0, "red")
    + '<div class="impact-rows">'
    + f'<div class="ir" data-fx="slide" data-in="{round(287.2-283.1,2)}"><span class="ir-k">KEWANGAN</span><span class="ir-v">hutang asal → <b>hutang lebih besar</b></span></div>'
    + f'<div class="ir" data-fx="slide" data-in="{round(296.6-283.1,2)}"><span class="ir-k">EMOSI</span><span class="ir-v">malu · tertekan · <b>salahkan diri</b></span></div>'
    + '</div></div>'))
sfx(283.12, "paper", 0.45); sfx(287.22, "pop-2", 0.5); sfx(296.62, "pop-2", 0.5)
ke.append(card("ke-keluarga", 303.1, 319.0,
    '<div class="paper paper-dark">' + kicker("KELUARGA MANGSA TURUT TERJEJAS", 0, "amber")
    + '<div class="threat">'
    + f'<div class="th-row" data-fx="slide" data-in="{round(306.1-303.1,2)}"><span class="th-ic">!</span><span>Gambar &amp; nombor telefon <b>disebarkan</b></span></div>'
    + f'<div class="th-row th-hot" data-fx="slide" data-in="{round(311.2-303.1,2)}"><span class="th-ic">!</span><span>Diugut &amp; <b>dimalukan dengan berita palsu</b></span></div>'
    + '</div></div>'))
sfx(303.12, "glitch-2", 0.35); sfx(306.12, "pop-1", 0.5); sfx(311.22, "glitch-1", 0.4)
ke.append(card("ke-percaya", 319.1, 328.45,
    '<div class="paper">' + kicker("KESAN PALING DALAM", 0, "red")
    + '<div class="head" data-fx="rise" data-in="1.6">Hilangnya <span class="hl">kepercayaan</span></div>'
    + f'<div class="body" data-fx="rise" data-in="{round(322.6-319.1,2)}">Mangsa mula curiga semua orang, termasuk institusi kewangan yang sah.</div></div>'))
sfx(320.7, "impact-boom", 0.4)
B["s-kesan"] = ke

# ---- ETIKA 328.53 -> 404.23 --------------------------------------------------------------------
et = []
et += chapter("et-ch", 328.6, 404.23, 5, "Etika &amp;<br>Peradaban", "Etika & peradaban")
sfx(328.62, "whoosh-1", 0.45)
et.append(note("et-runtuh", 333.85, 339.95, "PADA PANDANGAN SAYA",
    '<i>Loan scam</i> membuktikan <span class="hl">keruntuhan etika</span>'))
sfx(333.87, "paper", 0.4); sfx(338.5, "stamp-clack", 0.4)
et.append(steps("et-nilai", 340.0, 358.7, "NILAI YANG HILANG", [
    (340.7, "Empati", "sanggup ambil wang orang yang sedang susah"),
    (345.6, "Rasa hormat", "mangsa dilihat dari sudut wang"),
    (350.8, "Susila &amp; kesopanan", "mangsa diugut & dimalukan depan keluarga"),
]))
sfx(340.02, "whoosh-2", 0.35); sfx(340.72, "pop-2", 0.55); sfx(345.62, "pop-2", 0.55); sfx(350.82, "pop-2", 0.55)
et.append(note("et-majmuk", 358.8, 370.4, "MASYARAKAT MAJMUK MALAYSIA",
    'Perpaduan dibina atas <span class="hl">saling percaya</span>',
    'Kesannya lebih besar daripada kehilangan wang.'))
sfx(358.82, "paper", 0.4)
et.append(card("et-curiga", 370.5, 384.8,
    '<div class="paper">' + kicker("BAGAIMANA KEPERCAYAAN RUNTUH", 0, "red")
    + '<div class="steps">'
    + f'<div class="step" data-fx="slide" data-in="{round(371.5-370.5,2)}"><div class="step-n">›</div><div class="step-txt"><div class="step-t">Menyamar sebagai pegawai bank</div></div></div>'
    + f'<div class="step" data-fx="slide" data-in="{round(374.0-370.5,2)}"><div class="step-n">›</div><div class="step-txt"><div class="step-t">Guna bahasa &amp; logat mangsa</div></div></div>'
    + f'<div class="step" data-fx="slide" data-in="{round(377.2-370.5,2)}"><div class="step-n">›</div><div class="step-txt"><div class="step-t">Guna akaun keldai rakyat pelbagai kaum</div></div></div>'
    + f'</div><div class="verdict" data-fx="slam" data-in="{round(381.9-370.5,2)}">Rakyat mula curiga sesama sendiri</div></div>'))
sfx(370.52, "paper", 0.4); sfx(371.5, "click", 0.45); sfx(374.0, "click", 0.45); sfx(377.2, "click", 0.45); sfx(381.95, "impact-boom", 0.35)
et.append(note("et-modul", 384.9, 393.1, "MODUL KURSUS",
    'Piawai kelakuan <span class="hl">dalam talian</span> = kehidupan sebenar'))
sfx(384.92, "whoosh-3", 0.35)
et.append(card("et-rukun", 393.2, 404.15,
    '<div class="paper paper-dark quote">' + kicker("RUKUN NEGARA", 0, "amber")
    + '<div class="q q-light" data-fx="rise" data-in="2.9">Kesopanan dan Kesusilaan</div>'
    + f'<div class="body body-light" data-fx="rise" data-in="{round(399.6-393.2,2)}">…hanya tinggal <span class="hl-amber">slogan</span>, dan keharmonian masyarakat majmuk tergugat.</div></div>'))
sfx(393.22, "whoosh-2", 0.35); sfx(403.6, "drone-hit", 0.3)
B["s-etika"] = et

# ---- UNDANG 404.23 -> 462.07 -------------------------------------------------------------------
un = []
un += chapter("un-ch", 404.3, 462.07, 6, "Penyelesaian", "Undang-undang")
sfx(404.32, "whoosh-1", 0.45); sfx(404.4, "ping-2", 0.35)
un.append(note("un-1", 407.3, 411.4, "CADANGAN 01", 'Penguatkuasaan <span class="hl">undang-undang</span>'))
sfx(407.32, "pop-1", 0.5)
un.append(card("un-s233", 411.5, 422.3,
    '<div class="paper">' + kicker("SKMM MENGGUNAKAN", 0, "red")
    + f'<div class="law" data-fx="type" data-in="{round(413.2-411.5,2)}">{chars("Seksyen 233")}</div>'
    + f'<div class="body" data-fx="rise" data-in="{round(414.6-411.5,2)}">Akta Komunikasi dan Multimedia 1998</div>'
    + f'<div class="body" data-fx="rise" data-in="{round(418.9-411.5,2)}">untuk <b>menurunkan</b> kandungan &amp; iklan palsu</div></div>'))
sfx(411.52, "paper", 0.4); sfx(413.25, "typing-2", 0.4)
un.append(card("un-96", 422.4, 430.7,
    '<div class="paper">' + kicker("DARI SEGI ANGKA", 0, "red")
    + f'<div class="ring-row"><div class="ring" data-fx="ring" data-in="{round(424.9-422.4,2)}" data-to="96"><svg viewBox="0 0 120 120"><circle class="ring-bg" cx="60" cy="60" r="50"/><circle class="ring-fg" cx="60" cy="60" r="50"/></svg>'
    + f'<div class="ring-num"><span class="stat-num" data-fx="count" data-in="{round(424.9-422.4,2)}" data-to="96" data-land="{round(425.6-422.4,2)}" data-fmt="plain" data-dec="0">0</span>%</div></div>'
    + f'<div class="ring-txt" data-fx="rise" data-in="{round(426.3-422.4,2)}">permohonan penurunan kandungan penipuan <b>berjaya</b></div></div></div>'))
sfx(422.42, "whoosh-2", 0.35); sfx(425.65, "ping-1", 0.45)
un.append(note("un-osa", 430.8, 438.7, "BERMULA 1 JANUARI 2026",
    '<span class="hl">Akta Keselamatan Dalam Talian</span>',
    'mewajibkan platform mengambil langkah keselamatan.'))
sfx(430.82, "paper", 0.4); sfx(433.65, "pop-2", 0.5)
un.append(steps("un-lemah", 438.8, 458.2, "NAMUN · MASIH ADA KELEMAHAN", [
    (445.5, "Bersifat reaktif", "diturunkan selepas tersiar, mungkin sudah ada mangsa"),
    (453.7, "Mudah buka iklan &amp; profil baru", "sebaik sahaja yang lama diturunkan"),
]))
sfx(438.82, "whoosh-3", 0.35); sfx(445.5, "pop-2", 0.55); sfx(453.7, "pop-2", 0.55)
un.append(card("un-verdict", 458.3, 462.0,
    '<div class="paper quote">' + kicker("BAGI SAYA", 0, "red")
    + '<div class="q" data-fx="rise" data-in="0.2">Undang-undang sahaja…</div>'
    + stamp("TIDAK CUKUP", round(461.3 - 458.3, 3), "red", 84, -6) + '</div>'))
sfx(461.35, "stamp-thud", 0.6)
B["s-undang"] = un

# ---- LITERASI 462.07 -> 519.03 -----------------------------------------------------------------
li = []
li.append(note("li-1", 462.2, 466.4, "CADANGAN 02", 'Literasi <span class="hl">digital</span>'))
sfx(462.22, "whoosh-1", 0.45)
li.append(card("li-dock", 462.2, 519.03, '<div class="dock" data-fx="dock" data-in="0"><span class="dock-num">06</span><span class="dock-t">Literasi digital</span></div>', zone="dock"))
li.append(steps("li-3", 466.5, 485.2, "INGAT 3 PERKARA INI", [
    (472.1, "Pinjaman sah TIDAK minta yuran pendahuluan", ""),
    (477.5, "Semak no. telefon &amp; akaun bank", "portal Semak Mule PDRM · semakmule.rmp.gov.my"),
]))
sfx(466.52, "paper", 0.4); sfx(472.12, "pop-2", 0.55); sfx(477.52, "pop-2", 0.55)
li.append(stat("li-997", 485.3, 497.5, "3 · SUDAH TERTIPU? HUBUNGI SEGERA", "☎", 997, "", "Pusat Respons Scam Kebangsaan (NSRC), supaya wang boleh <b>disekat</b>", 489.2, fmt="plain"))
sfx(485.32, "whoosh-2", 0.35); sfx(489.25, "ping-1", 0.55)
li.append(evidence("li-share", 497.6, 505.8, "3-cara-elak.jpg", "Kongsi dengan ibu bapa & warga emas", pos="50% 16%", h=330, w=860, rot=1.3, tag="KONGSI"))
sfx(497.62, "shutter", 0.35)
li.append(note("li-muda", 505.9, 518.9, "SEBAGAI ORANG MUDA",
    '<span class="hl">Cakna</span> &amp; saling mengingatkan',
    'tentang siapa-siapa yang ada di rumah kita.'))
sfx(505.92, "paper", 0.4)
B["s-literasi"] = li

# ---- INTEGRITI 519.03 -> 569.63 ----------------------------------------------------------------
ig = []
ig.append(note("ig-1", 519.1, 527.4, "CADANGAN 03 · PALING PENTING", 'Integriti <span class="hl">diri</span>'))
sfx(519.12, "whoosh-1", 0.45)
ig.append(card("ig-dock", 519.1, 569.63, '<div class="dock" data-fx="dock" data-in="0"><span class="dock-num">06</span><span class="dock-t">Integriti diri</span></div>', zone="dock"))
links = "".join(f'<div class="link l{i}" data-fx="pop" data-in="{round(0.4+i*0.25,2)}">{t}</div>' for i, t in enumerate(["SINDIKET", "AKAUN KELDAI", "MANGSA"]))
ig.append(card("ig-chain", 527.5, 545.4,
    '<div class="paper">' + kicker("SINDIKET TAK BOLEH BERGERAK TANPA AKAUN KELDAI", 0, "red")
    + f'<div class="chain" data-fx="none" data-in="0">{links}<div class="chain-cut" data-fx="cut" data-in="{round(540.9-527.5,2)}"></div></div>'
    + f'<div class="body" data-fx="rise" data-in="{round(532.4-527.5,2)}">Jika rakyat <b>menolak</b> tawaran sewa / jual akaun bank…</div>'
    + f'<div class="verdict" data-fx="slam" data-in="{round(541.0-527.5,2)}">rantaian ini pasti terputus</div></div>'))
sfx(527.52, "paper", 0.4); sfx(540.9, "glitch-1", 0.45); sfx(540.95, "impact-boom", 0.5)
ig.append(evidence("ig-hukum", 545.5, 553.4, "keldai-didakwa.png", "Pemilik akaun keldai boleh didakwa", pos="50% 40%", h=330, w=860, rot=-1.2))
sfx(545.52, "shutter", 0.4)
ig.append(tag_bottom("ig-10", 548.4, 553.4, 'Kanun Keseksaan: sehingga <b class="hl-red">10 tahun penjara</b>'))
sfx(552.25, "stamp-clack", 0.5)
ig.append(note("ig-sedar", 553.5, 562.5, "TOLAK BUKAN KERANA TAKUT DIHUKUM",
    'Tolak kerana sedar ia <span class="hl">menyakiti orang lain</span>'))
sfx(553.52, "whoosh-2", 0.35); sfx(560.75, "ping-2", 0.4)
ig.append(note("ig-diri", 562.6, 569.5, "FIKIRKAN",
    'Bagaimana jika ia menimpa <span class="hl">diri kita sendiri</span>?'))
sfx(562.62, "paper", 0.4)
B["s-integriti"] = ig

# ---- PENUTUP 569.63 -> 604.13 ------------------------------------------------------------------
pe = []
pe += chapter("pe-ch", 569.7, 604.13, 7, "Penutup", "Penutup")
sfx(569.72, "whoosh-1", 0.45)
pe.append(card("pe-krisis", 572.9, 582.4,
    '<div class="paper">' + kicker("LOAN SCAM BUKAN SEKADAR JENAYAH KEWANGAN", 0, "red")
    + f'<div class="head" data-fx="rise" data-in="{round(576.3-572.9,2)}">Ia adalah <span class="hl">krisis etika</span></div>'
    + f'<div class="body" data-fx="rise" data-in="{round(579.0-572.9,2)}">yang menghakis kepercayaan dalam masyarakat kita.</div></div>'))
sfx(572.92, "paper", 0.4); sfx(577.9, "stamp-clack", 0.4)
plates = "".join(f'<div class="plate p{i}" data-fx="plate" data-in="{round(a-582.5,2)}"><span class="plate-n">{i+1}</span>{t}</div>'
                 for i, (a, t) in enumerate([(588.0, "Undang-undang yang tegas"), (590.2, "Rakyat yang celik digital"), (592.6, "Individu yang berintegriti")]))
pe.append(card("pe-3", 582.5, 594.8,
    '<div class="paper">' + kicker("3 LAPISAN YANG BERGERAK BERSAMA", 0, "red") + f'<div class="plates">{plates}</div></div>'))
sfx(582.52, "whoosh-3", 0.35); sfx(588.0, "pop-2", 0.55); sfx(590.2, "pop-2", 0.55); sfx(592.6, "pop-2", 0.55)
pe.append(card("pe-msia", 594.9, 603.9,
    '<div class="paper paper-dark">' + kicker("HANYA DENGAN CARA INI", 0, "amber")
    + f'<div class="head head-light" data-fx="rise" data-in="{round(597.2-594.9,2)}">Malaysia kekal <span class="hl-amber">lestari</span><br>&amp; <span class="hl-amber">bertamadun</span>.</div></div>'))
sfx(594.92, "whoosh-2", 0.35); sfx(601.45, "impact-boom", 0.4)
B["s-penutup"] = pe

# ---- END CARD ------------------------------------------------------------------------------------
END_START = round(TALK_DUR - 0.15, 3)
endc = [card("ed-card", END_START, TOTAL,
    '<div class="endcard" data-fx="fade" data-in="0">'
    '<div class="ec-k" data-fx="rise" data-in="0.3">SEKIAN, TERIMA KASIH</div>'
    '<div class="ec-t" data-fx="slam" data-in="0.45">LOAN SCAM</div>'
    '<div class="ec-rule" data-fx="draw" data-in="0.7"></div>'
    '<div class="ec-n" data-fx="rise" data-in="0.9">Evelyn Sofidu</div>'
    '<div class="ec-c" data-fx="rise" data-in="1.05">MPU 3182 · Penghayatan Etika dan Peradaban 2<br>Pensyarah: Puan Rusniyati</div>'
    '<div class="ec-src" data-fx="rise" data-in="1.4">RUJUKAN: Infografik BERNAMA (4 Ogos 2026) · Berita RTM · JSJK PDRM · SKMM · NSRC 997 · Akta Keselamatan Dalam Talian 2025</div>'
    '</div>', zone="full")]
sfx(END_START + 0.47, "stamp-thud", 0.45)
B["s-end"] = endc

SCENES = [
    ("s-hook", 0.0, SEC["hook2"]["end"]),
    ("s-intro", SEC["intro"]["start"], SEC["intro"]["end"]),
    ("s-data", SEC["data1"]["start"], SEC["data2"]["end"]),
    ("s-umpan", SEC["umpan"]["start"], SEC["umpan"]["end"]),
    ("s-jerat", SEC["jerat"]["start"], SEC["jerat"]["end"]),
    ("s-modus", SEC["modus"]["start"], SEC["keldai"]["end"]),
    ("s-kesan", SEC["kesan"]["start"], SEC["kesan"]["end"]),
    ("s-etika", SEC["etika"]["start"], SEC["etika"]["end"]),
    ("s-undang", SEC["undang"]["start"], SEC["undang"]["end"]),
    ("s-literasi", SEC["literasi"]["start"], SEC["literasi"]["end"]),
    ("s-integriti", SEC["integriti"]["start"], SEC["integriti"]["end"]),
    ("s-penutup", SEC["penutup"]["start"], END_START),
    ("s-end", END_START, TOTAL),
]

PUNCH = [(0.0, 1.06), (11.45, 1.0), (16.0, 1.07), (20.4, 1.0), (40.15, 1.06), (57.0, 1.0), (72.7, 1.06), (79.55, 1.0),
         (96.7, 1.07), (108.73, 1.0), (124.6, 1.06), (137.6, 1.0), (146.4, 1.07), (162.4, 1.0), (191.2, 1.06), (212.55, 1.0),
         (234.95, 1.07), (257.85, 1.0), (268.45, 1.07), (280.25, 1.0), (303.1, 1.07), (319.1, 1.0), (328.6, 1.06),
         (358.8, 1.0), (370.5, 1.06), (384.9, 1.0), (393.2, 1.07), (404.3, 1.0), (430.8, 1.06), (438.8, 1.0),
         (458.3, 1.08), (462.2, 1.0), (485.3, 1.06), (497.6, 1.0), (519.1, 1.07), (527.5, 1.0), (545.5, 1.07),
         (553.5, 1.0), (569.7, 1.06), (582.5, 1.0), (594.9, 1.07)]

# ----------------------------------------------------------------------------------------------
CSS = open(f"{S}/work/scene.css").read()
ENGINE = open(f"{S}/work/engine.js").read()

os.makedirs(f"{P}/compositions", exist_ok=True)
hosts = []
hud = f"""<template>
<style>
#s-hud {{ position:absolute; inset:0; pointer-events:none; }}
#s-hud .hud-bar {{ position:absolute; left:0; top:0; height:8px; width:{W}px; background:#E5383B; transform-origin:0 50%; }}
#s-hud .hud-tag {{ position:absolute; right:40px; top:48px; font:600 26px/1 'IBM Plex Mono', monospace; letter-spacing:.12em; color:#EFE8DA;
  background:rgba(13,23,38,.72); padding:10px 14px; border:1px solid rgba(239,232,218,.35); }}
#s-hud .hud-tag b {{ color:#E5383B; }}
</style>
<div id="s-hud" data-composition-id="s-hud" data-width="{W}" data-height="{H}" data-duration="{round(END_START,3)}">
  <div id="hud-bar" class="clip hud-bar" data-start="0" data-duration="{round(END_START,3)}"></div>
  <div id="hud-tag" class="clip hud-tag" data-start="11.2" data-duration="{round(END_START-11.2,3)}"><b>●</b> FAIL KES · LOAN SCAM</div>
</div>
<script>
(function(){{
const tl = gsap.timeline({{ paused: true }});
tl.fromTo("#hud-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {round(END_START,3)}, ease: "none" }}, 0);
tl.fromTo("#hud-tag", {{ opacity: 0, y: -10 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, 11.2);
window.__timelines = window.__timelines || {{}};
window.__timelines["s-hud"] = tl;
}})();
</script>
</template>
"""
os.makedirs(f"{P}/compositions", exist_ok=True)
open(f"{P}/compositions/s-hud.html", "w").write(hud)
hosts.append(f'<div id="s-hud" class="clip" data-composition-id="s-hud" data-composition-src="compositions/s-hud.html" data-start="0" '
             f'data-duration="{round(END_START,3)}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:8"></div>')
for sid, s0, s1 in SCENES:
    cards = B[sid]
    body = []
    for c in cards:
        st = max(c["start"], s0); en = min(c["end"], s1)
        if en - st < 0.2:
            continue
        local = round(st - s0, 3)
        h = c["html"].replace('data-start="{L}"', f'data-start="{local}"')
        h = h.replace(f'data-duration="{round(c["end"]-c["start"],3)}"', f'data-duration="{round(en-st,3)}"', 1)
        body.append(h)
    dur = round(s1 - s0, 3)
    doc = f"""<template>
<style>
#{sid} {{ position:absolute; inset:0; }}
{CSS.replace('#ROOT', '#' + sid)}
</style>
<div id="{sid}" data-composition-id="{sid}" data-width="{W}" data-height="{H}" data-duration="{dur}" data-layout-allow-overlap>
{chr(10).join(body)}
</div>
<script>
(function(){{
{ENGINE.replace('__SID__', sid)}
}})();
</script>
</template>
"""
    open(f"{P}/compositions/{sid}.html", "w").write(doc)
    hosts.append(f'<div id="{sid}" class="clip" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
                 f'data-start="{round(s0,3)}" data-duration="{dur}" data-track-index="2" data-track-kind="graphics" '
                 f'data-width="{W}" data-height="{H}" style="z-index:5"></div>')

# ---- SFX audio elements ------------------------------------------------------------------------
aud = []
X.sort()
lanes = []  # end time per SFX lane, so no lane holds two overlapping sounds
for i, (t, name, vol) in enumerate(X):
    if vol <= 0: continue
    if name not in SFXM: raise SystemExit("unknown sfx " + name)
    m = SFXM[name]
    start = max(0.0, round(t - m["peak"] + 1/30, 3))  # land the peak one frame after the picture
    lane = next((k for k, end in enumerate(lanes) if end <= start), None)
    if lane is None:
        lanes.append(0); lane = len(lanes) - 1
    lanes[lane] = start + m["dur"] + 0.01
    aud.append(f'<audio id="fx{i:03d}" class="clip" src="assets/sfx/{name}.mp3" data-start="{start}" data-duration="{m["dur"]}" '
               f'data-volume="{vol}" data-track-index="{10 + lane}" data-audio-group="sfx"></audio>')

# ---- music bed with ducking lane -----------------------------------------------------------------
# bed is built by ffmpeg (bgm/bed.wav) at about -20 LUFS; voice sits ~-16 LUFS.
UNDER = 0.25   # under the voice: bed sits ~12 dB below speech
pts = [{"t": 0, "v": 0.45}, {"t": 0.6, "v": UNDER}]
pts += [{"t": round(TALK_DUR - 1.2, 2), "v": UNDER}, {"t": round(TALK_DUR + 0.2, 2), "v": 0.95}, {"t": TOTAL, "v": 0.95}]
auto = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": pts}]}).replace('"', "&quot;")
fx = json.dumps({"version": 1, "nodes": [{"type": "highpass", "id": "b1", "label": "Clear low end for the voice", "params": {"frequency": 110}},
                                          {"type": "peaking", "id": "b2", "label": "Make room for speech", "params": {"frequency": 2500, "gain": -4, "q": 0.8}}]}).replace('"', "&quot;")
voice_fx = json.dumps({"version": 1, "nodes": [{"type": "peaking", "id": "v1", "label": "Clarity", "params": {"frequency": 3200, "gain": 2, "q": 1}},
                                               {"type": "limiter", "id": "v2", "label": "Catch peaks", "params": {"limit": -1}}]}).replace('"', "&quot;")

index = f"""<!doctype html>
<html lang="ms">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<script src="assets/vendor/gsap.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:#0D1726; }}
#main {{ position:relative; width:{W}px; height:{H}px; overflow:hidden; background:#0D1726; }}
#talk-wrap {{ position:absolute; inset:0; transform-origin:50% 40%; }}
#talk {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
#grade {{ position:absolute; inset:0; pointer-events:none; z-index:2;
  background: linear-gradient(180deg, rgba(13,23,38,.45) 0%, rgba(13,23,38,0) 18%, rgba(13,23,38,0) 60%, rgba(13,23,38,.62) 100%); }}
#hud {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; z-index:8; pointer-events:none; }}
#hud-bar {{ position:absolute; left:0; top:0; height:8px; width:{W}px; background:#E5383B; transform-origin:0 50%; }}
#hud-tag {{ position:absolute; right:40px; top:48px; font:600 26px/1 'IBM Plex Mono', monospace; letter-spacing:.12em; color:#EFE8DA;
  background:rgba(13,23,38,.72); padding:10px 14px; border:1px solid rgba(239,232,218,.35); }}
#hud-tag b {{ color:#E5383B; }}
</style>
</head>
<body>
<div id="main" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}" data-fps="30">
  <div id="talk-wrap">
    <video id="talk" class="clip" src="assets/talk.mp4" data-start="0" data-duration="{TALK_DUR}" data-track-index="0"
      data-has-audio="true" data-volume="1" data-audio-group="voice" data-fx-chain="{voice_fx}"></video>
  </div>
  <div id="grade"></div>
  {chr(10).join('  ' + h for h in hosts)}
  <audio id="bed" class="clip" src="assets/bgm/bed.wav" data-start="0" data-duration="{TOTAL}" data-track-index="9"
    data-volume="1" data-audio-group="music" data-automation="{auto}" data-fx-chain="{fx}"></audio>
  {chr(10).join('  ' + a for a in aud)}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
"""
prev = None
for t, sc in PUNCH:
    if prev is None:
        index += f'tl.set("#talk-wrap", {{ scale: {sc} }}, 0);\n'
    else:
        # hard punch on the cut (a jump-cut feel), not a slow zoom
        index += f'tl.set("#talk-wrap", {{ scale: {sc} }}, {t});\n'
    prev = sc
index += f"""tl.to("#talk-wrap", {{ scale: 1.03, duration: 2.2, ease: "power2.inOut" }}, {round(TALK_DUR - 2.4, 2)});
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
open(f"{P}/index.html", "w").write(index)
json.dump({"total": TOTAL, "talk": TALK_DUR, "sfx": len(aud), "scenes": [s[0] for s in SCENES]}, open(f"{S}/work/build_info.json", "w"))
print("total", TOTAL, "sfx", len(aud), "cards", sum(len(v) for v in B.values()))
