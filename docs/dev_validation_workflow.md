# Local validation workflow

## Standard command

Run the repository validation suite from the repository root:

```bash
make validate
```

This is the standard local validation entrypoint. It requires Docker and runs
the checks in the repository's configured Python 3.11 devcontainer image. If
the Docker CLI or daemon is unavailable, validation fails clearly; it never
falls back to host Poetry.

The explicit Docker alias runs the same path:

```bash
make validate-docker
```

## Checks performed

The Docker path installs the locked project dependencies and runs the repository-wide
release checklist in this order:

```bash
poetry install --no-interaction --no-ansi
poetry run pytest
poetry run ruff check .
poetry run mypy src tests app
```

The production `Dockerfile` is not used for validation because it packages the
FastAPI smoke-test service with main dependencies only. The validation path
uses `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm`, matching
`.devcontainer/devcontainer.json`, and installs Poetry 2.4.1 inside the
temporary container. The repository is mounted read-write so tests and tools
inspect the working tree; ignored tool caches may be created locally.

## Relationship to CI

This repository currently has no GitHub Actions workflow, so there are no CI
commands or Python matrix to reproduce exactly. The validation entrypoint uses
the full test, Ruff, and mypy commands documented in the README deployment
checklist. It therefore matches the repository's documented release checks,
but is only a partial CI equivalent.

The container covers Python 3.11 only. If GitHub Actions is added later with
additional Python versions or checks, Actions remains the final authority and
this script should be updated to track its commands.

## Explicit host validation and cleanup

Host validation is available only as an explicit troubleshooting choice:

```bash
make validate-host
```

This target delegates to `./scripts/validate_ci_local.sh --host`. Neither
`make validate` nor `make validate-docker` will select host Poetry.

Remove common ignored OS and Python tooling junk with:

```bash
make clean-junk
```

The cleanup target removes `.DS_Store`, `Thumbs.db`, Python bytecode,
`__pycache__`, and pytest, mypy, and Ruff cache directories. It does not remove
virtual environments, source data, runtime artifacts, or validation archives.
