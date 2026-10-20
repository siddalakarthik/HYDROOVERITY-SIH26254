"""Conserved lumped water paths; coefficients are unmeasured hypotheses."""
import numpy as np
from simulations.common import CollarObservation,readonly

def generate(case,seed,s,regime):
    rng=np.random.default_rng(seed);n=int(s['duration_s']);t=np.arange(n,dtype=float)
    local=case in ('G02','G03','G06','G07','G10','G11','G13','G14')
    rain=case in ('G04','G05','G14');service=case=='G12'
    volumes=np.zeros(5);history=[];pad=[];multi=[];total=drained=evaporated=0.
    pad_volume=0.;multi_volume=np.zeros(3)
    eff=s['regimes'][regime]['collection'];intrusion=s['regimes'][regime]['rain_intrusion']
    eff*=float(rng.uniform(.7,1.1));target=1 if case=='G03' else 0
    for k in range(n):
        q=.15 if local and k>=30 else 0.;external=.25 if rain and k>=30 else 0.
        if case=='G05':external=.012
        if case=='G11':q=.001
        challenge=.04 if service and 30<=k<40 else 0.
        e=eff*(.1 if case in ('G06','G07') else 1.)
        incoming=np.zeros(5);incoming[target]+=q*e;incoming[4]+=q*(1-e)
        incoming[3]+=external*(1-intrusion);incoming[0]+=external*intrusion
        incoming[0]+=challenge
        volumes+=incoming;total+=q+external+challenge
        if case=='G10':
            migration=volumes[0]*.15;volumes[0]-=migration;volumes[1]+=migration
        d=volumes*s['drain_fraction_per_s']
        if case in ('G06','G12','G13'):d[0]*=.1 if case!='G12' else 1.
        volumes-=d;drained+=d.sum()
        ev=np.minimum(volumes,s['evaporation_ml_per_s']);volumes-=ev;evaporated+=ev.sum()
        history.append(volumes.copy())
        # Baselines receive same incident water, their declared unguarded transfer differs.
        pad_volume=(pad_volume+q+external+challenge)*(1-s['drain_fraction_per_s'])
        multi_volume=(multi_volume+np.array([q+external*.5+challenge,external*.5,0.]))*(1-s['drain_fraction_per_s'])
        pad.append(pad_volume>s['activation_ml'])
        multi.append(multi_volume>s['activation_ml'])
    wet=np.array(history)>s['activation_ml'];health=['UNKNOWN']*5
    if case=='G08':wet[:,0]=False # unsupervised disconnection indistinguishable from dry
    if case=='G09':wet[:,0]=True
    if case=='G08':
        pad=np.zeros(n,dtype=bool);multi=np.array(multi);multi[:,0]=False
    if case=='G09':
        pad=np.ones(n,dtype=bool);multi=np.array(multi);multi[:,0]=True
    obs=CollarObservation(readonly(t),readonly(wet),tuple(health),0 if service else None,30. if service else None,40. if service else None)
    truth={'local':local,'case':case,'regime':regime,'input_ml':total,'retained_ml':float(volumes.sum()),'drained_ml':float(drained),'evaporated_ml':float(evaporated),'mass_error_ml':float(total-volumes.sum()-drained-evaporated),'blockage':case in ('G06','G13'),'fault':case in ('G08','G09')}
    return obs,readonly(np.array(pad)),readonly(np.array(multi)),truth
