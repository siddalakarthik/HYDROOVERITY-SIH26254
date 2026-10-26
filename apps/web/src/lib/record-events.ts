// A bounded SSE parser. Cursors and event references stay in this tab's memory.
export type RecordFrame = { event: string; id?: string; data: unknown };
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
