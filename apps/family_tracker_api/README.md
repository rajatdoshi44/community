# Family Tracker API

CRUD API for tracker records that associate a family with a member.

Run the service from the repository root:

```sh
uv run uvicorn apps.family_tracker_api.main:app --reload --port 8007
```

Endpoints use the `/family-tracker` prefix:

- `GET /family-tracker/list` — list records
- `POST /family-tracker/create` — create a record with `family_id` and `member_id`
- `POST /family-tracker/update` — update a record, including `family_tracker_id`
- `GET /family-tracker/{id}` — fetch a record
- `DELETE /family-tracker/{id}` — delete a record
- `GET /family-tracker/health` — health check
