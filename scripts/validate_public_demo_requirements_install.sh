#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly PYTHON_IMAGE="python:3.11-slim"

if ! command -v docker >/dev/null 2>&1; then
  echo "error: Docker is required for public deployment validation." >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "error: Docker daemon is unavailable for public deployment validation." >&2
  exit 1
fi

echo "Installing requirements in a clean Python 3.11 container."
docker run --rm \
  --mount "type=bind,src=${REPO_ROOT},dst=/workspace,readonly" \
  --workdir /workspace \
  "${PYTHON_IMAGE}" \
  sh -ceu "
    python -m pip install --no-cache-dir --quiet -r requirements.txt
    python -c 'import app.streamlit_app; from mip.demo.chat_first_demo import load_chat_first_demo_fixture; fixture = load_chat_first_demo_fixture(); assert fixture.fixture_id == \"saas_subscriptions_demo_v1\"; print(f\"validated fixture: {fixture.fixture_id}\")'
  "

echo "Public deployment import and fixture validation passed."
