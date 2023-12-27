from agents.testfile import testfile

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

DEFAULT_MODEL = 'text-davinci-003'
CHAT_MODELS = [
    'gpt-3.5-turbo',
]

class CodingAgent:
    def __init__(self, language, extension, model=None, temperature=0.3, debug=False, verbose=True):
        self.instruction_history = []
        self.debug = debug
        if debug:
            self.model_name = 'mock'
            return

        if language.lower() == 'go':
            language = 'Golang'
        system_msg = 'SYSTEM: Respond with only a main.{} file ({} code). The code should perform the user-specified task.'.format(extension, language)
        template = system_msg + """
{chat_history}{current_file}
HUMAN: {instructions}
FILE:
"""
        if model is None:
            model = DEFAULT_MODEL
        if model in CHAT_MODELS:
            llm = ChatOpenAI(model=model, temperature=temperature)
        else:
            llm = OpenAI(model=model, temperature=temperature)
        self.model_name = llm.model_name
        prompt = PromptTemplate(input_variables=['chat_history', 'current_file', 'instructions'], template=template)
        self.conversation = LLMChain(llm=llm, prompt=prompt, verbose=verbose)

    def initial_solution(self, instructions):
        return self._run(instructions, '')

    def revise_solution(self, instructions, code):
        return self._run(instructions, 'FILE:\n' + code)
    
    def abort_last(self):
        if len(self.instruction_history) > 0:
            self.instruction_history.pop()

    def _run(self, instructions, current_file):
        if self.debug:
            return testfile
        chat_history = ''
        for i in self.instruction_history:
            chat_history += 'HUMAN: {}\n'.format(i)
        result = self.conversation.run(chat_history=chat_history, instructions=instructions, current_file=current_file)
        self.instruction_history.append(instructions)
        return result
