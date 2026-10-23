"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useId, useState } from "react";
import { api, date, label, orgPath, uuid, type Model } from "@/lib/api";
import {
  ActionForm,
  Badge,
  Empty,
  ErrorPanel,
  Heading,
  Notice,
  ResourceState,
  Select,
  useResource,
  value,
} from "@/components/ui";

type Datum = Model<"M06Case">["data"];
const number = (v: number | null | undefined, digits = 2) =>
  v == null ? "Unavailable" : v.toFixed(digits);

export function ScientificChart({
  title,
  x,
  series,
  unit,
}: {
  title: string;
  x: (number | null)[];
  series: { name: string; values: (number | null)[] }[];
  unit: string;
}) {
  const id = useId();
  const values = series
    .flatMap((s) => s.values)
    .filter((v): v is number => v != null && Number.isFinite(v));
  if (!values.length)
    return <Empty title={title}>No valid numeric observations.</Empty>;
  const low = Math.min(...values),
    high = Math.max(...values);
  const first = x[0] ?? 0,
    last = x[x.length - 1] ?? 1;
  const px = (v: number) => 66 + ((v - first) / (last - first || 1)) * 610;
  const py = (v: number) => 170 - ((v - low) / (high - low || 1)) * 140;
  return (
    <figure className="science-chart panel">
      <figcaption id={id}>
        {title} <span className="meta">{unit} · SIMULATION</span>
      </figcaption>
      <svg viewBox="0 0 720 215" role="img" aria-labelledby={id}>
        <desc>
          Modeled series; gaps indicate missing data. Numeric samples are
          available in the observation export.
        </desc>
        {[30, 100, 170].map((y) => (
          <line
            key={y}
            x1="66"
            x2="676"
            y1={y}
            y2={y}
            stroke="currentColor"
            opacity=".15"
          />
        ))}
        <text x="4" y="35">
          {number(high)}
        </text>
        <text x="4" y="174">
          {number(low)}
        </text>
        <text x="66" y="202">
          {number(first, 3)} s
        </text>
        <text x="676" y="202" textAnchor="end">
          {number(last, 3)} s
        </text>
        {series.map((s, index) => {
          let connected = false;
          const path = s.values
            .map((v, i) => {
              if (v == null || x[i] == null) {
                connected = false;
                return "";
              }
              const command = connected ? "L" : "M";
              connected = true;
              return `${command}${px(x[i]!).toFixed(2)},${py(v).toFixed(2)}`;
            })
            .join(" ");
          return (
            <path
              key={s.name}
              d={path}
              className={`science-line line-${index}`}
              fill="none"
              strokeWidth="2"
            />
          );
        })}
      </svg>
      <div className="science-legend">
        {series.map((s, i) => (
          <span key={s.name} className={`legend-${i}`}>
            {i + 1}. {s.name}
          </span>
        ))}
      </div>
    </figure>
  );
}

function Watch({ data }: { data: Model<"M06Watch"> }) {
  return (
    <>
      <div className="science-metrics">
        <div>
          <span>Final supply state</span>
          <strong>{data.state.at(-1)}</strong>
        </div>
        <div>
          <span>Suspicious samples</span>
          <strong>
            {data.watch_alarm.filter(Boolean).length} /{" "}
            {data.watch_alarm.length}
          </strong>
        </div>
        <div>
          <span>Residual threshold</span>
          <strong>{number(data.threshold_lpm)} L/min</strong>
        </div>
        <div>
          <span>Unresolved samples</span>
          <strong>
            {data.qualified_outcome.filter((v) => v === "UNRESOLVED").length}
          </strong>
        </div>
      </div>
      <ScientificChart
        title="Hydraulic pressure"
        x={data.time_s}
        unit="bar"
        series={[{ name: "Pressure", values: data.pressure_bar }]}
      />
      <ScientificChart
        title="Measured flow balance"
        x={data.time_s}
        unit="L/min"
        series={[
          { name: "Inlet", values: data.inlet_lpm },
          { name: "Customer outlet", values: data.customer_outlet_lpm },
        ]}
      />
      <ScientificChart
        title="Unexplained flow and decision threshold"
        x={data.time_s}
        unit="L/min"
        series={[
          { name: "Residual", values: data.residual_lpm },
          {
            name: "Threshold",
            values: data.time_s.map(() => data.threshold_lpm),
          },
        ]}
      />
      <Notice>
        Only steady, known-storage observations support the water-balance
        decision. Customer outflow is already included; demand is not subtracted
        twice. Suspicion is not a confirmed leak.
      </Notice>
      {data.urgent_events.length > 0 && (
        <section className="panel">
          <h2>Independent fault / urgent observations</h2>
          <ul>
            {data.urgent_events.map((v, i) => (
              <li key={i}>
                {v.time_s} s · {label(v.reason)}
              </li>
            ))}
          </ul>
        </section>
      )}
    </>
  );
}

