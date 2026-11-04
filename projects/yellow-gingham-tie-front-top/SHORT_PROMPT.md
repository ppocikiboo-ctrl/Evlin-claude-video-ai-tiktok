# Yellow Gingham Tie-Front Top — Prompt pendek (jika Flow gagal jana)

Prompt panjang kadang-kadang ditolak atau gagal dalam Flow. Versi ini jauh
lebih pendek, tanpa senarai "Avoid" yang panjang dan tanpa perincian badan.
Guna **Frames to Video**, **Veo 3.1**, 9:16, dan `reference/model-mirror-selfie.png`
sebagai First frame.

## Versi 1 (disyorkan)

```
Vertical 9:16, 8-second smartphone mirror selfie video, starting from the
uploaded image. A young woman stands in front of a full-length mirror in a
bedroom, holding a burgundy phone in front of her face. She wears a pastel
yellow gingham tie-front top with ruffle trim and a white ruffled layer
underneath, a black pleated skirt, white socks and white sneakers. She gently
touches the small bow on her top, lifts the white ruffle, sways side to side,
then ends in a relaxed pose. Soft warm indoor light, steady handheld camera,
same bedroom throughout. No music, no speech, no text.
```

## Versi 2 (paling ringkas)

```
8-second vertical mirror selfie video from the uploaded image. The woman
holding the burgundy phone in front of her face shows off her yellow gingham
tie-front top: she touches the bow, lifts the white ruffle and sways gently.
Same bedroom, steady camera, natural light, no sound.
```

## Jika masih gagal

| Cuba | Sebab |
|---|---|
| Tukar model ke **Veo 3.1 Fast** | Kadang-kadang Quality sibuk atau gagal |
| Jana semula 2–3 kali | Kegagalan sementara pada pelayan |
| Crop gambar (potong ruang kosong, kekalkan 9:16) | Gambar terlalu besar boleh gagal dimuat naik |
| Buang `skirt` dan perincian kaki dari prompt | Tapis kandungan boleh menolak pakaian pendek |
| Mula tanpa gambar (Text to Video) untuk uji prompt | Mengasingkan masalah gambar daripada masalah prompt |
| Salin mesej ralat Flow dan hantar kepada saya | Saya boleh tepatkan punca sebenar |
