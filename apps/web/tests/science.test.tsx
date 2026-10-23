import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { ScientificChart } from "../src/features/science";

it("preserves missing measurements as gaps instead of zero or interpolated evidence", () => {
  const { container } = render(
    <ScientificChart
      title="Pressure"
      unit="bar"
      x={[0, 1, 2, 3]}
      series={[{ name: "Observed", values: [2, null, 4, 5] }]}
    />,
  );
  const path = container.querySelector("path")!.getAttribute("d")!;
  expect(path.match(/M/g)).toHaveLength(2);
  expect(path.match(/L/g)).toHaveLength(1);
  expect(path).not.toMatch(/NaN|Infinity/);
  expect(screen.getByRole("img", { name: /Pressure/ })).toBeTruthy();
  expect(screen.getByText(/SIMULATION/)).toBeTruthy();
});

it("reports an empty invalid series without manufacturing a chart", () => {
  const { container } = render(
    <ScientificChart
      title="Unavailable pressure"
      unit="bar"
      x={[0, 1]}
      series={[{ name: "Observed", values: [null, null] }]}
    />,
  );
  expect(container.querySelector("path.science-line")).toBeNull();
  expect(screen.getByText("No valid numeric observations.")).toBeTruthy();
});