function Guard({ data }: { data: Model<"M06Guard"> }) {
  return (
    <section className="panel">
      <h2>GUARD-5 · five independent wetness channels</h2>
      <Badge>{label(data.outcome)}</Badge>
      <div className="science-channels">
        {data.channels.map((channel, index) => (
          <article key={channel}>
            <h3>{channel}</h3>
            <strong>
              {data.wet.filter((row) => row[index]).length} / {data.wet.length}{" "}
              wet samples
            </strong>
            <p>
              Health: <b>{data.health[index]}</b>
            </p>
            <svg
              viewBox="0 0 180 30"
              role="img"
              aria-label={`${channel} modeled wetness timeline; unknown sensor health`}
            >
              {data.wet.map((row, i) => (
                <rect
                  key={i}
                  x={(i * 180) / data.wet.length}
                  y={row[index] ? 2 : 23}
                  width={180 / data.wet.length}
                  height={row[index] ? 26 : 5}
                  fill="currentColor"
                />
              ))}
            </svg>
            <p className="meta">0–{data.time_s.at(-1)} s</p>
          </article>
        ))}
      </div>
      <dl className="details-grid">
        <div>
          <dt>Collection concern</dt>
          <dd>
            {data.blockage_suspected
              ? "Suspected"
              : "Not detected — not excluded"}
          </dd>
        </div>
        <div>
          <dt>Service challenge</dt>
          <dd>{label(data.service)}</dd>
        </div>
        <div>
          <dt>Reference pad / multizone alarm</dt>
          <dd>
            {String(data.reference_pad_alarm)} /{" "}
            {String(data.reference_multizone_alarm)}
          </dd>
        </div>
      </dl>
      <Notice tone="warning">
        No wetness is not proof of no leak. UNKNOWN health remains unknown.
        Collector performance has not been physically verified.
      </Notice>
    </section>
  );
}

function Ear({ data }: { data: Model<"M06Ear"> }) {
  return (
    <>
      <section className="panel">
        <h2>HYDRO-EAR · qualified acoustic investigation</h2>
        <Badge>{label(data.outcome)}</Badge>
        <p className="science-interval">
          {data.interval_m
            ? `${number(data.interval_m[0], 3)}–${number(data.interval_m[1], 3)} m candidate interval`
            : "No qualified localization interval"}
        </p>
        <dl className="details-grid">
          <div>
            <dt>Clock</dt>
            <dd>
              {data.shared_clock
                ? "One shared modeled sampling clock"
                : "Invalid synchronization"}
            </dd>
          </div>
          <div>
            <dt>Eligible modeled span</dt>
            <dd>
              {data.eligible_path ? `${number(data.span_m)} m` : "Ineligible"}
            </dd>
          </div>
          <div>
            <dt>Assumed wave speed</dt>
            <dd>
              {number(data.assumed_speed_mps)} m/s ±{" "}
              {number(data.speed_fraction * 100)}%
            </dd>
          </div>
          <div>
            <dt>Sampling / display stride</dt>
            <dd>
              {data.sample_rate_hz} Hz / every {data.preview_stride} samples
            </dd>
          </div>
          <div>
            <dt>Peak correlation / ratio</dt>
            <dd>
              {number(data.peak_correlation, 3)} / {number(data.peak_ratio, 3)}
            </dd>
          </div>
        </dl>
      </section>
      <ScientificChart
        title="Paired acoustic waveform preview"
        x={data.time_s}
        unit="modeled amplitude"
        series={data.waveforms.map((values, i) => ({
          name: `Channel ${i + 1}`,
          values,
        }))}
      />
      <ScientificChart
        title="Filtered cross-correlation"
        x={data.correlation_lag_s}
        unit="correlation amplitude"
        series={[{ name: "Correlation", values: data.correlation }]}
      />
      <Notice tone="warning">
        This is an interval estimate under wave-speed and path assumptions, not
        an exact crack location. Accepted intervals can be wrong. Weak or
        missing sound does not exclude a leak.
      </Notice>
    </>
  );
}

