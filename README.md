# Medical Device Statistics

Medical Device Statistics is a local controlled-record web application for medical device quality sampling and R&D statistical analysis.

## Scope

- Attribute sampling plans
- OC curve calculation
- R&D statistics
- Dataset versions
- Analysis records
- Report snapshots
- Audit logs

## Backend

```sh
cd backend
python -m pip install -e ".[test]"
python -m pytest -v
python -m uvicorn app.main:app --reload
```

## Frontend

```sh
cd frontend
npm install
npm test -- --run
npm run dev
```

## Local Deployment

```sh
docker compose up
```

Docker Compose builds local backend and frontend images before starting the services. The backend SQLite database is stored at `/app/backend/data/statistics.db` and persisted in the `app-data` volume.

The backend runs at http://localhost:8000 and the frontend runs at http://localhost:5173.
For local frontend development, Vite proxies `/api` to `http://localhost:8000` by default. Docker Compose overrides that target to `http://backend:8000` so the frontend container can reach the backend service.

Note: the frontend image currently uses `npm install` during Docker build because no package lockfile is present.
