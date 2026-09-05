DEV_PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: help test test-dev lint typecheck check validate harness-score harness-score-gate

help:
	@printf '%s\n' \
	  'lai harness development commands:' \
	  '  make test          Run the dependency-free Python test suite' \
	  '  make test-dev      Run tests with pytest' \
	  '  make lint          Run Ruff lint checks' \
	  '  make typecheck     Run the strict mypy ratchet' \
	  '  make check         Run fast deterministic static checks' \
	  '  make validate      Run the complete publication gate' \
	  '  make harness-score Measure repository harness maturity' \
	  '  make harness-score-gate Require L4 repository harness maturity'


test:
	python3 -m unittest discover -s tests -v

test-dev:
	$(DEV_PYTHON) -m pytest -q

lint:
	$(DEV_PYTHON) -m ruff check src tests .cursor/hooks

typecheck:
	$(DEV_PYTHON) -m mypy --config-file mypy.ini

check:
	python3 -m compileall -q src tests .cursor/hooks
	python3 -m py_compile src/local-agent .cursor/hooks/*.py
	node --check vscode-extension/extension.js
	bash -n scripts/*.sh
	python3 -m json.tool vscode-extension/package.json >/dev/null
	git diff --check

validate:
	./scripts/validate.sh

harness-score:
	npx --yes harness-score@1.6.3 .

harness-score-gate:
	npx --yes harness-score@1.6.3 . --min-level 4
