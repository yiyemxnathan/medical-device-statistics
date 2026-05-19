export type SamplingPlanRequest = {
  standard_name: string;
  standard_version: string;
  lot_size: number;
  inspection_level: string;
  aql: string;
  inspection_state: string;
};

export type SamplingPlanResult = {
  sample_size: number;
  accept: number;
  reject: number;
};

export type OCCurvePoint = {
  quality_level: number;
  acceptance_probability: number;
};

export type SamplingPlanResponse = {
  analysis_task_id?: number;
  plan: SamplingPlanResult;
  oc_curve: OCCurvePoint[];
};

export async function calculateSamplingPlan(
  payload: SamplingPlanRequest,
): Promise<SamplingPlanResponse> {
  const response = await fetch("/api/sampling/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}
