# ResearchConnect

A Django portal for finding professors, exploring research areas, and accessing
resources for research internships and applications.

## Features

- Search faculty by name, college, department, or research area.
- Filter results by university and research area.
- View professor profiles and contact details.
- Read guides on resumes, cover letters, emailing professors, and internships.
- Import faculty through management commands or manage records through Python.

The portal uses SQLite and includes an existing faculty database.

## Run locally

Run these commands from the repository root. Use Python 3.9, 3.10, or 3.11 with pip.

### macOS / Linux

```bash
cd ResearchConnect/portal
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Windows PowerShell

```powershell
cd ResearchConnect/portal
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open [the homepage](http://127.0.0.1:8000/) or
[the faculty directory](http://127.0.0.1:8000/search/).
Press Ctrl+C in the server terminal to stop it.

### Start again

After the initial setup, run this on macOS / Linux:

```bash
cd ResearchConnect/portal
source .venv/bin/activate
python manage.py runserver
```

On Windows, activate `.venv` with `.\.venv\Scripts\Activate.ps1` instead.
Run `python manage.py migrate` after pulling changes that add database migrations.

If a package download times out, retry the installation with:

```bash
python -m pip install --timeout 120 --retries 10 -r requirements.txt
```

The templates load styles and scripts from external services, so the site's
full styling and interactions require an internet connection.

## Import faculty

Run all remaining commands from `ResearchConnect/portal/` with `.venv` active.

Preview data without writing to the database:

```bash
python manage.py scrape_all_faculty --dry-run
```

Import faculty from the configured IIT, IIM, IISc, and MIT WPU sources:

```bash
python manage.py scrape_all_faculty
```

Run either importer separately:

```bash
python manage.py scrape_iit_faculty
python manage.py scrape_iim_iisc_mitwpu
```

Limit the number of new records:

```bash
python manage.py scrape_iit_faculty --limit 50
```

Both importers support `--dry-run` and `--limit`. A limit of `0` means no limit.
With `scrape_all_faculty`, the limit applies separately to each importer.
Existing records with the same name and college are skipped rather than updated.
Imports require network access and depend on the source websites' HTML structure.

## Add or update records through Python

Open the Django shell:

```bash
python manage.py shell
```

Use the `Faculty` model:

```python
from faculty.models import Faculty

faculty, created = Faculty.objects.update_or_create(
    name="[Name]",
    college="[College]",
    defaults={
        "department": "[Department]",
        "designation": "[Designation]",
        "email": "name@example.com",
        "research_areas": ["Machine Learning", "AI"],
    },
)
```

Replace the placeholders before saving. `name` is required; optional fields are
`college`, `department`, `designation`, `email`, `phone`, `profile_url`, and
`research_areas`. Store research areas as a list of strings. Saved records appear
in the faculty directory.

## Project structure

```text
ResearchConnect/
├── README.md
└── portal/
    ├── manage.py
    ├── requirements.txt
    ├── db.sqlite3
    ├── vercel.json
    ├── portal/                 Django settings, routes, and entry points
    └── faculty/
        ├── models.py           Faculty database model
        ├── views.py            Homepage, search, and profile views
        ├── scraping.py         Shared fetch and import logic
        ├── tests.py
        ├── management/commands/
        ├── migrations/
        ├── static/images/      Source images
        └── templates/faculty/  Shared layout and page templates
```

The repository-root `requirements.txt` delegates to
`ResearchConnect/portal/requirements.txt`.

## Static files

The development server finds source assets automatically. To generate static
files for a deployment artifact:

```bash
python manage.py collectstatic --noinput --clear
```

This rebuilds `public/static/`, which is excluded from Git. Include that directory
in the deployment artifact and regenerate it after changing assets.

## Checks

```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
```

Tests cover public pages, search filters, unavailable admin routes, faculty
imports, duplicate handling, import limits, dry runs, and fetch error handling.
