.PHONY: help test test-dev lint check validate harness-score

help:
	@printf '%s\n' \
	  'LAI Harness development commands:' \
	  '  make test          Run the Python test suite' \
	  '  make test-dev      Run tests with pytest' \
	  '  make lint          Run Ruff lint checks' \
	  '  make check         Run fast deterministic static checks' \
	  '  make validate      Run the complete publication gate' \
	  '  make harness-score Measure repository harness maturity'

test:
	python3 -m unittest discover -s tests -v

test-dev:
	.venv/bin/python -m pytest -q

lint:
	.venv/bin/ruff check src tests

check:
	python3 -m compileall -q src tests
	node --check vscode-extension/extension.js
	bash -n scripts/*.sh
	python3 -m json.tool vscode-extension/package.json >/dev/null
	git diff --check

validate:
	./scripts/validate.sh

harness-score:
	npx --yes harness-score@latest .
