# Todo List REST API

Simple todo list REST API built with Django + Django REST Framework.

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

API base: `http://127.0.0.1:8000/api/`
Browsable API & admin: `http://127.0.0.1:8000/api/todos/`, `http://127.0.0.1:8000/admin/`

## Endpoints

| Method | URL                | Action              |
|--------|--------------------|---------------------|
| GET    | `/api/todos/`      | List todos          |
| POST   | `/api/todos/`      | Create todo         |
| GET    | `/api/todos/{id}/` | Retrieve todo       |
| PUT    | `/api/todos/{id}/` | Replace todo        |
| PATCH  | `/api/todos/{id}/` | Partial update      |
| DELETE | `/api/todos/{id}/` | Delete todo         |

## Todo fields

- `id` (read-only)
- `title` (string, required)
- `description` (string, optional)
- `completed` (bool, default `false`)
- `created_at`, `updated_at` (read-only)

## Example

```bash
curl -X POST http://127.0.0.1:8000/api/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk", "description": "2 liters"}'
```

## Database

Configured via a single `DATABASE_URL` env var (parsed by `dj-database-url`).

```bash
export DATABASE_URL="postgres://user:pass@host:5432/dbname"
```

No `DATABASE_URL` set → falls back to local SQLite (dev convenience).
Pooling: `conn_max_age=600` + health checks.

Local Postgres quick option:

```bash
docker run -d --name todopg -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=todos \
  -p 5432:5432 postgres:16-alpine
export DATABASE_URL="postgres://postgres:pass@localhost:5432/todos"
python manage.py migrate
```

## Async tasks (Celery + Redis)

Background processing via Celery, broker/result backend = Redis.

Broker URL from env `REDIS_URL` (default `redis://localhost:6379/0`).

### Run locally

Need a running Redis. Quick option:

```bash
docker run -d --name tododis -p 6379:6379 redis:7-alpine
```

Then, in separate terminals (venv activated):

```bash
# worker — processes async tasks
celery -A config worker -l info

# beat — kicks off scheduled tasks
celery -A config beat -l info
```

Creating a todo (`POST /api/todos/`) fires `send_todo_notification.delay(id)` —
returns immediately, worker handles it.

To run tasks inline without a worker/broker (tests/dev):

```bash
export CELERY_TASK_ALWAYS_EAGER=true
```

### Tasks (`todos/tasks.py`)

| Task | Type | What |
|------|------|------|
| `send_todo_notification` | async | Triggered on todo create |
| `count_todos` | scheduled | Hourly, logs counts |
| `delete_old_completed_todos` | scheduled | Daily 03:00, purges completed > 30d |

### Scheduled tasks (Celery Beat)

Uses `django_celery_beat` DatabaseScheduler — schedules live in the DB,
editable in Django admin (`/admin/django_celery_beat/`). Defaults defined in
`CELERY_BEAT_SCHEDULE` (`config/settings.py`) and synced into the DB on beat start.

## Deploy (Railway)

Run 3 separate services off the same repo/image, all sharing `REDIS_URL`
(add a Redis plugin):

| Service | Start command |
|---------|---------------|
| web | `gunicorn config.wsgi --bind 0.0.0.0:$PORT` |
| worker | `celery -A config worker -l info` |
| beat | `celery -A config beat -l info` |

Run `migrate` once (web service already does it via `railway.json`).
