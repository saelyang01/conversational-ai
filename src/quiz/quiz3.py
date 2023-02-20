from emora_stdm import DialogueFlow
from emora_stdm import Macro, Ngrams
from typing import Dict, Any, List
import re


class MacroGetName(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        r = re.compile(r"(my name is|call me|i go by)?(\s*)([a-z]+)?(?:\s([a-z']+))?")
        m = r.search(ngrams.text())
        if m is None:
            return False
        firstname, lastname = None, None
        if m.group(1):
            # print("1", m.group(1))
            if m.group(3):
                firstname = m.group(3)
                lastname = m.group(4)
            else:
                firstname = m.group()
                lastname = m.group(3)
        else:
            firstname = m.group(3)
            # print("3", firstname)
            lastname = m.group(4)
            # print("4", lastname)

        vars['FIRSTNAME'] = firstname
        vars['LASTNAME'] = lastname

        return True


transitions = {
        'state': 'start',
        '`Hello. What should I call you?`': {
            '#GET_NAME': {
                '`It\'s nice to meet you,` $FIRSTNAME `.What was the latest movie you watched?`': {
                    '[#ONT(marvel)]': {
                        '`I love Marvels! Who is your favorite avenger?`': {
                            '[$FAVORITE_AVENGER=#ONT(avengers)]': {
                                '`I\'m addicted to `$FAVORITE_AVENGER` too. So I guess you are a big fan of Sci-Fi Movies?`': {
                                    '[{yes,correct,right,of course}]': {
                                        '`Excellent,what\'s the reason you like them so much?`': {
                                            'error': {
                                                '`I got the same feelings too. Thanks for sharing!`': 'end'}
                                        }
                                    },
                                    '[{no, incorrect,not right, not exactly}]': {
                                         '`Oh fine, I guess you must have other preferences!`': {
                                            'error': {
                                                '`Anyway, thank you so much for sharing!`': 'end'
                                            }
                                         }
                                    }
                                },
                                'error': {
                                    '`Sorry, I didn\'t understand you.`': 'end'
                                }
                            }
                        },
                        'error': {
                            '`Sorry, I didn\'t understand you.`': 'end'
                        }
                    },
                    '[#ONT(disney)]': {
                        '`I love Disney! Who is your favorite princess？`': {
                            '[$FAVORITE_PRINCESS=#ONT(princess)]': {
                                '`she is truly the best princess I\'ve never seen.So do you love cartoon movies?`': {
                                    '[{yes,correct,right,of course}]': {
                                        '`Great! same for me. Can you tell me why the cartoons are so attractive?`': {
                                            'error': {
                                                '`Totally agree. Thanks for sharing!`': 'end'
                                            }
                                        }
                                    },
                                    '[{no,incorrect,not right,not exactly}]': {
                                        '`Oh fine, I guess you must have other preferences!`': {
                                            'error': {
                                                '`Anyway, thank you so much for sharing!`': 'end'
                                            }
                                        }
                                    },
                                    'error': {
                                        '`Sorry, I didn\'t understand you.`': 'end'
                                    }
                                }
                            },
                            'error': {
                                '`Sorry, I didn\'t understand you.`': 'end'
                            }
                        },
                        'error': {
                            '`Sorry, I didn\'t understand you.`': 'end'
                        }
                    },
                    'error': {
                        '`Sorry, I didn\'t understand you.`': 'end'
                    }
                },
                'error': {
                    '`Sorry, I didn\'t understand you.`': 'end'
                }
            },
            'error': {
                '`Sorry, I didn\'t understand you.`': 'end'
            }
        }
}


macros = {
    'GET_NAME': MacroGetName()
}

df = DialogueFlow('start', end_state='end')
df.load_transitions(transitions)
df.knowledge_base().load_json_file('resources/ontology_quiz3.json')
df.add_macros(macros)

if __name__ == '__main__':
    df.run()