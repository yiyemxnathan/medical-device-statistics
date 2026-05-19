import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("App", () => {
  it("renders controlled statistics workbench navigation", () => {
    render(<App />);

    expect(screen.getByText("医疗器械统计工作台")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "抽样检验" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "统计分析" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "报告" })).toBeInTheDocument();
  });
});
