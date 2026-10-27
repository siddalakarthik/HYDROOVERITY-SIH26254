"""Scientific and sample-boundary invariants; no physical performance claims."""
import hashlib
import json
import unittest
from pathlib import Path

PROJECT=Path(__file__).resolve().parents[1]
REPO=PROJECT.parents[1]

class ProductionInvariants(unittest.TestCase):
    def test_frozen_engineering_source(self):
        envelope=json.loads((REPO/'hardware/guard5-collar/envelope.json').read_text('utf-8'))
        self.assertEqual(set(envelope['pockets']),{'A','B','C'})
        cad=(REPO/'hardware/mechanical-cad/guard5.py').read_text('utf-8')
        self.assertIn("parts['EXT_witness']",cad)
        self.assertIn("parts['BYPASS_witness']",cad)

    def test_unfavorable_benchmark_and_budget_preserved(self):
        summary=json.loads((REPO/'simulations/evaluation/reference_summary.json').read_text('utf-8'))
        nominal=summary['guard']['nominal']
        self.assertLess(nominal['guard5']['f1'],nominal['pad']['f1'])
        self.assertLess(nominal['pad']['f1'],nominal['multizone']['f1'])
        acoustic=summary.get('acoustics',summary.get('acoustic'))
        self.assertEqual((acoustic['eligible'],acoustic['accepted'],acoustic['unresolved'],acoustic['confidently_wrong_intervals']),(264,190,74,20))
        bom=json.loads((REPO/'hardware/bom/m08_bom.json').read_text('utf-8'))
        self.assertEqual(len(bom['items']),41)
        self.assertEqual(sum(i['extended_cost_inr'] for i in bom['items'])+bom['contingency_inr'],59870)
        self.assertEqual(bom['cap_inr']-bom['grand_total_inr'],130)

    def test_audio_is_contiguous_and_bounded(self):
        report=json.loads((PROJECT/'public/audio/audio-measurements.json').read_text('utf-8'))
        cursor=0
        for i,track in enumerate(report['tracks']):
            self.assertEqual(track['file'],f'part{i}.mp3')
            self.assertEqual(track['global_start_sample'],cursor)
            cursor+=track['decoded_samples_48k']
            self.assertEqual(track['global_end_sample'],cursor)
            self.assertLessEqual(float(track['after']['input_tp']),-1)
        self.assertEqual(cursor,report['total_samples'])
        self.assertLess(abs(report['frames_at_30fps']/30-report['duration_seconds']),1/30)
        self.assertLessEqual(float(report['master_measurement']['input_tp']),-1)

    def test_cad_provenance_and_complete_parts(self):
        manifest=json.loads((PROJECT/'public/cad/manifest.json').read_text('utf-8'))
        self.assertEqual(manifest['source_sha256'],hashlib.sha256((REPO/manifest['source']).read_bytes()).hexdigest())
        self.assertEqual(len(manifest['parts']),25)
        for part in manifest['parts']:
            self.assertEqual(part['sha256'],hashlib.sha256((PROJECT/f"public/cad/{part['name']}.json").read_bytes()).hexdigest())

if __name__=='__main__':
    unittest.main()
