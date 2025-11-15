.PHONY: help install install-dev test test-quick lint format type-check clean build docs example-docs build-all-docs serve-docs serve-examples ci-test prepare-release generate-badges

install:
	pip install .

install-dev:
	pip install -e .[dev]

test:
	pytest --cov=pyaterochka_api --cov-report=xml --cov-report=html --cov-report=term-missing

test-quick:
	pytest --tb=short

format:
	black pyaterochka_api/ tests/
	isort pyaterochka_api/ tests/

clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf docs/_build/ examples/docs/_build/
	rm -rf htmlcov/ .coverage coverage.xml coverage.svg
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

build-install:
	$(MAKE) build
	$(MAKE) install

docs:
	cd docs && sphinx-build -b html source _build/html

serve-docs:
	cd docs/_build/html && python -m http.server 8000
