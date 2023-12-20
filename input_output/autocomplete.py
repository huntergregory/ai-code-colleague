import glob
import os
import readline

def _complete(text, state):
    return (glob.glob(os.path.expanduser(text)+'*')+[None])[state]

def tab_to_autocomplete_filepaths():
    # pressing tab will complete filepaths
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(_complete)
