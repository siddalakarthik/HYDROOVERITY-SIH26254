# M08 firmware interface readiness

DIGITAL DESIGN / NOT PHYSICALLY VALIDATED. No executable firmware is delivered or claimed build-tested. `../electronics/interfaces.json` is the canonical pin, ADC, clock and power map. Board choice is ESP32-S3-DevKitC-1-N8R8, not the older ESP32. WATCH and EAR are separate controllers, each with its own GPIO namespace.

## WATCH acquisition

| Local channel | Quantity / units | Proposed schedule | Qualification |
|---|---|---|---|
| PRESSURE_IN / OUT | bar after calibration; retain voltage locally | 10 Hz each | Warm-up, range, calibration, stale and wiring checks |
| FLOW_IN / OUT | bulk L/min | pulse interrupt; 1 s count / 5 s average | Measured K-factor; below useful pulse rate = SUSPECT |
| COLLAR_A / B / C / EXT / BYPASS | paired polarity voltages (V), derived dimensionless wetness | 1 paired scan/s | Individual calibration, EOL ambiguity and excitation test |
| SHT31 temperature / humidity | °C / %RH, context | 1 Hz | CRC, plausible range and bus timeout |
| DS18B20 | °C, context | 1 Hz | Powered 3.3 V; CRC and conversion completion |
| V3V3_MONITOR | V after divider compensation | 1 Hz | Advisory; ADC and GPIO share this rail, not an independent safety monitor |

ADS1115s use single-shot multiplexed conversions at 128 SPS and ±4.096 V PGA. Inputs must still stay within GND–VDD in normal operation. Addresses 0x48 (ADDR=GND), 0x49 (ADDR=VDD) and SHT31 0x44 do not conflict. Even charging both polarities separately gives 20 pressure + 10 wetness + 1 rail = 31 conversions/s across two ADCs. Reserve timeout margin. No simultaneous sampling claim is made for WATCH.

Wetness scan: idle P=N=0; P=3.3/N=0, settle 50 ms, acquire all five; P=0/N=3.3, settle 50 ms, acquire all five; restore idle. Each leg has 47 kΩ; worst theoretical short current is 3.3/94k = 35.1 µA per channel. A distal 100 kΩ EOL yields approximately 2.50 V / 0.80 V at the sensed positive electrode when dry; open approximately 3.3/0; short approximately 1.65/1.65. These are unloaded circuit calculations, not validated thresholds. ADS1115 loading, clamp leakage, supply, water conductivity, polarity imbalance and corrosion need measurement. EOL means a path to that resistor was observed, not that the exposed electrodes or collection path work. Never translate DRY into HEALTHY or NO LEAK.

## EAR acquisition

PCM1808 master, MD1=MD0=HIGH, FMT=LOW: external 3.3 V CMOS oscillator drives SCKI=12.288 MHz; ADC outputs BCLK=3.072 MHz and LRCLK=48 kHz. ESP32-S3 standard I²S RX **slave** receives GPIO15/16/17 BCLK/WS/DIN; it does not drive MCLK or those clocks. Both channels pass through this same stereo converter. This is a proposed pin/clock contract, not a working capture implementation.

ADC uses 5 V analog and 3.3 V digital supply, 24 valid bits in 32-bit stereo slots. 48,000×2×4=384,000 B/s; 10 s = 3,840,000 bytes; packed 24-bit = 2,880,000 bytes. 64 KiB DMA gives only 170.7 ms of gross buffering. SD pauses, SPI throughput, DMA-capable memory versus PSRAM and power integrity are unverified. PSRAM size does not prove lossless capture. Require preallocated files, frame counters, overflow counters, bounded ring buffers, sequence checks, throughput margin and fail-closed recording. Discard at least a proposed 1 s startup and verify clocks/data, not merely elapsed time.

`../acoustic-acquisition/acquisition.schema.json` defines local metadata. Enforce frames_written + dropout_frames = frames_expected; any missing frames, DMA overflow, bad hash, unknown channel order or absent clock verification prevents localization. Store sample indices for inter-channel timing; UTC start is for provenance only. Test left/right injection separately and common-input phase skew before accepting evidence. Never infer passive leak audibility from tap calibration.

