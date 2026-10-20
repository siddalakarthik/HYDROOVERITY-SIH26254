# Engineering limitations and claim boundaries

Source: [master context](../project/HYDROOVERITY_MASTER_CONTEXT.md). These are design constraints; M01 performs no physical experiments.

| Limitation | Required engineering behavior |
| --- | --- |
| Weak plastic-pipe passive acoustics, especially realistic quiet leaks | Do not infer audibility from leak flow or active taps; evaluate source level, attenuation, mounting and noise; abstain when insufficient |
| Low/zero pressure or dry pipe | Retain NO_PRESSURE/UNOBSERVABLE/INSUFFICIENT_SIGNAL rather than inventing a coordinate |
| Unknown effective propagation mode/speed | Preserve assumptions and speed uncertainty; calibration does not automatically transfer between conditions |
| Sparse access/buried pipes | State eligible-span and accessible-joint coverage; one collar or portable pair cannot monitor every pipe |
| Branches, mixed material, reflections and multiple leaks | Treat correlation peaks/path assignment as ambiguous; allow multiple candidates or unresolved |
| Rain, splash, runoff and condensation | EXT/BYPASS and environmental context support explanations, not perfect source separation |
| Collection geometry, blockage and off-axis migration | Wetness may miss collectors or cross paths; validate challenge/drain behavior physically |
| Dry versus broken/corroded electrodes | Require supervised electronics and service evidence; dry reading alone cannot establish sensor health |
| False confident correlation | Compare competent baselines, pump controls, repeated windows and holdouts; report confident errors/coverage |
| Unknown demand/storage and meter uncertainty | Call residual unexplained loss, not proven leakage; define boundaries and comparability |
| EPANET/WNTR validity | Use pressurized quasi-steady/extended-period studies where valid; disclose filling abstractions, no full trapped-air/water-hammer claim |
| Toy GUARD-5 transport model | Assumed transfer coefficients illustrate logic, not validated CFD or manufactured separation |
| Unbuilt reliability/power/safety | No measured lifespan, corrosion resistance, battery years, compliance or hardware accuracy claim |

Confirmed wetness is not confirmed leak origin. Recorded repair is not verified recovery. Compare operating states, pressure/demand/storage, sensor calibration and freshness before declaring a repair verified; retain not-verifiable cases.

Physical novelty and improvement over commercial systems are unestablished. Prior-art/source claims in the brief require later review before reuse/public claims; no patent score or exclusivity assertion is made. Historic 30.1–38.9 m candidate interval is synthetic, not a hole found in a physical pipeline. The 480 L/day illustration is hypothetical, not measured recovery.

The digital-first plan leaves a Hardware-category competition risk. A polished concept animation, HIL stub, code-test count or simulated benchmark cannot substitute for a fabricated and tested prototype.
