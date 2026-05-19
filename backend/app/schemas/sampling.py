from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SamplingPlanRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    standard_name: str = Field(min_length=1)
    standard_version: str = Field(min_length=1)
    lot_size: int = Field(gt=0)
    inspection_level: str = Field(min_length=1)
    aql: str = Field(min_length=1)
    inspection_state: str = Field(min_length=1)

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


class SamplingPlanResult(BaseModel):
    standard_name: str
    standard_version: str
    code: str
    lot_size: int
    inspection_level: str
    aql: str
    inspection_state: str
    sample_size: int
    accept: int
    reject: int


class OCCurvePoint(BaseModel):
    quality_level: float
    acceptance_probability: float
