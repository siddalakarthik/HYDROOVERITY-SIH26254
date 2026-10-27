import { bundle } from "@remotion/bundler";
import { selectComposition, renderStill } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const timeline = JSON.parse(fs.readFileSync("src/data/timeline.json", "utf8"));
const browserExecutable =
  process.env.M10_CHROME ??
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const serveUrl = await bundle({
  entryPoint: path.join(root, "src/index.ts"),
  publicDir: path.join(root, "public"),
  outDir: path.join(root, "local/review-bundle"),
});
const composition = await selectComposition({
  serveUrl,
  id: "HYDROOVERITYFullDraft",
  browserExecutable,
});
fs.mkdirSync("local/scene-review", { recursive: true });
const requested = new Set(process.argv.slice(2));
for (const scene of timeline.scenes.filter(
  (s) => requested.size === 0 || requested.has(s.id),
)) {
  const frame = scene.from + Math.min(100, Math.floor(scene.duration * 0.5));
  const output = path.join(root, `local/scene-review/${scene.id}.png`);
  await renderStill({
    serveUrl,
    composition,
    frame,
    output,
    scale: 0.5,
    imageFormat: "png",
    browserExecutable,
    chromiumOptions: { gl: "angle" },
  });
  console.log(scene.id, frame, scene.kind);
}
fs.writeFileSync(
  "local/scene-review/rendered.json",
  JSON.stringify(
    {
      baseline: timeline.baseline,
      frames: timeline.scenes.length,
      status: "RENDERED_NOT_YET_VISUALLY_REVIEWED",
    },
    null,
    2,
  ),
);
