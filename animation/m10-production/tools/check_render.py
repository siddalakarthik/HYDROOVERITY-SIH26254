"""Decode actual output, check timing/codecs and create review sheets. No subjective pass claims."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

import av
import numpy as np
from PIL import Image, ImageDraw

p=argparse.ArgumentParser()
p.add_argument('video',type=Path)
p.add_argument('--ffprobe',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
root=Path(__file__).resolve().parents[1]
timeline=json.loads((root/'src/data/timeline.json').read_text('utf-8'))
probe=json.loads(subprocess.check_output([str(a.ffprobe),'-v','error','-show_streams','-show_format','-of','json',str(a.video)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video')
audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert v['codec_name']=='h264' and audio['codec_name']=='aac'
assert v['r_frame_rate']=='30/1' and audio['sample_rate']=='48000'
assert (v['width'],v['height']) in [(960,540),(1920,1080)]
expected=timeline['duration_frames']
assert abs(float(probe['format']['duration'])-expected/30)<.08
a.output.mkdir(parents=True,exist_ok=True)
targets={}
for scene in timeline['scenes']:
    for label,frame in [('mid',scene['from']+scene['duration']//2),('end',scene['from']+scene['duration']-2)]:
        targets[frame]=f"{scene['id']}-{label}"
sampled=[]
count=0
black=[]
with av.open(str(a.video)) as container:
    stream=container.streams.video[0]
    stream.thread_type='AUTO'
    for count,frame in enumerate(container.decode(stream),start=1):
        n=count-1
        assert frame.pts is not None
        assert abs(float(frame.pts*stream.time_base)-n/30)<.002
        if n%15==0:
            pixels=np.asarray(frame.to_image().resize((96,54)).convert('L'))
            if float((pixels<8).mean())>.98:black.append(n)
        if n in targets:
            image=frame.to_image();image.thumbnail((960,540))
            path=a.output/(targets[n]+'.jpg');image.save(path,quality=93)
            sampled.append({'frame':n,'seconds':n/30,'image':path.name})
assert count==expected,(count,expected)
assert len(sampled)==len(timeline['scenes'])*2
for page in range(math.ceil(len(sampled)/12)):
    sheet=Image.new('RGB',(1440,1180),'#102533');draw=ImageDraw.Draw(sheet)
    for i,item in enumerate(sampled[page*12:page*12+12]):
        image=Image.open(a.output/item['image']);image.thumbnail((464,261))
        x=(i%3)*480;y=(i//3)*295
        sheet.paste(image,(x,y+28))
        draw.text((x+8,y+6),f"{item['image']} / {item['seconds']:.2f}s",fill='white')
    sheet.save(a.output/f'contact-{page:02}.jpg',quality=92)
result={'video':a.video.name,'sha256':hashlib.sha256(a.video.read_bytes()).hexdigest(),
 'codec':v['codec_name'],'audio_codec':audio['codec_name'],'sample_rate':48000,
 'width':v['width'],'height':v['height'],'fps':30,'decoded_frames':count,
 'duration_seconds':float(probe['format']['duration']),
 'decode':'PASS','frame_timestamps':'PASS','all_scenes_sampled':'PASS',
 'near_black_sampled_frames':black,'black_scan':'Every 15th frame; >98% luma <8; deliberate opening must be assessed separately',
 'visual_review':'PENDING: inspect the generated mid/end sheets; decoding alone is not visual approval',
 'sampled_frames':sampled}
(a.output/'technical-qa.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='sampled_frames'},indent=2))
