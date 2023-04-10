from setuptools import setup

VERSION = "0.0.1"

with open("README.md", "r") as fp:
    README = fp.read()

setup(
    name="ChatGPTOps",
    version=VERSION,
    description="Ask chatGPT llm to investigate your unhandled exceptions & file github issues with proposed fixes without filing duplicate issues",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Chris Simpson",
    author_email="oss@karmacomputing.co.uk",
    url="https://github.com/karmacomputing/chatgptops",
    py_modules=["ChatGPTHandler"],
    classifiers=["License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
    python_requires=">=3.9",
    install_requires=["unhandled_exception_logger", "openai"],
)
