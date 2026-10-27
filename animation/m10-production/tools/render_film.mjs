/** Render video without per-frame audio extraction, then mux the untouched PCM master. */
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";
const root = process.cwd();
const preview = process.argv.includes("--preview");
const smoke = process.argv.includes("--smoke");
const concurrency = Number(process.env.M10_CONCURRENCY ?? 2);
if (!Number.isInteger(concurrency) || concurrency < 1 || concurrency > 4)
  throw new Error("Use 1–4 bounded workers.");
const chrome =
  process.env.M10_CHROME ??
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const ffmpeg =
  process.env.M10_FFMPEG ??
  path.join(
    root,
    "node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe",
  );
const name = smoke
  ? "M10_SILENT_SMOKE"
  : preview
    ? "HYDROOVERITY_M10_DRAFT_540P"
    : "HYDROOVERITY_M10_MASTER_1080P";
const started = Date.now();
function files(dir) {
  return fs
    .readdirSync(dir, { withFileTypes: true })
    .flatMap((e) =>
      e.isDirectory()
        ? files(path.join(dir, e.name))
        : [path.join(dir, e.name)],
    );
}
const sourceHashes = Object.fromEntries(
  files("src").map((file) => [
    file.replaceAll("\\", "/"),
    createHash("sha256").update(fs.readFileSync(file)).digest("hex"),
  ]),
);
const serveUrl = await bundle({
  entryPoint: path.join(root, "src/index.ts"),
  publicDir: path.join(root, "public"),
});
const inputProps = { narration: false };
const composition = await selectComposition({
  serveUrl,
  id: "HYDROOVERITYFullDraft",
  inputProps,
  browserExecutable: chrome,
});
fs.mkdirSync("renders", { recursive: true });
let last = -1;
await renderMedia({
  serveUrl,
  composition,
  inputProps,
  browserExecutable: chrome,
  outputLocation: `renders/${name}.silent.mp4`,
  codec: "h264",
  pixelFormat: "yuv420p",
  scale: preview || smoke ? 0.5 : 1,
  crf: preview || smoke ? 22 : 18,
  concurrency,
  chromiumOptions: { gl: "angle" },
  muted: true,
  ...(smoke ? { frameRange: [0, 119] } : {}),
  onProgress: ({ renderedFrames, encodedFrames, progress }) => {
    const pct = Math.floor(progress * 100);
    if (pct !== last) {
      last = pct;
      console.log(
        JSON.stringify({
          pct,
          renderedFrames,
          encodedFrames,
          elapsedSeconds: Math.round((Date.now() - started) / 1000),
        }),
      );
    }
  },
});
const duration = (smoke ? 120 : composition.durationInFrames) / composition.fps;
const args = [
  "-y",
  "-v",
  "error",
  "-i",
  `renders/${name}.silent.mp4`,
  "-i",
  "public/audio/HYDROOVERITY_M10_VOICE_MASTER.wav",
  "-map",
  "0:v:0",
  "-map",
  "1:a:0",
  "-c:v",
  "copy",
  "-c:a",
  "aac",
  "-b:a",
  "192k",
  "-ar",
  "48000",
  "-af",
  "apad",
  "-t",
  String(duration),
  "-movflags",
  "+faststart",
  `renders/${name}.mp4`,
];
const result = spawnSync(ffmpeg, args, { stdio: "inherit" });
if (result.status !== 0) throw new Error(`Mux failed: ${result.status}`);
fs.writeFileSync(
  `local/${name}.render.json`,
  JSON.stringify(
    {
      name,
      completed: new Date().toISOString(),
      seconds: (Date.now() - started) / 1000,
      duration,
      concurrency,
      scale: preview || smoke ? 0.5 : 1,
      sourceHashes,
      audio:
        "One PCM voice master; no per-part AAC seams; apad only after narration",
      status: "RENDERED_QA_PENDING",
    },
    null,
    2,
  ),
);
console.log(`Completed renders/${name}.mp4`);
