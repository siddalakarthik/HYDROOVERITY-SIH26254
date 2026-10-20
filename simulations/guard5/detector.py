"""Wetness supports hypotheses; it cannot confirm origin or unsupported health."""
import numpy as np
def assess(obs,s):
    wet=obs.wet;protected=wet[:,:3].any(axis=1);env=wet[:,3];bypass=wet[:,4]
    persistent=lambda v: bool(np.any(np.convolve(v.astype(int),np.ones(s['persistence_samples']),mode='valid')>=s['persistence_samples']))
    suspect=persistent(protected & ~env)
    outcome='LOCAL_SUSPECT' if suspect else 'ENVIRONMENTAL_OR_AMBIGUOUS' if env.any() else 'COLLECTION_UNRESOLVED' if bypass.any() else 'NO_WETNESS_UNKNOWN_HEALTH'
    service='NOT_PERFORMED'
    if obs.service_target is not None:
        post=(obs.time_s>=obs.service_start_s)&(obs.time_s<=obs.service_end_s+30)
        service='RESPONSE_OBSERVED' if wet[post,obs.service_target].any() else 'COLLECTION_OR_SENSOR_UNRESOLVED'
        suspect=False;outcome='SERVICE_TEST'
    return {'local_suspect':suspect,'outcome':outcome,'health':list(obs.health),'blockage_suspected':bool(bypass.any() and not protected.any()),'service':service}
