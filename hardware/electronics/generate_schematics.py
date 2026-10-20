"""Generate self-contained KiCad 2023-format schematic DRAFTS and exact net CSV.

Native KiCad/ERC is a release gate. No PCB/production-readiness claim.
"""
import csv,json,uuid,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics'

def uid(name):return str(uuid.uuid5(uuid.NAMESPACE_URL,'HYDROOVERITY-M08/'+name))
def q(s):return json.dumps(str(s))
def component(ref,model,pins):return {'ref':ref,'model':model,'pins':{str(p):str(n) for p,n in pins.items()}}
def resistor(ref,value,a,b):return component(ref,value,{'1':a,'2':b})

def designs():
    d=json.loads((OUT/'interfaces.json').read_text('utf-8'));watch=[];wet=[];ear=[]
    watch.append(component('U1','ESP32-S3-DevKitC-1-N8R8',{'5V':'5V','3V3':'3V3','GND':'GND',**{'GPIO'+str(v):k for k,v in d['watch_gpio'].items()}}))
    for index,(address,channels) in enumerate(d['adc_map'].items(),1):
        pins={'1':'GND' if index==1 else '3V3','2':'ADC'+str(index)+'_ALERT_NC','3':'GND','8':'3V3','9':'I2C_SDA','10':'I2C_SCL'}
        pins.update({str(k+4):value for k,value in enumerate(channels.values())})
        watch.append(component('U'+str(index+1),'ADS1115IDGST '+address,pins))
        watch.append(resistor('C'+str(index),'100nF','3V3','GND'))
    for key,pull in [('I2C_SDA','R1'),('I2C_SCL','R2')]:watch.append(resistor(pull,'4.7k',key,'3V3'))
    for j,side in enumerate(('IN','OUT'),1):
        watch.append(component('JP'+str(j),'SEN0257 / lot pinout verify',{'1':'P_'+side+'_RAW','2':'5V','3':'GND'}))
        watch.extend([resistor('RP'+str(j)+'A','20k 0.1%','P_'+side+'_RAW','PRESSURE_'+side),resistor('RP'+str(j)+'B','20k 0.1%','PRESSURE_'+side,'GND'),resistor('CP'+str(j),'1uF','PRESSURE_'+side,'GND')])
        watch.append(component('JF'+str(j),'SEN0217 / lot pinout verify',{'1':'FLOW_'+side+'_RAW','2':'5V','3':'GND'}))
        watch.extend([resistor('RF'+str(j)+'A','47k','FLOW_'+side+'_RAW','FLOW_'+side+'_BASE'),resistor('RF'+str(j)+'B','10k','FLOW_'+side,'3V3'),resistor('RF'+str(j)+'C','10k','FLOW_'+side+'_RAW','5V'),resistor('RF'+str(j)+'D','100k','FLOW_'+side+'_BASE','GND')])
        watch.append(component('Q'+str(j),'2N3904 pinout candidate',{'1':'GND','2':'FLOW_'+side+'_BASE','3':'FLOW_'+side}))
    watch.append(component('JH','SHT31-DIS-B breakout',{'1':'3V3','2':'GND','3':'I2C_SDA','4':'I2C_SCL'}))
    watch.append(component('JT','DS18B20 externally powered',{'1':'GND','2':'DS18B20','3':'3V3'}));watch.append(resistor('RT','4.7k','DS18B20','3V3'))
    watch.extend([resistor('RV1','200k','3V3','V3V3_MONITOR'),resistor('RV2','100k','V3V3_MONITOR','GND')])
    watch.append(component('JPOWER','Protected regulated 5V input',{'1':'5V','2':'GND'}))
    watch.append(component('JW','Five-channel daughterboard',{'1':'PROBE_P','2':'PROBE_N','3':'GND',**{str(i+4):'COLLAR_'+name for i,name in enumerate(d['wetness']['channels'])},'9':'3V3'}))
    for i,name in enumerate(d['wetness']['channels'],1):
        eplus='E_'+name+'_PLUS';eminus='E_'+name+'_MINUS';adc='COLLAR_'+name
        wet.extend([resistor('R'+str(i)+'P','47k','PROBE_P',eplus),resistor('R'+str(i)+'N','47k',eminus,'PROBE_N'),resistor('R'+str(i)+'S','1k',eplus,adc),resistor('C'+str(i),'10nF',adc,'GND')])
        wet.append(component('JE'+str(i),'Electrode '+name+' insert',{'1':eplus,'2':eminus}))
        wet.append(resistor('REOL'+str(i),'100k DISTAL insert',eplus,eminus))
        wet.append(component('D'+str(i),'Low-leak clamp network / MPN and pinout gate',{'GND':'GND','SIG':adc,'VDD':'3V3'}))
    wet.append(component('JB','WATCH daughterboard link',watch[-1]['pins']))
    ear.append(component('U1','ESP32-S3-DevKitC-1-N8R8',{'5V':'5V','3V3':'3V3','GND':'GND',**{'GPIO'+str(v):k for k,v in d['ear_gpio'].items()}}))
    ear.append(component('U2','PCM1808PW',{'1':'PCM_VREF','2':'GND','3':'5V_ANALOG','4':'3V3','5':'GND','6':'MCLK_12M288','7':'I2S_WS_IN','8':'I2S_BCLK_IN','9':'I2S_DIN','10':'3V3','11':'3V3','12':'GND','13':'AUDIO_L_ADC','14':'AUDIO_R_ADC'}))
    ear.append(component('X1','12.288MHz3.3V CMOS / MPN gate',{'VDD':'3V3','GND':'GND','OUT':'MCLK_OSC','OE':'3V3'}));ear.append(resistor('RX','33R','MCLK_OSC','MCLK_12M288'))
    ear.extend([resistor('CREF','10uF','PCM_VREF','GND'),resistor('C5V','100nF','5V_ANALOG','GND'),resistor('C3V','100nF','3V3','GND'),resistor('CBULK','10uF','5V_ANALOG','GND'),resistor('RBIAS1','10k','5V_ANALOG','BIAS_2V5'),resistor('RBIAS2','10k','BIAS_2V5','GND'),resistor('CBIAS','100uF','BIAS_2V5','GND')])
    # One independent quad per channel, exactly matched topology and values.
    for ch in ('L','R'):
        n=lambda name:ch+'_'+name
        ear.append(component('J'+ch,'Shielded passive piezo input',{'1':n('PICKUP'),'2':'GND','SHIELD':'CHASSIS_STAR'}))
        ear.extend([resistor('RI'+ch,'1k',n('PICKUP'),n('IN_PROTECTED')),resistor('CI'+ch,'1uF',n('IN_PROTECTED'),n('IN_BIASED')),resistor('RB'+ch,'1M',n('IN_BIASED'),'BIAS_2V5')])
        ear.append(component('DI'+ch,'Low-leak transient clamp / capacitance and MPN gate',{'GND':'GND','SIG':n('IN_PROTECTED'),'VDD':'5V_ANALOG'}))
        pins={'1':n('BUFFER'),'2':n('BUFFER'),'3':n('IN_BIASED'),'4':'5V_ANALOG','5':n('BUFFER'),'6':n('GAIN_FB'),'7':n('GAIN'),'8':n('LP1_BUFFER'),'9':n('LP1_BUFFER'),'10':n('LP1'),'11':'GND','12':n('LP2'),'13':n('LP2_BUFFER'),'14':n('LP2_BUFFER')}
        ear.append(component('UA'+ch,'TLV9064IPWR',pins))
        ear.extend([resistor('RG'+ch,'10k',n('GAIN_FB'),'BIAS_2V5'),resistor('RF'+ch,'100k',n('GAIN'),n('GAIN_FB')),resistor('R1'+ch,'3.3k',n('GAIN'),n('LP1')),resistor('C1'+ch,'10nF',n('LP1'),'BIAS_2V5'),resistor('R2'+ch,'3.3k',n('LP1_BUFFER'),n('LP2')),resistor('C2'+ch,'10nF',n('LP2'),'BIAS_2V5'),resistor('CO'+ch,'1uF',n('LP2_BUFFER'),n('OUT_AC')),resistor('RO'+ch,'1k',n('OUT_AC'),'AUDIO_'+ch+'_ADC'),resistor('CU'+ch,'100nF','5V_ANALOG','GND')])
    ear.append(component('JSD','3.3V SPI microSD module',{'1':'3V3','2':'GND','3':'SD_SCK','4':'SD_MOSI','5':'SD_MISO','6':'SD_CS'}))
    ear.append(component('JPWR','Regulated filtered 5V inputs / board derives3V3',{'1':'5V_ANALOG','2':'5V','3':'GND'}))
    power=[component('J1','Certified isolated24V5A PSU',{'POS':'RAW24','NEG':'STAR_GND'}),
        resistor('F1','Master fuse / inrush rating gate','RAW24','FUSED24'),
        component('Q1','Reverse-polarity protection module / MPN gate',{'IN':'FUSED24','OUT':'PROTECTED24','GND':'STAR_GND'}),
        resistor('D1','TVS / clamp-energy-coordination gate','PROTECTED24','STAR_GND'),
        resistor('F2','Pump branch fuse / rating gate','PROTECTED24','PUMP_FUSED'),
        resistor('S1','Latching DC pump stop / DC contact rating gate','PUMP_FUSED','PUMP24'),
        component('JPUMP','SEAFLO SFDP2-012-035-21',{'POS':'PUMP24','NEG':'PUMP_RETURN'}),
        resistor('STAR','Dedicated pump return to supply star','PUMP_RETURN','STAR_GND'),
        resistor('F3','Electronics branch fuse / rating gate','PROTECTED24','ELEC24'),
        component('U1','Protected buck24V to5V3A / exact module gate',{'IN':'ELEC24','GND':'STAR_GND','OUT':'REG5'}),
        resistor('F4','WATCH branch protection','REG5','WATCH5'),
        resistor('F5','EAR branch protection','REG5','EAR5'),
        resistor('FB1','Analog rail ferrite / impedance-current gate','EAR5','EAR_ANALOG5'),
        resistor('C1','100uF / voltage-rating gate','EAR_ANALOG5','STAR_GND'),
        component('JW','WATCH JPOWER harness',{'1':'WATCH5','2':'STAR_GND'}),
        component('JE','EAR JPWR harness',{'1':'EAR_ANALOG5','2':'EAR5','3':'STAR_GND'})]
    return {'watch':watch,'wetness':wet,'ear':ear,'power':power}

