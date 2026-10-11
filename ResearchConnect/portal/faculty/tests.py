from django.test import TestCase
from django.urls import reverse

from .models import Faculty
from .scraping import FacultyImportCommand, fetch


class FacultyViewsTests(TestCase):
    def test_admin_pages_are_unavailable(self):
        for url in ('/admin/', '/admin/login/'):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    @classmethod
    def setUpTestData(cls):
        cls.delhi = Faculty.objects.create(
            name='Alice Example', college='IIT Delhi',
            department='Computer Science', research_areas=['Algorithms', 'AI'],
        )
        cls.kanpur = Faculty.objects.create(
            name='Bob Example', college='IIT Kanpur',
            department='Mathematics', research_areas=['Algorithms'],
        )
        cls.physics = Faculty.objects.create(
            name='Carol Example', college='IIT Delhi',
            department='Physics', research_areas=['Optics'],
        )
        cls.empty = Faculty.objects.create(
            name='Dana Example', college=None, research_areas=None,
        )

    def test_search_matches_each_searchable_field(self):
        cases = {
            'Alice': [self.delhi],
            'Kanpur': [self.kanpur],
            'Computer': [self.delhi],
            'Optics': [self.physics],
        }
        for query, expected in cases.items():
            with self.subTest(query=query):
                response = self.client.get(reverse('search'), {'query': query})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(list(response.context['Faculties']), expected)

    def test_filters_combine_with_search(self):
        response = self.client.get(reverse('search'), {
            'query': 'Example', 'university': 'IIT Delhi', 'area': 'Algorithms',
        })
        self.assertEqual(list(response.context['Faculties']), [self.delhi])
        self.assertEqual(response.context['colleges'], ['IIT Delhi', 'IIT Kanpur'])
        self.assertEqual(response.context['research_areas'], ['AI', 'Algorithms', 'Optics'])

    def test_home_limits_featured_faculty_and_handles_empty_fields(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['Faculties']), [self.delhi, self.kanpur, self.physics])
        self.assertEqual(response.context['colleges'], ['IIT Delhi', 'IIT Kanpur'])
        self.assertEqual(response.context['research_areas'], ['AI', 'Algorithms', 'Optics'])

    def test_articles_keep_their_routes_and_templates(self):
        routes = [
            'optimizing-your-resume', 'sample-cover-letter', 'tips-for-cold-emailing',
            'tips-for-getting-internships', 'undergraduate-physics-research-internships',
        ]
        for number, route in enumerate(routes, start=1):
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, f'faculty/blog{number}.html')

    def test_professor_detail_uses_requested_id(self):
        response = self.client.get(
            reverse('professor', kwargs={'professor_name': 'alice-example'}),
            {'id': self.delhi.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['professor'], self.delhi)
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command


class FacultyImportTests(TestCase):
    def test_dry_run_limit_and_existing_records(self):
        records = [
            {'name': 'First Example', 'college': 'IIT Delhi'},
            {'name': 'Second Example', 'college': 'IIT Delhi'},
        ]
        command = FacultyImportCommand(stdout=StringIO())
        command.save_faculties(records, dry_run=True)
        self.assertFalse(Faculty.objects.exists())
        command.save_faculties(records, limit=1)
        self.assertEqual(Faculty.objects.count(), 1)
        command.save_faculties(records, limit=1)
        self.assertEqual(Faculty.objects.count(), 2)
        self.assertEqual(Faculty.objects.get(name='Second Example').research_areas, [])

    def test_iim_iisc_and_mit_sources_keep_their_departments(self):
        pages = {
            'https://iimlibrariesconsortium.in/faculty/IIM_Ahmedabad.html': '''
                <h3>Management Example (IIM Ahmedabad)</h3>
                <p>Subject/Area: Finance Email: example@example.com</p>
            ''',
            'https://cds.iisc.ac.in/people-all/faculty/': '''
                <div><a href="https://csa.iisc.ac.in/~example">Science Example</a>
                example [AT] iisc.ac.in Machine Learning, Algorithms</div>
            ''',
            'https://mitwpu.edu.in/faculty/teaching': '''
                <div class="faculty-card"><h3>Engineering Example</h3>
                <p>Computer Science</p></div>
            ''',
        }
        with patch('faculty.management.commands.scrape_iim_iisc_mitwpu.fetch', side_effect=pages.get):
            call_command('scrape_iim_iisc_mitwpu', stdout=StringIO())
        self.assertEqual(Faculty.objects.count(), 3)
        self.assertEqual(Faculty.objects.get(name='Management Example').college, 'IIM Ahmedabad')
        self.assertEqual(
            Faculty.objects.get(name='Science Example').department, 'Computational and Data Sciences',
        )
        self.assertEqual(Faculty.objects.get(name='Engineering Example').college, 'MIT WPU Pune')

    def test_import_command_inserts_faculty_without_admin(self):
        html = '''
            <div class="card-agent">
                <h3>Imported Example</h3>
                <a href="mailto:example@cse.iitd.ac.in">Email</a>
                <p>Machine Learning</p>
            </div>
        '''
        with patch(
            'faculty.management.commands.scrape_iit_faculty.fetch',
            side_effect=lambda url: html if 'homecse.iitd.ac.in' in url else None,
        ):
            call_command('scrape_iit_faculty', limit=1, stdout=StringIO())
        faculty = Faculty.objects.get(name='Imported Example')
        self.assertEqual(faculty.college, 'IIT Delhi')
        self.assertEqual(faculty.email, 'example@cse.iitd.ac.in')
        self.assertEqual(faculty.research_areas, ['Machine Learning'])


class FetchTests(TestCase):
    @patch('faculty.scraping.requests.get')
    def test_success_and_ssl_retry(self, get):
        from requests.exceptions import SSLError

        get.side_effect = [SSLError('test'), get.return_value]
        get.return_value.text = 'Faculty page'
        self.assertEqual(fetch('https://example.com', timeout=20), 'Faculty page')
        self.assertTrue(get.call_args_list[0].kwargs['verify'])
        self.assertFalse(get.call_args_list[1].kwargs['verify'])
        self.assertEqual(get.call_args_list[1].kwargs['timeout'], 20)

    @patch('builtins.print')
    @patch('faculty.scraping.requests.get')
    def test_failed_fetch_returns_none(self, get, print_error):
        from requests.exceptions import Timeout

        get.side_effect = Timeout('test')
        self.assertIsNone(fetch('https://example.com'))
        print_error.assert_called_once()
