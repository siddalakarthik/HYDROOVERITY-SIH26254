"""Numerical invariants and observation-only contracts, not physical validation."""
from dataclasses import fields,replace
import numpy as np
import pytest
from simulations.common import Capture,HydraulicObservation,CollarObservation,config,digest
from simulations.hydraulics.model import solve,generate as hydro
from simulations.hydraulics.detector import assess as watch
from simulations.acoustics.model import generate as acoustic,delay
from simulations.acoustics.detector import assess as locate,peak
from simulations.guard5.model import generate as collar
from simulations.guard5.detector import assess as guard
from simulations.evaluation.metrics import binary,wilson

@pytest.mark.parametrize('area',[0.,1e-7,5e-6])
def test_epanet_balance(area):
    r=solve(area_m2=area)
    assert r['valid'] and r['solver']=='EPANET 2.2 PDA'
    assert abs(r['balance_error_lpm'])<1e-3 and r['pressure_bar']>0
    assert r['inlet_lpm']>=r['outlets_lpm']-1e-3

@pytest.mark.parametrize('case',['H01','H04','H07'])
def test_hydraulic_controls(case):
    obs,truth=hydro(case,12);p=watch(obs,config()['hydraulic'])
    assert not np.any(p['watch_alarm'])
    if case=='H07':assert set(p['state'])=={'OFF'}

def test_invalid_solver_observation_abstains():
    obs,_=hydro('H01',12)
    p=watch(replace(obs,solver_valid=np.zeros(len(obs.time_s),bool)),config()['hydraulic'])
    assert not np.any(p['watch_alarm']) and set(p['state'])=={'UNKNOWN'}

@pytest.mark.parametrize('case,sign',[('A01',1),('A02',0),('A03',-1)])
def test_sign_and_position(case,sign):
    cap,truth=acoustic(case,7,8);p=locate(cap,config()['acoustic'])
    assert abs(p['cc_m']-truth['position_m'])<.1
    assert abs(p['lag_s'])<.0001 if sign==0 else p['lag_s']*sign>0

def test_fractional_delay():
    a=np.random.default_rng(2).normal(size=8192);b=delay(a,2.4/4096,4096)
    lag=peak(a,b,4096,.01)[0]*4096
    assert abs(lag-2.4)<.25

@pytest.mark.parametrize('change,outcome',[({'pressure_bar':0},'NO_PRESSURE'),({'eligible_path':False},'INVALID_PATH'),({'shared_clock':False},'INVALID_PATH')])
def test_acoustic_metadata_gates(change,outcome):
    cap,_=acoustic('A01',7,8);assert locate(replace(cap,**change),config()['acoustic'])['outcome']==outcome

def test_invalid_and_weak_signal():
    cap,_=acoustic('A01',7,8)
    assert locate(replace(cap,samples=np.full_like(cap.samples,np.nan)),config()['acoustic'])['outcome']=='INVALID_CAPTURE'
    assert locate(replace(cap,samples=np.zeros_like(cap.samples)),config()['acoustic'])['outcome']=='INSUFFICIENT_SIGNAL'

def test_speed_sensitivity_and_bounds():
    cap,truth=acoustic('A01',7,8);s=config()['acoustic'];p=locate(cap,s);bad=locate(replace(cap,speed_mps=cap.speed_mps*1.25),s)
    assert abs(bad['cc_m']-truth['position_m'])>abs(p['cc_m']-truth['position_m'])
    if bad['interval_m']:assert 0<=bad['interval_m'][0]<=bad['interval_m'][1]<=cap.span_m

@pytest.mark.parametrize('case',[f'G{i:02d}' for i in range(1,15)])
def test_guard_mass_and_channels(case):
    obs,_,_,truth=collar(case,7,config()['guard'],'nominal')
    assert obs.wet.shape==(180,5) and abs(truth['mass_error_ml'])<1e-9
    assert guard(obs,config()['guard'])['health']==['UNKNOWN']*5

def test_environment_bypass_and_service():
    s=config()['guard']
    obs,*_=collar('G04',7,s,'unfavorable');assert not guard(obs,s)['local_suspect']
    obs,*_=collar('G07',7,s,'nominal');assert obs.wet[:,4].any() and not obs.wet[:,3].any()
    obs,*_=collar('G12',7,s,'nominal');assert guard(obs,s)['service']=='RESPONSE_OBSERVED'

def test_truth_seed_separation_and_determinism():
    c=config();assert len({c[k] for k in c if k.endswith('_seed')})==4
    for dtype in (Capture,HydraulicObservation,CollarObservation):
        assert not {'position_m','actual_labels','truth_seed','seed','local'} & {f.name for f in fields(dtype)}
    a,t=acoustic('A07',1,2);b,u=acoustic('A07',1,2)
    assert np.array_equal(a.samples,b.samples) and t==u
    import inspect
    from simulations.acoustics import detector
    assert 'model' not in inspect.getsource(detector) and 'truth' not in inspect.getsource(detector)

def test_metric_denominators():
    rows=[dict(truth=True,predicted=True),dict(truth=True,predicted=False),dict(truth=False,predicted=True),dict(truth=False,predicted=False)]
    m=binary(rows);assert (m['tp'],m['fp'],m['fn'],m['tn'],m['f1'])==(1,1,1,1,.5)
    lo,hi=wilson(0,10);assert 0<=lo<.00001 and .27<hi<.28

def test_solver_failure_explicit(monkeypatch):
    import wntr
    def fail(*args,**kwargs):raise RuntimeError('intentional solver failure')
    monkeypatch.setattr(wntr.sim.EpanetSimulator,'run_sim',fail)
    r=solve(head_m=29.876543)
    assert not r['valid'] and r['solver']=='INVALID_SOLVER_RESULT'

def test_shared_clock_bias_and_fault_controls():
    from simulations.evaluation.sensitivity import run
    rows=run();timing=[r for r in rows if r['experiment']=='unmodeled_channel_skew']
    assert timing[-1]['error_m']>timing[0]['error_m']+.5
    assert rows[-2]['health'][0]=='UNKNOWN' and rows[-1]['health'][0]=='DISCONNECTED'

def test_capture_same_input_not_mutated():
    cap,_=acoustic('A06',7,8);before=cap.samples.copy()
    locate(cap,config()['acoustic'])
    assert np.array_equal(before,cap.samples)

def test_unknown_storage_abstains():
    obs,_=hydro('H03',12)
    p=watch(replace(obs,storage_known=np.zeros(len(obs.time_s),bool)),config()['hydraulic'])
    assert not np.any(p['watch_alarm']) and set(p['qualified_outcome'])=={'UNRESOLVED'}

def test_out_of_bounds_qualified_location_rejected(monkeypatch):
    from simulations.acoustics import detector
    cap,_=acoustic('A01',7,8)
    monkeypatch.setattr(detector,'peak',lambda *a,**k:(.2,2.,.8,np.array([.2]),np.array([1.])))
    p=detector.assess(cap,config()['acoustic'])
    assert p['outcome']=='UNRESOLVED' and p['position_m'] is None and p['interval_m'] is None
