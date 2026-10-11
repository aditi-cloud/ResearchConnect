import re
from functools import partial

from bs4 import BeautifulSoup

from faculty.scraping import FacultyImportCommand, add_unique, fetch

fetch = partial(fetch, timeout=20)


def parse_iim_consortium(html, college=None):

    soup = BeautifulSoup(html, 'html.parser')
    faculties = []

    for h3 in soup.find_all('h3'):
        text = h3.get_text(strip=True)
        match = re.match(r'^(.+?)\s*\(IIM\s+.+\)\s*$', text, re.I)
        if match:
            name = match.group(1).strip()
            inst = college or 'IIM'
        else:
            continue
        if len(name) < 3 or 'Faculty' in name or 'Search' in name:
            continue

        block_text = ''
        for sib in h3.find_next_siblings():
            if sib.name == 'h3':
                break
            block_text += sib.get_text() + ' '
        if not block_text:
            block = h3.find_next()
            if block:
                block_text = block.get_text()
        email = None
        department = None
        research_areas = []
        em_match = re.search(r'Email[:\s]*(?:&nbsp;)?([a-zA-Z0-9_.+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', block_text, re.I)
        if em_match:
            email = em_match.group(1).strip()
        area_match = re.search(r'Subject/Area[:\s]*([^\n]+?)(?=Email|Website|$)', block_text, re.I)
        if area_match:
            dept = area_match.group(1).strip()
            department = dept[:100]
            research_areas = [d.strip() for d in re.split(r'[,&]', dept) if len(d.strip()) > 3][:3]
        faculties.append({
            'name': name,
            'email': email,
            'phone': None,
            'college': inst,
            'department': department or 'Management',
            'designation': None,
            'research_areas': research_areas[:5] or ['Management'],
        })
    return faculties


def parse_iim_calcutta(html, college="IIM Calcutta"):

    soup = BeautifulSoup(html, 'html.parser')
    faculties = []
    seen = set()
    for mailto in soup.find_all('a', href=re.compile(r'mailto:.*iimcal\.ac\.in')):
        email = mailto['href'].replace('mailto:', '').split('?')[0].strip()
        if not email or '@' not in email:
            continue
        block = mailto.parent
        for _ in range(5):
            if not block:
                break
            block = block.parent
        if not block:
            block = mailto.parent

        user_link = block.find('a', href=re.compile(r'/users/'))
        name = user_link.get_text(strip=True) if user_link else None
        if not name or name in seen:
            continue

        dept_el = block.find(string=re.compile(r'Department'))
        dept = None
        if dept_el:
            parent = dept_el.parent
            if parent:
                next_el = parent.find_next_sibling() or parent.find_next()
                dept = next_el.get_text(strip=True)[:80] if next_el else None
        seen.add(name)
        faculties.append({
            'name': name,
            'email': email,
            'phone': None,
            'college': college,
            'department': dept or 'Management',
            'designation': None,
            'research_areas': [dept] if dept else ['Management'],
        })
    return faculties


def parse_iisc_csa(html, college="IISc Bangalore"):

    soup = BeautifulSoup(html, 'html.parser')
    faculties = []
    seen = set()

    for link in soup.find_all('a', href=re.compile(r'csa\.iisc\.ac\.in/~|cds\.iisc\.ac\.in/~|/~\w+')):
        name = link.get_text(strip=True)
        if not name or len(name) < 3 or name in seen:
            continue
        block = link.find_parent(['div', 'article', 'p', 'li'])
        if not block:
            block = link.parent
        for _ in range(3):
            if block and block.name in ('div', 'article', 'li', 'section'):
                break
            block = block.parent if block else None
        if not block:
            continue
        text = block.get_text()
        em_match = re.search(r'([a-z0-9]+)\s*\[\s*AT\s*\]\s*iisc\.ac\.in', text, re.I)
        email = f"{em_match.group(1)}@iisc.ac.in" if em_match else None
        ra_match = re.search(r'\[AT\].*?iisc\.ac\.in\s*([^\n\[\]]{15,200})', text, re.DOTALL)
        research_text = ra_match.group(1).strip() if ra_match else ''
        if 'Adjunct' in research_text:
            research_text = re.sub(r'Adjunct Professor.*', '', research_text).strip()
        research_areas = [a.strip() for a in re.split(r'[,;]', research_text) if len(a.strip()) > 5][:5]
        if not research_areas and research_text:
            research_areas = [research_text[:80]]
        seen.add(name)
        faculties.append({
            'name': name,
            'email': email,
            'phone': None,
            'college': college,
            'department': 'Computer Science and Automation',
            'designation': None,
            'research_areas': research_areas[:5],
        })
    return faculties


