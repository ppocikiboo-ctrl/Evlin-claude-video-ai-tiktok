# Burgundy Ruffle Babydoll Top with Back Bow — Google Flow, 8s, joget, tanpa bunyi

Mirror selfie OOTD 8 saat. Perempuan berjoget ringan sambil memperagakan baju:
mula dari depan, kemudian pusing ke belakang untuk tunjuk reben besar. Tiada
muzik dan tiada suara; muzik ditambah sendiri kemudian.

**Gambar rujukan**

| Fail | Guna |
|---|---|
| [`reference/first-frame-front.png`](reference/first-frame-front.png) | **First frame** (pandangan depan) |
| [`reference/last-frame-back.png`](reference/last-frame-back.png) | **Last frame** (pandangan belakang) |
| [`reference/front-back-collage.png`](reference/front-back-collage.png) | Gambar asal (kolaj). Jangan upload ini terus, Flow perlukan satu pandangan setiap frame |

## Cara guna dalam Google Flow

1. **New project** → mod **Frames to Video** → model **Veo 3.1**. Aspect ratio **9:16**.
2. Upload `first-frame-front.png` di slot **First frame** dan
   `last-frame-back.png` di slot **Last frame**. Jika Flow minta crop ke 9:16,
   pastikan seluruh baju (bahu hingga hujung baju) kekal dalam bingkai.
3. Paste **Prompt 1** (depan → belakang). Jana 3–4 versi; pusingan badan
   kadang-kadang rosak, pilih yang paling licin.
4. Buang bunyi selepas muat turun (Veo selalu letak bunyi):
   CapCut → Volume 0, atau `ffmpeg -i in.mp4 -an -c:v copy out_silent.mp4`.
   Kemudian letak lagu sendiri.

Mahu habis menghadap depan semula? Guna **Prompt 2** dengan first frame
sahaja (kosongkan slot last frame).

## Prompt 1 — depan → belakang (first + last frame)

```
8-second vertical 9:16 video, one continuous shot, from the uploaded first
frame (front view) to the uploaded last frame (back view). An authentic
TikTok OOTD mirror selfie in a bedroom, filmed on a phone, handheld but
steady, warm afternoon sunlight with soft light stripes on the floor. No
cuts, no zoom, no camera moves other than her hand. Framing from her head to
mid-thigh, the top always fully visible.

Keep EVERYTHING exactly as in the reference frames. The same young Malaysian
woman: very long dark-brown wavy hair, half-up with a messy bun on top, slim,
real skin texture. She holds the same burgundy phone with a triple camera in
front of her face with the same hand the whole time, so her face is never
shown, including during the turn. Thin silver pendant necklace, a pearl
bracelet on her free wrist, a small cream leather shoulder bag with gold
hardware on her phone-side shoulder.

THE PRODUCT, unchanged in every frame: a wine-red / burgundy cotton poplin
babydoll top. Front: square neckline, a flat yoke across the chest, soft
gathers falling into a loose flowy body ending at the hip; wide straps with
ruffled flutter sleeves on the shoulders. Back: square open back with an
elasticated top edge, and a large self-fabric bow tied at the centre back
with two long tails hanging down past the hem; the same ruffled straps. She
wears cream / ivory denim shorts with back patch pockets.

She does a light, happy, casual joget-style dance to an imagined upbeat beat,
relaxed and cute, not a choreographed routine:
0–3 s: Facing the mirror, she sways her hips side to side and bounces her
shoulders to the beat; her free hand lightly swings, then flicks the
ruffled sleeve. The flowy body of the top swings with her.
3–4 s: Still dancing, her free hand sweeps her long hair over her front
shoulder to clear her back.
4–6 s: She turns around slowly on the beat with small dancing steps,
keeping the phone raised in front of her face and pointed at the mirror,
until her back faces the mirror.
6–8 s: With her back to the mirror, she keeps swaying her hips and bouncing
a little, so the big back bow and its long tails swing; the square open back
and ruffled straps are clearly visible. She ends matching the last frame.

Real body movement and fabric physics: the light cotton top swings and
settles, the bow tails sway, natural hair movement. Photorealistic, no
beauty filter, no slow motion, no cinematic grading.

SILENT VIDEO: no music, no speech, no singing, no sound effects.
No text, no subtitles, no watermark.

Avoid: revealing her face, phone moving away from her face, changing face,
different woman, extra fingers, distorted hands, twisted arms, unnatural
spin, body morphing during the turn, phone changing colour, warped mirror,
top changing colour, red or pink top, missing ruffles, missing back bow, bow
on the front, closed back, sleeves, long top, skirt, jeans, white shorts
turning into a skirt, bag disappearing, background change, flickering,
jump cut, music, voice.
```

## Prompt 2 — depan → belakang → depan (first frame sahaja)

Guna Prompt 1, tetapi tukar baris pertama dan bahagian aksi seperti ini:

```
8-second vertical 9:16 video, one continuous shot, starting exactly from the
uploaded first frame (front view).
...
0–2 s: Facing the mirror, she sways her hips and bounces her shoulders to
the beat; her free hand flicks the ruffled sleeve.
2–3 s: She sweeps her long hair over her front shoulder.
3–5 s: She turns around on the beat with small dancing steps, phone still in
front of her face, and sways with her back to the mirror so the big back bow
and long tails swing and the square open back is clearly visible.
5–7 s: She turns back to the front, still dancing.
7–8 s: She ends facing the mirror in a cute pose, free hand holding the hem
of the top out a little.
```

## Jika ada masalah

| Masalah | Penyelesaian |
|---|---|
| Badan berpintal / pusingan pelik | Tambah `she turns slowly in small steps, feet stepping naturally` dan jana semula |
| Muka terdedah masa pusing | Guna Prompt 1 (dengan last frame); ulang `the phone covers her face during the turn` |
| Reben hilang / pindah ke depan | Pastikan last frame diupload; tambah `the bow is only on the back` |
| Joget terlalu kuat / nampak AI | Tukar `joget-style dance` jadi `gentle swaying to the beat` |
| Masih ada bunyi | Buang dengan CapCut atau ffmpeg (langkah 4) |

## Caption TikTok

```
Baju babydoll merah wine ni comel sangat 🍷🎀 Lengan ruffle, belakang
terbuka dengan reben besar. Padan dengan short cream je dah cantik. Tekan beg
kuning untuk beli! 🛒

#ootd #babydolltop #ribbontop #ootdmalaysia #koreanstyle #tiktokshopmalaysia #fyp
```

Hidupkan label **AI-generated content** semasa post di TikTok.
