from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from semester_module.models import Current_Semester, Semester
from user_module.models import Student_Profile,Teacher_Profile,Employee_Profile,General_Profile
from permits_module.models import Permit
profiles={'student':Student_Profile,'teacher':Teacher_Profile,'employee':Employee_Profile}
def restrict_view_access(profile_types,roles='all'):
    def wrapper(func):
        def to_do(*args,**kwargs):
            if any((pr for pr in profile_types if not pr in profiles)):
                return HttpResponse('نقش وارد شده معتبر نمی باشد!')

            user=args[0].user
            cond=Q(user_id=user.id,is_approved=True)
            if roles!='all':
                cond&=Q(role__in=roles)
            for prof in profile_types:
                if profiles[prof].objects.filter(cond).exists():

                     return func(*args,**kwargs)
            return HttpResponse(
                f'کاربر گرامی،شما مجاز به انجام چنین عملیاتی نمی باشید،برای انجام این عملیات شما باید یکی از نقش های '
                f'{roles}'
                f'را داشته باشید')



        return to_do
    return wrapper

def check_semester_status(status_permits_pair:dict,response_type):
    def wrapper(func):
        def to_do(*args,**kwargs):
            request=args[0] or kwargs['request']
            sem=(Semester.objects.get(id=request.session.get('semester')) or Current_Semester.objects.first().semester)
            for key,value in status_permits_pair.items():
                if sem.semester_status==key and (Permit.objects.filter(creator=request.user,semester=sem,permit_type=value) if value!='__all__' else True):
                    return func(*args, **kwargs)
            response = render(args[0], 'Dynamic_Message.html',
                              context={'message': 'شما مجاز به انجام این عملیات در نیمسال فعلی نمی باشید!'}
                              , status=401) if response_type == 'html' else JsonResponse(
                data={'message': 'شما مجاز به انجام این عملیات در نیمسال فعلی نمی باشید!'}, status=401)
            return response
        return to_do
    return wrapper


