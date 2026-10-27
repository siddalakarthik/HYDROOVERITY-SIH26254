"""Local ASR word estimates. Originals remain the authority; never generate speech."""
import argparse
import json
import subprocess
import io
import wave
from pathlib import Path
import numpy as np

from faster_whisper import WhisperModel

p = argparse.ArgumentParser()
p.add_argument('--input', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--model-cache', type=Path, required=True)
p.add_argument('--model', default='base.en')
p.add_argument('--ffmpeg', type=Path, required=True)
args = p.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
model = WhisperModel(args.model, device='cpu', compute_type='int8', cpu_threads=4,
                     download_root=str(args.model_cache))
for i in range(4):
    destination = args.output / f'part{i}.transcript.json'
    if destination.exists():
        continue
    pcm=subprocess.run([str(args.ffmpeg),'-v','error','-i',str(args.input/f'part{i}.mp3'),
                        '-ar','16000','-ac','1','-c:a','pcm_s16le','-f','wav','-'],capture_output=True,check=True).stdout
    with wave.open(io.BytesIO(pcm),'rb') as wav:
        samples=np.frombuffer(wav.readframes(wav.getnframes()),dtype=np.int16).astype(np.float32)/32768.0
    segments, info = model.transcribe(samples, language='en',
                                     word_timestamps=True, beam_size=5, vad_filter=False,
                                     initial_prompt='HYDROOVERITY, Team TARK, HYDRO-WATCH, GUARD-5, HYDRO-EAR, HYDRO-VERIFY, EXT, BYPASS.')
    rows = []
    for segment in segments:
        rows.append({'start': segment.start, 'end': segment.end, 'text': segment.text,
                     'words': [{'start': w.start, 'end': w.end, 'word': w.word,
                                'probability': w.probability} for w in segment.words]})
    destination.write_text(json.dumps({'file': f'part{i}.mp3', 'method': f'faster-whisper {args.model} int8; estimated, review required',
                                       'duration': info.duration, 'segments': rows}, indent=2) + '\n', encoding='utf-8')
    print(destination.name, len(rows), 'segments', flush=True)