def parse_mit_wpu(html, college="MIT WPU Pune"):

    soup = BeautifulSoup(html, 'html.parser')
    faculties = []

    for card in soup.select('.faculty-card, .faculty-item, .member-card, [class*="faculty"], [class*="member"]'):
        name_el = card.find(['h3', 'h4', 'h5', 'strong', 'a'])
        if not name_el:
            continue
        name = name_el.get_text(strip=True)
        if not name or len(name) < 4 or len(name) > 60:
            continue

        if name.lower() in ('menu', 'home', 'apply', 'view more', 'teaching', 'non teaching'):
            continue
        text = card.get_text()
        email_match = re.search(r'([a-z0-9_.]+@mitwpu\.edu\.in)', text, re.I)
        email = email_match.group(1) if email_match else None
        dept_match = re.search(r'(Engineering|Computer Science|Business|Management|School of)', text, re.I)
        dept = dept_match.group(0)[:80] if dept_match else 'MIT WPU'
        faculties.append({
            'name': name,
            'email': email,
            'phone': None,
            'college': college,
            'department': dept,
            'designation': None,
            'research_areas': [dept],
        })

    if len(faculties) < 5:
        for mailto in soup.find_all('a', href=re.compile(r'mailto:.*mitwpu\.edu\.in')):
            email = mailto['href'].replace('mailto:', '').split('?')[0].strip()
            if 'admissions' in email or 'info' in email:
                continue
            block = mailto.parent
            for _ in range(6):
                if not block:
                    break
                block = block.parent
            name_el = (block.find('h2') or block.find('h3') or block.find('h4')) if block else None
            name = name_el.get_text(strip=True) if name_el else None
            if name and len(name) > 3:
                faculties.append({
                    'name': name,
                    'email': email,
                    'phone': None,
                    'college': college,
                    'department': 'MIT WPU',
                    'designation': None,
                    'research_areas': ['MIT WPU'],
                })
    return faculties


IIM_CAMPUSES = (
    'Ahmedabad', 'Calcutta', 'Bangalore', 'Lucknow', 'Indore', 'Kozhikode',
    'Mumbai', 'Ranchi', 'Raipur', 'Rohtak', 'Jammu', 'Nagpur',
    'Sambalpur', 'Shillong', 'Sirmaur', 'Tiruchirappalli', 'Udaipur', 'Visakhapatnam',
    'Bodh Gaya', 'Amritsar', 'Kashipur',
)

IIM_CONSORTIUM_URLS = [
    (f"https://iimlibrariesconsortium.in/faculty/IIM_{campus.replace(' ', '_')}.html", f'IIM {campus}')
    for campus in IIM_CAMPUSES
]


class Command(FacultyImportCommand):
    help = 'Scrape faculty from IIMs, IISc, and MIT WPU'

    def handle(self, *args, **options):
        all_faculties = []
        existing_names = set()

        sources = [
            (url, parse_iim_consortium, college, None)
            for url, college in IIM_CONSORTIUM_URLS
        ] + [
            ('https://www.iimcal.ac.in/faculty/faculty-directory', parse_iim_calcutta, 'IIM Calcutta', None),
            ('https://www.csa.iisc.ac.in/people-all/faculty/', parse_iisc_csa, 'IISc Bangalore', None),
            ('https://cds.iisc.ac.in/people-all/faculty/', parse_iisc_csa, 'IISc Bangalore', 'Computational and Data Sciences'),
        ]
        for url, parser, college, department in sources:
            self.stdout.write(f'Fetching {department or college}...')
            html = fetch(url)
            if not html:
                continue
            candidates = parser(html, college)
            if department:
                for record in candidates:
                    record['department'] = department
            new = add_unique(all_faculties, candidates, existing_names)
            self.stdout.write(self.style.SUCCESS(f'  {college}: {len(new)} faculty'))


        self.stdout.write('Fetching MIT WPU Pune...')
        for url in ['https://mitwpu.edu.in/faculty-members', 'https://mitwpu.edu.in/faculty/teaching']:
            html = fetch(url)
            if html:
                new = add_unique(all_faculties, parse_mit_wpu(html), existing_names)
                if new:
                    self.stdout.write(self.style.SUCCESS(f'  MIT WPU: {len(new)} faculty'))
                break

        self.save_faculties(all_faculties, **options)
