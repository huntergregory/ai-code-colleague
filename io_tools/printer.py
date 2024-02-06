import platform
import shutil

if platform.system().lower() != 'windows':
    # importing readline allows you to use arrow keys to navigate input() (already possible in Windows powershell)
    # https://stackoverflow.com/a/56275842
    import readline

def sys_display(msg):
    print('⛏️  ' + msg)

def user_prompt(msg):
    while True:
        print('💻  ' + msg)
        result = input('> ').strip()
        if result == '':
            sys_display('WARNING: specify input')
            continue
        line_break()
        return result

def user_prompt_with_options(msg, options):
    print('💻  {}'.format(msg))
    for i, o in enumerate(options):
        if i == 0:
            print('{}) {} [default]'.format(i+1, o))
        else:
            print('{}) {}'.format(i+1, o))
    # get user choice
    while True:
        result = input('> ')

        # default is the first option
        if result == '':
            line_break()
            return options[0]

        for i, o in enumerate(options):
            if result.lower().strip() == o.lower() or (result.isdigit() and int(result) == i+1):
                line_break()
                return o

        sys_display('WARNING: invalid option')

def line_break(character='-'):
    terminal_width, _ = shutil.get_terminal_size()
    print(character * terminal_width)
