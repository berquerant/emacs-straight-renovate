.PHONY: init
init:
	@uv sync

.PHONY: check
check:
	uv run tox -e black,ruff,mypy -p 3

.PHONY: test
test:
	uv run tox -e py313

.PHONY: ci
ci:
	uv run tox -e black,ruff,mypy,py313 -p 4

.PHONY: dev
dev:
	uv run pip install --editable .

.PHONY: install
install:
	pip install .
