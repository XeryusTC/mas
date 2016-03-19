from django.conf.urls import url
from guesswho import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^play/$', views.PlayView.as_view(), name='play'),
    url(r'^play/reset/$', views.reset_game, name='reset'),
]
