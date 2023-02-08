from emora_stdm import DialogueFlow

transitions = {
    'state': 'start',
    '`Hello, how can I help you?`': {

        '[{haircut, haircutting,cut}]':{
            '`Sure. What date and time are you looking for?`':{
                '[monday, <10>, am]':{
                     '`Your appointment is set. See you!`':'end'
                        },
                '[monday, <1>, pm]':{
                     '`Your appointment is set. See you!`':'end'
                        },
                '[monday,<2>, pm]':{
                    '`Your appointment is set. See you!`':'end'
                        },
                '[tuesday,<2>, pm]':{
                    '`Your appointment is set. See you!`':'end'
                        },
                'error':{
                    '`Sorry, that slot is not available for a haircut.`':'end'
                        }
            }
        },

        '[{hair coloring, coloring,color}]':{
            '`Sure. What date and time are you looking for?`':{
                '[wednesday,<10>, am]':{
                    '`Your appointment is set. See you!`':'end'
                        },
                '[wednesday,<11>, am]':{
                    '`Your appointment is set. See you!`':'end'
                        },
                '[wednesday,<1>, pm]':{
                    '`Your appointment is set. See you!`':'end'
                        },
                '[thursday,<10>, am]':{
                    '`Your appointment is set. See you!`':'end'
                        },
                '[thursday,<11>, am]':{
                    '`Your appointment is set. See you!`':'end'
                        },
                'error':{
                    '`Sorry, that slot is not available for a hair coloring.`':'end'
                        }
            }
                },

        '[{hair perming, perming,perm}]':{
            '`Sure. What date and time are you looking for?`':{
                '[friday, <10>, am]':{
                    '`Your appointment is set. See you!`':'end'
                        },
                '[friday, <11>, am]':{
                    '`Your appointment is set. See you!`':'end'
                        },
                '[friday, <1>, pm]':{
                    '`Your appointment is set. See you!`':'end'
                        },
                '[friday, <2>, pm]':{
                    '`Your appointment is set. See you!`':'end'
                        },
                '[saturday, <10>, am]':{
                    '`Your appointment is set. See you!`':'end'
                        },
                '[saturday, <2>, pm]':{
                    '`Your appointment is set. See you!`':'end'
                        },
                'error':{
                    '`Sorry, that slot is not available for a perming.`':'end'
                        }
                }
        },

        'error':{
            '`Sorry, we do not provide that service.`':{
                    'error': {'goodbye.':'end'}
                        }
                }
        }
}













df = DialogueFlow('start', end_state='end')
df.load_transitions(transitions)

if __name__ == '__main__':
    df.run()
