from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('report/', views.GangReportFormView.as_view(), name='report'),
    path('reports/', views.GangReportListView.as_view(), name='reports_list'),
    path('reports/<slug:slug>/', views.GangReportDetailView.as_view(), name='report_detail'),
    path('report/success/', views.GangReportSuccessView.as_view(), name='report_success'),

    path('report/<slug:slug>/edit/', views.GangReportUpdateView.as_view(), name='report_edit'),
    path('report/<slug:slug>/delete/', views.GangReportDeleteView.as_view(), name='report_delete'),
]
