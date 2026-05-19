from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.statistics import (
    GroupedSamplesRequest,
    NumericSeriesRequest,
    RegressionRequest,
    TwoSampleRequest,
)
from app.services.controlled_records import create_controlled_analysis_task
from app.services.statistics import (
    describe_values,
    independent_t_test,
    one_way_anova,
    simple_linear_regression,
)

router = APIRouter(prefix="/api/statistics", tags=["statistics"])


def _controlled_statistics_response(
    session: Session,
    analysis_type: str,
    parameters: dict[str, Any],
    operation: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    try:
        result = operation()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    task = create_controlled_analysis_task(
        session=session,
        analysis_type=analysis_type,
        parameters=parameters,
        result=result,
    )
    return result | {"analysis_task_id": task.id}


@router.post("/describe")
def describe_series(
    request: NumericSeriesRequest,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    return _controlled_statistics_response(
        session=session,
        analysis_type="statistics_describe",
        parameters=request.model_dump(),
        operation=lambda: describe_values(request.values),
    )


@router.post("/independent-t-test")
def run_independent_t_test(
    request: TwoSampleRequest,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    return _controlled_statistics_response(
        session=session,
        analysis_type="statistics_independent_t_test",
        parameters=request.model_dump(),
        operation=lambda: independent_t_test(
            request.group_a,
            request.group_b,
            request.equal_var,
        ),
    )


@router.post("/anova")
def run_anova(
    request: GroupedSamplesRequest,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    return _controlled_statistics_response(
        session=session,
        analysis_type="statistics_anova",
        parameters=request.model_dump(),
        operation=lambda: one_way_anova(request.groups),
    )


@router.post("/regression")
def run_regression(
    request: RegressionRequest,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    return _controlled_statistics_response(
        session=session,
        analysis_type="statistics_regression",
        parameters=request.model_dump(),
        operation=lambda: simple_linear_regression(request.x, request.y),
    )
