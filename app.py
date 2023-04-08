import sys
import logging
import os
import traceback
from ChatGPTHandler import ChatGPTHandler
from flask import Flask
from dotenv import load_dotenv

PYTHON_LOG_LEVEL = os.getenv("PYTHON_LOG_LEVEL", "DEBUG")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

load_dotenv()

logger = logging.getLogger()


# Log all uncuaght exceptions
def handle_exception(exc_type=None, exc_value=None, exc_traceback=None):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    # Walk the trackback until reaching the last traceback frame
    for tb_frame in traceback.walk_tb(exc_traceback):
        last_tb_frame = tb_frame
    # TODO pass also full callstack, since we've cut off the previous tb frames
    logger.critical(
        "Uncaught exception", exc_info=(exc_type, exc_value, last_tb_frame)
    )  # noqa: E501


# Direct all uncaught exceptions to handle_exception
sys.excepthook = handle_exception

# Register chatGPTHandler log handler
chatGPTHandler = ChatGPTHandler()
chatGPTHandler.setLevel(PYTHON_LOG_LEVEL)
logger.addHandler(chatGPTHandler)

# Minimal python app example with example unhandled exception
app = Flask(__name__)
logging.getLogger("werkzeug").disabled = True
app.logger.disabled = True


@app.errorhandler(Exception)
def flask_handle_exception(e):
    handle_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])


@app.errorhandler(500)
def error_page(e):
    return "An error occurred"


@app.route("/")
def index():
    return "index"


@app.route("/error")
def error():
    names = ["Bob", "Alice"]
    print(names[2])
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    app.run(threaded=True)
