"""Explicit observation projections. Never serialize generator return objects."""

from simulations.common import CHANNELS, LABEL, clean


def watch_series(observation, prediction):
    return clean({
        "module": "HYDRO-WATCH", "label": LABEL,
        "time_s": observation.time_s,
        "pressure_bar": observation.pressure_bar,
        "inlet_lpm": observation.inlet_lpm,
        "customer_outlet_lpm": observation.customer_outlet_lpm,
        "pump_on": observation.pump_on,
        "storage_known": observation.storage_known,
        "solver_valid": observation.solver_valid,
        "meter_sigma_lpm": observation.meter_sigma_lpm,
        **{key: prediction[key] for key in (
            "state", "qualified_outcome", "fixed_alarm", "watch_alarm",
            "residual_lpm", "urgent_events", "threshold_lpm",
        )},
        "limitations": [
            "EPANET steady snapshots; supply transitions are phenomenological abstractions.",
            "Unaccounted flow is suspicion, not proof of a leak or its location.",
            "Customer outflow is already included in the balance; demand is not subtracted twice.",
        ],
    })


def guard_series(observation, prediction, pad, multizone):
    return clean({
        "module": "GUARD-5", "label": LABEL,
        "channels": [name.removeprefix("COLLAR_") for name in CHANNELS],
        "time_s": observation.time_s, "wet": observation.wet,
        "health": observation.health,
        "outcome": prediction["outcome"],
        "local_suspect": prediction["local_suspect"],
        "blockage_suspected": prediction["blockage_suspected"],
        "service": prediction["service"],
        "reference_pad_alarm": bool(pad.any()),
        "reference_multizone_alarm": bool((multizone[:, 0] & ~multizone[:, 1]).any()),
        "limitations": [
            "Exactly five wetness channels; UNKNOWN health is not HEALTHY.",
            "Physical collector performance is unverified; dry disconnected electrodes can be indistinguishable from dryness.",
            "Wetness does not establish its source. GUARD-5 can perform worse than reference models.",
        ],
    })


def ear_series(observation, prediction, settings):
    # Compute display correlation using the SAME filtering and peak routine as M05.
    # This does not change the detector's decision or its localization interval.
    import numpy as np
    from scipy.signal import butter, sosfiltfilt
    from simulations.acoustics.detector import peak

    a, b = sosfiltfilt(butter(
        4, [settings["filter_low_hz"], settings["filter_high_hz"]],
        fs=observation.sample_rate_hz, btype="band", output="sos",
    ), observation.samples, axis=1)
    correlation = peak(a, b, observation.sample_rate_hz,
                       observation.span_m / (observation.speed_mps * (1-observation.speed_fraction)))
    # A display preview only. All detector calculations use the full recording.
    stride = max(1, observation.samples.shape[1] // 1024)
    return clean({
        "module": "HYDRO-EAR", "label": LABEL,
        "time_s": np.arange(0, observation.samples.shape[1], stride) / observation.sample_rate_hz,
        "waveforms": observation.samples[:, ::stride],
        "preview_stride": stride,
        "sample_rate_hz": observation.sample_rate_hz,
        "shared_clock": observation.shared_clock,
        "eligible_path": observation.eligible_path,
        "span_m": observation.span_m,
        "assumed_speed_mps": observation.speed_mps,
        "speed_fraction": observation.speed_fraction,
        "timing_uncertainty_s": observation.timing_uncertainty_s,
        "pressure_bar": observation.pressure_bar,
        "correlation_lag_s": correlation[3], "correlation": correlation[4],
        "outcome": prediction["outcome"], "interval_m": prediction["interval_m"],
        "peak_correlation": prediction.get("peak_correlation"),
        "peak_ratio": prediction.get("peak_ratio"),
        "limitations": [
            "Paired modeled captures share one sampling clock; no physically validated recorder exists.",
            "Display waveforms are subsampled previews, not a replacement for the full detector recording.",
            "An accepted interval is a qualified candidate, not an exact crack location or calibrated probability.",
            "M05 includes accepted wrong intervals; absence of acoustic evidence does not exclude a leak.",
        ],
    })
