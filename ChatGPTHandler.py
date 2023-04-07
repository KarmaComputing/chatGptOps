from logging import StreamHandler
import openai
import os


class ChatGPTHandler(StreamHandler):
    def __init__(self, *args, **kwards):
        super().__init__(*args, **kwards)

    def emit(self, record):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        with open(record.pathname) as fp:
            code = fp.read()
            traceback = f"{str(record.exc_info)}, lineno: {record.lineno}, filename: {record.filename}"  # noqa: E501
            prompt = (
                f"##### Explain the bug in the below traceback and code. Where possible, always include the line number(s) of where the error(s) may be. Also, if possible include a possible fix for the code at the end- but always warn the user to check the code and not assume the proposed solution is correct.\n \n## Buggy Python code\n{code}\n \n## Traceback \n{traceback}",  # noqa: E501
            )
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0,
                max_tokens=182,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
            return response
