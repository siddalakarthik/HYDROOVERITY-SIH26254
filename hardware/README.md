# Digital hardware engineering

Status: M08 digital package prepared for review; physical trials 0, field trials 0. See the [engineering report](../docs/engineering/M08_DIGITAL_HARDWARE_REPORT.md) for executed checks and incomplete release gates.

| Folder | Responsibility |
| --- | --- |
| `guard5-collar/` | Collector/guard/bypass mechanism requirements and fit design. |
| `hydro-watch/` | Pressure/flow/context interfaces and state/device design. |
| `acoustic-acquisition/` | Pickups, matched analog channels and one physical sample clock. |
| `mechanical-cad/` | Editable collar/rig CAD and drawings; exports separate. |
| `electronics/` | Editable KiCad schematics/PCB; exports separate. |
| `firmware/` | Future buildable ESP32 device source, pin/protocol and simulation/HIL plans. |
| `bom/` | Estimated materials and later supplier/quotation ledger; ₹60,000 cap. |
| `calibration/` | Future measurement/probe/acoustic calibration and service procedures. |

Follow [AGENTS.md](../AGENTS.md) and the [documentation index](../docs/README.md) before development.

M08 supplies editable [parametric CAD](mechanical-cad/guard5.py), [mechanical parameters](guard5-collar/envelope.json), four generated [schematic drafts and netlists](electronics/netlist.json), [pin/clock map](electronics/interfaces.json), [firmware readiness](firmware/INTERFACE_READINESS.md), [calibration plan](calibration/VALIDATION_PLAN.md), [rig layout](mechanical-cad/rig_layout.json), [itemized BOM](bom/M08_BOM.md), and [seven-figure renderer](render_m08.py). All are DIGITAL DESIGN / NOT PHYSICALLY VALIDATED. No executable firmware, PCB fabrication release, physical build or purchase. Revised ₹59,330 materials estimate includes ₹5,000 reserve; no prices are vendor-verified. Native KiCad opening/ERC, exact protection/module details and physical fit/performance remain gates.
