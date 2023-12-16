import os
from random import choice
import shutil
import subprocess
import sys

from agents.coding_agent import CodingAgent
# from agents.coding_agent_mock import CodingAgentMock as CodingAgent
from config import (
    OAI_API_KEY,
    LOCAL_LLM,
    AOC_SESSION_KEY,
)
from integrations.aoc import AocIntegration
from log.logger import (
    sys_display,
    user_prompt,
    user_prompt_with_options,
    line_break,
)

DEBUG = False

OAI_MODEL = None # 'gpt-3.5-turbo'
TEMPERATURE = 0.3

# relative base directory for advent of code puzzles
AOC_DIRECTORY = 'aoc/'
AOC_FNAME = 'solution'

GOLANG = 'Go'
PYTHON = 'Python'
LANGUAGES = [
    GOLANG,
    PYTHON,
]
FILE_EXTENSIONS = {
    GOLANG: 'go',
    PYTHON: 'py',
}
REACTIONS = [
    'Nice!',
    'Got it.',
]

MULTI_FILE = 'create/edit files'
AOC = 'Advent of Code'
TASKS = [MULTI_FILE, AOC]

MAX_ARCHIVE_DIRS = 100

def main(oai_api_key, local_model, session_key):
    ## setup
    if not local_model:
        local_model = os.environ.get('LOCAL_LLM')

    if not local_model and not oai_api_key:
        oai_api_key = os.environ.get('OAI_API_KEY')
        if not oai_api_key:
            oai_api_key = os.environ.get('OPENAI_API_KEY')
        if not oai_api_key:
            sys_display("""ERROR: Please configure your LLM (see README for more details).
Options:
- Set an OpenAI API key in config.py
- Download an LLM locally, then specify model filepath in config.py')""")
            sys.exit(1)

    if not local_model:
        os.environ['OPENAI_API_KEY'] = oai_api_key

    mode = user_prompt_with_options(choice(REACTIONS) + ' Which task?', "Task", TASKS)

    if mode == AOC and not session_key:
        session_key = os.environ.get('AOC_SESSION_KEY')
        if not session_key:
            sys_display('INFO: session key not set. Set this to automate input downloads and submissions (see README)')
            line_break()

    script_dir = os.path.dirname(os.path.abspath(__file__)) + '/'

    while True:
        ## outer loop which selects the file/workspace to work on
        if mode == AOC:
            aoc_integration = AocIntegration(script_dir + AOC_DIRECTORY, session_key)
            aoc_integration.prompt_puzzle()
            dir = aoc_integration.puzzle_dir()
            language = user_prompt_with_options("Let's code! Which language?", "Language", LANGUAGES)
            file = dir + AOC_FNAME + '.' + FILE_EXTENSIONS[language]
            tmp_file = dir + 'tmp-' + AOC_FNAME + '.' + FILE_EXTENSIONS[language]
            is_part_one = True
        
        if mode == MULTI_FILE:
            while True:
                file = user_prompt('Specify filepath (default is "./script.<language-extension>")')

                if file == '':
                    language = user_prompt_with_options("Let's code! Which language?", "Language", LANGUAGES)
                    dir = './'
                    fname = 'script'
                    file = dir + fname + '.' + FILE_EXTENSIONS[language]
                    tmp_file = dir + 'tmp-' + fname + '.' + FILE_EXTENSIONS[language]
                    break

                # TODO validate path and convert ~ to actual home
                dir = os.path.dirname(os.path.abspath(file)) + '/'
                base = os.path.basename(file)
                fname, extension = os.path.splitext(base)
                language = None
                for l, e in FILE_EXTENSIONS.items():
                    if extension[1:] == e:
                        language = l
                        break
                if language is not None:
                    file = dir + fname + extension
                    tmp_file = dir + 'tmp-' + fname + extension
                    break

                sys_display('ERROR: extension/language not supported. extension: {}'.format(extension))

        if os.path.exists(dir):
            sys_display('WARNING: directory already exists: {}'.format(dir))
        else:
            sys_display('INFO: creating directory: {}'.format(dir))
            os.makedirs(dir)
        line_break()

        if mode == AOC:
            aoc_integration.download_inputs()

        if local_model:
            # TODO
            pass
        model = CodingAgent(language, FILE_EXTENSIONS[language], model=OAI_MODEL, temperature=TEMPERATURE, debug=DEBUG)
        sys_display('INFO: using model: {}'.format(model.model_name))
        line_break()

        # TODO git commits
        # if mode == AOC:
        #     base = os.path.basename(file)
        #     commit_name = 'wip: {}'.format(base)
        # else:
        #     base = os.path.basename(file)
        #     commit_name = 'wip: {}'.format(base)

        if os.path.isfile(file):
            with open(file, 'r') as f:
                sys_display('INFO: file exists:\n{}'.format(f.read()))
                line_break()
            instructions = user_prompt('What should change?')
        else:
            instructions = user_prompt('What should we code?')
        while True:
            ## inner loop to create the file and iterate on it
            if os.path.isfile(file):
                ## rewrite code
                with open(file, 'r') as f:
                    contents = f.read()
                sys_display('INFO: rewriting code in a tmp file...')
                # TODO let chat model know if there was an error?
                code = model.revise_solution(instructions, contents)
                with open(tmp_file, 'w') as f:
                    f.write(code)
                sys_display('INFO: wrote code to: {}\n\n{}'.format(tmp_file, code))
                line_break()

                if mode == MULTI_FILE:
                    options = ['overwrite', 'abort + retry', 'abort + go to new file']
                if mode == AOC:
                    options = ['overwrite', 'abort + retry', 'abort + new puzzle/language']
                action = user_prompt_with_options('What next? Overwriting will replace: {}'.format(file), 'Action', options)

                if action == 'abort + go to new file' or action == 'abort + new puzzle/language':
                    model.abort_last()
                    os.remove(tmp_file)
                    sys_display('INFO: deleted tmp file')
                    line_break(character='=')
                    # restart outer loop
                    break

                if action == 'abort + retry':
                    model.abort_last()
                    os.remove(tmp_file)
                    sys_display('INFO: deleted tmp file')
                    line_break()
                    # restart inner loop
                    instructions = user_prompt("Ok, let's retry. What should change?")
                    continue

                if action == 'overwrite':
                    shutil.copy2(dst=file, src=tmp_file)
                    os.remove(tmp_file)
                    sys_display('INFO: overwrote file and deleted tmp file. file: {}'.format(file))
                    line_break()
                else:
                    raise RuntimeError('unknown action: ' + action)
            else:
                ## create code
                sys_display('INFO: creating code...')
                code = model.initial_solution(instructions)
                with open(file, 'w') as f:
                    f.write(code)
                sys_display('INFO: wrote code to: {}\n\n{}'.format(file, code))
                line_break()

            if mode == MULTI_FILE:
                options = ['run', 'go to new file']
            if mode == AOC:
                if is_part_one:
                    options = ['run', 'modify', 'start part 2', 'new puzzle/language']
                else:
                    options = ['run', 'modify', 'new puzzle/language']
            action = user_prompt_with_options('What next?', 'Action', options)

            if action == 'run':
                if language == GOLANG:
                    cmd = ['go', 'run', file]
                elif language == PYTHON:
                    cmd = ['python', file]
                else:
                    cmd = ['echo', '"{} does not support \"run\" currently'.format(language)]
                sys_display('INFO: running code...\n' + ' '.join(cmd))
                run_result = subprocess.run(cmd, capture_output=True)
                print(run_result.stdout.decode())
                if run_result.returncode != 0:
                    print(run_result.stderr.decode())
                    print('exit code: {}'.format(run_result.returncode))
                    line_break()
                    if mode == MULTI_FILE:
                        options = ['modify', 'go to new file']
                    if mode == AOC:
                        options = ['modify', 'new puzzle/language']
                    action = user_prompt_with_options('Bummer, there was an error.', 'Action', options)
                else:
                    if mode == MULTI_FILE:
                        options = ['modify', 'go to new file']
                    if mode == AOC:
                        if is_part_one:
                            options = ['modify', 'submit', 'start part 2', 'new puzzle/language']
                        else:
                            options = ['modify', 'submit', 'new puzzle/language']
                    action = user_prompt_with_options('We can iterate or move on.', 'Action', options)

            if action == 'submit':
                success = aoc_integration.submit(run_result.stdout.decode())
                if success == 1:
                    if is_part_one:
                        action = user_prompt_with_options('Start part 2?', 'Action', ['yes', 'no, start new puzzle/language'])
                    else:
                        action == 'new puzzle/language'
                else:
                    options = ['modify', 'new puzzle/language']
                    action = user_prompt_with_options('What do you want to do?', 'Action', options)

            if action == 'go to new file' or 'new puzzle/language' in action:
                # technically will have a '-' line break above this
                # not worth optimizing to remove that '-' line break
                line_break(character='=')
                # restart outer loop
                break

            # if 'archive' in action:
            #     for i in range(MAX_ARCHIVE_DIRS):
            #         archive_dir = dir + 'archive-{:02}'.format(i+1) + '/'
            #         if not os.path.exists(archive_dir):
            #             break
            #         if i == MAX_ARCHIVE_DIRS - 1:
            #             raise RuntimeError('unable to create archive dir. {} archives already exist. example: {}'.format(MAX_ARCHIVE_DIRS, archive_dir))

            #     sys_display('INFO: creating directory: {}'.format(archive_dir))
            #     os.makedirs(archive_dir)
            #     archive_file = archive_dir + os.path.basename(file)
            #     shutil.copy2(src=file, dst=archive_file)
            #     sys_display('INFO: copied file into archive directory')
            #     line_break()

            if action == 'yes' or action == 'start part 2':
                part1_file = dir + AOC_FNAME + '-part1.' + FILE_EXTENSIONS[language]
                shutil.copy2(src=file, dst=part1_file)
                is_part_one = False
                # restart inner loop
                instructions = user_prompt('On to part 2! What should change?')
                continue

            if action != 'modify':
                raise RuntimeError('unknown action: ' + action)

            instructions = user_prompt('What should change?')

if __name__ == '__main__':
    main(OAI_API_KEY, LOCAL_LLM, AOC_SESSION_KEY)
