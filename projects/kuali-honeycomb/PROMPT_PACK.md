# Kuali Honeycomb — Tumis Udang & Sayur, Tangan Sahaja (8s, 9:16)

Video TikTok affiliate yang realistik: hanya tangan yang kelihatan memotong
sayur dan bawang putih, lalu menumis udang dengan sayur dalam kuali honeycomb.
Suara latar (voiceover) dalam Bahasa Melayu Malaysia.

**Gambar rujukan:**
- [`reference/product-poster.jpg`](reference/product-poster.jpg): poster produk
- [`reference/cooking-scene.png`](reference/cooking-scene.png): adegan masak (rujukan utama untuk gaya video)

### Butiran produk (ikut gambar)

| Ciri | Apa yang kelihatan |
|---|---|
| Badan kuali | Kuali wok bulat dan dalam, warna hitam matte di luar |
| Permukaan dalam | Corak honeycomb (heksagon) perak halus pada latar hitam |
| Bibir atas | Jalur corak "api / daun" perak di sekeliling bahagian atas dinding dalam |
| Dasar | Bulatan honeycomb yang lebih terang di tengah dasar |
| Pemegang | Dua pemegang gelung (loop) warna emas di kiri dan kanan, dipasang dengan rivet perak |
| Senduk | Senduk nilon hitam berlubang dengan pemegang kayu |
| Dapur | Dapur gas kaca hitam, dinding jubin putih berkilat, pasu pokok hijau di belakang |

---

## 1. Cara guna dalam Google Flow

1. Pilih model **Veo 3** (Veo 3 Quality atau Fast). Hanya Veo 3 yang menjana
   suara dan dialog, jadi pastikan audio dihidupkan.
2. Pilih mod **Ingredients to Video** dan muat naik `cooking-scene.png`
   (serta `product-poster.jpg` jika boleh) sebagai ingredient. Kuali akan
   lebih tepat berbanding jika ia dijana daripada teks sahaja.
3. Tetapkan nisbah **9:16 (portrait)**.
4. Tampal **Prompt Utama** di bawah. Jana 2–4 versi dan pilih yang paling bagus.
5. Jika suara lari atau terpotong, guna **Pilihan B** (2 klip) di bahagian 4.

---

## 2. Prompt Utama (8 saat, satu klip)

```
Vertical 9:16 ultra-realistic TikTok cooking video, 8 seconds, filmed on a
smartphone. ONLY HANDS are visible: a Malaysian woman's hands with natural
skin and short clean nails. No face, no body, no head ever appears in frame.
Bright, clean modern kitchen: glossy white tiled wall, black glass gas stove,
green potted plant and wooden utensils in a white holder in the background,
soft natural daylight.

The product: a deep round black wok with a silver honeycomb hexagon pattern
on the inside surface, a silver flame/leaf pattern band around the upper inner
rim, a brighter honeycomb circle at the base, and two gold loop handles fixed
with silver rivets on the left and right. Keep the wok exactly like the
reference image.

Shot 1 (0–2s): close-up top-down on a wooden chopping board. The hands use a
kitchen knife to quickly slice fresh green kailan stalks into short pieces,
crisp chopping sounds.
Shot 2 (2–3.5s): quick close-up of the hands slicing garlic cloves and a red
chili on the same board.
Shot 3 (3.5–8s): 45-degree angle over the stove. The black honeycomb wok sits
on a gas flame. The hands toss in the garlic, then pink prawns and the kailan.
One hand holds the gold handle, the other stir-fries with a black nylon
spatula with a wooden handle. Steam rises, light sizzling, the food slides
smoothly across the honeycomb surface without sticking, very little oil. The
camera slowly pushes in on the wok so the honeycomb pattern and gold handles
are clearly visible.

Audio: realistic kitchen ASMR, knife chopping then oil sizzling, plus a warm,
cheerful female voiceover in Malaysian Malay (Bahasa Melayu Malaysia accent),
spoken off-screen, starting at 1 second and finishing before 8 seconds, at a
lively and natural pace:
"Ini kuali honeycomb, masak lebih sihat dan tak melekat. Haba sekata, tahan
lama, dan boleh masak kurang minyak!"

Style: realistic, natural colors, sharp focus, smooth handheld movement, quick
TikTok-style cuts. No subtitles, no on-screen text, no music, no watermark.
```

### Negative prompt (jika ada ruangan)

```
face, head, full body, person visible, extra fingers, deformed hands, extra
hands, blurry, cartoon, CGI look, text, subtitles, watermark, logo change,
wok with long single handle, non-stick coating without honeycomb, food
sticking, burnt food, excess oil, background music
```

---

## 3. Petua

- **8 saat agak padat** untuk 3 aksi dan 18 patah perkataan. Prompt menetapkan
  suara bermula pada saat ke-1 dengan tempo laju supaya tidak terpotong.
