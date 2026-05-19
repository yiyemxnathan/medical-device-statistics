import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

import app.models.records  # noqa: F401
from app.db.session import get_session
from app.main import create_app
from app.models.records import AnalysisTask, AuditLog


@pytest.fixture
def client_with_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_session():
        with Session(engine) as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_session

    yield TestClient(app), engine


def test_sampling_api_returns_plan_and_curve(client_with_session):
    client, _engine = client_with_session

    response = client.post(
        "/api/sampling/plan",
        json={
            "standard_name": "GB/T 2828.1",
            "standard_version": "2012",
            "lot_size": 800,
            "inspection_level": "II",
            "aql": "1.0",
            "inspection_state": "normal",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["plan"]["sample_size"] == 80
    assert body["plan"]["accept"] == 2
    assert len(body["oc_curve"]) == 11
    assert body["standard_package"] == {
        "standard_name": "GB/T 2828.1",
        "standard_version": "2012",
        "package_version": "demo-0.1",
    }
    assert isinstance(body["analysis_task_id"], int)


def test_sampling_api_persists_analysis_task_and_audit_log(client_with_session):
    client, engine = client_with_session

    response = client.post(
        "/api/sampling/plan",
        json={
            "standard_name": "GB/T 2828.1",
            "standard_version": "2012",
            "lot_size": 800,
            "inspection_level": "II",
            "aql": "1.0",
            "inspection_state": "normal",
        },
    )

    assert response.status_code == 200
    analysis_task_id = response.json()["analysis_task_id"]
    with Session(engine) as session:
        task = session.get(AnalysisTask, analysis_task_id)
        audits = session.exec(select(AuditLog)).all()

    assert task is not None
    assert task.analysis_type == "sampling_plan"
    assert task.created_by == "system"
    assert task.parameters["lot_size"] == 800
    assert task.result["plan"]["sample_size"] == 80
    assert len(audits) == 1
    assert audits[0].actor == "system"
    assert audits[0].action == "create"
    assert audits[0].object_type == "AnalysisTask"
    assert audits[0].object_id == str(analysis_task_id)


def test_sampling_api_rejects_unsupported_standard_version(client_with_session):
    client, engine = client_with_session

    response = client.post(
        "/api/sampling/plan",
        json={
            "standard_name": "ANSI/ASQ Z1.4",
            "standard_version": "2008",
            "lot_size": 800,
            "inspection_level": "II",
            "aql": "1.0",
            "inspection_state": "normal",
        },
    )

    assert response.status_code == 422
    assert "Unsupported demo standard/version" in response.json()["detail"]
    with Session(engine) as session:
        assert session.exec(select(AnalysisTask)).all() == []


def test_statistics_api_returns_description(client_with_session):
    client, _engine = client_with_session

    response = client.post("/api/statistics/describe", json={"values": [1, 2, 3]})

    assert response.status_code == 200
    assert response.json()["mean"] == 2.0


def test_statistics_describe_persists_analysis_task_and_audit_log(client_with_session):
    client, engine = client_with_session

    response = client.post("/api/statistics/describe", json={"values": [1, 2, 3]})

    assert response.status_code == 200
    analysis_task_id = response.json()["analysis_task_id"]
    with Session(engine) as session:
        task = session.get(AnalysisTask, analysis_task_id)
        audit = session.exec(select(AuditLog)).one()

    assert task is not None
    assert task.analysis_type == "statistics_describe"
    assert task.created_by == "system"
    assert task.parameters == {"values": [1.0, 2.0, 3.0]}
    assert task.result["mean"] == 2.0
    assert audit.object_type == "AnalysisTask"
    assert audit.object_id == str(analysis_task_id)


def test_statistics_api_returns_independent_t_test(client_with_session):
    client, _engine = client_with_session

    response = client.post(
        "/api/statistics/independent-t-test",
        json={"group_a": [10, 11, 12, 13], "group_b": [12, 13, 14, 15]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["test"] == "independent_t_test"
    assert body["statistic"] < 0
    assert 0 < body["p_value"] < 1


def test_statistics_api_returns_anova(client_with_session):
    client, _engine = client_with_session

    response = client.post(
        "/api/statistics/anova",
        json={"groups": [[1, 2, 1], [5, 6, 5], [9, 10, 9]]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["test"] == "one_way_anova"
    assert body["statistic"] > 0
    assert body["p_value"] < 0.01


def test_statistics_api_returns_regression(client_with_session):
    client, _engine = client_with_session

    response = client.post(
        "/api/statistics/regression",
        json={"x": [1, 2, 3], "y": [2, 4, 6]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["test"] == "simple_linear_regression"
    assert body["slope"] == 2.0
    assert body["intercept"] == 0.0


def test_statistics_api_returns_422_for_service_value_error(client_with_session):
    client, _engine = client_with_session

    response = client.post(
        "/api/statistics/regression",
        json={"x": [1, 2, 3], "y": [2, 4]},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "x and y must have the same length"
