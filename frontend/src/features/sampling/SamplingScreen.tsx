import { useState } from "react";
import type { FormEvent } from "react";
import { calculateSamplingPlan } from "../../api/client";
import type { SamplingPlanResponse } from "../../api/client";

type SamplingDisplayResult = SamplingPlanResponse & SamplingPlanResponse["plan"];

const standardVersions: Record<string, string> = {
  "GB/T 2828.1": "2012",
  "ISO 2859-1": "2026",
};

export default function SamplingScreen() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<SamplingDisplayResult | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const standardName = String(formData.get("standard_name") ?? "GB/T 2828.1");

    setIsLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await calculateSamplingPlan({
        standard_name: standardName,
        standard_version: standardVersions[standardName],
        lot_size: Number(formData.get("lot_size") ?? 0),
        inspection_level: String(formData.get("inspection_level") ?? "II"),
        aql: String(formData.get("aql") ?? "1.0"),
        inspection_state: String(formData.get("inspection_state") ?? "normal"),
      });
      setResult({ ...response, ...response.plan });
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "计算抽样计划失败");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="panel">
      <h2>抽样检验</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            标准
            <select name="standard_name" defaultValue="GB/T 2828.1">
              <option>GB/T 2828.1</option>
              <option>ISO 2859-1</option>
            </select>
          </label>
          <label>
            批量
            <input name="lot_size" type="number" defaultValue={800} min={1} />
          </label>
          <label>
            检验水平
            <select name="inspection_level" defaultValue="II">
              <option>I</option>
              <option>II</option>
              <option>III</option>
            </select>
          </label>
          <label>
            AQL
            <input name="aql" defaultValue="1.0" />
          </label>
          <label>
            检验状态
            <select name="inspection_state" defaultValue="normal">
              <option value="normal">normal</option>
            </select>
          </label>
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? "计算中..." : "计算抽样计划"}
        </button>
      </form>
      {error ? <p role="alert">{error}</p> : null}
      {result ? (
        <div className="result-summary">
          <p>样本量：{result.sample_size}</p>
          <p>接收数：{result.accept}</p>
          <p>拒收数：{result.reject}</p>
          <h3>OC curve</h3>
          <table>
            <thead>
              <tr>
                <th>quality_level</th>
                <th>acceptance_probability</th>
              </tr>
            </thead>
            <tbody>
              {result.oc_curve.map((point) => (
                <tr key={point.quality_level}>
                  <td>{point.quality_level}</td>
                  <td>{point.acceptance_probability}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}
