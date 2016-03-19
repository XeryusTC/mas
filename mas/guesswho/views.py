from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'home.html'


class PlayView(TemplateView):
    template_name = 'play.html'


def reset_game(request):
    request.session.flush()
    return HttpResponseRedirect(reverse('guesswho:play'))
