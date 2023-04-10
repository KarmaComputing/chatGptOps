import logging
import openai
import os
import inspect
import urllib.request
import json
import hashlib
from pathlib import Path


class ChatGPTHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.GITHUB_FINE_GRAINED_ACCESS_TOKEN = os.getenv(
            "GITHUB_FINE_GRAINED_ACCESS_TOKEN"
        )
        self.GITHUB_ORG_NAME_OR_USERNAME = os.getenv(
            "GITHUB_ORG_NAME_OR_USERNAME"
        )  # noqa: E501
        self.GIT_REPO_NAME = os.getenv("GIT_REPO_NAME")
        super().__init__(*args, **kwargs)

        if (
            self.OPENAI_API_KEY is None
            or self.GITHUB_FINE_GRAINED_ACCESS_TOKEN is None
            or self.GITHUB_ORG_NAME_OR_USERNAME is None
            or self.GIT_REPO_NAME is None
        ):
            raise Exception(
                "\nChatGPTHandler is missing one or more config settings.\nYou must set OPENAI_API_KEY, GITHUB_FINE_GRAINED_ACCESS_TOKEN, GITHUB_ORG_NAME_OR_USERNAME, and GIT_REPO_NAME as environment settings."
            )

    def emit(self, record):
        # Create unique hash for issue made of:
        #   - file name
        #   - error linenumber
        #   - exception name
        #   - hash of the line of the file with the error
        exception_name = record.exc_info[0].__name__
        import traceback

        for tb_frame in traceback.walk_tb(record.exc_info[2]):
            last_tb_frame = tb_frame
        last_tb_frame_only, last_tb_frame_lineno = last_tb_frame
        last_tb_filepath = inspect.getfile(last_tb_frame_only)
        last_tb_filename = Path(last_tb_filepath).name

        # Read last_tb_frame_lineno to build unique hash of issue and
        # cater to code changes (exception type + last_tb_frame_lineno is insufficient) # noqa: E501
        with open(last_tb_filepath) as fp:
            code = fp.read().split("\n")
            str_sourcecode_error_line_extracted = code[
                last_tb_frame_lineno - 1
            ]  # noqa: E501

        concat_exception_hints = (
            str(exception_name)
            + str(last_tb_frame_lineno)
            + str(last_tb_filepath)
            + str(str_sourcecode_error_line_extracted)
        )  # noqa: E501
        issue_sha = hashlib.sha1(concat_exception_hints.encode("utf-8"))
        issue_sha_digest = issue_sha.hexdigest()[:7]
        issue_title = f"{exception_name} on line {last_tb_frame_lineno} in file {last_tb_filename} uniq ref: {issue_sha_digest}"  # noqa: E501
        issue_already_exists = False

        # Search issues to check issue does not already exist
        repo_owner = self.GITHUB_ORG_NAME_OR_USERNAME
        repo_name = self.GIT_REPO_NAME

        # Set up the API request headers
        headers = {"Accept": "application/vnd.github.v3+json"}

        # Set up the search query parameters
        params = {
            "q": f"{issue_sha_digest}+repo:{repo_owner}/{repo_name} is:issue"
        }  # noqa: E501

        # Encode the search query parameters as a URL-encoded string
        query_string = urllib.parse.urlencode(params)

        # Set up the API request URL
        url = f"https://api.github.com/search/issues?{query_string}"

        # Create a request object and set the headers
        req = urllib.request.Request(url, headers=headers)

        # Send the API request
        response = urllib.request.urlopen(req)

        # Extract the search results
        search_results = json.loads(response.read().decode())["items"]

        #
        if len(search_results) > 0:
            issue_already_exists = True
            print(
                f"Issue {issue_sha_digest} already exists so refusing to continue"  # noqa: E501
            )

        if issue_already_exists is False:
            with open(last_tb_filepath) as fp:
                code = fp.read()
                # Get code from around the problem area
                line_start = last_tb_frame_lineno - 5
                line_end = last_tb_frame_lineno + 5
                code_snippet = "\n".join(code.split("\n")[line_start:line_end])

                print("#" * 80)
                print(f"Exception in file: {last_tb_filepath}")
                print(f"Sending code_snippet:\n\n{code_snippet}")
                print("#" * 80)
                str_traceback = f"{str(record.exc_info)}, lineno: {last_tb_frame_lineno}, filename: {last_tb_filepath}"  # noqa: E501
                prompt = f"##### Explain the bug in the below traceback and code. Where possible, always include the line number(s) of where the error(s) may be. Also, if possible include a possible fix for the code at the end- but always warn the user to check the code and not assume the proposed solution is correct.\n \n## Buggy Python code\n{code_snippet}\n \n## Traceback \n{str_traceback}"  # noqa: E501
                print("#" * 80, f"Sending the following promt:\n{prompt}")
                openai.api_key = os.getenv("OPENAI_API_KEY")
                try:
                    chatGPT_request = openai.Completion.create(
                        model="text-davinci-003",
                        prompt=prompt,
                        temperature=0,
                        max_tokens=800,
                        top_p=1.0,
                        frequency_penalty=0.0,
                        presence_penalty=0.0,
                    )
                    print("#" * 80)
                    print(f"The response was:\n\n{chatGPT_request}")
                    print("#" * 80)

                    issue_body = chatGPT_request.choices[0].text
                except Exception as e:
                    print(f"error getting response from ChatGPT: {e}")

            # Create Github issue
            url = f"https://api.github.com/repos/{self.GITHUB_ORG_NAME_OR_USERNAME}/{self.GIT_REPO_NAME}/issues"  # noqa: E501
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.GITHUB_FINE_GRAINED_ACCESS_TOKEN}",  # noqa: E501
                "X-GitHub-Api-Version": "2022-11-28",
            }

            data = {
                "title": issue_title,
                "body": issue_body,
                "assignees": [],
                "labels": ["bug", "chatgptops"],
            }

            req = urllib.request.Request(
                url, headers=headers, data=json.dumps(data).encode("utf-8")
            )
            response = urllib.request.urlopen(req)
