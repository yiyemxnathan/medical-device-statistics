from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.sampling import SamplingPlanRequest
from app.services.controlled_records import create_controlled_analysis_task
from app.services.sampling import SamplingTable, build_sampling_plan, oc_curve

router = APIRouter(prefix="/api/sampling", tags=["sampling"])

SUPPORTED_DEMO_STANDARDS = {
    ("GB/T 2828.1", "2012"): "demo-0.1",
    ("ISO 2859-1", "2026"): "demo-0.1",
}

DEMO_TABLE = SamplingTable(
    sample_size_codes=[
        {"lot_min": 501, "lot_max": 1200, "inspection_level": "II", "code": "J"}
    ],
    plans=[
        {
            "code": "J",
            "aql": "1.0",
            "inspection_state": "normal",
            "sample_size": 80,
            "accept": 2,
            "reject": 3,
        }
    ],
)


@router.post("/plan")
def create_sampling_plan(
    request: SamplingPlanRequest,
    session: Session = Depends(get_session),
) -> dict[str, object]:
    standard_key = (request.standard_name, request.standard_version)
    package_version = SUPPORTED_DEMO_STANDARDS.get(standard_key)
    if package_version is None:
        supported = ", ".join(
            f"{name} {version}" for name, version in SUPPORTED_DEMO_STANDARDS
        )
        raise HTTPException(
            status_code=422,
            detail=(
                "Unsupported demo standard/version. "
                f"Supported combinations: {supported}."
            ),
        )

    try:
        plan = build_sampling_plan(request, DEMO_TABLE)
        curve = oc_curve(
            sample_size=plan.sample_size,
            accept=plan.accept,
            quality_levels=[level / 100 for level in range(11)],
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    result = {
        "plan": plan.model_dump(),
        "oc_curve": [point.model_dump() for point in curve],
        "standard_package": {
            "standard_name": request.standard_name,
            "standard_version": request.standard_version,
            "package_version": package_version,
        },
    }
    task = create_controlled_analysis_task(
        session=session,
        analysis_type="sampling_plan",
        parameters=request.model_dump(),
        result=result,
    )
    return result | {"analysis_task_id": task.id}
