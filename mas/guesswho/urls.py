from django.conf.urls import url
from guesswho import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^play/$', views.PlayView.as_view(), name='play'),
    url(r'^play/reset/$', views.reset_game, name='reset'),
    url(r'^play/char/([a-zA-Z]+)/$', views.pick_char, name='char'),
    url(r'^play/question/([a-zA-Z]+)/$', views.question, name='question'),
]
