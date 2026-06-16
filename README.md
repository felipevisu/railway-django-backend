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
