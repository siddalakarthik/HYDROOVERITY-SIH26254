"""Assumed linear shared-clock propagation; truth never enters Capture."""
import numpy as np
from scipy.signal import butter, sosfiltfilt
from simulations.common import Capture, readonly

def delay(x, seconds, fs, distance=0., attenuation=.003):
    f=np.fft.rfftfreq(len(x),1/fs)
    return np.fft.irfft(np.fft.rfft(x)*np.exp(-2j*np.pi*f*seconds)*np.exp(-attenuation*distance*np.sqrt(f/100)),n=len(x))

def generate(case, truth_seed, noise_seed):
    g=np.random.default_rng(truth_seed);rng=np.random.default_rng(noise_seed)
    fs=4096;n=8192;L=float(g.uniform(10,25) if case=='A12' else 15)
    c=float(g.uniform(250,450));x=L*{'A01':.12,'A02':.5,'A03':.88}.get(case,float(g.uniform(.1,.9)))
    source=sosfiltfilt(butter(4,[80,1000],fs=fs,btype='band',output='sos'),rng.normal(size=n))
    source/=np.std(source);amp=.12 if case in ('A04','A10') else 1.
    attenuation=.03 if case=='A12' else .003
    a=amp*delay(source,x/c,fs,x,attenuation);b=amp*delay(source,(L-x)/c,fs,L-x,attenuation)
    if case=='A07':b+=.95*delay(source,(L-x)/c+.009,fs,L-x,attenuation)
    if case=='A08':
        s=rng.normal(size=n);x2=.8*L
        a+=delay(s,x2/c,fs);b+=delay(s,(L-x2)/c,fs)
    if case=='A06':
        pump=np.sin(2*np.pi*150*np.arange(n)/fs)+.6*np.sin(2*np.pi*300*np.arange(n)/fs)
        a+=2*pump;b+=2*delay(pump,.004,fs)
    if case=='A09':a*=0;b*=0
    a+=rng.normal(0,.2,n);b+=rng.normal(0,.35,n)
    # Distinct sensor response, channel gain, and declared common-clock sensitivity.
    b=sosfiltfilt(butter(2,1100,fs=fs,output='sos'),b)
    if case=='A11':b=np.clip(b*.2,-.08,.08)
    speed=c*1.25 if case=='A05' else c
    cap=Capture(readonly(np.array([a,b])),fs,L,speed,.08 if case!='A05' else .15,0 if case=='A09' else 2.,True,True,1/fs)
    return cap,{'position_m':x,'speed_true_mps':c,'sources':2 if case=='A08' else 1,'case':case,'eligible':case!='A09'}
