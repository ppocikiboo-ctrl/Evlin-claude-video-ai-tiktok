import sys, re, json, subprocess, wave
import numpy as np, torch
from transformers import VitsModel, AutoTokenizer

P, OUT = sys.argv[1], sys.argv[2]
m = VitsModel.from_pretrained(P); tok = AutoTokenizer.from_pretrained(P)
m.speaking_rate = 1.05
SR = m.config.sampling_rate

# speaker: S = penjual (seller / narrator), B = pembeli (buyer, deeper voice)
LINES = {
 1: ('S', "bayangkan anda jual yogurt. tapi tiada siapa yang beli."),
 2: ('B', "okey."),
 3: ('S', "satu cawan tulis, dua puluh peratus lemak. satu lagi, lapan puluh peratus bebas lemak. mana satu laku?"),
 4: ('B', "lapan puluh peratus bebas lemak."),
 5: ('S', "kenapa?"),
 6: ('B', "sebab bunyinya lebih sihat."),
 7: ('S', "padahal, ia yogurt yang sama."),
 8: ('B', "jadi orang beli perkataan. bukan yogurt."),
 9: ('S', "itulah, frem ming efek. orang beli, cara ia disampaikan."),
 10: ('B', "apa lagi?"),
 11: ('S', "beg dan jam tangan, empat puluh sembilan ringgit. atau beg empat puluh sembilan ringgit, jam tangan percuma?"),
 12: ('B', "jam percuma la. mestilah."),
 13: ('S', "harga sama. barang sama."),
 14: ('B', "tapi percuma, rasa lebih untung."),
 15: ('S', "itulah, bandel prising."),
 16: ('B', "dan yang terakhir?"),
 17: ('S', "butang tulis, beli sekarang. anda terus beli?"),
 18: ('B', "tak naklah. nanti nanti la beli."),
 19: ('S', "sekarang tulis, tinggal tiga lagi."),
 20: ('B', "saya beli sekarang juga."),
 21: ('S', "kenapa?"),
 22: ('B', "sebab takut terlepas."),
 23: ('S', "skar siti. takut terlepas, buat orang cepat bertindak."),
 24: ('B', "jadi produk tak pernah berubah. cuma cara saya sampaikan."),
 25: ('S', "folo untuk lagi tips marketing."),
}

def synth(text, seed):
    torch.manual_seed(seed)
    with torch.no_grad():
        w = m(**tok(text, return_tensors='pt')).waveform[0].numpy()
    # trim leading/trailing near-silence
    idx = np.where(np.abs(w) > 0.02 * np.abs(w).max())[0]
    return w[max(0, idx[0] - 200): idx[-1] + 400] if len(idx) else w

durs = {}
for n, (spk, line) in LINES.items():
    parts = re.split(r'([,.?])', line)
    audio = []
    for k in range(0, len(parts), 2):
        ph = parts[k].strip()
        if not ph: continue
        punct = parts[k + 1] if k + 1 < len(parts) else '.'
        w = synth(ph, 100 + n * 10 + k)
        audio.append(w / (np.abs(w).max() + 1e-9) * 0.9)
        audio.append(np.zeros(int(SR * (0.18 if punct == ',' else 0.32))))
    w = np.concatenate(audio[:-1])
    raw = f'{OUT}/raw_{n}.wav'
    with wave.open(raw, 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((w * 32767).astype(np.int16).tobytes())
    af = 'aresample=44100'
    if spk == 'B':
        af = 'aresample=44100,rubberband=pitch=0.86:formant=preserved'
    else:
        af = 'aresample=44100,rubberband=pitch=1.03'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', af + ',highpass=f=80,acompressor=threshold=-18dB:ratio=3', '-ar', '44100', '-ac', '1', f'{OUT}/voice_{n}.wav'], check=True)
    with wave.open(f'{OUT}/voice_{n}.wav') as f:
        durs[n] = f.getnframes() / f.getframerate()
    print(n, spk, round(durs[n], 2))
json.dump(durs, open(f'{OUT}/durs.json', 'w'))
