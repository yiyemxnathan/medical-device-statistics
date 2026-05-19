import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import SamplingScreen from "./SamplingScreen";

describe("SamplingScreen", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders required sampling inputs", () => {
    render(<SamplingScreen />);

    expect(screen.getByLabelText("标准")).toBeInTheDocument();
    expect(screen.getByLabelText("批量")).toBeInTheDocument();
    expect(screen.getByLabelText("检验水平")).toBeInTheDocument();
    expect(screen.getByLabelText("AQL")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "计算抽样计划" })).toBeInTheDocument();
  });

  it("submits sampling payload and renders the returned plan summary", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        analysis_task_id: 7,
        plan: { sample_size: 80, accept: 2, reject: 3 },
        oc_curve: [
          { quality_level: 0, acceptance_probability: 1 },
          { quality_level: 0.01, acceptance_probability: 0.952 },
        ],
      }),
    } as Response);

    render(<SamplingScreen />);

    fireEvent.change(screen.getByLabelText("标准"), {
      target: { value: "ISO 2859-1" },
    });
    fireEvent.change(screen.getByLabelText("批量"), {
      target: { value: "1200" },
    });
    fireEvent.change(screen.getByLabelText("检验水平"), {
      target: { value: "III" },
    });
    fireEvent.change(screen.getByLabelText("AQL"), {
      target: { value: "0.65" },
    });
    fireEvent.click(screen.getByRole("button", { name: "计算抽样计划" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(fetchMock).toHaveBeenCalledWith("/api/sampling/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        standard_name: "ISO 2859-1",
        standard_version: "2026",
        lot_size: 1200,
        inspection_level: "III",
        aql: "0.65",
        inspection_state: "normal",
      }),
    });

    expect(await screen.findByText("样本量：80")).toBeInTheDocument();
    expect(screen.getByText("接收数：2")).toBeInTheDocument();
    expect(screen.getByText("拒收数：3")).toBeInTheDocument();
    expect(screen.getByText("OC curve")).toBeInTheDocument();
    expect(screen.getByText("0.01")).toBeInTheDocument();
    expect(screen.getByText("0.952")).toBeInTheDocument();
  });
});
