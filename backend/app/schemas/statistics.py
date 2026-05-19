from pydantic import BaseModel, Field, FiniteFloat


class NumericSeriesRequest(BaseModel):
    values: list[FiniteFloat] = Field(min_length=1)


class TwoSampleRequest(BaseModel):
    group_a: list[FiniteFloat] = Field(min_length=2)
    group_b: list[FiniteFloat] = Field(min_length=2)
    equal_var: bool = False
    alpha: float = Field(default=0.05, gt=0, lt=1)


class GroupedSamplesRequest(BaseModel):
    groups: list[list[FiniteFloat]] = Field(min_length=2)
    alpha: float = Field(default=0.05, gt=0, lt=1)


class RegressionRequest(BaseModel):
    x: list[FiniteFloat] = Field(min_length=2)
    y: list[FiniteFloat] = Field(min_length=2)
