import os
import re
import requests
import string
import time

from input_output.input_output import (
    line_break,
    sys_display,
    user_prompt
)

BASE_URL = 'https://adventofcode.com/'

NUMBERS_TO_INT = {
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9
}

TIME_UNIT_TO_SECONDS = {
    'second': 1,
    's': 1,
    'minute': 60,
    'm': 60,
    'hour': 60 * 60,
    'h': 60 * 60,
    'day': 24 * 60 * 60,
    'd': 24 * 60 * 60
}

class AocIntegration:
    def __init__(self, dir, session_key=None):
        self.is_part_one = True
        self.last_submission_time = 0
        self.submission_seconds_to_wait = 0
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
        if os.path.exists(self.inputs_dir()):
            sys_display('INFO: AoC inputs directory already configured: {}'.format(self.inputs_dir()))
            line_break()
            return

        sys_display('INFO: making directory: {}'.format(self.inputs_dir()))
        os.makedirs(self.inputs_dir())

        sys_display('INFO: downloading Advent of Code test input...')
        url = '{}/{}/day/{}'.format(BASE_URL, self.year, self.day)
        response = requests.get(url)
        if response.status_code != 200:
            sys_display('WARNING: unable to curl website for test input. url: {}. response code: {}'.format(url, response.status_code))
            line_break()
            return

        content = text_between(response.text, '<main>', '</main>')
        if content is None:
            sys_display('WARNING: unable to get main element for test input. url: {}. response: {}'.format(url, response.text))
            line_break()
            return

        test_inputs = []
        search_string = 'for example:'
        for i in range(len(response.text)-len(search_string)):
            if response.text[i:i+len(search_string)].lower() == search_string:
                example_start = i+len(search_string)
                t = text_between(response.text[example_start:], '<code>', '</code>')
                if t is None:
                    continue
                if t[len(t)-1] == '\n':
                    t = t[:len(t)-1]
                test_inputs.append(t)

        for i, t in enumerate(test_inputs):
            file = self.inputs_dir() + 'test-input-{}.txt'.format(i+1)
            with open(file, 'w') as f:
                f.write(t)

        if len(test_inputs) > 0:
            sys_display('INFO: successfully download {} test input(s)'.format(len(test_inputs)))
        else:
            sys_display('WARNING: unable to find test inputs. url: {}'.format(url))

        if not self.session_key:
            line_break()
            return

        sys_display('INFO: downloading AoC user input...')
        url += '/input'
        headers = {
            'cookie': 'session={}'.format(self.session_key),
            'User-Agent': 'github.com/huntergregory/code-gpt',
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            sys_display('WARNING: unable to get user input. url: {}. response code: {}'.format(url, response.status_code))
            line_break()
            return
        t = response.text
        if t[len(t)-1] == '\n':
            t = t[:len(t)-1]
        file = self.inputs_dir() + 'input.txt'
        with open(file, 'w') as f:
            f.write(t)
        sys_display('INFO: successfully download user input')
        line_break()

    def submit(self, output):
        if not self.session_key:
            sys_display('ERROR: cannot submit. Session key must be specified in config.py before running the CLI (see README)')
            line_break()
            return False

        output = output.strip()
        if not output.isdigit():
            sys_display('ERROR: cannot submit. Program output/submission must be a single digit')
            line_break()
            return False

        elapsed_time = time.time() - self.last_submission_time
        if elapsed_time < self.submission_seconds_to_wait:
            sys_display('ERROR: must wait to submit. Wait {} more seconds'.format(self.submission_seconds_to_wait - (elapsed_time)))
            line_break()
            return False

        sys_display('INFO: submitting...')
        headers = {
            'cookie': 'session={}'.format(self.session_key),
            'content-type': 'application/x-www-form-urlencoded',
            'User-Agent': 'github.com/huntergregory/code-gpt',
        }

        part = 1 if self.is_part_one else 2
        body = 'level={}&answer={}'.format(part, output)
        url = '{}/{}/day/{}/answer'.format(BASE_URL, self.year, self.day)
        response = requests.post(url, headers=headers, data=body)
        if response.status_code != 200:
            sys_display('WARNING: failed to submit. url: {}. body: {}. response code: {}'.format(url, body, response.status_code))
            line_break()
            return

        content = text_between(response.text, '<main>', '</main>')
        if content is None:
            sys_display('WARNING: unable to get main element for submission response. url: {}. body: {}. response: {}'.format(url, body, response.text))
            line_break()
            return

        if "That's the right answer" in content:
            if self.is_part_one:
                sys_display('INFO: ✅ Solved part 1!')
            else:
                sys_display('INFO: ✅🏆✅ Solved part 2!')
            line_break()
            return True

        if "You don't seem to be solving the right level" in content:
            sys_display('WARNING: already completed this day/part or it is unavailable')
            line_break()
            return False

        if "That's not the right answer" in content:
            sys_display('INFO: ❌ incorrect solution. Full response:\n{}'.format(content))

        if 'You gave an answer too recently' in content:
            sys_display('WARNING: must wait longer to submit again')
        else:
            sys_display('WARNING: unknown submission response. Full repsonse:\n{}'.format(content))

        time_result = re.findall(r"(one|two|three|four|five|six|seven|eight|nine|ten) (second|minute|hour|day)", content)
        if len(time_result) > 0:
            self.last_submission_time = time.time()
            self.submission_seconds_to_wait = 0
            for num, unit in time_result:
                self.submission_seconds_to_wait += NUMBERS_TO_INT[num] * TIME_UNIT_TO_SECONDS[unit]
            sys_display('INFO: must wait {} seconds before submitting again'.format(self.submission_seconds_to_wait))
            line_break()
            return False

        time_result = re.findall(r"(\d+)\s*(s|m|h|d)", content)
        if len(time_result) > 0:
            self.last_submission_time = time.time()
            self.submission_seconds_to_wait = 0
            for num, unit in time_result:
                self.submission_seconds_to_wait += int(num) * TIME_UNIT_TO_SECONDS[unit]
            sys_display('INFO: must wait {} seconds before submitting again'.format(self.submission_seconds_to_wait))
        line_break()
        return False

def text_between(text, left, right):
    left_start = text.index(left)
    if left_start < 0:
        return None
    text = text[left_start+len(left):]
    for j in range(len(text) - len(right)):
        if text[j:j+len(right)] == right:
            return text[:j]
    return None
