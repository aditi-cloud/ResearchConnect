from urllib.parse import unquote_plus

from django.db.models import Q
from django.shortcuts import render

from .models import Faculty


def _filter_choices(faculties):
    return {
        'research_areas': sorted({area for faculty in faculties for area in faculty.research_areas or []}),
        'colleges': sorted({faculty.college for faculty in faculties if faculty.college}),
    }


def search(request):
    query = request.GET.get('query')
    all_faculties = Faculty.objects.all()
    faculties = all_faculties

    if query:
        faculties = faculties.filter(
            Q(college__icontains=query)
            | Q(name__icontains=query)
            | Q(department__icontains=query)
            | Q(research_areas__icontains=query)
        )
    for parameter, field in (('university', 'college'), ('area', 'research_areas')):
        value = request.GET.get(parameter)
        if value:
            faculties = faculties.filter(**{f'{field}__icontains': unquote_plus(value)})

    context = {'Faculties': faculties, **_filter_choices(all_faculties)}
    return render(request, 'faculty/search.html', context)


def professor(request, professor_name):
    professor = Faculty.objects.get(pk=request.GET.get('id'))
    return render(request, 'faculty/professor.html', {'professor': professor})


def home(request):
    faculties = Faculty.objects.all()
    context = {**_filter_choices(faculties), 'Faculties': faculties[:3]}
    return render(request, 'faculty/home.html', context)
