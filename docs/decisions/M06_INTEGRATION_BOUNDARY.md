# M06 integration boundary

Owner-authorized implementation builds on main `1da657d59bccdb6b66fb7dd66cb9f8310c3e7931`.
PR #18 and all four post-merge jobs passed (run 39995544866).

M05 formulas, benchmark configuration and published reference summary remain unchanged.
An offline scientific producer exports 69 deterministic observation/detector datasets:
12 hydraulic, 12 acoustic, 42 collar cases across all three regimes, and three modeled
verification cases. This is repeat-zero playback, not a fresh randomized experiment or
an exhaustive evaluation. Published PPT aggregate results retain their original denominators.

The producer has no API/database credentials. The API does not load generators,
evaluation rows, private seeds, raw example files, or infrastructure geometry.
The repository includes a digest-pinned, strictly validated observation catalogue,
exported once from the existing verified M05 environment. It contains no seeds,
raw truth or hidden per-case evaluation labels. Each JSON file is below 70 KiB.
The API loads this fixed catalogue by default; an operator may disable it or point
to an identical approved catalogue. It cannot accept arbitrary uploaded scenarios.
An authenticated engineer imports a selected immutable snapshot into tenant-scoped
simulation storage. This synchronous import is not advertised as a queued simulation
job. Canonical M02 arbitrary run/job-lease ingestion and evaluator endpoints remain
deferred; scoped M06 replay contracts describe the implemented behavior explicitly.
The existing 70 operations remain compatible.

Replay and export always carry SIMULATION provenance. No operational incidents,
work orders, repairs or verification records are generated. Unknown collar health
remains UNKNOWN. Acoustic output exposes qualified intervals rather than exact
source positions. A modeled PASSED result does not verify an operational repair.

Raw truth and generator seeds remain outside the API image and ordinary artifacts.
Historical aggregate error counts are permitted; individual hidden source labels
are not. Catalogue validation rejects unknown fields instead of stripping them.
