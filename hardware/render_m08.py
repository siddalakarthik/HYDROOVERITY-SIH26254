"""Regenerate seven M08 engineering plates from JSON, netlists and BRep geometry.

No photographs, synthetic experimental results or native ERC claims are generated.
Run after mechanical-cad/guard5.py, using requirements-m08-cad.txt.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Wedge, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'hardware/results/ppt'
NAVY='#102b46'; BLUE='#266b98'; TEAL='#008c95'; GOLD='#d99b25'; RED='#b94c50'
COLORS={'A':'#1b998b','B':'#3877b5','C':'#b78728','EXT':'#9e5b9c','BYPASS':'#bb5960'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'svg.fonttype':'none'})

def read(path): return json.loads((ROOT/path).read_text('utf-8'))
def plate(title, subtitle):
    fig=plt.figure(figsize=(16,9),facecolor='#f5f8fc')
    fig.text(.045,.943,title,fontsize=24,weight='bold',color=NAVY)
    fig.text(.045,.902,subtitle,fontsize=12,color='#536b80')
    fig.text(.045,.031,'HYDROOVERITY | TARK | SIH26254',fontsize=10,color=NAVY)
    fig.text(.955,.031,'PROPOSED DESIGN / NOT PHYSICALLY TESTED',ha='right',fontsize=10,color=RED,weight='bold')
    return fig
def canvas(fig):
    ax=fig.add_axes([.04,.10,.92,.76]);ax.set(xlim=(-2,104),ylim=(-2,104));ax.axis('off');return ax
def node(ax,x,y,w,h,text,color=BLUE,size=13,zorder=1):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.5,rounding_size=1.4',facecolor='white',edgecolor=color,lw=2,zorder=zorder))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',color=NAVY,fontsize=size,zorder=max(3,zorder+1))
def arrow(ax,a,b,text='',color=BLUE):
    ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',lw=2,color=color))
    if text:ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+2,text,ha='center',color=color,fontsize=11)
def note(ax,x,y,s,size=12,color=NAVY):ax.text(x,y,s,va='top',fontsize=size,color=color,linespacing=1.55)

def cad_axis(fig,rect,parts,exploded=False,installed=False,cut=False):
    ax=fig.add_axes(rect,projection='3d',computed_zorder=False)
    ax.set_facecolor('#f5f8fc')
    for name,shape in parts.items():
        if cut and name.startswith('shell_'):continue
        vertices,triangles=shape.tessellate(.65,.18)
        v=np.array([[p.x,p.y,p.z] for p in vertices])
        shift=np.zeros(3)
        if exploded:
            if name=='shell_upper':shift[1]=45
            elif name=='shell_lower':shift[1]=-40
            elif name.startswith('probe_carrier'):shift[2]=-38
        v+=shift
        # Plot pipe axis horizontally: CAD Z -> plotted X; CAD X -> plotted Y.
        v=v[:,[2,0,1]]
        channel=next((k for k in COLORS if name.endswith('_'+k) or name.startswith(k+'_')),None)
        color=COLORS.get(channel,'#9daebc' if 'shell' in name else '#718fa2')
        mesh=Poly3DCollection(v[np.array(triangles)],facecolor=color,edgecolor='none',alpha=.38 if 'shell' in name and not exploded else 1,rasterized=False)
        ax.add_collection3d(mesh)
    if installed:
        z=np.linspace(-110,110,2);t=np.linspace(0,2*np.pi,48)
        Z,T=np.meshgrid(z,t);ax.plot_surface(Z,16*np.cos(T),16*np.sin(T),color='#ccd5de',alpha=.55)
    ax.set(xlim=(-115,95),ylim=(-65,75),zlim=(-100 if exploded else -65,100 if exploded else 65))
    ax.set_box_aspect((210,140,200 if exploded else 130));ax.view_init(elev=23,azim=-58);ax.axis('off')
    return ax

def generate():
    OUT.mkdir(parents=True,exist_ok=True)
    d=read('hardware/electronics/interfaces.json');p=read('hardware/guard5-collar/envelope.json');b=read('hardware/bom/m08_bom.json');rig=read('hardware/mechanical-cad/rig_layout.json')
    spec=importlib.util.spec_from_file_location('guard5',ROOT/'hardware/mechanical-cad/guard5.py');cad=importlib.util.module_from_spec(spec);spec.loader.exec_module(cad)
    parts,_=cad.build()
    figures=[]
    def save(fig,stem,caption,sources):
        fig.savefig(OUT/(stem+'.png'),dpi=160,facecolor=fig.get_facecolor())
        fig.savefig(OUT/(stem+'.svg'),facecolor=fig.get_facecolor())
        plt.close(fig)
        figures.append({'id':stem[:3],'stem':stem,'caption':caption,'assumptions':'Proposed digital design; no physical validation. See M08 engineering report for release gates.','sources':sources})

    fig=plate('H01  |  HYDROOVERITY engineering architecture','Observation → qualification → supported action; hardware and field validation remain pending')
    ax=canvas(fig)
    node(ax,1,61,27,27,'HYDRO-WATCH\n2 pressure + 2 bulk-flow\nSupply-state qualification',BLUE)
    node(ax,36,61,27,27,'GUARD-5\nProtected A / B / C\nIndependent EXT + BYPASS',TEAL)
    node(ax,71,61,27,27,'HYDRO-EAR\n2 contact pickups\nOne stereo sampling clock',GOLD)
    node(ax,21,24,58,23,'Evidence qualification\nProvenance • quality • faults • uncertainty\nInsufficient support → UNRESOLVED',NAVY)
    for x in (15,50,85):arrow(ax,(x,61),(50,47))
    node(ax,27,1,46,13,'HYDRO-VERIFY\nRepair and post-repair evidence',TEAL)
    arrow(ax,(50,24),(50,14))
    save(fig,'H01_architecture','Five frozen functional sections; evidence quality governs interpretation.',['hardware/electronics/interfaces.json','hardware/guard5-collar/envelope.json','docs/architecture/SYSTEM_ARCHITECTURE.md'])

    fig=plate('H02  |  GUARD-5 assembled and exploded CAD','CadQuery / OpenCascade BRep geometry; non-pressure-bearing external collar; dimensions in mm')
    cad_axis(fig,[.025,.19,.47,.66],parts,installed=True)
    cad_axis(fig,[.49,.19,.49,.66],parts,exploded=True)
    fig.text(.08,.82,'ASSEMBLED ON REFERENCE PIPE',color=NAVY,weight='bold',fontsize=13)
    fig.text(.58,.82,'EXPLODED / SERVICE ACCESS',color=NAVY,weight='bold',fontsize=13)
    fig.text(.07,.15,f'Pipe OD {p["pipe_od"]:g} • fitting envelope OD {p["fitting_od_max"]:g} × {p["fitting_length_max"]:g}\nShell OD {2*p["shell_outer_r"]:g} × {p["shell_length"]:g} • M4 clearance Ø{2*p["bolt_clearance_r"]:g}',fontsize=13,color=NAVY)
    fig.text(.57,.15,'Grey: split shell / drip guards\nTeal / blue / gold: A / B / C • purple: EXT • red: BYPASS\nSeparate probes, drains and external cable-tie lugs',fontsize=12,color=NAVY)
    save(fig,'H02_guard5_cad','Assembled and exploded solid-model views. Fastener access, tolerances and retention remain physical/detail-design gates.',['hardware/mechanical-cad/guard5.py','hardware/guard5-collar/envelope.json'])

    fig=plate('H03  |  GUARD-5 collection and service paths','Selected sectors leave coverage gaps; geometry does not establish collection efficiency or rain discrimination')
    ax=fig.add_axes([.045,.20,.40,.63]);ax.set_aspect('equal');ax.set(xlim=(-64,72),ylim=(-64,65));ax.axis('off')
    ax.add_patch(Circle((0,0),p['shell_outer_r'],fill=False,lw=2,color='#748da2'))
    ax.add_patch(Circle((0,0),p['fitting_od_max']/2,facecolor='#dbe4eb',edgecolor=NAVY))
    for ch,(a0,a1) in p['pockets'].items():
        ax.add_patch(Wedge((0,0),p['tray_outer_r'],a0,a1,width=p['tray_outer_r']-p['tray_inner_r'],facecolor=COLORS[ch],alpha=.7))
        t=np.deg2rad((a0+a1)/2);ax.text(29*np.cos(t),29*np.sin(t),ch,ha='center',va='center',color='white',weight='bold',fontsize=16)
    ax.add_patch(Rectangle((41,1),20,8,facecolor=COLORS['EXT']));ax.text(51,16,'EXT',ha='center',color=COLORS['EXT'],weight='bold')
    ax.add_patch(Rectangle((-12,-53),24,8,facecolor=COLORS['BYPASS']));ax.text(0,-61,'BYPASS',ha='center',color=COLORS['BYPASS'],weight='bold')
    for x in (28,-28,0):
        start=9 if x else -27;ax.annotate('',xy=(x,-44),xytext=(x,start),arrowprops=dict(arrowstyle='->',color=TEAL,lw=2,ls='--'))
    ax.text(-62,62,'RADIAL LAYOUT\nProjection of drains at Z=30',fontsize=11,color=NAVY)
    ax.annotate('gravity',xy=(62,-34),xytext=(62,-5),ha='center',arrowprops=dict(arrowstyle='->',color=NAVY),fontsize=11)
    ax2=fig.add_axes([.51,.47,.44,.34]);ax2.set_aspect('equal');ax2.set(xlim=(-65,65),ylim=(-53,47));ax2.axis('off')
    # Actual longitudinal material slice from BRep, projected to Z/Y.
    slice_box=cad.box(.15,130,140,(0,0,0))
    for name,shape in parts.items():
        section=shape.intersect(slice_box)
        if section.Volume()<1e-6:continue
        vertices,triangles=section.tessellate(.5,.2)
        vv=np.array([[v.z,v.y] for v in vertices])
        from matplotlib.collections import PolyCollection
        ax2.add_collection(PolyCollection(vv[np.array(triangles)],facecolor=COLORS.get('C') if name=='pocket_C' else '#9cafbf',edgecolor='none'))
    ax2.add_patch(Rectangle((-30,-22.5),60,45,facecolor='#dbe4eb',edgecolor=NAVY,alpha=.7))
    ax2.text(-64,43,'LONGITUDINAL BRep SLICE AT X=0',fontsize=11,color=NAVY)
    ax2.annotate('BYPASS slot → witness',xy=(0,-42),xytext=(8,-25),fontsize=10,arrowprops=dict(arrowstyle='->'))
    fig.text(.52,.36,'WATER / SERVICE INTENT',color=NAVY,weight='bold',fontsize=14)
    fig.text(.52,.19,'A/B/C: separate inward entries → electrode region → own tube\nEXT: outside exposure witness; no normal drain enters it\nBYPASS: bottom escape path at Z=0; drains exit at Z=30\nØ3 axial challenge ports offset 15° from each probe carrier\nWeak wetting, blockage, cross-migration and orientation remain risks',fontsize=12,linespacing=1.6,color=NAVY)
    save(fig,'H03_guard5_cutaway','Radial layout plus actual longitudinal BRep slice; arrows show intended gravity paths, not simulated fluid flow.',['hardware/mechanical-cad/guard5.py','hardware/guard5-collar/envelope.json'])

    fig=plate('H04  |  HYDRO-WATCH electrical interfaces','3.3 V logic / ADC; separate 5 V sensors; editable connectivity drafts and exact pin/net ledger supplied')
    ax=canvas(fig)
    node(ax,1,70,26,23,'2 × SEN0257 pressure\n5 V; 0.5–4.5 V output\n20k / 20k → 0.25–2.25 V',BLUE,12)
    node(ax,1,39,26,23,'Five wetness inserts\nA / B / C / EXT / BYPASS\n47k each leg + distal 100k',TEAL,12)
    node(ax,36,48,27,36,'2 × ADS1115, 3.3 V\n0x48: P-in / P-out / A / B\n0x49: C / EXT / BYPASS / rail\n±4.096 V PGA ≠ input rating',BLUE,12)
    node(ax,73,48,26,36,'ESP32-S3 N8R8\nSDA GPIO8 / SCL GPIO9\nFlow GPIO4 / GPIO5\nProbe drive GPIO12 / 13',NAVY,12)
    arrow(ax,(27,80),(36,75));arrow(ax,(27,51),(36,60));arrow(ax,(63,67),(73,67),'I²C')
    node(ax,1,8,26,22,'2 × bulk flow pulses\n5 V interface → NPN translator\nNot a small-leak reference',GOLD,12)
    # Route translated flow pulses around the context-sensor box, not across its label.
    ax.plot([27,30,30,78],[19,19,41,41],color=BLUE,lw=2)
    arrow(ax,(78,41),(78,48))
    node(ax,36,8,27,22,'SHT31: 3.3 V I²C\nDS18B20: powered 3.3 V\nContext, not wetness channels',TEAL,12)
    arrow(ax,(63,19),(85,48))
    node(ax,73,8,26,22,'24 V isolated supply\nProtected buck → 5 V\nBoard regulator → 3.3 V',RED,12)
    note(ax,2,101,'Dry ≠ healthy electrode. EOL observes a circuit path; wet cable, fouling and faults can remain ambiguous.',11)
    save(fig,'H04_watch_electronics','WATCH channel capacity and voltage translation; protection MPNs, sensor lot pinout and native ERC remain gates.',['hardware/electronics/interfaces.json','hardware/electronics/netlist.json','hardware/electronics/generate_schematics.py'])

    a=d['acoustic']; rate=a['sample_rate_hz'];stream=rate*a['channels']*a['slot_bits']//8
    fig=plate('H05  |  HYDRO-EAR: one physical sampling clock','Two matched contact channels → one PCM1808 stereo ADC → ESP32-S3 I²S receive slave')
    ax=canvas(fig)
    for y,ch in ((72,'L'),(44,'R')):
        node(ax,0,y,18,19,f'Pickup {ch}\nPassive piezo\nMatched mount',TEAL,12)
        node(ax,25,y,27,19,'1 MΩ input bias / follower\nGain 11, bias 2.5 V\n2 × buffered RC, fc ≈ 4.82 kHz',BLUE,11)
        arrow(ax,(18,y+9),(25,y+9));arrow(ax,(52,y+9),(59,y+9))
    node(ax,59,43,19,49,'PCM1808PW\n5 V analog\n3.3 V logic\nMD1=MD0=1\nFMT=0 (I²S)',GOLD,12)
    node(ax,84,43,16,49,'ESP32-S3\nRX slave\nGPIO15 BCLK\nGPIO16 WS\nGPIO17 DIN',NAVY,11)
    arrow(ax,(78,65),(84,65))
    node(ax,25,13,28,17,'12.288 MHz CMOS oscillator\n3.3 V → SCKI (one clock)',RED,12)
    arrow(ax,(53,21),(66,43))
    note(ax,61,29,f'48,000 stereo frames/s\n24 valid bits / 32-bit slots\n{stream:,} bytes/s; 10 s = {stream*10/1e6:.2f} MB\n64 KiB buffer ≈ {65536/stream*1000:.1f} ms',12)
    note(ax,0,34,'CLOCK RELATIONSHIPS\nMCLK 12.288 MHz = 256 fs\nBCLK 3.072 MHz = 64 fs\nLRCLK 48 kHz = 1 fs',12)
    save(fig,'H05_ear_shared_clock','Clock ratios are derived from selected PCM1808 master mode; board straps, jitter, alias rejection and uninterrupted SD capture need validation.',['hardware/electronics/interfaces.json','hardware/electronics/ear.kicad_sch','hardware/acoustic-acquisition/acquisition.schema.json'])

    fig=plate('H06  |  Proposed 12 m laboratory demonstrator','Low-voltage contained loop; separate from the much larger M05 EPANET simulation network')
    ax=canvas(fig)
    node(ax,0,42,15,27,f'{rig["reservoir_l"]} L vented\nreservoir\nCatch containment',TEAL,12)
    node(ax,22,48,14,17,'Strainer\n24 V pump',BLUE,12)
    arrow(ax,(15,56),(22,56));arrow(ax,(36,56),(43,56))
    ax.plot([43,97],[56,56],color=BLUE,lw=5)
    for m in rig['leak_stations_m']:
        x=43+54*m/12;ax.plot(x,56,'o',ms=11,color=GOLD)
        note(ax,x+1,49,f'{m} m\nLeak station',10)
        arrow(ax,(x,54),(x,31),color=TEAL)
    node(ax,51,13,39,16,'Contained leak cups → balance + timer\n0.01 g display resolution ≠ accuracy',TEAL,11)
    for m in rig['acoustic_endpoints_m']:
        x=43+54*m/12;node(ax,x-3,70,9,12,'EAR '+('L' if m==0 else 'R'),TEAL,10);arrow(ax,(x+1,70),(x,58))
    note(ax,66,93,'12 m span + 12 m return; GUARD-5 at 6 m\nPressure / bulk flow at supply and return',12)
    arrow(ax,(97,56),(97,5));arrow(ax,(97,5),(-1,5));arrow(ax,(-1,5),(-1,45));arrow(ax,(-1,45),(0,45))
    ax.plot([39,39,18,18,7,7],[56,93,93,76,76,69],color=RED,lw=2)
    node(ax,23,88,12,9,'Relief',RED,10,zorder=3)
    ax.plot([37,37,20,20,13,13],[56,80,80,72,72,69],color=GOLD,lw=2)
    node(ax,25,75,10,9,'Bypass',GOLD,10,zorder=3)
    note(ax,1,106,'Unisolatable relief + adjustable bypass → reservoir\nNo operating pressure approved; component-rating / relief-flow gate',11,RED)
    note(ax,1,35,'Dry electrical zone:\nCertified isolated 24 V PSU\nDC stop / fuses / strain relief\nQualified mains connection',11)
    save(fig,'H06_test_rig','Conceptual P&ID and positioning; 0.5/1.0/1.5 bar are contingent future points, not authorized conditions.',['hardware/mechanical-cad/rig_layout.json','hardware/bom/m08_bom.json'])

    fig=plate('H07  |  Hardware budget and engineering readiness','All prices are engineering estimates in INR; no verified supplier quotations or purchases')
    groups={}
    for item in b['items']:groups[item['group']]=groups.get(item['group'],0)+item['extended_cost_inr']
    groups['Contingency']=b['contingency_inr']
    ax=fig.add_axes([.09,.22,.44,.58]);keys=list(groups);vals=list(groups.values())
    bars=ax.barh(keys,vals,color=[TEAL if k!='Contingency' else GOLD for k in keys]);ax.invert_yaxis();ax.set_xlim(0,max(vals)*1.25);ax.set_xlabel('INR (estimated)');ax.spines[['top','right','left']].set_visible(False)
    ax.bar_label(bars,labels=[f'₹{v:,}' for v in vals],padding=5,fontsize=12)
    fig.text(.60,.74,f'₹{b["grand_total_inr"]:,}',fontsize=38,color=NAVY,weight='bold')
    fig.text(.60,.65,f'Components ₹{b["component_total_inr"]:,} + reserve ₹{b["contingency_inr"]:,}\nCeiling ₹{b["cap_inr"]:,} • remaining ₹{b["headroom_inr"]:,}',fontsize=15,color=NAVY,linespacing=1.7)
    fig.text(.60,.39,'READY FOR ENGINEERING REVIEW\nParametric CAD + STEP checks\nEditable circuit connectivity drafts\nPower / clocks / calibration / rig plans\n\nGATES: quotations, real fit, native ERC,\npressure ratings and all physical tests',fontsize=14,color=NAVY,linespacing=1.65)
    fig.text(.09,.12,f'Previous allocation ₹56,750 → revised ₹{b["grand_total_inr"]:,} (+₹{b["grand_total_inr"]-b["previous_allocation_inr"]:,}). Tax / shipping must fit reserve and headroom.',fontsize=12,color=RED)
    save(fig,'H07_budget','Complete materials estimate reconciles previous allocation; narrow residual margin is a procurement risk, not proof of affordability.',['hardware/bom/m08_bom.json','hardware/electronics/interfaces.json'])
    # Supplementary timing detail: one I2S stereo frame, measured in BCLK periods.
    details=OUT.parent/'details';details.mkdir(exist_ok=True)
    fig=plate('EAR timing detail  |  PCM1808 master / ESP32-S3 receive slave','Ideal I²S framing intent, not a measured oscilloscope capture; one physical oscillator clocks both channels')
    ax=fig.add_axes([.10,.24,.83,.53]);ax.set(xlim=(0,64),ylim=(-.7,3.5),xlabel='BCLK periods within one stereo frame (64 total)',yticks=[0,1.4,2.8],yticklabels=['DOUT','LRCLK / WS','BCLK'])
    t=np.arange(0,64.01,.5);ax.step(t,2.8+.35*(np.arange(len(t))%2),where='post',color=BLUE)
    ax.step([0,32,64],[1.4,1.75,1.4],where='post',color=TEAL,lw=2)
    ax.add_patch(Rectangle((1,-.15),24,.4,color=BLUE,alpha=.3));ax.add_patch(Rectangle((33,-.15),24,.4,color=GOLD,alpha=.5))
    ax.text(13,.4,'LEFT: 24 valid bits',ha='center',fontsize=13);ax.text(45,.4,'RIGHT: 24 valid bits',ha='center',fontsize=13)
    ax.text(29,-.4,'padding',ha='center',fontsize=11);ax.text(61,-.4,'padding',ha='center',fontsize=11)
    ax.text(3,2.1,'I²S payload begins one BCLK after WS transition',fontsize=13,color=NAVY)
    ax.spines[['top','right']].set_visible(False);fig.text(.10,.13,'MCLK 12.288 MHz = 256fs → BCLK 3.072 MHz = 64fs → LRCLK 48 kHz. Verify edges, bit alignment, polarity and channel order on actual boards.',fontsize=12,color=NAVY)
    for ext in ('png','svg'):fig.savefig(details/('ear_clock_timing.'+ext),dpi=160,facecolor=fig.get_facecolor())
    plt.close(fig)
    source_names=sorted({s for f in figures for s in f['sources']}|{'hardware/render_m08.py'})
    manifest={'status':'DIGITAL DESIGN / NOT PHYSICALLY VALIDATED','canvas_pixels':[2560,1440],'figures':figures,'supplementary':['hardware/results/details/ear_clock_timing.png','hardware/results/details/ear_clock_timing.svg'],'source_sha256':{s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in source_names}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (OUT/'CAPTIONS.md').write_text('# M08 proposed digital figures\n\n'+ '\n\n'.join(f'**{f["stem"]}** — {f["caption"]}\n\n{f["assumptions"]}' for f in figures)+'\n',encoding='utf-8')
    print('Rendered',len(figures),'plates as 2560×1440 PNG and editable SVG.')

if __name__=='__main__':generate()
