#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly DEVCONTAINER_IMAGE="mcr.microsoft.com/devcontainers/python:1-3.11-bookworm"
readonly POETRY_VERSION="2.4.1"

usage() {
  cat <<'EOF'
Usage: scripts/validate_ci_local.sh [--docker|--host|--inside-container]

Without an option, Docker is preferred and host Poetry is used only when the
Docker CLI or daemon is unavailable. Use --docker to require containerized
validation or --host to explicitly use the local Poetry installation.
EOF
}

run_checks() {
  poetry install --no-interaction --no-ansi
  poetry run pytest
  poetry run ruff check .
  poetry run mypy src tests app
}

docker_is_available() {
  command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1
}

run_in_docker() {
  echo "Running validation in the Python 3.11 devcontainer image: ${DEVCONTAINER_IMAGE}"
  docker run --rm \
    --volume "${REPO_ROOT}:/workspace" \
    --workdir /workspace \
    --env POETRY_VIRTUALENVS_IN_PROJECT=false \
    --env POETRY_NO_INTERACTION=1 \
    "${DEVCONTAINER_IMAGE}" \
    bash -lc "python -m pip install --disable-pip-version-check --quiet 'poetry==${POETRY_VERSION}' && ./scripts/validate_ci_local.sh --inside-container"
}

run_on_host() {
  if ! command -v poetry >/dev/null 2>&1; then
    echo "error: Docker is unavailable and Poetry is not installed on the host." >&2
    echo "Start Docker and run 'make validate', or install Poetry and retry." >&2
    return 1
  fi

  echo "Docker is unavailable; running the same validation sequence with host Poetry."
  run_checks
}

case "${1:-}" in
  "")
    if docker_is_available; then
      run_in_docker
    else
      run_on_host
    fi
    ;;
  --docker)
    if ! docker_is_available; then
      echo "error: --docker requires a running Docker daemon." >&2
      exit 1
    fi
    run_in_docker
    ;;
  --host)
    run_on_host
    ;;
  --inside-container)
    run_checks
    ;;
  -h|--help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
