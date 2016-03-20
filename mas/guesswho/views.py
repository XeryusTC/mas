from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
import random

characters = {
    'David': ['beard'],
    'Frans': [],
    'Max': ['moustache'],
    'Paul': ['glasses'],
    'Richard': ['bald', 'beard', 'moustache'],
    'Sam': ['bald', 'glasses'],
}

# States of knowledge
NO     = 1
YES    = 2
UNKNOWN = 3

class HomeView(TemplateView):
    template_name = 'home.html'


class PlayView(TemplateView):
    template_name = 'play.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PlayView, self).get_context_data(*args, **kwargs)
        context['chars'] = characters
        try:
            context['npc_knows'] = []
            for k, v in self.request.session['npc_knows'].items():
                if v == YES:
                    context['npc_knows'].append(k)
                elif v == NO:
                    context['npc_knows'].append('&not;' + k)
                elif v == UNKNOWN:
                    context['npc_knows'].append(k + ' &#8897; &not;' +  k)

            context['player_knows'] = []
            for k, v in self.request.session['player_knows'].items():
                if v == YES:
                    context['player_knows'].append(k)
                elif v == NO:
                    context['player_knows'].append('&not;' + k)
                elif v == UNKNOWN:
                    context['player_knows'].append(k + ' &#8897; &not;' + k)
        except KeyError:
            context['npc_knows'] = None
            context['player_knows'] = None
        return context


def reset_game(request):
    request.session.flush()
    return HttpResponseRedirect(reverse('guesswho:play'))

def pick_char(request, name):
    if name in characters.keys():
        request.session['char'] = name
        request.session['npc_char'] = random.choice(list(characters.keys()))
        request.session['npc_knows'] = {
            'bald': UNKNOWN,
            'beard': UNKNOWN,
            'glasses': UNKNOWN,
            'moustache': UNKNOWN,
        }
        request.session['player_knows'] = {
            'bald': UNKNOWN,
            'beard': UNKNOWN,
            'glasses': UNKNOWN,
            'moustache': UNKNOWN,
        }
        request.session['questions'] = []
    else:
        messages.warning(request, 'This is not a valid character')
    return HttpResponseRedirect(reverse('guesswho:play'))

def question(request, subject):
    if subject == 'bald':
        question = 'Is he bald?'
    elif subject == 'beard':
        question = 'Does he have a beard?'
    elif subject == 'glasses':
        question = 'Does he wear glasses?'
    elif subject == 'moustache':
        question = 'Does he have a moustache?'

    if subject in characters[request.session['npc_char']]:
        question += ' Yes.'
        request.session['player_knows'][subject] = YES
    else:
        question += ' No.'
        request.session['player_knows'][subject] = NO
    request.session['questions'].append(question)
    request.session.modified = True

    return HttpResponseRedirect(reverse('guesswho:play'))
