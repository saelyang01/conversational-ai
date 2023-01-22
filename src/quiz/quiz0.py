from emora_stdm import DialogueFlow

transitions = {
    'state': 'start',
    '`Hello. How are you?`': {
        '[{good, fantastic}]': {
            '`Glad to hear that you are doing well :)`': {
                'error': {
                    '`See you later!`': 'end'
                }
            }
        },
        'error': {
            '`I hope your day gets better soon :(`': {
                'error': {
                    '`Take care!`': 'end'
                }
            }
        }
    }
}

df = DialogueFlow('start', end_state='end')
df.load_transitions(transitions)

if __name__ == '__main__':
    df.run()