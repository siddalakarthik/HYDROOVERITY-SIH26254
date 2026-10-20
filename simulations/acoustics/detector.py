"""Observation-only identical-recording CC/PHAT and qualified interval inference."""
import numpy as np
from scipy.signal import butter, sosfiltfilt, correlate, correlation_lags, find_peaks

def peak(a,b,fs,max_delay,phat=False):
    if phat:
        size=2**int(np.ceil(np.log2(len(a)+len(b)-1)))
        z=np.fft.rfft(b,size)*np.conj(np.fft.rfft(a,size));z/=np.maximum(np.abs(z),1e-12)
        raw=np.fft.irfft(z,size);v=np.r_[raw[-len(a)+1:],raw[:len(b)]]
    else:v=correlate(b,a,method='fft')
    lag=correlation_lags(len(b),len(a));keep=np.abs(lag/fs)<=max_delay
    v=v[keep];lag=lag[keep];i=int(np.argmax(v));frac=0.
    if 0<i<len(v)-1:
        den=v[i-1]-2*v[i]+v[i+1]
        if abs(den)>1e-15:frac=float(np.clip(.5*(v[i-1]-v[i+1])/den,-.5,.5))
    peaks,_=find_peaks(v,distance=8);heights=np.sort(v[peaks])
    ratio=float(heights[-1]/max(heights[-2],1e-12)) if len(heights)>1 else 100.
    normalized=float(v[i]/max(np.linalg.norm(a)*np.linalg.norm(b),1e-12)) if not phat else None
    return (float(lag[i])+frac)/fs,ratio,normalized,lag/fs,v

def assess(cap,s):
    out={'outcome':'UNRESOLVED','interval_m':None,'position_m':None,'cc_m':None,'phat_m':None,'lag_s':None}
    if not cap.eligible_path or not cap.shared_clock:out['outcome']='INVALID_PATH';return out
    if cap.pressure_bar<=0:out['outcome']='NO_PRESSURE';return out
    if cap.samples.shape[0]!=2 or not np.isfinite(cap.samples).all():out['outcome']='INVALID_CAPTURE';return out
    a,b=sosfiltfilt(butter(4,[s['filter_low_hz'],s['filter_high_hz']],fs=cap.sample_rate_hz,btype='band',output='sos'),cap.samples,axis=1)
    maxlag=cap.span_m/(cap.speed_mps*(1-cap.speed_fraction))
    cc=peak(a,b,cap.sample_rate_hz,maxlag);ph=peak(a,b,cap.sample_rate_hz,maxlag,True)
    out.update(cc_m=(cap.span_m-cap.speed_mps*cc[0])/2,phat_m=(cap.span_m-cap.speed_mps*ph[0])/2,lag_s=cc[0],peak_correlation=cc[2],peak_ratio=cc[1])
    if min(np.std(a),np.std(b))<s['minimum_rms'] or cc[2]<s['minimum_peak_correlation']:out['outcome']='INSUFFICIENT_SIGNAL';return out
    windows=[peak(aa,bb,cap.sample_rate_hz,maxlag)[0] for aa,bb in zip(np.array_split(a,s['windows']),np.array_split(b,s['windows']))]
    lag=float(np.median(windows));mad=float(np.max(np.abs(np.array(windows)-lag)))
    if cc[1]<s['minimum_peak_ratio'] or mad>s['maximum_lag_mad_s']:return out
    center=(cap.span_m-cap.speed_mps*lag)/2
    half=(cap.length_uncertainty_m+cap.speed_mps*(cap.timing_uncertainty_s+mad)+abs(lag)*cap.speed_mps*cap.speed_fraction)/2
    if not 0<=center<=cap.span_m or 2*half>cap.span_m*s['maximum_interval_span_fraction']:return out
    out.update(outcome='QUALIFIED_CANDIDATE',position_m=center,interval_m=[max(0.,center-half),min(cap.span_m,center+half)])
    return out
