from urllib.parse import urlencode
import base64

import numpy as np
import cv2.cv2 as cv
import requests

from config_loader import config, logger


def contact_images(*images, sep=1):
    width = max([images.shape[1] for images in images])
    height = sum([images.shape[0] + sep for images in images]) - sep
    background = np.zeros((height, width, 3), dtype='uint8')
    x = 0
    y = 0
    for image in images:
        h, w = image.shape[:2]
        background[y:y+h, x:x+w, :] = image
        y += h + sep
    return background


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

    def api_request(self, name, image, params=None):
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
        res = requests.post(
            "https://aip.baidubce.com/rest/2.0/ocr/v1/"+name,
            params=params, headers=headers, data=body, timeout=3)
        return res.json()

    def parse_result(self, res):
        if "words_result" not in res:
            logger.error("OCR Error: %s", res)
        res = [item["words"] for item in res.get("words_result", [])]
        if len(res) == 1:
            res = res[0]
        return res

    def image2numbers(self, image):
        info = self.api_request("numbers", image)
        return self.parse_result(info)

    def image2text(self, image):
        info = self.api_request("general_basic", image)
        return self.parse_result(info)

    def image2text_accurate(self, image):
        info = self.api_request("accurate_basic", image)
        return self.parse_result(info)

    def images2text(self, *images):
        image = contact_images(*images)
        result = self.image2text(image)
        if not (isinstance(result, list) and len(result) == len(images)):
            result = self.image2text_accurate(image)
        if isinstance(result, list) and len(result) == len(images):
            return result

        logger.info("Count Not Match(Get %d for %d). Check each one.", len(result), len(images))
        result = []
        for image in images:
            text = self.image2text(image)
            if not text:
                text = self.image2text_accurate(image)
                logger.info("Use accurate ocr: %s", text)
            if isinstance(text, list):
                text = '\n'.join(text)
            result.append(text)
        return result

ocr = BaiduOCR()
if __name__ == "__main__":
    from simulator.image_tools import cv_imread
    image = cv_imread('ocrtest.png')
    print(ocr.image2text(image))
