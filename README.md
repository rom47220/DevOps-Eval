# DevOps Eval

Mini API Flask + Redis, avec Docker, CI/CD GitHub Actions et un peu d'observabilite
(Prometheus / Grafana).

Repo : a remplir apres creation GitHub

## Lancer en local

```bash
cd app
docker compose up -d --build
```

Ensuite :

- App : http://localhost:8080/health
- Status : http://localhost:8080/status
- Metrics : http://localhost:8080/metrics
- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000 (admin / admin)

Stop :

```bash
docker compose down
```

## Tests / lint (sans Docker)

```bash
cd app
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
# Redis doit tourner (compose up redis -d)
flake8 .
pytest -v
```

## CI / CD

- `ci.yml` : lint, tests (matrix Python 3.11/3.12 + Redis), build image, lint YAML, job final `ci-ok`
- `cd.yml` : push image sur GHCR (`latest`, SHA court, `1.0.0`) puis deploy sur le runner self-hosted

Le CD tourne sur un runner self-hosted (ta machine), puis verifie `/health` (3 essais).
Si ca casse, rollback vers l'image precedente.

## Alertes Prometheus

Fichier `app/observability/prometheus/alerts.yml` :

- `HighErrorRate` : plus de 5% d'erreurs 5xx pendant 30s
- `HighLatencyP95` : p95 > 500ms pendant 1 minute

## Image

```bash
docker pull ghcr.io/<ton-user>/devops-eval:1.0.0
```
