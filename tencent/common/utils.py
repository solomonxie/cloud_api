import hmac
import hashlib


def chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i: i+size]


def sign(key, msg):
    # 计算签名摘要函数
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()
