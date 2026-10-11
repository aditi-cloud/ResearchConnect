import re

from bs4 import BeautifulSoup

from faculty.scraping import FacultyImportCommand, add_unique, fetch


def parse_iit_kanpur(html, college="IIT Kanpur"):

    soup = BeautifulSoup(html, 'html.parser')
    faculties = []

    blocks = soup.find_all(['a', 'div'], href=re.compile(r'/users/'))
    seen = set()
    for block in blocks:
        if block.name == 'a':
            link = block
        else:
            link = block.find('a', href=re.compile(r'/users/'))
        if not link:
            continue

        name_el = (block.find('h5') or block.find('h4') or block.find('h3') or link)
        name = name_el.get_text(strip=True).split('\n')[0].strip()
        if not name or len(name) < 3 or name in seen:
            continue

        uname_match = re.search(r'\(([a-z0-9]+)\)', block.get_text())
        email = f"{uname_match.group(1)}@cse.iitk.ac.in" if uname_match else None

        phone_match = re.search(r'\+\d+\s*\(\d+\)\s*259[/]?679[-]?\d+', block.get_text())
        phone = phone_match.group(0).strip() if phone_match else None

        text = block.get_text()
        research_match = re.search(r'(Complexity|Cryptography|Algorithms|Machine Learning|Networks|Database|NLP|Systems|Vision|Theory|Security|Formal|IoT|Compilers)[^\]\n]*', text, re.I)
        research_text = research_match.group(0).strip() if research_match else ''
        research_areas = [a.strip() for a in re.split(r'[,;]', research_text) if len(a.strip()) > 4][:5]
        if not research_areas and research_text:
            research_areas = [research_text[:80]]
        if name:
            seen.add(name)
            faculties.append({
                'name': name,
                'email': email,
                'phone': phone,
                'college': college,
                'department': 'Computer Science and Engineering',
                'designation': None,
                'research_areas': research_areas[:5],
            })
    return faculties


def parse_iit_kharagpur(html, college="IIT Kharagpur"):

    soup = BeautifulSoup(html, 'html.parser')
    faculties = []

    for heading in soup.find_all(['h5', 'h4', 'h3']):
        name = heading.get_text(strip=True)
        if not name or len(name) < 4:
            continue
        block = heading.find_parent(['div', 'section']) or heading
        text = block.get_text() if block else ''

        email_match = re.search(r'([a-z0-9_.]+)\s*\[\s*at\s*\]\s*cse\.iitkgp\.ac\.in', text, re.I)
        if email_match:
            email = f"{email_match.group(1)}@cse.iitkgp.ac.in"
        else:
            email_match = re.search(r'([a-z0-9_.]+)\s*\[\s*at\s*\]\s*iitkgp\.ac\.in', text, re.I)
            email = f"{email_match.group(1)}@iitkgp.ac.in" if email_match else None

        phone_match = re.search(r'Phone:\s*(\d{4,6})', text, re.I)
        phone = f"+91-3222-28{phone_match.group(1)}" if phone_match else None

        ra_match = re.search(r'Research Areas?:\s*([^\n]+)', text, re.I)
        research_text = ra_match.group(1).strip() if ra_match else ''
        research_areas = [a.strip() for a in re.split(r'[,;]', research_text) if len(a.strip()) > 2][:6]

        desig_match = re.search(r'(Professor|Associate Professor|Assistant Professor|Head of Department|Distinguished)', text, re.I)
        designation = desig_match.group(0) if desig_match else None
        if name:
            faculties.append({
                'name': name,
                'email': email,
                'phone': phone,
                'college': college,
                'department': 'Computer Science and Engineering',
                'designation': designation,
                'research_areas': research_areas[:5],
            })
    return faculties


