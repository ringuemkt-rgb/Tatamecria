#!/usr/bin/env bash
set -euo pipefail
ruff check src tests
mypy src/neurojitsu
pytest --cov=neurojitsu --cov-report=term-missing
