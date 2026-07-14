.PHONY: validate validate-docker validate-host validate-public-deployment clean-junk

validate:
	./scripts/validate_ci_local.sh --docker

validate-docker:
	./scripts/validate_ci_local.sh --docker

validate-host:
	./scripts/validate_ci_local.sh --host

validate-public-deployment:
	./scripts/validate_public_demo_requirements_install.sh

clean-junk:
	find . -type f \( -name '.DS_Store' -o -name 'Thumbs.db' -o -name '*.py[co]' \) -delete
	find . -type d \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.mypy_cache' -o -name '.ruff_cache' \) -prune -exec rm -rf {} +
