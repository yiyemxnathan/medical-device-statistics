# Medical Device Statistics Implementation Plan

**Goal:** Build a locally deployable controlled-record web application for medical device quality sampling and R&D statistical analysis.

**Architecture:** React renders the workbench, FastAPI owns validation and calculations, and SQLite stores controlled records for the first release. Core calculations live in backend service modules with deterministic tests before UI work begins.

**Tech Stack:** Python 3.12, FastAPI, SQLModel, SQLite, pandas, numpy, scipy, statsmodels, pytest, React, TypeScript, Vite, Vitest, Playwright.

## Implemented Scope

- Backend scaffold with FastAPI health endpoint.
- Controlled-record SQLModel entities for projects, dataset versions, analysis tasks, report snapshots, audit logs, and standard packages.
- Attribute sampling service for ISO 2859 / GB/T 2828 style sample-size code lookup, Ac/Re acceptance criteria, and binomial OC curve calculation.
- Statistics service covering descriptive statistics, independent t test, one-way ANOVA, and simple linear regression.
- API routers for sampling and descriptive statistics.
- Reporting helper for frozen HTML report snapshots.
- React/Vite frontend shell with a sampling-plan screen and API client.
- Docker Compose and README instructions for local deployment.

## Verification Targets

Backend:

```powershell
cd backend
python -m pip install -e ".[test]"
python -m pytest -v
python -m uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
npm test -- --run
npm run dev
```

Deployment:

```powershell
docker compose up
```

## Follow-up Work

- Full standard data package import and version-locking UI.
- Project and dataset import workflow.
- Report list, report voiding, and PDF export flow.
- Additional statistics: normality tests, variance tests, paired and one-sample t tests, non-parametric tests, confidence intervals, and method recommendation logic.
- Enterprise validation artifacts, permission model, and electronic-signature extensions.
