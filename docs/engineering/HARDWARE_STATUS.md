# Hardware status

M08 update: [digital engineering package](M08_DIGITAL_HARDWARE_REPORT.md) prepared for review with executed CadQuery/STEP checks, four editable connectivity drafts, seven figures, interface/calibration/rig plans and a ₹59,870 estimated BOM. Native KiCad/ERC, manufacturing details and all physical qualification remain incomplete. Physical trials **0**, field trials **0**. The original baseline below is retained as historical context; no purchase or build is authorized.

As of the M01 baseline: **functional concept documented; physical prototype unbuilt; physical trials 0; field trials 0**, according to the supplied master context. No finished CAD, PCB/Gerbers, firmware implementation, component readings or laboratory results are delivered in M01.

| Subsystem | Documented proposal | Required before validation |
| --- | --- | --- |
| GUARD-5 | Split external non-pressure-bearing five-channel joint collar | Pipe/fitting envelope, mounting orientation, channel isolation, guards, bypass/drains, tolerances, liners/probes and test-port geometry |
| WATCH | ESP32-class devices, two ADS1115 modules, pressure/bulk flow, SHT31/DS18B20 context | Channel/address/pin allocation, calibration, range/protection, probe supervision and state qualification |
| EAR-PAIR | Two pickups/front ends and PCM1808-class shared-clock stereo acquisition | Pickup coupling/noise qualification, module clocks/MCLK, matched response, I²S compatibility and capture/storage timing |
| Rig | Roughly 10–15 m PVC/HDPE, 12/24 V pump, 60–80 L tank, relief/bypass, about six leak/dummy stations | Rated pressure/flow design, supports, collection, electrical protection and independently selected leak truth |

Hypothetical rig trials around 0.5, 1.0 and 1.5 bar require component-rated safety margins; they are not an authorized build or tested operating envelope. Small-leak truth should use controlled collection/weighing; bulk YF-S201-type meter readings are not assumed micro-leak references.

Future artifacts belong in [hardware](../../hardware/README.md): editable FreeCAD-compatible source/drawings, KiCad source/PCB, board maps, firmware and simulation/HIL stubs, clock and power plans, calibration/error tables, safety review and cost ledger. HIL stubs do not count as hardware tests.

## Qualification backlog

Compare single moisture pad, unguarded multizone and guarded GUARD-5 with service challenge. Test true joint seepage, rain/splash/runoff, condensation, off-axis migration, blocked drainage, neighboring crosstalk, disconnected/corroded probes and dry controls. Establish a method for distinguishing dry from disconnected electrodes.

Acoustics needs passive weak-pinhole/slit trials under pressure/material/noise variation, competent correlation baselines, sensor reseating and independent pump-noise controls. Calibration impulses alone do not prove passive observability.

No procurement or construction now. The ₹60,000 cap and ₹56,750 estimated allocation include contingency; obtain quotations and the missing detailed BOM before ordering. No drinking-line injection, pressure load on printed collar, unsafe pump deadheading/dry run or municipal actuation. [Limitations](ENGINEERING_LIMITATIONS.md) remain binding.
