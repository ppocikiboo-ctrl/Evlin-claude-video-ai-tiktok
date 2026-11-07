import sherpa_onnx, wave, numpy as np, json, sys
M='/tmp/claude-0/models/sherpa-onnx-whisper-medium/'
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=M+'medium-encoder.int8.onnx',decoder=M+'medium-decoder.int8.onnx',tokens=M+'medium-tokens.txt',language='ms',task='transcribe',num_threads=8)
w=wave.open(sys.argv[1]); sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
cfg=sherpa_onnx.VadModelConfig(); cfg.silero_vad.model='/tmp/claude-0/models/silero_vad.onnx'; cfg.silero_vad.min_silence_duration=0.3; cfg.silero_vad.max_speech_duration=12; cfg.sample_rate=sr
vad=sherpa_onnx.VoiceActivityDetector(cfg,buffer_size_in_seconds=120)
segs=[]
ws=cfg.silero_vad.window_size
def drain():
  while not vad.empty():
    s=vad.front; st=s.start/sr; d=len(s.samples)/sr
    stream=rec.create_stream(); stream.accept_waveform(sr,s.samples); rec.decode_stream(stream)
    segs.append({'start':round(st,2),'end':round(st+d,2),'text':stream.result.text.strip()}); print(segs[-1],flush=True); vad.pop()
for i in range(0,len(x),ws):
  vad.accept_waveform(x[i:i+ws]); drain()
vad.flush(); drain()
json.dump(segs,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
