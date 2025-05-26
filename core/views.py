from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views.generic import (
    TemplateView, FormView, 
    ListView, DetailView,
    UpdateView, DeleteView,
)
from django.http import JsonResponse
from django.utils import translation
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .forms import GangReportForm, ExtraAreaFormSet
from .models import GangReport

import pytz
import threading

def get_now():
    central = pytz.timezone(settings.TIME_ZONE)
    local_time = timezone.now().astimezone(central)
    return local_time

def localize(t):
    central = pytz.timezone(settings.TIME_ZONE)
    return t.astimezone(central)

def send_report_email(report):
    def _send():
        send_mail(
            subject="New Report Submitted",
            message=f"""
A new gang report was submitted:

Gang Name: {report.gang_name}
Location: {report.main_area}
Start Date: {report.start_date}
End Date: {report.end_date}
Submitted On: {localize(report.created_at).strftime("%Y-%m-%d %H:%M:%S")}

        """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email for _, email in settings.ADMINS],
            fail_silently=True,
        )

    threading.Thread(target=_send).start()


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['reported_gangs'] = GangReport.objects.filter()[:20]
        return context

class GangReportFormView(FormView):
    template_name = 'report.html'
    form_class = GangReportForm
    success_url = reverse_lazy('report_success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['extraarea_formset'] = ExtraAreaFormSet(self.request.POST)
        else:
            context['extraarea_formset'] = ExtraAreaFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['extraarea_formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()

            send_report_email(self.object)

            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class GangReportListView(LoginRequiredMixin, ListView):
    model = GangReport
    template_name = 'reports_list.html'
    context_object_name = 'reports'
    login_url = settings.ADMINISTRATION_URL + 'login'
    redirect_field_name = 'next'

    def get_queryset(self):
        return GangReport.objects.filter(is_validated=True, parent__isnull=True)

class GangReportDetailView(LoginRequiredMixin, DetailView):
    model = GangReport
    template_name = 'report_detail.html'
    context_object_name = 'report'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = settings.ADMINISTRATION_URL + 'login'
    redirect_field_name = 'next'


class GangReportUpdateView(LoginRequiredMixin, UpdateView):
    model = GangReport
    form_class = GangReportForm
    template_name = 'report.html' 
    context_object_name = 'report'
    login_url = settings.ADMINISTRATION_URL + 'login'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['extraarea_formset'] = ExtraAreaFormSet(self.request.POST, instance=self.object)
        else:
            context['extraarea_formset'] = ExtraAreaFormSet(instance=self.object)
        return context

    def get_success_url(self):
        return reverse_lazy('report_detail', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['extraarea_formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)

class GangReportSuccessView(TemplateView):
    template_name = 'report_success.html'


class GangReportDeleteView(LoginRequiredMixin, DeleteView):
    model = GangReport
    template_name = 'report_confirm_delete.html'
    context_object_name = 'report'
    success_url = reverse_lazy('home')
    login_url = settings.ADMINISTRATION_URL + 'login'
    redirect_field_name = 'next'

def change_language(request):
    lang = request.POST.get('language')
    next_url = request.POST.get('next', request.GET.get('next'))

    if lang in dict(settings.LANGUAGES):
        request.session[settings.LANGUAGE_COOKIE_NAME] = lang
        translation.activate(lang)

        response = HttpResponseRedirect(next_url)
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME, lang,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
        )

        return response
    return redirect('home')