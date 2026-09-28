# Incident Copilot

A REST service for logging and searching ops incidents, with AI summarization and ML severity prediction. It's the capstone for my **100 Days of DevOps**: a small app wrapped in a real delivery pipeline (Docker, Kubernetes, Terraform, CI/CD, monitoring, GenAI, MLOps).

> **Status:** early development (Phase 1, Foundations). See the [project brief](docs/PROJECT_BRIEF.md) for architecture and stack, and the [learning guide](docs/LEARNING_GUIDE.md) for a beginner walkthrough of the code.

## Planned features
- Create, list and fetch incidents via REST API
- AI-generated incident summaries and "seen this before?" search (RAG)
- ML-suggested severity and category
- Deployed to AKS via Terraform, shipped by GitHub Actions, observed with Prometheus/Grafana

## Quick start
Requires Python 3.12+.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Data is persisted to `data/incidents.db` (SQLite), so it survives a restart. To run the tests, install the dev requirements too:
```bash
pip install -r requirements-dev.txt
pytest -v
```

### Run with Docker
```bash
docker build -t incident-copilot:0.1 .
docker run -d --name incident-copilot -p 8000:8000 -v incident-data:/app/data incident-copilot:0.1
curl http://localhost:8000/health
```
The `-v incident-data:/app/data` volume keeps the SQLite file when the container is removed. The image is a multi-stage build: dependencies are installed in a builder stage, and only the finished virtual environment and `app/` are copied into the final image.

Interactive API docs: http://127.0.0.1:8000/docs

```bash
curl -X POST http://127.0.0.1:8000/incidents \
  -H 'Content-Type: application/json' \
  -d '{"title":"AKS node NotReady","severity":"high","symptoms":"Pods Pending after drain"}'

curl http://127.0.0.1:8000/incidents
curl "http://127.0.0.1:8000/incidents?severity=high"
curl http://127.0.0.1:8000/incidents/1
```

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/incidents` | Create an incident (201) |
| GET | `/incidents` | List incidents, optional `?severity=` filter |
| GET | `/incidents/{id}` | Fetch one incident (404 if missing) |

## Roadmap
- [x] **P1** Repo, README, licence, project brief
- [x] **P1** App v0 (in-memory REST API)
- [x] **P1** Persistence (SQLite) and one automated test
- [ ] **P2** Multi-stage Dockerfile (written; build + run verification pending)
- [ ] **P2** Compose with Postgres, push to GHCR, harden image
- [ ] **P3** Kubernetes: ConfigMap/Secret, probes, HPA, NetworkPolicy, Ingress
- [ ] **P4** Terraform + AKS with remote state
- [ ] **P5** CI/CD with GitHub Actions
- [ ] **P6** Monitoring and logging
- [ ] **P7** AI feature (summaries + RAG)
- [ ] **P8** MLOps: model tracked in MLflow, deployed on Azure ML
- [ ] **P9** Final architecture diagram and polish

## Repo layout (planned)
```
app/         FastAPI service (main, models, store)
Dockerfile   Multi-stage image build
tests/       pytest suite
k8s/         Kubernetes manifests
terraform/   Azure infrastructure
.github/     CI/CD workflows
docs/        Project brief, learning guide, diagrams, incident write-ups
```

## License
[MIT](LICENSE)
