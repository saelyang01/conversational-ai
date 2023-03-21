__author__ = 'Jinho D. Choi'

from typing import Dict
from typing import Any
from typing import List
from emora_stdm import DialogueFlow, Macro, Ngrams
import time
import json
import requests
import pickle
import re
import os


class MacroSetBool:
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[str]):
        if len(args) != 2:
            return False

        variable = args[0]
        if variable[0] == '$':
            variable = variable[1:]

        boolean = args[1].lower()
        if boolean not in {'true', 'false'}:
            return False

        vars[variable] = bool(boolean)
        return True


class MacroTime(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[str]):
        current_time = time.strftime("%H:%M")
        return "It's currently {}.".format(current_time)



class MacroGetName(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        vn = 'VISITS'
        r = re.compile(
            r"(?i)(.* call me|call me|.* it\'s|it\'s|.* i\'m|i\'m|.* i am|i am|.* this is|this is|.* it is|it is|this\'s|.* this\'s|my name is|.* my name is)?(?:\s)*([A-z']{2,12})(?:\s([A-z']{2,12}))?")
        m = r.search(ngrams.text())
        if m is None: return False
        intro, firstname, lastname = None, None, None
        if m.group(2):
            firstname = m.group(2)
            lastname = m.group(3)
        if m.group(1):
            intro = m.group(1)

        fn = 'FIRSTNAME'
        # if the first name is not in the dictionary, then add it to the dictionary
        if fn not in vars:
            vars[fn] = firstname
            vars['RETURN'] = 0
        else:  # else if the first name is in the dictionary, then check if the first name is the same as the one in the dictionary
            if vars[fn] == firstname:
                vars['RETURN'] = 1
            else:
                vars[fn] = firstname
                vars['RETURN'] = 0
        return True

class MacroRemember(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if 'RETURN' in vars:
            if vars['RETURN'] == 1:
                return True
            else:
                return False

        return False


class MacroWeather(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        url = 'https://api.weather.gov/gridpoints/FFC/52,88/forecast'
        r = requests.get(url)
        d = json.loads(r.text)
        periods = d['properties']['periods']
        today = periods[0]
        #match certain keywords in the forecast (sunny, cloudy, etc.), and return that weather keyword
        return today['shortForecast'].lower()


class MacroVisits(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        vn = 'VISITS'
        if vn not in vars:
            vars[vn] = 1
            return 'first'
        else:
            count = vars[vn] + 1
            vars[vn] = count
            match count:
                case 2:
                    return 'second'
                case 3:
                    return 'third'
                case default:
                    return '{}th'.format(count)


class MacroWhatElse(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        vn = 'HAVE_TALK'
        if vn in vars and vars[vn]:
            return 'What else do you want to talk about?'
        else:
            vars[vn] = True
            return 'What do you want to talk about?'


def quiz4() -> DialogueFlow:
    transitions = {
        'state': 'start',
        '`Hi. `#TIME`and`#WEATHER`.what can I do for you today?`': {
            'state': 'introduce',
            '[{song,movie,film,music,recommendation}]': {

                '#GATE`Sure. What should I call you?`': {
                    '#GETNAME': {
                        '#IF(#VISITED) `Welcome back, `$FIRSTNAME`,Have you watched ` $MOVIE_CHOSEN `that I recommended last time?` #SET($MOVIE_RETURN=False)': {
                            '[/(?i)(yes|yea|definitely|of course|yep|sure|will watch|i\'ll|try|interesting|ok|okay)/]':{
                                '`Wonderful! What else do you want me to recommend this time?`':{
                                    'state':'recommend',
                                    '[{#LEM(movie),#LEM(film)}]': 'movie',
                                    '[{#LEM(music),#LEM(song)}]': 'music',
                                    'error': {
                                        '`Sorry, I don\'t provide such service`': 'end'
                                    }
                                }
                            },

                            'error': {
                                '`Fine! Do you want other recommendations?`':'recommend'
                            }
                        },
                        '#IF(#VISITED) `Welcome back, `$FIRSTNAME`,Have you get to listened to ` $SONG_CHOSEN `that I recommended last time?` #SET($SONG_RETURN=False)': {
                            '[/(?i)(yes|yea|definitely|of course|yep|sure|will watch|i\'ll|try|interesting|ok|okay)/]':{
                                '`Wonderful! What else do you want me to recommend this time?`':{
                                    'state':'recommend',
                                    '[{#LEM(movie),#LEM(film)}]': 'movie',
                                    '[{#LEM(music),#LEM(song)}]': 'music',
                                    'error': {
                                        '`Sorry, I don\'t provide such service`': 'end'
                                    }
                                }
                            },

                            'error': {
                                '`OK! Do you have any other preferences?`':'recommend'
                            }
                        },
                        '`It\'s nice to meet you,`$FIRSTNAME`.What do you want to know about today?`': {
                            '[{#LEM(movie),#LEM(film)}]': 'movie',
                            '[{#LEM(music),#LEM(song)}]': 'music',
                            'error': {
                                '`Sorry, I don\'t provide such service`': 'end'
                            }
                        }
                    },
                    'error': {
                        'Sorry, I cannot understand you': 'start'
                    }},
                '#GATE`Alright. May I have your name?`': {
                    '#GETNAME': {
                        '#IF(#VISITED) `Welcome back, `$FIRSTNAME`,Have you watched ` $MOVIE_CHOSEN `that I recommended last time?` #SET($MOVIE_RETURN=False)': {
                            '[/(?i)(yes|yea|definitely|of course|yep|sure|will watch|i\'ll|try|interesting|ok|okay)/]':{
                                '`Wonderful! What else do you want me to recommend this time?`':{

                                    '[{#LEM(movie),#LEM(film)}]': 'movie',
                                    '[{#LEM(music),#LEM(song)}]': 'music',
                                    'error': {
                                        '`Sorry, I don\'t provide such service`': 'end'
                                    }
                                }
                            },

                            'error': {
                               '`OK! Are you interested in other recommendations?`':'recommend'
                            }
                        },
                        '#IF(#VISITED) `Welcome back, `$FIRSTNAME`,Have you get to listened to ` $SONG_CHOSEN `that I recommended last time?` #SET($SONG_RETURN=False)': {
                            '[/(?i)(yes|yea|definitely|of course|yep|sure|will watch|i\'ll|try|interesting|ok|okay)/]': {
                                '`Wonderful! What else do you want me to recommend this time?`': {

                                    '[{#LEM(movie),#LEM(film)}]': 'movie',
                                    '[{#LEM(music),#LEM(song)}]': 'music',
                                    'error': {
                                        '`Sorry, I don\'t provide such service`': 'end'
                                    }
                                }
                            },

                            'error': {
                                '`That\'s fine. Any other preferences?`':'recommend'
                            }
                        },
                        '`It\'s nice to meet you,`$FIRSTNAME`.What do you want to know about today?`': {

                            '[{#LEM(movie),#LEM(film)}]': 'movie',
                            '[{#LEM(music),#LEM(song)}]': 'music',
                            'error': {
                                '`Sorry, I don\'t provide such service`': 'end'
                            }
                        }
                    },
                    'error': {
                        'Sorry, I cannot understand you': 'start'
                    }},
                '#GATE`Of course. Could you tell me your name?`': {
                    '#GETNAME': {
                        '#IF(#VISITED) `Welcome back, `$FIRSTNAME`,Have you watched ` $MOVIE_CHOSEN `that I recommended last time?` #SET($MOVIE_RETURN=False)': {
                            '[/(?i)(yes|yea|definitely|of course|yep|sure|will watch|i\'ll|try|interesting|ok|okay)/]':{
                                '`Wonderful! What else do you want me to recommend this time?`':{
                                    '[{#LEM(movie),#LEM(film)}]': 'movie',
                                    '[{#LEM(music),#LEM(song)}]': 'music',
                                    'error': {
                                        '`Sorry, I don\'t provide such service`': 'end'
                                    }
                                }
                            },

                            'error': {
                                '`I get it. Anything interest?`':'recommend'
                            }
                        },
                        '#IF(#VISITED) `Welcome back, `$FIRSTNAME`,Have you get to listened to ` $SONG_CHOSEN `that I recommended last time?` #SET($SONG_RETURN=False)': {
                            '[/(?i)(yes|yea|definitely|of course|yep|sure|will watch|i\'ll|try|interesting|ok|okay)/]': {
                                '`Wonderful! What else do you want me to recommend this time?`': {
                                    '[{#LEM(movie),#LEM(film)}]': 'movie',
                                    '[{#LEM(music),#LEM(song)}]': 'music',
                                    'error': {
                                        '`Sorry, I don\'t provide such service`': 'end'
                                    }
                                }
                            },

                            'error': {
                               '`Come on. What other things do you enjoy?`':'recommend'
                            }
                        },
                        '`It\'s nice to meet you,`$FIRSTNAME`.What do you want to know about today?`': {

                            '[{#LEM(movie),#LEM(film)}]': 'movie',
                            '[{#LEM(music),#LEM(song)}]': 'music',
                            'error': {
                                '`Sorry, I don\'t provide such service`': 'end'
                            }
                        }
                    },
                    'error': {
                        'Sorry, I cannot understand you': 'start'
                    }},
                'error': {
                    'Sorry, I cannot understand you': 'start'
                }
            },
            'error': {'`Sorry, I don\'t provide such service. Are you interested in movie or music?`':'introduce'
                      }
        }
    }

    music_transitions = {
        'state': 'music',
        '`How about "Raining Tacos"? It\'s a really nice song.` #SET($SONG_CHOSEN=Raining Tacos)': {
            '[/(?i)(no|nope|not|nah|already|known|listened|knew|do not|don\'t like|do not like|won\'t|wouldn\'t)/]': 'other_recommend_song',
            '[/(?i)(why not|yes|yea|definitely|of course|yep|sure|will listen|i\'ll|try|interesting|ok|okay)/]': {
                '`Sure! Enjoy your song!`#SET($SONG_RETURN=True)': 'end'
            },
            '[/(?i)(what.*?about|what.*?story|what.*?plot|more information|more info|know more|detail|details)/]': {
                '`It\'s a fun children\'s song by Parry Gripp`': {
                    'state': 'ifListen',
                    '[/(?i)(why not|yes|yea|definitely|of course|yep|sure|will listen|i\'ll|try|interesting|ok|okay)/]': {
                        '`Great! Enjoy your song!`#SET($SONG_RETURN=True)': 'end'
                    },
                    '[/(?i)(no|nope|not|nah|already seen|have seen|not interesting|lame|won\'t|don\'t|wouldn\'t)/]': 'other_recommend_song',
                    '#UNX': {
                        '`So do you want to try listening to it?`': 'ifListen'
                    }

                }
            },
            'error': {
                '`I\'m sorry. I don\'t understand`': 'start'
            }
        }
    }

    movie_transitions = {
        'state': 'movie',
        '`How about "Spider-Man: Homecoming"? It\'s my personal favorite.` #SET($MOVIE_CHOSEN=Spider-Man: Homecoming)': {
            '[/(?i)(no|nope|not|nah|already seen|have seen|seen|do not|don\'t like|do not like)/]': 'other_recommend_movie',
            '[/(?i)(why not|yes|yea|definitely|of course|yep|sure|will watch|i\'ll|try|interesting|ok|okay)/]': {
                '`Sure! Enjoy your movie!`#SET($MOVIE_RETURN=True)': 'end'
            },
            '[/(?i)(what.*?about|what.*?story|what.*?plot|more information|more info|know more|detail|details)/]': {
                '`It\'s a superhero movie about a teenager who is trying to balance his life as a high school student and as a superhero.`': {
                    'state': 'ifWatch',
                    '[/(?i)(why not|yes|yea|definitely|of course|yep|sure|will watch|i\'ll|try|interesting|ok|okay)/]': {
                        '`Perfect! Enjoy your movie!`#SET($MOVIE_RETURN=True)':'end'
                    },
                    '[/(?i)(no|nope|not|nah|already seen|have seen|not interesting|lame|won\'t|don\'t)/]': 'other_recommend_movie',
                    '#UNX': {
                        '`Thanks for sharing.`': 'start'
                    }

                }
            },
            'error': {
                '`I am sorry, I don\'t understand.`': 'start'
            }
        }
    }
    other_recommendation_movie_transitions = {
        'state': 'other_recommend_movie',
        '#GATE `Well. How about "Titanic"? It\'s fantastic.` #SET($MOVIE_CHOSEN=Titanic)': {
            '[/(?i)(no|nope|not|nah|already|known|listened|knew|do not|don\'t like|do not like|won\'t|wouldn\'t)/]': 'other_recommend_movie',
            '[/(?i)(why not|yes|yea|definitely|of course|yep|sure|will listen|i\'ll|try|interesting|ok|okay)/]': {
                '`Sure! Enjoy your movie!`#SET($MOVIE_RETURN=True)': 'end'
            },
            '[/(?i)(what.*?about|what.*?story|what.*?background|more information|more info|know more|detail|details)/]': {
                '`It\'s a famous romance movie narrating the story of a young couple `': 'ifWatch'
            },
            'error': {
                '`I am sorry, I don\'t understand.`': 'movie'
            }
        },
        '#GATE `Well. How about "Annabelle"? It\'s amazing.` #SET($MOVIE_CHOSEN=Annabelle)': {
            '[/(?i)(no|nope|not|nah|already|known|listened|knew|do not|don\'t like|do not like|won\'t|wouldn\'t)/]': 'other_recommend_movie',
            '[/(?i)(why not|yes|yea|definitely|of course|yep|sure|will listen|i\'ll|try|interesting|ok|okay)/]': {
                '`Sure! Enjoy your movie!`#SET($MOVIE_RETURN=True)': 'end'
            },
            '[/(?i)(what.*?about|what.*?story|what.*?background|more information|more info|know more|detail|details)/]': {
                '`It\'s a famous horror movie talking about the supernatural evil occurrence in the form of a doll `': 'ifWatch'
            },
            'error': {
                '`I am sorry, I don\'t understand.`': 'movie'
            }
        },
        '#GATE `Well. How about "Creed"? It\'s amazing.` #SET($MOVIE_CHOSEN=Creed)': {
            '[/(?i)(no|nope|not|nah|already|known|listened|knew|do not|don\'t like|do not like|won\'t|wouldn\'t)/]': 'other_recommend_movie',
            '[/(?i)(why not|yes|yea|definitely|of course|yep|sure|will listen|i\'ll|try|interesting|ok|okay)/]': {
                '`Sure! Enjoy your movie!`#SET($MOVIE_RETURN=True)': 'end'
            },
            '[/(?i)(what.*?about|what.*?story|what.*?background|more information|more info|know more|detail|details)/]': {
                '`It\'s a famous action movie narrating an inspirational story of the world boxing champion  `': 'ifWatch'
            },
            'error': {
                '`I am sorry, I don\'t understand.`': 'movie'
            }
        },
        '`I don\'t know what other to recommend. Maybe I can give you some song recommendations instead?` #SET($MOVIE_CHOSEN=anything)': {
            'score': 0.8,
            '[/(?i)(why not|sure|will listen|i\'ll|try|yes|yea|definitely|of course|yep|ok|okay)/]': 'music',
            '#UNX': {
                '`I don\'t know what to say.Anyway, thanks for sharing!`': 'end'
            }
        }

    }
    other_recommendation_music_transitions = {
        'state': 'other_recommend_song',
        '#GATE `Well. How about "Love Story"?.` #SET($SONG_CHOSEN=Love Story)': {
            '[/(?i)(no|nope|not|nah|already|known|listened|knew|do not|don\'t like|do not like|won\'t|wouldn\'t)/]': 'other_recommend_song',
            '[/(?i)(why not|yes|yea|definitely|of course|yep|sure|will listen|i\'ll|try|interesting|ok|okay)/]': {
                '`Great! Enjoy your song!`#SET($SONG_RETURN=True)': 'end'
            },
            '[/(?i)(what.*?about|what.*?story|what.*?background|more information|more info|know more|detail|details)/]': {
                '`It\'s a famous lyric song by Taylor Swifts that tells a classic story of young love overcoming obstacles `': 'ifListen'
            },
            'error': {
                '`I am sorry, I don\'t understand. `': 'music'
            }
        },
        '#GATE `Well. How about "21 Guns"?.` #SET($SONG_CHOSEN=21 Guns)': {
            '[/(?i)(no|nope|not|nah|already|known|listened|knew|do not|don\'t like|do not like|won\'t|wouldn\'t)/]': 'other_recommend_song',
            '[/(?i)(why not|yes|yea|definitely|of course|yep|sure|will listen|i\'ll|try|interesting|ok|okay)/]': {
                '`Great! Enjoy your song!`#SET($SONG_RETURN=True)': 'end'
            },
            '[/(?i)(what.*?about|what.*?story|what.*?background|more information|more info|know more|detail|details)/]': {
                '`It\'s a famous rock song by Green Day that express a longing for change and a desire to escape from the difficulties of life. `': 'ifListen'
            },
            'error': {
                '`I am sorry, I don\'t understand. `': 'music'
            }
        },
        '#GATE `Well. How about "The Next Episode"?.` #SET($SONG_CHOSEN=The Next Episode)': {
            '[/(?i)(no|nope|not|nah|already|known|listened|knew|do not|don\'t like|do not like|won\'t|wouldn\'t)/]': 'other_recommend_song',
            '[/(?i)(why not|yes|yea|definitely|of course|yep|sure|will listen|i\'ll|try|interesting|ok|okay)/]': {
                '`Great! Enjoy your song!`#SET($SONG_RETURN=True)': 'end'
            },
            '[/(?i)(what.*?about|what.*?story|what.*?background|more information|more info|know more|detail|details)/]': {
                '`It\'s a popular rap song by Eminem that is an anecdote describing his transition from living in a trailer park to becoming a rap superstar. `': 'ifListen'
            },
            'error': {
                '`I am sorry, I don\'t understand. `': 'music'
            }
        },
        '`I do not have more songs to recommend. Maybe I can give you some movie recommendations instead?` #SET($SONG_CHOSEN=anything)': {
            'score': 0.8,
            '[/(?i)(why not|sure|will listen|i\'ll|try|yes|yea|definitely|of course|yep|ok|okay)/]': 'movie',
            '#UNX': {
                '`I don\'t know what to say.Anyway, thanks for sharing!`': 'end'
            }
        }
    }

    macros = {
        'SETBOOL': MacroSetBool(),
        'TIME': MacroTime(),
        'WEATHER': MacroWeather(),
        'VISITS': MacroVisits(),
        'GETNAME': MacroGetName(),
        'WHATELSE': MacroWhatElse(),
        'VISITED': MacroRemember()
    }

    df = DialogueFlow('start', end_state='end')
    df.load_transitions(transitions)
    df.load_transitions(music_transitions)
    df.load_transitions(movie_transitions)
    df.load_transitions(other_recommendation_movie_transitions)
    df.load_transitions(other_recommendation_music_transitions)
    df.add_macros(macros)
    return df

def loadThenSave(df: DialogueFlow, varfile: str):
    d = pickle.load(open(varfile, 'rb'))
    df.vars().update(d)
    df.run()
    d = {k: v for k, v in df.vars().items() if not k.startswith('_')}
    pickle.dump(d, open(varfile, 'wb'))


def save(df: DialogueFlow, varfile: str):
    df.run()
    d = {k: v for k, v in df.vars().items() if not k.startswith('_')}
    pickle.dump(d, open(varfile, 'wb'))


def load(df: DialogueFlow, varfile: str):
    d = pickle.load(open(varfile, 'rb'))
    df.vars().update(d)
    df.run()
    save(df, varfile)


if __name__ == '__main__':
    # if the pkl file does not exist, call save(), otherwise call loadThenSave()
    if (os.path.exists('/Users/yangchenxiang/PycharmProjects/conversational-ai/resources/quiz4.pkl')):
        loadThenSave(quiz4(), '/Users/yangchenxiang/PycharmProjects/conversational-ai/resources/quiz4.pkl')
    else:
        save(quiz4(), '/Users/yangchenxiang/PycharmProjects/conversational-ai/resources/quiz4.pkl')
