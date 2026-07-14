.PHONY: validate validate-docker clean-junk

validate:
	./scripts/validate_ci_local.sh

validate-docker:
	./scripts/validate_ci_local.sh --docker

clean-junk:
	find . -type f \( -name '.DS_Store' -o -name 'Thumbs.db' -o -name '*.py[co]' \) -delete
	find . -type d \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.mypy_cache' -o -name '.ruff_cache' \) -prune -exec rm -rf {} +
