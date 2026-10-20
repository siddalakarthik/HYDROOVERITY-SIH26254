"""EPANET 2.2 PDA snapshots; transitions are separately labeled abstractions."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
import tempfile

import numpy as np
import wntr

from simulations.common import HydraulicObservation, readonly

NODES = {'R': (0, 0), 'J0': (100, 0), 'L1': (220, 60), 'L2': (220, -60),
         'D1': (360, 90), 'D2': (360, -90), 'D3': (200, 0)}
PIPES = [('IN', 'R', 'J0', 100, .15), ('B1', 'J0', 'L1', 140, .09),
         ('B2', 'J0', 'L2', 140, .09), ('C1', 'L1', 'D1', 150, .065),
         ('C2', 'L2', 'D2', 150, .065), ('C3', 'J0', 'D3', 100, .065)]


def network(head_m: float = 30, demand_factor: float = 1, area_m2: float = 0,
            leak_node: str = 'L1') -> wntr.network.WaterNetworkModel:
    wn = wntr.network.WaterNetworkModel()
    wn.add_reservoir('R', base_head=head_m, coordinates=NODES['R'])
    for name in NODES:
        if name == 'R':
            continue
        demand = {'D1': .00015, 'D2': .00018, 'D3': .00012}.get(name, 0) * demand_factor
        wn.add_junction(name, base_demand=demand, elevation=1 if name.startswith('D') else 0, coordinates=NODES[name])
    for name, start, end, length, diameter in PIPES:
        wn.add_pipe(name, start, end, length=length, diameter=diameter, roughness=130, minor_loss=0)
    wn.options.time.duration = 0
    wn.options.hydraulic.demand_model = 'PDA'
    wn.options.hydraulic.required_pressure = 15.0  # metres of water, not bar
    wn.options.hydraulic.minimum_pressure = 0
    wn.options.hydraulic.pressure_exponent = .5
    wn.options.hydraulic.emitter_exponent = .5
    wn.options.hydraulic.accuracy = 1e-6
    if area_m2:
        wn.get_node(leak_node).emitter_coefficient = .62 * area_m2 * np.sqrt(2 * 9.80665)
    return wn


@lru_cache(maxsize=512)
def solve(head_m: float = 30, demand_factor: float = 1, area_m2: float = 0,
          leak_node: str = 'L1') -> dict:
    """Cached deterministic operating points, not fitted/artificial flow subtraction."""
    try:
        wn = network(head_m, demand_factor, area_m2, leak_node)
        with tempfile.TemporaryDirectory(prefix='hydro-m05-') as tmp:
            result = wntr.sim.EpanetSimulator(wn).run_sim(file_prefix=str(Path(tmp) / 'network'), version=2.2, convergence_error=True)
        pressures = result.node['pressure'].iloc[0]
        flows = result.link['flowrate'].iloc[0]
        values = np.r_[pressures.values, flows.values]
        if not np.all(np.isfinite(values)) or (pressures.drop('R') < -.001).any():
            raise ValueError('nonfinite or negative pressurized solution')
        inlet = float(flows['IN'] * 60000)
        outlets = float(flows[['C1', 'C2', 'C3']].sum() * 60000)
        predicted_leak = .62 * area_m2 * np.sqrt(2 * 9.80665 * max(0, pressures[leak_node])) * 60000
        return {'valid': True, 'solver': 'EPANET 2.2 PDA', 'inlet_lpm': inlet,
                'outlets_lpm': outlets, 'leak_lpm': float(predicted_leak),
                'balance_error_lpm': inlet - outlets - predicted_leak,
                'pressure_bar': float(pressures['L1'] * .0980665),
                'pressures_bar': {k: float(v * .0980665) for k, v in pressures.items()}}
    except (RuntimeError, ValueError, wntr.epanet.exceptions.EpanetException) as exc:
        return {'valid': False, 'solver': 'INVALID_SOLVER_RESULT', 'reason': type(exc).__name__}


@dataclass(frozen=True)
class HydraulicTruth:
    scenario: str
    active_leak: np.ndarray
    leak_lpm: np.ndarray
    phase: tuple[str, ...]
    balance_error_lpm: np.ndarray
    solver_status: tuple[str, ...]
    parameters: dict


def generate(case: str, seed: int, *, repair_fraction: float = 0,
             missing_post: bool = False) -> tuple[HydraulicObservation, HydraulicTruth]:
    rng = np.random.default_rng(seed)
    t = np.arange(0, 3601, 60, dtype=float)
    n = len(t)
    p = np.zeros(n); qi = np.zeros(n); qo = np.zeros(n); leak = np.zeros(n)
    errors = np.zeros(n); pump = np.ones(n, bool); valid = np.ones(n, bool)
    phase = []; status = []
    area = {'H02': 1e-7, 'H03': 5e-6, 'H10': 5e-6, 'H12': 5e-6}.get(case, 0)
    node = 'L2' if case == 'H10' else 'L1'
    for k, time in enumerate(t):
        head, demand, current_area = 30.0, 1.0, area if time >= 900 else 0
        mode = 'PRESSURIZED'
        if case == 'H04' and time >= 900: demand = 1.6
        if case == 'H05' and time >= 900: head = 18.0
        if case == 'H06' and time >= 900: head = 3.0
        if case == 'H07': mode = 'OFF'
        if case in ('H08', 'H12') and time < 600: mode = 'OFF' if time < 180 else 'FILLING'
        if case == 'H09' and time >= 2400: mode = 'DRAINING' if time < 3000 else 'OFF'
        if case == 'H10' and time >= 900: demand = 1.6
        if case == 'H12' and time >= 2400: current_area = area * repair_fraction
        if mode == 'PRESSURIZED':
            s = solve(head, demand, current_area, node)
            valid[k] = s['valid']
            if valid[k]:
                p[k], qi[k], qo[k], leak[k] = s['pressure_bar'], s['inlet_lpm'], s['outlets_lpm'], s['leak_lpm']
                errors[k] = s['balance_error_lpm']
            else:
                p[k] = qi[k] = qo[k] = leak[k] = errors[k] = np.nan
            status.append(s['solver'])
        else:
            # Explicit phenomenological state observations; no EPANET filling claim.
            pump[k] = mode == 'FILLING'
            if mode == 'FILLING':
                p[k] = (time - 180) / 420 * 2.9
                qi[k], qo[k] = 40, 10
            elif mode == 'DRAINING':
                p[k] = max(0, (3000 - time) / 600 * 2.9)
                qi[k], qo[k] = 0, 8
            status.append('STATE_ABSTRACTION_' + mode)
        phase.append(mode)
    sigma = .25
    p += rng.normal(0, .005, n)
    qi += rng.normal(0, sigma, n); qo += rng.normal(0, sigma, n)
    known = np.ones(n, bool)
    known[np.array(phase) != 'PRESSURIZED'] = False
    if case == 'H11':
        qi += np.maximum(0, t - 900) / 2700 * 3.5  # unknown drift, not supplied to detector
        qo[28:32] = np.nan
    if missing_post:
        qo[t >= 2400] = np.nan
    obs = HydraulicObservation(*map(readonly, (t, p, qi, qo, pump, known)), sigma, readonly(valid))
    truth = HydraulicTruth(case, readonly(leak > .02), readonly(leak), tuple(phase), readonly(errors), tuple(status),
                           {'area_m2': area, 'node': node, 'repair_fraction': repair_fraction, 'missing_post': missing_post})
    return obs, truth
