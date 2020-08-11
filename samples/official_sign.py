import json
import hmac
import hashlib
from datetime import datetime


# 密钥参数
SECRET_ID = "AKIDz8krbsJ5yKBZQpn74WFkmLPx3*******"
SECRET_KEY = "Gu5t9xGARNpq86cd98joQYCN3*******"

SERVICE = "asr"
HOST = "asr.tencentcloudapi.com"
ENDPOINT = "https://" + HOST
REGION = "ap-beijing"
ACTION = "CreateRecTask"
VERSION = "2019-06-14"
ALGORITHM = "TC3-HMAC-SHA256"

payload = json.dumps({"Limit": 1, "Filters": [{"Name": "instance-name", "Values": [u"未命名"]}]})


def sign(key, msg):
    # 计算签名摘要函数
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def get_auth_string(payload):
    dt = datetime.now()
    timestamp = dt.timestamp()
    date = dt.strftime('%Y-%m-%d')

    # ************* 步骤 1：拼接规范请求串 *************
    http_request_method = "POST"
    canonical_uri = "/"
    canonical_querystring = ""
    ct = "application/json; charset=utf-8"
    canonical_headers = "content-type:%s\nhost:%s\n" % (ct, HOST)
    signed_headers = "content-type;host"
    hashed_request_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    canonical_request = '\n'.join([
        http_request_method,
        canonical_uri,
        canonical_querystring,
        canonical_headers,
        signed_headers,
        hashed_request_payload,
    ])
    print(canonical_request)

    # ************* 步骤 2：拼接待签名字符串 *************
    credential_scope = f'{date}/{SERVICE}/tc3_request'
    hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    string_to_sign = '\n'.join([ALGORITHM, str(timestamp), credential_scope, hashed_canonical_request])
    print(string_to_sign)

    # ************* 步骤 3：计算签名 *************
    secret_date = sign(("TC3" + SECRET_KEY).encode("utf-8"), date)
    secret_service = sign(secret_date, SERVICE)
    secret_signing = sign(secret_service, "tc3_request")
    signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    print(signature)

    # ************* 步骤 4：拼接 Authorization *************
    authorization = ', '.join([
        f'{ALGORITHM} Credential={SECRET_ID}/{credential_scope}',
        f'SignedHeaders={signed_headers}',
        f'Signature={signature}',
    ])
    print(authorization)

    headers = {
        'Authorization': authorization,
        'Content-Type': 'application/json; charset=utf-8',
        'Host': HOST,
        'X-TC-Action': ACTION,
        'X-TC-Timestamp': str(timestamp),
        'X-TC-Version': VERSION,
        'X-TC-Region': REGION,
    }

    print('curl -X POST ' + ENDPOINT
          + ' -H "Authorization: ' + authorization + '"'
          + ' -H "Content-Type: application/json; charset=utf-8"'
          + ' -H "Host: ' + HOST + '"'
          + ' -H "X-TC-Action: ' + ACTION + '"'
          + ' -H "X-TC-Timestamp: ' + str(timestamp) + '"'
          + ' -H "X-TC-Version: ' + VERSION + '"'
          + ' -H "X-TC-Region: ' + REGION + '"'
          + " -d '" + payload + "'")
    return headers
