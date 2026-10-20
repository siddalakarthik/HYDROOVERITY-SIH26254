"""python -m simulations.run_all --profile smoke|ppt|stress; no API required."""
import argparse,platform,subprocess,sys,json
from importlib.metadata import version
from pathlib import Path
from dataclasses import asdict
import numpy as np
from simulations.common import ROOT,config,write_json,digest,clean,LABEL
from simulations.hydraulics.model import generate as hydraulic,solve,NODES,PIPES
from simulations.hydraulics.detector import assess as watch
from simulations.acoustics.model import generate as capture
from simulations.acoustics.detector import assess as locate
from simulations.guard5.model import generate as collar
from simulations.guard5.detector import assess as guard
from simulations.evaluation.metrics import binary,acoustic

def run(profile='smoke',output=None):
    cfg=json.loads((ROOT/'simulations/scenarios/final_benchmark.json').read_text('utf-8'));reps=cfg['profiles'][profile];out=Path(output) if output else ROOT/'simulations/results'/profile
    rows={'hydraulics':[],'acoustics':[],'guard':[]};examples={};failures=[]
    for split in ('development','holdout'):
        ts=cfg[split+'_truth_seed'];ns=cfg[split+'_observation_seed']
        hrep=reps['hydraulic_repeats'] if split=='holdout' else 1
        for i in range(1,13):
            case=f'H{i:02d}'
            for repeat in range(hrep):
                obs,truth=hydraulic(case,ns+repeat*100+i);pred=watch(obs,cfg['hydraulic'])
                target=bool(truth.active_leak.any());start=np.where(truth.active_leak)[0]
                for method,key in [('fixed','fixed_alarm'),('watch','watch_alarm')]:
                    alarm=pred[key];after=np.where(alarm & truth.active_leak)[0]
                    rows['hydraulics'].append({'split':split,'case':case,'repeat':repeat,'method':method,'truth':target,'predicted':bool(len(after)) if target else bool(alarm.any()),'delay_s':float(obs.time_s[after[0]]-obs.time_s[start[0]]) if len(after) and len(start) else None,'pre_event_alarms':int(alarm[:start[0]].sum()) if len(start) else 0,'unresolved_fraction':float(np.mean(np.array(pred['qualified_outcome'])=='UNRESOLVED')),'max_balance_error_lpm':float(np.nanmax(np.abs(truth.balance_error_lpm))),'solver_failures':sum('INVALID' in v for v in truth.solver_status)})
                if split=='holdout' and repeat==0:examples[case]={'observed':asdict(obs),'predicted':pred,'truth':asdict(truth)}
        arep=reps['acoustic_repeats'] if split=='holdout' else 1
        for i in range(1,13):
            for repeat in range(arep):
                case=f'A{i:02d}';cap,truth=capture(case,ts+i*1000+repeat,ns+i*1000+repeat);p=locate(cap,cfg['acoustic'])
                error=lambda x:abs(x-truth['position_m']) if x is not None else None
                interval=p['interval_m'];rows['acoustics'].append(dict(split=split,case=case,repeat=repeat,eligible=truth['eligible'],**p,error_m=error(p['position_m']),cc_error_m=error(p['cc_m']),phat_error_m=error(p['phat_m']),interval_contains_truth=bool(interval and interval[0]<=truth['position_m']<=interval[1]),speed_assumed_mps=cap.speed_mps))
                if split=='holdout' and repeat==0:examples[case]={'observed':asdict(cap),'predicted':p,'truth':truth}
        grep=reps['guard_repeats'] if split=='holdout' else 1
        for regime in cfg['guard']['regimes']:
            for i in range(1,15):
                for repeat in range(grep):
                    case=f'G{i:02d}';obs,pad,multi,truth=collar(case,ts+i*1000+repeat,cfg['guard'],regime);p=guard(obs,cfg['guard'])
                    for method,alarm in [('pad',pad.any()),('multizone',(multi[:,0] & ~multi[:,1]).any()),('guard5',p['local_suspect'])]:
                        rows['guard'].append({'split':split,'case':case,'repeat':repeat,'regime':regime,'method':method,'truth':truth['local'],'predicted':bool(alarm),'outcome':p['outcome'] if method=='guard5' else 'BINARY_WETNESS_ALARM','mass_error_ml':truth['mass_error_ml'],'service':p['service'],'blockage_truth':truth['blockage'],'blockage_suspected':p['blockage_suspected'],'health':p['health']})
                    if regime=='nominal' and split=='holdout' and repeat==0:examples[case]={'observed':asdict(obs),'predicted':p,'truth':truth}
    # Verification uses observations, not generator repair labels.
    timeline=[]
    for name,missing in [('comparable_repair',False),('missing_post_evidence',True),('incomplete_repair',False)]:
        obs,_=hydraulic('H12',123,repair_fraction=.6 if name=='incomplete_repair' else 0,missing_post=missing)
        p=watch(obs,cfg['hydraulic']);before=(obs.time_s>=1500)&(obs.time_s<2400);after=obs.time_s>=2700
        valid=np.isfinite(obs.customer_outlet_lpm[after]).all()
        pre=float(np.mean(p['residual_lpm'][before]));post=float(np.mean(p['residual_lpm'][after])) if valid else None
        status='NOT_VERIFIABLE' if not valid else 'PASSED' if post<1 and pre-post>1 else 'FAILED'
        cap,_=capture('A01',71099,91099);acoustic_result=locate(cap,cfg['acoustic'])
        wet,*_=collar('G02',71099,cfg['guard'],'nominal');collar_result=guard(wet,cfg['guard'])
        timeline.append({'case':name,'source':'SIMULATION','events':[{'time_s':180,'event':'FILLING state abstraction'},{'time_s':660,'event':p['state'][11]},{'time_s':900,'event':'Scenario intervention: modeled emitter enabled'},{'time_s':1200,'event':p['qualified_outcome'][20]},{'time_s':1320,'event':'GUARD-5: '+collar_result['outcome']},{'time_s':1380,'event':'EAR: '+acoustic_result['outcome']},{'time_s':1500,'event':'SIMULATED incident / investigation'},{'time_s':2400,'event':'SIMULATED repair intervention'},{'time_s':3000,'event':status}],'verification':status,'before_residual_lpm':pre,'after_residual_lpm':post,'acoustic':acoustic_result,'guard5':collar_result,'integration_limit':'Independent engine scenario outputs joined for demonstration; not a coupled fluid-acoustic model or backend workflow.'})
    hold=lambda key:[r for r in rows[key] if r['split']=='holdout']
    summary={'label':LABEL,'profile':profile,'hydraulics':{m:binary([r for r in hold('hydraulics') if r['method']==m]) for m in ('fixed','watch')},'acoustics':acoustic(hold('acoustics')),'guard':{regime:{m:binary([r for r in hold('guard') if r['method']==m and r['regime']==regime]) for m in ('pad','multizone','guard5')} for regime in cfg['guard']['regimes']},'solver_failures':sum(r['solver_failures'] for r in hold('hydraulics')),'max_hydraulic_balance_error_lpm':max(r['max_balance_error_lpm'] for r in hold('hydraulics')),'max_guard_mass_error_ml':max(abs(r['mass_error_ml']) for r in hold('guard')),'integrated':timeline}
    for method in ('fixed','watch'):
        rr=[r for r in hold('hydraulics') if r['method']==method];delays=[r['delay_s'] for r in rr if r['delay_s'] is not None]
        summary['hydraulics'][method].update(median_detected_delay_s=float(np.median(delays)) if delays else None,unresolved_fraction_mean=float(np.mean([r['unresolved_fraction'] for r in rr])) if method=='watch' else None,pre_event_alarm_samples=sum(r['pre_event_alarms'] for r in rr),nonleak_observed_hours=sum(not r['truth'] for r in rr),false_alarm_unit='Scenario/cycle events, not independent per-sample alarms')
    for regime in cfg['guard']['regimes']:
        rr=[r for r in hold('guard') if r['method']=='guard5' and r['regime']==regime]
        summary['guard'][regime]['diagnostics']={'n':len(rr),'unknown_health_fraction':float(np.mean([any(h=='UNKNOWN' for h in r['health']) for r in rr])),'blockage_true_positive':sum(r['blockage_truth'] and r['blockage_suspected'] for r in rr),'blockage_missed':sum(r['blockage_truth'] and not r['blockage_suspected'] for r in rr),'service_outcomes':{k:sum(r['service']==k for r in rr if r['case']=='G12') for k in ('RESPONSE_OBSERVED','COLLECTION_OR_SENSOR_UNRESOLVED')}}
    from simulations.evaluation.sensitivity import run as sensitivities
    write_json(out/'sensitivity.json',sensitivities())
    manifest={'label':LABEL,'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'dependencies':{p:version(p) for p in ('numpy','scipy','pandas','matplotlib','wntr','pytest')},'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'config':cfg,'config_sha256':digest(cfg),'algorithm_version':'M05-2','solver':'EPANET 2.2 PDA; transition abstractions explicitly labeled','access':'Evaluator-only results; not an ordinary dashboard export'}
    examples['network']={'nodes':NODES,'pipes':PIPES,'solution':solve(area_m2=5e-6)}
    manifest['algorithm_source_sha256']=digest({str(p.relative_to(ROOT)):p.read_text('utf-8') for p in sorted((ROOT/'simulations').rglob('*.py'))})
    write_json(out/'manifest.json',manifest);write_json(out/'summary.json',summary);write_json(out/'evaluation.json',rows);write_json(out/'examples.json',examples)
    from simulations.figures import render
    render(out)
    print('Completed',profile,'EPANET/hydraulics, acoustics, GUARD-5; 8 figures. Output:',out)
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--profile',choices=['smoke','ppt','stress'],default='smoke');parser.add_argument('--output');args=parser.parse_args();run(args.profile,args.output)
