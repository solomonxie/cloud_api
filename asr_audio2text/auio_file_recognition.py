import base64

from tencentcloud.asr.v20190614 import models

from common.auth import get_asr_auth_client


def audio_file_recognize(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
        data_len = len(data)
        base64_wav = base64.b64encode(data).decode()

    req = models.CreateRecTaskRequest()
    params = {
        "EngineModelType": "16k_0",
        "ChannelNum": 1,
        "ResTextFormat": 0,
        "SourceType": 1,
        "Data": base64_wav,
        "DataLen": data_len,
    }
    req._deserialize(params)
    resp = get_asr_auth_client().CreateRecTask(req)
    print(resp.to_json_string())


def main():
    path = ''
    audio_file_recognize(path)


if __name__ == '__main__':
    main()
