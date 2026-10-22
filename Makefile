.PHONY: install dev test lint format clean run-all build release-check

PYTHON := .venv/bin/python

## Require the repository-local environment before invoking package tools
.PHONY: check-venv
check-venv:
	@test -x $(PYTHON) || (echo "Create and activate the repository .venv first; see DEVELOPMENT.md"; exit 1)

## Install the package in production mode
install: check-venv
	$(PYTHON) -m pip install .

## Install with development dependencies
dev: check-venv
	$(PYTHON) -m pip install -e ".[dev,plot]"

## Run the full test suite with coverage
test: check-venv
	$(PYTHON) -m pytest tests/ -v --cov=metaheuristics --cov-report=term-missing

## Run ruff lint check
lint: check-venv
	$(PYTHON) -m ruff check metaheuristics/ scripts/ tests/ examples/ tools/

## Auto-format and fix lint issues
format: check-venv
	$(PYTHON) -m ruff check metaheuristics/ scripts/ tests/ examples/ --fix
	$(PYTHON) -m ruff format metaheuristics/ scripts/ tests/ examples/

## Run all four algorithms (quick mode, no plot)
run-all: check-venv
	$(PYTHON) scripts/run.py ga  --seed 42 --runs 3 --no-plot --quick
	$(PYTHON) scripts/run.py pso --seed 42 --runs 3 --no-plot --quick
	$(PYTHON) scripts/run.py sa  --seed 42 --runs 3 --no-plot --quick
	$(PYTHON) scripts/run.py de  --seed 42 --runs 3 --no-plot --quick

## Remove build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage coverage.xml
	find metaheuristics scripts tests examples tools final -type d -name __pycache__ -exec rm -rf {} +

## Validate release metadata and build/check distributions
release-check: check-venv
	$(PYTHON) tools/check_release.py

build: release-check
	$(PYTHON) -m build
	$(PYTHON) -m twine check --strict dist/*
