import {
  Activity,
  Droplets,
  AudioLines,
  ScanSearch,
  ClipboardCheck,
  ArrowDown,
} from "lucide-react";

// Original semantic engineering diagram derived from the approved M02/M08 architecture.
// This is explanatory vector UI, not a photograph or a claim of connected hardware.
export function Architecture() {
  return (
    <figure className="architecture">
      <div className="observation-row">
        <section>
          <Droplets aria-hidden="true" />
          <div>
            <h3>HYDRO-WATCH</h3>
            <p>Pressure and flow context</p>
            <small>Supply-state qualification</small>
          </div>
        </section>
        <section>
          <Activity aria-hidden="true" />
          <div>
            <h3>GUARD-5</h3>
            <p>Protected A / B / C</p>
            <small>Independent EXT + BYPASS</small>
            <p className="help">Five independent wetness channels</p>
          </div>
        </section>
        <section>
          <AudioLines aria-hidden="true" />
          <div>
            <h3>HYDRO-EAR</h3>
            <p>Two contact pickups</p>
            <small>One physical sampling clock</small>
          </div>
        </section>
      </div>
      <div className="observation-connectors" aria-hidden="true">
        <ArrowDown />
        <ArrowDown />
        <ArrowDown />
      </div>
      <section className="qualification">
        <ScanSearch aria-hidden="true" />
        <div>
          <h3>Evidence qualification</h3>
          <p>Provenance · quality · faults · uncertainty</p>
          <small>Insufficient support → UNRESOLVED</small>
        </div>
      </section>
      <div className="diagram-connector" aria-hidden="true">
        ↓
      </div>
      <section className="verification-node">
        <ClipboardCheck aria-hidden="true" />
        <div>
          <h3>HYDRO-VERIFY</h3>
          <p>Repair record + independent evidence review</p>
        </div>
      </section>
      <figcaption>PROPOSED DESIGN / NOT PHYSICALLY TESTED</figcaption>
    </figure>
  );
}
