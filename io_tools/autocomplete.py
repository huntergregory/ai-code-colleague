import glob
import os
import platform

def _complete(text, state):
    return (glob.glob(os.path.expanduser(text)+'*')+[None])[state]

def tab_to_autocomplete_filepaths():
    if platform.system().lower() != 'windows':
        import readline
        # pressing tab will complete filepaths
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(_complete)
