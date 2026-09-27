# Notes oral — Evaluation DevOps

Repo : https://github.com/rom47220/DevOps-Eval

## Pitch global (30 sec)

J'ai une petite API Flask avec Redis. Elle tourne en Docker,
passe dans une CI GitHub Actions, puis un CD qui pousse l'image
sur GHCR et la deploie sur ma machine via un runner self-hosted.
Il y a aussi des metriques Prometheus et deux alertes.

## 1. Application

Endpoints :
- `/health` : verifie Redis (200 si ok, 503 sinon)
- `/status` : version + SHA
- `/metrics` : format Prometheus
- `/simulate-error` : renvoie 500 pour tester les alertes

Tests pytest : health, status, metrics, et un test qui parle vraiment a Redis.

## 2. Docker

Dockerfile multi-stage :
- builder : installe les deps
- runtime : image slim, user non-root, HEALTHCHECK sur /health, gunicorn

`.dockerignore` exclut `.git`, venv, tests, etc.

`docker-compose.yml` : au moins `web` + `redis` (plus prometheus/grafana).
Une commande : `docker compose up -d --build` dans `app/`.

## 3. CI (`ci.yml`)

Declenchee sur push/PR vers main.

Jobs :
1. Lint (flake8)
2. Test (matrix Python 3.11 / 3.12) avec service Redis
3. Build (image Docker, sans push) + download des artefacts de tests
4. YAML lint
5. Ci-ok (job final vert = tout est bon)

On utilise une action locale `setup-python-deps` (setup Python + cache pip + install).
Cache des deps, artefacts coverage/junit, timeout sur chaque job.

## 4. CD (`cd.yml`)

Se declenche apres une CI verte (ou manuellement avec environment=production).

Tags image : `latest`, SHA court, `1.0.0`.
Deploy sur runner self-hosted (Windows) :
- pull image
- `docker compose up`
- healthcheck PowerShell x3
- si ca casse : rollback vers le tag precedent

## 5. Observabilite

`/metrics` expose :
- counter `http_requests_total` (labels endpoint + code)
- histogramme de latence
- gauge `app_info` (version + git_sha)

Alertes :
- HighErrorRate : > 5% d'erreurs 5xx pendant 30s
- HighLatencyP95 : p95 > 500ms pendant 1 min

Grafana provisionne (datasource + dashboard).

## Commandes a montrer

```bash
cd app
docker compose up -d --build
curl http://localhost:8080/health
curl http://localhost:8080/status
curl -s http://localhost:8080/metrics | grep http_requests_total
```

Interfaces :
- App : http://localhost:8080
- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000 (admin/admin)

## Ce qui reste avant le rendu

- [ ] Installer le runner self-hosted (pour que le CD tourne)
- [ ] Creer l'environment GitHub `production`
- [ ] Donner acces write au package GHCR si besoin
- [ ] Ajouter bastien.awadesamtou@ext.esiea.fr en collaborateur
- [ ] Faire le zip `dumoulin_romain_livrable.zip`
