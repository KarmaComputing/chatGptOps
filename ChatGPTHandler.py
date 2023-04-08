import logging
import openai
import os
import inspect


class ChatGPTHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        super().__init__(*args, **kwargs)

    def emit(self, record):
        last_tb_frame, last_tb_frame_lineno = record.exc_info[2]
        last_tb_filename = inspect.getfile(last_tb_frame)
        with open(last_tb_filename) as fp:
            code = fp.read()
            # Get code from around the problem area
            line_start = last_tb_frame_lineno - 5
            line_end = last_tb_frame_lineno + 5
            code_snippet = "\n".join(code.split("\n")[line_start:line_end])

            print("#" * 80)
            print(f"Exception in file: {record.pathname}")
            print(f"Sending code_snippet:\n\n{code_snippet}")
            print("#" * 80)
            traceback = f"{str(record.exc_info)}, lineno: {last_tb_frame_lineno}, filename: {last_tb_filename}"  # noqa: E501
            prompt = f"##### Explain the bug in the below traceback and code. Where possible, always include the line number(s) of where the error(s) may be. Also, if possible include a possible fix for the code at the end- but always warn the user to check the code and not assume the proposed solution is correct.\n \n## Buggy Python code\n{code_snippet}\n \n## Traceback \n{traceback}"  # noqa: E501
            print("#" * 80, f"Sending the following promt:\n{prompt}")
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0,
                max_tokens=800,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
            print("#" * 80)
            print(f"The response was:\n\n{response}")
            print("#" * 80)
