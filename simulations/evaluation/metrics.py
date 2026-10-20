"""Evaluator-only access to simulation truth and statistical denominators."""
import numpy as np
def wilson(k,n):
    if not n:return None
    z=1.95996398454;p=k/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0.,center-half),min(1.,center+half)]
def binary(rows,pred='predicted',label='truth'):
    tp=sum(bool(r[pred]) and bool(r[label]) for r in rows);fp=sum(bool(r[pred]) and not r[label] for r in rows)
    fn=sum(not r[pred] and bool(r[label]) for r in rows);tn=len(rows)-tp-fp-fn
    return dict(n=len(rows),tp=tp,fp=fp,fn=fn,tn=tn,precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+fn) if tp+fn else None,f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None)
def acoustic(rows):
    eligible=[r for r in rows if r['eligible']];accepted=[r for r in eligible if r['position_m'] is not None]
    err=[r['error_m'] for r in accepted];correct=sum(e<=1 for e in err);wrong=sum(not r['interval_contains_truth'] for r in accepted)
    return {'eligible':len(eligible),'accepted':len(accepted),'unresolved':len(eligible)-len(accepted),'coverage':len(accepted)/len(eligible),'coverage_ci95':wilson(len(accepted),len(eligible)),'accepted_median_error_m':float(np.median(err)) if err else None,'accepted_p95_error_m':float(np.percentile(err,95)) if err else None,'accepted_within_1m':correct,'correct_all_eligible':correct/len(eligible),'correct_all_ci95':wilson(correct,len(eligible)),'confidently_wrong_intervals':wrong,'unresolved_error_policy':'No point error imputed: report accepted errors and correct/ALL eligible; unresolved count as not located.', 'cc_median_error_m':float(np.median([r['cc_error_m'] for r in eligible])),'phat_median_error_m':float(np.median([r['phat_error_m'] for r in eligible]))}
