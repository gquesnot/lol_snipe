import requests
from requests import Session


class Session:
    headers: dict[str, str]
    base_url: str
    session: Session

    def __init__(self):
        self.session = requests.Session()

    def init(self, protocol, address, port, headers):
        self.session.headers.update(headers)
        self.headers = headers
        self.base_url = '{}://{}:{}'.format(protocol, address, port)

    def request(self, method, path, data=""):
        fn = getattr(self.session, method.lower())
        if method == "get":
            if data == "":
                return fn("{}{}".format(self.base_url, path), verify=False)
            else:
                return fn("{}{}?{}".format(self.base_url, path, data), verify=False)
        else:
            if data == "":
                return fn("{}{}".format(self.base_url, path), verify=False)
            else:
                return fn("{}{}".format(self.base_url, path), json=data, verify=False)