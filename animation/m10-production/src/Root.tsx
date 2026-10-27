import { Composition, Series } from "remotion";
import { PipelineScene } from "./scenes/Pipeline";
import { GuardScene } from "./scenes/Guard";
import { AcousticScene } from "./scenes/Acoustic";
import { TownScene } from "./scenes/Town";
import { QualificationScene } from "./scenes/Qualification";
import { WorkflowScene } from "./scenes/Workflow";
import { VerificationScene } from "./scenes/Verification";
import { EvidenceScene } from "./scenes/Evidence";
import { SoftwareScene } from "./scenes/Software";
import { RigScene } from "./scenes/Rig";
import { Film } from "./Film";
import timeline from "./data/timeline.json";

const StyleTest = () => (
  <Series>
    <Series.Sequence
      durationInFrames={240}
      name="Connected pipe and illustrative leak"
      premountFor={30}
    >
      <PipelineScene />
    </Series.Sequence>
    <Series.Sequence
      durationInFrames={300}
      name="Source CAD and five channels"
      premountFor={30}
    >
      <GuardScene />
    </Series.Sequence>
    <Series.Sequence
      durationInFrames={240}
      name="One common-clock ADC"
      premountFor={30}
    >
      <AcousticScene />
    </Series.Sequence>
  </Series>
);

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="HYDROOVERITYFullDraft"
        component={Film}
        durationInFrames={timeline.duration_frames}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="M10StyleTest"
        component={StyleTest}
        durationInFrames={780}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="Pipeline"
        component={PipelineScene}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="Guard5"
        component={GuardScene}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="Acoustic"
        component={AcousticScene}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="Introduction"
        component={TownScene}
        durationInFrames={429}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ intro: true, opening: true }}
      />
      <Composition
        id="Town"
        component={TownScene}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="Qualification"
        component={QualificationScene}
        durationInFrames={360}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ mode: "supply" as const }}
      />
      <Composition
        id="Workflow"
        component={WorkflowScene}
        durationInFrames={360}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ mode: "service" as const }}
      />
      <Composition
        id="Verification"
        component={VerificationScene}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ outcomes: true }}
      />
      <Composition
        id="Benchmark"
        component={EvidenceScene}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ kind: "guard" as const }}
      />
      <Composition
        id="Software"
        component={SoftwareScene}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          asset: "home.png",
          title: "One accountable\nworkflow.",
          note: "Actual development application. Synthetic records. No live hardware or field deployment.",
        }}
      />
      <Composition
        id="DigitalRig"
        component={RigScene}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
