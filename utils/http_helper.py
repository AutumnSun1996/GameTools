from functools import wraps
from urllib.parse import urljoin
from http.cookies import SimpleCookie, BaseCookie

import requests
import logging


logger = logging.getLogger(__name__)


def try_decode(data):
    if not hasattr(data, "decode"):
        return data
    try:
        data = data.decode("UTF8")
    except UnicodeDecodeError:
        pass
    return data


class HttpClient(object):
    def __init__(self, base_url: str = None, timeout: int = 10) -> None:
        self.base_url = base_url
        self.session = requests.session()
        self.timeout = timeout
        self.hooks = {"before_request": [], "after_response": []}

    def __str__(self) -> str:
        return "{}({})".format(self.__class__.__name__, self.base_url or "")

    __repr__ = __str__

    def load_cookies(self, cookies):
        if isinstance(cookies, str):
            cookies = cookies.strip()
            if cookies.startswith("Cookie: "):
                cookies = cookies[8:]
            self.session.cookies.update(SimpleCookie(cookies))
        elif isinstance(cookies, (dict, BaseCookie)):
            self.session.cookies.update(cookies)
        else:
            raise TypeError("无法加载cookie %r" % cookies)

    def _make_request(self, req):
        for hook in self.hooks["before_request"]:
            res = hook(req, self)
            if isinstance(res, requests.Response):
                # 返回最终响应
                return res
            if res is not None:
                # 返回更新后的请求参数
                req = res
            # 为None时, 无动作

        return self.session.request(**req)

    def _after_response(self, resp, req):
        for hook in self.hooks["after_response"]:
            res = hook(resp, req, self)
            if res is not None:
                # 返回更新后的请求参数
                resp = res
        return resp

    @wraps(requests.Session.request)
    def request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        if self.base_url is not None:
            url = urljoin(self.base_url, url)

        req = {"method": method, "url": url, **kwargs}
        resp = self._make_request(req)
        resp = self._after_response(resp, req)
        logger.info(
            "Request: %s %s %s %s",
            method,
            resp.request.url,
            resp.request.headers,
            try_decode(resp.request.body),
        )
        logger.info(
            "Response: %s %s %s",
            resp,
            resp.headers,
            try_decode(resp.content),
        )
        return resp

    @wraps(requests.Session.get)
    def get(self, url, **kwargs):
        kwargs.setdefault("allow_redirects", True)
        return self.request("GET", url, **kwargs)

    @wraps(requests.Session.post)
    def post(self, url, data=None, json=None, **kwargs):
        return self.request("POST", url, data=data, json=json, **kwargs)

    @wraps(requests.Session.put)
    def put(self, url, data=None, **kwargs):
        return self.request("PUT", url, data=data, **kwargs)

    @wraps(requests.Session.delete)
    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

    @wraps(requests.Session.patch)
    def patch(self, url, **kwargs):
        return self.request("PATCH", url, **kwargs)
