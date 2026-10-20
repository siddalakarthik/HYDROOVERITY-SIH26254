# M08 consolidated estimated materials BOM

DIGITAL DESIGN / NOT PHYSICALLY VALIDATED. All prices ESTIMATED_NOT_QUOTED; no verified supplier quote. INR, 2026-10-20. Technical datasheet URLs are not price quotations.

| ID | Part / model | Qty | Unit INR | Extended INR |
|---|---|---:|---:|---:|
| PIPE | PVC-U PN10 OD32 pipe | 24 m | 180 | 4,320 |
| ELBOW | OD32 pressure elbows | 4 each | 150 | 600 |
| TEE | OD32 pressure tees | 5 each | 180 | 900 |
| UNION | OD32 service unions | 4 each | 250 | 1,000 |
| VALVE | Rated isolation/control ball valves | 4 each | 250 | 1,000 |
| RELIEF | Mechanical relief and gauge adapter set | 1 set | 1,400 | 1,400 |
| TANK | 75L vented HDPE reservoir | 1 each | 1,400 | 1,400 |
| PUMP | SEAFLO SFDP2-012-035-21 candidate | 1 each | 6,500 | 6,500 |
| HOSE | Rated pump hose3m+clamps | 1 set | 850 | 850 |
| ADAPTER | Thread adapters and strainer | 1 set | 1,400 | 1,400 |
| FRAME | Supports and raised dry workbench frame | 1 set | 2,500 | 2,500 |
| TRAY | Containment and drain tray | 1 set | 1,000 | 1,000 |
| GAUGE | 0..2.5bar analog pressure gauges | 2 each | 650 | 1,300 |
| PRESSURE | DFRobot SEN0257 | 2 each | 2,200 | 4,400 |
| FLOW | DFRobot SEN0217 candidate | 2 each | 700 | 1,400 |
| MCU | ESP32-S3-DevKitC-1-N8R8 | 2 each | 1,100 | 2,200 |
| ADC | ADS1115IDGST compatible3.3V breakouts | 2 each | 350 | 700 |
| SHT | SHT31-DIS-B3.3V breakout | 1 each | 450 | 450 |
| TEMP | Externally powered DS18B20 probe | 1 each | 200 | 200 |
| PROBE | Replaceable stainless electrode pairs | 5 pair | 100 | 500 |
| WETPCB | 47k limiters/EOL100k/protection carrier | 1 set | 650 | 650 |
| COLLAR | PETG print+silicone pads/wick trials | 1 set | 1,500 | 1,500 |
| FIX | M4x20 screws/nuts/washers+strap/strain relief | 1 set | 600 | 600 |
| PICKUP | Murata7BB-27-4L0 passive piezo candidate | 2 each | 250 | 500 |
| MOUNT | Two identical removable contact mounts | 2 each | 500 | 1,000 |
| OPAMP | TLV9064IPWR quad opamp | 2 each | 300 | 600 |
| AFE | Matched analog passives and prototype carrier | 1 set | 900 | 900 |
| PCM | PCM1808PW breakout/prototype carrier | 1 each | 1,000 | 1,000 |
| CLOCK | 12.288MHz3.3V CMOS oscillator | 1 each | 400 | 400 |
| SD | 3.3V SPI microSD carrier+32GB card | 1 set | 800 | 800 |
| PSU | Certified isolated24V5A DC supply | 1 each | 2,200 | 2,200 |
| BUCK | 24V->5V3A protected buck | 1 each | 600 | 600 |
| LDO | 3.3V rail and analog5V filter carrier | 1 set | 400 | 400 |
| ESTOP | DC stop/fuses/reverse/TVS/branch protection | 1 set | 1,200 | 1,200 |
| BOX | Dry electronics enclosures and glands | 2 each | 700 | 1,400 |
| CABLE | Shielded pairs/connectors/strain relief | 1 set | 1,800 | 1,800 |
| DEBUG | Isolated/selected USB service interface | 1 set | 1,000 | 1,000 |
| SCALE | 500g0.01g-resolution balance candidate | 1 each | 1,600 | 1,600 |
| REF | Check weights/catch cups/timer/materials | 1 set | 900 | 900 |
| LEAK | Contained rated leak/dummy cartridge | 2 each | 450 | 900 |
| CONS | Rated seals/PTFE/clamps/consumables | 1 set | 900 | 900 |

Components **₹54,870** + contingency **₹5,000** = **₹59,870**, against **₹60,000**; remaining **₹130**. Previous allocation ₹56,750: revised +₹3,120. Reserve is not already spent. Tax/shipping uncertainty must fit reserve plus headroom; actual affordability is unconfirmed. No purchase authorized.

Loop correction: the initial M08 draft undercounted return pipe. A full12m return requires24m total hardpipe, adding₹1,620 over the15m draft. Retain two controlled leak stations at6/9m (multiple stations), one fewer tee and two fewer valves: no inlet service valve and one fewer station valve. Savings:₹180 tee +₹500 valves +₹400 cartridge allowance. Cartridge unit allowance rises conservatively to₹450, rather than lowering an assumed vendor price. Revised net increase₹540 over draft₹59,330. Before intake service, empty/depressurize the system; retain return throttle, adjustable bypass, independent relief and all electrical protection. No safety-relief deletion or change to five wetness/shared-clock architecture.

CSV/JSON hold specification, source, date/status, necessity and substitution review for all41 lines. Every remaining line is essential to this proposed complete demonstrator. Actual cut lengths/fittings, ratings, quotations and taxes/shipping require review; ₹130 is a narrow residual margin. Further overrun requires owner tradeoff review, not invented lower quotes.

Recurring outside cap: local software ₹0/month; assumed electricity4.68kWh/month ×₹8 =₹37.44/month (48W pump2h/day +7.5W electronics8h/day,30days); optional data₹100–300/month; consumables₹500/quarter. Estimates exclude labour, hosted deployment and actual tariff variation.