function Waterfall({ data }: { data: Datum }) {
  const hydraulic =
    data.module === "HYDRO-WATCH"
      ? data
      : data.module === "HYDRO-VERIFY"
        ? data.watch
        : null;
  const collar =
    data.module === "GUARD-5"
      ? data
      : data.module === "HYDRO-VERIFY"
        ? data.guard
        : null;
  const acoustic =
    data.module === "HYDRO-EAR"
      ? data
      : data.module === "HYDRO-VERIFY"
        ? data.ear
        : null;
  const steps = [
    [
      "Hydraulic observation",
      hydraulic
        ? `${hydraulic.time_s.length} modeled samples; missing samples remain gaps.`
        : "Not part of this recording.",
    ],
    [
      "Supply-state qualification",
      hydraulic
        ? `Observed states: ${[...new Set(hydraulic.state)].join(", ")}.`
        : "No hydraulic qualification inferred.",
    ],
    [
      "Suspicious water loss",
      hydraulic
        ? `${hydraulic.watch_alarm.filter(Boolean).length} flagged samples. Unknown storage and invalid conditions abstain.`
        : "No water-loss conclusion inferred.",
    ],
    [
      "GUARD-5 interpretation",
      collar
        ? `${label(collar.outcome)}. All health states UNKNOWN.`
        : "Not joined to an unrelated collar scenario.",
    ],
    [
      "Acoustic investigation",
      acoustic
        ? `${label(acoustic.outcome)}. An interval is only a qualified candidate.`
        : "No acoustic localization inferred.",
    ],
    [
      "Evidence assessment",
      data.module === "HYDRO-VERIFY"
        ? `${data.outcome} — modeled residual comparison only.`
        : "Simulation-only observations; no confirmed field outcome.",
    ],
    [
      "Operational recommendation",
      "Review assumptions and obtain appropriate independent evidence. No incident, work order or repair is created.",
    ],
  ];
  return (
    <section className="panel">
      <h2>Evidence waterfall</h2>
      <p className="help">
        Independent M05 scenarios are not a coupled fluid-acoustic model.
      </p>
      <ol className="science-waterfall">
        {steps.map(([title, body]) => (
          <li key={title}>
            <details>
              <summary>{title}</summary>
              <p>{body}</p>
            </details>
          </li>
        ))}
      </ol>
    </section>
  );
}

