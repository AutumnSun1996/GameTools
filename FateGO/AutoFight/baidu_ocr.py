from urllib.parse import urlencode
import base64

import cv2.cv2 as cv
import requests

from config import config


class BaiduOCR:
    def __init__(self):
        self.token = None

    def get_token(self):
        res = requests.post("https://aip.baidubce.com/oauth/2.0/token", params={
            "grant_type": "client_credentials",
            "client_id": config.get("OCR", "APIKEY"),
            "client_secret": config.get("OCR", "SecretKey"),
        })
        self.token = res.json()["access_token"]
        print("Token:", self.token)

    def api_request(self, url, image, params=None):
        if self.token is None:
            self.get_token()
        if params is None:
            params = {}

        ret, data = cv.imencode('.jpg', image)

        params.update({"access_token": self.token})
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = urlencode({
            "image": base64.encodebytes(data.tobytes())
        })
        res = requests.post(url, params=params, headers=headers, data=body)
        return res.json()

    def image2numbers(self, image):
        info = self.api_request("https://aip.baidubce.com/rest/2.0/ocr/v1/numbers", image)
        return info["words_result"][0]["words"]

    def image2text(self, image):
        info = self.api_request("https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic", image)
        return info["words_result"][0]["words"]


if __name__ == "__main__":
    from image_tools import cv_imread
    image = cv_imread('ocrtest.png')
    ocr = BaiduOCR()
    print(ocr.image2numbers(image))
else:
    ocr = BaiduOCR()
