"""Eight presentation figures regenerated exclusively from saved experiment files."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from simulations.common import CHANNELS

NAMES=['01_hydraulic_network','02_supply_timeline','03_hydraulic_benchmark','04_acoustic_localization','05_acoustic_reliability','06_guard5_timelines','07_guard5_comparison','08_integrated_verification']
def render(out):
    out=Path(out);summary=json.loads((out/'summary.json').read_text());examples=json.loads((out/'examples.json').read_text());rows=json.loads((out/'evaluation.json').read_text())
    target=out.parent/'ppt' if out.name=='ppt' else out/'figures';target.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white'})
    captions=[]
    def new(title,panels=1):
        fig,axes=plt.subplots(panels,1,figsize=(16,9),squeeze=False);fig.suptitle(title,fontsize=23,fontweight='bold',x=.06,ha='left');fig.subplots_adjust(left=.09,right=.96,top=.85,bottom=.17,hspace=.55)
        return fig,list(axes[:,0])
    def save(fig,index,caption):
        fig.text(.06,.045,'SIMULATION • Physical sensors and field reliability unvalidated',fontsize=14,color='#b45309')
        fig.text(.06,.09,caption,fontsize=12,color='#475569');name=NAMES[index]
        fig.savefig(target/(name+'.png'),dpi=120);fig.savefig(target/(name+'.svg'));plt.close(fig);captions.append({'figure':name,'caption':caption,'source_files':['summary.json','evaluation.json','examples.json'],'limitations':'Assumed models; no measured physical performance.'})
    fig,(ax,)=new('01  Hydraulic network and modeled emitter leak')
    NODES=examples['network']['nodes'];PIPES=examples['network']['pipes'];press=examples['network']['solution']['pressures_bar']
    for _,a,b,_,_ in PIPES:ax.plot([NODES[a][0],NODES[b][0]],[NODES[a][1],NODES[b][1]],color='#94a3b8',lw=6)
    pts=ax.scatter(*np.array(list(NODES.values())).T,c=[press[k] for k in NODES],s=500,cmap='viridis',zorder=3)
    for k,(x,y) in NODES.items():ax.text(x,y+15,k,ha='center')
    ax.text(40,-28,'IN sector meter',fontsize=13);ax.text(270,120,'D1/D2/D3: customer meters',fontsize=13)
    ax.scatter(*NODES['L1'],marker='x',s=700,color='#dc2626',lw=5,zorder=4);ax.set(xlabel='Schematic layout x (m)',ylabel='Schematic layout y (m)');fig.colorbar(pts,ax=ax,label='Solved pressure (bar)')
    save(fig,0,'EPANET 2.2 PDA; IN minus terminal customer meters; red cross is generator truth, not detected location.')
    fig,axes=new('02  Intermittent supply and comparable observations',3)
    e=examples['H12'];t=np.array(e['observed']['time_s'])/60
    axes[0].plot(t,e['observed']['pressure_bar'],label='Pressure (bar)');axes[0].set_ylabel('bar');axes[0].legend()
    axes[1].plot(t,e['observed']['inlet_lpm'],label='Inlet');axes[1].plot(t,e['observed']['customer_outlet_lpm'],label='Customer outlets');axes[1].set(xlabel='Time (min)',ylabel='Flow (L/min)');axes[1].legend()
    for ax in axes[:2]:ax.axvspan(0,3,color='#94a3b8',alpha=.25);ax.axvspan(3,10,color='#fbbf24',alpha=.2);ax.axvline(15,color='#dc2626',ls='--');ax.axvline(40,color='#16a34a',ls='--')
    axes[2].plot(t,examples['H04']['observed']['inlet_lpm'],label='H04 demand rise (L/min)');axes[2].plot(t,np.array(examples['H06']['observed']['pressure_bar'])*10,label='H06 low pressure (bar ×10)');axes[2].plot(t,np.array(examples['H09']['observed']['pressure_bar'])*10,label='H09 draining (bar ×10)');axes[2].set_xlabel('Independent control scenarios: time (min)');axes[2].legend(fontsize=10,ncol=3)
    save(fig,1,'OFF 0–3 min; FILLING 3–10 min is an abstraction; modeled leak at 15 min, repair at 40 min. No two-phase claim.')
    fig,(ax,)=new('03  Hydraulic detection: all holdout scenario events')
    labels=['True positive','False positive','Missed event','True negative'];x=np.arange(4)
    for j,m in enumerate(('fixed','watch')):ax.bar(x+(j-.5)*.34,[summary['hydraulics'][m][k] for k in ('tp','fp','fn','tn')],.34,label=m)
    ax.set_xticks(x,labels);ax.set_ylabel('Scenario-event count');ax.legend();save(fig,2,'Same observations for both methods; small leaks and drifting meters can defeat qualification. Denominators include all cases.')
    fig,axes=new('04  Acoustic delay and qualified candidate interval',3);e=examples['A01'];a,b=np.array(e['observed']['samples']);fs=e['observed']['sample_rate_hz']
    axes[0].plot(np.arange(300)/fs,a[:300],label='A');axes[0].plot(np.arange(300)/fs,b[:300],alpha=.7,label='B');axes[0].set(xlabel='Shared-clock time (s)',ylabel='Amplitude (a.u.)');axes[0].legend()
    from simulations.acoustics.detector import peak
    lag,_,_,lags,v=peak(a,b,fs,.1);axes[1].plot(lags*1000,v);axes[1].set(xlabel='B minus A delay (ms)',ylabel='Correlation')
    axes[2].axvline(e['truth']['position_m'],color='#dc2626',label='Evaluation truth');interval=e['predicted']['interval_m']
    if interval:axes[2].axvspan(*interval,color='#0284c7',alpha=.35,label='Qualified candidate interval')
    axes[2].set(xlim=(0,e['observed']['span_m']),xlabel='Distance from endpoint A (m)',yticks=[]);axes[2].legend();save(fig,3,'Truth shown only by evaluator; shared sample grid; speed and coupling are assumptions. Result: '+e['predicted']['outcome'])
    fig,axes=new('05  Acoustic reliability includes unresolved and wrong cases',2)
    ar=[r for r in rows['acoustics'] if r['split']=='holdout' and r['eligible']];cases=sorted({r['case'] for r in ar})
    rates=[];wrong=[];err=[]
    for case in cases:
        rr=[r for r in ar if r['case']==case];accepted=[r for r in rr if r['position_m'] is not None];rates.append(len(accepted)/len(rr));wrong.append(sum(not r['interval_contains_truth'] for r in accepted)/len(rr));err.append(np.median([r['error_m'] for r in accepted]) if accepted else np.nan)
    axes[0].bar(cases,rates,label='Accepted fraction');axes[0].bar(cases,wrong,color='#dc2626',label='Wrong interval / all eligible');axes[0].set_ylabel('Fraction');axes[0].legend()
    axes[1].plot(cases,err,'o-',color='#0284c7');axes[1].set_ylabel('Accepted median error (m)');save(fig,4,'A04 weak SNR; A05 wrong speed; A06 pump; A07 multipath; A08 multiple sources. Missing error means abstention.')
    fig,axes=new('06  Five independent GUARD-5 channels',4)
    for ax,case in zip(axes,('G02','G04','G06','G12')):
        e=examples[case];wet=np.array(e['observed']['wet']);ax.imshow(wet.T,aspect='auto',origin='lower',extent=[0,len(wet),-.5,4.5],cmap='Blues',vmin=0,vmax=1);ax.set_yticks(range(5),[k.replace('COLLAR_','') for k in CHANNELS]);ax.set_title(case+'  '+e['predicted']['outcome'],fontsize=13);ax.set_xlabel('Time (s)')
    save(fig,5,'Local leak, rain and service challenge; assumed volume transfer/activation thresholds. Dry and disconnected remain indistinguishable.')
    fig,(ax,)=new('07  GUARD-5 comparison across uncertain collection assumptions')
    x=np.arange(3);regimes=list(summary['guard']);colors=['#64748b','#0284c7','#d97706']
    for j,m in enumerate(('pad','multizone','guard5')):
        fp=[summary['guard'][r][m]['fp'] for r in regimes];fn=[summary['guard'][r][m]['fn'] for r in regimes]
        ax.bar(x+(j-1)*.25,fp,.25,label=m+' false alarm',color=colors[j]);ax.bar(x+(j-1)*.25,fn,.25,bottom=fp,color=colors[j],alpha=.45,hatch='//',label=m+' missed')
    ax.set_xticks(x,regimes);ax.set_ylabel('Event count (false alarm + missed)');ax.legend(ncol=2,fontsize=11);save(fig,6,'Same water inputs; different declared transfer models. Hatched = missed. All GUARD-5 runs retain UNKNOWN electrical health.')
    fig,(ax,)=new('08  Simulated incident, intervention and independent verification')
    for k,event in enumerate(summary['integrated']):
        indices=[0,1,2,3,6,7,8];events=[event['events'][i] for i in indices];t=[v['time_s']/60 for v in events];ax.plot(t,[k]*len(t),'o-',label=event['case'])
        short=['Filling','Steady','Leak scenario','WATCH anomaly','Investigation','Repair','Verification']
        for x,text in zip(t,short):
            if k==2:ax.annotate(text,(x,k),xytext=(0,18),textcoords='offset points',rotation=35,fontsize=13,ha='left')
        ax.text(22,k-.22,'GUARD: '+event['guard5']['outcome']+'  |  EAR: '+event['acoustic']['outcome'],fontsize=11,ha='center')
    ax.set(xlabel='Simulated time (min)',xlim=(0,57),ylim=(-.7,3.1),yticks=range(3),yticklabels=[e['verification'].replace('_','\n') for e in summary['integrated']]);save(fig,7,'Separate engine outputs joined as a demonstration; no coupled fluid/acoustic model or real worker action. Missing post-data → NOT_VERIFIABLE.')
    from simulations.common import write_json,digest
    write_json(target/'captions.json',captions);write_json(target/'figure_traceability.json',{'source_hashes':{p.name:digest(json.loads(p.read_text())) for p in (out/'summary.json',out/'evaluation.json',out/'examples.json')},'figures':NAMES})

if __name__=='__main__':
    import sys
    render(Path(sys.argv[1]))
