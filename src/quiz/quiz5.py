from emora_stdm import DialogueFlow, Ngrams, Macro

from typing import Dict, Any, List
import openai


PATH_API_KEY = 'resources/openai_api.txt'
openai.api_key_path = PATH_API_KEY

class MacroCheck(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Based on the input statement,  ' \
                  'return \'HAIRCUT\' if the user wants to cut their hair, return \'HAIRPERM\' if ther user wants to schedule a perm, ' \
                  'return \'HAIRCOLOR\' if the user wants to color their hair, return \'NOSERVICE\' if the user is scheduling for a hair service that is not ' \
                  'one of haircut, perm, and haircoloring, return \'NO\' if the user talks about stuff unrelated to hair. ' \
                  'The user\'s statement(only return the uppercase letter codes):'
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(
            model= model,
            messages=[{'role': 'user', 'content': content}]
        )
        output = response['choices'][0]['message']['content'].strip()
        vars['HAIRCUT'] = False
        vars['HAIRPERM'] = False
        vars['HAIRCOLOR'] = False
        vars['NO'] = False
        vars['NOSERVICE'] = False

        if output == 'HAIRCUT':
            vars['HAIRCUT'] = True
        elif output == 'HAIRPERM':
            vars['HAIRPERM'] = True
        elif output == 'HAIRCOLOR':
            vars['HAIRCOLOR'] = True
        elif output == 'NO':
            vars['NO'] = True
        elif output == 'UN':
            vars['NOUNDERSTAND'] = True
        return True

class MacroHaircut(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = ' Based on the input statement, return \'True\'if the if the user is making appointment on Monday 10am, 1pm, 2om' \
                  'otherwise return \'False\'. return only True or false(only return the uppercase letter codes):'
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        output = response['choices'][0]['message']['content'].strip()
        if output == 'True':
            vars['POSITIVE'] = True
            vars['NEGATIVE'] = False

        else:
            vars['POSITIVE'] = False
            vars['NEGATIVE'] = True

        return True

class MacroHaircolor(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Based on the input statement, return \'True\' if the user is making appointment   ' \
                  'on Wednesday 10 AM, 11 AM and 1 PM and Thursday 10 AM and 11 AM. Otherwise return \'False\'. ' \
                  'return only True or false(only return the uppercase letter codes):'
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        output = response['choices'][0]['message']['content'].strip()
        if output == 'True':
            vars['POSITIVE'] = True
            vars['NEGATIVE'] = False

        else:
            vars['POSITIVE'] = False
            vars['NEGATIVE'] = True

        return True


class MacroHairperm(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = ' Based on the input statement, return \'True\' if the user is making appointment on Friday 10 AM, 11AM, ' \
                  '1 PM, 2 PM and Saturday 10 AM, and 2 PM. Otherwise return \'False\''\
                  'return only True or false(only return the uppercase letter codes):'

        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        output = response['choices'][0]['message']['content'].strip()
        if output == 'True':
            vars['POSITIVE'] = True
            vars['NEGATIVE'] = False

        else:
            vars['POSITIVE'] = False
            vars['NEGATIVE'] = True

        return True






transitions = {
        'state': 'start',
        '`Hi, what can I do for you?`': {
            '#CHECK': {
                '#IF($HAIRCUT)`Sure. What date and time are you looking for a cut? `': {
                    '#CUT': {
                        '#IF($POSITIVE)`Your appointment for the haircut is set. See you!`': 'end',
                        '#IF($NEGATIVE)`Sorry, that slot is not available for a haircut.`': 'end',
                        'error':{
                          '`Sorry, I don\'t undersntand you`':'end'
                        }
                        }
                    },
                '#IF($HAIRCOLOR)`Sure. What date and time are you looking for a color?`':{
                    '#COLOR':{
                        '#IF($POSITIVE)`Your appointment for the haircoloring is set. See you!`':'end',
                        '#IF($NEGATIVE)`Sorry, that slot is not available for a haircoloring.`':'end',
                        'error':{
                          '`Sorry, I don\'t understand you`':'end'

                      }
                      }
                },
                '#IF($HAIRPERM)`Sure. What date and time are you looking for a perm?`':{
                    '#PERM':{
                        '#IF($POSITIVE)`Your appointment for the hairperming is set. See you!`':'end',
                        '#IF($NEGATIVE)`Sorry, that slot is not available for a hairperming.`':'end',
                        'error':{
                            '`Sorry, I don\'t understand you`':'end'
                        }

                    }
                },
                'error':{
                    '`Sorry, we do not provide such service`':'end'
                }
                }



        },
        'error':{
            '`I don\'t understand you`':'end'
        }
    }

macros = {
        'CHECK': MacroCheck(),
        'CUT': MacroHaircut(),
        'COLOR': MacroHaircolor(),
        'PERM': MacroHairperm()

    }

df = DialogueFlow('start', end_state='end')
df.load_transitions(transitions)
df.add_macros(macros)
if __name__ == '__main__':
    df.run()