def parse_iit_roorkee(html, college="IIT Roorkee"):

    soup = BeautifulSoup(html, 'html.parser')
    faculties = []
    seen = set()

    for elem in soup.find_all(string=re.compile(r'\[at\]\s*cs\.iitr\.ac\.in', re.I)):
        block = elem.parent
        for _ in range(8):
            if not block:
                break
            if getattr(block, 'name', None) in ('div', 'article', 'section', 'li'):
                break
            block = getattr(block, 'parent', None)
        if not block:
            block = elem.parent
        if not block:
            continue
        text = block.get_text()

        email_match = re.search(r'([a-z0-9_.]+)\s*\[\s*at\s*\]\s*cs\.iitr\.ac\.in', text, re.I)
        email = f"{email_match.group(1)}@cs.iitr.ac.in" if email_match else None

        lines = [l.strip() for l in text.split('\n') if l.strip()]
        name = None
        for line in lines[:5]:
            if re.match(r'^[A-Z][a-zA-Z.\s]+$', line) and len(line) > 5 and 'at' not in line.lower():
                name = line
                break
        if not name:

            for tag in block.find_all(['strong', 'b', 'h2', 'h3', 'h4']):
                t = tag.get_text(strip=True)
                if len(t) > 4 and t not in ('Professor', 'Assistant', 'Associate', 'READ MORE'):
                    name = t
                    break
        if not name or name in seen:
            continue

        phone_match = re.search(r'(\+91[-]?[\d\s\-]{10,15}|\d{10})', text)
        phone = phone_match.group(1).strip() if phone_match else None
        desig_match = re.search(r'(Professor|Associate professor|Assistant professor|Head of the Department)', text, re.I)
        designation = desig_match.group(0) if desig_match else None
        research_match = re.search(r'(Computer Vision|IoT|Cryptography|Algorithms|Machine Learning|Software Engineering|Security|Networks|Data Mining|NLP|Formal Methods|Distributed|Embedded)[^\[\]]{5,100}', text, re.I)
        research_text = research_match.group(0).strip() if research_match else ''
        research_areas = [a.strip() for a in re.split(r'[,;]', research_text) if len(a.strip()) > 5][:5]
        if not research_areas and research_text:
            research_areas = [research_text[:80]]
        seen.add(name)
        faculties.append({
            'name': name,
            'email': email,
            'phone': phone,
            'college': college,
            'department': 'Computer Science and Engineering',
            'designation': designation,
            'research_areas': research_areas[:5],
        })
    return faculties


def parse_iit_guwahati(html, college="IIT Guwahati"):

    soup = BeautifulSoup(html, 'html.parser')
    faculties = []

    for heading in soup.find_all(['h3', 'h4']):
        name = heading.get_text(strip=True)
        if not name or len(name) < 4:
            continue
        block = heading.find_parent(['div', 'article', 'li']) or heading
        text = block.get_text() if block else ''

        email_match = re.search(r'([a-z0-9_.]+)\s*@\s*iitg\.ac\.in', text, re.I)
        if not email_match:
            email_match = re.search(r'Email[:\s]*([a-z0-9_.]+)\s*@', text, re.I)
        email = None
        if email_match:
            user = email_match.group(1).strip()
            if '.' in user or len(user) > 2:
                email = f"{user}@iitg.ac.in"

        ext_match = re.search(r'(\+91[-]?361[-]?258[-]?\d{4})', text)
        phone = ext_match.group(1) if ext_match else None
        desig_match = re.search(r'(Professor|Associate Professor|Assistant Professor|Senior Professor|Head)', text, re.I)
        designation = desig_match.group(0) if desig_match else None

        ra_match = re.search(r'Research Interest[:\s]*([^\*]+)', text, re.I)
        research_text = ra_match.group(1).strip() if ra_match else ''
        research_areas = [a.strip() for a in re.split(r'[,;]', research_text) if len(a.strip()) > 3][:6]
        if not research_areas and research_text:
            research_areas = [research_text[:80]]
        if name:
            faculties.append({
                'name': name,
                'email': email,
                'phone': phone,
                'college': college,
                'department': 'Computer Science and Engineering',
                'designation': designation,
                'research_areas': research_areas[:5],
            })
    return faculties


