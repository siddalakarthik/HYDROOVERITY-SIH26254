import { ApiError, type Model } from "./api";

export function position(
  longitude: number,
  latitude: number,
): [number, number] {
  if (
    !Number.isFinite(longitude) ||
    !Number.isFinite(latitude) ||
    Math.abs(longitude) > 180 ||
    Math.abs(latitude) > 90
  )
    throw new ApiError(
      422,
      "INVALID_GEOMETRY",
      "Use finite WGS84 longitude −180…180 and latitude −90…90.",
    );
  return [longitude, latitude];
}
export function lineCoordinates(text: string): [number, number][] {
  const coordinates = text
    .trim()
    .split("\n")
    .map((row) => {
      const pair = row.split(",").map((v) => v.trim());
      if (pair.length !== 2 || pair.some((v) => v === ""))
        throw new ApiError(
          422,
          "INVALID_GEOMETRY",
          "Enter one longitude, latitude pair per line.",
        );
      return position(Number(pair[0]), Number(pair[1]));
    });
  if (coordinates.length < 2 || coordinates.length > 10000)
    throw new ApiError(
      422,
      "INVALID_GEOMETRY",
      "A pipe requires 2–10,000 coordinate pairs.",
    );
  return coordinates;
}
export function featureCollection(
  junctions: Model<"Junction">[],
  pipes: Model<"Pipe">[],
) {
  return {
    type: "FeatureCollection" as const,
    features: [
      ...pipes.map((p) => ({
        type: "Feature" as const,
        id: p.id,
        geometry: p.geometry,
        properties: { id: p.id, kind: "pipes", quality: p.topology_quality },
      })),
      ...junctions.map((j) => ({
        type: "Feature" as const,
        id: j.id,
        geometry: j.geometry,
        properties: {
          id: j.id,
          kind: "junctions",
          quality: j.topology_quality,
        },
      })),
    ],
  };
}
