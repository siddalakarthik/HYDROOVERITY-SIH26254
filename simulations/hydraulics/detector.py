"""Both detectors see exactly the same observation-only record."""
from __future__ import annotations
import numpy as np
from simulations.common import HydraulicObservation


def assess(obs: HydraulicObservation, settings: dict) -> dict:
    n = len(obs.time_s)
    states = []; outcomes = []; residual = obs.inlet_lpm - obs.customer_outlet_lpm
    baseline = 0.0; count = 0
    fixed = np.zeros(n, bool); alarms = np.zeros(n, bool)
    reference_flow = float(np.nanmedian(obs.inlet_lpm[:10]))
    reference_pressure = float(np.nanmedian(obs.pressure_bar[:10]))
    urgent = []
    for k in range(n):
        p = obs.pressure_bar[k]
        dp = p - obs.pressure_bar[k - 1] if k else 0
        finite = np.isfinite([p, obs.inlet_lpm[k], obs.customer_outlet_lpm[k]]).all()
        if not finite or not obs.solver_valid[k]: state = 'UNKNOWN'
        elif not obs.pump_on[k] and p < .08: state = 'OFF'
        elif not obs.pump_on[k] and p >= .08: state = 'DRAINING'
        elif dp > settings['stable_pressure_change_bar']: state = 'FILLING'
        elif p < settings['minimum_pressure_bar']: state = 'UNKNOWN'
        else: state = 'STEADY'
        states.append(state)
        fixed[k] = bool(np.isfinite(p) and (p < reference_pressure - settings['fixed_pressure_drop_bar'] or
                        obs.inlet_lpm[k] > reference_flow * settings['fixed_inlet_multiplier'] or
                        residual[k] > settings['fixed_residual_lpm']))
        threshold = max(settings['residual_floor_lpm'], settings['sigma_multiplier'] * np.sqrt(2) * obs.meter_sigma_lpm)
        if state != 'STEADY' or not obs.storage_known[k]:
            outcomes.append('UNRESOLVED'); count = 0
        else:
            anomalous = residual[k] - baseline > threshold
            count = count + 1 if anomalous else 0
            alarms[k] = count >= settings['persistence_samples']
            outcomes.append('UNEXPLAINED_LOSS_SUSPECTED' if alarms[k] else 'NO_PERSISTENT_ANOMALY')
            # Adapt only within comparable measured pressure and nonanomalous residual.
            if not anomalous and abs(dp) <= settings['stable_pressure_change_bar']:
                baseline += settings['ewma_alpha'] * (residual[k] - baseline)
        if not finite: urgent.append({'time_s': float(obs.time_s[k]), 'reason': 'MISSING_SENSOR_DATA'})
        elif dp < -.8: urgent.append({'time_s': float(obs.time_s[k]), 'reason': 'PRESSURE_COLLAPSE_REVIEW'})
    return {'state': states, 'qualified_outcome': outcomes, 'fixed_alarm': fixed, 'watch_alarm': alarms,
            'residual_lpm': residual, 'urgent_events': urgent, 'threshold_lpm': threshold}
