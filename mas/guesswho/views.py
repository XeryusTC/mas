from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
import random

characters = {
    'Ben': ['glasses', 'beard'],
    'Bob': ['glasses', 'bald'],
    'Jake': ['glasses', 'hat'],
    'John': ['hat', 'bald'],
    'Richard': ['hat', 'beard'],
    'Sam': ['bald', 'beardt'],
}

class HomeView(TemplateView):
    template_name = 'home.html'


class PlayView(TemplateView):
    template_name = 'play.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PlayView, self).get_context_data(*args, **kwargs)
        context['chars'] = characters
        return context


def reset_game(request):
    request.session.flush()
    return HttpResponseRedirect(reverse('guesswho:play'))

def pick_char(request, name):
    if name in characters.keys():
        request.session['char'] = name
        request.session['npc_char'] = random.choice(list(characters.keys()))
    else:
        messages.warning(request, 'This is not a valid character')
    return HttpResponseRedirect(reverse('guesswho:play'))
