import pytest

from app.schemas.sampling import SamplingPlanRequest
from app.services.sampling import (
    SamplingTable,
    binomial_acceptance_probability,
    build_sampling_plan,
    oc_curve,
)


def test_build_sampling_plan_from_standard_payload():
    table = SamplingTable(
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
    request = SamplingPlanRequest(
        standard_name="GB/T 2828.1",
        standard_version="2012",
        lot_size=800,
        inspection_level="II",
        aql="1.0",
        inspection_state="normal",
    )

    plan = build_sampling_plan(request, table)

    assert plan.code == "J"
    assert plan.sample_size == 80
    assert plan.accept == 2
    assert plan.reject == 3


def test_oc_curve_uses_binomial_acceptance_probability():
    points = oc_curve(sample_size=10, accept=0, quality_levels=[0.0, 0.1])

    assert points[0].quality_level == 0.0
    assert points[0].acceptance_probability == 1.0
    assert points[1].acceptance_probability == pytest.approx(0.3486784401)


def test_missing_sampling_combination_raises_clear_error():
    table = SamplingTable(sample_size_codes=[], plans=[])
    request = SamplingPlanRequest(
        standard_name="ISO 2859-1",
        standard_version="2026",
        lot_size=20,
        inspection_level="II",
        aql="1.0",
        inspection_state="normal",
    )

    with pytest.raises(ValueError, match="No sample size code"):
        build_sampling_plan(request, table)


def test_inverted_lot_range_rejected_by_sampling_table_construction():
    with pytest.raises(ValueError, match="lot_max"):
        SamplingTable(
            sample_size_codes=[
                {"lot_min": 1200, "lot_max": 501, "inspection_level": "II", "code": "J"}
            ],
            plans=[],
        )


def test_numeric_aql_in_plan_payload_matches_string_request():
    table = SamplingTable(
        sample_size_codes=[
            {"lot_min": 501, "lot_max": 1200, "inspection_level": "II", "code": "J"}
        ],
        plans=[
            {
                "code": "J",
                "aql": 1.0,
                "inspection_state": "normal",
                "sample_size": 80,
                "accept": 2,
                "reject": 3,
            }
        ],
    )
    request = SamplingPlanRequest(
        standard_name="GB/T 2828.1",
        standard_version="2012",
        lot_size=800,
        inspection_level="II",
        aql="1.0",
        inspection_state="normal",
    )

    plan = build_sampling_plan(request, table)

    assert plan.aql == "1.0"
    assert plan.sample_size == 80


@pytest.mark.parametrize(
    ("sample_size", "accept", "match"),
    [
        (0, 0, "sample_size"),
        (10, -1, "accept"),
        (10, 11, "accept"),
    ],
)
def test_invalid_binomial_sample_size_and_accept_raise_clear_value_error(
    sample_size, accept, match
):
    with pytest.raises(ValueError, match=match):
        binomial_acceptance_probability(
            sample_size=sample_size,
            accept=accept,
            defect_rate=0.1,
        )


def test_whitespace_and_case_normalization_for_inspection_state_matching():
    table = SamplingTable(
        sample_size_codes=[
            {"lot_min": 501, "lot_max": 1200, "inspection_level": " II ", "code": " J "}
        ],
        plans=[
            {
                "code": "J",
                "aql": "1.0",
                "inspection_state": " Normal ",
                "sample_size": 80,
                "accept": 2,
                "reject": 3,
            }
        ],
    )
    request = SamplingPlanRequest(
        standard_name="GB/T 2828.1",
        standard_version="2012",
        lot_size=800,
        inspection_level="II",
        aql="1.0",
        inspection_state="normal",
    )

    plan = build_sampling_plan(request, table)

    assert plan.code == "J"
    assert plan.inspection_state == "normal"


def test_sampling_plan_request_rejects_none_aql():
    with pytest.raises(ValueError, match="aql"):
        SamplingPlanRequest(
            standard_name="GB/T 2828.1",
            standard_version="2012",
            lot_size=800,
            inspection_level="II",
            aql=None,
            inspection_state="normal",
        )


def test_sampling_table_rejects_plan_row_with_none_aql():
    with pytest.raises(ValueError, match="aql"):
        SamplingTable(
            sample_size_codes=[
                {"lot_min": 501, "lot_max": 1200, "inspection_level": "II", "code": "J"}
            ],
            plans=[
                {
                    "code": "J",
                    "aql": None,
                    "inspection_state": "normal",
                    "sample_size": 80,
                    "accept": 2,
                    "reject": 3,
                }
            ],
        )
