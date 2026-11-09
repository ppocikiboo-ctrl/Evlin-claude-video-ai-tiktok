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
