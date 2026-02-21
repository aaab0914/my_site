# my_site

A Django-based blog website with tag support, sitemap integration, PostgreSQL, and Docker deployment.

## Features

- Django 6 project
- Blog app with tag support
- PostgreSQL database
- Sitemap and site framework support
- Docker and Docker Compose setup
- Static files support

## Tech Stack

- Python
- Django
- PostgreSQL
- django-taggit
- django-doc
- Docker

## Project Structure

```bash
my_site/
├── blog/
├── my_site/
├── static/
├── manage.py
├── main.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Local Development

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd my_site
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
# or
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file with values like:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=blog
DB_USER=blog
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open:

```bash
http://127.0.0.1:8000/
```

## Docker

### Build and run with Docker Compose

```bash
docker compose up --build
```

## Notes

- The project uses PostgreSQL by default.
- Static files are served from the `static/` directory.
- Sitemap and site framework support are enabled.

## License

Add your preferred license here.
