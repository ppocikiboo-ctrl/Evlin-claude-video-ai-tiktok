# Double cleansing routine — TikTok video ("skincare diary")

This is a routine explainer built from a UGC take of the creator removing makeup
with O'CHEAL Micellar Water. It uses the same pipeline as
[the O'CHEAL edits](../ocheal-micellar-water/README.md): run `build_base.py`,
then `render.py`. Helpers are loaded from `../ocheal-micellar-water/render.py`.

Output: `output/double_cleansing_routine.mp4`. It is 25.9 s, 1080×1920, 30 fps, about −15 LUFS.

## Style

- **Calm "skincare diary" look:** cream cards, a mocha accent, Playfair italic, Great Vibes script, and Montserrat.
- **Hook:** *Cuci muka je?* is struck through, then **TAK CUKUP!** slams in, then the script line *ni rutin double cleansing aku 🌙* writes on.
- **Tracker:** a two-step bar stays at the top the whole time (1 Buang makeup → 2 Cuci muka). Its progress line fills through step 1, and step 1 is ticked off when step 2 starts.
- **Step titles:** big outline numerals **01** and **02** open each step.
- **Tip cards:** cream cards slide up, timed to the real action: *Basahkan kapas dulu*, *Lap lembut-lembut, jangan gosok*, *Tekap dulu ±3 saat, baru lap* (on the pads held on the eyes), *Sekeliling mulut & dagu sekali*, *Leher pun kena cuci!*, and *Ulang guna kapas baru*.
- **Cuts and music:** cuts are soft freeze-dissolves (7 frames), over a calm 90 BPM lo-fi bed (Cmaj7–Am7–Dm7–G7).

## Important: step 2 is a graphic, not footage

The source clip shows only step 1 (micellar water). Step 2 (cuci muka) appears
as a text card with rising foam bubbles over the clean-face close-up. It does not
pretend a face wash was filmed. If a clip of the face wash is added later, put it
in `edl.py` between `repeat` and `clean`, and move `FoamCard` onto it.

## Edit (source `src/original.mp4`, 84.8 s, VFR 1280×2276)

| Out | Source | Footage | On screen |
|---|---|---|---|
| 0.0–2.4 | 0.3–2.7 | face, bottle brought up | hook |
| 2.4–4.8 | 17.6–20.0 | settles in frame | *Apa tu double cleansing?* (1 tanggalkan makeup & sunscreen, 2 baru cuci muka) |
| 4.8–7.3 | 7.0–11.0 (1.6×) | pad on the pump | **01 Buang makeup**, *Basahkan kapas dulu* |
| 7.3–17.5 | 20–23, 39.5–41.8, 29.6–32, 46.3–48.2, 52–55 | wipes, eyes, mouth, neck, more wipes | tip cards |
| 17.5–20.5 | 77.5–80.5 | clean face close-up | **02 Cuci muka**, foam card |
| 20.5–23.5 | 80.5–83.5 | clean face, smile | *bersih & terasa lembut ✨*, *Baru sambung toner & pelembap* |
| 23.5–25.9 | 1.5–2.7 (0.5× slow-mo) | bottle | *Rutin malam aku 🌙*, *Langkah 1 aku: O’CHEAL Micellar Water*, **Tekan beg kuning 🛍️** |

## Claims

- "Tekap dulu ±3 saat" comes from the brand's own usage slide (9/9).
- "Proceed to the next skincare step" is also from slide 9. Every other line is general routine advice or the creator's own experience ("terasa lembut").
- There is no lip-makeup claim, because her lips are still tinted at the end.
