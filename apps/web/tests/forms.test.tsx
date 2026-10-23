import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import {
  ActionForm,
  Field,
  TextArea,
  ErrorPanel,
  Select,
} from "../src/components/ui";
import { ApiError } from "../src/lib/api";
it("provides unique persistent labels for repeated independent forms", () => {
  render(
    <>
      <Field name="reason" label="First reason" />
      <Field name="reason" label="Second reason" />
    </>,
  );
  expect(screen.getByLabelText("First reason").id).not.toBe(
    screen.getByLabelText("Second reason").id,
  );
});
it("supports multiline input with an accessible character counter", () => {
  render(<TextArea name="notes" label="Inspection notes" maxLength={2000} />);
  fireEvent.change(screen.getByLabelText("Inspection notes"), {
    target: { value: "Observed wetness" },
  });
  expect(screen.getByText("16 / 2000 characters")).toBeTruthy();
});
it("retains a deliberate selection when its options are refreshed", () => {
  const { rerender } = render(
    <Select
      name="category"
      label="Service category"
      options={[{ value: "VISIBLE_LEAK", label: "Visible leak" }]}
    />,
  );
  const select = screen.getByLabelText("Service category") as HTMLSelectElement;
  fireEvent.change(select, { target: { value: "VISIBLE_LEAK" } });
  rerender(
    <Select
      name="category"
      label="Service category"
      options={[
        { value: "VISIBLE_LEAK", label: "Visible leak" },
        { value: "LOW_PRESSURE", label: "Low pressure" },
      ]}
    />,
  );
  expect(
    (screen.getByLabelText("Service category") as HTMLSelectElement).value,
  ).toBe("VISIBLE_LEAK");
});
it("never renders a verification conflict as success", () => {
  render(
    <ErrorPanel
      error={new ApiError(412, "VERSION_CONFLICT", "Task changed")}
    />,
  );
  expect(screen.getByRole("alert").textContent).toContain(
    "Review the current version",
  );
  expect(screen.queryByRole("status")).toBeNull();
});
it("disables duplicate submission and reports only a received server receipt", async () => {
  let finish: (r: Response) => void = () => undefined;
  const fetch = vi
    .fn()
    .mockResolvedValueOnce(
      new Response(JSON.stringify({ csrf_token: "synthetic-only" }), {
        status: 200,
      }),
    )
    .mockImplementationOnce(
      () =>
        new Promise<Response>((r) => {
          finish = r;
        }),
    );
  vi.stubGlobal("fetch", fetch);
  render(
    <ActionForm
      path="/auth/logout"
      auth
      build={() => undefined}
      submit="Sign out test"
    />,
  );
  fireEvent.click(screen.getByRole("button", { name: "Sign out test" }));
  await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
  expect((screen.getByRole("button") as HTMLButtonElement).disabled).toBe(true);
  expect(screen.queryByRole("status")).toBeNull();
  finish(
    new Response(JSON.stringify({ message: "Session revoked" }), {
      status: 200,
    }),
  );
  await waitFor(() =>
    expect(screen.getByRole("status").textContent).toContain("Session revoked"),
  );
});