function Historical({ detail }: { detail: Model<"M06Detail"> }) {
  const aggregate = detail.snapshot.historical_benchmark;
  const acoustic = aggregate.acoustics as Record<string, number>;
  const guard = aggregate.guard as Record<
    string,
    Record<string, Record<string, number>>
  >;
  return (
    <section className="panel">
      <h2>Published M05 benchmark · all results retained</h2>
      <Notice tone="warning">
        PPT profile: acoustic eligible {acoustic.eligible}, accepted{" "}
        {acoustic.accepted}, unresolved {acoustic.unresolved};{" "}
        {acoustic.confidently_wrong_intervals} accepted wrong intervals. These
        historical aggregates are not a new evaluation of this single replay.
      </Notice>
      <div
        className="table-scroll"
        tabIndex={0}
        role="region"
        aria-label="Scientific observation table"
      >
        <table className="science-comparison">
          <caption>
            GUARD-5 and reference F1 scores · identical M05 denominators
          </caption>
          <thead>
            <tr>
              <th>Regime</th>
              <th>GUARD-5</th>
              <th>Pad</th>
              <th>Multizone</th>
              <th>Cases per method</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(guard).map(([regime, result]) => (
              <tr key={regime}>
                <th>{label(regime)}</th>
                <td>{number(result.guard5.f1, 3)}</td>
                <td>{number(result.pad.f1, 3)}</td>
                <td>{number(result.multizone.f1, 3)}</td>
                <td>{result.guard5.n}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <details>
        <summary>Complete historical benchmark and denominators</summary>
        <pre className="science-json">{JSON.stringify(aggregate, null, 2)}</pre>
      </details>
    </section>
  );
}

function Replay({ org, detail }: { org: string; detail: Model<"M06Detail"> }) {
  const [offset, setOffset] = useState<number | null>(0);
  const [playing, setPlaying] = useState(false);
  const [page, setPage] = useState<Model<"M06Frames">>();
  const [error, setError] = useState<unknown>();
  useEffect(() => {
    if (!playing || offset === null) return;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      void api<Model<"M06Frames">>(
        orgPath(
          org,
          `/scientific-replays/${uuid(detail.id)}/frames?offset=${offset}&limit=10`,
        ),
        { signal: controller.signal },
      )
        .then((result) => {
          if (!controller.signal.aborted) {
            setPage(result.data);
            setOffset(result.data.next_offset);
            if (result.data.next_offset === null) setPlaying(false);
          }
        })
        .catch((reason) => {
          if (!controller.signal.aborted) {
            setError(reason);
            setPlaying(false);
          }
        });
    }, 1000);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [playing, offset, org, detail.id]);
  return (
    <section className="panel">
      <h2>Deterministic observation replay</h2>
      <p>
        Ten recorded samples per batch; playback speed is not physical elapsed
        time. Each batch checks current access.
      </p>
      <div className="actions">
        <button
          className="button"
          disabled={offset === null}
          onClick={() => {
            setError(undefined);
            setPlaying(!playing);
          }}
        >
          {playing ? "Pause replay" : "Play replay"}
        </button>
        <button
          className="button secondary"
          onClick={() => {
            setPlaying(false);
            setOffset(0);
            setPage(undefined);
            setError(undefined);
          }}
        >
          Restart replay
        </button>
      </div>
      <p role="status">
        {offset === null
          ? "Replay complete"
          : playing
            ? "Replaying persisted observations"
            : "Replay paused"}
        {page
          ? ` · ${page.items.at(-1)!.sequence + 1} / ${page.total_frames} samples`
          : ""}
      </p>
      {error != null && <ErrorPanel error={error} />}
      {page && (
        <details open>
          <summary>Current batch · SIMULATION</summary>
          <div
            className="table-scroll"
            tabIndex={0}
            role="region"
            aria-label="Scientific observation table"
          >
            <table>
              <caption>Recorded simulation samples</caption>
              <thead>
                <tr>
                  <th>Sequence</th>
                  <th>Time (s)</th>
                  <th>Values and qualification</th>
                </tr>
              </thead>
              <tbody>
                {page.items.map((frame) => (
                  <tr key={frame.sequence}>
                    <td>{frame.sequence}</td>
                    <td>{number(frame.time_s, 3)}</td>
                    <td>
                      <code className="science-values">
                        {JSON.stringify(frame.values)}
                      </code>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      )}
    </section>
  );
}

function Investigation({ org, id }: { org: string; id: string }) {
  const resource = useResource<Model<"M06Detail">>(
    orgPath(org, `/scientific-replays/${uuid(id)}`),
  );
  const [exportError, setExportError] = useState<unknown>();
  const detail = resource.data;
  async function exportData() {
    setExportError(undefined);
    try {
      const result = await api<Model<"M06Detail">>(
        orgPath(org, `/scientific-replays/${uuid(id)}/export`),
      );
      const url = URL.createObjectURL(
        new Blob([JSON.stringify(result.data, null, 2)], {
          type: "application/json",
        }),
      );
      const link = document.createElement("a");
      link.href = url;
      link.download = `HYDROOVERITY_SIMULATION_${id}.json`;
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (error) {
      setExportError(error);
    }
  }
  return (
    <>
      <Link href={`/app/${org}/simulations`}>← Scenario lab</Link>
      <ResourceState {...resource}>
        {detail && (
          <>
            <Heading
              eyebrow="Scientific command center · SIMULATION"
              title={detail.name}
              action={
                <button
                  className="button secondary"
                  onClick={() => void exportData()}
                >
                  Export observations
                </button>
              }
            >
              Reproducible M05 evidence · {detail.module} · no physical
              validation
            </Heading>
            {exportError != null && <ErrorPanel error={exportError} />}
            <div className="science-provenance">
              <Badge>SIMULATION MODE</Badge>
              <span>
                Imported {date(detail.created_at)} · historical modeled data,
                not a fresh measurement
              </span>
              <details>
                <summary>Provenance and integrity</summary>
                <p className="science-values">
                  Configuration: {detail.configuration_hash}
                  <br />
                  Content: {detail.content_hash}
                  <br />
                  Algorithm: {detail.algorithm_version} ·{" "}
                  {detail.algorithm_source_hash}
                </p>
              </details>
            </div>
            <Waterfall data={detail.snapshot.case.data} />
            {detail.snapshot.case.data.module === "HYDRO-WATCH" && (
              <Watch data={detail.snapshot.case.data} />
            )}
            {detail.snapshot.case.data.module === "GUARD-5" && (
              <Guard data={detail.snapshot.case.data} />
            )}
            {detail.snapshot.case.data.module === "HYDRO-EAR" && (
              <Ear data={detail.snapshot.case.data} />
            )}
            {detail.snapshot.case.data.module === "HYDRO-VERIFY" && (
              <>
                <section className="panel">
                  <h2>HYDRO-VERIFY · modeled outcome</h2>
                  <p className="science-interval">
                    {detail.snapshot.case.data.outcome}
                  </p>
                  <p>
                    Before:{" "}
                    {number(detail.snapshot.case.data.before_residual_lpm)}{" "}
                    L/min · After:{" "}
                    {number(detail.snapshot.case.data.after_residual_lpm)} L/min
                  </p>
                  <Notice>
                    No operational repair is verified by this modeled result.
                    Missing comparable evidence remains NOT_VERIFIABLE.
                  </Notice>
                </section>
                <Watch data={detail.snapshot.case.data.watch} />
                <Notice>
                  Independent engine outputs joined as in M05; these module
                  timelines are not synchronized field recordings or a coupled
                  fluid-acoustic model.
                </Notice>
                <Guard data={detail.snapshot.case.data.guard} />
                <Ear data={detail.snapshot.case.data.ear} />
              </>
            )}
            <Replay key={detail.id} org={org} detail={detail} />
            <Historical detail={detail} />
            <section className="panel">
              <h2>Limitations and unresolved conditions</h2>
              <ul>
                {detail.limitations.map((v) => (
                  <li key={v}>{v}</li>
                ))}
              </ul>
            </section>
          </>
        )}
      </ResourceState>
    </>
  );
}

export function Science({ org, id }: { org: string; id?: string }) {
  const router = useRouter();
  const [page, setPage] = useState(0);
  const catalogue = useResource<Model<"M06Catalogue">>(
    id ? null : orgPath(org, "/scientific-replays/catalogue"),
  );
  const runs = useResource<Model<"M06ReplayList">>(
    id ? null : orgPath(org, `/scientific-replays?offset=${page}`),
  );
  if (id) return <Investigation key={id} org={org} id={id} />;
  return (
    <>
      <Heading
        eyebrow="SIMULATION MODE · Engineering workspace"
        title="Scientific scenario lab"
      >
        Investigate the evidence. Preserve the uncertainty.
      </Heading>
      <Notice>
        Import an observation-only M05 recording. This is deterministic replay
        of verified outputs, not a new randomized experiment or a live hardware
        connection.
      </Notice>
      <ResourceState {...catalogue}>
        {catalogue.data && (
          <ActionForm
            path={orgPath(org, "/scientific-replays")}
            build={(form) => ({ scenario_code: value(form, "scenario") })}
            submit="Import scenario"
            onDone={(result) =>
              router.push(
                `/app/${org}/simulations/${(result as Model<"M06Replay">).id}`,
              )
            }
          >
            <Select
              name="scenario"
              label="Scientific scenario"
              options={catalogue.data.items.map((v) => ({
                value: v.code,
                label: `${v.module} · ${v.code} · ${v.name}`,
              }))}
            />
          </ActionForm>
        )}
      </ResourceState>
      <section className="panel">
        <h2>Persisted investigations</h2>
        <ResourceState {...runs}>
          {runs.data?.items.length ? (
            <>
              <ul className="science-run-list">
                {runs.data.items.map((run) => (
                  <li key={run.id}>
                    <Link href={`/app/${org}/simulations/${run.id}`}>
                      <strong>{run.name}</strong>
                      <span>
                        {run.module} · {date(run.created_at)}
                      </span>
                      <Badge>SIMULATION</Badge>
                    </Link>
                  </li>
                ))}
              </ul>
              <div className="actions">
                <button
                  className="button secondary"
                  disabled={!page}
                  onClick={() => setPage(Math.max(0, page - 25))}
                >
                  Previous
                </button>
                <button
                  className="button secondary"
                  disabled={runs.data.next_offset === null}
                  onClick={() => setPage(runs.data!.next_offset!)}
                >
                  Next
                </button>
              </div>
            </>
          ) : (
            <Empty title="No simulation imports yet">
              Choose a supported scenario to begin a real, persisted
              investigation.
            </Empty>
          )}
        </ResourceState>
      </section>
    </>
  );
}
