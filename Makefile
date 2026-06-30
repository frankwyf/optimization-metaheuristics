.PHONY: install dev test lint format clean run-all

## Install the package in production mode
install:
	pip install .

## Install with development dependencies
dev:
	pip install -e ".[dev]"

## Run the full test suite with coverage
test:
	python -m pytest tests/ -v --cov=metaheuristics --cov-report=term-missing

## Run ruff lint check
lint:
	ruff check metaheuristics/ scripts/ tests/

## Auto-format and fix lint issues
format:
	ruff check metaheuristics/ scripts/ tests/ --fix
	ruff format metaheuristics/ scripts/ tests/

## Run all four algorithms (quick mode, no plot)
run-all:
	python scripts/run.py ga  --seed 42 --runs 3 --no-plot --quick
	python scripts/run.py pso --seed 42 --runs 3 --no-plot --quick
	python scripts/run.py sa  --seed 42 --runs 3 --no-plot --quick
	python scripts/run.py de  --seed 42 --runs 3 --no-plot --quick

## Remove build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