- Jika Veo menyebut perkataan dengan loghat Indonesia, ulang jana atau tambah
  `Malaysian accent, not Indonesian` dalam bahagian audio.
- Jika muka atau badan muncul, tambah `extreme close-up, camera framed only on
  the hands and countertop` dalam prompt.
- Tukar `kailan` kepada `asparagus` jika mahu sayur yang sama seperti dalam
  gambar rujukan.

---

## 4. Pilihan B — 2 klip × 8 saat (lebih santai), sambung dalam Flow Scenebuilder / CapCut

**Klip 1: potong bahan**

```
Vertical 9:16 ultra-realistic smartphone video, 8 seconds, ONLY HANDS visible,
no face or body. Bright white tiled kitchen, wooden chopping board. Close-up:
a woman's hands slice fresh green kailan stalks, then garlic cloves and a red
chili, then push them into a small bowl beside fresh pink prawns. Crisp knife
chopping ASMR. Warm female voiceover in Malaysian Malay, off-screen:
"Jom masak tumis udang sayur guna kuali honeycomb ni!"
No subtitles, no music, no watermark.
```

**Klip 2: masak dalam kuali**

```
Vertical 9:16 ultra-realistic smartphone video, 8 seconds, ONLY HANDS visible,
no face or body. A deep round black wok with a silver honeycomb hexagon inner
pattern, a silver flame-pattern rim band and two gold loop handles with silver
rivets, on a black glass gas stove in a bright white kitchen. One hand holds the
gold handle, the other stir-fries prawns, kailan, garlic and red chili with a
black nylon spatula with a wooden handle. Steam, sizzling, food slides without
sticking, very little oil, slow push-in on the honeycomb surface. Warm female
voiceover in Malaysian Malay, off-screen, natural pace:
"Ini kuali honeycomb, masak lebih sihat dan tak melekat. Haba sekata, tahan
lama, dan boleh masak kurang minyak!"
No subtitles, no music, no watermark.
```

---

## 5. Konsep 2 — Ujian Telur Tak Melekat (8s, tangan sahaja)

```
Vertical 9:16 ultra-realistic TikTok video, 8 seconds, filmed on a smartphone.
ONLY HANDS visible, a Malaysian woman's hands, no face or body ever in frame.
Bright modern kitchen, glossy white tiled wall, black glass gas stove, soft
daylight.

The product: a deep round black wok with a silver honeycomb hexagon pattern
inside, a silver flame/leaf pattern band around the upper inner rim and two
gold loop handles with silver rivets. Keep it exactly like the reference image.

Shot 1 (0–2s): close-up, one hand pours only a few drops of oil into the hot
honeycomb wok on a gas flame.
Shot 2 (2–5s): the hand cracks two eggs into the wok, the whites sizzle and
turn crispy at the edges, bright orange yolks.
Shot 3 (5–8s): one hand holds the gold handle and gently tilts and shakes the
wok; both fried eggs slide freely across the honeycomb surface without
sticking. Slow push-in on the eggs gliding.

Audio: loud satisfying sizzling ASMR, plus a warm, excited female voiceover
in Malaysian Malay accent, off-screen, starting at 0.5 seconds, natural lively
pace:
"Tengok ni, minyak sikit je... telur langsung tak melekat! Kuali honeycomb,
haba sekata, masak lebih sihat."

Realistic, natural colors, sharp focus, smooth handheld movement. No
subtitles, no on-screen text, no music, no watermark.
```

## 6. Konsep 3 — Senang Cuci Lepas Masak (8s, tangan sahaja)

```
Vertical 9:16 ultra-realistic TikTok video, 8 seconds, filmed on a smartphone.
ONLY HANDS visible, a Malaysian woman's hands, no face or body ever in frame.
Bright white kitchen with a stainless steel sink.

The product: a deep round black wok with a silver honeycomb hexagon pattern
inside, a silver flame/leaf pattern band around the upper inner rim and two
gold loop handles with silver rivets. Keep it exactly like the reference image.

Shot 1 (0–2.5s): close-up of the honeycomb wok just after cooking, with
leftover sticky red sambal sauce coating the inside.
Shot 2 (2.5–6s): at the sink, one hand holds the gold handle under running
tap water, the other wipes once with a soft yellow sponge; the sauce rinses
off instantly, revealing the clean shiny honeycomb pattern.
Shot 3 (6–8s): the hands lift the clean, glossy wok toward the camera,
showing the honeycomb surface and gold handles catching the light.

Audio: running water and light sponge sounds, plus a warm, cheerful female
voiceover in Malaysian Malay accent, off-screen, starting at 0.5 seconds:
"Masak sambal pun tak melekat. Bilas sikit je, terus bersih! Kuali honeycomb
ni memang tahan lama."

Realistic, natural colors, sharp focus, smooth handheld movement. No
subtitles, no on-screen text, no music, no watermark.
```
