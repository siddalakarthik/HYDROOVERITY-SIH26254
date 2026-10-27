"""Build scene cuts from actual ASR words and sample-accurate audio offsets."""
import json
import math
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
audio=json.loads((ROOT/'public/audio/audio-measurements.json').read_text('utf-8'))
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
specs=[
 (0,'','town',{'intro':True,'opening':True}),
 (1,'','town',{}),
 (1,'Now imagine a small leak','pipe',{}),
 (1,'Wet soil could','qualification',{'mode':'rain'}),
 (1,'And in areas','qualification',{'mode':'supply'}),
 (1,'The challenge is','workflow',{'mode':'service'}),
 (1,'This is the problem','town',{'intro':True}),
 (1,'brings together four','workflow',{'mode':'architecture'}),
 (1,'First','qualification',{'mode':'watch'}),
 (1,'Is the pipeline','qualification',{'mode':'supply'}),
 (1,'Next comes','guard',{'exploded':False}),
 (1,'Inside the proposed','guard',{'exploded':True}),
 (1,'A fourth channel','guard',{'exploded':True,'focus':'EXT'}),
 (1,'A fifth','guard',{'exploded':True,'focus':'BYPASS'}),
 (1,'The aim is','qualification',{'mode':'patterns'}),
 (1,'This five channel','guard',{'exploded':False}),
 (1,'For suitable pipe','ear',{}),
 (1,'If the signal','ear',{'unresolved':True}),
 (1,'Together these ideas','workflow',{'mode':'architecture'}),
 (2,'','town',{}),
 (2,'A resident notices','software',{'asset':'home.png','title':'A resident notices\nsomething unusual.','note':'Simulated demonstration. No real village incident or installed sensor is claimed.'}),
 (2,'They sign in','software',{'asset':'resident-intake.png','title':'Describe. Submit.\nTrack securely.','note':'Authenticated service request intake. A submitted concern is not a confirmed leak.','scrollPixels':220}),
 (2,"On the supervisor's",'software',{'asset':'supervisor-triage.png','title':'Review before\ndispatch.','note':'Authorized utility review and legitimate investigation linkage.','scrollPixels':500}),
 (2,'Residents see safe','software',{'asset':'resident-timeline.png','title':'Progress residents\ncan safely see.','note':'Customer-safe updates. Internal utility notes remain restricted.','startScrollPixels':1220,'scrollPixels':120}),
 (2,'Now imagine the engineer','software',{'asset':'science-watch.png','title':'A scientific\nworkspace.','note':'Stored synthetic recordings, qualified pressure and flow traces.','science':True,'scrollPixels':640}),
 (2,'Charts show pressure','qualification',{'mode':'watch'}),
 (2,'These are research','software',{'asset':'science-ear.png','title':'Research scenarios.\nExplicit uncertainty.','note':'A separate synthetic scientific test capture. No installed sensors or exact-hole claim.','science':True,'startScrollPixels':850,'scrollPixels':220}),
 (2,'In our example','ear',{}),
 (2,'Next the supervisor','software',{'asset':'findings.png','title':'Authorized work.\nRecorded findings.','note':'Service requests link to genuinely triaged incidents and permitted work.','scrollPixels':430}),
 (2,'Scheduling checks','workflow',{'mode':'booking'}),
 (2,'A resident may request','booking',{}),
 (2,'Database rules','concurrency',{}),
 (2,'The technician opens','software',{'asset':'findings.png','title':'A technician\nrecords findings.','note':'Actual synthetic investigation-work capture. Findings do not fabricate a repair receipt.','startScrollPixels':1320,'scrollPixels':300}),
 (2,'In a future physical trial','repair',{}),
 (2,'And this is where','verification',{}),
 (2,'Reliable verification','verification',{}),
 (2,'Our scientific simulations','verification',{'outcomes':True}),
 (2,'But in the current','software',{'asset':'verification.png','title':'No evidence?\nNo invented success.','note':'Separate operational boundary-test capture: a manual-only record remains NOT_VERIFIABLE.'}),
 (2,'Residents can track','software',{'asset':'inbox.png','title':'Updates inside\nthe application.','note':'Separate authentic notification test. Delivered and read are distinct; external delivery remains disabled.','scrollPixels':180}),
 (2,'and leave feedback','software',{'asset':'feedback.png','title':'Feedback is heard.\nEvidence is separate.','note':'Separate eligible-closure feedback test using synthetic records. Satisfaction does not prove leak repair.','mobile':True,'startScrollPixels':1320,'scrollPixels':440}),
 (2,'From the first report','workflow',{'mode':'service'}),
 (3,'','workflow',{'mode':'architecture'}),
 (3,'Each is useful','workflow',{'mode':'architecture'}),
 (3,'Our testable idea','workflow',{'mode':'service'}),
 (3,'We are not claiming','guard',{'exploded':False}),
 (3,'In fact our own','evidence',{'kind':'guard'}),
 (3,'And some acoustic','evidence',{'kind':'ear'}),
 (3,'Rather than hiding','evidence',{'kind':'ear'}),
 (3,'Our private development software','software',{'asset':'supervisor.png','title':'Working software.\nExplicit boundaries.','note':'Authentic private-development dashboard. Synthetic data; no field performance claim.'}),
 (3,'At the current reviewed','evidence',{'kind':'software'}),
 (3,'The hardware is also','rig',{}),
 (3,'Its engineering files','guard',{'exploded':True}),
 (3,'The estimated complete','evidence',{'kind':'budget'}),
 (3,'Physical tests must','tests',{}),
 (3,'Privacy offline operation','workflow',{'mode':'gates'}),
 (3,'So hydro severity','town',{'closing':True}),
 (3,'When water is lost','town',{'closing':True}),
]
all_words={}
for part in range(4):
    raw=json.loads((ROOT/f'local/transcripts/part{part}.transcript.json').read_text('utf-8'))
    all_words[part]=[w for s in raw['segments'] for w in s['words']]

