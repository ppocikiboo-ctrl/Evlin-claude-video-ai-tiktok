# Candy Monjo — edit video "cara ambil"

- Output: `candy-monjo-edit.mp4` (1080x1920, 10.4s)
- Sumber dipotong pada 0–10.4s (bahagian cara pengambilan sahaja).
- Dibuang: bahagian 10.4s ke atas — suara & kapsyen asal sebut "seminggu boleh dapat 2 ke 3",
  "sesuai untuk orang yang susah...", "pakai jeans lama" (dakwaan berat badan = risiko violation).
- Teks tambahan hanya di jalur atas (y 11%–36%), tidak tutup botol.
- Teks: "RAMAI DM TANYA... / CARA AMBIL CANDY MONJO", "1) PAGI, SEBELUM SARAPAN",
  "2) 1 BIJI SEHARI | 1 BOTOL = 7 BIJI", "NAK CUBA? / TEKAN BEG KUNING".
- Overlay dijana oleh `make_overlays.py <out_dir>`.

## V2 — gaya "checklist"
- Output: `candy-monjo-edit-v2.mp4` (1080x1920, 10.4s), bahagian sumber yang sama (0–10.4s).
- Hook: "SOALAN NO.1 DALAM DM / MACAM MANA NAK AMBIL?"
- Checklist muncul ikut suara: Waktu pagi → Sebelum sarapan → 1 biji sehari → 1 botol = 7 biji.
- CTA di header: "NAK CUBA? TEKAN BEG KUNING". Tona lebih hangat + vignette.
- Overlay: `make_overlays_v2.py <out_dir>`.
