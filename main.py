import sys
import logging
import os
import openai
import traceback
from ChatGPTHandler import ChatGPTHandler

PYTHON_LOG_LEVEL = os.getenv("PYTHON_LOG_LEVEL", "DEBUG")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

logger = logging.getLogger()


class ExceptionFormatter(logging.Formatter):
    def format(self, record):
        return super().format(record)


# Log all uncuaght exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    # Create issue
    # Send code + traceback to ChatGPT
    # Get code
    traceback.print_exc()
    logger.critical(
        "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
    )  # noqa: E501


sys.excepthook = handle_exception


chatGPTHandler = ChatGPTHandler()
chatGPTHandler.setLevel(PYTHON_LOG_LEVEL)
logger.addHandler(chatGPTHandler)

openai.api_key = os.getenv("OPENAI_API_KEY")

names = ["Bob", "Alice"]

print(names[2])


print("hello")
