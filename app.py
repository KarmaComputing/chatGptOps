import sys
import logging
import os
from ChatGPTHandler import ChatGPTHandler
from flask import Flask
from dotenv import load_dotenv
from unhandled_exception_logger import (
    unhandled_exception_setup,
    handle_exception,
)

load_dotenv()

PYTHON_LOG_LEVEL = os.getenv("PYTHON_LOG_LEVEL", "DEBUG")


# Register chatGPTHandler log handler
chatGPTHandler = ChatGPTHandler()
chatGPTHandler.setLevel("CRITICAL")

unhandled_exception_setup(handler=chatGPTHandler)


logger = logging.getLogger()
logger.setLevel(PYTHON_LOG_LEVEL)
logger.addHandler(chatGPTHandler)


# # Direct all uncaught exceptions to handle_exception
sys.excepthook = handle_exception


# Minimal python app example with example unhandled exception
app = Flask(__name__)
logging.getLogger("werkzeug").disabled = True
app.logger.disabled = True


@app.errorhandler(Exception)
def flask_handle_exception(e):
    handle_exception(
        sys.exc_info()[0],
        sys.exc_info()[1],
        sys.exc_info()[2],
        handler=chatGPTHandler,  # noqa: E501
    )


@app.errorhandler(500)
def error_page(e):
    return "An error occurred"


@app.route("/")
def index():
    return "index"


@app.route("/error")
def error():
    colors = ["Red", "Blue"]
    print(colors[3])
    names = ["Bob", "Alice"]
    print(names[2])
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    app.run(threaded=True)
