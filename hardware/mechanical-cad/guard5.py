"""Parametric CadQuery source, millimetres. Non-pressure-bearing hypothesis only."""
import json,math,itertools
from pathlib import Path
import cadquery as cq

ROOT=Path(__file__).resolve().parents[2]
CONFIG=ROOT/'hardware/guard5-collar/envelope.json'

def box(x,y,z,center):
    return cq.Workplane('XY').box(x,y,z).translate(center).val()
def cylinder(radius,length,start,direction=(0,0,1)):
    return cq.Solid.makeCylinder(radius,length,cq.Vector(*start),cq.Vector(*direction))
def annulus(ro,ri,length,z=0):
    return cq.Workplane('XY').circle(ro).circle(ri).extrude(length).translate((0,0,z-length/2)).val()
def sector(ro,ri,a,b,length):
    def point(t):return (100*math.cos(math.radians(t)),100*math.sin(math.radians(t)))
    wedge=cq.Workplane('XY').polyline([(0,0),point(a),point((a+b)/2),point(b)]).close().extrude(length+2).translate((0,0,-length/2-1)).val()
    return annulus(ro,ri,length).intersect(wedge)
def radial_box(radial,tangential,length,r,theta,z):
    return box(radial,tangential,length,(r,0,z)).rotate((0,0,0),(0,0,1),theta)

