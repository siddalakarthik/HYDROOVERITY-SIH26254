"""Public-source production checks, independent of private audio/capture files."""
import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]

class PublicProductionContract(unittest.TestCase):
    def test_timeline_covers_all_four_parts_without_gaps(self):
        t=json.loads((ROOT/'src/data/timeline.json').read_text('utf-8'))
        self.assertEqual((t['width'],t['height'],t['fps']),(1920,1080,30))
        cursor=0
        parts=[]
        for s in t['scenes']:
            self.assertEqual(s['from'],cursor)
            self.assertGreater(s['duration'],0)
            self.assertLessEqual(abs(s['global_start']-s['from']/30),1/60+.000001)
            cursor+=s['duration'];parts.append(s['part'])
            self.assertEqual(s['original_audio'],f"part{s['part']}.mp3")
        self.assertEqual(parts,sorted(parts))
        self.assertEqual(set(parts),{0,1,2,3})
        self.assertEqual(cursor,t['duration_frames'])
        self.assertTrue(3<=cursor/30-t['audio_seconds']<3+1/30)

    def test_public_facts_match_frozen_evidence(self):
        facts=json.loads((ROOT/'public/data/facts.json').read_text())
        source=json.loads((REPO/'simulations/evaluation/reference_summary.json').read_text())
        for k,v in facts['guard_f1'].items():
            self.assertEqual(v,source['guard']['nominal'][k]['f1'])
        self.assertEqual(facts['acoustics'],source.get('acoustics',source.get('acoustic')))
        bom=json.loads((REPO/'hardware/bom/m08_bom.json').read_text())
        self.assertEqual(sum(facts['bom_groups'].values())+bom['contingency_inr'],59870)
        self.assertEqual(facts['bom_item_count'],len(bom['items']))

    def test_draft_captions_are_ordered_and_bounded(self):
        text=(ROOT/'HYDROOVERITY_M10_CAPTIONS_DRAFT.srt').read_text('utf-8')
        def seconds(stamp):
            h,m,s,ms=map(int,re.split('[:,]',stamp));return h*3600+m*60+s+ms/1000
        previous=0
        for a,b in re.findall(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})',text):
            start,end=seconds(a),seconds(b)
            self.assertGreater(end,start)
            self.assertGreaterEqual(start,previous-.01)
            previous=end
        self.assertTrue(520<previous<525)

if __name__=='__main__':unittest.main()
