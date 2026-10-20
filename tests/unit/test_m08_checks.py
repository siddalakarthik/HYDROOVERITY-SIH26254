"""Reject consequential M08 consistency errors; no physical-validation claims."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('m08',ROOT/'scripts/check_m08.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class EngineeringChecks(unittest.TestCase):
    def setUp(self):
        self.d=m.load('hardware/electronics/interfaces.json');self.b=m.load('hardware/bom/m08_bom.json');self.p=m.load('hardware/guard5-collar/envelope.json');self.r=m.load('hardware/mechanical-cad/rig_layout.json')
    def check(self):m.check_data(self.d,self.b,self.p,self.r)
    def test_baseline(self):self.check()
    def test_sixth_wetness_rejected(self):
        self.d['wetness']['channels'].append('EXTRA')
        with self.assertRaisesRegex(AssertionError,'five'):self.check()
    def test_gpio_collision_rejected(self):
        self.d['ear_gpio']['SD_SCK']=15
        with self.assertRaisesRegex(AssertionError,'GPIO collision'):self.check()
    def test_independent_clock_rejected(self):
        self.d['acoustic']['clock_hz']=12000000
        with self.assertRaisesRegex(AssertionError,'sample clock'):self.check()
    def test_overbudget_rejected(self):
        self.b['contingency_inr']+=1000;self.b['grand_total_inr']+=1000;self.b['headroom_inr']-=1000
        with self.assertRaisesRegex(AssertionError,'budget cap'):self.check()
    def test_pressure_overvoltage_rejected(self):
        self.d['pressure']['divider_bottom_ohm']=100000
        with self.assertRaisesRegex(AssertionError,'overvoltage'):self.check()
    def test_operation_authority_rejected(self):
        self.r['pressure_authorized']=True
        with self.assertRaisesRegex(AssertionError,'authorization'):self.check()
    def test_undercounted_return_rejected(self):
        self.r['supply_return_additional_m']=3
        with self.assertRaisesRegex(AssertionError,'return length'):self.check()
    def test_broken_schematic_rejected(self):
        with self.assertRaisesRegex(AssertionError,'incomplete'):m.parse_sexpr('(kicad_sch (version 20230121)')

if __name__=='__main__':unittest.main()
