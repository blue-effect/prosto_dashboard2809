from django.urls import path, include
from . import views

app_name = 'dash'

urlpatterns = [
    path('', views.tvshows_report, name='tvshows'),
    path('programs/', views.generate_programs_report, name='programs'),
    path('general/', views.general_report, name='general'),
    path('titles/', views.get_titles),
]