## Transport and M02 compatibility

Map local IDs to provisioned UUID channel IDs and device_configuration_id. M02 `ObservationInput` accepts exactly event_id, channel_id, collection_time (UTC), unit, scalar value, device_configuration_id, quality (VALID/SUSPECT/INVALID/UNCALIBRATED). Batch at most 500. No arbitrary source/environment/run/truth fields. Trusted adapter identity supplies provenance; prototype tests must be laboratory evidence, never FIELD_VALIDATED. Waveforms and capture metadata require the separately authorized artifact flow; they do not fit scalar observation batches. No API or upload adapter is implemented by M08.

No-connection, conversion timeout, ADC saturation, implausible range, expired calibration and stale timestamps are separate local reason codes. Map stale/fault data to INVALID; omit non-finite numeric payloads. Until calibration, use UNCALIBRATED. Do not send fabricated zero values for missing measurements. Retry idempotently by event_id with a bounded offline queue; queue loss is explicit. Watchdog must restore excitation idle and retain a reboot/fault record; it cannot assert safe hydraulic operation or actuate infrastructure. Separate maintenance electrical self-test state from actual water-path challenge state. Future evidence interpretation retains supply state, independent urgent/fault observations, confidence and UNRESOLVED abstention.

## Power, protection and wiring gate

Certified isolated 24 V/5 A source → master DC fuse/reverse-polarity protection/appropriately rated TVS → separately fused pump branch with latching DC stop and dry-run provision; independent protected 24→5 V/3 A buck powers WATCH/EAR. Peak allowances are WATCH 0.65 A and EAR 0.85 A at 5 V (7.5 W), not measurements. Pump allowance 48 W; at assumed 85% buck efficiency combined 24 V draw is about 2.37 A. Select wire, connectors and transient-rated fuses from actual inrush/temperature ratings. Mechanical pressure relief is independent of firmware and pump switch.

Each DevKit's regulator provides its own 3.3 V rail; do not parallel two board outputs. EAR analog 5 V is filtered locally; its adequacy and ADC noise need measurement. BOM rail-filter allowance is not authorization to parallel an external LDO with a board regulator. USB service requires power selection or isolation; no simultaneous external 5 V and USB backfeed. A shared design-net name in separate schematic sheets is not a wiring instruction to parallel controller supplies.

Pressure: SEN0257 5 V, 0.5–4.5 V candidate output, 20k/20k 0.1% divider + 1 µF at ADC. Rth=10k gives ~15.9 Hz filter; output up to 5 V divides to 2.5 V. Normal range 0.25–2.25 V fits 3.3 V ADC rail. Worst-case supply-off, transients, clamp leakage and sensor output loading still need protection review. Sensor 0–16 bar is a poor span match for proposed low-pressure rig; advertised 1%FS is 0.16 bar, not 1% of 0.5 bar. Calibration or reviewed lower-range substitution is necessary.

Flow: SEN0217 candidate pulse interface must be verified on actual lot. NPN open-collector level translator isolates assumed 5 V pulse output from 3.3 V GPIO; 47k base resistor, 100k base pulldown, 10k 5 V raw pull-up and 10k 3.3 V collector pull-up. Exact transistor package pinout and switching waveform are release gates. Do not directly connect assumed 5 V flow pulses to GPIO.

Connectors and every proposed pin/net appear in connections.csv. Pressure/flow connector numbers denote design harness numbering, not verified manufacturer cable colors. Label and key all harnesses after continuity review. Five wetness inserts use keyed two-pole connectors; nine-way WATCH wetness daughterboard link includes P, N, GND, five returns and 3.3 V. Both acoustic channels use equal-length shielded cable, single-point shield connection, strain relief and identical removable couplers; separate analog returns from pump current until supply star. Do not use a shield as the sensor return. Protection clamp MPN/capacitance/leakage, fuse/TVS coordination, buck/oscillator board details, power sequencing and native ERC are explicitly incomplete. Schematic files are editable connectivity drafts, not fabrication release.
