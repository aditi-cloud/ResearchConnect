# ResearchConnect

A Django-based research portal for connecting with faculty and exploring research opportunities.

## Prerequisites

- **Python 3.8+** (3.10 or 3.11 recommended)
- **pip** (Python package manager)

## Steps to Run

### 1. Navigate to the project directory

```bash
cd ResearchConnect/portal
```

### 2. Create a virtual environment (recommended)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Database setup

The project already uses **SQLite** and includes a database with faculty records. No database service or credentials are required for local development.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

### 7. Access the application

- **Homepage:** http://127.0.0.1:8000/
- **Search:** http://127.0.0.1:8000/search/

---

## Adding Professor Details

Faculty data is managed through code and Django management commands. Run these
commands from `ResearchConnect/portal/` with the virtual environment active.

### Import faculty

Preview the existing scrapers without saving records:

```bash
python manage.py scrape_all_faculty --dry-run
```

Import records from the configured sources:

```bash
python manage.py scrape_all_faculty
```

Run an individual importer when needed:

```bash
python manage.py scrape_iit_faculty
python manage.py scrape_iim_iisc_mitwpu
```

The importers skip records already present with the same name and college. They
require network access to the source websites.

### Add or update faculty through code

Open the Django shell:

```bash
python manage.py shell
```

Then use the model directly:

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

Replace the placeholders with the faculty's details. Research areas must be a
list of strings. Saved records appear in the public directory.

### Professor fields reference

| Field | Required | Example |
|-------|----------|---------|
| Name | Yes | [Name] |
| College | No | IIT Kharagpur |
| Department | No | Computer Science |
| Designation | No | Professor |
| Email | No | name@example.com |
| Phone | No | +91 98765 43210 |
| Profile URL | No | https://cse.iitkgp.ac.in/~john |
| Research Areas | No | `["Machine Learning", "AI", "NLP"]` |

---

## Quick Reference (macOS/Linux, from repository root)

```bash
cd ResearchConnect/portal
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

If a dependency download times out, retry with:

```bash
python -m pip install --timeout 120 --retries 10 -r requirements.txt
```

## Static files

Source images live in `portal/faculty/static/images/`.
The development server finds these assets automatically.

Generated static files are excluded from Git. Before deploying, run this from
`ResearchConnect/portal/` to generate `public/static/`:

```bash
python manage.py collectstatic --noinput --clear
```

Include that generated directory in the deployment artifact; regenerate it after
changing assets or upgrading Django.

## Checks

From `ResearchConnect/portal/` with the virtual environment active:

```bash
python manage.py check
python manage.py test
```
