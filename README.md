# DevOps Eval

Romain Dumoulin — https://github.com/rom47220/DevOps-Eval

Petite API Flask + Redis pour l'eval. Docker, CI/CD GitHub Actions,
runner self-hosted sur ma machine, et un peu de Prometheus / Grafana
(comme sur les ateliers).

## Lancer

```bash
cd app
docker compose up -d --build
```

- App : http://localhost:8080/health
- Status : http://localhost:8080/status
- Metrics : http://localhost:8080/metrics
- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000 (admin / admin)

```bash
docker compose down
```

## Tests / lint en local

```bash
cd app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# faut que Redis tourne (docker compose up redis -d)
flake8 .
pytest -v
```

## CI / CD

- `ci.yml` : flake8, pytest (3.11 + 3.12 avec Redis), build image, yamllint, job `ci-ok`
- `cd.yml` : apres une CI verte, build/push sur GHCR puis deploy sur le runner

Tags image : `latest`, SHA court, `1.0.0`.
Le deploy fait un healthcheck (3 essais). Si ca casse, rollback sur le tag d'avant.

Image : `ghcr.io/rom47220/devops-eval:1.0.0`

## Alertes

Dans `app/observability/prometheus/alerts.yml` :
- HighErrorRate (> 5% de 5xx pendant 30s)
- HighLatencyP95 (p95 > 500ms pendant 1 min)
