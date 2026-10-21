start-members-api:
	uv run uvicorn apps.members_api.main:app --reload --port 8005

start-family-unit-api:
	uv run uvicorn apps.family_unit_api.main:app --reload --port 8002

start-parent_child-api:
	uv run uvicorn apps.parent_child_api.main:app --reload --port 8003

start-split-family-api:
	uv run uvicorn apps.split_family_api.main:app --reload --port 8004

gateway:
	uv run uvicorn apps.gateway.main:app --port 8000 --reload

stop-all:
	lsof -ti :8000,8001,8002,8003,8004 | xargs -r kill -9

db-setup:
	uv run python packages/database/src/my_database/main.py

run-all: stop-all
	make -j4 gateway start-members-api start-family-unit-api start-parent_child-api start-split-family-api

new-app/%:
	uv init --app apps/$*

