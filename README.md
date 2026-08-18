# Education System

A Django-based e-learning platform for creating courses, managing structured
content, enrolling students, and communicating in real time.

## Features

- **Course management** — instructors create courses grouped by subject,
  organized into ordered modules with drag-and-drop reordering.
- **Polymorphic content** — each module can contain text, video, image, or
  file content via a generic relation, so new content types can be added
  without touching the module model.
- **Student enrollment** — self-registration, course enrollment, and a
  student dashboard for viewing joined courses.
- **REST API** — course and subject endpoints built with Django REST
  Framework, using viewsets and a router.
- **Real-time chat** — a WebSocket chat room per course, built with Django
  Channels, backed by a Redis channel layer and persisted to the database.
- **Caching** — course and subject listings are cached with Redis to reduce
  database load.

## Tech stack

| Layer         | Technology                                   |
|---------------|-----------------------------------------------|
| Backend       | Django 5, Django REST Framework                |
| Real-time     | Django Channels, Daphne (ASGI), Redis          |
| Database      | PostgreSQL                                     |
| Cache         | Redis (via `pymemcache`/`django-redisboard`)   |
| Web server    | uWSGI + Nginx                                  |
| Deployment    | Docker & Docker Compose                        |

## Project structure

```
education/
├── courses/     # Subjects, courses, modules, content, ordering, REST API
├── students/    # Registration, enrollment, student course views
├── chat/        # WebSocket consumer + chat models
└── education/   # Project settings (base/local/prod), URLs, ASGI/WSGI
config/
├── nginx/       # Nginx templates
└── uwsgi/       # uWSGI config
```

## Getting started

### With Docker (recommended)

```bash
docker compose up --build
```

This starts PostgreSQL, Redis, the uWSGI app server, Daphne (for WebSockets),
and Nginx as a reverse proxy.

### Local development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd education
export DJANGO_SETTINGS_MODULE=education.settings.local
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

You'll need local PostgreSQL and Redis instances, or point the settings at
your own. Environment-specific values are managed with `python-decouple`.

## Running tests

```bash
cd education
python manage.py test
```

## License

This project is for personal/educational purposes.
