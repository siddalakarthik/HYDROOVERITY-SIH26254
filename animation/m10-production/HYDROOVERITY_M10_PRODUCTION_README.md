# HYDROOVERITY M10 production

Status: **WORK IN PROGRESS — FINAL MASTER NOT READY**.

This isolated project is based on accepted main `886bf01d1c775ce0f1f7ec9f2ff2f27bc65a1d91`.
The application, M05 results, M08 source and deployment gates are unchanged.
The owner authorized M10 on 27 October 2026. No milestone issue is closed by a style test.

## Actual completed preparation

- Four immutable input copies, SHA256 recorded in local `public/audio/audio-measurements.json`.
- FFmpeg n7.1 two-pass per-track normalization; no speech regeneration, pitch or speed changes.
- 48 kHz / mono / 24-bit PCM voice master: 25,186,640 samples = 524.7216667 seconds.
- Measured master: −16.33 LUFS integrated, −1.45 dBTP, LRA 3.40 LU.
- 25 valid accepted CadQuery BRep parts tessellated into 15,476 triangles. This is digital geometry, not physical validation.
- A 26-second, 960×540, 30 fps H.264 style-test video rendered. CAD clipping and asynchronous mesh loading were corrected and inspected.
- Local Remotion Studio: `http://localhost:3100`. Original files, audio, derived meshes, captures and renders are ignored.
- Local faster-whisper base.en produced word estimates for all four original recordings. The timeline contains 57 anchored scenes / 15,832 frames, including a three-second final visual hold.
- The four-second audio/video smoke check passed H.264 / 48 kHz AAC inspection and full decode. Seven production invariants, lint, TypeScript, bundle and repository integrity pass locally.
- Final voice-only mix preserves all normalized narration samples and adds only closing silence: 527.733333 seconds. Measured −16.33 LUFS / −1.45 dBTP. This uses the brief's permitted clean-voice fallback; no stock soundtrack was licensed or imported.

## Reproduction

Run Node commands from this directory with Node 24 and the committed npm lock:

```powershell
npm ci
npm run dev -- --no-open --port=3100
npx tsc --noEmit
npx remotion render src/index.ts M10StyleTest renders/M10_STYLE_TEST_540P.mp4 --scale=0.5 --concurrency=1
```

Python preparation accepts explicit paths; no credential or application fixture is read:

```powershell
python tools/prepare_audio.py --input <original-mp3-directory> --output public/audio --ffmpeg <ffmpeg-executable> --ffprobe <ffprobe-executable>
python tools/export_cad.py --repo ../.. --output public/cad
python tools/prepare_assets.py --workspace <existing-project-workspace> --project .
python tools/transcribe.py --input <original-mp3-directory> --output local/transcripts --model-cache <local-model-cache> --model base.en --ffmpeg <ffmpeg-executable>
python tools/build_timeline.py
python tools/write_captions.py
python tools/prepare_handoff.py
python -m unittest discover -s tests -v
node tools/render_review.mjs
node tools/render_film.mjs --preview
python tools/check_render.py renders/HYDROOVERITY_M10_DRAFT_540P.mp4 --ffprobe <ffprobe-executable> --output local/draft-qa
# Inspect the draft and fix demonstrated defects before proceeding:
node tools/render_film.mjs
python tools/check_render.py renders/HYDROOVERITY_M10_MASTER_1080P.mp4 --ffprobe <ffprobe-executable> --output local/master-qa
node tools/preview.mjs
```

Use the existing CadQuery 2.8.0 environment only for `export_cad.py`. The local audio environment uses faster-whisper 1.2.1; its resolved environment is recorded in `local/audio-toolchain.txt`. Native app credentials never enter this production project.

## Boundaries and outstanding work

The existing captures originate from separate synthetic browser test cases. They are explicitly labeled and must not be edited to imply a single live case. The requested single-case continuity remains a shortfall. Top/middle/end privacy samples were inspected: synthetic records, no real resident information or credentials observed. This is not a full-pixel OCR guarantee. Appropriate viewport crops focus actual forms, findings, timelines and scientific charts without rewriting their contents.

Do not publish estimated ASR words as verified captions. `HYDROOVERITY_M10_CAPTIONS_DRAFT.srt` preserves the raw ASR result with canonical naming. `HYDROOVERITY_M10_CAPTIONS.srt` is a context-corrected review copy; corrections are logged locally, and listening review remains unverified. Audio pronunciation is never silently replaced. Full draft and final-master technical results are recorded in `HYDROOVERITY_M10_RENDER_QA.md` when available.

The optional review player serves only the named draft/master MP4s at `http://127.0.0.1:3101`; it exposes no project directory, credentials or application APIs. Renderer defaults to two workers; `M10_CONCURRENCY` permits 1–4. `M10_CHROME` and `M10_FFMPEG` override the documented Windows defaults. Video-only rendering followed by one PCM-to-AAC mux preserves absolute audio timing and avoids per-frame audio extraction overhead.

Source CI deliberately runs only the public contract tests, lint, typecheck and bundle. Local production tests additionally require owner audio, prepared meshes and sanitized captures. No missing private assets are replaced with fake CI fixtures. Existing application/science/CAD CI jobs remain intact.

Remotion's installed license permits individuals and nonprofit/not-for-profit use; this student engineering-film workflow does not purchase a commercial license. If ownership/use changes to a non-eligible for-profit organization, reassess before use. React/Three.js and transcription/CAD packages retain their own licenses. Do not bundle binaries or original audio in Git. No stock music or third-party logos have been used.

The private Descript project was created before connector availability changed; no narration uploads succeeded. A later retry was rejected by automatic approval review for missing specific external-transfer authorization. The failed import expired with zero uploaded files. Runway video generation is unavailable on the connected free plan; no purchase occurred. Local production does not depend on either service.

Zod is overridden to 4.6.6 within this isolated animation package to address [GHSA-mrhx-c7xc-m3w5](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5). The initial audit reported ten transitive high findings rooted in this single dependency; the patched lock reports zero. Application dependencies are untouched. Final installed-dependency validation is recorded with render QA.
