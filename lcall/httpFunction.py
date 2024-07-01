import logging

import requests


class HTTPFunction:
    """
    Object representing a http endpoint to make the call

    The endpoint is described by its URL and optional authentication info
    """

    def __init__(self, url: str, auth: str):
        """
        Create the object with its URL

        :param url: URL to make a request to
        :param auth: Authentication parameters (can be )
        """
        self.url = url
        self.auth = auth

    def exec(self, params: list):
        """
        Execute the call

        :param params: parameter values to use
        :return: result of the execution of the call
        """
        sent_params = {k: v for k, v in enumerate(params)}

        try:
            if self.auth is not None:
                # Send auth parameters if they exist
                sent_auth = self.auth   # TODO : Do treatment to get correct sent format
                req = requests.get(self.url, sent_params, auth=sent_auth, timeout=10)
            else:
                req = requests.get(self.url, sent_params, timeout=10)
            req.raise_for_status()
        except requests.exceptions.ConnectionError or requests.exceptions.Timeout or requests.exceptions.HTTPError as e:
            logging.error(f"Call failed", exc_info=e)
            return None
        return req.text

    def __repr__(self):
        return f'"{self.url}"'