def parse_iit_delhi_v2(html, college="IIT Delhi"):

    soup = BeautifulSoup(html, 'html.parser')
    faculties = []
    seen = set()

    for card in soup.select('.card-agent, .property-item, .agent-item, .w-dyn-item'):
        h3 = card.find('h3') or card.find('h2')
        if not h3:
            continue
        name = h3.get_text(strip=True)
        if not name or len(name) < 3 or name in seen:
            continue
        mailto = card.find('a', href=re.compile(r'^mailto:'))
        email = mailto['href'].replace('mailto:', '').strip() if mailto else None
        if not email or 'cse.iitd.ac.in' not in email:
            continue
        tel = card.find('a', href=re.compile(r'^tel:'))
        phone = (tel.get_text(strip=True) or tel.get('href', '').replace('tel:', '').strip()) if tel else None
        desig_link = card.find('a', href=re.compile(r'/team/'))
        designation = None
        if desig_link:
            for a in card.find_all('a', href=re.compile(r'/team/')):
                t = a.get_text(strip=True)
                if t and t != name and len(t) < 50 and 'Professor' in t:
                    designation = t
                    break
        p = card.find('p')
        research_text = p.get_text(strip=True)[:300] if p else ''
        research_areas = [a.strip() for a in re.split(r'[,;]', research_text) if 4 < len(a.strip()) < 60][:5]
        if not research_areas and research_text:
            research_areas = [research_text[:80]]
        seen.add(name)
        faculties.append({
            'name': name,
            'email': email,
            'phone': phone,
            'college': college,
            'department': 'Computer Science and Engineering',
            'designation': designation,
            'research_areas': research_areas[:5],
        })

    if len(faculties) < 10:
        for mailto in soup.find_all('a', href=re.compile(r'mailto:.*cse\.iitd\.ac\.in')):
            email = mailto['href'].replace('mailto:', '').split('?')[0].strip()
            if not email:
                continue
            block = mailto.parent
            for _ in range(6):
                if not block:
                    break
                block = block.parent
            if not block:
                block = mailto.parent
            name_el = (block.find('h2') or block.find('h3') or block.find('h4'))
            name = name_el.get_text(strip=True) if name_el else None
            if not name or name in seen:
                continue
            tel = block.find('a', href=re.compile(r'^tel:'))
            phone = (tel.get_text(strip=True) or (tel.get('href', '').replace('tel:', ''))) if tel else None
            text = block.get_text()
            ra = re.search(r'(Algorithms|ML|NLP|Vision|Systems|Networks|Security|Database|AI)[^\.\n]*', text, re.I)
            research_areas = [ra.group(0).strip()[:60]] if ra else []
            seen.add(name)
            faculties.append({
                'name': name,
                'email': email,
                'phone': phone,
                'college': college,
                'department': 'Computer Science and Engineering',
                'designation': None,
                'research_areas': research_areas[:5],
            })
    return faculties


class Command(FacultyImportCommand):
    help = 'Scrape faculty from IITs and add to database'

    def handle(self, *args, **options):
        all_faculties = []
        existing_names = set()
        sources = [
            ('https://homecse.iitd.ac.in/faculty/', parse_iit_delhi_v2, 'IIT Delhi'),
            ('https://www.cse.iitk.ac.in/pages/Faculty.html', parse_iit_kanpur, 'IIT Kanpur'),
            ('https://cse.iitkgp.ac.in/faculty4.php', parse_iit_kharagpur, 'IIT Kharagpur'),
            ('https://iitr.ac.in/Departments/Computer%20Science%20and%20Engineering%20Department/People/Faculty/index.html', parse_iit_roorkee, 'IIT Roorkee'),
            ('https://www.iitg.ac.in/cse/faculty.php', parse_iit_guwahati, 'IIT Guwahati'),
        ]
        for url, parser_fn, college in sources:
            self.stdout.write(f'Fetching {college}...')
            html = fetch(url)
            if not html:
                continue
            new_facs = add_unique(all_faculties, parser_fn(html, college), existing_names)
            self.stdout.write(self.style.SUCCESS(f'  Found {len(new_facs)} faculty from {college}'))


        iitm_url = 'https://www.cse.iitm.ac.in/listpeople.php?arg=RmFjdWx0eSEzJDEkMTEk'
        if len(all_faculties) < 80:
            self.stdout.write('Fetching IIT Madras...')
            html = fetch(iitm_url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                for link in soup.select('a[href*="profile.php"]'):
                    name = link.get_text(strip=True)
                    if name and len(name) > 3:
                        all_faculties.append({
                            'name': name,
                            'email': None,
                            'phone': None,
                            'college': 'IIT Madras',
                            'department': 'Computer Science and Engineering',
                            'designation': None,
                            'research_areas': ['Computer Science'],
                        })

        self.save_faculties(all_faculties, **options)
