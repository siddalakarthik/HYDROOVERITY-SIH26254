# M10 production decisions

Authorized by the owner's M10 cinematic production brief, 27 October 2026.
Baseline: `886bf01d1c775ce0f1f7ec9f2ff2f27bc65a1d91` (remote main verified).

- Isolated animation project; accepted application, hardware and scientific source remain unchanged.
- Remotion 4.0.539, React 19.2.3, TypeScript 5.9.3 scaffold. Local 1920×1080, 30 fps rendering; bounded concurrency. CAD meshes are tessellated from the accepted CadQuery source, not invented geometry.
- Original narration is immutable, hash-verified and outside Git. Two-pass FFmpeg loudness normalization targets −16 LUFS / −1.5 dBTP at 48 kHz. Concatenate decoded samples without overlap or time stretching; report MP3 container versus decoded durations explicitly.
- Local faster-whisper transcription produces estimated word anchors, subject to alignment and rendered-scene review. It never regenerates speech. No claim of manually verified word timing until checked.
- A private Descript project was created, but uploads were blocked before execution. The connector is subsequently unavailable. Runway free-plan video generation is unavailable; no purchase or substitute generated narration.
- Actual sanitized browser captures may be reused with their provenance. Separate test cases must not be represented as one continuous live case. New captures use the existing approved fixture workflow only.
- Five GUARD-5 channels, one physical common-clock ADC, supply-state qualification and abstention remain explicit. Proposed hardware and future field scenes are labeled. M05 unfavorable results and procurement risk remain unchanged.
- Fonts, packages and any soundtrack require license provenance. No third-party competition logo, external stock music, paid hosting or public deployment is assumed.
- Full draft, final render, audio measurements, claim checks, contact sheets and decode checks are required before READY. Issue #10 stays open for review.
