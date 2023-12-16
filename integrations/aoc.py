import os
import requests
import string

from log.logger import (
    line_break,
    sys_display,
    user_prompt,
)

class AocIntegration:
    def __init__(self, dir, session_key=None):
        self.year = 0
        self.day = 0
        self.base_dir = dir
        self.session_key = session_key

    def prompt_puzzle(self):
        # specify puzzle to solve
        while True:
            puzzle = user_prompt('Which puzzle should we solve?')
            puzzle = ''.join(char.lower() for char in puzzle if char not in string.punctuation)
            info = puzzle.split()
            if len(info) != 3 or not (info[0].isdigit() and info[1] == 'day' and info[2].isdigit):
                sys_display('ERROR: respond like: "<year> day <number>"')
                continue

            self.year = int(info[0])
            self.day = int(info[2])
            return

    def puzzle_dir(self):
        return self.base_dir + '{}/day-{:02}/'.format(self.year, self.day)
    
    def inputs_dir(self):
        return self.puzzle_dir() + 'inputs/'

    def download_inputs(self):
        if not self.session_key:
            return

        os.makedirs(self.inputs_dir)
        # TODO

    def submit(self):
        if not self.session_key:
            sys_display("WARNING: can't submit. Session key must be specified in before running the CLI (see README)")
            line_break()
            return -1
        sys_display('INFO: submitting...')
        # TODO
        line_break()
        return 1
