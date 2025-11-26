# Makefile for XENO AI Assistant
# Quick commands for development workflow

.PHONY: help install test lint format clean build docs run

# Default target
help:
	@echo "XENO AI Assistant - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install dependencies"
	@echo "  make install-dev   - Install with dev dependencies"
	@echo "  make setup         - Complete development setup"
	@echo ""
	@echo "Development:"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-e2e      - Run E2E tests only"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code with black/isort"
	@echo "  make security      - Run security checks"
	@echo ""
	@echo "Quality:"
	@echo "  make pre-commit    - Run pre-commit hooks"
	@echo "  make benchmark     - Run performance benchmarks"
	@echo "  make quality       - Run all quality checks"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  make build         - Build distribution package"
	@echo "  make docs          - Build documentation"
	@echo "  make clean         - Clean build artifacts"
	@echo ""
	@echo "Run:"
	@echo "  make run           - Run XENO assistant"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

setup: install-dev
	pre-commit install
	@echo "Development environment ready!"

# Testing
test:
	pytest tests/ -v

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

test-e2e:
	pytest tests/e2e -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-benchmark:
	pytest tests/benchmarks --benchmark-only

# Code Quality
lint:
	flake8 src --count --max-line-length=100 --statistics
	pylint src --max-line-length=100 --disable=C0114,C0115,C0116,R0913,R0914

format:
	black src tests --line-length 100
	isort src tests

security:
	bandit -r src -f screen
	safety check

type-check:
	mypy src --ignore-missing-imports

# Pre-commit
pre-commit:
	pre-commit run --all-files

# Quality gate (all checks)
quality: format lint type-check security test
	@echo "All quality checks passed!"

# Build
build: clean
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Documentation
docs:
	mkdocs build

docs-serve:
	mkdocs serve

# Run application
run:
	python -m src.jarvis

# Development workflow
dev: format lint test
	@echo "Development cycle complete!"

# CI simulation
ci: quality test-cov benchmark
	@echo "CI checks complete!"
