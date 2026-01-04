#!/bin/bash
set -e

echo "🔍 Running formatting check..."
uv run ruff format

echo "🧹 Running linting check..."
uv run ruff check --fix

echo "🧪 Running tests..."
uv run pytest --cov=src/qr_network --cov-report=term-missing

echo "✅ All checks passed!"
