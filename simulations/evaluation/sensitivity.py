"""Predeclared timing/path/fault controls; all runs retained, evaluator owns truth."""
from dataclasses import replace
import numpy as np
from simulations.common import config
from simulations.acoustics.model import generate,delay
from simulations.acoustics.detector import assess
from simulations.guard5.model import generate as collar
from simulations.guard5.detector import assess as guard

def run():
    cfg=config();rows=[]
    for offset in (0.,.00025,.001,.004):
        cap,truth=generate('A01',71099,91099);samples=cap.samples.copy()
        samples[1]=delay(samples[1],offset,cap.sample_rate_hz)
        prediction=assess(replace(cap,samples=samples),cfg['acoustic'])
        rows.append({'experiment':'unmodeled_channel_skew','offset_s':offset,'error_m':abs(prediction['cc_m']-truth['position_m']),'expected_bias_m':cap.speed_mps*offset/2,'outcome':prediction['outcome']})
    for setting in ({'eligible_path':False},{'shared_clock':False},{'pressure_bar':0.}):
        cap,_=generate('A01',71099,91099)
        rows.append({'experiment':'eligibility_control','change':setting,'outcome':assess(replace(cap,**setting),cfg['acoustic'])['outcome']})
    for supervised in (False,True):
        obs,*_=collar('G08',71099,cfg['guard'],'nominal')
        health=list(obs.health)
        if supervised:health[0]='DISCONNECTED'
        prediction=guard(replace(obs,health=tuple(health)),cfg['guard'])
        rows.append({'experiment':'electrical_supervision','observable':supervised,'health':prediction['health']})
    return rows
