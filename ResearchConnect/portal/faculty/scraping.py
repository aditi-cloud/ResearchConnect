import requests
from django.core.management.base import BaseCommand

from .models import Faculty

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ResearchConnect/1.0',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
}


def fetch(url, timeout=15, verify_ssl=True):
    try:
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout, verify=verify_ssl)
        except requests.exceptions.SSLError:
            response = requests.get(url, headers=HEADERS, timeout=timeout, verify=False)
        response.raise_for_status()
        return response.text
    except Exception as error:
        print(f'  Error fetching {url}: {error}')
        return None


def add_unique(records, candidates, seen):
    new = []
    for record in candidates:
        key = (record['name'], record['college'])
        if key not in seen:
            seen.add(key)
            new.append(record)
    records.extend(new)
    return new


class FacultyImportCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Fetch and parse without saving')
        parser.add_argument('--limit', type=int, default=0, help='Maximum new records (0=no limit)')

    def save_faculties(self, records, *, dry_run=False, limit=0, **options):
        self.stdout.write(f'\nTotal faculty collected: {len(records)}')
        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run - not saving to database'))
            for number, record in enumerate(records[:20], 1):
                self.stdout.write(f"  {number}. {record['name']} - {record['college']}")
            return

        existing = set(Faculty.objects.values_list('name', 'college'))
        added = 0
        for record in records:
            if limit and added >= limit:
                break
            key = (record['name'], record.get('college') or '')
            if key in existing:
                continue
            fields = {
                field: record.get(field) or None
                for field in ('email', 'phone', 'college', 'department', 'designation')
            }
            Faculty.objects.create(
                name=record['name'], research_areas=record.get('research_areas') or [], **fields,
            )
            existing.add(key)
            added += 1
        self.stdout.write(self.style.SUCCESS(
            f'\nAdded {added} professors to database. Total: {Faculty.objects.count()}'
        ))
