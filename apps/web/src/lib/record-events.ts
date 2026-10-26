// A bounded SSE parser. Cursors and event references stay in this tab's memory.
import { createContext } from "react";
export const RecordSnapshotReady = createContext(true);
export type RecordFrame = { event: string; id?: string; data: unknown };
const families: Record<string, string[]> = {
  citizen_complaints: ["complaints"],
  complaint_status_events: ["complaints"],
  work_orders: ["work-orders"],
  work_order_actions: ["work-orders"],
  repair_records: ["work-orders", "repairs"],
  verification_records: ["work-orders", "repairs"],
  work_investigation_findings: ["work-orders"],
  incidents: ["incidents"],
  incident_links: ["incidents"],
  water_zones: ["zones"],
  network_junctions: ["junctions"],
  pipe_segments: ["pipes"],
  service_requests: ["service-requests"],
  service_public_updates: ["service-requests"],
  service_request_events: ["service-requests"],
  service_work_order_links: ["service-requests", "work-orders"],
  appointments: [
    "appointments",
    "appointment-requests",
    "service-requests",
    "work-orders",
    "dispatch",
  ],
  appointment_requests: [
    "appointment-requests",
    "appointments",
    "service-requests",
    "dispatch",
  ],
  appointment_events: [
    "appointments",
    "service-requests",
    "work-orders",
    "dispatch",
  ],
  feedback_items: ["feedback"],
};
export function recordFamilies(type: unknown): string[] {
  if (typeof type !== "string" || !type.startsWith("record_changed."))
    throw new Error("Unknown record kind");
  const result = families[type.slice("record_changed.".length)];
  if (!result) throw new Error("Unknown record kind");
  return result;
}
export function recordAffects(path: string, affected?: string[]) {
  const match = /^\/orgs\/[^/?]+(?:\/([^/?]+))?(?:[/?]|$)/.exec(path);
  if (match && !match[1]) return false; // Organization metadata is not an outbox record family.
  return !affected || Boolean(match && affected.includes(match[1]));
}
export class RecordFrameParser {
  private buffer = "";
  push(chunk: string): RecordFrame[] {
    this.buffer = (this.buffer + chunk).replaceAll("\r\n", "\n");
    if (new TextEncoder().encode(this.buffer).length > 256 * 1024)
      throw new Error("Record stream exceeded its bounded frame size");
    const frames: RecordFrame[] = [];
    let boundary: number;
    while ((boundary = this.buffer.indexOf("\n\n")) >= 0) {
      const block = this.buffer.slice(0, boundary);
      this.buffer = this.buffer.slice(boundary + 2);
      let event = "message";
      let id: string | undefined;
      const data: string[] = [];
      for (const line of block.split("\n")) {
        if (line.startsWith("event: ")) event = line.slice(7);
        if (line.startsWith("id: ")) id = line.slice(4);
        if (line.startsWith("data: ")) data.push(line.slice(6));
      }
      if (id && !/^[a-f0-9]{64}$/.test(id))
        throw new Error("Invalid opaque record cursor");
      if (data.length)
        frames.push({ event, id, data: JSON.parse(data.join("\n")) });
    }
    if (frames.length > 100)
      throw new Error("Record stream batch exceeded capacity");
    return frames;
  }
}

export function reconnectDelay(failures: number, random = Math.random()) {
  return (
    Math.min(30000, 1000 * 2 ** Math.min(failures, 5)) * (0.75 + 0.25 * random)
  );
}
