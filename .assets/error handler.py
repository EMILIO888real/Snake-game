human_notes = input('Could you explain a bit more about the error? What or How or When did the error happen? (Leave empty if you got nothing to say)\nInput: ')
if bool(human_notes):
    with open('error report.txt', 'a') as f:
        f.write(f'\nHuman notes: {human_notes}\n')
    print('Thanks for the info')