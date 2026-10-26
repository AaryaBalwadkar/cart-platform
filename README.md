# Cart Platform exam practice

A tiny but working shopping-cart microservice for the provided case study. It has a browser frontend and a JSON backend API, validates the sample inventory in CI, runs in separate frontend/backend containers, deploys a two-replica Nginx frontend and backend service to Docker Desktop Kubernetes, and creates a Terraform-generated endpoint file for Ansible to verify.

The frontend is in `frontend\` and is served by Nginx. The backend is in `backend\` and provides `GET /api/cart`, `POST /api/cart`, and `GET /health`. Cart data is intentionally in memory and resets when the backend restarts; a database is outside the exam scope.

This is a classroom exercise, not a production shopping platform.

See [COMPLETE-GUIDE.md](COMPLETE-GUIDE.md) for the setup and exam runbook.
