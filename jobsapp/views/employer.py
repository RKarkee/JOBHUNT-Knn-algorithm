from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView
from random import  randint
from ..decorators import user_is_employer
from ..forms import CreateJobForm
from ..models import Job, Applicant,Profile

from django.shortcuts import render,get_object_or_404

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import joblib






class DashboardView(ListView):
    model = Job
    template_name = 'jobs/employer/dashboard.html'
    context_object_name = 'jobs'

    @method_decorator(login_required(login_url=reverse_lazy('jobs:login')))
    @method_decorator(user_is_employer)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(user_id=self.request.user.id)


class ApplicantPerJobView(ListView): # views for
    model = Applicant
    template_name = 'jobs/employer/applicants.html'
    context_object_name = 'applicants'
    paginate_by = 1

    @method_decorator(login_required(login_url=reverse_lazy('jobs:login')))
    @method_decorator(user_is_employer)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get_queryset(self):
        return Applicant.objects.filter(job_id=self.kwargs['job_id']).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = Job.objects.get(id=self.kwargs['job_id'])
        applicants=Applicant.objects.filter(job_id=self.kwargs['job_id']).order_by('id')
        knn = joblib.load('knnMODEL.pkl')
        data1 = joblib.load("data1.pkl")
        data2 = joblib.load("data3.pkl")
        data3 = joblib.load("data3.pkl")
        data4 = joblib.load("data4.pkl")
        recommendation = {}
        for each in applicants:
            user = (each.user)
            prof = Profile.objects.filter(user=user)
            skill1 = prof[0].skill1
            skill2 = prof[0].skill2
            skill3 = prof[0].skill3
            skill4 = prof[0].skill4
            skill1n, skill2n, skill3n, skill4n = randint(0,500), randint(0,500), randint(0,500), randint(0,500)
            if skill1 in data1:
                skill1n = data1[skill1]
            elif skill1 in data2:
                skill1n = data2[skill2]
            elif skill1 in data3:
                skill1n = data2[skill2]
            elif skill1 in data4:
                skill1n = data2[skill2]
            if skill2 in data1:
                skill2n = data1[skill2]
            elif skill2 in data2:
                skill2n = data2[skill2]
            elif skill2 in data3:
                skill2n = data2[skill2]
            elif skill2 in data4:
                skill2n = data2[skill2]
            if skill3 in data1:
                skill3n = data1[skill3]
            elif skill3 in data2:
                skill3n = data2[skill3]
            elif skill3 in data3:
                skill3n = data2[skill3]
            elif skill3 in data4:
                skill3n = data2[skill3]
            if skill4 in data1:
                skill4n = data1[skill4]
            elif skill4 in data2:
                skill4n = data2[skill4]
            elif skill4 in data3:
                skill4n = data2[skill4]
            elif skill4 in data4:
                skill4n = data2[skill4]
            prediction = knn.predict(([[skill1n, skill2n, skill3n, skill4n]]))
            print(prediction)
            if prediction[0].lower() == each.job.title.lower():
                recommendation[prof[0]] = each

        context['recommendation']=recommendation

        return context


class JobCreateView(CreateView):
    template_name = 'jobs/create.html'
    form_class = CreateJobForm
    extra_context = {
        'title': 'Post New Job'
    }
    success_url = reverse_lazy('jobs:employer-dashboard')

    @method_decorator(login_required(login_url=reverse_lazy('jobs:login')))
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return reverse_lazy('jobs:login')
        if self.request.user.is_authenticated and self.request.user.role != 'employer':
            return reverse_lazy('jobs:login')
        return super().dispatch(self.request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(JobCreateView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ApplicantsListView(ListView):
    model = Applicant
    template_name = 'jobs/employer/all-applicants.html'
    context_object_name = 'applicants'

    def get_queryset(self):
        # jobs = Job.objects.filter(user_id=self.request.user.id)
        return self.model.objects.filter(job__user_id=self.request.user.id)


@login_required(login_url=reverse_lazy('jobs:login'))
def filled(request, job_id=None):
    job = Job.objects.get(user_id=request.user.id, id=job_id)
    job.filled = True
    job.save()
    return HttpResponseRedirect(reverse_lazy('jobs:employer-dashboard'))


def seeker_render_pdf_view(request, *args, **kwargs):
    pk =kwargs.get('pk')
    applicant = get_object_or_404(Applicant,pk=pk)

    template_path = 'jobs/employer/cv2.html'
    context = {'applicant': applicant}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if download:
    #   response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # if display:
    response['Content-Disposition'] = 'filename="cv.pdf"'

    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

#
# def render_pdf_view(request):
#     template_path = 'jobs/employer/cv1.html'
#     context = {'myvar': 'this is your template context'}
#     # Create a Django response object, and specify content_type as pdf
#     response = HttpResponse(content_type='application/pdf')
#     #if download:
#      #   response['Content-Disposition'] = 'attachment; filename="report.pdf"'
#     #if display:
#     response['Content-Disposition'] = 'filename="cv.pdf"'
#
#     # find the template and render it.
#     template = get_template(template_path)
#     html = template.render(context)
#
#     # create a pdf
#     pisa_status = pisa.CreatePDF(
#        html, dest=response)
#     # if error then show some funy view
#     if pisa_status.err:
#         return HttpResponse('We had some errors <pre>' + html + '</pre>')
#     return response
