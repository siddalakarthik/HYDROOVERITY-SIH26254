"""M08 digital consistency checks; does not replace CAD, ERC or physical tests."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import struct

ROOT=Path(__file__).resolve().parents[1]
def load(name):return json.loads((ROOT/name).read_text('utf-8'))

def check_data(d,b,p,rig):
    assert d['wetness']['channels']==['A','B','C','EXT','BYPASS'],'five separate wetness channels'
    assert len(d['adc_map'])==2 and all(len(v)==4 for v in d['adc_map'].values()),'ADC capacity'
    channels=[v for m in d['adc_map'].values() for v in m.values()]
    assert len(set(channels))==8 and all('COLLAR_'+x in channels for x in d['wetness']['channels']),'ADC assignment'
    for bank in ('watch_gpio','ear_gpio'):
        pins=list(d[bank].values())
        assert len(pins)==len(set(pins)),'GPIO collision'
        assert not set(pins)&{0,3,19,20,35,36,37,45,46},'boot/USB/PSRAM pin reservation'
    assert len(set(d['i2c_addresses'].values()))==3,'I2C collision'
    pressure=d['pressure'];ratio=pressure['divider_bottom_ohm']/(pressure['divider_top_ohm']+pressure['divider_bottom_ohm'])
    assert max(pressure['output_range_v']+[5])*ratio<d['rails']['logic'],'pressure input overvoltage'
    assert pressure['filter_c_f']==1e-6,'pressure schematic capacitor consistency'
    a=d['acoustic']
    assert a['clock_hz']==a['mclk_ratio']*a['sample_rate_hz']==12288000,'shared sample clock'
    assert a['sample_rate_hz']*a['bclk_ratio']==3072000 and (a['md1'],a['md0'],a['fmt'])==(1,1,0),'PCM clock mode'
    assert a['channels']==2 and a['slot_bits']==32 and a['sample_bits']==24,'stereo format'
    assert a['mcu_mode']=='I2S standard RX slave; MCU MCLK disabled','RX clock ownership'
    assert math.isclose(5*(d['power_budget']['watch_5v_peak_a']+d['power_budget']['ear_5v_peak_a']),d['power_budget']['combined_5v_w']),'power allowance'
    ids=[x['id'] for x in b['items']];assert len(ids)==len(set(ids)),'duplicate BOM line'
    for item in b['items']:
        assert item['quantity']>0 and item['unit_cost_inr']>=0
        assert item['quantity']*item['unit_cost_inr']==item['extended_cost_inr'],'BOM multiplication'
        assert item['price_status']=='ESTIMATED_NOT_QUOTED' and item['supplier_url'] is None,'no fabricated verified prices'
        assert item['currency']=='INR' and item['necessity']=='ESSENTIAL'
    total=sum(x['extended_cost_inr'] for x in b['items'])
    assert total==b['component_total_inr'] and total+b['contingency_inr']==b['grand_total_inr'],'BOM sum'
    assert b['headroom_inr']==b['cap_inr']-b['grand_total_inr']>=0,'budget cap'
    assert {'PIPE','PUMP','TANK','RELIEF','FRAME','PROBE','COLLAR','MCU','ADC','PRESSURE','FLOW','SHT','TEMP','PICKUP','OPAMP','PCM','CLOCK','SD','PSU','BUCK','ESTOP','SCALE','LEAK','CABLE'}<=set(ids),'BOM subsystem coverage'
    assert p['pipe_od']==rig['pipe_od_mm'] and p['end_bore_r']>p['pipe_od']/2,'pipe clearance'
    assert p['tray_inner_r']>p['fitting_od_max']/2 and p['shell_inner_r']>p['tray_outer_r'],'collector clearance'
    assert p['bolt_clearance_r']*2>p['bolt_diameter'] and p['gravity']==[0,-1,0],'fastener/gravity'
    assert rig['pressure_authorized'] is False and sum(rig['sections_m'])==rig['straight_span_m']==12,'rig authorization/span'
    pipe=next(x for x in b['items'] if x['id']=='PIPE')
    assert pipe['quantity']>=rig['straight_span_m']+rig['supply_return_additional_m'],'full return pipe allowance'
    assert rig['supply_return_additional_m']>=rig['straight_span_m'],'straight rig return length'
    assert len(rig['leak_stations_m'])>=2 and next(x for x in b['items'] if x['id']=='LEAK')['quantity']==len(rig['leak_stations_m']),'multiple controlled stations'

def parse_sexpr(text):
    """Structural parser only: no KiCad semantic/ERC claim."""
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text)
    stack=[];root=None
    for token in tokens:
        if token=='(':
            node=[]
            if stack:stack[-1].append(node)
            elif root is not None:raise AssertionError('multiple schematic roots')
            else:root=node
            stack.append(node)
        elif token==')':
            assert stack,'unexpected closing parenthesis'
            stack.pop()
        else:
            assert stack,'token outside schematic'
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    assert root and not stack,'incomplete schematic'
    return root

def verify_artifacts():
    manifest=load('hardware/results/ppt/manifest.json')
    assert len(manifest['figures'])==7
    for name,expected in manifest['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,'stale figure source: '+name
    for f in manifest['figures']:
        png=ROOT/'hardware/results/ppt'/(f['stem']+'.png');svg=png.with_suffix('.svg')
        assert struct.unpack('>II',png.read_bytes()[16:24])==(2560,1440),'figure dimensions'
        assert 'PROPOSED DESIGN / NOT PHYSICALLY TESTED' in svg.read_text('utf-8'),'figure caveat'
    r=load('hardware/mechanical-cad/exports/geometry_checks.json')
    assert len(r['parts'])==25 and not r['pair_interferences']
    assert max(r['pipe_fitting_intersection_mm3'].values())<1e-4
    assert all(v['valid'] and v['solids']==1 for v in r['parts'].values())

def run(artifacts=False):
    d=load('hardware/electronics/interfaces.json');b=load('hardware/bom/m08_bom.json')
    check_data(d,b,load('hardware/guard5-collar/envelope.json'),load('hardware/mechanical-cad/rig_layout.json'))
    bomrows=list(csv.DictReader((ROOT/'hardware/bom/m08_bom.csv').open(encoding='utf-8')))
    assert len(bomrows)==len(b['items'])
    table=(ROOT/'hardware/bom/M08_BOM.md').read_text('utf-8')
    for row,item in zip(bomrows,b['items']):
        assert all(row[k]==('' if v is None else str(v)) for k,v in item.items()),'BOM CSV drift'
        assert f"| {item['id']} | {item['model']} | {item['quantity']} {item['unit']} | {item['unit_cost_inr']:,} | {item['extended_cost_inr']:,} |" in table,'BOM table drift'
    n=load('hardware/electronics/netlist.json')['sheets']
    csvrows=list(csv.DictReader((ROOT/'hardware/electronics/connections.csv').open(encoding='utf-8')))
    expected=[{'sheet':s,'reference':c['ref'],'model':c['model'],'pin':p,'net':net} for s,cc in n.items() for c in cc for p,net in c['pins'].items()]
    assert csvrows==expected,'CSV / netlist drift'
    for sheet,parts in n.items():
        tree=parse_sexpr((ROOT/f'hardware/electronics/{sheet}.kicad_sch').read_text('utf-8'))
        assert tree[0]=='kicad_sch'
        instances=[x for x in tree if isinstance(x,list) and x and x[0]=='symbol']
        assert len(instances)==len(parts),'schematic component count'
        labels=[x[1] for x in tree if isinstance(x,list) and x and x[0]=='label']
        assert sorted(labels)==sorted(c['net'] for c in csvrows if c['sheet']==sheet),'schematic label ledger'
    # Exact package pin map checks for selected converter devices.
    watch={x['ref']:x for x in n['watch']};ear={x['ref']:x for x in n['ear']}
    for ref,address in (('U2','0x48'),('U3','0x49')):
        pins=watch[ref]['pins']
        assert pins['8']=='3V3' and pins['3']=='GND' and pins['9']=='I2C_SDA' and pins['10']=='I2C_SCL'
        assert [pins[str(i)] for i in range(4,8)]==list(d['adc_map'][address].values())
    assert watch['JW']['pins']==next(x for x in n['wetness'] if x['ref']=='JB')['pins']
    assert watch['JW']['pins']['9']=='3V3','daughterboard clamp rail'
    assert ear['U2']['pins']=={'1':'PCM_VREF','2':'GND','3':'5V_ANALOG','4':'3V3','5':'GND','6':'MCLK_12M288','7':'I2S_WS_IN','8':'I2S_BCLK_IN','9':'I2S_DIN','10':'3V3','11':'3V3','12':'GND','13':'AUDIO_L_ADC','14':'AUDIO_R_ADC'}
    schemas=load('docs/architecture/openapi-design.json')['components']['schemas']
    observation=schemas['ObservationInput']
    assert observation['additionalProperties'] is False and set(observation['required'])=={'event_id','channel_id','collection_time','unit','value','device_configuration_id','quality'}
    for name in ('hardware/calibration/VALIDATION_PLAN.md','hardware/firmware/INTERFACE_READINESS.md','docs/engineering/M08_DIGITAL_HARDWARE_REPORT.md'):
        assert 'DIGITAL DESIGN / NOT PHYSICALLY VALIDATED' in (ROOT/name).read_text('utf-8')
    if artifacts:verify_artifacts()
    return {'bom_inr':b['grand_total_inr'],'headroom_inr':b['headroom_inr'],'schematic_drafts':len(n),'pin_net_connections':len(csvrows),'artifacts_checked':artifacts,'native_erc':'UNAVAILABLE','physical_tests':'NOT PERFORMED'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--artifacts',action='store_true');args=parser.parse_args()
    print(json.dumps(run(args.artifacts),indent=2))