def build(p=None):
    p=p or json.loads(CONFIG.read_text('utf-8'));parts={};ports=[]
    ro,ri,L=p['shell_outer_r'],p['shell_inner_r'],p['shell_length']
    shell=annulus(ro,ri,L)
    for z in (-L/2+p['end_lip_thickness']/2,L/2-p['end_lip_thickness']/2):
        shell=shell.fuse(annulus(ro,p['end_bore_r'],p['end_lip_thickness'],z))
    for z in (-46,46):shell=shell.fuse(annulus(ro+3,ro-.5,5,z))
    # Open tie slots: cable bundles stay outside the collectors and the pressure pipe.
    for x in (-41,41):
        lug=box(10,8,12,(x,12,-20)).cut(box(3,10,6,(x,12,-20)))
        shell=shell.fuse(lug)
    # External witness shelf meets the tray bottom; screw/strap choice remains a fit gate.
    shell=shell.fuse(box(14,3,18,(41,-.5,0)))
    # BYPASS support is at its back (Z), leaving its upward mouth and drain slot open.
    shell=shell.fuse(box(24,15,3,(0,-42,-13.5)))
    for x in (-p['bolt_x'],p['bolt_x']):
        for z in (-p['bolt_z'],p['bolt_z']):
            for y in (-2.8,2.8):shell=shell.fuse(box(22,5,14,(x,y,z)))
            shell=shell.cut(cylinder(p['bolt_clearance_r'],30,(x,-15,z),(0,1,0)))
    # Three independent gravity drain tubes. No normal drain empties into BYPASS.
    drains=[]
    for channel,x,top in [('A',p['drain_x'],9.),('B',-p['drain_x'],9.),('C',0.,-27.)]:
        start=(x,p['drain_bottom_y'],p['drain_z']);length=top-p['drain_bottom_y']
        hole=cylinder(p['drain_bore_r'],length+3,start,(0,1,0));shell=shell.cut(hole);drains.append(hole)
        tube=cylinder(p['drain_tube_od']/2,length,start,(0,1,0)).cut(cylinder(p['drain_tube_id']/2,length,start,(0,1,0)))
        parts['drain_'+channel]=tube
        ports.append({'channel':channel,'outlet':list(start),'gravity_down_y':True,'bore_mm':p['drain_tube_id']})
    for name,(a,b) in p['pockets'].items():
        theta=(a+b)/2;r=(p['tray_inner_r']+p['tray_outer_r'])/2
        tray=sector(p['tray_outer_r'],p['tray_inner_r'],a,b,p['tray_length'])
        cavity=sector(p['tray_outer_r']-p['tray_wall'],p['tray_inner_r']+p['tray_wall'],a+2,b-2,p['tray_length']-3)
        tray=tray.cut(cavity)
        # Inward-facing inlet window, isolated end walls and removable axial probe carrier.
        tray=tray.cut(sector(p['tray_inner_r']+2,p['tray_inner_r']-1,a+3,b-3,50))
        tray=tray.cut(radial_box(6.6,5.0,15,r,theta,-32.5))
        for hole in drains:tray=tray.cut(hole)
        # Offset challenge from electrode carrier; injecting along its centre would be blocked.
        challenge_theta=theta+15
        xy=(r*math.cos(math.radians(challenge_theta)),r*math.sin(math.radians(challenge_theta)))
        challenge=cylinder(p['challenge_bore_diameter']/2,35,(xy[0],xy[1],-60))
        shell=shell.cut(challenge);tray=tray.cut(challenge)
        parts['pocket_'+name]=tray
        carrier=radial_box(6.,4.4,10,r,theta,-31)
        # Two separate metal strips flush with the inward face; no sixth channel.
        for index,tangent in enumerate((-1.2,1.2),1):
            electrode=box(p['electrode_thickness'],1.,6,(r-3+p['electrode_thickness']/2,tangent,-31)).rotate((0,0,0),(0,0,1),theta)
            socket=box(p['electrode_thickness']+.2,1.2,6.2,(r-3+p['electrode_thickness']/2,tangent,-31)).rotate((0,0,0),(0,0,1),theta)
            carrier=carrier.cut(socket);parts['electrode_'+name+'_'+str(index)]=electrode
        parts['probe_carrier_'+name]=carrier
    # Uncollected water exits a separate bottom slot into the independent BYPASS witness.
    shell=shell.cut(box(12,22,10,(0,-37,0)))
    gap=p['split_gap']/2
    parts['shell_upper']=shell.intersect(box(200,100,200,(0,50+gap,0)))
    parts['shell_lower']=shell.intersect(box(200,100,200,(0,-50-gap,0)))
    def tray(x,y,z,width):
        return box(width,8,24,(x,y,z)).cut(box(width-3,8,21,(x,y+1.5,z)))
    parts['EXT_witness']=tray(51,5,0,20)
    parts['BYPASS_witness']=tray(0,-49,0,24)
    parts['probe_carrier_EXT']=box(6,1,10,(51,3,0))
    parts['probe_carrier_BYPASS']=box(6,1,10,(0,-50,0))
    for name,x,y in [('EXT',51,3),('BYPASS',0,-50)]:
        for index,dx in enumerate((-1.5,1.5),1):
            strip=box(1,p['electrode_thickness'],6,(x+dx,y+.5,0))
            socket=box(1.2,p['electrode_thickness']+.2,6.2,(x+dx,y+.5,0))
            parts['probe_carrier_'+name]=parts['probe_carrier_'+name].cut(socket)
            parts['electrode_'+name+'_'+str(index)]=strip
    return parts,ports