def schematic(name,components):
    rootid=uid(name);lib=[];instances=[];wires=[];records=[]
    for i,c in enumerate(components):
        symbolid='M08:'+c['ref'];count=len(c['pins']);height=max(7.62,(count+1)*2.54)
        pins=[]
        x=22+(i%5)*79;y=25+(i//5)*55
        for k,(pin,net) in enumerate(c['pins'].items()):
            py=height/2-2.54*(k+1)
            pins.append(f'(pin passive line (at -12.7 {py:.3f} 0) (length 2.54) (name {q(pin)} (effects (font (size 1 1)))) (number {q(pin)} (effects (font (size 1 1)))))')
            a=(x-12.7,y-py);b=(x-17.78,y-py)
            wires.append(f'(wire (pts (xy {a[0]:.3f} {a[1]:.3f}) (xy {b[0]:.3f} {b[1]:.3f})) (stroke (width 0) (type default)) (uuid {q(uid(name+c["ref"]+pin+"wire"))}))')
            wires.append(f'(label {q(net)} (at {b[0]:.3f} {b[1]:.3f} 0) (effects (font (size .9 .9)) (justify left bottom)) (uuid {q(uid(name+c["ref"]+pin+"net"))}))')
            records.append({'sheet':name,'reference':c['ref'],'model':c['model'],'pin':pin,'net':net})
        lib.append(f'(symbol {q(symbolid)} (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" {q(c["ref"])} (at 0 {height/2+2:.3f} 0) (effects (font (size 1.27 1.27)))) (property "Value" {q(c["model"])} (at 0 {-height/2-2:.3f} 0) (effects (font (size 1 1)))) (symbol {q(c["ref"]+"_0_1")} (rectangle (start -10.16 {height/2:.3f}) (end 10.16 {-height/2:.3f}) (stroke (width .254) (type default)) (fill (type background)))) (symbol {q(c["ref"]+"_1_1")} {" ".join(pins)}))')
        instances.append(f'(symbol (lib_id {q(symbolid)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {q(uid(name+c["ref"]))}) (property "Reference" {q(c["ref"])} (at {x} {y-height/2-2:.3f} 0) (effects (font (size 1.27 1.27)))) (property "Value" {q(c["model"])} (at {x} {y+height/2+2:.3f} 0) (effects (font (size 1 1)))) (instances (project {q(name)} (path {q("/"+rootid)} (reference {q(c["ref"])}) (unit 1)))))')
    text=f'(kicad_sch (version 20230121) (generator "HYDROOVERITY_M08") (uuid {q(rootid)}) (paper "A1") (title_block (title {q("HYDROOVERITY "+name+" - DIGITAL DESIGN / NOT PHYSICALLY VALIDATED")}) (comment 1 "Draft module/component connectivity; native KiCad open/ERC not executed")) (lib_symbols {" ".join(lib)}) {" ".join(instances)} {" ".join(wires)})\n'
    (OUT/(name+'.kicad_sch')).write_text(text,encoding='utf-8',newline='\n')
    return records

def generate():
    sheets=designs();allrows=[]
    for name,parts in sheets.items():allrows+=schematic(name,parts)
    with (OUT/'connections.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=allrows[0].keys());w.writeheader();w.writerows(allrows)
    (OUT/'netlist.json').write_text(json.dumps({'status':'DRAFT DIGITAL DESIGN; native KiCad/ERC unavailable','sheets':sheets},indent=2)+'\n',encoding='utf-8')
    print('Generated',len(sheets),'self-contained KiCad draft schematics and',len(allrows),'exact pin/net connections.')
if __name__=='__main__':generate()
