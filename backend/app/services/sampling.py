from math import comb
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.sampling import OCCurvePoint, SamplingPlanRequest, SamplingPlanResult


class SampleSizeCodeRow(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    lot_min: int = Field(gt=0)
    lot_max: int = Field(gt=0)
    inspection_level: str = Field(min_length=1)
    code: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_lot_range(self) -> "SampleSizeCodeRow":
        if self.lot_max < self.lot_min:
            raise ValueError("lot_max must be greater than or equal to lot_min")
        return self


class SamplingPlanRow(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    code: str = Field(min_length=1)
    aql: str = Field(min_length=1)
    inspection_state: str = Field(min_length=1)
    sample_size: int = Field(gt=0)
    accept: int = Field(ge=0)
    reject: int = Field(ge=0)

    @field_validator("aql", mode="before")
    @classmethod
    def normalize_aql(cls, value: Any) -> Any:
        if value is None:
            return value
        return str(value).strip()

    @field_validator("inspection_state")
    @classmethod
    def normalize_inspection_state(cls, value: str) -> str:
        return value.lower()


class SamplingTable(BaseModel):
    sample_size_codes: list[SampleSizeCodeRow]
    plans: list[SamplingPlanRow]


def build_sampling_plan(
    request: SamplingPlanRequest,
    table: SamplingTable,
) -> SamplingPlanResult:
    code_row = next(
        (
            row
            for row in table.sample_size_codes
            if row.lot_min <= request.lot_size <= row.lot_max
            and row.inspection_level == request.inspection_level
        ),
        None,
    )
    if code_row is None:
        raise ValueError("No sample size code matches lot size and inspection level")

    code = code_row.code
    plan_row = next(
        (
            row
            for row in table.plans
            if row.code == code
            and row.aql == request.aql
            and row.inspection_state == request.inspection_state
        ),
        None,
    )
    if plan_row is None:
        raise ValueError("No sampling plan matches code, AQL, and inspection state")

    return SamplingPlanResult(
        standard_name=request.standard_name,
        standard_version=request.standard_version,
        code=code,
        lot_size=request.lot_size,
        inspection_level=request.inspection_level,
        aql=request.aql,
        inspection_state=request.inspection_state,
        sample_size=plan_row.sample_size,
        accept=plan_row.accept,
        reject=plan_row.reject,
    )


def binomial_acceptance_probability(
    sample_size: int, accept: int, defect_rate: float
) -> float:
    if sample_size <= 0:
        raise ValueError("sample_size must be greater than 0")
    if accept < 0 or accept > sample_size:
        raise ValueError("accept must be between 0 and sample_size")
    if defect_rate < 0 or defect_rate > 1:
        raise ValueError("defect_rate must be between 0 and 1")
    return sum(
        comb(sample_size, defects)
        * defect_rate**defects
        * (1 - defect_rate) ** (sample_size - defects)
        for defects in range(accept + 1)
    )


def oc_curve(
    sample_size: int,
    accept: int,
    quality_levels: list[float],
) -> list[OCCurvePoint]:
    return [
        OCCurvePoint(
            quality_level=level,
            acceptance_probability=binomial_acceptance_probability(
                sample_size, accept, level
            ),
        )
        for level in quality_levels
    ]
