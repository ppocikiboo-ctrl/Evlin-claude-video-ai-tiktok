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

**Peraturan susun atur:** kopi dalam mug (y ≈ 380–1040) tidak pernah ditutup. Semua teks di jalur atas (y 165–360) atau bawah mug (y ≥ 1080); gambar latte kecil di sebelah kanan bawah, frame akhir hanya dimalapkan sedikit.

| Masa | Bahagian | Teks / visual |
|---|---|---|
| 0.0–2.6s | Hook | KOPI SEDAP, TAPI... TANPA GULA PUTIH?! · Guna gula nano + kunyit hitam |
| 2.6–5.0s | Tengok ni | Tengok buih dia... CREAMY GILA! · Lemak hazelnut & vanila, wangi macam kopi kafe. · tag "DURIMEX COFFEE" pada sachet |
| 5.0–8.6s | Kenapa wajib cuba | Gambar latte kecil + 4 kebaikan: tanpa gula putih (gula nano, 5.2g gula sesachet), kunyit hitam & kunyit, durian belanda + sacha inchi, Halal JAKIM & MeSTI |
| 8.6–11.8s | Emosi | Penat seharian? Rehat sekejap, jaga diri sendiri. · Secawan kopi herba, manis tanpa gula putih, untuk awak & keluarga. |
| 11.8–14.4s | CTA | TEKAN BAKUL KUNING · Grab sekarang sebelum stok promo habis! · anak panah |

Tiada harga dalam video. Tiada dakwaan perubatan (kencing manis / kebas / lenguh) — lihat nota pematuhan TikTok Shop.

```bash
SPEED=1.1 python3 scripts/cut.py input.mp4 cut.mov
python3 scripts/render3.py cut.mov video_kotak_asal.mp4 final_v3.mp4   # video kotak = sumber gambar kopi
```

## Versi 4 — "3 SEBAB" listicle (klip kacau kopi, 14.4s)

Final: [`output/durimex-coffee-tiktok-edit-v4.mp4`](output/durimex-coffee-tiktok-edit-v4.mp4)

| Masa | Bahagian | Teks / visual |
|---|---|---|
| 0.0–2.3s | Hook | 3 SEBAB AKU TUKAR KE KOPI NI! · tag kuning "DURIMEX COFFEE" + anak panah ke sachet · "Tonton sampai habis" |
| 2.3–4.9s | #1 | TANPA GULA PUTIH · ikon gula kiub dipangkah · Guna gula nano, 5.2g gula sesachet |
| 4.9–7.5s | #2 | ADA KUNYIT HITAM · sticker kunyit hitam + kunyit · Herba tradisional pilihan orang kita |
| 7.5–10.1s | #3 | CREAMY MACAM KAFE · sticker latte + durian belanda · Lemak hazelnut & vanila + durian belanda |
| 10.1–11.8s | Bonus | HALAL & LULUS MeSTI · Halal JAKIM / MeSTI / Bancuh 1 minit |
| 11.8–14.4s | CTA | NAK CUBA? · butang kuning TEKAN BAKUL KUNING · ringkasan 3 sebab · Cuba sendiri hari ni! |

Gaya: palet hijau jenama + kuning, nombor besar #1/#2/#3, sticker bahan, peralihan glitch RGB,
muzik ceria 104 BPM (C–G–Am–F, arpeggio + tepukan). Kopi dalam mug tidak ditutup. Tiada harga, tiada dakwaan perubatan.

```bash
python3 scripts/render4.py cut.mov video_kotak_asal.mp4 final_v4.mp4   # cut.mov sama seperti versi 3
```
