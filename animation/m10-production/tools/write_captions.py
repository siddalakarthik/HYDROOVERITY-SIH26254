"""Draft timed captions from observed ASR; canonical spelling only, review tracked."""
import json
from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
audio=json.loads((root/'public/audio/audio-measurements.json').read_text('utf-8'))
def stamp(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
def spelling(text):
    text=re.sub(r'hydro[- ]?(?:overity|verity|varity|severity)', 'HYDROOVERITY',text,flags=re.I)
    text=re.sub(r'hydro[- ]?(?:ir|ear)', 'HYDRO-EAR',text,flags=re.I)
    text=re.sub(r'hydro[- ]?(?:verified|verification|verify)', 'HYDRO-VERIFY',text,flags=re.I)
    text=re.sub(r'hydro[- ]?watch', 'HYDRO-WATCH',text,flags=re.I)
    return text.strip()
captions=[]
for part in range(4):
    data=json.loads((root/f'local/transcripts/part{part}.transcript.json').read_text('utf-8'))
    offset=audio['tracks'][part]['global_start'];pending=[]
    def flush():
        if pending:
            captions.append({'start':offset+pending[0]['start'],'end':offset+pending[-1]['end'],
                'text':spelling(''.join(w['word'] for w in pending)), 'part':part})
            pending.clear()
    for segment in data['segments']:
        for word in segment['words']:
            if pending and (len(''.join(w['word'] for w in pending))+len(word['word'])>78 or word['end']-pending[0]['start']>4.5):flush()
            pending.append(word)
            if word['word'].rstrip().endswith(('.', '?', '!')):flush()
    flush()
for a,b in zip(captions,captions[1:]):
    assert a['end']<=b['start']+.01,(a,b)
srt='\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(captions))+'\n'
(root/'HYDROOVERITY_M10_CAPTIONS_DRAFT.srt').write_text(srt,encoding='utf-8')
# Preserve the raw ASR draft. Correct obvious project terminology in a separate
# review copy; these are contextual editorial corrections, not listening evidence.
corrections={
 'called AP and C.':'called A, B and C.',
 'internal nodes':'internal notes',
 'import and replace':'import and replay',
 'conclusions – past,':'conclusions – passed,',
 'basic legal arm':'basic leak alarm',
 'five distinct water parts':'five distinct water paths',
 'our caller':'our collar',
 '-5 caller':'-5 collar',
 'whether physics supports it':'where the physics supports it',
}
edited=srt
applied=[]
for original,replacement in corrections.items():
    if original in edited:
        edited=edited.replace(original,replacement)
        applied.append({'asr':original,'editorial':replacement})
(root/'HYDROOVERITY_M10_CAPTIONS.srt').write_text(edited,encoding='utf-8')
(root/'local/caption-corrections.json').write_text(json.dumps({'status':'CONTEXT_CORRECTED_REVIEW_COPY_NOT_LISTENING_VERIFIED','corrections':applied},indent=2),encoding='utf-8')
(root/'local/caption-review.json').write_text(json.dumps({'status':'ASR_DRAFT_REQUIRES_LISTENING_REVIEW','canonical_spelling':True,'speech_modified':False,'captions':captions},indent=2),encoding='utf-8')
print(len(captions),'nonoverlapping draft captions; listening review remains required')
