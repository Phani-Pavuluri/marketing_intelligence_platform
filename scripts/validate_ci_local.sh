#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly DEVCONTAINER_IMAGE="mcr.microsoft.com/devcontainers/python:1-3.11-bookworm"
readonly POETRY_VERSION="2.4.1"

usage() {
  cat <<'EOF'
Usage: scripts/validate_ci_local.sh [--docker|--host|--inside-container]

Without an option, validation requires Docker and uses the repository's
devcontainer image. Use --docker for the same explicit containerized path or
--host to explicitly opt into the local Poetry installation.
EOF
}

run_checks() {
  poetry install --no-interaction --no-ansi
  poetry run pytest
  poetry run ruff check .
  poetry run mypy src tests app
}

run_in_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "error: Docker is required for repository-standard validation, but the Docker CLI was not found." >&2
    echo "Install/start Docker and run 'make validate' again. Use 'make validate-host' only for explicit host validation." >&2
    return 1
  fi
  if ! docker info >/dev/null 2>&1; then
    echo "error: Docker is required for repository-standard validation, but the Docker daemon is unavailable." >&2
    echo "Start Docker and run 'make validate' again. Host Poetry fallback is disabled." >&2
    return 1
  fi

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
    echo "error: explicit host validation requires Poetry, but Poetry was not found." >&2
    echo "Install Poetry and run 'make validate-host' again, or use Docker with 'make validate'." >&2
    return 1
  fi

  echo "Running explicitly requested host validation with Poetry."
  run_checks
}

case "${1:-}" in
  ""|--docker)
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
