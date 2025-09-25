from django.contrib.auth.decorators import login_required
from django.db.models import Window, F, Case, When, Value, CharField
from django.db.models.functions import RowNumber, Lag
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from .models import News
from semester_module.models import Semester,Current_Semester
# Create your views here.

@method_decorator(login_required,name='dispatch')
class Index_Page(ListView):
    template_name = 'Base_Layout.html'
    context_object_name = 'news'
    model=News
    ordering = '-date'
    paginate_by = 20
    def get(self,request):
        current_id=Current_Semester.objects.all()[0].id
        window=Window(order_by=F('end_date').asc(),expression=Lag('end_date'))
        query=Semester.objects.annotate(prev=window).annotate(previous=Case(When(prev__isnull=False,then=Value(F('prev'),output_field=CharField())))).filter(id__gte=1)
        for ob in query.filter(id=current_id):
            print(ob.start_date,ob.end_date,ob.previous)
        return super().get(request)
