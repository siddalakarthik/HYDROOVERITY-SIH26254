import { AbsoluteFill, Sequence, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import timeline from "./data/timeline.json";
import { TownScene } from "./scenes/Town";
import { PipelineScene } from "./scenes/Pipeline";
import { GuardScene } from "./scenes/Guard";
import { AcousticScene } from "./scenes/Acoustic";
import { QualificationScene } from "./scenes/Qualification";
import { WorkflowScene } from "./scenes/Workflow";
import { VerificationScene } from "./scenes/Verification";
import { EvidenceScene } from "./scenes/Evidence";
import { SoftwareScene } from "./scenes/Software";
import { RigScene } from "./scenes/Rig";
import { DispatchScene } from "./scenes/Dispatch";
import { FieldScene } from "./scenes/Field";
import type { ComponentProps } from "react";

type Scene = { kind: string; props: Record<string, unknown> };
export function SceneView({ scene }: { scene: Scene }) {
  const p = scene.props;
  switch (scene.kind) {
    case "town":
      return <TownScene {...(p as ComponentProps<typeof TownScene>)} />;
    case "pipe":
      return <PipelineScene />;
    case "guard":
      return <GuardScene {...(p as ComponentProps<typeof GuardScene>)} />;
    case "ear":
      return <AcousticScene {...(p as ComponentProps<typeof AcousticScene>)} />;
    case "qualification":
      return (
        <QualificationScene
          {...(p as ComponentProps<typeof QualificationScene>)}
        />
      );
    case "workflow":
      return <WorkflowScene {...(p as ComponentProps<typeof WorkflowScene>)} />;
    case "verification":
      return (
        <VerificationScene
          {...(p as ComponentProps<typeof VerificationScene>)}
        />
      );
    case "evidence":
      return <EvidenceScene {...(p as ComponentProps<typeof EvidenceScene>)} />;
    case "software":
      return <SoftwareScene {...(p as ComponentProps<typeof SoftwareScene>)} />;
    case "rig":
      return <RigScene />;
    case "booking":
      return <DispatchScene />;
    case "concurrency":
      return <DispatchScene concurrency />;
    case "repair":
      return <FieldScene />;
    case "tests":
      return <FieldScene tests />;
    default:
      throw new Error(`Unimplemented scene ${scene.kind}`);
  }
}
export function Film({ narration = true }: { narration?: boolean }) {
  return (
    <AbsoluteFill style={{ background: "#071623" }}>
      {/* One manifest owns all scene edits; absolute word anchors never accumulate clip rounding. */}
      {timeline.scenes.map((scene) => (
        <Sequence
          key={scene.id}
          name={`${scene.id} ${scene.opening_phrase}`}
          from={scene.from}
          durationInFrames={scene.duration}
          premountFor={30}
        >
          <SceneView scene={scene as Scene} />
        </Sequence>
      ))}
      {narration && (
        <Audio
          src={staticFile("audio/HYDROOVERITY_M10_VOICE_MASTER.wav")}
          premountFor={30}
        />
      )}
    </AbsoluteFill>
  );
}
