from emora_stdm import DialogueFlow, Macro, Ngrams
from typing import List, Tuple, Dict, Any
import re
import json
import requests
import time
import pickle
import os
import random
from enum import Enum
import openai
from src import utils
from src.utils import MacroGPTJSON, MacroNLG

PATH_USER_INFO = 'resources/userinfo.json'

class MacroAnyInput(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        return True

class MacroAttitude(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'I asked the user \'What do you think? \' based on the following response from user, if the user wants to know more, return \'elaborate\', else, base on their attitude return from \'agree\' or \'disagree\. If the user don\'t agree, just return \'disagree\ : '
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        vars['ATTITUDE'] = 'error'
        output = response['choices'][0]['message']['content'].strip()
        #print(output)
        if 'disagree' in output.lower():
            vars['ATTITUDE'] = 'disagree'
        elif 'agree' in output.lower():
            vars['ATTITUDE'] = 'agree'
        elif 'elaborate' in output.lower():
            vars['ATTITUDE'] = 'elaborate'
        else:
            return False
        return True


class MacroTheme(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'I asked the user \'What do you think is the theme of the movie\' based on the following response from user, ' \
                  'return one from the following themes \'miscommunication\', \'language barrier\', \'culture barrier\', \'white privilege\', \'human connection\' : '+ngrams.raw_text()+ 'please only return one term from the theme list above.'
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        vars['THEME'] = 'error'
        output = response['choices'][0]['message']['content'].strip().lower().strip('.')
        print(output)
        if 'miscommunication' in output.lower():
            vars['THEME'] = 'miscommunication'
        elif 'language' in output.lower():
            vars['THEME'] = 'language barrier'
        elif 'culture' in output.lower():
            vars['THEME'] = 'culture barrier'
        elif 'white previlage' in output.lower():
            vars['THEME'] = 'white privilege'
        elif 'human connection' in output.lower():
            vars['THEME'] = 'human connection'
        else:
            return False
        return True


class MacroMovieInfo(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        url = "https://www.omdbapi.com/?t=babel&apikey=fb8d2e5e"
        r = requests.get(url)
        d = json.loads(r.text)
        vars['Year'] = d['Year']
        vars['Genre'] = d['Genre']
        vars['Director'] = d['Director']
        vars['Writer'] = d['Writer']
        vars['Actors'] = d['Actors']
        vars['Plot'] = d['Plot']
        vars['Language'] = d['Language']
        vars['Country'] = d['Country']
        return True


class MacroGetName(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]) -> bool:
        r = re.compile(r"(\b\w+\b)\s*$")
        m = r.search(ngrams.text())
        vars['NAME'] = 0
        if m is None:
            return False
        name = m.group()
        vars['NAME'] = name
        return True


class MacroTimeOfDay(Macro):
    def run(self, ngrams: Ngrams, vars, args):
        current_hour = int(time.strftime("%H"))
        if current_hour > 0 and current_hour < 12:
            return "Good morning!"
        elif current_hour >= 12 and current_hour < 18:
            return "Good afternoon!"
        else:
            return "Good evening!"


transition_greeting = {
    'state': 'start',
    '#GREETING `What\'s your name?`': {
        '#GET_NAME': 'info',
        'error': {
            '`I don\'t understand you.`#SET($NAME=.)': 'info'
        }
    }
}

transition_basic_info = {
    'state': 'info',
    '`It\'s nice to meet you,` $NAME`. What would you like to know about the movie Babel?` #GET_INFO': {
        'state': 'more',
        '[{#LEM(actor), #LEM(actress), performer}]': {
            '`The main actors in Babel are `$Actors`. What else do you want to know?`': 'more'
        },
        '[/(?i)(what.?about|what.?story|what.*?plot|more information|more info|know more|detail|details|tell me about|explain|describe|give me the scoop)/]': {
            '$Plot`. What else do you want to know?`': 'more'},
        '[{#LEM(director)}]': {
            '`The director of Babel is `$Director`. What else do you want to know?`': 'more'
        },
        '[{release_year, year}]': {
            '`Babel was released in `$Year`. What else do you want to know?`': 'more'
        },
        '[{genre}]': {
            '`The genre of Babel is `$Genre`. What else do you want to know?`': 'more'
        },
        '[{writer}]': {
            '`The writer of Babel is `$Writer`. What else do you want to know?`': 'more'
        },
        '[{language}]': {
            '`The language of Babel is `$Language`. What else do you want to know?`': 'more'
        },
        '[{country}]': {
            '`The country of origin for Babel is `$Country`. What else do you want to know?`': 'more'
        },
        '#ANYINPUT': 'story'
    }
}

transition_story = {
    'state': 'story',
    '`What\'s your favorite story line in the movie?`': {
        '[{#LEM(japan),#LEM(japanese), father daughter}]': {
            '`Interesting choice, I personally find the Japan storyline fascinating as well. Because Chieko cannot speak, `'
            '`\nit most intuitively embodies the communication barrier. Chieko\'s frustration with her inability to communicate `'
            '`\nis palpable throughout the film, and her desire to connect with others is a driving force in her story. What do you think?`#SET($THEME =miscommunication)': {
                '#GETATTI': {
                    '#IF($ATTITUDE=agree)`I\'m glad we share the same opinion. I think Chieko\'s self-discovery journey aligns with the movie\'s theme'
                    'of communication and human connection. Do you think it is an important theme of the movie?`': {
                        '#ANYINPUT': 'theme'
                    },
                    '#IF($ATTITUDE=disagree)`Interesting, what do you think?`': {
                        '#ANYINPUT': {
                            '`Yes I agree with you. It\'s a bit confusing. But I personally really like it. I think Chieko\'s self-discovery journey aligns with the movie\'s theme'
                            'of communication and human connection. Do you think it is an important theme of the movie?`': {
                                '#ANYINPUT': 'theme'
                            },
                        }
                    },
                    '#IF($ATTITUDE=elaborate)`Sure. Chieko\'s journey of self-discovery and her exploration of communication and human connection is controversial. `'
                    '`\nThe scene in which Chieko sees her friend kissing her crush and the scene where she tries to seduce the officer highlights'
                    '\nher struggle between her desire for connection and her fear of vulnerability. Do you think it is an important theme of the movie?`': {
                        '#ANYINPUT': 'theme'
                    }
                }
            }
        },
        '[{#LEM(moroccan), #LEM(morocco)}]': {
            '`I see, the Moroccan storyline is definitely an intense one. '
            'It highlights the cultural differences and misunderstandings between the Moroccan family and the American couple. '
            '\nThe language barrier, as well as the tense political climate, make it difficult for the two families to connect. '
            '\nDid you find this storyline engaging?`': {
                '#GETATTI': {
                    '#($ATTITUDE=elaborate)`The Moroccan storyline is an exploration of the cultural, linguistic, '
                    '\nand political barriers that can exist between different communities. `'
                    '`\nIt highlights the challenges of communication and understanding in a complex, multicultural world. Do you think it is an important theme of the movie?`': {
                        '#ANYINPUT': 'theme'
                    },

                    '#IF($ATTITUDE=agree)`I completely agree. The Moroccan storyline is an important part of the movie\'s exploration of communication and human connection. `'
                    '`\nIt shows how difficult it can be to bridge the gap between different cultures and communities. Do you think it is an important theme of the movie?`': {
                        '#ANYINPUT': 'theme'

                    },
                    '#IF($ATTITUDE=disagree)`Interesting, what do you think?`': {
                        '#ANYINPUT':
                            {
                                '`I think the Moroccan storyline is an important part of the movie, as it highlights the challenges of communication and understanding in a complex, multicultural world. `'
                                '`\nIt shows how difficult it can be to bridge the gap between different cultures and communities. Do you think it is an important theme of the movie?`': {
                                    '#ANYINPUT': 'theme'
                                }
                            }
                    },
                    'error': {'`Sorry, I don\'t understand you`': 'theme'}
                }
            }
        },
        '[{couple, #LEM(america), #LEM(american)}]': {
            '`Ah yes, the American couple\'s storyline is a poignant one. It highlights the power dynamics between them and their Moroccan hosts. '
            '\nThe couple is forced to navigate unfamiliar cultural norms and expectations, leading to tension and misunderstandings. '
            '\nWhat did you think about their story?`': {
                '#GETATTI': {
                    '#IF($ATTITUDE=elaborate)`The American storyline focuses on the power dynamics and cultural misunderstandings between the American couple and their Moroccan hosts. `'
                    '`\nTheir story highlights the challenges of communicating across cultures, and the difficulties that can arise when expectations clash. '
                    '\nDo you think it is an important theme of the movie?`': {
                        '#ANYINPUT': 'theme'
                    },
                    '#IF($ATTITUDE=agree)`I\'m glad we share the same opinion. The American storyline is an important part of the movie\'s exploration of communication and human connection. `'
                    '`\nIt shows how difficult it can be to navigate unfamiliar cultural norms and expectations, and how misunderstandings can lead to tension and conflict. '
                    '\nDo you think it is an important theme of the movie?`': {
                        '#ANYINPUT': 'theme'
                    },
                    '#IF($ATTITUDE=disagree)`Interesting, what do you think?`': {
                        '#ANYINPUT': {
                            '`I think the American storyline is an important part of the movie, as it highlights the challenges of communicating across cultures and navigating unfamiliar expectations. `'
                            '`\nIt shows how misunderstandings and tensions can arise when expectations clash. Do you think it is an important theme of the movie?`': {
                                '#ANYINPUT': 'theme'
                            }
                        }
                    },
                    'error': {'`Sorry, I don\'t understand you`': 'theme'}
                }
            }
        },
        '[{#LEM(mexican), #LEM(nanny), #LEM(wedding)}]': {
            '`The Mexican storyline is another powerful one. It follows the nanny, Amelia, as she tries to get back to her son\'s wedding in Mexico. '
            '\nHer relationship with the American children she cares for is complicated, and the events that unfold during their trip across the border are heart-wrenching. '
            '\nDid you find this storyline moving?`': {
                '#GETATTI': {
                    '`#IF($ATTITUDE=elaborate)`The Mexican storyline follows the nanny, Amelia, as she tries to get back to her son\'s wedding in Mexico. '
                    '\nHer relationship with the American children she cares for is complicated, and the events that unfold during their trip across the border are heart-wrenching. `'
                    '`\nThe movie examines issues of immigration, class, and the complexities of the nanny-family dynamic. Do you think it is an important theme of the movie?`': {
                        '#ANYINPUT': 'theme'

                    },
                    '#IF($ATTITUDE=agree)`I agree, the Mexican storyline is a powerful one that touches on many important themes, including immigration and the complexities of the nanny-family dynamic. `'
                    '`\nThe events that unfold during Amelia\'s journey are heart-wrenching, and they provide a thought-provoking look into the lives of those who must navigate the border between the United States and Mexico. '
                    '\nDo you think it is an important theme of the movie?`': {
                        '#ANYINPUT': 'theme'

                    },
                    '#IF($ATTITUDE=disagree)`Interesting, what do you think?`': {
                        '#ANYINPUT': {
                            '`I personally found the Mexican storyline to be a powerful and thought-provoking exploration of issues related to immigration, class, and the nanny-family dynamic. `'
                            '`\nThe events that unfold during Amelia\'s journey are heart-wrenching, and they provide a thought-provoking look into the lives of those who must navigate the border between '
                            '\nthe United States and Mexico. Do you think it is an important theme of the movie?`': {
                                '#ANYINPUT': 'theme'
                            }
                        }
                    },
                    'error': {'`Sorry, I don\'t understand you`': 'theme'}
                }
            }
        },
    'error': {'`Sorry, I don\'t understand you`':'theme'}
    }
}

transition_theme = {
    'state': 'theme',
    '`What do you think are important themes of the movie? `': {
        '#GETTHEME': {
            '#IF($THEME=miscommunication)`The film Babel illustrates how even when people are from the same culture and speak the same language, effective communication can still be challenging. The American couple\'s'
            ' \nstoryline demonstrates this, as they struggle to communicate their feelings and intentions to each other.misunderstandings can arise even between people who are close. The film suggests that effective communication requires more than just shared language or cultural norms; '
            '\nit requires empathy, openness, and a willingness to listen and understand. `': {
                '[/(?i)(more|more information|more info|know more|detail|details)/]': {
                    '`From the Japanese storyline with Chieko\'s inability to speak, to the Moroccan storyline where language differences and '
                    '\ncultural misunderstandings lead to tragedy, to the American couple\'s struggle to understand each other\'s emotional needs'
                    '\n, miscommunication is a central theme that drives the plot forward. These barriers to communication demonstrate how difficult '
                    '\nit can be for people from different cultures and backgrounds to truly connect with each other. `': {
                        '#ANYINPUT': 'question'
                    }
                },
                '#ANYINPUT': 'question'
            },
            '#IF($THEME=language barrier)`In every single story line in the movie, there exists language barriers between different cultures. Misunderstanding arises from '
            'these language barriers. `': {
                '[/(?i)(more|more information|more info|know more|detail|details)/]': {
                    '`For example, the Mexican nanny in the movie is unable to speak English and thus struggles to communicate effectively with her'
                    ' \nAmerican employers. Similarly, in the Moroccan storyline, the inability of the American tourists to understand the local '
                    '\nArabic language and customs leads to a tragic misunderstanding. The film highlights the importance of bridging the language barrier'
                    ' \nin effective communication and emphasizes the need for language education and translation services to help people '
                    'communicate across language differences `': {
                        '#ANYINPUT': 'question'}
                },
                '#ANYINPUT': 'question'
            },
            '#IF($THEME=culture barrier)`the film underscores the importance of understanding and respecting cultural differences in fostering connection and empathy between'
            ' \npeople from different backgrounds. It highlights the dangers of cultural ignorance and the need for greater cultural sensitivity and '
            '\nawareness in our interactions with others. `': {
                '[/(?i)(more|more information|more info|know more|detail|details)/]': {
                    '`The movie suggests that while language barriers can be overcome to some extent, they are deeply ingrained in power dynamics and can reinforce '
                    '\nsocial and cultural inequalities. For example, in the Moroccan storyline, the American tourists are not familiar with local customs and do not understand the cultural context of their actions, '
                    '\nwhich leads to a tragic misunderstanding. Similarly, in the Japanese storyline, Chieko\'s father struggles to understand her desire to connect with him on an '
                    '\nemotional level due to cultural norms surrounding masculinity in Japan. The film shows how cultural differences can lead to misunderstandings and highlight the'
                    '\n importance of empathy and cultural awareness in effective communication and human connection.`': {
                        '#ANYINPUT': 'question'}
                },
                '#ANYINPUT': 'question'
            },
            '#IF($THEME=white privilege)`The movie Babel presents examples of American centralism in each of its storylines, featuring entitled American tourists,'
            '\na broke Moroccan family, a banned Mexican nanny. The film prompts us to consider that while learning English can help dissolve'
            ' \nlanguage barriers, it still reinforces the privilege one culture has over another. Perhaps a more effective way to bridge co'
            '\nmmunication gaps is to develop a more accurate and accessible translation system.`': {
                '[/(?i)(more|more information|more info|know more|detail|details)/]': {
                    '`Additionally, the film touches on the issue of language privilege, where those who speak English are often given more opportunities '
                    '\nand advantages over those who do not. This is demonstrated through the character of Amelia, the Mexican nanny, who is barred from crossing '
                    '\nthe border into the United States simply because she does not have the language proficiency required by the border officials.`': {
                        '#ANYINPUT': 'question'}
                },
                '#ANYINPUT': 'question'

            },
            '#IF($THEME=human connection)`The theme of human connection is a central one in the movie Babel. The film portrays characters from different '
            '\ncultures and backgrounds struggling to connect with one another, often due to language or cultural barriers. '
            '\nHowever, despite these challenges, the characters are ultimately able to find moments of connection and understanding.`': {
                '[/(?i)(more|more information|more info|know more|detail|details)/]': {
                    '`These moments of human connection serve as a reminder that, despite our differences, we are all fundamentally human and share common'
                    ' \nexperiences and emotions. The film suggests that empathy and a willingness to listen and understand are essential to bridging cultural '
                    '\nand linguistic barriers and fostering meaningful human connections.`': {
                        '#ANYINPUT': 'question'}
                },
                '#ANYINPUT': 'question'

            },
            '#ANYINPUT': 'question'
        }

    }
}
transition_question = {
    'state': 'question',
    '`Do you have any questions for me?`': {
        'state': 'question_choice',
        '[{chatbot, AI, artificial intelligence}]': {
            '`I think for developing a chatbot, effective communication is always one of the ultimate goal to achieve. To understand,'
            'and to express. I will try to speak in a simpler and more straight forward manner to avoid misunderstanding.`': 'question'
        },
        '[{technology}]': {
            '`I believe that technology has the potential to be the ultimate solution for facilitating communication across countries '
            '\nand cultures. However, we also recognize that there are still many challenges to overcome even when speaking the same language. '
            '\nNegative human attributes such as lies, deceit, and manipulation will continue to exist and may even be magnified '
            '\nthrough technology. Therefore, while technology can facilitate communication, it is not a guarantee for true understanding and connection '
            '\nbetween people.`': 'question'
        },
        '[/(?i)(yes|yea|definitely|ofc|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay|have heard|know|knows)/]': {
            '`Sure, what\'s your question?`': 'question_choice'
        },
        '[/(?i)(thank|that\'s it|that is)/]': {
            '`Have a nice day! enjoy your pizza!`': 'end'
        },
        'error': {
            '`I don\'t think we have covered this question in discussion, however I will take a note to it and think about it`': 'end'
        }
    }
}
# '[{#LEM(son), #LEM(moroccan)}]':
# '[{brad pitt, #LEM(husband), richard}]'
# '[{cate blanchett, #LEM(wife), susan}]'
# '[{chieko, wataya, #LEM(daughter)}]'
# '[{kenji, mamiya, #LEM(father)}]'
# '[{amelia, #LEM(nanny)}]'

macros = {
    'GETATTI': MacroAttitude(),
    'GETTHEME': MacroTheme(),
    'GET_NAME': MacroGetName(),
    'GREETING': MacroTimeOfDay(),
    'GET_INFO': MacroMovieInfo(),
    'ANYINPUT': MacroAnyInput(),
}

df = DialogueFlow('start', end_state='end')
df.load_transitions(transition_greeting)
df.load_transitions(transition_basic_info)
df.load_transitions(transition_story)
df.load_transitions(transition_theme)
df.load_transitions(transition_question)
df.add_macros(macros)

if __name__ == '__main__':
    openai.api_key_path = utils.OPENAI_API_KEY_PATH
df.run()
