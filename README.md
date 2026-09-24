# Incident Copilot

A REST service for logging and searching ops incidents, with AI summarization and ML severity prediction. It's the capstone for my **100 Days of DevOps**: a small app wrapped in a real delivery pipeline (Docker, Kubernetes, Terraform, CI/CD, monitoring, GenAI, MLOps).

> **Status:** early development (Phase 1, Foundations). See the [project brief](docs/PROJECT_BRIEF.md) for architecture and stack.

## Planned features
- Create, list and fetch incidents via REST API
- AI-generated incident summaries and "seen this before?" search (RAG)
- ML-suggested severity and category
- Deployed to AKS via Terraform, shipped by GitHub Actions, observed with Prometheus/Grafana

## Quick start
> Coming with app v0. This section will cover running locally, running tests, and running via Docker Compose.

## Roadmap
- [x] **P1** Repo, README, licence, project brief
- [ ] **P1** App v0 with persistence and tests
- [ ] **P2** Dockerize (multi-stage), Compose with Postgres, push to GHCR
- [ ] **P3** Kubernetes: ConfigMap/Secret, probes, HPA, NetworkPolicy, Ingress
- [ ] **P4** Terraform + AKS with remote state
- [ ] **P5** CI/CD with GitHub Actions
- [ ] **P6** Monitoring and logging
- [ ] **P7** AI feature (summaries + RAG)
- [ ] **P8** MLOps: model tracked in MLflow, deployed on Azure ML
- [ ] **P9** Final architecture diagram and polish

## Repo layout (planned)
```
app/         FastAPI service
tests/       pytest suite
docker/      Dockerfile, compose files
k8s/         Kubernetes manifests
terraform/   Azure infrastructure
.github/     CI/CD workflows
docs/        Project brief, diagrams, incident write-ups
```

## License
[MIT](LICENSE)
