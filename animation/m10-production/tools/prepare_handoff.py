"""Assemble truthful manifests and voice-only final mix; never mark render QA passed."""
import hashlib
import json
from pathlib import Path
import wave

root=Path(__file__).resolve().parents[1]
t=json.loads((root/'src/data/timeline.json').read_text())
voice=root/'public/audio/HYDROOVERITY_M10_VOICE_MASTER.wav'
mix=root/'public/audio/HYDROOVERITY_M10_FINAL_MIX.wav'
with wave.open(str(voice),'rb') as src:
    params=src.getparams();pcm=src.readframes(src.getnframes())
    target=t['duration_frames']*48000//30
    padding=target-src.getnframes()
    assert params.framerate==48000 and padding>=0
with wave.open(str(mix),'wb') as out:
    out.setparams(params);out.writeframes(pcm);out.writeframes(b'\0'*(padding*params.nchannels*params.sampwidth))
manifest=json.loads((root/'local/asset-manifest.json').read_text())
for item in manifest:
    if 'asset' in item:
        item['visual_privacy_review']='Top/middle/end inspected: synthetic utility/test records, no credentials or real resident data observed. Full-pixel OCR not performed.'
manifest.extend([{'asset':f'audio/{p.name}','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'classification':'OWNER_NARRATION_LOCAL_ONLY'} for p in [voice,mix]])
payload={'baseline':t['baseline'],'assets':manifest,'music':'None: owner-authorized clean voice-only fallback; no third-party soundtrack',
 'mix':'Exact normalized voice PCM followed by silent visual hold. No narration cuts, overlaps, pitch or speed changes.',
 'original_recordings':'Remain outside Git. SHA256 and per-track measurements in local public/audio/audio-measurements.json.',
 'review_status':'Source and sampled privacy review complete; rendered-film QA recorded separately.'}
(root/'HYDROOVERITY_M10_ASSET_MANIFEST.json').write_text(json.dumps(payload,indent=2)+'\n')
print(f'Voice-only final mix: {target} samples, {target/48000:.6f}s; {padding} silence samples after narration')
