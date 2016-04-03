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
        context['chars'] = sorted(characters.keys())
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
            context['exclude'] = set()
            for k, v in self.request.session['player_knows'].items():
                if v == YES:
                    context['player_knows'].append(k)
                elif v == NO:
                    context['player_knows'].append('&not;' + k)
                elif v == UNKNOWN:
                    context['player_knows'].append(k + ' &#8897; &not;' + k)

                # Find out which characters to grey out
                for name, traits in characters.items():
                    if k in traits and v == NO:
                        context['exclude'].add(name)
                    elif k not in traits and v == YES:
                        context['exclude'].add(name)
            context['exclude'] = list(context['exclude']) + \
                self.request.session['exclude_extra']
            context['questions'] = reversed(self.request.session['questions'])
        except KeyError:
            context['npc_knows'] = None
            context['player_knows'] = None
            context['exclude'] = None
            context['questions'] = None
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
        request.session['npc_possible'] = list(characters.keys())
        request.session['questions'] = []
        request.session['exclude_extra'] = []
        request.session['finished'] = False
    else:
        messages.warning(request, 'This is not a valid character')
    return HttpResponseRedirect(reverse('guesswho:play'))

def guess(request, name):
    question = 'You: is it ' + name + '?'
    request.session['questions'].append(question)
    if request.session['npc_char'] == name:
        request.session['questions'].append('Computer: Yes')
        request.session['questions'].append("You've won")
        request.session['finished'] = True
    else:
        request.session['questions'].append('Computer: No')
        request.session['exclude_extra'].append(name)
        computer_turn(request)

    request.session.modified = True
    return HttpResponseRedirect(reverse('guesswho:play'))

def get_question_text(subject):
    if subject == 'bald':
        return 'Is he bald?'
    elif subject == 'beard':
        return 'Does he have a beard?'
    elif subject == 'glasses':
        return 'Does he wear glasses?'
    elif subject == 'moustache':
        return 'Does he have a moustache?'

def question(request, subject):
    question = 'You: ' + get_question_text(subject)
    request.session['questions'].append(question)

    if subject in characters[request.session['npc_char']]:
        question = 'Computer: Yes.'
        request.session['player_knows'][subject] = YES
    else:
        question = 'Computer: No.'
        request.session['player_knows'][subject] = NO
    request.session['questions'].append(question)

    computer_turn(request)

    request.session.modified = True
    return HttpResponseRedirect(reverse('guesswho:play'))

def computer_turn(request):
    request.session.modified = True
    # Check whether we know for sure what the player's character is
    print(request.session['npc_possible'], request.session['char'])
    if len(request.session['npc_possible']) == 1 and \
            request.session['npc_possible'][0] == request.session['char']:
        request.session['questions'].append('Computer is it ' + \
            request.session['npc_possible'][0] + '?')
        request.session['questions'].append('You: Yes')
        request.session['questions'].append('The computer has won')
        request.session['finished'] = True
        return
    # Count the number of traits that are present in the possible characters
    traits = {}
    for c in request.session['npc_possible']:
        for t in characters[c]:
            if request.session['npc_knows'][t] != UNKNOWN:
                continue # Skip traits we already know something about
            try:
                traits[t] += 1
            except KeyError:
                traits[t] = 1
    print(traits)
    # Pick the trait with the highest character count
    trait = max(traits)
    # If there is only one character with a trait max, start guessing
    if traits[trait] == 1:
        char = random.choice(request.session['npc_possible'])
        question = 'Computer: Is it ' + char + '?'
        request.session['questions'].append(question)
        if request.session['char'] == char:
            request.session['questions'].append('You: Yes.')
            request.session['questions'].append('The computer has won')
            request.session['finished'] = True
        else:
            request.session['questions'].append('You: No.')
            request.session['npc_possible'].remove(char)
        return
    # Ask the question about the trait (and update the Kripke model)
    question = 'Computer: ' + get_question_text(trait)
    request.session['questions'].append(question)
    remove = set()
    if trait in characters[request.session['char']]:
        answer = 'You: Yes.'
        request.session['npc_knows'][trait] = YES
        for char in request.session['npc_possible']:
            if trait not in characters[char]:
                remove.add(char)
    else:
        answer = 'You: No.'
        request.session['npc_knows'][trait] = NO
        for char in request.session['npc_possible']:
            if trait in characters[char]:
                remove.add(char)
    request.session['questions'].append(answer)
    for c in remove:
        request.session['npc_possible'].remove(c)
