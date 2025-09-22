
from django import template
from semester_module.models import Semester,Current_Semester
from review_module.models import Reviews
register=template.Library()


@register.filter
def get_current_semester(request):
    sem=request.session.get('semester')
    sem=Semester.objects.get(id=sem).start_date if sem!=None else Current_Semester.objects.first().semester.start_date
    return sem

@register.filter
def get_review_choices(a):
    return list([x[0] for x in Reviews.review_choices])