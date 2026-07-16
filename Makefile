.PHONY: install demo test lint typecheck api dashboard docker

install:
	python -m pip install -e ".[dev,api,dashboard]"

demo:
	neurojitsu demo --output outputs/demo

test:
	pytest

lint:
	ruff check src tests

typecheck:
	mypy src/neurojitsu

api:
	uvicorn neurojitsu.api.main:app --reload

dashboard:
	streamlit run src/neurojitsu/dashboard/app.py

docker:
	docker compose up --build
