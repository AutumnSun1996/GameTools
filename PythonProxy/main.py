__author__ = 'qiushiyang'
__date__ = '2020/08/04'

import logging
import time
from baseproxy.proxy import RspIntercept, AsyncMitmProxy
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


class DebugInterceptor(RspIntercept):
    def deal_response(self, response):
        """处理响应结果"""
        # 此处将响应放入队列，然后直接返回
        items.put(response)
        logger.debug("One response added")
        return response


def check_items():
    """检查队列
    """
    while True:
        try:
            resp = items.get(block=True, timeout=1)
        except Empty:
            # 队列为空，等待1s后重新获取
            time.sleep(1)
            continue

        try:
            # 尝试处理响应内容
            handle_response(resp)
        except:
            logger.exception("ParseFailed")


def to_json(data):
    """将python类型转换为json文本"""
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))


def handle_response(resp):
    """处理响应内容"""
    # 获取对应的请求
    req = resp.request
    path = req.path
    # 提取path和params
    if "?" in path:
        path, params = path.split("?", 1)
    else:
        params = ""

    # 忽略部分请求
    if path.endswith(("heartbeat", ".bin", ".png", ".jpg")):
        logger.info("Ignore %s", path)
        return

    # 输出请求信息
    logger.info(
        "Request: %s %s %s \n%s\n%s",
        req.command,
        req.hostname,
        req.path,
        req.get_headers(),
        req.get_body_data()[:200],
    )
    # 获取响应数据
    body = resp.get_body_data()
    # 尝试解码
    if body.startswith(b"ey"):
        # 经过Base64编码的JSON
        # 开头为: {"... -> ey...
        body = base64.b64decode(unquote(body.decode()))
    # 输出响应信息
    logger.info("Response: %s\n%s", resp.get_headers(), body[:200])

    # 保存到数据库
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

    # 开始监控队列
    parser = threading.Thread(target=check_items)
    parser.start()

    baseproxy = AsyncMitmProxy(https=True)
    baseproxy.register(DebugInterceptor)
    baseproxy.serve_forever()
