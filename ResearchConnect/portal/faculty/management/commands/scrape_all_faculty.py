from django.core.management import call_command

from faculty.scraping import FacultyImportCommand


class Command(FacultyImportCommand):
    help = 'Scrape faculty from IITs, IIMs, IISc, and MIT WPU'

    def handle(self, *args, **options):
        for command in ('scrape_iit_faculty', 'scrape_iim_iisc_mitwpu'):
            self.stdout.write(self.style.NOTICE(f'Running {command}...'))
            call_command(command, **options)
