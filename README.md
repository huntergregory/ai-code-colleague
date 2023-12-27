# Voice IDE 🗣️💻✨
Free, CLI-based editor to create/iterate on code using natural language.

Built for hands-free, accessible coding via dictation.

## [Advent of Code](https://adventofcode.com) Integration
Focus on developing puzzle solutions instead of the logistics & coding minutiae like parsing.

Automates:
- Creating files/folders.
- Downloading inputs.
- Running code.
- Submitting answers.

_**Note:**_ AI should not be used for AOC submissions impacting leaderboards. For more info, see https://adventofcode.com/about.

## Usage
Supports OpenAI or a locally run model for privacy.

### Option 1: OpenAI
#### Python Dependencies
```
python -m pip install langchain
python -m pip install openai
```

#### API Key
First, [create your key](https://platform.openai.com/api-keys).

Then:

- Modify this line in *config.py*:
```
OAI_API_KEY=None # replace with string
```

or

- Set an environment variable like:
```
export OAI_API_KEY='<your-key>'
```

### Option 2: Local Model
Work in progress.

#### Dependencies
Install/configure [LLM](https://llm.datasette.io/en/stable/) utility with below commands:
```
python -m pip install llm
llm install llm-gpt4all
```

Then:

- Modify this line in *config.py*:
```
LOCAL_LLM='mistral-7b-openorca' # replace with model name from llm utility
```

or

- Set an environment variable like:
```
export LOCAL_LLM='mistral-7b-openorca'
```

### Advent of Code
#### Optional: Advent of Code Session Key
This allows automation of downloading input and submitting answers.

1. Login to [adventofcode.com](https://adventofcode.com)
2. Get your session key from inspecting the webpage:
- Open the Inspector (CTRL + SHIFT + C).
- Copy the cookie value called "session" in Application > Cookies
![cookie-location](images/cookie.png)

3. Modify config:
- Modify this line in *config.py*:
```
AOC_SESSION_KEY=None # replace with string
```

OR

- Set an environment variable like:
```
export AOC_SESSION_KEY='<your-key>'
```

#### Special Notes
Some AOC submission logic is inspired by [github.com/caderek/aocrunner](https://github.com/caderek/aocrunner). Like aocrunner, this project respects [the concerns of the AoC creator](https://www.reddit.com/r/adventofcode/comments/3v64sb/aoc_is_fragile_please_be_gentle/), and limits unnecessary requests.

The tool:
- Downloads inputs once (re-download by deleting the input directory).
- Submits only valid answers (expected format: single number).
- Prevents resubmissions until the server-specified timeout for incorrect answers.
