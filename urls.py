from django.urls import path

from . import views


app_name = 'project'
'''
urlpatterns = [
    path('', views.IndexView.as_view(), name='index')
    #path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    #path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    #path('<int:question_id>/vote/', views.vote, name='vote'),
]
'''

urlpatterns = [
	path('', views.homepg, name='homepg'),
	path('results/<zip_code>/', views.results, name='results'),
	path('about/', views.about, name='about'),
	path('team/', views.team, name='team'),
	path('US-map/', views.us_map, name='us_map'),
]