def anchor(part,phrase):
    if not phrase:return 0.0,0
    words=all_words[part]; target=norm(phrase)
    for i in range(len(words)):
        joined=''
        for j in range(i,min(i+18,len(words))):
            joined+=norm(words[j]['word'])
            if joined==target:return words[i]['start'],i
            if len(joined)>len(target):break
    raise ValueError(f'Unmatched narration cue part{part}: {phrase}')

rows=[]
for index,(part,phrase,kind,props) in enumerate(specs):
    local,word_index=anchor(part,phrase)
    start=audio['tracks'][part]['global_start']+local
    rows.append({'id':f'M10-{index:02d}','part':part,'original_audio':f'part{part}.mp3',
       'local_start':local,'global_start':start,'from':round(start*30),'kind':kind,'props':props,
       'opening_phrase':phrase or all_words[part][0]['word'].strip(),
       'word_index':word_index,'alignment_method':'Actual local faster-whisper word estimate; audiovisual review pending',
       'transition':'Continuous navy stage; frame-driven reveal; no audio overlap',
       'render_status':'NOT_RENDERED'})
for i,row in enumerate(rows):
    end=rows[i+1]['from'] if i+1<len(rows) else math.ceil(audio['duration_seconds']*30)+90
    assert end>row['from'],(i,row,end)
    row['duration']=end-row['from'];row['global_end']=end/30
    row['local_end']=min(row['global_end']-audio['tracks'][row['part']]['global_start'],audio['tracks'][row['part']]['decoded_samples_48k']/48000)
    words=[w['word'] for w in all_words[row['part']] if row['local_start']<=w['start']<row['local_end']]
    row['closing_phrase']=''.join(words[-8:]).strip()
    sources={
      'guard':['hardware/mechanical-cad/guard5.py','hardware/guard5-collar/envelope.json'],
      'rig':['hardware/mechanical-cad/rig_layout.json','hardware/render_m08.py'],
      'ear':['hardware/electronics/interfaces.json','hardware/electronics/netlist.json'],
      'evidence':['simulations/evaluation/reference_summary.json','hardware/bom/m08_bom.json','docs/testing/PRE_M10_COMPLETION_REGISTER.md'],
      'verification':['docs/testing/M06_SCIENTIFIC_INTEGRATION.md'],
    }
    row['source_assets']=[f"captures/{row['props']['asset']}"] if row['kind']=='software' else sources.get(row['kind'],['docs/project/HYDROOVERITY_MASTER_CONTEXT.md','CONCEPTUAL_ILLUSTRATION'])
    row['frame_start_seconds']=row['from']/30
    row['evidence_label']='AUTHENTIC SYNTHETIC SOFTWARE TEST' if row['kind']=='software' else 'SIMULATION / PROPOSED DESIGN / ILLUSTRATIVE'
timeline={'baseline':'886bf01d1c775ce0f1f7ec9f2ff2f27bc65a1d91','fps':30,'width':1920,'height':1080,
 'audio_seconds':audio['duration_seconds'],'duration_frames':rows[-1]['from']+rows[-1]['duration'],
 'rounding':'round each absolute word-anchor time to nearest frame; end ceil(audio samples / 48000 * 30) + 90 frame hold',
 'status':'DRAFT_TIMING_REVIEW_REQUIRED','scenes':rows}
(ROOT/'src/data').mkdir(exist_ok=True)
for dest in [ROOT/'src/data/timeline.json',ROOT/'HYDROOVERITY_M10_TIMELINE.json']:
    dest.write_text(json.dumps(timeline,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(ROOT/'HYDROOVERITY_M10_STORYBOARD.md').write_text('# HYDROOVERITY M10 storyboard\n\nActual ASR phrase anchors; audiovisual review pending. Software captures from different tests are explicitly identified as separate demonstrations.\n\n| Scene | Time | Visual | Opening phrase |\n|---|---|---|---|\n'+'\n'.join(f"| {r['id']} | {r['global_start']:.2f}–{r['global_end']:.2f}s | {r['kind']} | {r['opening_phrase']} |" for r in rows)+'\n',encoding='utf-8')
print(len(rows),'anchored scenes;',timeline['duration_frames'],'frames')
