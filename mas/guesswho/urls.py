from django.conf.urls import url
from guesswho import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
]
