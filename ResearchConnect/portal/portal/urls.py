from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView

from faculty import views

ARTICLES = (
    'optimizing-your-resume', 'sample-cover-letter', 'tips-for-cold-emailing',
    'tips-for-getting-internships', 'undergraduate-physics-research-internships',
)

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('professor/<slug:professor_name>/', views.professor, name='professor'),
] + [
    path(f'{slug}/', TemplateView.as_view(template_name=f'faculty/blog{number}.html'), name=slug)
    for number, slug in enumerate(ARTICLES, 1)
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
