# Durimex Coffee — TikTok edit (kopi durian belanda + kunyit hitam)

Final: [`output/durimex-coffee-tiktok-edit.mp4`](output/durimex-coffee-tiktok-edit.mp4) — 1080x1920, 28.7s (asal 36.8s).

## Apa yang diedit
- **Lebih laju & lancar**: jeda senyap >0.2s dipotong (pad 70ms), kemudian keseluruhan dipercepat 1.2x (pitch suara kekal).
- **Jump-cut zoom**: setiap potongan bertukar zoom 1.00x / 1.08x + slow push-in supaya potongan nampak sengaja.
- **Warna**: kontras & saturasi dinaikkan sedikit, sharpen ringan. Audio: compressor + loudnorm -14 LUFS.
- **Hook (frame pertama)**: "RAMAI TAK TAHU!" + "KOPI DURIAN BELANDA + KUNYIT HITAM?!" dengan kad gambar.
- **Kad bahan**: Durian Belanda (dipotong dari gambar kotak), Kunyit Hitam, Kunyit, Sacha Inchi, Kopi Robusta (ilustrasi).
- **Checklist bahan, Halal JAKIM / MeSTI / 10 sachet x 25g**, CTA "TEKAN BAKUL KUNING" + anak panah.
- SFX pop/whoosh pada setiap animasi dan potongan.

## Jana semula
```bash
python3 scripts/cut.py input.mp4 cut.mov          # potong jeda + 1.2x
ffmpeg -ss 1 -i input.mp4 -frames:v 1 front.jpg   # frame kotak depan (untuk gambar durian belanda)
python3 scripts/render.py cut.mov front.jpg final.mp4
```

## Versi 2 — gaya & struktur berbeza

Final: [`output/durimex-coffee-tiktok-edit-v2.mp4`](output/durimex-coffee-tiktok-edit-v2.mp4) — 29.7s.

Struktur: **Hook → Features → Bukti label → Benefits (emosi) → Kenapa sekarang → CTA**

| Bahagian | Teks atas skrin | Visual |
|---|---|---|
| Hook | MINUM KOPI TIAP PAGI? / Tengok ni dulu sebelum beli kopi lain. | Skrin gelap terang perlahan, teks marker besar, bunyi boom |
| Apa dalam ni? | Kopi + herba pilihan dalam 1 sachet | Kad spec dengan nombor naik: 2.0% jus durian belanda, 0.5% kunyit hitam, 0.5% kunyit, sacha inchi, 10% robusta, 116 kcal |
| Bukti di label | Bukan claim kosong. Tertulis kat label. | Zoom label sebenar + highlight oren, badge Halal JAKIM / MeSTI / 25g x 10 |
| Kenapa orang suka | Pagi yang tenang. Secawan yang wangi. / Nikmat kopi, TANPA RASA BERSALAH. / Sebab awak layak jaga diri walaupun hidup sibuk. | Kinetic text perkataan demi perkataan |
| Kenapa sekarang? | Harga promo TikTok tak kekal lama. Lagi cepat order, lagi cepat rasa. | |
| Cara order | KLIK BAKUL KUNING + 3 langkah | Butang berdenyut, anak panah |

Gaya: grade sinematik hangat + vignette + grain, palet coklat kopi / krim / oren, bar cerita 6 segmen,
tag bab, flash putih + goncang kamera setiap tukar bahagian. Audio: muzik lo-fi 88 BPM (disintesis, turun
automatik bila bercakap), SFX boom / tick / ding / riser / whoosh.

```bash
python3 scripts/render2.py cut.mov input.mp4 final_v2.mp4
```

## Versi 3 — klip kacau kopi (14.4s)

Final: [`output/durimex-coffee-tiktok-edit-v3.mp4`](output/durimex-coffee-tiktok-edit-v3.mp4)

| Masa | Bahagian | Teks / visual |
|---|---|---|
| 0.0–2.6s | Hook harga | KOPI RASA KAFE, TAK SAMPAI RM8 SECAWAN?! · Harga label RM79 / 10 sachet · tag "DURIMEX COFFEE" pada sachet |
| 2.6–5.0s | Tengok ni | Kamera zoom ke buih · Tengok buih dia... CREAMY GILA! · Lemak hazelnut & vanila, wangi macam kopi kafe. |
| 5.0–8.6s | Kenapa wajib cuba | Gambar kopi latte + 4 kebaikan: durian belanda + kunyit hitam, gula nano 116 kcal, bancuh 1 minit, Halal JAKIM & MeSTI |
| 8.6–11.8s | Emosi | Awak penat jaga semua orang. Pagi ni, jaga diri sendiri. · Secawan kopi wangi, 5 minit tenang yang awak layak dapat. |
| 11.8–14.4s | CTA | Frame akhir dimalapkan · TEKAN BAKUL KUNING · gambar kopi · Grab sekarang sebelum stok promo habis! · anak panah |

```bash
SPEED=1.1 python3 scripts/cut.py input.mp4 cut.mov
python3 scripts/render3.py cut.mov video_kotak_asal.mp4 final_v3.mp4   # video kotak = sumber gambar kopi
```
