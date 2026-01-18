# Distributed Rate Limiter 🛡️

A high-performance, distributed rate limiting service built with **FastAPI**, **Redis (Lua Scripts)**, and **Kubernetes**. Designed to handle high concurrency with atomic token bucket logic.

## 🚀 Features
* **Distributed Architecture:** Stateless Python containers coordinated via Redis.
* **Atomic Operations:** Uses custom **Redis Lua scripts** to prevent race conditions during token refills.
* **Token Bucket Algorithm:** Allows burst traffic while maintaining a steady refill rate.
* **Kubernetes Ready:** Deployable with full HPA and Load Balancing configurations.
* **Performance:** <10ms p99 latency under load (Benchmarked).

## 🛠️ Tech Stack
* **Language:** Python 3.9 (FastAPI)
* **Database:** Redis (Alpine)
* **Orchestration:** Kubernetes (Docker Desktop)
* **Tooling:** Docker, uvicorn, pytest

## ⚡ How to Run
### 1. Prerequisites
* Docker Desktop (with Kubernetes enabled)
* Python 3.9+

### 2. Deploy to Kubernetes
```bash
# Build the image
docker build -t rate-limiter:v1 .

# Deploy Redis and App
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/app.yaml