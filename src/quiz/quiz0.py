from emora_stdm import DialogueFlow

transitions = {
    'state': 'start',
    '`Hello. How are you?`': {
        '[{good, fantastic}]': {
            '`Glad to hear that you are doing well :)`': {
                '[{how, and}, {you, going}]': {
                    '`I feel superb. Thank you!`': 'end'
                }
            }
        },
        'error': {
            '`Got it; thanks for sharing.`': 'end'
        },
    }
}

df = DialogueFlow('start', end_state='end')
df.load_transitions(transitions)

if __name__ == '__main__':
    df.run()