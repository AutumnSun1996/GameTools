__author__ = 'qiushiyang'
__date__ = '2020/08/04'

import logging
import time
from baseproxy.proxy import ReqIntercept, RspIntercept, AsyncMitmProxy
import base64
from urllib.parse import unquote
import threading
from queue import Queue, Empty
import yaml

try:
    import simplejson as json
except ImportError:
    import json


from helper import Record, get_session

logger = logging.getLogger(__name__)
items = Queue()
db_session = get_session()


class DebugInterceptor(ReqIntercept, RspIntercept):
    def deal_request(self, request):
        return request

    def deal_response(self, response):
        items.put(response)
        logger.info("Add One")
        return response


def show_items():
    while True:
        try:
            resp = items.get(block=True, timeout=1)
        except Empty:
            time.sleep(1)
            continue

        try:
            show_response(resp)
        except:
            logger.exception("ParseFailed")


def to_json(data):
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))


def show_response(resp):
    req = resp.request
    path = req.path
    if "?" in path:
        path, params = path.split("?", 1)
    else:
        params = ""

    if path.endswith(("heartbeat", ".bin")):
        logger.info("Ignore %s", path)
        return
    logger.info(
        "Request: %s %s %s \n%s\n%s",
        req.command,
        req.hostname,
        req.path,
        req.get_headers(),
        req.get_body_data()[:200],
    )
    body = resp.get_body_data()
    if body.startswith(b"ey"):
        # 经过Base64编码的JSON
        # 开头为 b'{"...' -> b'ey...'
        body = base64.b64decode(unquote(body.decode()))
    logger.info("Response: %s\n%s", resp.get_headers(), body[:200])

    rec = Record(
        method=req.command,
        path=path,
        host=req.hostname,
        params=params,
        headers=to_json(req.get_headers()),
        body=req.get_body_data(),
        resp_headers=to_json(resp.get_headers()),
        resp_body=body,
    )
    db_session.add(rec)
    db_session.commit()
    logger.info("Record Saved: %s", rec.id)

    # data = json.loads(body)
    # text_yml = yaml.dump(data, allow_unicode=True)
    # print(text_yml[:200])


if __name__ == "__main__":
    logging.basicConfig(level="INFO")

    parser = threading.Thread(target=show_items)
    parser.start()

    baseproxy = AsyncMitmProxy(https=True)
    baseproxy.register(DebugInterceptor)
    baseproxy.serve_forever()
