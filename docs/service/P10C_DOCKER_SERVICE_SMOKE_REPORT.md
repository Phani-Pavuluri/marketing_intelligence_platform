# P10c Docker Service Smoke Report

## Status

| Field | Value |
|-------|-------|
| **Phase** | P10c — Dockerfile + local container smoke test |
| **Type** | Packaging / local smoke only |
| **Service** | Deterministic FastAPI (`mip.service`) |
| **API phase** | `P10b.1` (unchanged — Docker is packaging only) |
| **Public Streamlit demo** | Unchanged — https://marketingintelligenceplatform.streamlit.app/ |

## Purpose

P10c adds a minimal Docker image to build and run the deterministic FastAPI service locally for smoke testing. This is **not** production deployment, hosted API hardening, or Streamlit containerization.

## Boundaries

Docker in P10c:

- **Does** package `mip.service` with `uvicorn` on port 8000
- **Does** support local `curl` smoke of `/health` and `/version`

Docker in P10c does **not**:

- Enable LLM mode, BYOK, or provider calls
- Run Streamlit or change the public demo deployment
- Add secrets, auth, databases, queues, or external connectors
- Add production data ingestion or raw-row exposure
- Run MMM fitting or GeoX design/inference
- Imply production readiness or causal/ROI/budget claims

MIP remains the **control plane**, not the statistical engine.

## Build and run

```bash
docker build -t mip-service:p10c .
docker run --rm -p 8000:8000 mip-service:p10c
```

If port 8000 is busy:

```bash
docker run --rm -p 8001:8000 mip-service:p10c
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8001/version
```

## Expected smoke results

- `GET /health` → `200`, `status: ok`, deterministic flags (`llm_enabled: false`, etc.)
- `GET /version` → `200`, `api_phase: P10b.1`, `mode: deterministic`

Workflow routes remain available inside the container but P10c validation focuses on health/version smoke.

## Related documents

- [P10 FastAPI/Docker wrapper plan](P10_FASTAPI_DOCKER_WRAPPER_PLAN.md)
- [Deterministic usage modes](DETERMINISTIC_USAGE_MODES.md)
- [Roadmap execution sequence](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md)