def export_and_check(out=None):
    out=Path(out) if out else ROOT/'hardware/mechanical-cad/exports';out.mkdir(parents=True,exist_ok=True)
    p=json.loads(CONFIG.read_text('utf-8'));parts,ports=build(p);records={}
    for name,shape in parts.items():
        assert shape.isValid() and shape.Volume()>0,name
        path=out/(name+'.step');cq.exporters.export(shape,str(path))
        imported=cq.importers.importStep(str(path)).val()
        # STEP healing can perturb tiny boolean edges. This numerical audit tolerance
        # is not a manufacturing tolerance: <=0.002% volume AND <=0.001 mm bbox.
        err=abs(imported.Volume()-shape.Volume())
        bb=shape.BoundingBox();ib=imported.BoundingBox()
        bbox_error=max(abs(getattr(bb,k)-getattr(ib,k)) for k in ('xmin','xmax','ymin','ymax','zmin','zmax'))
        assert imported.isValid() and len(imported.Solids())==len(shape.Solids()) and err<max(1e-5,shape.Volume()*2e-5) and bbox_error<.001,name
        records[name]={'volume_mm3':shape.Volume(),'bbox_mm':[bb.xlen,bb.ylen,bb.zlen],'solids':len(shape.Solids()),'valid':True,'step_roundtrip_volume_error_mm3':err,'step_roundtrip_bbox_error_mm':bbox_error}
    cq.exporters.export(cq.Compound.makeCompound(list(parts.values())),str(out/'GUARD5_assembly.step'))
    # Reference pipe/fitting envelope is not a manufactured pressure part.
    reference=cylinder(p['pipe_od']/2,180,(0,0,-90)).fuse(cylinder(p['fitting_od_max']/2,p['fitting_length_max'],(0,0,-p['fitting_length_max']/2)))
    collisions={name:shape.intersect(reference).Volume() for name,shape in parts.items()}
    assert max(collisions.values())<1e-4,collisions
    interference=[]
    for (a,sa),(b,sb) in itertools.combinations(parts.items(),2):
        v=sa.intersect(sb).Volume()
        if v>1e-4:interference.append({'a':a,'b':b,'volume_mm3':v})
    assert not interference,interference
    # M4 driver access envelope, not a strength or torque check.
    for x in (-p['bolt_x'],p['bolt_x']):
        for z in (-p['bolt_z'],p['bolt_z']):
            driver=cylinder(4,25,(x,5.31,z),(0,1,0))
            assert all(s.intersect(driver).Volume()<1e-4 for s in parts.values()),'driver access'
    # Remove external witnesses, loose tubes and cable ties before separating halves.
    keep={k:s for k,s in parts.items() if k.startswith(('pocket_','probe_carrier_')) and not k.endswith(('EXT','BYPASS'))}
    for name,direction in [('shell_upper',1),('shell_lower',-1)]:
        for distance in (1,5,15,30,60):
            moving=parts[name].translate((0,direction*distance,0))
            assert all(moving.intersect(s).Volume()<1e-4 for s in keep.values()),('opening clearance',name,distance)
    # Analytic bore continuity through each separate tube, including an open lower end.
    for port in ports:
        x,y,z=port['outlet'];shape=parts['drain_'+port['channel']]
        assert not shape.isInside(cq.Vector(x,y+.5,z),1e-6),port
    report={'status':'DIGITAL DESIGN / NOT PHYSICALLY VALIDATED','tool':'CadQuery/OpenCascade BRep and STEP round-trip','parts':records,'pipe_fitting_intersection_mm3':collisions,'pair_interferences':interference,'drain_ports':ports,'minimum_nominal_fitting_radial_clearance_mm':p['tray_inner_r']-p['fitting_od_max']/2,'end_bore_radial_clearance_mm':p['end_bore_r']-p['pipe_od']/2,'seam_gap_mm':p['split_gap'],'driver_access_radius_mm':4,'half_opening_sample_distances_mm':[1,5,15,30,60],'unavailable':['FreeCAD native FCStd validation','Fluid-transport/CFD/rain tests','Fastener preload/strength, witness mounting hardware fit, print tolerance and physical disassembly tests'],'notes':['Gravity -Y. Individual drains at Z30 avoid BYPASS Z0.','Detach witnesses/tubes/cables, open halves, lift collectors out, then slide carriers axially. Sampled translations are not a continuous motion proof.','Witness fasteners, pocket retention, electrode seating, port plugs and drain tube retention are detail-design gates; no claim of production readiness.']}
    (out/'geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return parts,report

if __name__=='__main__':
    parts,r=export_and_check();print('CAD:',len(parts),'parts; STEP round-trips passed; interference pairs:',len(r['pair_interferences']))
